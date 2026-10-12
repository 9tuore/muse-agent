#!/usr/bin/env python3
"""Prepare/execute fixed-candidate cold starts through the WorkBuddy .app entry.

Execution requires an existing marked NIGHT-004 or NIGHT-006 state; this tool never installs,
copies profiles, creates consent, rebuilds packages, or writes Calendar/Mail.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import socket
import subprocess
import sys
import threading
import time
from urllib.error import URLError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURES = (ROOT / 'build/night-004', ROOT / 'build/night006')
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def check_files(root, identities):
    require(isinstance(identities, dict) and identities, 'Missing frozen file identities')
    for name, expected in identities.items():
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts,
                'Frozen file name must be a relative path without ..')
        path = (root / relative).resolve()
        require(path.is_relative_to(root) and path.is_file(), f'Frozen file missing or escapes root: {name}')
        require(isinstance(expected, str) and len(expected) == 64 and sha(path) == expected,
                f'Frozen SHA differs: {name}')


def present(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def cpu_seconds(value):
    days, rest = (value.split('-', 1) if '-' in value else ('0', value))
    fields = [float(item) for item in rest.split(':')]
    seconds = 0.0
    for field in fields:
        seconds = seconds * 60 + field
    return int(days) * 86400 + seconds


class Sampler:
    """Observed ps maxima for the two owned PIDs and their current descendants."""
    def __init__(self, pids):
        self.pids = set(pids)
        self.phase = 'startup'
        self.stop_event = threading.Event()
        self.rows = []
        self.errors = []
        self.thread = threading.Thread(target=self.sample, daemon=True)

    def sample(self):
        while not self.stop_event.is_set():
            try:
                answer = subprocess.check_output(
                    ['/bin/ps', '-axo', 'pid=,ppid=,%cpu=,rss=,time='], text=True)
                processes = {}
                for line in answer.splitlines():
                    fields = line.split()
                    if len(fields) == 5:
                        pid, parent = map(int, fields[:2])
                        processes[pid] = (parent, float(fields[2]), int(fields[3]), cpu_seconds(fields[4]))
                owned = self.pids & processes.keys()
                while True:
                    expanded = owned | {pid for pid, row in processes.items() if row[0] in owned}
                    if expanded == owned:
                        break
                    owned = expanded
                self.rows.append({'at_monotonic': time.monotonic(), 'phase': self.phase,
                                  'processes': [{'pid': pid, 'cpu_percent_ps': processes[pid][1],
                                                 'rss_kib': processes[pid][2],
                                                 'cpu_seconds': processes[pid][3]} for pid in sorted(owned)]})
            except (subprocess.SubprocessError, ValueError) as error:
                self.errors.append(type(error).__name__)
            self.stop_event.wait(.25)

    def finish(self):
        self.stop_event.set()
        self.thread.join(timeout=3)
        phases = {}
        for phase in ('startup', 'interactivity', 'shutdown'):
            rows = [row for row in self.rows if row['phase'] == phase]
            phases[phase] = {
                'samples': len(rows),
                'observed_peak_cpu_percent_ps_sum': max(
                    (sum(item['cpu_percent_ps'] for item in row['processes']) for row in rows), default=None),
                'observed_peak_rss_kib_sum': max(
                    (sum(item['rss_kib'] for item in row['processes']) for row in rows), default=None)}
        return {'coverage': 'From owned ready-file discovery until graceful shutdown. ps CPU percentage is its reported average, not an instantaneous CPU measurement. Peaks are sampled maxima, not guaranteed absolute maxima.',
                'phases': phases, 'rows': self.rows, 'errors': self.errors}


def numeric_counts(value):
    require(isinstance(value, dict) and value, 'Counter helper must return a nonempty JSON object')
    for key, item in value.items():
        require(isinstance(key, str), 'Counter keys must be strings')
        if isinstance(item, dict):
            numeric_counts(item)
        else:
            require(type(item) is int and item >= 0, 'Counter JSON must contain only nonnegative integer counts')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('candidate-app', 'state-root', 'out', 'expected-source-identities'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--repetitions', type=int, default=20)
    parser.add_argument('--startup-timeout', type=float, default=60)
    parser.add_argument('--calendar-reader', type=Path,
                        help='Existing read_calendar.py; real os.calendar/events read protocol')
    parser.add_argument('--side-effect-reader', type=Path,
                        help='Reviewed read-only executable: argv[1]=STATE_ROOT; stdout=numeric JSON counts. Optional until supplied.')
    parser.add_argument('--host-only', action='store_true', help='Explicitly measure Host only; cannot report Muse 20 PASS')
    parser.add_argument('--prepare-only', action='store_true', help='Validate frozen inputs and boundaries; do not launch/capture/probe a process')
    args = parser.parse_args()
    require(1 <= args.repetitions <= 20, 'Repetitions must be 1..20')
    require(1024 <= args.port <= 65535 and 0 < args.startup_timeout <= 120, 'Invalid port or timeout')
    require(all(path.is_absolute() for path in (args.candidate_app, args.state_root, args.out,
                                               args.expected_source_identities)), 'All input/output paths must be absolute')
    app, state, out = (path.resolve() for path in (args.candidate_app, args.state_root, args.out))
    require(app.is_dir() and app.suffix == '.app', 'Candidate must be an existing .app')
    require(any(state.is_relative_to(base) and state != base for base in FIXTURES) and state.is_dir(),
            'State must already exist below central build/night-004 or build/night006')
    require((state / 'FIXTURE_ONLY').is_file() and (state / 'apps/.host/FIXTURE_ONLY').is_file(), 'State and owner root must both be explicitly FIXTURE_ONLY')
    require(any(out.is_relative_to(base) and out != base for base in FIXTURES) and not out.exists(),
            'Output must be a new central build/night-004 or build/night006 directory')
    require(not state.is_relative_to(out) and not out.is_relative_to(state), 'Evidence and persistent state must be separate directories')
    expected = json.loads(args.expected_source_identities.read_text())
    critical = ('Contents/Info.plist', 'Contents/MacOS/Launcher', 'Contents/MacOS/muse-launcher',
                'Contents/Resources/launcher.json', 'Contents/Resources/host-runtime/muse-host',
                'Contents/Resources/host-runtime/octos-kernel', 'Contents/Resources/host-runtime/octos-kernel.json',
                'Contents/Resources/mirror/catalog.json')
    require(all(name in expected.get('candidate_files', {}) for name in critical), 'Expected identities must freeze all launcher/runtime/catalog inputs')
    check_files(app, expected['candidate_files'])
    with (app / 'Contents/Info.plist').open('rb') as handle:
        require(plistlib.load(handle).get('CFBundleExecutable') == 'Launcher', 'Candidate does not use the confirmed outer Launcher entry')
    installed = state / 'apps/.bundles/muse-goals/bundle'
    if not args.host_only:
        require(all(name in expected.get('installed_bundle_files', {}) for name in ('main.splash', 'manifest.json')), 'Freeze the installed formal Muse manifest/main; prototype is insufficient')
        check_files(installed, expected['installed_bundle_files'])
        manifest = json.loads((installed / 'manifest.json').read_text())
        require(manifest.get('id') == 'muse-goals' and manifest.get('name') == expected.get('muse_title'), 'Installed formal Muse ID/title differs')
    identity_checker = HERE / 'check_host_identity.py'
    require(identity_checker.is_file() and (HERE / 'owned-main-window-id').is_file(), 'Prepared identity/window helpers missing')
    helpers = {'identity_checker': sha(identity_checker), 'window_probe': sha(HERE / 'owned-main-window-id')}
    for name in ('calendar_reader', 'side_effect_reader'):
        value = getattr(args, name)
        if value:
            require(value.is_absolute() and value.resolve().is_file(), f'{name} must be an absolute existing helper')
            helpers[name] = sha(value.resolve())
            require(helpers[name] == expected.get('helper_files', {}).get(name), f'Freeze reviewed {name} SHA before execution')
    require(not list(state.glob('launch-*.ready')), 'Owned fixture launcher still active or stale ready file; central must resolve it before testing')
    report = {'status': 'PREPARED_NOT_EXECUTED', 'muse_20_pass': False, 'candidate_app': str(app),
              'state_root': str(state), 'port': args.port, 'requested_repetitions': args.repetitions,
              'expected_source_identities_sha256': sha(args.expected_source_identities),
              'helpers': helpers, 'launches': [],
              'boundary': 'Existing marked state is reused without copying/rebuilding profiles or reinstalling. Ordinary menu/navigation only, no permissions/approval/calendar/mail writes. Native screenshot review is required; remote /g is never used for black-screen classification.',
              'side_effect_coverage': {'calendar_reader': bool(args.calendar_reader), 'generic_reader': bool(args.side_effect_reader)}}
    out.mkdir(parents=True)
    save(out / 'expected-source-identities.json', expected)
    if args.prepare_only:
        save(out / 'result.json', report)
        print(json.dumps({'status': report['status'], 'evidence': str(out)}))
        return 0
    remote = Remote(args.port)
    host_exe = app / 'Contents/Resources/host-runtime/muse-host'

    def counters():
        counts = {}
        if args.calendar_reader:
            reply = subprocess.run([str(args.calendar_reader.resolve()), str(state / 'apps/.host')],
                                   input=json.dumps({'owner': 'os.calendar', 'method': 'events', 'args': {'limit': 200}}),
                                   capture_output=True, text=True, timeout=15)
            require(reply.returncode == 0, 'Independent Calendar reader failed')
            data = json.loads(reply.stdout)['result']
            require(data.get('ok') is True and isinstance(data.get('data', {}).get('events'), list), 'Independent Calendar events response invalid')
            require(len(data['data']['events']) < 200,
                    'Calendar events page is saturated; use a complete owner-store counter before checking unchanged totals')
            counts['calendar_event_count'] = len(data['data']['events'])
        if args.side_effect_reader:
            reply = subprocess.run([str(args.side_effect_reader.resolve()), str(state)], capture_output=True, text=True, timeout=15)
            require(reply.returncode == 0, 'Independent counter reader failed')
            counts['supplied_counts'] = numeric_counts(json.loads(reply.stdout))
        return counts

    def wait(test, seconds, message, required=True):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                value = test()
                if value:
                    return value
            except (URLError, ConnectionError, TimeoutError, AssertionError, FileNotFoundError, json.JSONDecodeError):
                pass
            time.sleep(.15)
        if required:
            raise RuntimeError(message)
        return None

    def ready():
        files = list(state.glob('launch-*.ready'))
        require(len(files) <= 1, 'Multiple owned fixture launchers appeared')
        return json.loads(files[0].read_text()) if files else None

    def capture(pid, target):
        window = subprocess.check_output([str(HERE / 'owned-main-window-id'), str(pid)], text=True).strip()
        require(window.isdigit(), 'No actual native window owned by the checked Host')
        subprocess.run(['/usr/sbin/screencapture', '-x', '-l', window, str(target)], check=True, capture_output=True)
        require(target.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'), 'Native capture did not produce PNG')
        return {'path': str(target), 'sha256': sha(target), 'window_id': int(window), 'owner_pid': pid,
                'visual_review': 'PENDING; PNG existence is not proof of rendered Muse'}

    def formal_shell():
        widgets = remote.widgets()
        ids = {item.get('i') for item in widgets}
        texts = {item.get('t') for item in widgets}
        if not {'sidebar', 'central_main'}.issubset(ids) or expected['muse_title'] not in texts:
            return None
        # rc.6 mounts the shell before staged storage and navigation restore.
        # This readiness applies on every restored page, not only Chat.
        buttons = {item.get('t') for item in widgets
                   if item.get('ty') == 'Button' and item.get('r', [0, 0, 0, 0])[3] >= 24}
        return widgets if {'对话', '切换事项'}.issubset(buttons) and {'新对话', '＋ 新对话'} & buttons else None

    def full_muse():
        # Chat deliberately hides page_header/page_title in the real source.
        widgets = formal_shell()
        if not widgets or 'goal_input' not in {item.get('i') for item in widgets}:
            return None
        return widgets

    def open_formal(pid, row):
        # The confirmed Launcher already asks to open Muse. Host /s and its
        # ready file precede the bounded multi-frame Splash preparation.
        # Wait without input before falling back; opening AppsMenu during
        # preparation would interrupt the application being measured.
        waiting = time.monotonic()
        if wait(formal_shell, args.startup_timeout, 'Launcher Muse autoload did not settle', required=False):
            row['autoload_wait_seconds'] = time.monotonic() - waiting
            row['open_route'] = 'Launcher autoload; exact installed Muse source and restored navigation checked'
            return
        row['autoload_wait_seconds'] = time.monotonic() - waiting
        remote.request('/k', k='press', c='Space', cmd=1, alt=1)
        time.sleep(.2)
        remote.request('/k', k='press', c='KeyU', ctrl=1)
        # apphub is the real native module ID, confirmed in the SDK registry.
        # Its ordinary Library/Open flow refreshes the verified catalog first.
        for char in 'apphub':
            remote.request('/k', k='press', c='Key' + char.upper())
        time.sleep(.2)
        row['menu_native_capture'] = capture(pid, Path(row['directory']) / 'menu-before-open.png')
        remote.request('/k', k='press', c='ReturnKey')
        time.sleep(.2)
        row['menu_after_return_capture'] = capture(pid, Path(row['directory']) / 'menu-after-return.png')
        save(Path(row['directory']) / 'menu-after-return-widgets.json',
             [{key: item[key] for key in ('i', 'ty', 't', 'r') if key in item}
              for item in remote.widgets() if item.get('ty') != 'Splash'])

        def inside(item, area):
            x, y, width, height = item.get('r', (0, 0, 0, 0))
            ax, ay, aw, ah = area['r']
            return (width >= 2 and height >= 2 and x >= ax - 1 and y >= ay - 1
                    and x + width <= ax + aw + 1 and y + height <= ay + ah + 1)

        def hub_widgets():
            widgets = remote.widgets()
            hubs = [item for item in widgets if item.get('ty') == 'AppHubView']
            require(len(hubs) <= 1, 'Multiple App Hub views; refuse ambiguous controls')
            return [item for item in widgets if inside(item, hubs[0])] if hubs else []

        def library_control():
            return next((item for item in hub_widgets()
                         if item.get('i') == 'library' and item.get('ty') == 'Button'
                         and item.get('t') == 'Library' and item['r'][3] >= 24), None)

        def click_widget(item):
            x, y, width, height = item['r']
            require(width >= 2 and height >= 24, 'App Hub control is clipped')
            # No wait=1: a click may produce no frame while the catalog worker
            # is busy. Inspect subsequent state; never repeat an Open blindly.
            remote.request('/click', x=int(x + width / 2), y=int(y + height / 2))

        library = wait(library_control, args.startup_timeout, 'Actual App Hub did not render after AppsMenu Return')
        click_widget(library)
        wait(lambda: any(item.get('t') == 'Your installed apps' for item in hub_widgets()),
             15, 'App Hub did not navigate to the actual Library page')
        deadline = time.monotonic() + args.startup_timeout
        scrolls = 0
        target = None
        while time.monotonic() < deadline:
            widgets = hub_widgets()
            pane = next((item for item in widgets if item.get('i') == 'list'
                         and item.get('ty') == 'PortalList'), None)
            require(pane is not None, 'App Hub Library list missing')
            names = [item for item in widgets if item.get('i') == 'name'
                     and item.get('ty') == 'Label' and item.get('t') == expected['muse_title']
                     and inside(item, pane)]
            require(len(names) <= 1, 'Multiple Muse rows; refuse ambiguous Open')
            if names:
                name = names[0]
                ny, nh = name['r'][1], name['r'][3]
                actions = [item for item in widgets if item.get('i') == 'action'
                           and item.get('ty') == 'Button' and inside(item, pane)
                           and item['r'][3] >= 24
                           and max(item['r'][1], ny) < min(item['r'][1] + item['r'][3], ny + nh)]
                if actions:
                    require(len(actions) == 1 and actions[0].get('t') == 'Open',
                            'Muse Library row is not an installed Open; no Get/Update/Install attempted')
                    target = actions[0]
                    row['apphub_muse_row'] = {'name': name, 'open': target}
                    break
            # PortalList may still be loading asynchronously. Scroll only once
            # rows exist, only its real rectangle, with a bounded attempt count.
            if scrolls < 12 and any(item.get('i') == 'name' for item in widgets):
                x, y, width, height = pane['r']
                remote.scroll(int(x + width / 2), int(y + height / 2), 80)
                scrolls += 1
            time.sleep(.2)
        require(target is not None, 'Installed Muse Open was not reachable in actual App Hub Library')
        row['apphub_library_capture'] = capture(pid, Path(row['directory']) / 'apphub-library-before-open.png')
        row['apphub_library_scrolls'] = scrolls
        click_widget(target)
        time.sleep(.2)
        row['apphub_after_open_capture'] = capture(pid, Path(row['directory']) / 'apphub-after-open.png')
        row['open_route'] = 'Actual AppsMenu apphub → App Hub Library → exact Muse row installed Open; worker may_open and Shell launch_app admission preserved'
        wait(formal_shell, args.startup_timeout, 'Full Muse restore did not become interactive; initial mount cannot pass')

    def navigate(name):
        # The live Muse ScrollYView is shortcuts. App Hub also exposes nav,
        # which is a different pane and must never be scrolled for Muse.
        direction = -80 if name == '对话' else 80
        for _ in range(10):
            try:
                control = remote.find(name)
                rect = control['r']
                if rect[2] >= 2 and rect[3] >= 24:
                    remote.click(name)
                    return
            except AssertionError:
                pass
            x, y, width, height = remote.find('shortcuts')['r']
            require(width >= 2 and height >= 2, 'Muse shortcuts scroll area is clipped')
            remote.scroll(int(x + width / 2), int(y + height / 2), direction)
        raise RuntimeError(f'Muse navigation control remains clipped: {name}')

    def page(name):
        def current():
            if name == '对话':
                return full_muse()
            widgets = formal_shell()
            if not widgets:
                return None
            ids = {item.get('i') for item in widgets}
            texts = {item.get('t') for item in widgets}
            title = next((item for item in widgets if item.get('i') == 'page_title'), None)
            return widgets if title and title.get('t') == name and 'memory_search' in ids and '全局记忆' in texts else None
        return wait(current, 15, f'Muse page did not become {name}')

    def stop_owned(row):
        pid, guardian = row['owner_pid'], row['guardian_pid']
        if present(pid):
            require(json.loads(remote.request('/s')).get('pid') == pid, 'Remote PID changed; refuse to quit another process')
            remote.request('/quit')
        wait(lambda: not present(pid) and not present(guardian) and not list(state.glob('launch-*.ready')),
             15, 'Owned Host/guardian did not exit gracefully; no force kill attempted')

    try:
        baseline = counters()
        report['baseline_counts'] = baseline
        if 'expected_side_effect_counts' in expected:
            require(baseline == expected['expected_side_effect_counts'], 'Baseline counters differ from central expected counts')
        for number in range(1, args.repetitions + 1):
            check_files(app, expected['candidate_files'])
            if not args.host_only:
                check_files(installed, expected['installed_bundle_files'])
            with socket.socket() as sock:
                require(sock.connect_ex(('127.0.0.1', args.port)) != 0, 'Test port occupied; refuse to reuse another process')
            trial = out / f'{number:02d}'
            trial.mkdir()
            row = {'number': number, 'directory': str(trial), 'status': 'STARTING'}
            report['launches'].append(row)
            owner = None
            sampler = None
            started = time.monotonic()
            try:
                launched = subprocess.run(['/usr/bin/open', '-n', '--env', f'MUSE_INTEGRATED_STATE={state}',
                                           '--env', f'MUSE_INTEGRATED_REMOTE={args.port}', str(app)],
                                          capture_output=True, text=True, timeout=15)
                require(launched.returncode == 0, 'WorkBuddy open -n .app failed')
                row['open_return_seconds'] = time.monotonic() - started
                owner = wait(ready, args.startup_timeout, 'Owned launcher ready file did not appear')
                require(type(owner.get('owner_pid')) is int and type(owner.get('guardian_pid')) is int,
                        'Ready file has invalid owned PIDs')
                row.update(owner)
                require(subprocess.check_output(['/bin/ps', '-p', str(owner['guardian_pid']), '-o', 'ppid='], text=True).strip() == str(owner['owner_pid']),
                        'Guardian is not a child of the owned Host')
                sampler = Sampler((owner['owner_pid'], owner['guardian_pid']))
                sampler.thread.start()
                wait(lambda: json.loads(remote.request('/s')).get('pid') == owner['owner_pid'],
                     args.startup_timeout, 'Remote did not identify the owned Host')
                checked = subprocess.run([sys.executable, str(identity_checker), '--pid', str(owner['owner_pid']),
                                          '--expected-executable', str(host_exe)], capture_output=True, text=True, timeout=15)
                row['dynamic_signature'] = json.loads(checked.stdout)
                require(checked.returncode == 0, 'Owned Host dynamic identity failed')
                row['host_ready_seconds'] = time.monotonic() - started
                if not args.host_only:
                    open_formal(owner['owner_pid'], row)
                    navigate('对话')
                    page('对话')
                row['muse_ready_seconds'] = None if args.host_only else time.monotonic() - started
                row['native_initial'] = capture(owner['owner_pid'], trial / 'native-initial.png')
                sampler.phase = 'interactivity'
                interactive = time.monotonic()
                if args.host_only:
                    row['interactivity_boundary'] = 'Host remote /s only; no Muse claim'
                    json.loads(remote.request('/s'))
                else:
                    navigate('对话')
                    page('对话')
                    navigate('记忆')
                    page('记忆')
                    row['native_memory'] = capture(owner['owner_pid'], trial / 'native-memory.png')
                    navigate('对话')
                    page('对话')
                    require(full_muse(), 'Full Muse widgets disappeared after navigation')
                    text = f'Muse cold start {number} input readback'
                    remote.set_text('goal_input', text)
                    require(remote.find('goal_input').get('val') == text, 'Actual input readback differs')
                    remote.set_text('goal_input', '')
                    require(remote.find('goal_input').get('val') == '', 'Actual input did not clear')
                    row['input_readback_and_clear'] = True
                    row['muse_widget_proof'] = [{'i': item.get('i'), 'ty': item.get('ty'), 't': item.get('t'), 'r': item.get('r')}
                                               for item in remote.widgets() if item.get('i') in ('goal_input', 'sidebar', 'central_main', 'chat_list', 'right_column', 'shortcuts')]
                row['interactivity_seconds'] = time.monotonic() - interactive
                row['native_after_navigation'] = capture(owner['owner_pid'], trial / 'native-after-navigation.png')
                sampler.phase = 'shutdown'
                quitting = time.monotonic()
                stop_owned(row)
                row['graceful_shutdown_seconds'] = time.monotonic() - quitting
                owner = None
                row['counts_after_shutdown'] = counters()
                require(row['counts_after_shutdown'] == baseline, 'Independent side-effect counts changed during cold start')
                row['status'] = 'HOST_ONLY' if args.host_only else 'MUSE_STARTUP_INTERACTION_CHECKED_NATIVE_REVIEW_PENDING'
            except Exception as error:
                row['status'] = 'FAILED'
                row['error'] = f'{type(error).__name__}: {error}'
                if owner is not None:
                    try:
                        row['native_failure'] = capture(owner['owner_pid'], trial / 'native-failure.png')
                    except Exception as capture_error:
                        row['failure_capture_error'] = type(capture_error).__name__
                else:
                    row['cleanup_boundary'] = 'No owned ready PID established; no unowned quit or force kill attempted'
                raise
            finally:
                if owner is not None:
                    try:
                        stop_owned(row)
                    except Exception as error:
                        row['cleanup_error'] = f'{type(error).__name__}: {error}'
                if sampler:
                    row['resource_samples'] = sampler.finish()
                    phases = row['resource_samples']['phases']
                    row['resource_metrics_complete'] = (phases['startup']['samples'] > 0
                                                        and (args.host_only or phases['interactivity']['samples'] > 0)
                                                        and not row['resource_samples']['errors'])
                row['total_seconds'] = time.monotonic() - started
                save(trial / 'result.json', row)
                save(out / 'result.json', report)
            require(row.get('resource_metrics_complete'), 'Startup/interactivity resource sample coverage incomplete')
        check_files(app, expected['candidate_files'])
        if not args.host_only:
            check_files(installed, expected['installed_bundle_files'])
        report['status'] = ('HOST_STARTUP_ONLY_NOT_MUSE_20_PASS' if args.host_only else
                            'MUSE_20_STARTUP_INTERACTION_CHECKS_PASS_NATIVE_REVIEW_PENDING' if args.repetitions == 20 else
                            'MUSE_SMOKE_CHECKS_PASS_NOT_20_NATIVE_REVIEW_PENDING')
        report['remaining_gate'] = 'Central must review actual native screenshots and confirm both Calendar/Mail counter coverage before Muse 20 PASS. Business T18 is a separate gate.'
        return 0
    except Exception as error:
        report['status'] = 'FAILED_NOT_MUSE_20_PASS'
        report['error'] = f'{type(error).__name__}: {error}'
        return 1
    finally:
        save(out / 'result.json', report)
        print(json.dumps({'status': report['status'], 'muse_20_pass': False, 'evidence': str(out)}, ensure_ascii=False))


if __name__ == '__main__':
    raise SystemExit(main())
