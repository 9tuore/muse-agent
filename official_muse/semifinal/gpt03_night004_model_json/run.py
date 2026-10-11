#!/usr/bin/env python3
"""Actual SDK raw provider JSON → unchanged actual Main callback, owned synthetic state only."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_SHA = 'c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'
VM_SHA = 'f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351'
MAIL_SHA = 'ba37b915b24917be68964c10c38409169b7162489fbd2de22c082a1e05055367'
RECEIVER_SHA = '7be09ed1af4310f5d40bb108d807100d661058cba88f64a48c0504ac50bf5288'
sha = lambda data: hashlib.sha256(data).hexdigest()
write_json = lambda path, data: path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
CASES = [
    ('invalid-calendar', '请安排日程：2030年12月12日10点到11点，地点合成会议室。', b'{'),
    ('invalid-mail-fenced', '请起草邮件给 receiver@example.invalid，主题合成核对，正文合成内容。', b'```json\n{"reply":"damaged"\n```'),
    ('valid-control', '请解释这条合成说明。', b'{"reply":"synthetic decoded control"}'),
]

def validate_prepared(prepared, source_sha):
    assert len(source_sha)==64 and all(c in '0123456789abcdef' for c in source_sha), '--source-sha must be a lowercase SHA-256'
    identity=json.loads(prepared.with_name('identity.json').read_text())
    assert identity['source_sha256']==source_sha, 'prepared source identity mismatch'
    assert sha(prepared.read_bytes())==identity['executed_sha256'], 'prepared execution identity mismatch'
    return identity

def run_case(mode, query, raw_model, case, prepared, vm_binary, mail_binary, model_binary, receiver, source_sha):
    case.mkdir()
    state = case / 'main-state'; state.mkdir(); (state/'FIXTURE_ONLY').write_text('NIGHT004 Main model fixture only\n')
    model_root = case / 'model-state'; model_root.mkdir(); (model_root/'FIXTURE_ONLY').write_text('NIGHT004 model JSON fixture only\n')
    (model_root/'.host').mkdir()
    (case/'raw-model-output.bin').write_bytes(raw_model)
    identity = validate_prepared(prepared, source_sha)
    env = dict(os.environ, NIGHT004_MODEL_ALLOWED_ROOT=str(ROOT/'build'))
    model_error = (case/'sdk-stderr.log').open('w')
    model = subprocess.Popen([str(model_binary), str(model_root)], env=env, text=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=model_error)
    mail_env = dict(os.environ, NIGHT004_TMP_ROOT=str(ROOT/'build'), NIGHT004_L3_ROOT=str(case/'mail-state'),
                    NIGHT004_RECEIVER_SCRIPT=str(receiver))
    mail = subprocess.Popen([str(mail_binary), '--exact','night004_l2::l3_protocol_driver','--ignored','--nocapture','--test-threads=1'],
        env=mail_env, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    mail_queue, model_queue, vm_queue = queue.Queue(), queue.Queue(), queue.Queue()
    def read_json(child, inbox, path, harness=False):
        with path.open('w') as log:
            for line in child.stdout:
                log.write(line); log.flush()
                start = line.find('{') if harness else 0
                if start >= 0:
                    try: inbox.put(json.loads(line[start:]))
                    except json.JSONDecodeError: inbox.put({'reader_error':line})
            inbox.put(None)
    threading.Thread(target=read_json,args=(model,model_queue,case/'sdk-stdout.log'),daemon=True).start()
    threading.Thread(target=read_json,args=(mail,mail_queue,case/'mail-stdout.log',True),daemon=True).start()
    vm_error = (case/'vm-stderr.log').open('w')
    vm = subprocess.Popen([str(vm_binary),str(prepared),'--rpc'], text=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=vm_error)
    def read_vm():
        for line in vm.stdout: vm_queue.put(line)
        vm_queue.put(None)
    threading.Thread(target=read_vm,daemon=True).start()
    mail_id, serial, sdk_observation = 0, 0, None
    counters, trace, helper_trace = collections.Counter(), [], []
    def mail_call(method, payload):
        nonlocal mail_id
        mail_id += 1; request=dict(id=mail_id,method=method,args=payload)
        # No approval is supplied. Any unexpected review call cannot send.
        mail.stdin.write(json.dumps(request)+'\n'); mail.stdin.flush()
        reply=mail_queue.get(timeout=15)
        assert reply is not None and reply.get('id') == mail_id, 'Actual Mail reply missing/mismatched'
        helper_trace.append(dict(request=request,reply=reply))
        return {key:value for key,value in reply.items() if key!='id'}
    def jailed(name):
        path=(state/name).resolve(); path.relative_to(state); assert path!=state; return path
    def dispatch(request):
        nonlocal serial, sdk_observation
        method,payload=request['method'],request['payload']; counters[method]+=1
        if method=='model.complete':
            assert sdk_observation is None, 'One logical Main model request per case'
            wire=dict(method=method,args=payload,raw_model_text=raw_model.decode('utf-8'))
            write_json(case/'actual-main-model-request.json',payload)
            model.stdin.write(json.dumps(wire,ensure_ascii=False)+'\n'); model.stdin.flush()
            sdk_observation=model_queue.get(timeout=20)
            assert sdk_observation and 'reply' in sdk_observation, 'Actual SDK response unavailable'
            sdk_observation['original_sdk_reply_forwarded']=True
            for index,attempt in enumerate(sdk_observation['provider_attempts']):
                assert attempt['raw_model_text'].encode()==raw_model
                (case/('raw-provider-response-'+str(index)+'.bin')).write_bytes(attempt['raw_provider_response_utf8'].encode())
                write_json(case/('actual-sdk-provider-request-'+str(index)+'.json'),attempt['request'])
            return sdk_observation['reply']
        if method.startswith('mail.') or method in ('runtime.list','fixture.receiver'): return mail_call(method,payload)
        if method=='fixture.options': return dict(is_ok=True,data=dict(mode=mode,query=query))
        if method=='fixture.counts': return dict(is_ok=True,data=dict(counters))
        if method=='fixture.model-observed':
            assert sdk_observation is not None
            return dict(is_ok=True,data=dict(original_sdk_reply_forwarded=sdk_observation['original_sdk_reply_forwarded'],
                provider_attempts=len(sdk_observation['provider_attempts']),sdk_reply=sdk_observation['reply']))
        if method=='fixture.clock': return dict(is_ok=True,data=1791741600)
        if method=='fixture.random': serial+=1; return dict(is_ok=True,data=serial)
        if method.startswith('fixture.fs.'):
            operation=method.rsplit('.',1)[-1]; path=jailed(payload['path'])
            if operation=='exists': value=path.exists()
            elif operation=='read': value=path.read_text()
            elif operation=='write': path.write_text(payload['data']); value=None
            elif operation=='mkdir': path.mkdir(parents=True,exist_ok=True); value=None
            elif operation=='sha256_file': value=sha(path.read_bytes())
            else: raise ValueError('Unconfigured owned IO operation '+operation)
            return dict(is_ok=True,data=value)
        raise ValueError('Unconfigured backend '+method)
    data,error,exit_code=None,None,None
    try:
        with (case/'vm-stdout.log').open('w') as log:
            deadline=time.monotonic()+100
            while time.monotonic()<deadline:
                line=vm_queue.get(timeout=min(20,deadline-time.monotonic()))
                if line is None: break
                log.write(line); log.flush()
                if line.startswith('MUSE_VM_REQUEST '):
                    request=json.loads(line[len('MUSE_VM_REQUEST '):])
                    try: reply=dispatch(request)
                    except Exception as exception: reply=dict(is_ok=False,error=type(exception).__name__+': '+str(exception))
                    trace.append(dict(request=request,reply=reply))
                    vm.stdin.write(json.dumps(reply,ensure_ascii=False)+'\n'); vm.stdin.flush()
                elif line.startswith('MUSE_VM_RESULT '): data=json.loads(line[len('MUSE_VM_RESULT '):])
            exit_code=vm.wait(timeout=10)
    except Exception as exception: error=type(exception).__name__+': '+str(exception)
    finally:
        if vm.poll() is None: vm.kill(); vm.wait()
        for child,inbox,quit_request in [(model,model_queue,dict(method='fixture.quit'))]:
            try:
                child.stdin.write(json.dumps(quit_request)+'\n');child.stdin.flush();inbox.get(timeout=5);child.wait(timeout=10)
            except Exception:
                if child.poll() is None: child.kill();child.wait()
        try: mail_call('fixture.quit',{});mail.wait(timeout=10)
        except Exception:
            if mail.poll() is None: mail.kill();mail.wait()
        vm_error.close();model_error.close()
    checks=dict((data or {}).get('checks',{}))
    attempts=(sdk_observation or {}).get('provider_attempts',[])
    checks.update(actual_provider_raw_bytes_preserved=len(attempts)==(1 if mode=='valid-control' else 2)
        and all(attempt['raw_model_text'].encode()==raw_model for attempt in attempts),
        actual_sdk_retry_correction_present=mode=='valid-control' or (len(attempts)==2
            and 'not valid JSON' in json.dumps(attempts[1]['request'])),
        actual_sdk_response_not_synthesized=sdk_observation is not None and any(row['request']['method']=='model.complete'
            and row['reply']==sdk_observation['reply'] for row in trace),
        no_real_http=(sdk_observation or {}).get('real_http_calls')==0,
        runtime_clean=exit_code==0 and (case/'vm-stderr.log').read_text()=='' and error is None,
        actual_sdk_mail_processes_clean=model.returncode==0 and mail.returncode==0)
    failed=[key for key,value in checks.items() if value is not True]
    report=dict(status='PASS' if data and checks and not failed else 'FAIL',mode=mode,checks=checks,failed=failed,
        exit_code=exit_code,error=error,probe=data,counters=dict(counters),trace=trace,helper_trace=helper_trace,
        actual_sdk_observation=sdk_observation,raw_model_sha256=sha(raw_model),raw_model_bytes=len(raw_model),
        source_identity=identity,source_sha256=source_sha,
        processes=dict(vm_pid=vm.pid,model_sdk_pid=model.pid,mail_pid=mail.pid,model_exit_code=model.returncode,mail_exit_code=mail.returncode),
        source_files_sha256={str(path.relative_to(case)):sha(path.read_bytes()) for path in sorted(case.rglob('*'))
            if path.is_file() and path.name!='report.json'},
        full_chain_status='NOT_TESTED',boundary='Actual existing SDK ModelService dispatch and parser/repair/refusal → actual Main callback. Synthetic provider bytes/grants/UI/timers/clock. No Kernel/GUI/HTTP/SMTP.')
    write_json(case/'report.json',report)
    print(json.dumps(dict(mode=mode,status=report['status'],checks=len(checks),failed=failed,error=error)),flush=True)
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha',default=SOURCE_SHA)
    parser.add_argument('--prepared',type=Path,required=True)
    parser.add_argument('--runner',type=Path,required=True)
    parser.add_argument('--mail-binary',type=Path,required=True)
    parser.add_argument('--receiver-script',type=Path,required=True)
    parser.add_argument('--sdk-driver',type=Path,required=True)
    parser.add_argument('--sdk-build-identity',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    validate_prepared(args.prepared.resolve(),args.source_sha)
    out=args.out.resolve();out.relative_to(ROOT/'build');out.mkdir(parents=True,exist_ok=False)
    sdk_identity=json.loads(args.sdk_build_identity.read_text())
    assert sdk_identity['status']=='LINKED_NOT_RUNTIME_TESTED' and sha(args.sdk_driver.read_bytes())==sdk_identity['driver_binary_sha256']
    assert sha(Path(sdk_identity['library']).read_bytes())==sdk_identity['library_sha256']
    for path,expected in [(args.runner,VM_SHA),(args.mail_binary,MAIL_SHA),(args.receiver_script,RECEIVER_SHA)]:assert sha(path.read_bytes())==expected
    binaries={}
    for name,path in [('vm-bin',args.runner),('mail-bin',args.mail_binary),('sdk-model-bin',args.sdk_driver)]:
        shutil.copy2(path,out/name);binaries[name]=out/name
    rows=[run_case(mode,query,raw,out/mode,args.prepared.resolve(),binaries['vm-bin'],binaries['mail-bin'],binaries['sdk-model-bin'],args.receiver_script.resolve(),args.source_sha)
        for mode,query,raw in CASES]
    library_unchanged=sha(Path(sdk_identity['library']).read_bytes())==sdk_identity['library_sha256']
    report=dict(status='PASS' if library_unchanged and all(row['status']=='PASS' for row in rows) else 'FAIL',
        source_sha256=args.source_sha,checks=sum(len(row['checks']) for row in rows),cases=[dict(mode=row['mode'],status=row['status'],
            checks=len(row['checks']),failed=row['failed']) for row in rows],sdk_build_identity=sdk_identity,
        sdk_library_unchanged=library_unchanged,runner_sha256=VM_SHA,mail_binary_sha256=MAIL_SHA,
        parent_sha256=sha(Path(__file__).read_bytes()),full_chain_status='NOT_TESTED',
        boundary='Actual SDK parser/refusal and Main error-state mechanism, synthetic raw provider output. No model provider/network/Kernel/GUI/SMTP called.')
    write_json(out/'summary.json',report);print(json.dumps({key:report[key] for key in ['status','checks','cases','sdk_library_unchanged']}),flush=True)
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
