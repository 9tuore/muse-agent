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
p.add_argument('--kernel-test-frozen',action='store_true')
p.add_argument('--kernel-binary', type=Path)
p.add_argument('--kernel-config', type=Path)
p.add_argument('--calendar-owner-helper', type=Path)
p.add_argument('--authorize-external-owner-write',action='store_true',help='Explicit Root fixture scope: create/remove an exact marker for this one actual selected event')
p.add_argument('--fault-case', choices=['none','mail-review-timeout','mail-review-malformed-json'],default='none')
p.add_argument('--mail-mode', choices=['accepted','before','unknown'],default='accepted')
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
trace, counters, faults = [], collections.Counter(), []
write_fault, review_fault_used = None,False
source_identity = json.loads(prepared.with_name('identity.json').read_text())
assert sha(prepared.read_bytes()) == source_identity['executed_sha256'], 'Prepared production VM program changed'
kernel, kernel_start_error = None,None
kernel_options = [a.kernel_bridge,a.kernel_test_binary,a.kernel_binary,a.kernel_config]
assert not any(kernel_options) or all(kernel_options), 'All four explicit Kernel arguments are required'
assert not a.kernel_test_frozen or all(kernel_options), 'Frozen binary requires all explicit Kernel arguments'
if all(kernel_options):
    try:
        kernel = KernelBridge(bridge=a.kernel_bridge,test_binary=a.kernel_test_binary,
            kernel=a.kernel_binary,config=a.kernel_config,out=out,
            source_sha=source_identity['source_sha256'],source_file=prepared.with_name('frozen-main.splash'),
            use_frozen_test_binary=a.kernel_test_frozen)
    except Exception as error: kernel_start_error = type(error).__name__+': '+str(error)
