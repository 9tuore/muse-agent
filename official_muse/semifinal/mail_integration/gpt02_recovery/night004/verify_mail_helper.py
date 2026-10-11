#!/usr/bin/env python3
"""Verify the persistent helper against actual service replies and recipient data."""
import argparse, hashlib, json, os, subprocess, threading, queue, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--binary', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[5]
out = a.out.resolve()
out.relative_to(root / 'build')
out.mkdir(parents=True, exist_ok=False)
checks, cases = {}, {}
for mode in ('accepted', 'unknown', 'before'):
    env = dict(os.environ, NIGHT004_TMP_ROOT=str(out), NIGHT004_L3_ROOT=str(out / mode),
               NIGHT004_RECEIVER_SCRIPT=str(Path(__file__).with_name('receiver.py')))
    command = [sys.executable, str(Path(__file__).with_name('mail_helper.py')),
               '--binary', str(a.binary.resolve()), '--root', str(out / mode)]
    process = subprocess.Popen(command, env=env, text=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    responses, log, trace = queue.Queue(), [], []
    def read():
        for line in process.stdout:
            log.append(line)
            # Rust's harness prefixes the first nocapture line with the test name.
            start = line.find('{')
            if start >= 0:
                responses.put(json.loads(line[start:]))
    thread = threading.Thread(target=read)
    thread.start()
    def call(method, args=None, **controls):
        request = dict(id=len(trace)+1, method=method, args=args or {}, **controls)
        process.stdin.write(json.dumps(request)+'\n'); process.stdin.flush()
        response = responses.get(timeout=15)
        assert response['id'] == request['id']
        trace.append(dict(request=request, response=response))
        return response
    try:
        assert call('fixture.mode', mode=mode)['is_ok']
        assert call('mail.accounts')['is_ok']
        args = dict(account='one', to='receiver@example.invalid', subject='NIGHT004 synthetic', body='Protocol payload')
        draft = call('mail.compose', args)['data']
        status_args = dict(account='one', compose_id=draft['compose_id'])
        checks[mode+'_same_draft_id'] = call('mail.compose_status', status_args)['data']['compose_id'] == draft['compose_id']
        review = dict(args, compose_id=draft['compose_id'], expected_revision=draft['revision'])
        assert not call('mail.review_send', review, decision='cancel')['is_ok']
        checks[mode+'_cancel_no_delivery'] = call('fixture.receiver')['data']['received'] == []
        receipt = call('mail.review_send', review, decision='approve')
        status = call('mail.compose_status', status_args)['data']
        received = call('fixture.receiver')['data']
        expected_status = dict(accepted='accepted', unknown='outcome_unknown', before='failed_before_delivery')[mode]
        checks[mode+'_status'] = status['status'] == expected_status and receipt['is_ok'] == (mode == 'accepted')
        checks[mode+'_independent_recipient'] = len(received['received']) == (0 if mode == 'before' else 1)
        if mode != 'before':
            checks[mode+'_same_message_id'] = received['received'][0]['message_id'] == status['attempts'][-1]['payload']['message_id']
        assert not call('mail.review_send', review, decision='approve')['is_ok']
        after = call('fixture.receiver')['data']
        checks[mode+'_no_resubmit'] = after['transport_calls'] == 1 and after['received'] == received['received']
        checks[mode+'_smtp_zero'] = after['real_smtp_calls'] == 0
        call('fixture.quit')
        process.stdin.close()
        assert process.wait(timeout=10) == 0
        thread.join(timeout=10)
        cases[mode] = dict(command=command, trace=trace, status=status, recipient=after)
        (out / (mode+'-initial.txt')).write_text(''.join(log))
        # Start a new Rust service process over the same marked synthetic store.
        process = subprocess.Popen(command, env=env, text=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        responses, log = queue.Queue(), []
        thread = threading.Thread(target=read); thread.start()
        restored = call('mail.compose_status', status_args)['data']
        checks[mode+'_restart_same_id_status_attempts'] = all(restored[k] == status[k] for k in ('compose_id','status','attempts'))
        assert not call('mail.review_send', review, decision='approve')['is_ok']
        restored_receiver = call('fixture.receiver')['data']
        checks[mode+'_restart_no_resubmit'] = restored_receiver['received'] == after['received'] and restored_receiver['transport_calls'] == 0
        call('fixture.quit'); process.stdin.close()
        assert process.wait(timeout=10) == 0; thread.join(timeout=10)
        cases[mode]['restart'] = dict(status=restored, recipient=restored_receiver)
    finally:
        if process.poll() is None: process.kill(); process.wait()
        (out / (mode+'.txt')).write_text(''.join(log))
report = dict(kind='ACTUAL_MAIL_CRATE_PERSISTENT_HELPER_WITH_SYNTHETIC_REVIEW_AND_TRANSPORT',
              checks=checks, cases=cases, real_smtp_calls=0,
              binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
              boundary='Stdio helper verified; Muse full-chain integration and physical native approval are separate.')
(out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
assert checks and all(checks.values())
print(json.dumps(dict(status='HELPER_FIXTURE_PASS', checks=len(checks), binary_sha256=report['binary_sha256'])))
