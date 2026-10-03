#!/usr/bin/env python3
"""A new message must land on screen, not somewhere below the pane.

Visible card-host window, synthetic host transport, isolated app-data. Messages
go through the real 发送 button; the model call is answered by the fixture, so
nothing is inferred and nothing leaves this machine.

Why this shape: the runtime gives the app script no scroll API at all (`View`
answers `set_visible` / `is_visible` / `render` and nothing else, and the
ScrollBars offset is a Rust-side field), so the conversation cannot be
*commanded* to scroll to its newest line. The app instead renders only a tail
window that fits the pane — ScrollBars clamps its offset into
`[0, view_total - view_visible]`, so a window that fits is pinned at offset 0,
and offset 0 of a window that ends with the newest message is that message.
This test is what makes that claim checkable: it asserts the newest message is
inside the pane after every send and that older lines stay reachable.
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from visual_capture import HOST, TRANSPORT, Remote  # noqa: E402

SCENE = '''
fn tail_visible_seed(){
 if fs.exists("tail-seeded.json") { return }
 if !chat_ready { start_timeout(0.15, || tail_visible_seed()) return }
 if chat_sessions.len() == 0 { chat_new_session() }
 if chat_sessions.len() == 0 { start_timeout(0.15, || tail_visible_seed()) return }
 if chat_selected_id == "" { chat_select_session(chat_sessions[0].id) }
 while messages.len() > 0 { messages.pop() }
 let labels = ["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四"]
 let roles = ["user","assistant","user","assistant","user","assistant","user","assistant","user","assistant","user","assistant","user","assistant"]
 for i in 14 {
  messages.push({role: roles[i] text: "chat_tail 合成消息 " + (i + 1) + " / " + labels[i]
   state: "success" at: time_now() project: gm_project owner: gm_owner})
 }
 chat_save()
 set_page("Chat")
 if page != "Chat" { start_timeout(0.15, || tail_visible_seed()) return }
 fs.write("tail-seeded.json", {count: messages.len()}.to_json())
 redraw()
}
start_timeout(1.0, || tail_visible_seed())
'''
NUM = re.compile(r'^chat_tail 合成消息 (\d+)')
SENT_TEXT = 'chat_tail 发送测试'


def wait_until(check, description, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if check():
                return
        except (OSError, AssertionError, json.JSONDecodeError):
            pass
        time.sleep(0.15)
    raise AssertionError(description)


def message_labels(remote):
    out = {}
    for widget in remote.widgets():
        match = NUM.match(str(widget.get('t') or ''))
        if match and str(widget.get('ty')) == 'Label':
            out[int(match.group(1))] = widget['r']
    return out


def pane_labels(remote, pane):
    """Every conversation line actually drawn, in screen order."""
    px, py, pw, ph = pane
    rows = [w for w in remote.widgets()
            if str(w.get('ty')) == 'Label' and w['r'][2] > 2 and w['r'][3] > 2
            and w['r'][1] >= py - 2 and w['r'][1] + w['r'][3] <= py + ph + 2
            and w['r'][0] >= px - 2 and w['r'][0] <= px + pw]
    return [{'t': str(r.get('t'))[:40], 'r': r['r'], 'in_pane': inside(r['r'], pane)}
            for r in sorted(rows, key=lambda r: r['r'][1])]


def inside(rect, pane, slack=2):
    x, y, width, height = rect
    px, py, pw, ph = pane
    return (x >= px - slack and y >= py - slack
            and x + width <= px + pw + slack and y + height <= py + ph + slack)


def click_text(remote, predicate, description):
    for widget in remote.widgets():
        if widget.get('ty') in ('Button', 'ButtonFlat') and predicate(str(widget.get('t') or '')):
            x, y, width, height = widget['r']
            if width < 2 or height < 2:
                break
            remote.request('/click', x=int(x + width / 2), y=int(y + height / 2), wait=1)
            return str(widget['t'])
    raise AssertionError(description)


def last_message(state_dir):
    saved = json.loads((state_dir / 'muse-goals/chat-sessions.json').read_text())
    for session in saved['sessions']:
        texts = [str(m.get('text') or '') for m in session.get('messages') or []]
        if SENT_TEXT in texts:
            index = texts.index(SENT_TEXT)
            return session['messages'][index:]
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8598)
    # 990x546 mirrors the real app card inside the Shell, so the pane under test
    # is the 510x405 pane the budget was measured for.
    parser.add_argument('--size', default='990x546')
    parser.add_argument('--source-bundle', type=Path, default=ROOT / 'official_muse/app/bundle')
    args = parser.parse_args()

    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', args.port)) == 0:
            raise RuntimeError('Existing window is protected; choose a free port.')

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    bundle = out / 'bundle'
    shutil.copytree(args.source_bundle, bundle)
    source = (bundle / 'main.splash').read_text()
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.MULTILINE)
    if marker is None:
        raise RuntimeError('Startup marker missing; fixture injection is refused.')
    injected = source[:marker.start()] + TRANSPORT + SCENE + '\n' + source[marker.start():]
    (bundle / 'main.splash').write_text(injected.replace('host.request(', 'visual_host('))

    state = out / 'state'
    env = dict(os.environ, MAKEPAD_REMOTE=str(args.port))
    env.pop('MAKEPAD_HIDE_WINDOWS', None)
    env.pop('MAKEPAD_FOCUS', None)
    remote = Remote(args.port)
    log = (out / 'runtime.log').open('w')
    proc = subprocess.Popen(
        [str(HOST), '--bundle', str(bundle), '--app-data', str(state),
         '--allow-unsigned', '--stamp', '--size', args.size],
        env=env, cwd=HOST.parents[2], stdout=log, stderr=log)

    report = {'failed': []}
    try:
        wait_until(lambda: (state / 'muse-goals/tail-seeded.json').exists(), 'fixture did not seed')
        wait_until(lambda: len(message_labels(remote)) > 0, 'no conversation rendered')
        time.sleep(0.8)

        pane = remote.find('chat_list')['r']
        report['pane'] = pane
        first = message_labels(remote)
        report['visible_after_seed'] = sorted(first)
        report['pane_lines_after_seed'] = pane_labels(remote, pane)
        newest = 14
        if newest not in first:
            report['failed'].append('the newest seeded message is not on screen')
        elif not inside(first[newest], pane):
            report['failed'].append(f'the newest seeded message sticks out of the pane: {first[newest]} vs {pane}')
        if 1 in first:
            report['failed'].append('the oldest seeded message is drawn; the window is not bounded')

        pager = click_text(remote, lambda t: t.startswith('↑ 更早的'), 'no "older messages" control')
        report['pager_label'] = pager
        time.sleep(0.6)
        paged = message_labels(remote)
        report['visible_after_paging_back'] = sorted(paged)
        if not paged or min(paged) >= min(first):
            report['failed'].append('paging back did not reveal older messages')

        latest = click_text(remote, lambda t: t == '回到最新', 'no "back to newest" control')
        report['latest_label'] = latest
        time.sleep(0.6)
        returned = message_labels(remote)
        report['visible_after_return'] = sorted(returned)
        if newest not in returned:
            report['failed'].append('"back to newest" did not return to the newest message')

        remote.set_text('goal_input', SENT_TEXT)
        time.sleep(0.3)
        remote.click('发送')
        time.sleep(2.0)
        after_send = [w for w in remote.widgets() if str(w.get('t')) == SENT_TEXT]
        report['visible_after_send'] = sorted(message_labels(remote))
        if not after_send:
            report['failed'].append('the sent message is not on screen')
        elif not inside(after_send[0]['r'], pane):
            report['failed'].append(f'the sent message sticks out of the pane: {after_send[0]["r"]} vs {pane}')

        wait_until(lambda: len(last_message(state)) >= 2 and last_message(state)[-1]['role'] == 'assistant',
                   'the reply never arrived', seconds=30)
        time.sleep(1.0)
        reply = str(last_message(state)[-1].get('text') or '')
        replies = [w for w in remote.widgets() if str(w.get('t')) == reply]
        report['reply_text'] = reply[:60]
        report['visible_after_reply'] = sorted(message_labels(remote))
        report['pane_lines_after_reply'] = pane_labels(remote, pane)
        if not replies:
            report['failed'].append('the reply is not on screen')
        elif not inside(replies[0]['r'], pane):
            report['failed'].append(f'the reply sticks out of the pane: {replies[0]["r"]} vs {pane}')
        still_sent = [w for w in remote.widgets() if str(w.get('t')) == SENT_TEXT]
        if not still_sent:
            report['failed'].append('the sent message left the screen when the reply arrived')

        logged_errors = [line for line in (out / 'runtime.log').read_text().splitlines() if '[E]' in line]
        if logged_errors:
            report['failed'].append('Runtime logged an error: ' + logged_errors[0][:200])

        report.update({
            'kind': 'VISIBLE_CARD_HOST_SYNTHETIC',
            'real_model': False,
            'real_mail': False,
        })
    except AssertionError as error:
        report['failed'].append(str(error))
    finally:
        try:
            remote.request('/quit')
        except OSError:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        log.close()

    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(bool(report['failed']))


if __name__ == '__main__':
    main()
