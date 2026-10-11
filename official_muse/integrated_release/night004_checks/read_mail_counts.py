#!/usr/bin/env python3
"""Read official Mail draft/attempt counts from an explicitly marked fixture.

Only numeric aggregates go to stdout. No service, recovery, Vault, network, or
GUI call is made. Missing stores return zero counts with presence flags zero.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / 'build/night-004'
NAMESPACE = re.compile(r'drafts-[0-9a-f]{64}\Z')
DRAFT_FILE = re.compile(r'([A-Za-z0-9-]{1,96})\.json\Z')
STATES = ('draft', 'awaiting_approval', 'sending', 'accepted',
          'failed_before_delivery', 'outcome_unknown', 'cancelled')
CLAIMED = {'sending', 'accepted', 'failed_before_delivery', 'outcome_unknown'}
RECORD_MAX = 512 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def directory(path):
    mode = path.lstat().st_mode
    require(stat.S_ISDIR(mode), 'Fixture directory is missing, linked, or not a directory')


def marker(root):
    require(stat.S_ISREG((root / 'FIXTURE_ONLY').lstat().st_mode),
            'FIXTURE_ONLY marker missing or linked')


def guarded_root(path):
    require(path.is_absolute(), 'Fixture root must be absolute')
    relative = path.relative_to(FIXTURES)
    require(relative.parts and '..' not in relative.parts, 'Root must be below central build/night-004')
    directory(FIXTURES)
    cursor = FIXTURES
    for part in relative.parts:
        cursor /= part
        directory(cursor)
    marker(cursor)
    return cursor


def read_record(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                'Draft file is not a regular unlinked record')
        require(before.st_size <= RECORD_MAX, 'Draft exceeds official record size bound')
        with os.fdopen(fd, 'rb', closefd=False) as handle:
            raw = handle.read(RECORD_MAX + 1)
        after = os.fstat(fd)
        require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
                and len(raw) <= RECORD_MAX, 'Draft changed during the read')
        try:
            return json.loads(raw)
        except (ValueError, UnicodeError):
            raise ValueError('Invalid Mail draft JSON') from None
    finally:
        os.close(fd)


def counts(state, external=None):
    state = guarded_root(state)
    host = state / 'apps/.host'
    directory(state / 'apps')
    directory(host)
    marker(host)
    if external is not None:
        host = guarded_root(external)
        synthetic = host / 'night004-synthetic-state.txt'
        if synthetic.exists() or synthetic.is_symlink():
            require(stat.S_ISREG(synthetic.lstat().st_mode), 'Synthetic Mail marker is linked')
            require(synthetic.stat().st_size <= 128 and
                    synthetic.read_bytes() == b'NIGHT004 synthetic Mail fixture only\n',
                    'Unexpected GPT02 synthetic Mail marker')
    mail = host / 'mail'
    result = {'mail': {'draft_count': 0, 'compose_count': 0, 'accepted_count': 0,
                       'send_attempt_count': 0, 'submission_claim_count': 0,
                       'accepted_attempt_count': 0,
                       'attempts_by_status': dict.fromkeys(STATES, 0)},
              'coverage': {'state_double_marker_checked': 1,
                           'host_store_path_matches_gui_state': int(host == state / 'apps/.host'),
                           'external_mail_root_supplied': int(external is not None),
                           'mail_directory_present': 0, 'draft_namespace_count': 0,
                           'durable_mail_records_observed': 0,
                           'smtp_transport_observed': 0, 'recipient_delivery_observed': 0}}
    if not mail.exists() and not mail.is_symlink():
        return result
    directory(mail)
    result['coverage']['mail_directory_present'] = 1
    for namespace in sorted(mail.iterdir()):
        # Accounts, cached mail, contacts, secrets, and receiver data are never
        # opened. Only the production drafts namespace is enumerated.
        if not namespace.name.startswith('drafts-'):
            continue
        require(NAMESPACE.fullmatch(namespace.name), 'Unsupported Mail draft namespace')
        directory(namespace)
        result['coverage']['draft_namespace_count'] += 1
        for path in sorted(namespace.iterdir()):
            if path.suffix != '.json':
                continue  # Atomic .tmp files are outside committed-record counts.
            match = DRAFT_FILE.fullmatch(path.name)
            require(match is not None, 'Unsupported draft filename')
            record = read_record(path)
            require(isinstance(record, dict) and type(record.get('schema')) is int
                    and record['schema'] == 1 and record.get('draft_id') == match[1],
                    'Unsupported Mail draft schema or identity')
            account = record.get('account')
            require(isinstance(account, str) and
                    namespace.name == 'drafts-' + hashlib.sha256(account.encode()).hexdigest(),
                    'Draft namespace binding differs')
            require(record.get('kind') in (None, 'public_compose')
                    and record.get('status') in STATES
                    and isinstance(record.get('attempts'), list)
                    and len(record['attempts']) <= 32, 'Unsupported Mail draft ledger')
            if record['status'] == 'accepted':
                require(record['attempts'] and isinstance(record['attempts'][-1], dict)
                        and record['attempts'][-1].get('status') == 'accepted',
                        'Accepted draft has no matching terminal attempt')
            result['mail']['draft_count'] += 1
            result['mail']['compose_count'] += int(record.get('kind') == 'public_compose')
            result['mail']['accepted_count'] += int(record['status'] == 'accepted')
            for attempt in record['attempts']:
                require(isinstance(attempt, dict) and attempt.get('status') in STATES,
                        'Unsupported Mail attempt status')
                status = attempt['status']
                if status == 'accepted':
                    require(isinstance(attempt.get('receipt'), dict)
                            and attempt['receipt'].get('accepted') is True,
                            'Accepted attempt has no authoritative durable receipt')
                result['mail']['send_attempt_count'] += 1
                result['mail']['submission_claim_count'] += int(status in CLAIMED)
                result['mail']['accepted_attempt_count'] += int(status == 'accepted')
                result['mail']['attempts_by_status'][status] += 1
    result['coverage']['durable_mail_records_observed'] = int(result['mail']['draft_count'] > 0)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state_root', type=Path,
                        help='Existing absolute central build/night-004 state with two FIXTURE_ONLY markers')
    parser.add_argument('--mail-host-root', type=Path,
                        help='Explicit alternate host_dir in the same fixture base, with its own FIXTURE_ONLY marker; mail/ is appended')
    args = parser.parse_args()
    try:
        answer = counts(args.state_root, args.mail_host_root)
    except (OSError, ValueError, TypeError, KeyError):
        # Do not print decoder errors, filenames, record fields or path-derived
        # identities. A malformed/unsafe store must fail, never look empty.
        print('Mail count read refused: fixture guard, storage safety, or record schema failed.', file=sys.stderr)
        return 1
    print(json.dumps(answer, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
