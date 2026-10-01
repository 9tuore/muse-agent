#!/usr/bin/env python3
"""Inspect a copied packaged window in isolated data and capture only that window."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready

WINDOW_ID_SOURCE = r'''
#import <Cocoa/Cocoa.h>
#import <CoreGraphics/CoreGraphics.h>
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    pid_t target = (pid_t)atoi(argv[1]);
    CFArrayRef windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID);
    for (NSDictionary *entry in (__bridge NSArray *)windows) {
        if ([entry[(id)kCGWindowOwnerPID] intValue] == target &&
            [entry[(id)kCGWindowLayer] intValue] == 0 &&
            [entry[(id)kCGWindowName] isEqualToString:@"Muse · GOSIM"]) {
            printf("%u\n", [entry[(id)kCGWindowNumber] unsignedIntValue]);
            CFRelease(windows);
            return 0;
        }
    }
    CFRelease(windows);
    return 1;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--card-state', choices=('default', 'long', 'error'), default='default')
    parser.add_argument('--small-both', action='store_true')
    parser.add_argument('--all-sizes', action='store_true')
    parser.add_argument('--d27-matrix', action='store_true')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    copied = out / 'Muse-UI-Review.app'
    shutil.copytree(args.app.resolve(strict=True), copied, symlinks=True)
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(copied)], check=True)
    workspace = out / 'workspace'
    workspace.mkdir()
    helper_source = out / 'window_id.m'
    helper_source.write_text(WINDOW_ID_SOURCE)
    helper = out / 'window_id'
    subprocess.run(['/usr/bin/clang', '-fobjc-arc', '-framework', 'Cocoa', '-framework', 'CoreGraphics',
                    str(helper_source), '-o', str(helper)], check=True)
    observations = []
    assert sum((args.small_both, args.all_sizes, args.d27_matrix)) <= 1
    if args.d27_matrix:
        cases = [('default', 'light', 1280, 800), ('default', 'dark', 1280, 800),
                 ('default', 'light', 980, 640), ('default', 'dark', 980, 640),
                 ('long', 'light', 980, 640), ('long', 'dark', 980, 640),
                 ('error', 'light', 980, 640), ('error', 'dark', 980, 640)]
    else:
        sizes = ([('light', 1280, 800), ('dark', 1280, 800),
                  ('light', 980, 640), ('dark', 980, 640)] if args.all_sizes else
                 [('light', 980, 640), ('dark', 980, 640)] if args.small_both else
                 [('light', 1280, 800), ('dark', 980, 640)])
        cases = [(args.card_state, appearance, width, height) for appearance, width, height in sizes]
    for card_state, appearance, width, height in cases:
        env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_DEV_UI='0',
                   GOSIM_LOCAL_INBOX='0', GOSIM_UI_TEST_APPEARANCE=appearance,
                   GOSIM_SKIP_ONBOARDING='1')
        if card_state != 'default':
            env['GOSIM_UI_TEST_CARD'] = card_state
        stem = f'{card_state}-{appearance}-{width}x{height}'
        with (out / f'{stem}.stdout').open('w') as stdout, (out / f'{stem}.stderr').open('w') as stderr:
            proc = subprocess.Popen([str(copied / 'Contents/MacOS/GOSIM-Local-Agent')],
                                    env=env, stdout=stdout, stderr=stderr)
            try:
                wait_for('Muse window', lambda: window_ready(proc.pid))
                ax(proc.pid, f'set size of window "Muse · GOSIM" to {{{width}, {height}}}')
                time.sleep(2.5 if card_state != 'default' else 0.5)
                names = ax(proc.pid, 'get entire contents of window "Muse · GOSIM"')
                for label in ('对话', '长期目标', '记忆', '活动记录', '发送',
                              '设为长期目标', 'Edge 搜索目标', 'radio group 1'):
                    assert label in names, (label, names)
                if card_state == 'default':
                    for label in ('QQ 邮箱', '日历', '电脑能力'):
                        assert label in names, (label, names)
                selected = ax(proc.pid, 'get value of radio button 2 of radio group 1 of window "Muse · GOSIM"')
                assert selected == ('0' if card_state == 'default' else '1'), (card_state, selected)
                focus = None
                if card_state == 'default' and appearance == 'light' and (width, height) == (1280, 800):
                    try:
                        ax(proc.pid, 'click text field "即时对话输入" of group 2 of window "Muse · GOSIM"')
                        before = ax(proc.pid, 'get focused of text field "即时对话输入" of group 2 of window "Muse · GOSIM"')
                        subprocess.run(['/usr/bin/osascript', '-e', 'tell application "System Events" to key code 48'],
                                       check=True, capture_output=True, text=True, timeout=8)
                        after = ax(proc.pid, 'get focused of text field "即时对话输入" of group 2 of window "Muse · GOSIM"')
                        focus = {'input_focused_after_click': before, 'input_focused_after_tab': after,
                                 'status': 'PASS_LOCAL' if before == 'true' and after == 'false' else 'PARTIAL'}
                    except (AssertionError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                        focus = {'status': 'NOT_TESTED', 'reason': str(exc)[:240]}
                wid = subprocess.check_output([str(helper), str(proc.pid)], text=True).strip()
                image = out / f'{stem}.png'
                capture = subprocess.run(['/usr/sbin/screencapture', '-x', '-l', wid, str(image)],
                                         capture_output=True, text=True)
                assert capture.returncode == 0 and image.is_file(), capture.stderr
                scroll = None
                if card_state == 'long':
                    try:
                        target = 'scroll area 1 of group 3 of window "Muse · GOSIM"'
                        full_text = ax(proc.pid, 'get value of text area 1 of ' + target)
                        assert len(full_text) > 180, 'long card text missing'
                        before = ax(proc.pid, 'get value of scroll bar 1 of ' + target)
                        ax(proc.pid, 'set value of scroll bar 1 of ' + target + ' to 1.0')
                        time.sleep(0.4)
                        after = ax(proc.pid, 'get value of scroll bar 1 of ' + target)
                        scrolled_image = out / f'{stem}-scrolled.png'
                        capture = subprocess.run(['/usr/sbin/screencapture', '-x', '-l', wid, str(scrolled_image)],
                                                 capture_output=True, text=True)
                        assert capture.returncode == 0 and scrolled_image.is_file(), capture.stderr
                        scroll = {'full_text_chars': len(full_text), 'position_before': before,
                                  'position_after': after, 'screenshot': str(scrolled_image),
                                  'status': 'PASS_LOCAL' if before != after else 'PARTIAL'}
                    except AssertionError as exc:
                        scroll = {'status': 'NOT_TESTED', 'reason': str(exc)[:240]}
                observations.append({'appearance': appearance, 'size': [width, height],
                                     'card_state': card_state,
                                     'screenshot': str(image), 'buttons': names,
                                     'keyboard_focus': focus, 'long_card_scroll': scroll})
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
    (out / 'observations.json').write_text(json.dumps(observations, ensure_ascii=False, indent=2))
    settings_path = workspace / '.muse_model_settings.json'
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else None
    no_key_profile = settings is None or all(not profile.get('keychain_service')
                                               for profile in settings.get('profiles', {}).values())
    assert no_key_profile, 'isolated UI workspace unexpectedly configured a high-tier key'
    usage_path = workspace / '.muse_model_usage.json'
    usage = json.loads(usage_path.read_text()) if usage_path.exists() else {}
    assert usage.get('remote_calls', 0) == 0 and not usage.get('reservations'), usage
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(copied)], check=True)
    status = 'PARTIAL' if any(item['keyboard_focus'] and item['keyboard_focus']['status'] != 'PASS_LOCAL'
                              for item in observations) else 'PASS_LOCAL'
    print(json.dumps({'status': status, 'observations': observations,
                      'isolated_no_key_profile': no_key_profile, 'remote_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
