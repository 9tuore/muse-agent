#!/usr/bin/env python3
"""Exercise the real reader CLIs with disposable marked synthetic stores."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SENTINEL = 'SYNTHETIC_CONTENT_MUST_NOT_APPEAR'
checks = []


def mark(path):
    (path / 'apps/.host').mkdir(parents=True)
    (path / 'FIXTURE_ONLY').touch()
    (path / 'apps/.host/FIXTURE_ONLY').touch()
    return path


def numeric(value):
    assert isinstance(value, dict) and value
    for item in value.values():
        if isinstance(item, dict):
            numeric(item)
        else:
            assert type(item) is int and item >= 0


def invoke(label, state, success=True, reader='read_business_counts.py', extra=()):
    result = subprocess.run([sys.executable, str(HERE / reader), str(state), *map(str, extra)],
                            text=True, capture_output=True, timeout=10)
    assert (result.returncode == 0) == success, (label, result.stderr)
    assert SENTINEL not in result.stdout + result.stderr
    assert not result.stdout if not success else True
    value = json.loads(result.stdout) if success else None
    if value is not None:
        numeric(value)
    checks.append({'case': label, 'status': 'PASS', 'exit_code': result.returncode})
    return value


def event(event_id):
    return {'id': event_id, 'title': SENTINEL, 'start': '2026-10-13T12:00',
            'end': None, 'location': '', 'notes': '', 'request_id': '', 'timezone': ''}


def main():
    base = ROOT / 'build/night006'
    legacy = ROOT / 'build/night-004'
    base.mkdir(parents=True, exist_ok=True)
    legacy.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='business-counter-check-', dir=base) as temporary:
        samples = Path(temporary)
        state = mark(samples / 'absent')
        value = invoke('night006_absent_stores_numeric_zero', state)
        assert value['calendar']['event_count'] == value['calendar']['store_present'] == 0
        assert value['mail']['send_attempt_count'] == 0
        invoke('night006_mail_reader_accepted', state, reader='read_mail_counts.py')
        calendar = state / 'apps/.host/calendar'
        calendar.mkdir()
        assert invoke('missing_calendar_file_has_presence_zero', state)['calendar']['directory_present'] == 1
        store = calendar / 'events.json'
        store.write_text('[]')
        assert invoke('empty_store_is_present', state)['calendar']['store_present'] == 1
        store.write_text(json.dumps([event('event-' + str(i)) for i in range(51)]))
        before = (store.read_bytes(), store.stat().st_mtime_ns)
        assert invoke('all_51_events_counted_without_service_limit', state)['calendar']['event_count'] == 51
        assert (store.read_bytes(), store.stat().st_mtime_ns) == before
        bad = {'bad_json': '[', 'not_a_list': '{}', 'duplicate_ids': json.dumps([event('same'), event('same')]),
               'duplicate_json_keys': '[{"id":"a","id":"b","title":"x","start":"x"}]',
               'nonstandard_constant': '[NaN]', 'excessive_json_nesting': '[' * 2000 + ']' * 2000,
               'wrong_id_type': json.dumps([event(4)]),
               'invalid_id': json.dumps([event('../x')]), 'missing_fields': '[{"id":"a"}]',
               'too_many_events': json.dumps([event('e-' + str(i)) for i in range(501)])}
        for label, content in bad.items():
            store.write_text(content)
            invoke(label + '_refused', state, False)
        store.unlink()
        target = samples / 'synthetic-calendar.json'
        target.write_text(json.dumps([event('linked')]))
        store.symlink_to(target)
        invoke('linked_store_refused', state, False)
        store.unlink()
        os.link(target, store)
        invoke('hardlinked_store_refused', state, False)
        store.unlink()
        calendar.rmdir()
        calendar.symlink_to(samples, target_is_directory=True)
        invoke('linked_calendar_directory_refused', state, False)
        calendar.unlink()
        alias = samples / 'alias'
        alias.symlink_to(state, target_is_directory=True)
        invoke('linked_state_refused', alias, False)
        (state / 'FIXTURE_ONLY').unlink()
        invoke('missing_state_marker_refused', state, False)
        (state / 'FIXTURE_ONLY').touch()
        (state / 'apps/.host/FIXTURE_ONLY').unlink()
        invoke('missing_owner_marker_refused', state, False)
        (state / 'apps/.host/FIXTURE_ONLY').touch()
        invoke('nonfixture_root_refused', ROOT, False)
        invoke('relative_root_refused', Path('relative'), False)
        invoke('traversal_refused', state / '..' / state.name, False)
        with tempfile.TemporaryDirectory(prefix='business-counter-check-', dir=legacy) as old:
            old_state = mark(Path(old) / 'state')
            invoke('night004_business_reader_retained', old_state)
            invoke('night004_mail_reader_retained', old_state, reader='read_mail_counts.py')
            invoke('alternate_mail_base_cannot_cross_fixture_namespaces', state, False,
                   reader='read_mail_counts.py', extra=('--mail-host-root', old_state / 'apps/.host'))
    print(json.dumps({'status': 'PASS', 'checks': checks, 'scope': 'Disposable synthetic CLI fixtures only',
                      'existing_profiles_opened': 0, 'gui_actions': 0,
                      'reader_sha256': hashlib.sha256((HERE / 'read_business_counts.py').read_bytes()).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
