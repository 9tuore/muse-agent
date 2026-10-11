#!/usr/bin/env python3
"""Focused actual process/OS durability probes, restricted to owned synthetic state."""
import argparse
import collections
import hashlib
import json
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_SHA = 'c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'
VM_SHA = 'f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351'
MAIL_SHA = 'ba37b915b24917be68964c10c38409169b7162489fbd2de22c082a1e05055367'
BODY = 'NIGHT004-L4-DURABILITY exact synthetic body'
sha = lambda data: hashlib.sha256(data).hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def run_phase(mode, phase, out, state, mail_state, prepared, vm_bin, mail_bin, receiver_script):
    out.mkdir()
    state.relative_to(ROOT / 'build')
    mail_state.relative_to(ROOT / 'build')
    marker = state / 'FIXTURE_ONLY'
    if state.exists():
        assert marker.read_text() == 'NIGHT004 CLI VM fixture only\n'
    else:
        state.mkdir(parents=True)
        marker.write_text('NIGHT004 CLI VM fixture only\n')
    identity = json.loads(prepared.with_name('identity.json').read_text())
    assert identity['source_sha256'] == SOURCE_SHA
    assert sha(prepared.read_bytes()) == identity['executed_sha256']
    env = dict(os.environ, NIGHT004_TMP_ROOT=str(ROOT / 'build'),
               NIGHT004_L3_ROOT=str(mail_state), NIGHT004_RECEIVER_SCRIPT=str(receiver_script))
    mail_log = (out / 'mail-stdout.log').open('w')
    mail = subprocess.Popen([str(mail_bin), '--exact', 'night004_l2::l3_protocol_driver',
        '--ignored', '--nocapture', '--test-threads=1'], env=env, text=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    replies = queue.Queue()
    def read_mail():
        for line in mail.stdout:
            mail_log.write(line); mail_log.flush()
            start = line.find('{')
            if start >= 0:
                try: replies.put(json.loads(line[start:]))
                except json.JSONDecodeError: pass
        replies.put(None)
    threading.Thread(target=read_mail, daemon=True).start()
    mail_id = 0
    helper_trace = []
    def mail_call(method, payload):
        nonlocal mail_id
        mail_id += 1
        request = dict(id=mail_id, method=method, args=payload)
        if method == 'mail.review_send':
            request['decision'] = 'cancel' if mode == 'review-cancel' else 'approve'
        mail.stdin.write(json.dumps(request) + '\n'); mail.stdin.flush()
        reply = replies.get(timeout=15)
        assert reply is not None and reply['id'] == mail_id, 'Actual Mail driver response missing/mismatched'
        helper_trace.append(dict(request=request, reply=reply))
        return {key: value for key, value in reply.items() if key != 'id'}
    stderr = (out / 'vm-stderr.log').open('w')
    vm = subprocess.Popen([str(vm_bin), str(prepared), '--rpc'], text=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
    lines = queue.Queue()
    def read_vm():
        for line in vm.stdout: lines.put(line)
        lines.put(None)
    threading.Thread(target=read_vm, daemon=True).start()
    counters, trace, faults = collections.Counter(), [], []
    serial_file = state / 'fixture-random.json'
    serial = json.loads(serial_file.read_text()) if serial_file.exists() else 0
    receipt_write_armed, crash_proof, data, error = False, None, None, None
    receiver_pids = []
    def jailed(path):
        target = (state / path).resolve()
        target.relative_to(state)
        assert target != state
        return target
    def dispatch(request):
        nonlocal serial, receipt_write_armed, crash_proof, receiver_pids
        method, payload = request['method'], request['payload']
        counters[method] += 1
        if method.startswith('mail.') or method in ('runtime.list', 'fixture.receiver'):
            reply = mail_call(method, payload)
            if not receiver_pids:
                processes = subprocess.run(['ps', '-axo', 'pid=,ppid=,comm='], capture_output=True, text=True, check=True)
                receiver_pids = [int(row.split(None, 2)[0]) for row in processes.stdout.splitlines()
                    if len(row.split(None, 2)) == 3 and row.split(None, 2)[1] == str(mail.pid)]
            if method == 'mail.review_send' and phase == 'initial' and mode != 'review-cancel':
                assert reply.get('is_ok') and reply['data'].get('accepted') is True
                receiver = mail_call('fixture.receiver', {})['data']
                draft = json.loads((state / 'mail-draft.json').read_text())
                goals = json.loads((state / 'goals.json').read_text())
                status = mail_call('mail.compose_status', dict(account='one', compose_id=draft['host_compose_id']))['data']
                delivery_checks = dict(actual_service_accepted=status['status'] == 'accepted',
                    one_host_attempt=len(status['attempts']) == 1,
                    one_transport=receiver['transport_calls'] == 1,
                    independent_exact_recipient=len(receiver['received']) == 1 and receiver['received'][0]['body'] == BODY,
                    no_real_smtp=receiver['real_smtp_calls'] == 0)
                assert all(delivery_checks.values()), 'Actual pre-fault delivery evidence failed'
                proof = dict(checks=delivery_checks, actual_reply=reply, actual_host_status=status,
                    actual_recipient=receiver, persisted_draft=draft, persisted_goals=goals,
                    file_sha256={name: sha((state / name).read_bytes()) for name in ('mail-draft.json', 'mail-draft.backup.json', 'goals.json')})
                if mode == 'crash-after-review':
                    proof['checks'].update(persisted_sending=draft['status'] == 'sending',
                        persisted_original_action_in_flight=len(goals['actions']) == 1 and goals['actions'][0]['status'] == 'in_flight'
                        and goals['actions'][0]['id'] == draft['request_id'] and goals['actions'][0]['payload_json'] == draft['attempt'],
                        no_fake_completion=not goals['goals'] and not goals['runs'])
                    assert all(proof['checks'].values())
                    vm.kill()
                    proof.update(signal='SIGKILL', actual_vm_exit_code=vm.wait(timeout=10), reply_forwarded=False)
                    proof['checks']['actual_sigkill_exit'] = proof['actual_vm_exit_code'] == -9
                    crash_proof = proof
                    faults.append(dict(boundary='Actual Main VM SIGKILL after actual recipient accepted and before review reply delivery', proof=proof))
                    return None
                receipt_write_armed = True
                faults.append(dict(boundary='Actual accepted service and recipient before OS receipt write fault', proof=proof))
            return reply
        if method == 'fixture.options': return dict(is_ok=True, data=dict(mode=mode))
        if method == 'fixture.counts': return dict(is_ok=True, data=dict(counters))
        if method == 'fixture.clock': return dict(is_ok=True, data=1791741600)
        if method == 'fixture.host_capabilities': return dict(is_ok=True, data=['mail'])
        if method == 'fixture.random':
            serial += 1; serial_file.write_text(json.dumps(serial))
            return dict(is_ok=True, data=serial)
        if method.startswith('fixture.fs.'):
            operation = method.rsplit('.', 1)[-1]
            target = jailed(payload['path'])
            if operation == 'exists': value = target.exists()
            elif operation == 'read': value = target.read_text()
            elif operation == 'write':
                if receipt_write_armed and payload['path'] == 'mail-draft.backup.json':
                    receipt_write_armed = False
                    original = target.read_bytes()
                    primary = state / 'mail-draft.json'
                    before = dict(primary=sha(primary.read_bytes()), backup=sha(original))
                    saved = out / 'receipt-fault-original-backup.bin'
                    target.rename(saved); target.mkdir()
                    fault = dict(boundary='Actual Path.write_text against owned backup path replaced by directory after accepted Mail reply', before_sha256=before)
                    try: target.write_text(payload['data'])
                    except OSError as exception:
                        fault.update(actual_os_error=type(exception).__name__ + ': ' + str(exception), errno=exception.errno)
                        raise
                    finally:
                        target.rmdir(); shutil.copy2(saved, target)
                        fault['after_sha256'] = dict(primary=sha(primary.read_bytes()), backup=sha(target.read_bytes()))
                        fault['primary_and_backup_preserved'] = fault['before_sha256'] == fault['after_sha256']
                        faults.append(fault)
                else: target.write_text(payload['data'])
                value = None
            elif operation == 'mkdir': target.mkdir(parents=True, exist_ok=True); value = None
            elif operation == 'sha256_file': value = sha(target.read_bytes())
            else: raise ValueError('Unsupported owned IO operation: ' + operation)
            return dict(is_ok=True, data=value)
        raise ValueError('Unconfigured backend: ' + method)
    try:
        with (out / 'vm-stdout.log').open('w') as raw:
            deadline = time.monotonic() + 100
            while time.monotonic() < deadline:
                line = lines.get(timeout=min(20, deadline - time.monotonic()))
                if line is None: break
                raw.write(line); raw.flush()
                if line.startswith('MUSE_VM_REQUEST '):
                    request = json.loads(line[len('MUSE_VM_REQUEST '):])
                    try: reply = dispatch(request)
                    except Exception as exception: reply = dict(is_ok=False, error=type(exception).__name__ + ': ' + str(exception))
                    trace.append(dict(request=request, reply=reply))
                    if crash_proof is not None: break
                    vm.stdin.write(json.dumps(reply, ensure_ascii=False) + '\n'); vm.stdin.flush()
                elif line.startswith('MUSE_VM_RESULT '):
                    data = json.loads(line[len('MUSE_VM_RESULT '):])
            exit_code = vm.wait(timeout=10)
    except Exception as exception:
        error = type(exception).__name__ + ': ' + str(exception)
        exit_code = vm.poll()
    finally:
        if vm.poll() is None: vm.kill(); vm.wait()
        try: mail_call('fixture.quit', {})
        except Exception as exception: error = error or ('Mail quit failed: ' + str(exception))
        try: mail.wait(timeout=10)
        except subprocess.TimeoutExpired: mail.kill(); mail.wait()
        stderr.close(); mail_log.close()
    checks = dict((data or {}).get('checks', {}))
    if crash_proof is not None: checks.update(crash_proof['checks'])
    if mode == 'receipt-os-error' and phase == 'initial':
        os_faults = [fault for fault in faults if 'actual_os_error' in fault]
        checks.update(actual_postacceptance_os_error=len(os_faults) == 1 and os_faults[0]['errno'] == 21,
                      receipt_primary_and_backup_preserved=len(os_faults) == 1 and os_faults[0]['primary_and_backup_preserved'])
    runtime_errors = (out / 'vm-stderr.log').read_text()
    expected_exit = -9 if mode == 'crash-after-review' and phase == 'initial' else 0
    checks.update(expected_vm_exit=exit_code == expected_exit, mail_driver_clean_exit=mail.returncode == 0,
                  no_vm_runtime_errors=runtime_errors == '', no_parent_error=error is None)
    failed = [key for key, value in checks.items() if value is not True]
    report = dict(status='PASS' if checks and not failed and (data is not None or crash_proof is not None) else 'FAIL',
        mode=mode, phase=phase, checks=checks, failed=failed, probe=data, error=error, counters=dict(counters),
        trace=trace, helper_trace=helper_trace, faults=faults, crash_proof=crash_proof,
        processes=dict(vm_pid=vm.pid, mail_pid=mail.pid, recipient_child_pids=receiver_pids,
            vm_exit_code=exit_code, mail_exit_code=mail.returncode),
        source_identity=identity, source_sha256=SOURCE_SHA, runner_sha256=sha(vm_bin.read_bytes()), mail_binary_sha256=sha(mail_bin.read_bytes()),
        state_sha256={str(path.relative_to(state)): sha(path.read_bytes()) for path in sorted(state.rglob('*')) if path.is_file()},
        state_root=str(state), mail_root=str(mail_state), full_chain_status='NOT_TESTED',
        boundary='Actual official VM, actual SDK Mail service, actual separate recipient process, SIGKILL or OS write error. UI/approval/Vault/MockTransport/timer/clock are synthetic. No Kernel/GUI/SMTP.')
    write_json(out / 'report.json', report)
    print(json.dumps(dict(mode=mode, phase=phase, status=report['status'], checks=len(checks), failed=failed)), flush=True)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runner', type=Path, required=True)
    parser.add_argument('--mail-binary', type=Path, required=True)
    parser.add_argument('--receiver-script', type=Path, required=True)
    parser.add_argument('--initial-prepared', type=Path, required=True)
    parser.add_argument('--restart-prepared', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve(); out.relative_to(ROOT / 'build'); out.mkdir(parents=True, exist_ok=False)
    assert sha(args.runner.read_bytes()) == VM_SHA
    assert sha(args.mail_binary.read_bytes()) == MAIL_SHA
    vm_bin, mail_bin = out / 'vm-bin', out / 'mail-bin'
    shutil.copy2(args.runner, vm_bin); shutil.copy2(args.mail_binary, mail_bin)
    rows = []
    for mode in ('crash-after-review', 'receipt-os-error', 'review-cancel'):
        case = out / mode; case.mkdir()
        initial = run_phase(mode, 'initial', case / 'initial', case / 'state', case / 'mail-state',
            args.initial_prepared.resolve(), vm_bin, mail_bin, args.receiver_script.resolve())
        rows.append(initial)
        if initial['status'] != 'PASS': continue
        restart = run_phase(mode, 'restart', case / 'restart', case / 'state', case / 'mail-state',
            args.restart_prepared.resolve(), vm_bin, mail_bin, args.receiver_script.resolve())
        before, after = initial['processes'], restart['processes']
        restart['checks']['new_vm_mail_recipient_processes'] = (before['vm_pid'] != after['vm_pid']
            and before['mail_pid'] != after['mail_pid'] and len(before['recipient_child_pids']) == 1
            and len(after['recipient_child_pids']) == 1 and before['recipient_child_pids'] != after['recipient_child_pids'])
        prior_receiver = (initial['crash_proof'] or (initial['probe'] or {}).get('observations', {})).get('actual_recipient')
        if prior_receiver is None: prior_receiver = initial['probe']['observations']['receiver']
        restart['checks']['same_recipient_rows_message_ids'] = prior_receiver['received'] == restart['probe']['observations']['receiver']['received'] if restart['probe'] else False
        restart['failed'] = [key for key, value in restart['checks'].items() if value is not True]
        restart['status'] = 'PASS' if not restart['failed'] else 'FAIL'
        write_json(case / 'restart' / 'report.json', restart)
        rows.append(restart)
    report = dict(status='PASS' if len(rows) == 6 and all(row['status'] == 'PASS' for row in rows) else 'FAIL',
        source_sha256=SOURCE_SHA, checks=sum(len(row['checks']) for row in rows), phases=[dict(mode=row['mode'], phase=row['phase'],
            status=row['status'], failed=row['failed'], checks=len(row['checks'])) for row in rows],
        full_chain_status='NOT_TESTED', boundary='Focused Mail durability component probes; actual process and OS faults, synthetic transport/approval. No Kernel or GUI.')
    write_json(out / 'summary.json', report)
    print(json.dumps(report), flush=True)
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__': raise SystemExit(main())
