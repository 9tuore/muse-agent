#!/usr/bin/env python3
"""Authorized synthetic owner UI only. Central runs serially; no Muse/Person claim."""
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
from urllib.error import HTTPError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote

TITLE = 'MUSE-N002-20261011-A 合成联调'
FIELDS = dict(title=TITLE, timezone='Asia/Shanghai', location='Muse synthetic acceptance', notes='')
QUERY = dict(from_='2026-10-12', to='2026-10-13', limit=200)


class Stop(Exception):
    def __init__(self, state, message):
        self.state = state
        super().__init__(message)


class WindowRemote(Remote):
    def __init__(self, port, window):
        super().__init__(port)
        self.window = window

    def request(self, path, **params):
        if path in ('/snap', '/click', '/k', '/t', '/m', '/g'):
            params['w'] = self.window
        return super().request(path, **params)

    def click(self, key):
        # Exactly one delivery, including Save/Delete. No frame-timeout retries.
        widget = self.wait_for(key)
        x, y, width, height = widget['r']
        if width < 2 or height < 2:
            raise Stop('PARTIAL', f'Clipped control: {key}')
        self.request('/click', x=int(x + width/2), y=int(y + height/2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--binary-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True, help='New direct child of ROOT/build')
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--read-only-system-chat', action='store_true',
                        help='Existing startup System-chat UI and bounded read only; no event writes')
    parser.add_argument('--owned-window-id', type=Path,
                        default=ROOT / 'build/runtime-closure-render-compare-r1/owned-main-window-id')
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    probe = args.owned_window_id.resolve(strict=True)
    assert not binary.is_relative_to(Path('/Applications'))
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == args.binary_sha256
    kernel = binary.parent / 'octos-kernel'
    receipt = json.loads((binary.parent / 'octos-kernel.json').read_text())
    assert receipt['revision'] == 'b0759a57719fd35b3a2da1c5d969bc67538ed516'
    assert hashlib.sha256(kernel.read_bytes()).hexdigest() == receipt['sha256']
    assert os.access(probe, os.X_OK)
    out = args.out.resolve()
    assert out.parent == ROOT / 'build' and not out.exists()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', args.port))  # Refuse a port owned by any existing process.
    out.mkdir(mode=0o700)
    home = out / 'home'
    env = os.environ.copy()
    for key in ('OCTOS_APP_CORE_BIN', 'OCTOSENSE_KERNEL_ANY_REVISION', 'OCTOSENSE_CONTAINED_APPS',
                'MAKEPAD_HIDE_WINDOWS', 'MAKEPAD_NO_FOCUS', 'MAKEPAD_NO_GAUSS', 'MAKEPAD_REMOTE'):
        env.pop(key, None)
    for key, leaf in {'OCTOSENSE_HOME':'shell', 'OCTOSENSE_APP_DATA':'apps',
                      'OCTOS_APP_CORE_DIR':'kernel/.octos', 'RINX_DATA_DIR':'rinx', 'ROBRIX_DATA_DIR':'rinx',
                      'XDG_CONFIG_HOME':'config', 'XDG_DATA_HOME':'data', 'XDG_CACHE_HOME':'cache'}.items():
        directory = home / leaf
        directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        env[key] = str(directory)
    env.update(OCTOSENSE_DEV_MODE='0', MAKEPAD_FOCUS='1')
    report = dict(state='PREPARED', operations=[], processes=[], checks={}, event_id=None,
                  exact_get='BLOCKED_NO_EXISTING_SYSTEM_GRANT', authoritative_absence='BLOCKED',
                  muse_agent_relay='NOT_TESTED', trusted_person='NOT_CLAIMED',
                  png_visual_review='REQUIRED',
                  initial_pixels_reviewed=False,
                  read_only_system_chat=args.read_only_system_chat,
                  initial_visual_review_boundary='Test harness pixel review only; not Person, consent or business approval',
                  binary_sha256=args.binary_sha256, kernel_receipt=receipt,
                  owned_window_probe_sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),
                  home=str(home), boundary='Owner UI plus fixed-grant System events only; synthetic data.')
    proc = None
    remote = None
    log_path = None
    sequence = 0

    def persist():
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def operation(name, **data):
        nonlocal sequence
        sequence += 1
        report['operations'].append(dict(id=f'{sequence:03}-{uuid.uuid4()}', name=name,
            time=datetime.now().astimezone().isoformat(), **data))
        persist()

    def check_owner():
        status = json.loads(remote.request('/s'))
        if status.get('pid') != proc.pid or proc.pid == 503:
            raise Stop('PARTIAL', 'Remote PID does not match owned child')
        if not any(w['i'] == remote.window for w in status.get('w', [])):
            raise Stop('PARTIAL', 'Owned window closed; do not relaunch it')

    def gate():
        check_owner()
        widgets = remote.widgets()
        texts = [w.get('t', '').strip().lower() for w in widgets]
        if any(t in ('allow', 'approve', 'grant', 'confirm action', 'allow once', 'allow always')
               or any(term in t for term in ('permission required', 'requires approval', 'trusted input', 'no_consent'))
               for t in texts):
            raise Stop('HUMAN_REQUIRED', 'Consent/permission/trusted approval surface observed; no click')
        return widgets

    def capture(label):
        gate()
        (out / f'{sequence:03}-{label}-snapshot.json').write_text(json.dumps(remote.widgets(), ensure_ascii=False))
        remote_png = out / f'{sequence:03}-{label}-remote.png'
        for attempt in range(12):
            gate()
            try:
                remote.shot(remote_png)
                break
            except HTTPError as error:
                if error.code != 404 or attempt == 11:
                    raise
                time.sleep(.5)  # Read-only frame capture; never repeat an input.
        if not remote_png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            raise Stop('PARTIAL', 'Remote capture did not return PNG bytes')
        ids = subprocess.check_output([str(probe), str(proc.pid)], text=True, timeout=10).splitlines()
        if not ids or any(not i.isdigit() for i in ids):
            raise Stop('PARTIAL', 'Owned OS window capture unavailable')
        for window_id in ids:
            target = out / f'{sequence:03}-{label}-os-{window_id}.png'
            capture_result = subprocess.run(['screencapture', '-x', '-l', window_id, str(target)],
                                             capture_output=True, timeout=15)
            operation('OS capture', window_id=window_id, exit=capture_result.returncode,
                      stderr=capture_result.stderr.decode(errors='replace'), file=target.name)
            if capture_result.returncode or not target.is_file() or not target.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
                raise Stop('HUMAN_REQUIRED', 'OS capture permission/result missing')

    def start():
        nonlocal proc, remote, log_path
        log_path = out / f'shell-{len(report["processes"])}.log'
        with log_path.open('wb') as stream:
            command = [str(binary), f'--remote={args.port}', '--test-action', 'launch-calendar']
            if args.read_only_system_chat:
                command += ['--test-action', 'system-chat']
            proc = subprocess.Popen(command,
                                    cwd=binary.parent, env=env, stdout=stream, stderr=subprocess.STDOUT)
        assert proc.pid != 503
        report['processes'].append(dict(pid=proc.pid, started=datetime.now().astimezone().isoformat(), log=log_path.name))
        operation('Launch official Calendar owner', pid=proc.pid)
        discovery = Remote(args.port)
        deadline = time.monotonic()+40
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise Stop('PARTIAL', f'Owned Shell exited: {proc.returncode}')
            try:
                status = json.loads(discovery.request('/s'))
            except OSError:
                time.sleep(.2)
                continue
            if status.get('pid') != proc.pid:
                raise Stop('PARTIAL', 'Remote port belongs to another process')
            for window in status.get('w', []):
                candidate = WindowRemote(args.port, window['i'])
                if any(w.get('i') == 'month_title' for w in candidate.widgets()):
                    remote = candidate
                    gate()
                    remote.wait_for('+ Event', 10)
                    operation('Owner visible', remote_window=remote.window)
                    return
            time.sleep(.2)
        raise Stop('HUMAN_REQUIRED', 'Calendar layout not ready; no input or consent bypass')

    def stop():
        nonlocal proc, remote
        if proc is None:
            return
        shutdown = dict(remote_quit=False, fallback=False, exit=None,
                        time=datetime.now().astimezone().isoformat())
        report['processes'][-1]['shutdown'] = shutdown
        if proc.poll() is None:
            try:
                check_owner()
                answer = remote.request('/quit')
                shutdown['remote_quit'] = True
                shutdown['remote_quit_reply'] = answer.decode(errors='replace')
                proc.wait(timeout=10)
            except Exception as error:
                shutdown['fallback'] = True
                shutdown['error'] = str(error)
                operation('Owned quit fallback', error=str(error))
                if proc.poll() is None:
                    proc.terminate()  # Only the exact Popen child; never process groups or PID503.
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        operation('Owned child still alive; central action required', pid=proc.pid)
        shutdown['exit'] = proc.poll()
        operation('Owned child exit', pid=proc.pid, shutdown=shutdown)
        report['processes'][-1]['exit'] = proc.poll()
        if proc.poll() is None:
            raise Stop('HUMAN_REQUIRED', 'Owned child did not exit; no restart')
        proc = None
        remote = None
        if shutdown['fallback'] or not shutdown['remote_quit'] or shutdown['exit'] != 0:
            raise Stop('PARTIAL_SHUTDOWN', 'Shutdown was not a clean remote_quit/exit0; no restart or success')
        if any('[E]' in line or 'script time budget exceeded' in line
               for line in log_path.read_text(errors='replace').splitlines()):
            raise Stop('PARTIAL_RUNTIME_ERRORS', 'Runtime errors observed after process exit; no restart or success')

    def listing(label):
        gate()
        offset = log_path.stat().st_size
        args_json = json.dumps({'from':QUERY['from_'], 'to':QUERY['to'], 'limit':QUERY['limit']})
        operation('Fixed-grant System calendar.events', checkpoint=label, arguments=json.loads(args_json))
        remote.request('/event', data='system-call:calendar.events '+args_json)
        deadline = time.monotonic()+12
        while time.monotonic() < deadline:
            data = log_path.read_bytes()[offset:].decode(errors='replace')
            if '[system-call] calendar.events: a test call runs only a declared read tool' in data:
                raise Stop('BLOCKED_TOOL_NOT_DECLARED', 'Calendar read tool not registered; no write or grant change')
            for line in data.splitlines():
                marker = '[system-call] calendar.events '
                if marker not in line:
                    continue
                payload = line.split(marker, 1)[1]
                try:
                    reply, _ = json.JSONDecoder().raw_decode(payload)
                except ValueError:
                    continue
                if reply.get('ok') is not True:
                    operation('Read refused', checkpoint=label, reply=reply)
                    raise Stop('HUMAN_REQUIRED', 'System events denied/error; preserve grant and stop')
                body = reply.get('data')
                if isinstance(body, str):
                    body = json.loads(body)
                if not isinstance(body, dict) or not isinstance(body.get('events'), list):
                    raise Stop('PARTIAL', 'Observed reply does not match events shape')
                rows = body['events']
                operation('Read result', checkpoint=label, reply=reply)
                if len(rows) >= QUERY['limit']:
                    raise Stop('PARTIAL', 'Bounded list reached cap; cannot select or reconcile')
                return rows
            time.sleep(.2)
        raise Stop('PARTIAL', 'System events reply not observed; no assumed schema or tool success')

    def click(label):
        gate()
        operation('Normal owner UI click', label=label)
        remote.click(label)

    def event(rows, start_time, event_id=None):
        if len(rows) != 1 or not isinstance(rows[0], dict):
            raise Stop('PARTIAL', 'Expected exactly one authorized event; no further mutation')
        value = rows[0]
        expected = dict(FIELDS, start=f'2026-10-12T{start_time}:00', end=f'2026-10-12T{start_time}:30')
        # start_time is an hour; exact full field values, not a model/UI title claim.
        if any(value.get(k) != v for k,v in expected.items()) or value.get('request_id', '') != '':
            raise Stop('PARTIAL', 'Full event fields differ; no further mutation')
        if not set(value).issubset(set(expected) | {'id', 'request_id'}):
            raise Stop('PARTIAL', 'Unexpected event fields; no further mutation')
        identity = value.get('id')
        if not isinstance(identity, str) or not identity or (event_id is not None and identity != event_id):
            raise Stop('PARTIAL', 'Same event ID not established; no update/delete')
        return identity

    try:
        start()
        capture('initial')
        checkpoint = out / 'initial-visual-reviewed.txt'
        operation('Await central initial pixel review', checkpoint=str(checkpoint),
                  timeout_seconds=120, required_content='VISIBLE_REVIEWED')
        print(f'Initial OS screenshots: {out}\nVisual checkpoint: {checkpoint}', flush=True)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            gate()
            if checkpoint.is_file() and checkpoint.read_text() == 'VISIBLE_REVIEWED':
                report['initial_pixels_reviewed'] = True
                operation('Central initial pixels reviewed', checkpoint=str(checkpoint),
                          boundary=report['initial_visual_review_boundary'])
                break
            time.sleep(.2)
        else:
            raise Stop('PARTIAL', 'Initial visual review checkpoint absent/mismatched; no write')
        operation('Open existing System chat without sending',
                  boundary='Startup action or F8 only; no provider, grant or consent changes')
        gate()
        if not args.read_only_system_chat:
            remote.request('/k', k='down', c='F8')
            remote.request('/k', k='up', c='F8')
        time.sleep(3)
        gate()
        if listing('before create'):
            raise Stop('PARTIAL', 'Fresh authorized day not empty; no mutation')
        if args.read_only_system_chat:
            raise Stop('READ_PREFLIGHT_READY_NO_WRITES', 'Bounded legal read only; no CRUD or Muse Relay claim')
        remote.request('/k', k='down', c='F8')
        remote.request('/k', k='up', c='F8')
        remote.wait_for('+ Event', 10)
        click('+ Event')
        for key,value in {'e_title':TITLE, 'e_date':'2026-10-12', 'e_start':'15:00',
                          'e_end_date':'2026-10-12', 'e_end':'15:30', 'e_zone':'Asia/Shanghai',
                          'e_place':FIELDS['location'], 'e_notes':''}.items():
            gate()
            operation('Normal owner field input', field=key, value=value)
            remote.set_text(key, value)
        capture('create-fields')
        click('Save')  # Exactly once. Any unknown delivery is reconciled read-only, never retried.
        remote.wait_for(TITLE, 10)
        identity = event(listing('created'), '15')
        report['event_id'] = identity
        report['checks']['created_all_fields_and_id'] = True
        capture('created')
        click('View event  ›')
        click('Edit')
        for key,value in {'e_start':'16:00', 'e_end':'16:30'}.items():
            gate()
            operation('Normal owner field input', field=key, value=value)
            remote.set_text(key, value)
        capture('edit-fields')
        click('Save')
        remote.wait_for(TITLE, 10)
        event(listing('updated'), '16', identity)
        report['checks']['updated_same_id_all_fields'] = True
        capture('updated')
        stop()
        start()  # Same isolated home, only after real owned process exit.
        event(listing('restarted'), '16', identity)
        report['checks']['restart_same_id_no_duplicate'] = True
        click('12 •')  # Actual calendar day control, not an injected focus_event call.
        remote.wait_for(TITLE, 10)
        capture('restarted')
        click('View event  ›')
        click('Delete event')
        event(listing('delete pending'), '16', identity)
        report['checks']['first_delete_did_not_remove'] = True
        capture('delete-pending')
        click('Confirm delete')
        remote.wait_for('No events on this day', 10)
        if listing('deleted'):
            raise Stop('PARTIAL', 'Authorized day still has records; do not repeat delete')
        report['checks']['bounded_events_absence_after_delete'] = True
        capture('deleted')
        stop()
        start()
        if listing('restart after delete'):
            raise Stop('PARTIAL', 'Records returned after deletion restart')
        report['checks']['bounded_absence_after_restart'] = True
        capture('deleted-restarted')
        report['state'] = 'OWNER_UI_COMPLETED_BOUNDED_READBACK_EXACT_GET_BLOCKED'
    except Exception as error:
        report['state'] = error.state if isinstance(error, Stop) else 'PARTIAL_UNKNOWN_NO_WRITE_RETRY'
        operation('Stopped acceptance', error_type=type(error).__name__, error=str(error))
        if proc is not None and proc.poll() is None and remote is not None:
            # Observe once before stopping; never retry Save/modify/delete or grant.
            try:
                listing('read-only reconciliation after stop')
            except Exception as read_error:
                operation('Read-only reconciliation unavailable', error=str(read_error))
            try:
                capture('stopped')
            except Exception as capture_error:
                operation('Stopped capture unavailable', error=str(capture_error))
    finally:
        try:
            stop()
        except Exception as stop_error:
            report['state'] = stop_error.state if isinstance(stop_error, Stop) else 'HUMAN_REQUIRED'
            operation('Cleanup incomplete', error=str(stop_error))
        report['runtime_errors'] = [dict(log=log.name, line=line)
            for log in out.glob('shell-*.log') for line in log.read_text(errors='replace').splitlines()
            if '[E]' in line or 'script time budget exceeded' in line]
        if report['runtime_errors'] and report['state'] == 'OWNER_UI_COMPLETED_BOUNDED_READBACK_EXACT_GET_BLOCKED':
            report['state'] = 'PARTIAL_RUNTIME_ERRORS'
        if report['state'] == 'OWNER_UI_COMPLETED_BOUNDED_READBACK_EXACT_GET_BLOCKED' and any(
                not process.get('shutdown', {}).get('remote_quit') or process['shutdown'].get('fallback')
                or process['shutdown'].get('exit') != 0 for process in report['processes']):
            report['state'] = 'PARTIAL_SHUTDOWN'
        persist()
    return 0 if report['state'] == 'OWNER_UI_COMPLETED_BOUNDED_READBACK_EXACT_GET_BLOCKED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
