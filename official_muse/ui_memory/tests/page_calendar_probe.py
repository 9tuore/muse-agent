#!/usr/bin/env python3
"""Real 8483 card-host executes the owned Splash adapter; synthetic events only.
Python datetime provides an independent date/time projection oracle.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'official_muse/ui_page_adapters.splash'
HOST = Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/release/card-host')
ZONE = timezone(timedelta(hours=8))


def event(key, start, end):
    return dict(id=key, calendar_id='synthetic-calendar', title='合成日程-'+key,
                start=start, end=end, time_zone='UTC', location='synthetic',
                last_modified=0, version='synthetic-version-'+key)


EVENTS = [
    event('later', '2026-10-03T10:30:00Z', '2026-10-03T11:30:00Z'),
    event('utc-rollover', '2026-10-02T17:00:00Z', '2026-10-02T18:00:00Z'),
    event('negative-offset', '2026-10-02T23:00:00-07:00', '2026-10-03T00:00:00-07:00'),
    event('half-hour-offset', '2026-10-03T01:00:00+05:30', '2026-10-03T02:00:00+05:30'),
    event('midnight-end', '2026-10-04T23:00:00+08:00', '2026-10-05T00:00:00+08:00'),
    event('span', '2026-09-30T22:00:00+08:00', '2026-10-02T02:00:00+08:00'),
    event('fraction', '2026-10-05T00:00:00.100+08:00', '2026-10-05T00:00:00.200+08:00'),
    event('out-of-month', '2026-11-01T00:00:00+08:00', '2026-11-02T00:00:00+08:00'),
    event('same-start-a', '2026-10-03T10:30:00Z', '2026-10-03T11:30:00Z'),
    event('missing-offset', '2026-10-06T10:00:00', '2026-10-06T11:00:00'),
    event('invalid-date', '2026-02-30T10:00:00Z', '2026-03-02T10:00:00Z'),
    event('empty-interval', '2026-10-06T10:00:00Z', '2026-10-06T10:00:00Z'),
    event('reversed', '2026-10-06T11:00:00Z', '2026-10-06T10:00:00Z'),
]


def projected(events, view, cursor):
    d = date.fromisoformat(cursor)
    if view == 'week':
        first = d - timedelta(days=d.weekday())
        end = first + timedelta(days=7)
        grid = first
        count = 7
        label = f'{first} — {end-timedelta(days=1)}'
    else:
        first = d.replace(day=1)
        end = (first.replace(day=28)+timedelta(days=4)).replace(day=1)
        grid = first if view == 'agenda' else first-timedelta(days=first.weekday())
        count = (end-first).days if view == 'agenda' else 42
        label = f'{d.year}年{d.month}月'
    valid, skipped = [], 0
    for e in events:
        try:
            start = datetime.fromisoformat(e['start'].replace('Z', '+00:00'))
            finish = datetime.fromisoformat(e['end'].replace('Z', '+00:00'))
            if start.tzinfo is None or finish.tzinfo is None or finish <= start:
                raise ValueError('invalid event interval')
            valid.append((start, finish, e))
        except ValueError:
            skipped += 1
    rows = []
    for n in range(count):
        day = grid + timedelta(days=n)
        outside = day < first or day >= end
        t0 = datetime.combine(day, datetime.min.time(), ZONE)
        matches = [] if outside else [e for s, f, e in valid if s < t0+timedelta(days=1) and f > t0]
        if view != 'agenda' or matches:
            rows.append(dict(date=str(day), day=day.day, weekday=day.weekday(), outside=outside, events=matches))
    return dict(view=view, cursor=cursor, label=label,
                start=f'{first}T00:00:00+08:00', end=f'{end}T00:00:00+08:00',
                time_zone='Asia/Shanghai (UTC+08:00)', error='', skipped=skipped, rows=rows)


def run(output, port):
    source = SOURCE.read_text()
    # Render/resize callers can safely repeat: adapter contains no effectful APIs.
    forbidden = ('host.', 'fs.', 'ui.', 'start_timeout(', 'model.complete', 'redraw(')
    assert not any(symbol in source for symbol in forbidden), 'effectful symbol in display adapter'
    with socket.socket() as check:
        check.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        check.bind(('127.0.0.1', port))
    output.mkdir(parents=True, exist_ok=True)
    bundle, state = output / 'bundle', output / 'state'
    bundle.mkdir(exist_ok=True)
    if (state / 'muse-goals/page-probe.json').exists():
        raise FileExistsError('Choose a fresh output directory; prior evidence is preserved')
    (bundle / 'manifest.json').write_text(json.dumps(dict(schema=1, id='muse-goals', name='Muse 页面合成探针',
                                                          version='0.2.26', capabilities=['storage'])))
    cases, expectations = [], {}
    for view in ('month', 'week', 'agenda'):
        for cursor in ('2026-10-03', '2024-02-29', '2025-02-28', '2026-12-31', '2027-01-01', '1900-03-01', '2000-02-29'):
            key = f'{view}-{cursor}'
            cases.append(dict(key=key, events=EVENTS, view=view, cursor=cursor))
            expectations[key] = projected(EVENTS, view, cursor)
    host_max = [event(f'limit-{n:03}', f'2026-10-{n % 31 + 1:02}T09:00:00+08:00', f'2026-10-{n % 31 + 1:02}T10:00:00+08:00') for n in range(99, -1, -1)]
    host_span = [event(f'span-limit-{n:03}', '2026-09-30T00:00:00Z', '2026-11-02T00:00:00Z') for n in range(100)]
    cases.insert(0, dict(key='host-limit-100-span', events=host_span, view='month', cursor='2026-10-03'))
    expectations['host-limit-100-span'] = projected(host_span, 'month', '2026-10-03')
    cases.insert(0, dict(key='host-limit-100', events=host_max, view='month', cursor='2026-10-03'))
    expectations['host-limit-100'] = projected(host_max, 'month', '2026-10-03')
    cases.append(dict(key='empty-agenda', events=[], view='agenda', cursor='2026-10-03'))
    expectations['empty-agenda'] = projected([], 'agenda', '2026-10-03')
    cases.append(dict(key='nil-events', events=None, view='month', cursor='2026-10-03'))
    expectations['nil-events'] = projected([], 'month', '2026-10-03')
    for cursor in ('2026-02-30', '2026-13-01', '2026-10-00', '2026-1-03', '2026-10- 3', '', '1899-12-31'):
        cases.append(dict(key='invalid-'+cursor, events=[], view='month', cursor=cursor))
    cases.append(dict(key='invalid-view', events=EVENTS, view='year', cursor='2026-10-03'))
    moves = [
        ('2026-01-31', 'month', 1, '2026-02-28'), ('2024-01-31', 'month', 1, '2024-02-29'),
        ('2026-12-31', 'month', 1, '2027-01-31'), ('2027-01-31', 'agenda', -1, '2026-12-31'),
        ('2026-10-03', 'week', -1, '2026-09-26'), ('2026-12-31', 'week', 1, '2027-01-07'),
        ('2026-10-03', 'month', 0, '2026-10-03'), ('2026-10-03', 'year', 1, '2026-10-03'),
        ('2026-02-30', 'month', 1, ''), ('1900-01-01', 'month', -1, ''),
    ]
    readiness = [
        ('calendar-off', 'page_calendar_readiness(false,"full_access","synthetic")', False),
        ('calendar-write-only', 'page_calendar_readiness(true,"write_only","synthetic")', False),
        ('calendar-full-no-target', 'page_calendar_readiness(true,"full_access","")', False),
        ('calendar-full', 'page_calendar_readiness(true,"full_access","synthetic")', True),
        ('calendar-undetermined', 'page_calendar_readiness(true,"not_determined","")', False),
        ('calendar-denied', 'page_calendar_readiness(true,"denied","")', False),
        ('mail-off', 'page_mail_readiness(false,"synthetic",true)', False),
        ('mail-no-account', 'page_mail_readiness(true,"",true)', False),
        ('mail-pending', 'page_mail_readiness(true,"synthetic",false)', False),
        ('mail-connected', 'page_mail_readiness(true,"synthetic",true)', True),
    ]
    script = source + '\nlet page_cases = ' + json.dumps(json.dumps(cases, ensure_ascii=False)) + '.parse_json()\n'
    script += 'let results = []\nlet page_inputs_before = page_cases.to_json()\nfn page_probe_case(index){\nif index >= page_cases.len() { page_probe_finish() return }\nlet c = page_cases[index]\nfs.write("page-progress.json",{index: index key: c.key}.to_json())\nresults.push({key: c.key data: calendar_display_rows(c.events,c.view,c.cursor)})\nif c.events == nil || c.events.len() < 100 { for repeat in 2 { calendar_display_rows(c.events,c.view,c.cursor) } }\nstart_timeout(0.02,|| page_probe_case(index + 1))\n}\nfn page_probe_finish(){\n'
    script += 'let moves = []\n'
    for cursor, view, step, expected in moves:
        script += f'moves.push(calendar_display_move("{cursor}","{view}",{step}))\n'
    formats = [('2026-10-02T17:00:00Z', '2026-10-03 01:00 +08:00'), ('2026-10-02T23:00:00-07:00', '2026-10-03 14:00 +08:00'), ('2026-10-03T01:00:00+05:30', '2026-10-03 03:30 +08:00'), ('2026-02-30T10:00:00Z', '')]
    script += 'let formats = []\n'
    for value, expected in formats:
        script += f'formats.push(calendar_display_time("{value}"))\n'
    script += 'let readiness = []\n'
    for key, expression, expected in readiness:
        script += f'readiness.push({expression})\n'
    script += 'fs.write("page-probe.json",{results: results moves: moves formats: formats readiness: readiness today: calendar_display_today() unchanged: page_inputs_before == page_cases.to_json()}.to_json())\n}\n'
    script += 'start_timeout(0.05,|| page_probe_case(0))\nView{width: Fill height: Fill Label{text: "Muse 日历纯显示合成探针"}}\n'
    (bundle / 'main.splash').write_text(script)
    env = dict(os.environ, MAKEPAD_REMOTE=str(port), MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    with (output / 'runtime.log').open('w') as log:
        proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(state),
                                 '--allow-unsigned', '--stamp', '--size', '600x700'],
                                env=env, cwd=HOST.parents[2], stdout=log, stderr=log)
        try:
            result_path = state / 'muse-goals/page-probe.json'
            deadline = time.monotonic() + 25
            while not result_path.exists():
                if proc.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError((output / 'runtime.log').read_text()[-8000:])
                time.sleep(.2)
            results = json.loads(result_path.read_text())
            checks = {}
            for entry in results['results']:
                key, actual = entry['key'], entry['data']
                if key in expectations:
                    checks[key] = actual == expectations[key]
                else:
                    checks[key] = bool(actual['error']) and actual['rows'] == []
                if not checks[key]:
                    print(json.dumps(dict(key=key, actual=actual, expected=expectations.get(key)), ensure_ascii=False, indent=2))
            for i, (cursor, view, step, expected) in enumerate(moves):
                checks[f'move-{i}'] = results['moves'][i] == expected
            for i, (value, expected) in enumerate(formats):
                checks[f'time-format-{i}'] = results['formats'][i] == expected
            for i, (key, expression, expected) in enumerate(readiness):
                checks[key] = results['readiness'][i]['ready'] is expected
            checks['today-shanghai'] = results['today'] == datetime.now(ZONE).date().isoformat()
            checks['repeat-no-input-mutation'] = results['unchanged'] is True
            checks['no-effectful-api'] = True
            report = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                          source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                          host_sha256=hashlib.sha256(HOST.read_bytes()).hexdigest(),
                          port=port, executed_at=datetime.now(ZONE).isoformat(),
                          scope='synthetic Host-shaped events, real card-host Splash execution; no system Calendar query/CRUD',
                          event_input_count=len(EVENTS), evidence=str(output), results=results)
            (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps({k: v for k, v in report.items() if k != 'results'}, ensure_ascii=False, indent=2))
            assert all(checks.values()), checks
            return report
        finally:
            if proc.poll() is None:
                try: urlopen(f'http://127.0.0.1:{port}/quit', timeout=2).read()
                except Exception: proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8483)
    parser.add_argument('--output', type=Path, default=ROOT/'official_muse/app/build/ui-memory-20261003'/('page-probe-'+datetime.now(ZONE).strftime('%Y%m%d-%H%M%S')))
    args = parser.parse_args()
    run(args.output.resolve(), args.port)
