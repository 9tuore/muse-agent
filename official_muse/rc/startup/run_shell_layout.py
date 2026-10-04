#!/usr/bin/env python3
"""Inspect final native Shell geometry using existing WM mouse drag APIs.

Synthetic local-model-only profile, edit/clear input only; no model submit,
Calendar writes, Mail send or production data. Preserve every failed size.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from live_shell_layout import drag, settle
from visual_capture import navigate, shot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--port', type=int, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    assert a.port in (8486, 8488), 'Only controller-owned ports'
    meta = json.loads((a.candidate / 'candidate.json').read_text())
    assert meta['profile_kind'] == 'LOCAL_MODEL_ONLY_SYNTHETIC'
    jail = a.candidate / 'private/apps/muse-goals'
    assert sha(jail / 'bundle/main.splash') == meta['source_sha256']
    assert sha(Path(meta['host_app_path']) / 'Contents/MacOS/octosense') == meta['host_sha256']
    llm = json.loads((a.candidate / 'private/home/octos-home/.octos/profiles/_main.json').read_text())['config']['llm']
    assert llm['primary']['route']['base_url'] == 'http://127.0.0.1:65534/v1' and llm['fallbacks'] == []
    a.out.mkdir(parents=True, exist_ok=False)
    files = [x for x in jail.iterdir() if x.is_file() and x.name != 'ui-layout.json']
    before = {x.name: sha(x) for x in files}
    r = Remote(a.port)
    def goto(page):
        if any(w.get('t') == '☰' for w in r.widgets()):
            r.click('☰')
        navigate(r, page)
    report = {'kind': 'VISIBLE_NATIVE_SHELL_SYNTHETIC_LAYOUT', 'version': meta['version'],
              'source_sha256': meta['source_sha256'], 'host_sha256': meta['host_sha256'],
              'computer_restart': False, 'model_or_external_action': False, 'sizes': []}
    goto('对话')
    native = json.loads(r.request('/s'))
    report['native_before'] = native
    if native['w'][0]['sz'][1] < 900:
        r.request('/w', k='maximize')
    x, y, width, height = settle(r)
    drag(r, x + width / 2, y + 50, 20 - x, 70 - y, 0)
    native = json.loads(r.request('/s'))
    for width, height in ((412, 892), (990, 539), (990, 400), (1200, 700)):
        row = {'requested': [width, height], 'pass': False}
        report['sizes'].append(row)
        folder = a.out / f'{width}x{height}'
        folder.mkdir()
        try:
            goto('对话')
            x, y, old_width, old_height = settle(r)
            rect = drag(r, x + old_width - 24, y + old_height * .65,
                        width - old_width, height - old_height, 1)
            row['client_rect'] = rect
            expected_height = min(height, native['w'][0]['sz'][1] - rect[1] - 12)
            assert abs(rect[2] - width) <= 2 and abs(rect[3] - expected_height) <= 2
            if width <= 740 and any(w.get('t') == '‹' and w['r'][2] > 2 for w in r.widgets()):
                r.click('‹')
                row['left_collapsed_for_narrow'] = True
            input_rect = r.find('goal_input')['r']
            send_rect = r.find('发送')['r']
            content_rect = r.find('chat_list')['r']
            assert input_rect[2] > 80 and input_rect[3] >= 28
            assert content_rect[2] > 80 and content_rect[3] >= 80
            dock_top = native['w'][0]['sz'][1] - 88
            assert input_rect[1] + input_rect[3] <= dock_top and send_rect[1] + send_rect[3] <= dock_top
            row.update({'input_rect': input_rect, 'send_rect': send_rect,
                        'content_rect': content_rect, 'above_dock': True})
            r.set_text('goal_input', '长文本可编辑检查：' + '合成输入，不提交。' * 12)
            assert r.find('goal_input')['val'].endswith('合成输入，不提交。')
            r.set_text('goal_input', '')
            shot(r, folder / 'chat.png')
            pages = []
            for page, pane in [('记忆', 'memory_body'), ('邮箱', 'mail_list_body'),
                               ('日历', 'calendar_editor'), ('操作记录', 'activity_body'),
                               ('能力授权', 'capabilities_body'), ('设置', 'settings_body')]:
                goto(page)
                if width <= 740 and any(w.get('t') == '‹' for w in r.widgets()):
                    r.click('‹')
                r.wait_for('calendar_editor' if page == '日历' else 'page_content', 15)
                actual_pane = pane if any(w.get('i') == pane for w in r.widgets()) else 'page_content'
                area = r.find(actual_pane)['r']
                assert area[2] > 80 and area[3] >= 80, (page, area)
                r.scroll(int(area[0] + area[2] - 4), int(area[1] + area[3] / 2), 500)
                shot(r, folder / (pane + '-scrolled.png'))
                r.scroll(int(area[0] + area[2] - 4), int(area[1] + area[3] / 2), -10000)
                pages.append({'page': page, 'pane_id': actual_pane, 'pane': area, 'scrolled': True})
            row['pages'] = pages
            row['long_input_edited_and_cleared'] = True
            errors = [line for line in r.log(300)['l'] if '[E]' in line or 'budget exceeded' in line]
            assert not errors, errors
            row['pass'] = True
        except Exception as error:
            row['error'] = f'{type(error).__name__}: {error}'
            (folder / 'exception.txt').write_text(traceback.format_exc())
        try:
            (folder / 'snap.json').write_bytes(r.request('/snap'))
            (folder / 'log.json').write_bytes(r.request('/log', n=300))
            shot(r, folder / 'visible.png')
        except Exception as error:
            row['capture_error'] = str(error)
        (a.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(row, ensure_ascii=False), flush=True)
    report['persistent_files_equal'] = all(sha(jail / name) == digest for name, digest in before.items())
    report['passed'] = sum(row['pass'] for row in report['sizes'])
    (a.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert report['passed'] == 4 and report['persistent_files_equal']


if __name__ == '__main__':
    main()
