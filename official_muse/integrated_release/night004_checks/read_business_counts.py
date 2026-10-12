#!/usr/bin/env python3
"""Read numeric Mail/Calendar owner-store counters from a marked fixture.

Filesystem readback only, not Calendar RPC, SMTP observation, or business
execution evidence. No account, Vault, profile, network or GUI calls are made.
"""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys

import read_mail_counts as mail

MAX_BYTES = 4 * 1024 * 1024
EVENT_ID = re.compile(r'[A-Za-z0-9_-]{1,64}\Z')
EVENT_FIELDS = {'id', 'title', 'start', 'end', 'location', 'notes', 'request_id', 'timezone'}


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        mail.require(key not in value, 'Duplicate Calendar JSON key')
        value[key] = item
    return value


def invalid_constant(_):
    raise ValueError('Nonstandard Calendar JSON constant')


def calendar_counts(state):
    result = {'event_count': 0, 'directory_present': 0, 'store_present': 0,
              'durable_events_observed': 0, 'owner_store_readback': 1,
              'service_api_called': 0, 'writes': 0}
    calendar = state / 'apps/.host/calendar'
    try:
        mail.directory(calendar)
    except FileNotFoundError:
        return result
    result['directory_present'] = 1
    try:
        fd = os.open(calendar / 'events.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return result
    try:
        before = os.fstat(fd)
        mail.require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                     'Calendar store must be a regular unlinked file')
        mail.require(before.st_size <= MAX_BYTES, 'Calendar store exceeds read bound')
        with os.fdopen(fd, 'rb', closefd=False) as handle:
            raw = handle.read(MAX_BYTES + 1)
        after = os.fstat(fd)
        mail.require((before.st_size, before.st_mtime_ns, before.st_ino, before.st_dev)
                     == (after.st_size, after.st_mtime_ns, after.st_ino, after.st_dev)
                     and len(raw) <= MAX_BYTES, 'Calendar store changed during read')
    finally:
        os.close(fd)
    events = json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    mail.require(isinstance(events, list) and len(events) <= 500, 'Invalid Calendar event list')
    seen = set()
    for event in events:
        mail.require(isinstance(event, dict) and not set(event) - EVENT_FIELDS,
                     'Unsupported Calendar event fields')
        mail.require(all(isinstance(event.get(key), str) for key in ('id', 'title', 'start')),
                     'Invalid Calendar event identity or required fields')
        event_id = event['id']
        mail.require(EVENT_ID.fullmatch(event_id) and event_id not in seen,
                     'Invalid or ambiguous Calendar event identity')
        seen.add(event_id)
        mail.require(all(key not in event or isinstance(event[key], str)
                         for key in ('location', 'notes', 'request_id', 'timezone'))
                     and (event.get('end') is None or isinstance(event['end'], str)),
                     'Invalid Calendar event field types')
    result.update(event_count=len(events), store_present=1, durable_events_observed=int(bool(events)))
    return result


def counts(state):
    # The Mail reader enforces both markers and every state/host directory
    # before either owner store is opened. Its output excludes private fields.
    answer = mail.counts(state)
    answer['calendar'] = calendar_counts(state)
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state_root', type=Path,
                        help='Existing absolute NIGHT-004/NIGHT-006 state with two FIXTURE_ONLY markers')
    args = parser.parse_args()
    try:
        answer = counts(args.state_root)
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print('Business count read refused: fixture guard, storage safety, or record schema failed.',
              file=sys.stderr)
        return 1
    print(json.dumps(answer, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
