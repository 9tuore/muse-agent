#!/usr/bin/env python3
"""Capture official Mail owner and native login sheet; no login or delivery."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'official_muse/semifinal/calendar_integration'))
from run_owner_ui_acceptance import Remote, WindowRemote, Stop

SOURCE_SHA = '724c7d7faee03d1303b8caf20b33e6958f385a03f01bf29a92a704a477fcbf7c'
TITLE = 'OctoSense · 连接邮箱账号'
SYNTHETIC = 'INVALID-SYNTHETIC-NOT-A-CODE'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--binary-sha256', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, required=True)
    p.add_argument('--owned-window-id', type=Path, default=ROOT/'build/runtime-closure-render-compare-r1/owned-main-window-id')
    p.add_argument('--mail-source', type=Path, default=ROOT/'build/runtime-closure-full-shell-r1/sdk/apps/mail/host-service/src/lib.rs')
    p.add_argument('--probe-mask', action='store_true', help='Optional invalid synthetic input only; no submit')
    a = p.parse_args()
    binary = a.binary.resolve(strict=True); probe = a.owned_window_id.resolve(strict=True)
    assert not binary.is_relative_to(Path('/Applications')) and sha(binary) == a.binary_sha256
    receipt_path = binary.parent/'octos-kernel.json'
    receipt = json.loads(receipt_path.read_text()); kernel = binary.parent/'octos-kernel'
    assert receipt['revision'] == 'b0759a57719fd35b3a2da1c5d969bc67538ed516'
    assert sha(kernel) == receipt['sha256'] and sha(a.mail_source) == SOURCE_SHA
    assert os.access(probe, os.X_OK)
    out = a.out.resolve(); assert out.parent == ROOT/'build' and not out.exists()
    with socket.socket() as sock: sock.bind(('127.0.0.1', a.port))
    out.mkdir(mode=0o700); home = out/'home'
    env = os.environ.copy()
    for key in ('OCTOS_APP_CORE_BIN', 'OCTOSENSE_KERNEL_ANY_REVISION', 'OCTOSENSE_CONTAINED_APPS',
                'MAKEPAD_HIDE_WINDOWS', 'MAKEPAD_NO_FOCUS', 'MAKEPAD_NO_GAUSS', 'MAKEPAD_REMOTE'):
        env.pop(key, None)
    for key, leaf in {'OCTOSENSE_HOME':'shell', 'OCTOSENSE_APP_DATA':'apps', 'OCTOS_APP_CORE_DIR':'kernel/.octos',
                      'RINX_DATA_DIR':'rinx', 'ROBRIX_DATA_DIR':'rinx', 'XDG_CONFIG_HOME':'config',
                      'XDG_DATA_HOME':'data', 'XDG_CACHE_HOME':'cache'}.items():
        directory = home/leaf; directory.mkdir(parents=True, mode=0o700, exist_ok=True); env[key] = str(directory)
    env.update(OCTOSENSE_DEV_MODE='0', MAKEPAD_FOCUS='1')
    report = dict(state='PREPARED', binary_sha256=a.binary_sha256, kernel_receipt=receipt,
                  kernel_receipt_sha256=sha(receipt_path), mail_source_sha256=SOURCE_SHA,
                  source_to_binary_binding='Central build evidence required; separate source hash is not binary provenance',
                  window_probe_sha256=sha(probe), screenshots=[], checks={},
                  code_input='NOT_TESTED', real_login=False, submit_clicked=False,
                  send_clicked=False, consent_clicked=False, trusted_person='NOT_CLAIMED',
                  visual_review='REQUIRED', home=str(home))
    discovery = Remote(a.port); proc = None; log = out/'shell.log'
    def save():
        (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    def windows():
        status = json.loads(discovery.request('/s'))
        if status.get('pid') != proc.pid: raise Stop('FAIL', 'Remote PID differs from owned child')
        found = []
        for window in status.get('w', []):
            remote = WindowRemote(a.port, window['i']); widgets = remote.widgets()
            texts = [str(w.get('t', '')).strip().lower() for w in widgets]
            if any(t in ('allow', 'approve', 'grant', 'allow once', 'allow always', '允许', '批准')
                   or any(mark in t for mark in ('permission required', 'requires approval', 'trusted input',
                                                 'no_consent', '允许访问', '需要权限', '请求授权')) for t in texts):
                raise Stop('HUMAN_REQUIRED', 'Permission/consent surface; no click')
            found.append((remote, widgets))
        return found
    def locate(label, seconds=35):
        deadline = time.monotonic()+seconds
        while time.monotonic() < deadline:
            if proc.poll() is not None: raise Stop('FAIL', 'Owned Shell exited before UI ready')
            try:
                for remote, widgets in windows():
                    if any(w.get('t') == label for w in widgets): return remote, widgets
            except OSError:
                pass
            time.sleep(.2)
        raise Stop('HUMAN_REQUIRED', 'Expected native UI unavailable; no permission bypass: '+label)
    def capture(remote, label):
        windows()  # PID and permission gate before every capture/input.
        # No raw snapshot saved: drop every input value, including password val.
        sanitized = [{k: v for k, v in w.items()
                      if k not in ('val', 'value') and not (w.get('i') == 'password' and k == 't')}
                     for w in remote.widgets()]
        (out/(label+'-snapshot.json')).write_text(json.dumps(sanitized, ensure_ascii=False, indent=2)+'\n')
        target = out/(label+'-remote.png')
        for attempt in range(12):
            windows()
            try:
                remote.shot(target)
                break
            except HTTPError as error:
                if error.code != 404 or attempt == 11:
                    raise
                time.sleep(.5)  # Retry only a read-only frame, never Add/Cancel/input.
        if not target.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            raise Stop('FAIL', 'Remote screenshot is not PNG')
        report['screenshots'].append(dict(file=target.name, sha256=sha(target), remote_window=remote.window))
        ids = subprocess.check_output([str(probe), str(proc.pid)], text=True, timeout=10).splitlines()
        if not ids or any(not wid.isdigit() for wid in ids):
            raise Stop('HUMAN_REQUIRED', 'Owned CGWindow IDs unavailable')
        for wid in ids:
            target = out/(label+'-os-'+wid+'.png')
            result = subprocess.run(['screencapture', '-x', '-l', wid, str(target)], capture_output=True, timeout=15)
            if result.returncode or not target.is_file() or not target.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
                raise Stop('HUMAN_REQUIRED', 'OS capture unavailable; Screen Recording permission may be required')
            report['screenshots'].append(dict(file=target.name, sha256=sha(target), cgwindow=wid))
        save()
    save()
    try:
        with log.open('wb') as stream:
            proc = subprocess.Popen([str(binary), '--remote='+str(a.port), '--test-action', 'launch-mail'],
                                    cwd=binary.parent, env=env, stdout=stream, stderr=subprocess.STDOUT)
        report['pid'] = proc.pid; save()
        mail, _ = locate('Add account')
        capture(mail, '01-mail-owner')
        windows(); mail.click('Add account')  # One ordinary UI delivery, never repeated.
        report['add_account_clicks'] = 1
        sheet, widgets = locate(TITLE)
        capture(sheet, '02-native-sheet')
        report['checks'] = dict(chinese_title=True,
            no_username=not any(w.get('i') in ('username', 'login') for w in widgets),
            help_present=all(any(str(w.get('t', '')).startswith(prefix) for w in widgets)
                             for prefix in ('QQ 授权码：', '查找 IMAP/SMTP 服务', '入口以当前页面为准')))
        if a.probe_mask:
            # Never relax managed/secret-input policy. At most one invalid synthetic text event.
            windows()
            code = sheet.find('password')
            if code.get('val') not in ('', None): raise Stop('HUMAN_REQUIRED', 'Code field unexpectedly nonempty; do not inspect or edit it')
            x, y, w, h = code['r']
            if w <= 2 or h <= 2 or x < 0 or y < 0:
                report['code_input'] = 'NOT_TESTED_CLIPPED'
            else:
                try:
                    sheet.request('/click', x=int(x+w/2), y=int(y+h/2))
                    sheet.request('/t', t=SYNTHETIC)
                    time.sleep(.3)
                    shown = sheet.find('password')
                    if shown.get('val') == SYNTHETIC and shown.get('t') == '•'*len(SYNTHETIC):
                        report['code_input'] = 'SYNTHETIC_MASK_OBSERVED_NOT_LOGIN'
                        capture(sheet, '03-synthetic-mask')
                    else:
                        report['code_input'] = 'NOT_TESTED_INPUT_RESTRICTED_OR_MASK_UNVERIFIED'
                except OSError:
                    report['code_input'] = 'NOT_TESTED_REMOTE_INPUT_RESTRICTED'
        pane = sheet.find('card')['r']
        scroll_x, scroll_y = int(pane[0]+pane[2]/2), int(pane[1]+pane[3]/2)
        server_keys = ('pop_host', 'pop_port', 'smtp_host', 'smtp_port')
        for _ in range(10):
            windows()
            fields = {w.get('i'): w for w in sheet.widgets() if w.get('i') in server_keys}
            if all(key in fields and fields[key]['r'][2] > 2 and fields[key]['r'][3] >= 30 for key in server_keys):
                break
            sheet.scroll(scroll_x, scroll_y, 100)
        else:
            raise Stop('FAIL', 'Server fields remain clipped after bounded native scrolling')
        report['checks'].update(qq_imap=fields['pop_host'].get('val') == 'imap.qq.com',
            imap_port=fields['pop_port'].get('val') == '993',
            qq_smtp=fields['smtp_host'].get('val') == 'smtp.qq.com',
            smtp_port=fields['smtp_port'].get('val') == '465', server_controls_reachable=True)
        capture(sheet, '04-native-server-fields')
        for _ in range(10):
            windows()
            try:
                cancel = sheet.find('取消')
                if cancel['r'][2] > 2 and cancel['r'][3] >= 30:
                    break
            except AssertionError:
                pass
            sheet.scroll(scroll_x, scroll_y, -100)
        else:
            raise Stop('FAIL', 'Cancel remains clipped after bounded native scrolling')
        windows(); sheet.click('取消')
        report['cancel_clicks'] = 1
        deadline = time.monotonic()+5
        while any(w.get('t') == TITLE for _, ws in windows() for w in ws):
            if time.monotonic() > deadline: raise Stop('FAIL', 'Native sheet did not close after one cancel')
            time.sleep(.1)
        report['sheet_cancelled'] = True
        report['state'] = 'CAPTURED_NOT_VISUALLY_VERIFIED' if all(report['checks'].values()) else 'FAIL'
    except Stop as error:
        report.update(state=error.state, error=str(error))
    except Exception as error:
        report.update(state='FAIL', error=type(error).__name__+': '+str(error))
    finally:
        if proc is not None:
            report['shutdown'] = 'remote_quit'
            try:
                if proc.poll() is not None: raise RuntimeError('Owned child exited before quit')
                status = json.loads(discovery.request('/s'))
                if status.get('pid') != proc.pid: raise RuntimeError('Quit target PID mismatch')
                discovery.request('/quit'); proc.wait(timeout=10)
            except Exception:
                report['shutdown'] = 'terminate_unclean'
                if proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        report['shutdown'] = 'kill_unclean'; proc.kill(); proc.wait()
            report['exit'] = proc.returncode
            errors = [line for line in log.read_text(errors='replace').splitlines()
                      if '[E]' in line or 'script time budget exceeded' in line]
            report.update(runtime_errors=errors, log_sha256=sha(log))
            if errors or proc.returncode != 0 or report['shutdown'] != 'remote_quit':
                report['prior_state'] = report['state']; report['state'] = 'FAIL_UNCLEAN_OR_RUNTIME'
        save()
    print(json.dumps({key: report.get(key) for key in ('state', 'pid', 'exit', 'shutdown', 'code_input')}, ensure_ascii=False))
    return 0 if report['state'] == 'CAPTURED_NOT_VISUALLY_VERIFIED' else 2 if report['state'] == 'HUMAN_REQUIRED' else 1

if __name__ == '__main__':
    raise SystemExit(main())
