#!/usr/bin/env python3
"""Verify the retained actual observations without repeating processes or side effects."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence',type=Path,default=HERE/'evidence')
parser.add_argument('--source-sha',default='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4')
parser.add_argument('--combined',action='store_true',help='Four modes in one actual 107-check run; default preserves the archived 78+29 layout')
args=parser.parse_args()
evidence=args.evidence.resolve();evidence.relative_to(HERE/'evidence')
load = lambda path: json.loads(path.read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
summary = load(evidence / 'summary.json')
if args.combined:
    assert summary['status']=='PASS' and summary['checks']==107 and len(summary['phases'])==8
    prepared_names=('initial','restart')
else:
    assert summary['status'] == 'PASS' and summary['checks'] == 78 and len(summary['phases']) == 6
    gateway_summary = load(evidence / 'gateway-summary.json')
    assert gateway_summary['status'] == 'PASS' and gateway_summary['checks'] == 29 and len(gateway_summary['phases']) == 2
    prepared_names=('initial','restart','overlap','gateway-initial')
source=args.source_sha
assert summary['source_sha256']==source
results = {}
for mode in ('crash-after-review', 'receipt-os-error', 'review-cancel', 'gateway-timeout'):
    initial = load(evidence / mode / 'initial' / 'report.json')
    restart = load(evidence / mode / 'restart' / 'report.json')
    for report in (initial, restart):
        assert report['status'] == 'PASS' and not report['failed']
        assert all(value is True for value in report['checks'].values())
        assert report['source_sha256'] == source and report['source_identity']['source_sha256'] == source
        assert report['full_chain_status'] == 'NOT_TESTED'
    assert initial['processes']['vm_pid'] != restart['processes']['vm_pid']
    assert initial['processes']['mail_pid'] != restart['processes']['mail_pid']
    assert initial['processes']['recipient_child_pids'] != restart['processes']['recipient_child_pids']
    after = restart['probe']['observations']
    assert restart['counters'].get('mail.review_send', 0) == 0
    assert after['receiver']['transport_calls'] == 0 and after['receiver']['real_smtp_calls'] == 0
    if mode != 'review-cancel':
        proof = initial['crash_proof'] or initial['faults'][0]['proof']
        recipient = proof['actual_recipient']['received']
        status = proof['actual_host_status']
        assert len(recipient) == 1 and len(status['attempts']) == 1
        assert recipient[0] == status['attempts'][0]['payload']
        assert recipient[0]['message_id'] == status['attempts'][0]['receipt']['message_id']
        assert recipient[0]['to'] == proof['persisted_draft']['to']
        assert recipient[0]['subject'] == proof['persisted_draft']['subject']
        assert recipient[0]['body'] == proof['persisted_draft']['body']
        assert recipient == after['receiver']['received']
        assert proof['persisted_draft']['status'] == 'sending'
        assert proof['persisted_goals']['actions'][0]['status'] == 'in_flight'
        assert proof['persisted_goals']['actions'][0]['id'] == proof['persisted_draft']['request_id']
        assert proof['persisted_draft']['request_id'] == after['draft']['request_id']
        assert proof['persisted_draft']['host_compose_id'] == after['draft']['host_compose_id']
        assert after['restored_before']['status'] == 'unknown' and after['draft']['status'] == 'accepted'
        if mode == 'crash-after-review':
            assert initial['processes']['vm_exit_code'] == -9 and proof['reply_forwarded'] is False
            assert initial['trace'][-1]['request']['method'] == 'mail.review_send'
            assert initial['trace'][-1]['reply'] is None
            assert not proof['persisted_goals']['goals'] and not proof['persisted_goals']['runs']
        elif mode == 'receipt-os-error':
            fault = initial['faults'][1]
            assert fault['errno'] == 21 and fault['before_sha256'] == fault['after_sha256']
            assert initial['probe']['observations']['persisted_draft']['status'] == 'sending'
            review = next(index for index, row in enumerate(initial['trace']) if row['request']['method'] == 'mail.review_send')
            failure = next(index for index, row in enumerate(initial['trace']) if row['request']['method'] == 'fixture.fs.write'
                and row['reply'].get('is_ok') is False and 'IsADirectoryError' in row['reply'].get('error', ''))
            assert review < failure
        else:
            fault = initial['faults'][0]
            assert fault['fixture_deadline_ms'] == 50 and fault['fixture_delay_ms'] == 250
            assert fault['actual_exception'] == 'Empty' and fault['actual_wait_ms'] >= 50
            assert fault['reply_enqueued_monotonic'] > fault['expired_monotonic'] > fault['started_monotonic']
            assert fault['late_reply_discarded_monotonic'] >= fault['reply_enqueued_monotonic']
            assert fault['reply_forwarded'] is False and fault['actual_late_reply'] == proof['actual_reply']
            before = initial['probe']['observations']
            assert before['draft']['status'] == 'unknown' and before['persisted_draft']['status'] == 'unknown'
            assert before['actions'][0]['status'] == 'unknown'
            assert initial['counters']['mail.review_send'] == 1
            parent_name='executed-parent-r1.py' if args.combined else 'executed-parent-gateway-r1.py'
            assert sha((evidence / parent_name).read_bytes()) == initial['parent_script_sha256']
    else:
        before = initial['probe']['observations']
        assert before['receiver']['transport_calls'] == 0 and before['receiver']['received'] == []
        assert before['draft']['status'] == 'DRAFT' and after['draft']['status'] == 'DRAFT'
        assert before['actions'][0]['status'] == 'failed' and after['actions'][0]['status'] == 'failed'
        reviews = [row for row in initial['helper_trace'] if row['request']['method'] == 'mail.review_send']
        assert len(reviews) == 1 and reviews[0]['request']['decision'] == 'cancel'
        assert reviews[0]['reply']['is_ok'] is False and 'cancelled' in reviews[0]['reply']['error']
    results[mode] = 'PASS'
for name in prepared_names:
    prepared = evidence / (name + '-prepare')
    identity = load(prepared / 'identity.json')
    assert identity['source_sha256'] == source
    assert sha((prepared / 'executed.splash').read_bytes()) == identity['executed_sha256']
print(json.dumps(dict(status='PASS', phases=8, runtime_checks=107, exact_delivery_and_fault_boundary_audit=results,
    note='Evidence revalidation only; no additional runtime or business PASS counted.')))
