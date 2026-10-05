#!/usr/bin/env python3
"""rc49 visible card-host T19 probe; synthetic state and intercepted services only."""
import hashlib, json, os, re, shutil, socket, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from visual_capture import Remote, TRANSPORT, shot

HOST = ROOT / 'official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host'
SOURCE = ROOT / 'official_muse/rc/submission-ready-20261006-r1/readable-rc49-r2'
PORT = 8517
SCENE = '''
fn t19_seed(){
 if !chat_ready || !gm_ready { start_timeout(0.1, || t19_seed()) return }
 if chat_sessions.len() < 16 { chat_new_session() }
 if chat_sessions.len() < 16 { start_timeout(0.1, || t19_seed()) return }
 let long_text = ""
 for i in 24 { long_text = long_text + "合成验收段落 " + i + "：检查长正文换行与滚动；这不是模型回答，也不代表真实外部动作。\\n" }
 for i in chat_sessions.len() {
  chat_sessions[i].title = "合成长标题 " + i + "：当前项目的记忆、日历安排与邮件回复，这是用于检查两行省略和点击区域的完整标题。"
  chat_sessions[i].messages = [{role: "assistant" text: long_text state: "success" at: time_now()}]
 }
 chat_sessions[1].title = "短标题"
 messages = chat_sessions[chat_session_index(chat_selected_id)].messages
 chat_save()
 ui.goal_input.set_text("")
 fs.write("t19-seeded.json",{sessions: chat_sessions.len()}.to_json())
 redraw()
}
start_timeout(1.0, || t19_seed())
'''

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def main(size):
    out = HERE / ('visible-' + size + '-' + (sys.argv[2] if len(sys.argv)>2 else 'r1'))
    out.mkdir(exist_ok=False)
    with socket.socket() as probe:
        assert probe.connect_ex(('127.0.0.1', PORT)) != 0, 'Port occupied; existing process protected'
    bundle = out / 'bundle'
    shutil.copytree(SOURCE, bundle)
    source = (bundle / 'main.splash').read_text()
    assert hashlib.sha256(source.encode()).hexdigest() == '2bad514d69d777fabb9ad2daf2b0aa2862555c2db5c146b22bc635b3b1e70484'
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    assert marker, 'Missing verified startup marker'
    fixture = source[:marker.start()] + TRANSPORT + SCENE + source[marker.start():]
    (bundle / 'main.splash').write_text(fixture.replace('host.request(', 'visual_host('))
    manifest = json.loads((bundle / 'manifest.json').read_text())
    manifest['integrity'].pop('signature', None)
    save(bundle / 'manifest.json', manifest)
    env = dict(os.environ, MAKEPAD_REMOTE=str(PORT))
    env.pop('MAKEPAD_HIDE_WINDOWS', None)
    env.pop('MAKEPAD_NO_FOCUS', None)
    env.pop('MAKEPAD_FOCUS', None)
    r = Remote(PORT)
    statefile = out / 'state/muse-goals/chat-sessions.json'
    report = {'kind': 'FIXTURE_VISIBLE_CARD_HOST', 'requested_size': size,
              'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'host_sha256': hashlib.sha256(HOST.read_bytes()).hexdigest(),
              'external_actions': False, 'checks': {}, 'failures': []}
    def check(name, fn):
        try:
            report['checks'][name] = fn()
        except Exception as error:
            report['failures'].append({'check': name, 'error': str(error)})
        save(out / 'report.json', report)
    def capture(name):
        shot(r, out / (name + '.png'))
        save(out / (name + '.snap.json'), r.widgets())
        pixels = Image.open(out / (name + '.png')).convert('RGB')
        assert max(pixels.getextrema())[1]-min(pixels.getextrema())[0] > 20, 'Blank capture; not visual evidence'
    def controls():
        actual = report['actual_window']['sz']
        bounds = {}
        for key in ['goal_input', 'send_button']:
            rect = r.find(key)['r']; x, y, w, h = rect
            assert w >= 24 and h >= 24 and x >= 0 and y >= 0 and x+w <= actual[0]+1 and y+h <= actual[1]+1, (key, rect, actual)
            bounds[key] = rect
        r.set_text('goal_input', '合成输入检查，不发送')
        assert r.find('goal_input')['val'] == '合成输入检查，不发送'
        r.set_text('goal_input', '')
        r.click('send_button')
        assert any('请输入消息' in w.get('t', '') for w in r.widgets()), 'Empty-send validation not observed'
        return bounds
    log = (out / 'runtime.log').open('w')
    proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(out/'state'),
                             '--allow-unsigned', '--stamp', '--size', size], cwd=HOST.parents[2], env=env, stdout=log, stderr=log)
    try:
        deadline = time.monotonic()+35
        while not (out/'state/muse-goals/t19-seeded.json').exists():
            if proc.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Seed/startup failed; see runtime.log')
            time.sleep(.2)
        time.sleep(.5)
        status = json.loads(r.request('/s')); save(out/'remote-status.json', status)
        report['actual_window'] = status['w'][0]
        capture('expanded')
        report['png_pixels'] = list(Image.open(out/'expanded.png').size)
        before = json.loads(statefile.read_text())
        assert len(before['sessions']) == 16
        check('expanded_controls', controls)
        def sidebar():
            checks = []
            for bottom in [False, True]:
                x,y,w,h = r.find('history_list')['r']
                r.scroll(int(x+w/2), int(y+h/2), 10000 if bottom else -10000)
                visible = [a for a in r.widgets() if a.get('ty')=='Button' and a.get('t')=='删除'
                           and a['r'][3]>=34 and y<=a['r'][1] and a['r'][1]+a['r'][3]<=y+h]
                assert visible, ('No fully visible delete button', [x,y,w,h])
                button = visible[-1] if bottom else visible[0]
                bx,by,bw,bh = button['r']
                assert bx+bw <= x+w-12, 'Delete overlaps scrollbar'
                r.request('/click', x=int(bx+bw/2), y=int(by+bh/2))
                r.wait_for('delete_chat_cancel')
                assert any(a.get('t')=='删除对话？' for a in r.widgets())
                r.click('delete_chat_cancel')
                titles = [a for a in r.widgets() if a.get('ty')=='Button' and (a.get('t','').startswith('合成长标题') or a.get('t')=='短标题')
                          and a['r'][3]==48 and y<=a['r'][1] and a['r'][1]+a['r'][3]<=y+h]
                assert titles, 'No fully visible title'
                title = titles[-1] if bottom else titles[0]
                tx,ty,tw,th = title['r']
                pitches = [b['r'][1]-a['r'][1] for a,b in zip(titles,titles[1:])]
                assert all(pitch==58 for pitch in pitches), ('Expected 54 row + 4 spacing', pitches)
                r.request('/click', x=int(tx+tw/2), y=int(ty+th/2)); time.sleep(.2)
                state = json.loads(statefile.read_text())
                chosen = next(s for s in state['sessions'] if s['id']==state['selected_id'])
                assert chosen['title'] == title['t'], 'Wrong selected title'
                if size == '1400x760' and bottom: capture('oldest-and-short-title')
                checks.append({'end': 'oldest' if bottom else 'newest', 'title': title['t'],
                               'title_rect': title['r'], 'row_pitches': pitches, 'delete_rect': button['r'], 'preview_cancel': True})
            after = json.loads(statefile.read_text())
            clean = lambda d: [{k:v for k,v in s.items() if k!='updated_at'} for s in d['sessions']]
            assert clean(before)==clean(after), 'History content changed'
            return {'endpoints': checks, 'all_16_full_titles_preserved': True}
        check('sidebar_endpoints', sidebar)
        def collapse():
            r.click('‹'); r.wait_for('☰')
            result = {'left_collapsed': controls()}
            if report['actual_window']['sz'][0] > 740:
                r.click('收起'); assert not any(a.get('i')=='right_column' and a['r'][2]>0 for a in r.widgets())
                result['both_collapsed'] = controls()
            capture('collapsed')
            x,y,w,h = r.find('chat_list')['r']
            r.scroll(int(x+w-4),int(y+h/2),-10000); time.sleep(.3); shot(r,out/'long-top.png')
            r.scroll(int(x+w-4),int(y+h/2),10000); time.sleep(.3); shot(r,out/'long-bottom.png')
            assert ImageChops.difference(Image.open(out/'long-top.png').convert('RGB'),Image.open(out/'long-bottom.png').convert('RGB')).getbbox(), 'Long text scroll did not change pixels'
            result['long_text_scroll_pixel_change'] = True
            if report['actual_window']['sz'][0] > 740: r.click('›')
            r.click('☰'); r.wait_for('‹')
            result['restored'] = controls()
            return result
        check('collapse_and_long_text', collapse)
        calls = out/'state/muse-goals/visual-calls.json'
        report['intercepted_services'] = json.loads(calls.read_text()) if calls.exists() else []
        report['status'] = 'PASS' if not report['failures'] else 'PARTIAL'
    except Exception as error:
        report['failures'].append({'check': 'startup_or_harness', 'error': str(error)})
        report['status'] = 'BLOCKED'
    finally:
        save(out/'report.json', report)
        if proc.poll() is None:
            try: r.request('/quit')
            except OSError: proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()
        log.close()
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__': main(sys.argv[1])
