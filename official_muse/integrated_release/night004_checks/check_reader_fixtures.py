#!/usr/bin/env python3
"""CLI checks using newly created marked samples; never opens existing state."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
READER = HERE / 'read_mail_counts.py'
BASE = HERE.parents[2] / 'build/night-004'
SENTINEL = 'SYNTHETIC_PRIVATE_CONTENT_MUST_NOT_APPEAR'
checks = []


def mark(state):
    (state / 'apps/.host').mkdir(parents=True)
    (state / 'FIXTURE_ONLY').touch()
    (state / 'apps/.host/FIXTURE_ONLY').touch()
    return state


def namespace(host):
    path = host / ('mail/drafts-' + hashlib.sha256(b'fixture-account').hexdigest())
    path.mkdir(parents=True, exist_ok=True)
    return path


def draft(name, status='draft', attempts=(), public=False):
    value = {'schema': 1, 'draft_id': name, 'account': 'fixture-account',
             'publisher': 'fixture-app' if public else 'os.mail', 'revision': 2,
             'status': status, 'attempts': list(attempts), 'suggestions': [],
             'source_message': {}, 'email': {}, 'from': 'fixture@example.invalid',
             'to': 'recipient@example.invalid', 'subject': SENTINEL, 'body': SENTINEL,
             'in_reply_to': '', 'references': '', 'chat_thread': '', 'body_origin': 'app'}
    if public:
        value['kind'] = 'public_compose'
    return value


def attempt(name, status):
    value = {'operation_id': name, 'revision': 2, 'status': status,
             'payload': {'from': 'fixture@example.invalid', 'to': 'recipient@example.invalid',
                         'subject': SENTINEL, 'body': SENTINEL, 'in_reply_to': '',
                         'references': '', 'message_id': '<synthetic@example.invalid>'}}
    if status == 'accepted':
        value['receipt'] = {'accepted': True}
    return value


def invoke(label, state, success=True, extra=()):
    reply = subprocess.run([sys.executable, str(READER), str(state), *map(str, extra)],
                           capture_output=True, text=True)
    assert (reply.returncode == 0) == success, label
    assert SENTINEL not in reply.stdout + reply.stderr, label
    assert 'recipient@example.invalid' not in reply.stdout + reply.stderr, label
    assert 'fixture@example.invalid' not in reply.stdout + reply.stderr, label
    assert not reply.stdout if not success else True, label
    value = json.loads(reply.stdout) if success else None
    checks.append({'case': label, 'exit_code': reply.returncode, 'status': 'PASS',
                   'content_output_absent': True})
    return value


def main():
    require_base = BASE.is_dir() and not BASE.is_symlink()
    assert require_base, 'Central NIGHT-004 fixture base must already exist'
    with tempfile.TemporaryDirectory(prefix='gpt05-counter-samples-', dir=BASE) as temporary:
        samples = Path(temporary)
        state = mark(samples / 'absent')
        absent = invoke('missing_mail_directory_returns_zero_with_absence_flags', state)
        assert absent['mail']['draft_count'] == absent['mail']['send_attempt_count'] == 0
        assert absent['coverage']['mail_directory_present'] == 0
        assert absent['coverage']['durable_mail_records_observed'] == 0
        assert absent['coverage']['smtp_transport_observed'] == 0
        (state / 'apps/.host/mail').mkdir()
        empty = invoke('existing_empty_mail_directory_still_no_durable_records', state)
        assert empty['coverage']['mail_directory_present'] == 1
        assert empty['coverage']['durable_mail_records_observed'] == 0

        state = mark(samples / 'records')
        ns = namespace(state / 'apps/.host')
        records = [draft('reply-a'),
                   draft('composer-a', 'accepted', [attempt('send-a', 'cancelled'),
                         attempt('send-b', 'accepted')], public=True),
                   draft('composer-b', 'outcome_unknown', [attempt('send-c', 'outcome_unknown')], public=True),
                   draft('composer-c', 'awaiting_approval', [attempt('send-d', 'awaiting_approval')], public=True)]
        for record in records:
            (ns / (record['draft_id'] + '.json')).write_text(json.dumps(record))
        # Deliberately invalid unrelated data demonstrates these files are not parsed.
        for name in ('accounts.json', 'box-fixture.json', 'contacts.json', 'secrets.json'):
            (ns.parent / name).write_text(SENTINEL)
        (ns / 'interrupted.tmp').write_text(SENTINEL)
        value = invoke('production_record_shape_aggregates_without_unrelated_file_reads', state)
        assert {key: value['mail'][key] for key in ('draft_count', 'compose_count', 'accepted_count',
                    'send_attempt_count', 'submission_claim_count', 'accepted_attempt_count')} == {
                    'draft_count': 4, 'compose_count': 3, 'accepted_count': 1,
                    'send_attempt_count': 4, 'submission_claim_count': 2, 'accepted_attempt_count': 1}
        assert value['coverage']['durable_mail_records_observed'] == 1
        assert value['coverage']['recipient_delivery_observed'] == 0

        for label in ('malformed_json', 'unsupported_schema', 'wrong_account_namespace',
                      'accepted_without_receipt', 'accepted_without_attempt',
                      'symlink_record', 'hardlink_record'):
            state = mark(samples / label)
            ns = namespace(state / 'apps/.host')
            file = ns / 'reply-a.json'
            record = draft('reply-a')
            if label == 'malformed_json':
                file.write_text('{"body":"' + SENTINEL)
            elif label == 'unsupported_schema':
                record['schema'] = 2
                file.write_text(json.dumps(record))
            elif label == 'wrong_account_namespace':
                record['account'] = 'other-fixture-account'
                file.write_text(json.dumps(record))
            elif label == 'accepted_without_receipt':
                record['status'] = 'accepted'
                record['attempts'] = [{'status': 'accepted'}]
                file.write_text(json.dumps(record))
            elif label == 'accepted_without_attempt':
                record['status'] = 'accepted'
                file.write_text(json.dumps(record))
            elif label == 'symlink_record':
                target = state / 'synthetic-target'
                target.write_text(json.dumps(record))
                file.symlink_to(target)
            else:
                file.write_text(json.dumps(record))
                os.link(file, state / 'synthetic-hardlink')
            invoke(label + '_refused_without_content_output', state, success=False)

        state = mark(samples / 'marker-tests')
        (state / 'FIXTURE_ONLY').unlink()
        invoke('missing_state_marker_refused', state, success=False)
        (state / 'FIXTURE_ONLY').touch()
        (state / 'apps/.host/FIXTURE_ONLY').unlink()
        invoke('missing_host_marker_refused', state, success=False)
        invoke('root_outside_central_night004_refused', HERE, success=False)
        invoke('relative_root_refused', Path('relative-state'), success=False)

        state = mark(samples / 'external-state')
        external = samples / 'external-mail-host'
        external.mkdir()
        (external / 'FIXTURE_ONLY').touch()
        marker = external / 'night004-synthetic-state.txt'
        marker.write_text('NIGHT004 synthetic Mail fixture only\n')
        value = invoke('explicit_guarded_external_mail_host_does_not_claim_gui_store', state,
                       extra=('--mail-host-root', external))
        assert value['coverage']['external_mail_root_supplied'] == 1
        assert value['coverage']['host_store_path_matches_gui_state'] == 0
        marker.write_text('wrong synthetic marker\n')
        invoke('wrong_external_synthetic_marker_refused', state, success=False,
               extra=('--mail-host-root', external))
    report = {'status': 'PASS', 'checks': checks, 'sample_cases_only': True,
              'existing_fixture_states_read': 0, 'gui_actions': 0, 'host_startups': 0,
              'cargo_builds': 0, 'keychain_accesses': 0}
    (HERE / 'sample-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'checks': len(checks), 'sample_cases_only': True}))


if __name__ == '__main__':
    main()
