#!/usr/bin/env python3
"""Visible reference native UI on an explicit synthetic, persisted profile.

Clicks only navigation/disclosure controls; never an approval or tool action.
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def action_digest(path):
    records = json.loads(path.read_text())['actions']
    assert records, 'Use a persisted fixture with real action history'
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', required=True, type=Path)
    p.add_argument('--host-cwd', required=True, type=Path)
    p.add_argument('--fixture', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--port', type=int, default=8659)
    a = p.parse_args()
    out = a.out.resolve()
    assert out.is_relative_to(ROOT / 'build') and not out.exists()
    fixture = a.fixture.resolve(strict=True)
    assert fixture.is_relative_to(ROOT / 'build')
    with socket.socket() as s:
        assert s.connect_ex(('127.0.0.1', a.port)) != 0
    out.mkdir(parents=True)
    for name in ('home', 'state', 'bundle'):
        shutil.copytree(fixture / name, out / name)
    source = ROOT / 'official_muse/app/source/main.splash'
    (out / 'bundle/main.splash').write_bytes(source.read_bytes())
    mpath = out / 'bundle/manifest.json'
    manifest = json.loads(mpath.read_text()); manifest['integrity'] = {}
    mpath.write_text(json.dumps(manifest) + '\n')
    report = {'kind': 'REAL_VISIBLE_REFERENCE_NATIVE_UI_SYNTHETIC_STORED_STATE',
              'status': 'ERROR', 'source_sha256': digest(source), 'host_sha256': digest(a.host),
              'cases': [], 'boundary': 'Old reference host; no actual mail/model/calendar execution or new Host admission.'}
    action_path = out / 'state/muse-goals/goals.json'
    before = action_digest(action_path)
    remote = Remote(a.port)

    def click(text):
        assert text in ('‹', '›', '☰', '结果', '行动链', '来信与结果', '查看依据', '返回页面', '浅色', '深色', '切换事项', '跟随当前对话')
        item = next(w for w in remote.widgets() if w.get('ty') == 'Button' and w.get('t') == text)
        x, y, w, h = item['r']; assert w >= 2 and h >= 20
        remote.request('/click', x=int(x+w/2), y=int(y+h/2))
        time.sleep(.2)

    def save():
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    try:
        for number, size in enumerate(('1100x740', '412x892', '990x539', '1200x420', '1100x740')):
            case = {'requested_size': size, 'restart': number > 0, 'checks': {}}
            report['cases'].append(case)
            log = out / f'runtime-{number}.log'
            env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_FOCUS='1',
                       OCTOSENSE_HOME=str(out/'home'), OCTOSENSE_APP_DATA=str(out/'state'),
                       OCTOS_APP_CORE_DIR=str(out/'home/octos-home/.octos'), MAKEPAD_APP_CONFIG='{}')
            env.pop('MAKEPAD_HIDE_WINDOWS', None)
            with log.open('w') as stream:
                proc = subprocess.Popen([str(a.host.resolve(strict=True)), '--bundle', str(out/'bundle'),
                    '--app-data', str(out/'state'), '--allow-unsigned', '--stamp', '--size', size],
                    cwd=a.host_cwd.resolve(strict=True), env=env, stdout=stream, stderr=stream)
                try:
                    deadline = time.monotonic()+20
                    while True:
                        try:
                            remote.widgets()
                            break
                        except OSError:
                            if proc.poll() is not None or time.monotonic() > deadline:
                                raise
                            time.sleep(.1)
                    remote.wait_for('goal_input', 40)
                    deadline = time.monotonic()+25
                    while not any(w.get('ty') == 'Label' and ' '.join(w.get('t', '').split()) == '当前项目 · 合成验收项目 / 个人' for w in remote.widgets()):
                        if time.monotonic() > deadline: raise RuntimeError('Nonempty stored state did not recover')
                        time.sleep(.2)
                    time.sleep(.3)
                    remote.shot(out / f'{number}-{size}-chat.png')
                    if int(size.split('x')[0]) <= 740 and any(w.get('t') == '‹' for w in remote.widgets()):
                        click('‹')
                    rect = remote.find('goal_input')['r']
                    case['input_rect'] = rect
                    case['checks']['composer_usable'] = rect[2] > 80 and rect[3] >= 28
                    if int(size.split('x')[0]) <= 740:
                        click('结果')
                    elif any(w.get('t') == '›' for w in remote.widgets()):
                        click('›')
                    click('行动链')
                    remote.wait_for('事项 · 当前计划', 5)
                    labels = [w.get('t') for w in remote.widgets()]
                    case['checks']['appearance_restored'] = ('深色' in labels) if number > 0 else ('浅色' in labels)
                    remote.shot(out / f'{number}-{size}-chain.png')
                    labels = [w.get('t') for w in remote.widgets()]
                    waiting = '等你确认' in labels
                    failed = '失败' in labels
                    if not failed:
                        area = remote.find('right_page_content' if int(size.split('x')[0]) <= 740 else 'right_content')['r']
                        x, y, w, h = area
                        remote.scroll(int(x+w/2), int(y+h/2), 160)
                        failed = any(w.get('t') == '失败' for w in remote.widgets())
                        remote.shot(out / f'{number}-{size}-scrolled.png')
                        remote.scroll(int(x+w/2), int(y+h/2), -400)
                    case['checks']['restored_plan_and_failure'] = waiting and failed
                    click('查看依据')
                    case['checks']['details_visible'] = any(w.get('t') == '版本 1 · 计划不等于执行成功' for w in remote.widgets())
                    remote.shot(out / f'{number}-{size}-expanded.png')
                    if number == 0: click('浅色')
                    else:
                        click('深色')
                        click('浅色')
                    case['checks']['appearance_toggle'] = any(w.get('t') == '深色' for w in remote.widgets())
                    remote.shot(out / f'{number}-{size}-light.png')
                    click('切换事项')
                    case['checks']['matter_picker_usable'] = any(w.get('t') == '跟随当前对话' and w['r'][2] > 40 for w in remote.widgets())
                    remote.shot(out / f'{number}-{size}-picker.png')
                    click('跟随当前对话')
                    click('来信与结果')
                    case['checks']['original_result_retained'] = any(w.get('t') == '查看任务详情' for w in remote.widgets())
                    remote.shot(out / f'{number}-{size}-results.png')
                    (out / f'snapshot-{number}.json').write_text(json.dumps(remote.widgets(), ensure_ascii=False, indent=2))
                finally:
                    try: remote.request('/quit')
                    except Exception: proc.terminate()
                    try: proc.wait(timeout=5)
                    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
            case['runtime_errors'] = [line for line in log.read_text().splitlines() if '[E]' in line]
            case['checks']['no_runtime_errors'] = not case['runtime_errors']
            save()
            print(json.dumps({'size': size, 'checks': case['checks']}), flush=True)
        report['actions_sha256_before'] = before
        report['actions_sha256_after'] = action_digest(action_path)
        report['actions_unchanged'] = before == action_digest(action_path)
        report['status'] = 'PASS_NATIVE_UI_SUBSET' if report['actions_unchanged'] and all(
            len(c['checks']) == 8 and all(c['checks'].values()) for c in report['cases']) else 'FAIL'
    except Exception as error:
        report['error'] = repr(error)
    save()
    print(json.dumps({'status': report['status'], 'error': report.get('error')}), flush=True)
    return 0 if report['status'] == 'PASS_NATIVE_UI_SUBSET' else 1


if __name__ == '__main__':
    raise SystemExit(main())
