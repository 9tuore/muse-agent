#!/usr/bin/env python3
"""Same-data A/B/B/A slice check in the existing VM, not a GUI budget test."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def execute(vm_path, prepared, memory_path, directory):
    directory.mkdir()
    state = directory / 'state'
    state.mkdir()
    shutil.copy2(memory_path, state / 'memory.json')
    (state / 'FIXTURE_ONLY').write_text('SPRINT005 ZC03 pure Memory validation fixture\n')
    before = SHA(state / 'memory.json')
    marks, outcomes, checks, active = [], [], {}, None
    error_file = (directory / 'stderr.log').open('w')
    child = subprocess.Popen([str(vm_path), str(prepared), '--rpc'], text=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=error_file)
    result = None
    try:
        for line in child.stdout:
            if line.startswith('MUSE_VM_RESULT '):
                result = json.loads(line[len('MUSE_VM_RESULT '):])
                continue
            assert line.startswith('MUSE_VM_REQUEST '), 'Unexpected VM output'
            request = json.loads(line[len('MUSE_VM_REQUEST '):])
            method, payload = request['method'], request['payload']
            if method == 'fixture.fs.read':
                assert payload['path'] == 'memory.json'
                reply = dict(is_ok=True, data=(state / 'memory.json').read_text())
            elif method == 'fixture.mark':
                now = time.perf_counter_ns()
                key = (payload['phase'], payload['start'])
                if payload['edge'] == 'start':
                    assert active is None
                    active = key, now
                else:
                    assert payload['edge'] == 'end' and active and active[0] == key
                    marks.append(dict(phase=key[0], start=key[1], start_ns=active[1], end_ns=now,
                                      elapsed_ns=now-active[1]))
                    active = None
                reply = dict(is_ok=True, data=True)
            elif method == 'fixture.check':
                assert payload['name'] not in checks
                checks[payload['name']] = payload['value']
                reply = dict(is_ok=True, data=True)
            elif method == 'fixture.outcome':
                outcomes.append(payload)
                reply = dict(is_ok=True, data=True)
            else:
                raise AssertionError('No writes, clocks, Host or business dispatch: ' + method)
            child.stdin.write(json.dumps(reply, ensure_ascii=False) + '\n')
            child.stdin.flush()
        code = child.wait(timeout=10)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        error_file.close()
    assert code == 0 and (directory / 'stderr.log').read_text() == '', 'actual VM failure'
    assert result == dict(completed=True, sources=128, claims=64)
    assert len(marks) == 96 and len(outcomes) == 22 and len(checks) == 98 and all(checks.values())
    assert active is None and SHA(state / 'memory.json') == before
    record = dict(checks=checks, outcomes=outcomes, samples=marks, memory_sha256=before,
                  vm_pid=child.pid, result=result, source_identity=json.loads(prepared.with_name('identity.json').read_text()))
    (directory / 'result.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return record


def summarize(records, phase):
    ns = [r['elapsed_ns'] for record in records for r in record['samples'] if r['phase'] == phase]
    ordered = sorted(ns)
    return dict(samples=len(ns), median_ms=statistics.median(ns)/1e6,
                p95_ms=ordered[(95*len(ns)+99)//100-1]/1e6, max_ms=max(ns)/1e6,
                total_callback_intervals_ms=sum(ns)/1e6)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--fixture-memory', type=Path, required=True)
    p.add_argument('--vm', type=Path, required=True)
    p.add_argument('--vm-identity', type=Path, default=HERE / 'evidence/vm-build-identity.json')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    identity = json.loads((HERE / 'evidence/source-identity.json').read_text())
    assert SHA(a.baseline) == identity['baseline_source_sha256']
    assert SHA(a.candidate) == identity['performance_candidate_sha256']
    vm_identity = json.loads(a.vm_identity.read_text())
    assert SHA(a.vm) == vm_identity['binary_sha256']
    assert SHA(HERE / 'vm/src/main.rs') == vm_identity['driver_source_sha256']
    dataset = json.loads(a.fixture_memory.read_text())
    assert (len(dataset['claims']), len(dataset['sources']), len(dataset['forget'])) == (64, 128, 0)
    out = a.out.resolve()
    out.relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=False)
    prepare = ROOT / 'official_muse/semifinal/gpt03_night004_perf/prepare.py'
    prepared = {}
    for name, source in [('baseline', a.baseline), ('candidate', a.candidate)]:
        target = out / (name + '-prepare')
        subprocess.run(['python3', '-B', str(prepare), '--source', str(source), '--source-sha', SHA(source),
                        '--probe', str(HERE / 'memory_probe.splash'), '--out', str(target)], check=True)
        prepared[name] = target / 'executed.splash'
    records = []
    for i, name in enumerate(['baseline', 'candidate', 'candidate', 'baseline']):
        record = execute(a.vm.resolve(), prepared[name], a.fixture_memory, out / f'{i+1}-{name}')
        record['variant'] = name
        records.append(record)
    baseline = records[0]['source_identity']
    candidate = records[1]['source_identity']
    for field in ['production_function_sha256', 'production_global_sha256']:
        x, y = baseline[field], candidate[field]
        assert x.keys() == y.keys()
        changed = sorted(k for k in x if x[k] != y[k])
        assert changed == (['gm_validate_indexed_part'] if field == 'production_function_sha256' else [])
    checks = dict(same_dataset=all(r['memory_sha256'] == SHA(a.fixture_memory) for r in records),
                  all_valid_slices=all(all(r['checks'].values()) for r in records),
                  identical_edge_and_invalid_outcomes=all(r['outcomes'] == records[0]['outcomes'] for r in records),
                  only_one_production_function_changed=True,
                  all_globals_byte_equal=True, no_writes_or_dispatch=True,
                  exact_batch2_workload=all(len(r['samples']) == 96 for r in records))
    measurements = {name: {phase: summarize([r for r in records if r['variant'] == name], phase)
                          for phase in ['sources', 'claims']} for name in ['baseline', 'candidate']}
    report = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  source_identity=identity, dataset_sha256=SHA(a.fixture_memory), vm_sha256=SHA(a.vm),
                  vm_build_identity=vm_identity,
                  order=['baseline', 'candidate', 'candidate', 'baseline'], measurements=measurements,
                  compiler_sha256=SHA(prepare), runner_sha256=SHA(Path(__file__)),
                  environment=dict(platform=platform.platform(), clock=time.get_clock_info('perf_counter').implementation,
                                   instruction_limit=50_000_000, time_budget=None, isolated_system_load=False),
                  outcomes=records[0]['outcomes'],
                  boundary='New focused pure validator check. Same actual API-generated 64/128 fixture, same cached debug VM and marker method. Parent intervals include RPC/scheduling; no GUI, 64ms budget, timers, bootstrap latency, Kernel, provider or business result is claimed.')
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], checks=checks, measurements=measurements)))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
