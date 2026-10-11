#!/usr/bin/env python3
"""Measure real parent-clock upper intervals around production API calls in the pinned VM."""
import argparse
import collections
import hashlib
import json
import math
import platform
from pathlib import Path
import queue
import shutil
import statistics
import subprocess
import threading
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE_SHA='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'
VM_SHA='f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351'
NAMES=('bridge_only','gm_context','ac_projection')
sha=lambda data:hashlib.sha256(data).hexdigest()
write_json=lambda path,data:path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def summarize(rows):
    values=sorted(row['elapsed_ns'] for row in rows if not row['warmup'])
    assert values
    return dict(samples=len(values),iterations_per_sample=1,min_ms=values[0]/1e6,
        median_ms=statistics.median(values)/1e6,p95_ms=values[math.ceil(.95*len(values))-1]/1e6,
        max_ms=values[-1]/1e6,p95_definition='nearest rank ceil(0.95*n), no subtraction of bridge control')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared',type=Path,required=True)
    parser.add_argument('--source-sha',default=SOURCE_SHA)
    parser.add_argument('--runner',type=Path,required=True)
    parser.add_argument('--samples',type=int,default=31)
    parser.add_argument('--warmups',type=int,default=3)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    assert len(args.source_sha)==64 and all(c in '0123456789abcdef' for c in args.source_sha)
    identity=json.loads(args.prepared.with_name('identity.json').read_text())
    assert identity['source_sha256']==args.source_sha, 'prepared source identity mismatch'
    assert sha(args.prepared.read_bytes())==identity['executed_sha256'], 'prepared execution identity mismatch'
    assert identity['all_other_functions_byte_equal_after_transport_normalization'] is True
    assert sha(args.runner.read_bytes())==VM_SHA, 'fixed VM identity mismatch'
    assert 21<=args.samples<=101 and 1<=args.warmups<=5
    out=args.out.resolve();out.relative_to(ROOT/'build');out.mkdir(parents=True,exist_ok=False)
    state=out/'main-state';state.mkdir();(state/'FIXTURE_ONLY').write_text('NIGHT004 performance fixture only\n')
    shutil.copy2(args.prepared,out/'executed.splash')
    shutil.copy2(args.prepared.with_name('identity.json'),out/'identity.json')
    write_json(out/'invocation.json',dict(prepared=str(args.prepared.resolve()),source_sha=args.source_sha,
        runner=str(args.runner.resolve()),samples=args.samples,warmups=args.warmups,out=str(out)))
    stderr=(out/'vm-stderr.log').open('w')
    vm=subprocess.Popen([str(args.runner.resolve()),str(out/'executed.splash'),'--rpc'],
        text=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
    inbox=queue.Queue()
    def read_vm():
        for line in vm.stdout:inbox.put(line)
        inbox.put(None)
    threading.Thread(target=read_vm,daemon=True).start()
    counters=collections.Counter();serial=0;active=None;timings=[];unknown=[];data=None;error=None;code=None
    def jailed(name):
        path=(state/name).resolve();path.relative_to(state);assert path!=state;return path
    def dispatch(request):
        nonlocal active,serial
        method,payload=request['method'],request['payload'];counters[method]+=1
        if method=='fixture.perf_mark':
            now=time.perf_counter_ns()
            assert payload['name'] in NAMES and payload['iterations']==1
            key=(payload['name'],payload['sample'],payload['warmup'])
            if payload['phase']=='start':
                assert active is None, 'nested performance marker'
                active=dict(key=key,start_ns=now,start_counters=dict(counters))
            else:
                assert payload['phase']=='end' and active and active['key']==key, 'unpaired performance marker'
                row=dict(name=key[0],sample=key[1],warmup=key[2],iterations=1,start_ns=active['start_ns'],end_ns=now,
                    elapsed_ns=now-active['start_ns'],rpc_counts_within_interval={name:count-active['start_counters'].get(name,0)
                        for name,count in counters.items() if count>active['start_counters'].get(name,0)})
                timings.append(row);active=None
            return dict(is_ok=True,data=True)
        if method=='fixture.options':return dict(is_ok=True,data=dict(samples=args.samples,warmups=args.warmups))
        if method=='fixture.clock':return dict(is_ok=True,data=1791741600)
        if method=='fixture.random':serial+=1;return dict(is_ok=True,data=serial)
        if method.startswith('fixture.fs.'):
            operation=method.rsplit('.',1)[-1];path=jailed(payload['path'])
            if operation=='exists':value=path.exists()
            elif operation=='read':value=path.read_text()
            elif operation=='write':path.write_text(payload['data']);value=None
            elif operation=='mkdir':path.mkdir(parents=True,exist_ok=True);value=None
            elif operation=='sha256_file':value=sha(path.read_bytes())
            else:raise ValueError('unsupported owned IO '+operation)
            return dict(is_ok=True,data=value)
        unknown.append(request)
        raise ValueError('unconfigured backend '+method)
    try:
        with (out/'vm-stdout.log').open('w') as log:
            deadline=time.monotonic()+180
            while time.monotonic()<deadline:
                line=inbox.get(timeout=min(30,deadline-time.monotonic()))
                if line is None:break
                log.write(line);log.flush()
                if line.startswith('MUSE_VM_REQUEST '):
                    request=json.loads(line[len('MUSE_VM_REQUEST '):])
                    reply=dispatch(request)
                    vm.stdin.write(json.dumps(reply,ensure_ascii=False)+'\n');vm.stdin.flush()
                elif line.startswith('MUSE_VM_RESULT '):data=json.loads(line[len('MUSE_VM_RESULT '):])
            code=vm.wait(timeout=10)
    except Exception as exception:error=type(exception).__name__+': '+str(exception)
    finally:
        if vm.poll() is None:vm.kill();vm.wait()
        stderr.close()
    write_json(out/'samples.json',timings)
    checks=dict((data or {}).get('checks',{}))
    checks.update(actual_vm_clean=code==0 and error is None and (out/'vm-stderr.log').read_text()=='',
        actual_clock_is_monotonic=time.get_clock_info('perf_counter').monotonic,
        all_real_intervals_positive=bool(timings) and all(row['end_ns']>row['start_ns'] and row['elapsed_ns']==row['end_ns']-row['start_ns'] for row in timings),
        complete_sample_pairs=active is None and all(len([row for row in timings if row['name']==name and row['warmup']])==args.warmups
            and sorted(row['sample'] for row in timings if row['name']==name and not row['warmup'])==list(range(args.samples)) for name in NAMES),
        no_host_or_external_calls=not unknown and all(method.startswith('fixture.') for method in counters))
    failed=[name for name,value in checks.items() if value is not True]
    report=dict(status='PASS' if data and checks and not failed else 'FAIL',checks=checks,failed=failed,
        exit_code=code,error=error,probe=data,source_sha256=args.source_sha,source_identity=identity,runner_sha256=VM_SHA,
        parent_sha256=sha(Path(__file__).read_bytes()),vm_pid=vm.pid,
        measurements={name:summarize([row for row in timings if row['name']==name]) for name in NAMES if any(row['name']==name and not row['warmup'] for row in timings)},
        counters=dict(counters),unknown_calls=unknown,clock=dict(name='time.perf_counter_ns',implementation=time.get_clock_info('perf_counter').implementation,
            resolution_seconds=time.get_clock_info('perf_counter').resolution,monotonic=time.get_clock_info('perf_counter').monotonic),
        environment=dict(platform=platform.platform(),machine=platform.machine(),python=platform.python_version()),
        state_sha256={str(path.relative_to(state)):sha(path.read_bytes()) for path in sorted(state.rglob('*')) if path.is_file()},
        raw_file_sha256={name:sha((out/name).read_bytes()) for name in ['vm-stdout.log','vm-stderr.log','samples.json','executed.splash','identity.json','invocation.json']},
        full_chain_status='NOT_TESTED',boundary='One real production API call per interval in fixed official CLI VM. Parent receipt-of-start to receipt-of-end includes reply/RPC/VM scheduling; gm_context includes its real owned file audit write. Synthetic data/clock/UI/timers, no fsync guarantee. Bridge control is shown separately, not subtracted. No GUI/network/Host/Kernel/Mail/model timings.')
    write_json(out/'report.json',report)
    print(json.dumps(dict(status=report['status'],checks=len(checks),failed=failed,error=error,measurements=report['measurements']),ensure_ascii=False))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