owner_helper = None
assert not a.authorize_external_owner_write or a.calendar_owner_helper, 'External write scope requires the explicit owner binary'
if a.calendar_owner_helper:
    assert kernel is not None, 'External owner editing requires a ready actual Kernel fixture'
    owner_helper = out/'calendar-owner-helper'
    shutil.copy2(a.calendar_owner_helper.resolve(strict=True),owner_helper)
    assert sha(owner_helper.read_bytes()) == 'e7dc890860d1a17d2fbc08e68ed98aa39c75eaee370bb18a6eb2281b2ed6c265', 'GPT01 dedicated external owner identity differs'
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
    if method == 'fixture.mode':
        assert payload['mode'] in ('accepted','before','unknown')
        request['mode'] = payload['mode']
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
    global serial,write_fault,review_fault_used
    method, payload = request['method'],request['payload']
    counters[method] += 1
    if method.startswith('mail.') or method in ('runtime.list','fixture.receiver','fixture.incoming','fixture.mode'):
        reply = mail_call(method,payload)
        if method == 'mail.review_send' and not review_fault_used and a.fault_case != 'none':
            review_fault_used = True
            fault = dict(boundary='Parent delivery of actual Mail review reply; service already ran',
                         case=a.fault_case,actual_reply=reply,actual_recipient=mail_call('fixture.receiver',{}))
            if a.fault_case == 'mail-review-timeout':
                # Deliberately withhold a completed response. This is an injected
                # parent timeout event, not a service or Kernel timeout claim.
                forwarded = dict(is_ok=False,error='Injected parent review reply timeout; outcome unknown; never resend')
            else:
                broken = '{NIGHT004 deliberately malformed parent response'
                try: json.loads(broken)
                except json.JSONDecodeError as error:
                    fault.update(injected_wire=broken,actual_decode_error=str(error))
                    forwarded = dict(is_ok=False,error='Parent refused injected malformed JSON: '+str(error))
            fault['forwarded_reply'] = forwarded; faults.append(fault)
            return forwarded
        return reply
    if method == 'fixture/owner-update':
        assert owner_helper is not None, 'External actual owner helper was not supplied'
        assert set(payload) == {'id','expected','title','start','end','timezone','location','notes'}
        assert set(payload['expected']) == {'id','request_id','title','start','end','timezone','location','notes'}
        assert payload['id'] == payload['expected']['id']
        host_root = Path(kernel.identity['fixture_root'])/'apps/.host'
        host_root.resolve(strict=True).relative_to(Path(kernel.identity['fixture_root']).resolve(strict=True))
        assert (host_root/'FIXTURE_ONLY').is_file()
        assert all(payload[key] == payload['expected'][key] for key in ('start','end','timezone','location')), 'External fixture only changes notes/title'
        assert payload['notes'] != payload['expected']['notes'] or payload['title'] != payload['expected']['title']
        owner_request = dict(owner='os.calendar',method='update_event',args=payload)
        scope = dict(purpose='NIGHT004_SYNTHETIC_EXTERNAL_OWNER',host_dir=str(host_root.resolve(strict=True)),
                     event_id=payload['id'],fixture_request_id=payload['expected']['request_id'])
        permission = host_root/'EXTERNAL_CALENDAR_OWNER_WRITE_OK.json'
        (out/'external-owner-request.json').write_text(json.dumps(owner_request,ensure_ascii=False,indent=2)+'\n')
        (out/'external-owner-scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n')
        created_permission = False
        if not permission.exists() and a.authorize_external_owner_write:
            with permission.open('x') as file: file.write(json.dumps(scope)+'\n')
            created_permission = True
        assert not permission.is_symlink() and json.loads(permission.read_text()) == scope, 'Root exact external write scope marker required'
        events = host_root/'calendar/events.json'
        before = sha(events.read_bytes())
        try:
            result = subprocess.run([str(owner_helper),kernel.identity['fixture_root'],payload['id'],payload['expected']['request_id']],
                                    input=json.dumps(owner_request),capture_output=True,text=True,timeout=15)
            (out/'external-owner-stdout.json').write_text(result.stdout)
            (out/'external-owner-stderr.log').write_text(result.stderr)
            assert result.returncode == 0, 'Actual dedicated external owner process failed: '+result.stderr
            reply = json.loads(result.stdout)
        finally:
            if created_permission:
                assert json.loads(permission.read_text()) == scope, 'External marker changed during actual operation'
                permission.unlink()
        faults.append(dict(boundary='Separate dedicated actual CalendarService process on the marked Kernel fixture owner store',
            request=owner_request,actual_reply=reply,before_store_sha256=before,after_store_sha256=sha(events.read_bytes()),
            helper_sha256=sha(owner_helper.read_bytes()),exact_fixture_scope=scope,root_explicit_scope_flag=a.authorize_external_owner_write,
            own_marker_created_and_removed=created_permission,kernel_history_generated=False))
        actual = reply['result']
        return dict(is_ok=actual['ok'],data=actual.get('data'),error=actual.get('error'))
    if method == 'fixture/owner-store-sha':
        assert kernel is not None, 'Actual Kernel fixture is required for owner store SHA'
        root = Path(kernel.identity['fixture_root']).resolve(strict=True)
        events = root/'apps/.host/calendar/events.json'
        events.resolve(strict=True).relative_to(root)
        assert not events.is_symlink() and (root/'apps/.host/FIXTURE_ONLY').is_file()
        raw = events.read_bytes()
        return dict(is_ok=True,data=dict(sha256=sha(raw),bytes=len(raw)))
    if method.startswith('octos.') or method in ('fixture/read-owner','fixture/logsideeffects','fixture/history-sessions'):
        if kernel is None: raise ValueError('unconfigured actual backend: '+method+((': '+kernel_start_error) if kernel_start_error else ''))
        return kernel.call(method,payload)
    if method == 'fixture.clock': return dict(is_ok=True,data=1791741600)
    if method == 'fixture.host_capabilities': return dict(is_ok=True,data=['mail'])
    if method == 'fixture.observe': return dict(is_ok=True,data=None)
    if method == 'fixture/call-counts': return dict(is_ok=True,data=dict(counters))
    if method == 'fixture.fault.options': return dict(is_ok=True,data=dict(mail_mode=a.mail_mode,reply_fault=a.fault_case))
    if method == 'fixture.fault.arm_write':
        assert payload == {'path':'mail-draft.backup.json'} and write_fault is None
        write_fault = payload['path']
        return dict(is_ok=True,data=dict(armed=True,path=write_fault))
    if method == 'fixture.random':
        serial += 1
        serial_file.write_text(json.dumps(serial))
        return dict(is_ok=True,data=serial)
    if method.startswith('fixture.fs.'):
        operation = method.rsplit('.',1)[-1]
        target = jailed(payload['path'])
        if operation == 'exists': value = target.exists()
        elif operation == 'read': value = target.read_text()
        elif operation == 'write':
            if write_fault == payload['path']:
                write_fault = None
                original = target.read_bytes() if target.is_file() else None
                primary = state/'mail-draft.json'; primary_before = sha(primary.read_bytes())
                saved = out/'write-fault-original-backup.bin'
                if original is not None: target.rename(saved)
                target.mkdir()
                fault = dict(boundary='Actual Path.write_text against an owned directory at the backup file path',
                    path=payload['path'],original_backup_sha256=sha(original) if original is not None else None,
                    primary_before_sha256=primary_before)
                try: target.write_text(payload['data'])
                except OSError as error:
                    fault.update(actual_os_error=type(error).__name__+': '+str(error),errno=error.errno)
                    raise
                finally:
                    target.rmdir()
                    if original is not None: shutil.copy2(saved,target)
                    fault.update(primary_after_sha256=sha(primary.read_bytes()),
                        backup_after_sha256=sha(target.read_bytes()) if target.is_file() else None)
                    faults.append(fault)
            else: target.write_text(payload['data'])
            value = None
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
    exit_code=exit_code,error=error,failed=failed,probe=data,counters=dict(counters),trace=trace,faults=faults,
    source_identity=source_identity,
    runner_sha256=sha((out/'vm-bin').read_bytes()),mail_binary_sha256=sha((out/'mail-bin').read_bytes()),
    state_sha256={str(f.relative_to(state)):sha(f.read_bytes()) for f in sorted(state.rglob('*')) if f.is_file()},
    boundary='Real production VM/service functions. IO/timer/clock/UI/user approval are fixture boundaries; no Kernel history or Calendar success synthesized.')
