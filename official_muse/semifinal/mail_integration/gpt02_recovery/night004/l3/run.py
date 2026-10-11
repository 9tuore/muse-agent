#!/usr/bin/env python3
"""Real Splash VM RPC → real Mail service helper; owned filesystem boundary."""
import argparse, collections, hashlib, json, os, queue, shutil, subprocess, sys, threading, time
from pathlib import Path
from kernel_rpc import KernelBridge

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sha = lambda b: hashlib.sha256(b).hexdigest()
p = argparse.ArgumentParser()
p.add_argument('--prepared', type=Path, required=True)
p.add_argument('--runner', type=Path, required=True)
p.add_argument('--mail-binary', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--state-root', type=Path)
p.add_argument('--mail-root', type=Path)
p.add_argument('--kernel-bridge', type=Path)
p.add_argument('--kernel-test-binary', type=Path)
p.add_argument('--kernel-binary', type=Path)
p.add_argument('--kernel-config', type=Path)
p.add_argument('--timeout-seconds',type=int,default=120)
a = p.parse_args()
prepared = a.prepared.resolve(strict=True)
out = a.out.resolve(); out.relative_to(ROOT/'build'); out.mkdir(parents=True, exist_ok=False)
state = (a.state_root or out/'state').resolve(); state.relative_to(ROOT/'build')
marker = state/'FIXTURE_ONLY'
if state.exists(): assert marker.read_text() == 'NIGHT004 CLI VM fixture only\n'
else: state.mkdir(parents=True); marker.write_text('NIGHT004 CLI VM fixture only\n')
mail_root = (a.mail_root or out/'mail-state').resolve(); mail_root.relative_to(ROOT/'build')
shutil.copy2(a.runner.resolve(strict=True),out/'vm-bin')
shutil.copy2(a.mail_binary.resolve(strict=True),out/'mail-bin')
trace, counters = [], collections.Counter()
source_identity = json.loads(prepared.with_name('identity.json').read_text())
assert sha(prepared.read_bytes()) == source_identity['executed_sha256'], 'Prepared production VM program changed'
kernel, kernel_start_error = None,None
kernel_options = [a.kernel_bridge,a.kernel_test_binary,a.kernel_binary,a.kernel_config]
assert not any(kernel_options) or all(kernel_options), 'All four explicit Kernel arguments are required'
if all(kernel_options):
    try:
        kernel = KernelBridge(bridge=a.kernel_bridge,test_binary=a.kernel_test_binary,
            kernel=a.kernel_binary,config=a.kernel_config,out=out,
            source_sha=source_identity['source_sha256'],source_file=prepared.with_name('frozen-main.splash'))
    except Exception as error: kernel_start_error = type(error).__name__+': '+str(error)
serial_file = state/'fixture-random.json'
serial = json.loads(serial_file.read_text()) if serial_file.exists() else 0
mail_log = (out/'mail-stderr.log').open('w')
mail = subprocess.Popen([sys.executable,str(HERE.parent/'mail_helper.py'),'--binary',str(out/'mail-bin'),
    '--root',str(mail_root)],text=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=mail_log)
mail_replies = queue.Queue()
def read_mail():
    for line in mail.stdout: mail_replies.put(json.loads(line))
mail_reader = threading.Thread(target=read_mail,daemon=True); mail_reader.start()
mail_id = 0
def mail_call(method,payload):
    global mail_id
    mail_id += 1
    request = dict(id=mail_id,method=method,args=payload)
    if method == 'mail.review_send': request['decision'] = 'approve'
    mail.stdin.write(json.dumps(request)+'\n'); mail.stdin.flush()
    reply = mail_replies.get(timeout=15)
    assert reply['id'] == mail_id
    return {k:v for k,v in reply.items() if k != 'id'}

def jailed(path):
    target = (state/path).resolve()
    target.relative_to(state)
    assert target != state, 'operation must name a jailed file/directory'
    return target
def dispatch(request):
    global serial
    method, payload = request['method'],request['payload']
    counters[method] += 1
    if method.startswith('mail.') or method in ('runtime.list','fixture.receiver','fixture.incoming'):
        return mail_call(method,payload)
    if method.startswith('octos.') or method in ('fixture/read-owner','fixture/logsideeffects','fixture/history-sessions'):
        if kernel is None: raise ValueError('unconfigured actual backend: '+method+((': '+kernel_start_error) if kernel_start_error else ''))
        return kernel.call(method,payload)
    if method == 'fixture.clock': return dict(is_ok=True,data=1791741600)
    if method == 'fixture.host_capabilities': return dict(is_ok=True,data=['mail'])
    if method == 'fixture.observe': return dict(is_ok=True,data=None)
    if method == 'fixture.random':
        serial += 1
        serial_file.write_text(json.dumps(serial))
        return dict(is_ok=True,data=serial)
    if method.startswith('fixture.fs.'):
        operation = method.rsplit('.',1)[-1]
        target = jailed(payload['path'])
        if operation == 'exists': value = target.exists()
        elif operation == 'read': value = target.read_text()
        elif operation == 'write': target.write_text(payload['data']); value = None
        elif operation == 'mkdir': target.mkdir(parents=True,exist_ok=True); value = None
        elif operation == 'sha256_file': value = sha(target.read_bytes())
        else: raise ValueError('unsupported IO boundary operation')
        return dict(is_ok=True,data=value)
    raise ValueError('unconfigured actual backend: '+method)

stderr = (out/'vm-stderr.log').open('w')
vm = subprocess.Popen([str(out/'vm-bin'),str(prepared),'--rpc'],text=True,
                      stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
lines = queue.Queue()
def read_vm():
    for line in vm.stdout: lines.put(line)
    lines.put(None)
reader = threading.Thread(target=read_vm,daemon=True); reader.start()
data, error = None,None
try:
    with (out/'vm-stdout.log').open('w') as raw:
        deadline = time.monotonic()+a.timeout_seconds
        while time.monotonic() < deadline:
            line = lines.get(timeout=min(20,deadline-time.monotonic()))
            if line is None: break
            raw.write(line); raw.flush()
            if line.startswith('MUSE_VM_REQUEST '):
                request = json.loads(line[len('MUSE_VM_REQUEST '):])
                try: reply = dispatch(request)
                except Exception as e: reply = dict(is_ok=False,error=str(e))
                trace.append(dict(request=request,reply=reply))
                vm.stdin.write(json.dumps(reply,ensure_ascii=False)+'\n'); vm.stdin.flush()
            elif line.startswith('MUSE_VM_RESULT '):
                data = json.loads(line[len('MUSE_VM_RESULT '):])
        exit_code = vm.wait(timeout=10)
except Exception as e:
    error = str(e); exit_code = None
finally:
    if vm.poll() is None: vm.kill(); vm.wait()
    try: mail_call('fixture.quit',{})
    except Exception: pass
    if mail.poll() is None:
        try: mail.wait(timeout=10)
        except subprocess.TimeoutExpired: mail.kill(); mail.wait()
    stderr.close(); mail_log.close()
    if kernel is not None: kernel.close()
checks = data.get('checks',{}) if data else {}
failed = [k for k,v in checks.items() if v is not True]
runtime_errors = (out/'vm-stderr.log').read_text()
report = dict(kind='PRODUCTION_MUSE_CLI_VM_TO_ACTUAL_MAIL_SERVICE_WITH_MOCK_TRANSPORT',
    status='PASS' if data and checks and not failed and exit_code == 0 and not runtime_errors else 'FAIL',
    exit_code=exit_code,error=error,failed=failed,probe=data,counters=dict(counters),trace=trace,
    source_identity=source_identity,
    runner_sha256=sha((out/'vm-bin').read_bytes()),mail_binary_sha256=sha((out/'mail-bin').read_bytes()),
    state_sha256={str(f.relative_to(state)):sha(f.read_bytes()) for f in sorted(state.rglob('*')) if f.is_file()},
    boundary='Real production VM/service functions. IO/timer/clock/UI/user approval are fixture boundaries; no Kernel history or Calendar success synthesized.')
report['unconfigured_backends'] = sorted({row['request']['method'] for row in trace if isinstance(row['reply'].get('error'),str) and row['reply']['error'].startswith('unconfigured actual backend:')})
report['full_chain_status'] = 'NOT_TESTED'
report['kernel_identity'] = kernel.identity if kernel is not None else None
report['kernel_ready'] = kernel.ready if kernel is not None else None
report['kernel_start_error'] = kernel_start_error
if data and data.get('kind') == 'NIGHT004_NATIVE_L3_FULL_CHAIN':
    clean_kernel = kernel is not None and kernel.identity.get('exit_code')==0 and not kernel.identity.get('reader_error') and not kernel.identity.get('quit_error')
    if kernel is not None and not clean_kernel: report['status'] = 'FAIL'
    report['full_chain_status'] = 'PASS' if report['status']=='PASS' and clean_kernel else ('FAIL' if kernel is not None else 'NOT_TESTED')
report['state_root'] = str(state); report['mail_root'] = str(mail_root)
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','exit_code','failed','error']}))
raise SystemExit(0 if report['status']=='PASS' else 1)
