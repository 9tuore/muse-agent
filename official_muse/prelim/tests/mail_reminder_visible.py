#!/usr/bin/env python3
"""Real visible UI, explicit synthetic mailbox; no model or external writes."""
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
from visual_capture import HOST, Remote, navigate, shot

TRANSPORT = '''
let popup_calls = [] let popup_ok = true
// 字段形状必须与真实宿主一致：宿主 header() 给出的 time 是显示串（"Oct 03"），
// 机器时间在 date（ISO 8601）；host 的 mail.sync 只返回 {new,total}，没有 has_more/reset。
// 之前 fixture 用数字 time + has_more，正是它让「真实 mail.list 一律被判无效」的缺陷测不出来。
let popup_rows = [{id: "old" sender: "合成历史邮件" subject: "旧主题" time: "Oct 03" date: "2026-10-03T07:16:39+00:00" historical: true}]
fn popup_host(service,args,cb){
 popup_calls.push(service) fs.write("popup-calls.json",popup_calls.to_json())
 if service == "mail.accounts" { cb({is_ok: true data: [{id: "synthetic-account" address: "self@example.invalid"}]}) return }
 if service == "mail.add_account" {
  cb({is_ok: true})
  start_timeout(0.8, || {
   popup_rows.push({id: "new" sender: "合成来信发件人" subject: "新邮件自动提醒验收" time: "Oct 03" date: "2026-10-03T09:16:39+00:00" historical: false})
   mail_watch_poll()
   start_timeout(6.0, || {popup_ok = false mail_watch_poll()})
  }) return
 }
 if service == "mail.sync" { cb({is_ok: popup_ok data: {new: popup_rows.len() total: popup_rows.len()} error: "synthetic disconnect"}) return }
 if service == "mail.list" { cb({is_ok: true data: {messages: popup_rows total: popup_rows.len()}}) return }
 if service == "mail.message" { cb({is_ok: true data: {id: args.message address: "sender@example.invalid" body: "这是本地合成的新邮件正文，只验收自动来信卡，不发送邮件。"}}) return }
 if service == "calendar.status" { cb({is_ok: true data: {permission: "not_determined" calendars: []}}) return }
 cb({is_ok: false error: "synthetic environment forbids this operation"})
}
'''


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', 8490)) == 0:
            raise RuntimeError('Test port occupied; existing process protected')
    bundle = out / 'bundle'
    source_bundle = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else ROOT / 'official_muse/app/bundle'
    shutil.copytree(source_bundle, bundle)
    source = (bundle / 'main.splash').read_text()
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.MULTILINE)
    if marker is None:
        raise RuntimeError('Startup marker missing; fixture injection is refused.')
    fixture_source = source[:marker.start()] + TRANSPORT + '\n' + source[marker.start():]
    (bundle / 'main.splash').write_text(fixture_source.replace('host.request(', 'popup_host('))
    data = out / 'state/muse-goals'
    data.mkdir(parents=True)
    (data / 'mail-watch.json').write_text(json.dumps({'schema': 1, 'enabled': False, 'accounts': [], 'alerts': []}))
    (data / 'ui-layout.json').write_text(json.dumps({'schema': 1, 'sidebar_open': True, 'right_open': False}))
    (data / 'notification-settings.json').write_text(json.dumps({'schema': 1, 'enabled': False}))
    env = dict(os.environ, MAKEPAD_REMOTE='8490')
    env.pop('MAKEPAD_HIDE_WINDOWS', None)
    r = Remote(8490)
    checks = {}
    with (out / 'runtime.log').open('w') as log:
        proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(out / 'state'),
                                 '--allow-unsigned', '--stamp', '--size', '1200x650'], env=env,
                                cwd=HOST.parents[2], stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 20
            while True:
                try:
                    r.find('对话')
                    break
                except (OSError, AssertionError):
                    if proc.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('Visible UI did not start; inspect runtime.log')
                    time.sleep(.1)
            time.sleep(1.5)
            navigate(r, '邮箱')
            r.wait_for('连接账号')
            r.click('连接账号')
            navigate(r, '对话')
            r.wait_for('新邮件自动提醒验收')
            checks['new_arrival_visible_without_opening_results'] = True
            checks['sender_visible'] = r.find('发件人 · 合成来信发件人')['r'][2] > 20
            checks['body_visible'] = any('这是本地合成的新邮件正文' in w.get('t', '') for w in r.widgets())
            checks['reply_and_decline_reachable'] = all(r.find(k)['r'][2] > 20 and r.find(k)['r'][3] >= 24 for k in ('回复这封邮件', '不予回复'))
            shot(r, out / 'automatic-incoming-card.png')
            r.wait_for('邮箱暂时无法同步', seconds=12)
            checks['disconnect_visible'] = r.find('检查邮箱连接')['r'][2] > 20
            checks['existing_mail_retained_on_failure'] = r.find('新邮件自动提醒验收')['r'][2] > 20
            shot(r, out / 'connection-failure-card.png')
            checks['no_model_or_external_write'] = not any(s in ('model.complete', 'mail.send', 'mail.delete', 'calendar.create') for s in json.loads((data / 'popup-calls.json').read_text()))
            checks['no_runtime_error'] = '[E]' not in (out / 'runtime.log').read_text() and 'script time budget exceeded' not in (out / 'runtime.log').read_text()
        except Exception as error:
            checks['error'] = str(error)
            try:
                shot(r, out / 'failure.png')
            except OSError:
                pass
        finally:
            try:
                r.request('/quit')
            except OSError:
                proc.terminate()
            proc.wait(timeout=5)
    checks.update(kind='VISIBLE_CARD_HOST_SYNTHETIC_MAIL', source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  real_model=False, real_mail=False, real_calendar=False)
    checks['failed'] = [k for k, v in checks.items() if isinstance(v, bool) and not v and not k.startswith('real_')]
    (out / 'report.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(checks, ensure_ascii=False))
    return bool(checks['failed'] or checks.get('error'))


if __name__ == '__main__':
    raise SystemExit(main())
