#!/usr/bin/env python3
"""Visible card-host, isolated synthetic dialogs; no inference or external writes."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from visual_capture import HOST, TRANSPORT, Remote, shot

SCENE = '''
fn management_visual_seed(){
 if fs.exists("management-seeded.json") { return }
 if !chat_ready || !gm_ready { start_timeout(0.1, || management_visual_seed()) return }
 if chat_sessions.len() < 16 { chat_new_session() }
 if chat_sessions.len() < 16 { start_timeout(0.08, || management_visual_seed()) return }
 for i in chat_sessions.len() { chat_sessions[i].title = "合成对话 " + (i + 1) }
 let title = "待删除长标题："
 for i in 6 { title = title + "项目讨论与资料整理" }
 chat_sessions[0].title = title
 chat_save()
 gm_save("汇报时先写结论","preference","user","汇报偏好",chat_selected_id,"","","local")
 fs.write("management-seeded.json",{target: chat_sessions[0].id selected: chat_selected_id}.to_json())
 redraw()
}
start_timeout(1.0, || management_visual_seed())
'''


def wait_until(check, description, seconds=15):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if check():
                return
        except (OSError, AssertionError, json.JSONDecodeError):
            pass
        time.sleep(.1)
    raise AssertionError(description)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--size', default='990x539')
    p.add_argument('--port', type=int, default=8490)
    p.add_argument('--before', action='store_true')
    p.add_argument('--source-bundle', type=Path, default=ROOT / 'official_muse/app/bundle')
    a = p.parse_args()
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', a.port)) == 0:
            raise RuntimeError('Existing window is protected; choose a free port.')
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    bundle = out / 'bundle'
    shutil.copytree(a.source_bundle, bundle)
    if a.before:
        for name in ('main.splash', 'manifest.json'):
            (bundle / name).write_bytes(subprocess.check_output(
                ['git', 'show', '5913641:official_muse/app/bundle/' + name], cwd=ROOT))
    source = (bundle / 'main.splash').read_text()
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.MULTILINE)
    if marker is None:
        raise RuntimeError('Startup marker missing; fixture injection is refused.')
    fixture_source = source[:marker.start()] + TRANSPORT + SCENE + '\n' + source[marker.start():]
    (bundle / 'main.splash').write_text(fixture_source.replace('host.request(', 'visual_host('))
    env = dict(os.environ, MAKEPAD_REMOTE=str(a.port))
    env.pop('MAKEPAD_HIDE_WINDOWS', None)
    data = out / 'state/muse-goals'
    r = Remote(a.port)
    checks = {}
    proc = None
    log = None

    def state():
        return json.loads((data / 'chat-sessions.json').read_text())

    def launch(log_name):
        nonlocal proc, log
        log = (out / log_name).open('w')
        proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(out / 'state'),
                                 '--allow-unsigned', '--stamp', '--size', a.size], env=env,
                                cwd=HOST.parents[2], stdout=log, stderr=log)
        wait_until(lambda: (data / 'management-seeded.json').exists() and r.find('＋ 新对话'), 'Dialog fixture did not start')
        time.sleep(.4)

    def close():
        nonlocal proc, log
        if proc is not None:
            try:
                r.request('/quit')
            except OSError:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            log.close()
            proc = None

    def target_delete():
        for _ in range(16):
            widgets = r.widgets()
            targets = [w for w in widgets if w.get('ty') == 'Button' and w.get('t', '').startswith('待删除长标题：')
                       and w['r'][2] > 2 and w['r'][3] >= 24]
            if targets:
                y = targets[0]['r'][1]
                return next(w for w in widgets if w.get('ty') == 'Button' and w.get('t') == '删除' and abs(w['r'][1]-y) < 2)
            x, y, w, h = r.find('history_list')['r']
            r.scroll(int(x+w/2), int(y+h/2), 140)
        raise AssertionError('Target dialog row remained unreachable')

    try:
        launch('runtime.log')
        metadata = json.loads((data / 'management-seeded.json').read_text())
        original = state()
        memory = (data / 'memory.json').read_bytes()
        r.click('＋ 新对话')
        wait_until(lambda: any('16 个' in w.get('t', '') for w in r.widgets()), 'Capacity explanation missing')
        shot(r, out / 'capacity.png')
        checks['capacity_keeps_data'] = state() == original
        buttons = [w for w in r.widgets() if w.get('ty') == 'Button' and w.get('t') == '删除']
        if a.before:
            checks['baseline_delete_absent_from_sidebar'] = not buttons
        else:
            checks['delete_visible_in_sidebar'] = bool(buttons)
            checks['capacity_chinese_actionable'] = any('16 个对话' in w.get('t', '') and '删除' in w.get('t', '') for w in r.widgets())
            button = target_delete()
            x, y, w, h = button['r']
            checks['delete_button_usable'] = w >= 40 and h >= 24
            r.request('/click', x=int(x+w/2), y=int(y+h/2))
            wait_until(lambda: r.find('确认删除'), 'Confirmation missing')
            checks['confirmation_names_target'] = any(w.get('t', '').startswith('“待删除长标题：') for w in r.widgets())
            checks['request_preserves_selection'] = state() == original
            for key in ('确认删除', '取消', 'goal_input'):
                checks[key + '_rect'] = r.find(key)['r']
                checks[key + '_usable'] = checks[key + '_rect'][2] >= 40 and checks[key + '_rect'][3] >= 24
            shot(r, out / 'delete-confirmation.png')
            r.click('取消')
            wait_until(lambda: not any(w.get('t') == '确认删除' for w in r.widgets()), 'Cancel did not close confirmation')
            checks['cancel_keeps_data'] = state() == original
            # A second explicit click prepares the same target, then one confirmation.
            button = target_delete()
            x, y, w, h = button['r']
            r.request('/click', x=int(x+w/2), y=int(y+h/2))
            r.click('确认删除')
            wait_until(lambda: len(state()['sessions']) == 15, 'Confirmed deletion did not persist')
            checks['only_named_target_deleted'] = {s['id'] for s in state()['sessions']} == {s['id'] for s in original['sessions']} - {metadata['target']}
            checks['noncurrent_selection_preserved'] = state()['selected_id'] == metadata['selected']
            checks['memory_preserved'] = (data / 'memory.json').read_bytes() == memory
            checks['backup_removed_target'] = metadata['target'] not in (data / 'chat-sessions.backup.json').read_text()
            shot(r, out / 'deleted.png')
            r.click('＋ 新对话')
            wait_until(lambda: len(state()['sessions']) == 16 and state()['selected_id'] != metadata['selected'], 'New after deletion failed')
            checks['new_after_delete'] = True
            shot(r, out / 'new-after-delete.png')
            restored = state()
            close()
            launch('restart.log')
            checks['real_process_restart_preserves_ids'] = state()['selected_id'] == restored['selected_id'] and {s['id'] for s in state()['sessions']} == {s['id'] for s in restored['sessions']}
            checks['restart_memory_preserved'] = (data / 'memory.json').read_bytes() == memory
            shot(r, out / 'restart.png')
        calls = json.loads((data / 'visual-calls.json').read_text())
        checks['no_inference_or_external_write'] = all(s in ('mail.accounts', 'calendar.status') for s in calls)
        checks['runtime_no_error'] = all('[E]' not in f.read_text() and 'script time budget exceeded' not in f.read_text() for f in out.glob('*.log'))
        checks['failed'] = [k for k, v in checks.items() if isinstance(v, bool) and not v]
        checks.update(kind='VISIBLE_CARD_HOST_SYNTHETIC', source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                      requested_size=a.size, observed_windows=json.loads(r.request('/s')).get('w', []), real_model=False, real_mail=False, real_calendar=False)
        (out / 'report.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(checks, ensure_ascii=False), flush=True)
        return bool(checks['failed'])
    except Exception as error:
        checks.update(status='ERROR', error=str(error), source_sha256=hashlib.sha256(source.encode()).hexdigest())
        (out / 'report.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
        try:
            shot(r, out / 'failure.png')
            (out / 'failure.snap.json').write_text(json.dumps([w for w in r.widgets() if w.get('ty') != 'Splash'], ensure_ascii=False, indent=2))
        except OSError:
            pass
        raise
    finally:
        close()


if __name__ == '__main__':
    raise SystemExit(main())
