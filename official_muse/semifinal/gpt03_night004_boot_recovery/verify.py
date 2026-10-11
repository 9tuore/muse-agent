#!/usr/bin/env python3
"""Focused recovery checks in the existing pinned VM; no GUI or time-budget claim."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'build/gpt03-night004-boot-recovery'
VM = ROOT / 'build/gpt03-night004/target/debug/gpt03-night004-vm'
FIXTURE = ROOT / 'build/gpt03-night004-perf/candidate-8227-run-r1/gui-scale-export-r1/fixture_files'
SHA = lambda data: hashlib.sha256(data).hexdigest()
write_json = lambda path, data: path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=OUT / 'checks-r1')
    parser.add_argument('--prepared', type=Path, default=OUT / 'prepared/executed.splash')
    parser.add_argument('--fixture', type=Path, default=FIXTURE)
    parser.add_argument('--runner', type=Path, default=VM)
    args = parser.parse_args()
    out = args.out.resolve()
    out.relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=False)
    prepared = args.prepared.resolve()
    identity = json.loads(prepared.with_name('identity.json').read_text())
    assert identity['source_sha256'] == 'caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce'
    assert SHA(prepared.read_bytes()) == identity['executed_sha256']
    vm_path = args.runner.resolve()
    assert SHA(vm_path.read_bytes()) == 'f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351'
    original = args.fixture.joinpath('goals.json').read_bytes()
    backup = args.fixture.joinpath('goals.backup.json').read_bytes()
    initial = json.loads(original)
    assert len(initial['actions']) == 128 and all(a['status'] == 'in_flight' for a in initial['actions'])
    cases = []
    for name, pending, failure in [('zero', 0, None), ('one', 1, None), ('full', 128, None),
                                  ('backup_write_failure', 128, 'backup_write'),
                                  ('primary_write_failure', 128, 'primary_write'),
                                  ('primary_readback_failure', 128, 'primary_readback')]:
        case = out / name
        case.mkdir(exist_ok=False)
        state = case / 'state'
        state.mkdir()
        state.joinpath('FIXTURE_ONLY').write_text('Synthetic production-API fixture; recovery only.\n')
        data = json.loads(original)
        for i, action in enumerate(data['actions']):
            if i >= pending:
                action['status'] = 'unknown'
        encoded = original if pending == 128 else json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode()
        state.joinpath('goals.json').write_bytes(encoded)
        state.joinpath('goals.backup.json').write_bytes(backup)
        before = {name: SHA(state.joinpath(name).read_bytes()) for name in ['goals.json', 'goals.backup.json']}
        operations = []
        counters = collections.Counter()
        timing = {}
        result = None
        stderr = case.joinpath('stderr.log').open('w')
        vm = subprocess.Popen([str(vm_path), str(prepared), '--rpc'],
                              text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
        for line in vm.stdout:
            if line.startswith('MUSE_VM_RESULT '):
                result = json.loads(line[len('MUSE_VM_RESULT '):])
            elif line.startswith('MUSE_VM_REQUEST '):
                request = json.loads(line[len('MUSE_VM_REQUEST '):])
                method, payload = request['method'], request['payload']
                if method == 'fixture.perf_mark':
                    timing[payload['phase']] = time.perf_counter_ns()
                    reply = {'is_ok': True, 'data': True}
                else:
                    assert method.startswith('fixture.fs.'), 'No external dispatch allowed'
                    op = method.rsplit('.', 1)[-1]
                    name = payload['path']
                    assert name in ('goals.json', 'goals.backup.json', 'current.json')
                    path = state / name
                    counters[(op, name)] += 1
                    fail = ((failure == 'backup_write' and op == 'write' and name == 'goals.backup.json')
                            or (failure == 'primary_write' and op == 'write' and name == 'goals.json')
                            or (failure == 'primary_readback' and op == 'read' and name == 'goals.json'
                                and counters[(op, name)] == 2))
                    row = {'operation': op, 'path': name, 'injected_failure': fail}
                    if 'data' in payload:
                        row.update(bytes=len(payload['data'].encode()), sha256=SHA(payload['data'].encode()))
                    operations.append(row)
                    if fail:
                        reply = {'is_ok': False, 'error': 'owned_failure_injection'}
                    else:
                        if op == 'exists': value = path.exists()
                        elif op == 'read': value = path.read_text()
                        elif op == 'write': path.write_text(payload['data']); value = None
                        else: raise AssertionError(op)
                        reply = {'is_ok': True, 'data': value}
                vm.stdin.write(json.dumps(reply, ensure_ascii=False) + '\n')
                vm.stdin.flush()
        code = vm.wait(timeout=10)
        stderr.close()
        assert code == 0 and result is not None and case.joinpath('stderr.log').read_text() == ''
        primary = json.loads(state.joinpath('goals.json').read_bytes())
        snapshot = json.loads(result['memory_snapshot'])
        expected = json.loads(encoded)
        normalized = json.loads(encoded)
        for action in normalized['actions']:
            if action['status'] == 'in_flight': action['status'] = 'unknown'
        writes = [op for op in operations if op['operation'] == 'write']
        commit_reads = [op for op in operations if op['operation'] == 'read'][1:]
        checks = dict(vm_clean=True, fixture_only_no_dispatch=True,
                      shape_unchanged=(result['goals'], result['runs'], result['actions']) == (32, 32, 128))
        if failure is None:
            checks.update(recovered=result['is_ok'] and snapshot == normalized and primary == normalized,
                          all_unknown=result['unknown'] == 128 and result['in_flight'] == 0,
                          exactly_one_commit=(len(writes), len(commit_reads)) == ((2, 2) if pending else (0, 0)))
            if pending:
                checks['backup_is_entire_prior_snapshot'] = json.loads(state.joinpath('goals.backup.json').read_bytes()) == expected
                if pending == 128:
                    checks['original_primary_bytes_preserved_as_backup'] = state.joinpath('goals.backup.json').read_bytes() == original
            else:
                checks['zero_pending_no_file_changes'] = all(SHA(state.joinpath(n).read_bytes()) == h for n, h in before.items())
        else:
            checks.update(failure_returned=not result['is_ok'] and bool(result['error']),
                          prior_memory_restored=snapshot == expected and result['in_flight'] == 128,
                          no_completed_actions=all(a['status'] == 'in_flight' for a in snapshot['actions']))
            if failure == 'backup_write':
                checks['primary_and_backup_unchanged'] = all(SHA(state.joinpath(n).read_bytes()) == h for n, h in before.items())
                checks['primary_write_not_attempted'] = len(writes) == 1
            else:
                checks['backup_preserves_original_primary_bytes'] = state.joinpath('goals.backup.json').read_bytes() == original
                checks['primary_matches_actual_write_result'] = primary == (normalized if failure == 'primary_readback' else expected)
        observation = dict(name=case.name, pending=pending, injected_failure=failure, checks=checks,
                           elapsed_ms=(timing['end'] - timing['start']) / 1e6,
                           operations=operations, commit_writes=len(writes), commit_reads=len(commit_reads),
                           before_sha256=before, after_sha256={n: SHA(state.joinpath(n).read_bytes()) for n in before},
                           ok=result['is_ok'], unknown=result['unknown'], in_flight=result['in_flight'])
        write_json(case / 'observation.json', observation)
        write_json(case / 'vm-result.json', result)
        cases.append(observation)
    report = dict(status='PASS' if all(all(c['checks'].values()) for c in cases) else 'FAIL', cases=cases,
                  checks=sum(len(c['checks']) for c in cases), fixture_primary_sha256=SHA(original),
                  vm_sha256=SHA(vm_path.read_bytes()), identity=identity,
                  verifier_sha256=SHA(Path(__file__).read_bytes()),
                  boundary='Existing actual official debug VM, 50M total instruction limit; synthetic IO failure injection. Parent perf_counter_ns includes IPC and filesystem IO. No 64ms run budget, GUI, Host, Kernel, network or business dispatch. Timing is not a GUI-budget result.')
    write_json(out / 'report.json', report)
    print(json.dumps({'status': report['status'], 'checks': report['checks'],
                      'cases': [{k: c[k] for k in ['name', 'elapsed_ms', 'commit_writes', 'commit_reads', 'ok']} for c in cases]}))
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