report['unconfigured_backends'] = sorted({row['request']['method'] for row in trace if isinstance(row['reply'].get('error'),str) and row['reply']['error'].startswith('unconfigured actual backend:')})
report['full_chain_status'] = 'NOT_TESTED'
report['kernel_identity'] = kernel.identity if kernel is not None else None
report['kernel_ready'] = kernel.ready if kernel is not None else None
report['kernel_start_error'] = kernel_start_error
report['calendar_owner_helper_sha256'] = sha(owner_helper.read_bytes()) if owner_helper is not None else None
report['fault_case'] = a.fault_case
clean_kernel = kernel is not None and kernel.identity.get('exit_code')==0 and not kernel.identity.get('reader_error') and not kernel.identity.get('quit_error') and kernel.identity.get('frozen_binary_unchanged',True)
if kernel is not None and not clean_kernel: report['status'] = 'FAIL'
if data and data.get('kind') == 'NIGHT004_NATIVE_L3_FULL_CHAIN':
    report['full_chain_status'] = 'PASS' if report['status']=='PASS' and clean_kernel else ('FAIL' if kernel is not None else 'NOT_TESTED')
report['state_root'] = str(state); report['mail_root'] = str(mail_root)
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','exit_code','failed','error']}))
raise SystemExit(0 if report['status']=='PASS' else 1)
