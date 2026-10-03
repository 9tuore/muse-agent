#!/usr/bin/env python3
"""Inspect the actual Host login sheet; never type or submit credentials."""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'phase2/tests'))
from remote import Remote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8494)
    args = parser.parse_args()
    remote = Remote(args.port)
    deadline = time.monotonic() + 60
    while True:
        try:
            remote.find('Add account')
            break
        except (OSError, AssertionError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.2)
    remote.click('Add account')
    remote.wait_for('address', 30)
    time.sleep(0.5)
    widgets = remote.widgets()
    assert not any(w.get('i') == 'username' or w.get('t') == '用户名' for w in widgets)
    assert remote.find('address').get('val') == ''
    assert remote.find('password').get('val') == ''
    remote.find('密码或授权码')
    remote.find('登录')
    remote.find('取消')
    remote.shot(HERE / 'login-imap.png')
    imap = {'host': remote.find('pop_host')['val'], 'port': remote.find('pop_port')['val']}
    assert imap == {'host': 'imap.gmail.com', 'port': '993'}
    remote.click('pop_off')
    time.sleep(0.3)
    pop3 = {'host': remote.find('pop_host')['val'], 'port': remote.find('pop_port')['val']}
    assert pop3 == {'host': 'pop.gmail.com', 'port': '995'}
    assert remote.find('smtp_host')['val'] == 'smtp.gmail.com'
    assert remote.find('smtp_port')['val'] == '465'
    remote.shot(HERE / 'login-pop3.png')
    report = {'evidence': 'LIVE packaged Release Host sheet, mail_demo no network/keychain',
              'port': args.port, 'username_widget_absent': True, 'credential_fields_blank': True,
              'password_or_auth_code_caption': True, 'protocol_switch': {'imap': imap, 'pop3': pop3},
              'credentials_typed': False, 'signin_submitted': False, 'real_account_login': 'WAITING_USER'}
    (HERE / 'login_ui_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
    remote.click('取消')
    remote.request('/quit')


if __name__ == '__main__':
    main()
