"""Read/UI-only responsive smoke on Root's existing synthetic Shell.

Uses actual Shell move/resize chords. Never confirms or submits a task.
The real-account Mail reply/Calendar confirmation remain separate gates.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import argparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import navigate, shot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, default=ROOT/'official_muse/app/build/ui-memory-20261003/candidate-037-prelim-rc6-minimax')
    parser.add_argument('--out', type=Path, default=ROOT/'official_muse/prelim/evidence/live/rc6-responsive')
    parser.add_argument('--port', type=int, default=8412)
    parser.add_argument('--root-widget', default='166', help='Root ID observed in this Shell snapshot')
    args = parser.parse_args()
    assert args.port not in [8401,8413,8414], 'User and real-account windows are excluded'
    candidate = args.candidate.resolve()
    out = args.out.resolve()
    jail = candidate / 'private/apps/muse-goals'
    meta = json.loads((candidate / 'candidate.json').read_text())
    assert meta['profile_kind'] == 'AUTHORIZED_MODEL_ONLY_SYNTHETIC'
    assert hashlib.sha256((jail / 'bundle/main.splash').read_bytes()).hexdigest() == meta['source_sha256']
    ledger = candidate / 'private/apps/.host/model/ledger.json'
    before = ledger.read_bytes() if ledger.is_file() else None
    r = Remote(args.port)
    out.mkdir(parents=True, exist_ok=True)
    report = {'kind': 'REAL_VISIBLE_SHELL_UI_ONLY', 'source_sha256': meta['source_sha256'],
              'host_sha256': meta['host_sha256'], 'cases': [],
              'boundary': 'Synthetic model profile. No model submit, Mail send or Calendar write. Actual mail/reply/confirmation responsive gates pending.'}

    def save():
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def sidebar_open():
        layout = jail / 'ui-layout.json'
        if layout.exists():
            return json.loads(layout.read_text())['sidebar_open']
        # A fresh profile has no saved preference until its first toggle.
        # Observe the actual toggle rather than write a fabricated preference.
        buttons = [w.get('t') for w in r.widgets() if w.get('ty') == 'Button']
        assert ('‹' in buttons) != ('☰' in buttons), 'Sidebar state is ambiguous'
        return '‹' in buttons

    def expand():
        if not sidebar_open():
            try:
                r.click('☰')
            except AssertionError as error:
                # Remote may report the old toggle missing during its frame
                # retry even though the first click already changed state.
                # Accept only observed state; never blindly toggle again.
                if not sidebar_open():
                    raise
                report.setdefault('remote_toggle_warnings', []).append(str(error))
            time.sleep(.4)

    def collapse():
        if sidebar_open():
            try:
                r.click('‹')
            except AssertionError as error:
                if sidebar_open():
                    raise
                report.setdefault('remote_toggle_warnings', []).append(str(error))
            time.sleep(.4)

    def resize(width, outer_height):
        # Root ID is supplied from this Shell snapshot, not a native window API.
        x, y, w, h = r.find(args.root_widget)['r']
        # The bottom corner can be covered by Shell's Dock; the observed
        # resize handler accepts any point in the bottom/right half.
        sx, sy = int(x+w*.85), int(y+h*.65)
        # Caption is 31px in this frozen Shell. Available screen caps the
        # requested 892px tall case; keep the composer above the native Dock.
        target_h = min(outer_height-31, 620)
        tx, ty = int(sx+width-w), int(sy+target_h-h)
        r.request('/m', k='down', x=sx, y=sy, b=1, cmd=1)
        r.request('/m', k='move', x=tx, y=ty, b=1, cmd=1)
        r.request('/m', k='up', x=tx, y=ty, b=1, cmd=1)
        time.sleep(.4)
        # A WM resize updates its root before the embedded app's next frame.
        # A local sidebar toggle forces that frame without submitting work.
        if sidebar_open():
            collapse()
        expand()
        return r.find(args.root_widget)['r']

    # The wide case must fit the native Shell bounds, including its Dock.
    # Use the observed Shell super+primary move chord on the Muse title area.
    x,y,w,h = r.find(args.root_widget)['r']
    sx,sy = int(x+30),int(y+30)
    r.request('/m', k='down', x=sx, y=sy, b=0, cmd=1)
    r.request('/m', k='move', x=int(sx+84-x), y=int(sy+72-y), b=0, cmd=1)
    r.request('/m', k='up', x=int(sx+84-x), y=int(sy+72-y), b=0, cmd=1)
    time.sleep(.3)
    report['origin_after_move'] = r.find(args.root_widget)['r']
    for width, height in [(412, 892), (990, 539), (1260, 600), (1200, 420)]:
        actual = resize(width, height)
        tag = f'{width}x{height}'
        item = {'requested_outer': [width, height], 'actual_muse_content': actual, 'pages': {}}
        report['cases'].append(item)
        save()
        expand()
        navigate(r, '对话')
        shot(r, out / (tag+'-chat-expanded.png'))
        item['chat_expanded_input'] = r.find('goal_input')['r']
        if width <= 740:
            collapse()
            item['chat_collapsed_input'] = r.find('goal_input')['r']
        text = '合成界面长文本检查：这段文字只填写到输入框，不提交、不调用模型。' * 4
        r.set_text('goal_input', text)
        item['long_input_readback'] = r.find('goal_input').get('val') == text
        item['input_rect'] = r.find('goal_input')['r']
        item['input_usable'] = item['input_rect'][2] > 80 and item['input_rect'][3] >= 28
        shot(r, out / (tag+'-chat-long-input.png'))
        r.set_text('goal_input', '')
        expand()
        for page, area in [('记忆', 'page_content'), ('设置', 'settings_body')]:
            navigate(r, page)
            rect = r.find(area)['r']
            item['pages'][page] = {'body_rect': rect, 'body_usable': rect[2] > 80 and rect[3] > 60}
            shot(r, out / (tag+'-'+page+'.png'))
        save()
    resize(990, 539)
    navigate(r, '设置')
    ws = r.widgets()
    labels = [w.get('t', '') for w in ws if w.get('ty') == 'Label']
    report['settings'] = {'appearance_heading': '外观与模型' in labels,
        'appearance_text': 'Muse 当前为深色外观。' in labels,
        'official_model_management_text': '模型由 OctoSense 的“AI 模型设置”管理；此处只读。' in labels}
    shot(r, out / 'settings-current.png')
    navigate(r, '对话')
    report['ledger_bytes_unchanged'] = (ledger.read_bytes() if ledger.is_file() else None) == before
    report['status'] = 'PASS_UI_SUBSET' if report['ledger_bytes_unchanged'] and all(
        c['input_usable'] and c['long_input_readback'] and all(v['body_usable'] for v in c['pages'].values())
        for c in report['cases']) else 'FAIL'
    save()
    print(json.dumps({'status': report['status'], 'cases': len(report['cases']), 'model_increment_zero': report['ledger_bytes_unchanged']}))


if __name__ == '__main__':
    main()
