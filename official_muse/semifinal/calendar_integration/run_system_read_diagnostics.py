#!/usr/bin/env python3
"""Isolated cold-read test entry only; central executes serially, not Muse/Person."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
from run_owner_ui_acceptance import ROOT, WindowRemote, Remote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--binary-sha256', required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True, help='New direct child of ROOT/build')
    args = parser.parse_args()
    binary, out = args.binary.resolve(strict=True), args.out.resolve()
    assert not binary.is_relative_to(Path('/Applications'))
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == args.binary_sha256
    receipt = json.loads((binary.parent / 'octos-kernel.json').read_text())
    assert receipt['revision'] == 'b0759a57719fd35b3a2da1c5d969bc67538ed516'
    assert hashlib.sha256((binary.parent / 'octos-kernel').read_bytes()).hexdigest() == receipt['sha256']
    assert out.parent == ROOT / 'build' and not out.exists()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', args.port))
    out.mkdir(mode=0o700)
    env = os.environ.copy()
    for key in ('OCTOS_APP_CORE_BIN', 'OCTOSENSE_KERNEL_ANY_REVISION', 'OCTOSENSE_CONTAINED_APPS',
                'MAKEPAD_HIDE_WINDOWS', 'MAKEPAD_NO_FOCUS', 'MAKEPAD_NO_GAUSS', 'MAKEPAD_REMOTE'):
        env.pop(key, None)
    for key, leaf in {'OCTOSENSE_HOME':'shell', 'OCTOSENSE_APP_DATA':'apps', 'OCTOS_APP_CORE_DIR':'kernel/.octos',
                      'RINX_DATA_DIR':'rinx', 'ROBRIX_DATA_DIR':'rinx', 'XDG_CONFIG_HOME':'config',
                      'XDG_DATA_HOME':'data', 'XDG_CACHE_HOME':'cache'}.items():
        directory = out / 'home' / leaf
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        env[key] = str(directory)
    env.update(OCTOSENSE_DEV_MODE='0', MAKEPAD_FOCUS='1')
    report = dict(state='PENDING', binary_sha256=args.binary_sha256, kernel_receipt=receipt, calls=[],
                  boundary='Patched cold-read diagnostic entry only; no Muse/Agent Relay, Person, consent, model or private store access',
                  shutdown=dict(remote_quit=False, fallback=False, exit=None))
    log_path = out / 'shell.log'
    proc, remote = None, None

    def save():
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def owned():
        status = json.loads(remote.request('/s'))
        assert status.get('pid') == proc.pid and proc.pid != 503, 'Wrong remote PID'
        assert any(w['i'] == remote.window for w in status.get('w', [])), 'Owned window closed'

    def call(tool, payload, expected):
        owned()
        row = dict(id=str(uuid.uuid4()), time=datetime.now().astimezone().isoformat(), tool=tool,
                   args=payload, expected=expected, log_offset=log_path.stat().st_size)
        report['calls'].append(row); save()
        remote.request('/event', data='system-call:'+tool+' '+json.dumps(payload))
        deadline = time.monotonic()+12
        while time.monotonic() < deadline:
            for line in log_path.read_bytes()[row['log_offset']:].decode(errors='replace').splitlines():
                refusal = f'[system-call] {tool}: a test call runs only a declared read tool'
                marker = f'[system-call] {tool} '
                if refusal in line:
                    row['observed_refusal'] = refusal
                    assert expected == 'readonly_refusal', 'Unexpected declaration refusal'
                    row['matched'] = True; save(); return
                if marker not in line:
                    continue
                try:
                    reply, _ = json.JSONDecoder().raw_decode(line.split(marker, 1)[1])
                except ValueError:
                    continue
                row['reply'] = reply; save()
                assert expected != 'readonly_refusal', 'Write tool reached reply path; stop'
                if expected == 'empty_events':
                    body = reply.get('data')
                    if isinstance(body, str):
                        body = json.loads(body)
                    assert reply.get('ok') is True and isinstance(body, dict) and body.get('events') == [], 'Expected actual ok/events[]'
                else:
                    assert reply.get('ok') is False and reply.get('error', {}).get('kind') == expected, 'Unexpected schema/grant result'
                row['matched'] = True; save(); return
            time.sleep(.2)
        raise RuntimeError('No new log result; do not infer success or repeat request')

    try:
        with log_path.open('wb') as stream:
            proc = subprocess.Popen([str(binary), f'--remote={args.port}', '--test-action', 'launch-calendar'],
                                    cwd=binary.parent, env=env, stdout=stream, stderr=subprocess.STDOUT)
        report.update(pid=proc.pid, started=datetime.now().astimezone().isoformat()); save()
        assert proc.pid != 503
        discovery = Remote(args.port)
        deadline = time.monotonic()+40
        while time.monotonic() < deadline and remote is None:
            assert proc.poll() is None, 'Owned Shell exited before ready'
            try:
                status = json.loads(discovery.request('/s'))
            except OSError:
                time.sleep(.2); continue
            assert status.get('pid') == proc.pid, 'Port belongs to another process'
            for window in status.get('w', []):
                candidate = WindowRemote(args.port, window['i'])
                widgets = candidate.widgets()
                assert not any(w.get('t', '').strip().lower() in ('allow', 'approve', 'grant') for w in widgets), 'HUMAN_REQUIRED: no consent clicks'
                if any(w.get('i') == 'month_title' for w in widgets):
                    remote = candidate; report['window'] = window['i']; save(); break
            time.sleep(.2)
        assert remote is not None, 'Calendar owner layout unavailable'
        for tool, payload, expected in [
            ('calendar.events', {'limit':1}, 'empty_events'),
            ('calendar.events', {'limit':0}, 'invalid_args'),
            ('calendar.get_event', {'id':'MUSE-N002-READ-ABSENT'}, 'not_granted'),
            *[(f'calendar.{name}', {}, 'readonly_refusal') for name in ('add_event','update_event','remove_event','notify')],
            ('calendar.events', {'limit':1}, 'empty_events')]:
            call(tool, payload, expected)
        report['state'] = 'DIAGNOSTIC_EXPECTATIONS_MATCHED_PENDING_SHUTDOWN'
    except Exception as error:
        report.update(state='PARTIAL_DIAGNOSTIC', error_type=type(error).__name__, error=str(error))
    finally:
        if proc is not None:
            try:
                assert proc.poll() is None and remote is not None, 'No live owned remote for quit'
                owned()
                report['shutdown']['reply'] = remote.request('/quit').decode(errors='replace')
                report['shutdown']['remote_quit'] = True
                proc.wait(timeout=10)
            except Exception as error:
                report['shutdown'].update(fallback=True, error=str(error))
                if proc.poll() is None:
                    proc.terminate()  # Exact owned child only, never process groups or stable503.
                    try: proc.wait(timeout=10)
                    except subprocess.TimeoutExpired: report['shutdown']['still_alive'] = True
            report['shutdown'].update(exit=proc.poll(), time=datetime.now().astimezone().isoformat())
        report['runtime_errors'] = [line for line in log_path.read_text(errors='replace').splitlines()
            if '[E]' in line or 'script time budget exceeded' in line] if log_path.exists() else []
        clean = report['shutdown']['remote_quit'] and not report['shutdown']['fallback'] and report['shutdown']['exit'] == 0
        if report['state'] == 'DIAGNOSTIC_EXPECTATIONS_MATCHED_PENDING_SHUTDOWN':
            report['state'] = 'PASS_COLD_READ_DIAGNOSTIC_ONLY' if clean and not report['runtime_errors'] else 'PARTIAL_SHUTDOWN_OR_RUNTIME_ERRORS'
        save()
    return 0 if report['state'] == 'PASS_COLD_READ_DIAGNOSTIC_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())
