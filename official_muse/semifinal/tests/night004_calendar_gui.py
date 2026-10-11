#!/usr/bin/env python3
"""Official Calendar UI acceptance in a marked, empty NIGHT-004 store.

The public candidate is copied. Only the copy's launch target, test port and
state reference change. Host/Kernel/resource bytes stay identical. This tests
the owner UI, not Muse's Agent admission or tool choice. Independent reads use
the unchanged official CalendarService through a separately supplied helper.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-app', type=Path, required=True)
    parser.add_argument('--reader', type=Path, required=True)
    parser.add_argument('--identity-checker', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, default=9697)
    args = parser.parse_args()
    source = args.candidate_app.resolve()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'build/night-004') and not out.exists()
    assert args.reader.resolve().is_file()
    assert args.identity_checker.resolve().is_file()
    with socket.socket() as sock:
        assert sock.connect_ex(('127.0.0.1', args.port)) != 0, 'Test port already occupied'
    out.mkdir(parents=True)
    state = out / 'state'
    owner_root = state / 'apps/.host'
    owner_root.mkdir(parents=True)
    (owner_root / 'FIXTURE_ONLY').write_text('NIGHT004 synthetic events only. Never production consent.\n')
    app = out / 'Calendar Fixture.app'
    shutil.copytree(source, app, symlinks=True)
    resources = app / 'Contents/Resources'
    runtime = resources / 'host-runtime'
    frozen = {name: digest(source / 'Contents/Resources/host-runtime' / name)
              for name in ('muse-host', 'octos-kernel', 'octos-kernel.json')}
    wrapper = app / 'Contents/MacOS/Launcher'
    text = wrapper.read_text()
    assert text.count('launch-muse-native-prototype') == 1
    assert text.count('PORT=${MUSE_INTEGRATED_REMOTE:-9696}') == 1
    wrapper.write_text(text.replace('launch-muse-native-prototype', 'launch-calendar')
                      .replace('PORT=${MUSE_INTEGRATED_REMOTE:-9696}', f'PORT={args.port}'))
    settings = json.loads((resources / 'launcher.json').read_text())
    settings.update(state_root=str(state), model_mode='gpt')
    (resources / 'launcher.json').write_text(json.dumps(settings, indent=2) + '\n')
    subprocess.run(['codesign', '--force', '--sign', '-', str(app)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert {name: digest(runtime / name) for name in frozen} == frozen
    remote = Remote(args.port)
    window_probe = out / 'owned-window-id'
    subprocess.run(['clang', '-framework', 'ApplicationServices',
                    str(ROOT / 'official_muse/semifinal/tests/owned_main_window_id.c'),
                    '-o', str(window_probe)], check=True, capture_output=True)
    reads, checks, launches = [], {}, []
    report = {'status': 'ERROR', 'boundary': 'Actual official Calendar owner UI and service; isolated synthetic events. Test target/port/state are changed only in a signed public app copy. No Muse Agent, real model, production consent or email claim.',
              'source_app': str(source), 'host_kernel_identity': frozen,
              'reader_sha256': digest(args.reader.resolve()), 'checks': checks,
              'independent_reads': reads, 'launches': launches}

    def read(method, payload):
        assert method in ('events', 'get_event')
        command = [str(args.reader.resolve()), str(owner_root)]
        result = subprocess.run(command, input=json.dumps({'owner': 'os.calendar', 'method': method, 'args': payload}),
                                text=True, capture_output=True, timeout=10)
        assert result.returncode == 0, result.stderr
        reply = json.loads(result.stdout)
        reads.append({'command': command, 'method': method, 'payload': payload, 'reply': reply})
        assert reply['result']['ok'], reply
        return reply['result']['data']

    def wait(test, seconds=12):
        deadline = time.monotonic() + seconds
        while not test():
            assert time.monotonic() < deadline, 'Independent state did not settle'
            time.sleep(.15)

    def shot(name):
        # The remote framebuffer omits composed in-process card surfaces on
        # this Intel Host. Capture only the actual window owned by this PID.
        window = subprocess.check_output([str(window_probe), str(pid)], text=True).strip()
        assert window, 'No owned native window to capture'
        target = out / name
        subprocess.run(['screencapture', '-x', '-l', window, str(target)], check=True)
        assert target.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')

    def reveal(key, area):
        for attempt in range(12):
            try:
                widget = remote.find(key)
                if widget['r'][2] >= 2 and widget['r'][3] >= 18:
                    return widget
            except AssertionError:
                pass
            x, y, width, height = remote.find(area)['r']
            remote.scroll(int(x + width / 2), int(y + height * .7), 80)
        raise AssertionError(f'Calendar widget not visible after scroll: {key}')

    def start():
        result = subprocess.run(['open', '-n', str(app)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        deadline = time.monotonic() + 45
        while True:
            try:
                remote.find('Your schedule, all in one place')
                break
            except (AssertionError, URLError, ConnectionError, TimeoutError):
                assert time.monotonic() < deadline, 'Calendar owner UI did not become ready'
                time.sleep(.2)
        ready = list(state.glob('launch-*.ready'))
        assert len(ready) == 1, 'Exactly one owned launcher is expected'
        identity = json.loads(ready[0].read_text())
        signature = subprocess.run([sys.executable, str(args.identity_checker.resolve()),
                                    '--pid', str(identity['owner_pid']),
                                    '--expected-executable', str(runtime / 'muse-host')],
                                   capture_output=True, text=True, timeout=15)
        identity['dynamic_signature'] = json.loads(signature.stdout)
        launches.append(identity)
        assert signature.returncode == 0, signature.stdout + signature.stderr
        return identity['owner_pid']

    def stop(pid):
        remote.request('/quit')
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                wait(lambda: not list(state.glob('launch-*.ready')), 5)
                return
            time.sleep(.1)
        raise RuntimeError('Owned Host did not exit gracefully')

    pid = None
    try:
        assert read('events', {})['events'] == []
        pid = start()
        shot('01-empty.png')
        remote.click('+ Event')
        title = 'NIGHT004 official Calendar GUI test'
        remote.set_text('e_title', title)
        remote.set_text('e_start', '19:00')
        remote.set_text('e_end', '19:30')
        remote.set_text('e_zone', 'Asia/Shanghai')
        remote.set_text('e_place', 'NIGHT004 synthetic room')
        expected = {'title': title, 'start': remote.find('e_date')['val'] + 'T19:00',
                    'end': remote.find('e_end_date')['val'] + 'T19:30',
                    'timezone': 'Asia/Shanghai', 'location': 'NIGHT004 synthetic room',
                    'notes': ''}
        remote.click('Save')
        wait(lambda: len(read('events', {})['events']) == 1)
        event = read('events', {})['events'][0]
        event_id = event['id']
        saved = read('get_event', {'id': event_id})
        checks['create_and_exact_independent_read'] = saved['found'] and saved['event']['id'] == event_id and all(saved['event'][key] == value for key, value in expected.items())
        reveal(title, 'calendar')
        shot('02-created.png')
        remote.click_scroll('View event  ›', 'calendar')
        remote.click('Edit')
        remote.set_text('e_start', '20:00')
        remote.set_text('e_end', '20:30')
        expected.update(start=remote.find('e_date')['val'] + 'T20:00',
                        end=remote.find('e_end_date')['val'] + 'T20:30')
        remote.click('Save')
        wait(lambda: read('get_event', {'id': event_id})['event']['start'].endswith('T20:00'))
        revised = read('get_event', {'id': event_id})['event']
        checks['update_preserves_same_id'] = revised['id'] == event_id and len(read('events', {})['events']) == 1 and all(revised[key] == value for key, value in expected.items()) and revised.get('request_id', '') == saved['event'].get('request_id', '')
        reveal(title, 'calendar')
        shot('03-updated.png')
        stop(pid)
        pid = None
        pid = start()
        restored = read('get_event', {'id': event_id})
        checks['restart_preserves_same_updated_event'] = restored['found'] and restored['event'] == revised
        reveal(title, 'calendar')
        shot('04-restored.png')
        remote.click_scroll('View event  ›', 'calendar')
        remote.click_scroll('Delete event', 'detail')
        checks['delete_requires_second_owner_ui_click'] = read('get_event', {'id': event_id})['found']
        shot('05-delete-review.png')
        remote.click_scroll('Confirm delete', 'detail')
        wait(lambda: read('get_event', {'id': event_id}) == {'found': False, 'event': None})
        checks['delete_and_independent_exact_absence'] = read('events', {})['events'] == []
        shot('06-deleted.png')
        stop(pid)
        pid = None
        pid = start()
        checks['restart_preserves_absence'] = read('get_event', {'id': event_id}) == {'found': False, 'event': None}
        shot('07-deleted-after-restart.png')
        assert all(checks.values()), checks
        report.update(status='REAL_OFFICIAL_CALENDAR_OWNER_GUI_PASS', event_id=event_id)
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        if pid is not None:
            try:
                shot('failure-native-window.png')
                (out / 'failure-widgets.json').write_text(json.dumps(remote.widgets(), indent=2) + '\n')
            except Exception as capture_error:
                report['failure_capture_error'] = str(capture_error)
        raise
    finally:
        if pid is not None:
            try:
                stop(pid)
            except Exception as error:
                report['shutdown_error'] = str(error)
                report['status'] = 'ERROR'
        (out / 'result.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        print(json.dumps({'status': report['status'], 'checks': checks, 'evidence': str(out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
