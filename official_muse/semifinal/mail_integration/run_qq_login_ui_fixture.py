#!/usr/bin/env python3
"""Prepare/run isolated QQ sheet fixture; no real Host transport or credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
BASE_SHA = '5b9bbd082d7df01b9068bf1c830c30ff4f3d35ba31f182a387bea071fb2fc50e'
PATCH_SHA = '0415463dc87bba93b8867d1476f12260ac366eaf7be9a2c9380640d8437d5b25'
CANDIDATE_SHA = '724c7d7faee03d1303b8caf20b33e6958f385a03f01bf29a92a704a477fcbf7c'
TRANSPORT = '''// Synthetic Host only: never dispatch to a service or vault.
fn qq_fixture_request(method,args,cb){
    if method == "mail.sheet.cancel" { cb({is_ok: true}) return }
    if method != "mail.sheet.submit" { cb({is_ok: false error: "Unexpected fixture method"}) return }
    let checks = {
        address_trimmed: args.address == "muse-fixture@example.invalid"
        username_full_address_trimmed: args.username == "muse-fixture@example.invalid"
        password_left_empty_in_contained_fixture: args.password == ""
        manual_host_preserved_at_submit: args.host == "imap.fixture.invalid"
        manual_port_preserved_at_submit: args.port == "1993"
        final_protocol_imap: args.protocol == "imap"
        smtp_default: args.smtp_host == "smtp.qq.com" && args.smtp_port == "465"
        tls_unchanged: args.security == "tls" && args.smtp_security == "tls"
    }
    // Record booleans only; never serialize the form or authorization-code value.
    fs.write("qq-login-submit.json",{checks: checks transport: "synthetic_only"}.to_json())
    cb({is_ok: true})
}
'''

def sha(data):
    return hashlib.sha256(data).hexdigest()


def candidate(source, patch):
    if sha(source.encode()) == CANDIDATE_SHA:
        return source
    assert sha(source.encode()) == BASE_SHA, 'Source identity differs; regenerate harness identity'
    assert sha(patch.encode()) == PATCH_SHA, 'Patch identity differs'
    lines = source.splitlines(True)
    output = []
    pos = 0
    for line in patch.splitlines(True)[2:]:
        if line.startswith('@@'):
            target = int(re.match(r'@@ -(\d+)', line).group(1)) - 1
            output.extend(lines[pos:target]); pos = target
        elif line.startswith(' '):
            assert lines[pos] == line[1:]; output.append(lines[pos]); pos += 1
        elif line.startswith('-'):
            assert lines[pos] == line[1:]; pos += 1
        elif line.startswith('+'):
            output.append(line[1:])
    output.extend(lines[pos:])
    result = ''.join(output)
    assert sha(result.encode()) == CANDIDATE_SHA
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', type=Path, default=ROOT/'build/runtime-closure-full-shell-r1/sdk/apps/mail/host-service/src/lib.rs')
    parser.add_argument('--out', type=Path, required=True, help='Fresh directory under project build/')
    parser.add_argument('--host', type=Path, help='Explicit isolated reference/card-host binary; omit to prepare only')
    parser.add_argument('--host-sha256', help='Required identity when running')
    parser.add_argument('--host-cwd', type=Path)
    parser.add_argument('--port', type=int, default=8693)
    parser.add_argument('--size', default='412x1000', help='Reference viewport WIDTHxHEIGHT')
    a = parser.parse_args()
    dimensions = re.fullmatch(r'([1-9][0-9]*)x([1-9][0-9]*)', a.size)
    assert dimensions, 'Use positive WIDTHxHEIGHT'
    width, height = map(int, dimensions.groups())
    source = a.lib.read_text()
    patched = candidate(source, (OWN/'qq-login-ui-review.patch').read_text())
    block = patched.split('fn signin_sheet() -> String {', 1)[1].split('\n#[cfg(test)]', 1)[0]
    sheet = block.split('r##"', 1)[1].split('"##', 1)[0]
    assert 'ui.username' not in sheet and 'ui.login' not in sheet and 'username :=' not in sheet
    assert 'password := Field{empty_text: "请输入邮箱授权码" is_password: true}' in sheet
    assert sheet.count('host.request(') == 2
    executed = TRANSPORT + sheet.replace('host.request(', 'qq_fixture_request(')
    assert 'host.request(' not in executed
    out = a.out.resolve()
    assert out.is_relative_to(ROOT/'build') and not out.exists()
    out.mkdir(parents=True)
    bundle = out/'bundle'; bundle.mkdir()
    # Existing manifest schema, restricted synthetic identity and storage only.
    manifest = json.loads((ROOT/'bundle/manifest.json').read_text())
    manifest.update(id='qq-login-ui-fixture', name='QQ Login Synthetic Fixture', agent=None,
                    capabilities=['storage'], network={'hosts': []}, integrity={})
    (bundle/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False)+'\n')
    (bundle/'main.splash').write_text(executed)
    report = dict(status='PREPARED_NOT_EXECUTED', source_sha256=sha(source.encode()),
                  candidate_sha256=sha(patched.encode()), patch_sha256=PATCH_SHA,
                  executed_sha256=sha(executed.encode()), host_transport='synthetic_only',
                  real_login=False, person_consent_tested=False, checks={'password_mask_retained_static': True},
                  password_runtime_mask='NOT_TESTED_HOST_SHEET_REQUIRED',
                  size=a.size, screenshots=[], scroll_events=[],
                  boundary='Reference system-sheet fixture only; no Shell admission, Vault, account, SMTP or trusted Person evidence')
    def save():
        (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    save()
    if a.host is None:
        print(json.dumps(report, ensure_ascii=False)); return 0
    assert a.host_cwd and a.host_sha256, 'Provide verified binary cwd and SHA'
    host = a.host.resolve(strict=True)
    assert not host.is_relative_to(Path('/Applications'))
    assert sha(host.read_bytes()) == a.host_sha256
    with socket.socket() as s:
        assert s.connect_ex(('127.0.0.1', a.port)) != 0, 'Remote port occupied'
    sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
    from remote import Remote
    remote = Remote(a.port)
    state = out/'state'; home = out/'home'; core = home/'octos-home/.octos'; core.mkdir(parents=True)
    env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_FOCUS='1',
               OCTOSENSE_HOME=str(home), OCTOSENSE_APP_DATA=str(state),
               OCTOS_APP_CORE_DIR=str(core), MAKEPAD_APP_CONFIG='{}')
    env.pop('MAKEPAD_HIDE_WINDOWS', None)
    report.update(status='ERROR', host_sha256=a.host_sha256, input_path='Remote click + key press + TextInput event')
    proc = None
    try:
        with (out/'runtime.log').open('w') as log:
            # Ordinary contained reference; never relax secret-input policy.
            proc = subprocess.Popen([str(host), '--bundle', str(bundle), '--app-data', str(state),
                                     '--allow-unsigned', '--stamp', '--size', a.size], cwd=a.host_cwd.resolve(strict=True),
                                    env=env, stdout=log, stderr=log)
            report['pid'] = proc.pid
        deadline = time.monotonic()+30
        while True:
            try:
                remote.widgets(); break
            except (OSError, ValueError):
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('Remote did not become ready; log retained')
                time.sleep(.1)
        remote.wait_for('address', 10)
        checks = report['checks']
        def screenshot(name):
            path = out/name
            remote.shot(path)
            report['screenshots'].append({'path': name, 'sha256': sha(path.read_bytes())})
        def visible(key):
            # Original ScrollYView has no id; scroll at viewport center.
            # At most 12 scroll calls in each direction per target.
            counts = {-1: 0, 1: 0}
            direction = 1
            for _ in range(25):
                try:
                    widget = remote.find(key)
                except AssertionError:
                    widget = None
                if widget is not None:
                    x, y, w, h = widget['r']
                    assert w > 2 and h > 2, 'Widget has no usable geometry: '+key
                    assert x >= 0 and x+w <= width, 'Horizontal clipping: '+key
                    if y >= 0 and y+h <= height:
                        return widget
                    direction = -1 if y < 0 else 1
                if counts[direction] >= 12:
                    direction = -direction
                if counts[direction] >= 12:
                    break
                remote.scroll(width//2, height//2, direction*80)
                counts[direction] += 1
                report['scroll_events'].append({'target': key, 'dy': direction*80})
                time.sleep(.1)
            raise AssertionError('Widget not fully visible after bounded scrolling: '+key)
        def click(key):
            visible(key)
            remote.click(key)
        def value(key):
            return visible(key).get('val')
        def require(key, expected):
            visible(key)
            remote._wait_value(key, expected)
        screenshot('01-initial-form.png')
        def type_value(key, text):
            widget = visible(key)
            x, y, w, h = widget['r']
            remote.request('/click', x=int(x+w/2), y=int(y+h/2))
            remote.request('/k', k='press', c='End')
            for _ in widget.get('val', ''):
                remote.request('/k', k='press', c='Backspace')
            require(key, '')
            if text:
                remote.request('/t', t=text)
            require(key, text)
            time.sleep(.2)  # Allow queued on_change handler before protocol click.
        assert value('address') == '' and value('password') == '', 'Not a fresh synthetic form'
        checks['no_username_widget'] = not any(w.get('i') in ('username', 'login') for w in remote.widgets())
        checks['qq_defaults'] = value('pop_host') == 'imap.qq.com' and value('pop_port') == '993' and value('smtp_host') == 'smtp.qq.com' and value('smtp_port') == '465'
        click('POP3：仅收件箱'); require('pop_host', 'pop.qq.com'); require('pop_port', '995')
        checks['pop_defaults'] = True
        click('IMAP：全部文件夹'); require('pop_host', 'imap.qq.com'); require('pop_port', '993')
        checks['imap_defaults_restored'] = True
        type_value('pop_host', 'imap.fixture.invalid'); type_value('pop_port', '1993')
        click('POP3：仅收件箱'); require('pop_host', 'imap.fixture.invalid'); require('pop_port', '1993')
        click('IMAP：全部文件夹'); require('pop_host', 'imap.fixture.invalid'); require('pop_port', '1993')
        checks['manual_inputs_preserved_remote_events'] = True
        type_value('address', '  muse-fixture@example.invalid  ')
        # Official contained TextInput refuses secrets; leave code empty.
        # Retained is_password is static evidence, not runtime masking evidence.
        visible('连接账号')
        screenshot('02-before-submit.png')
        click('连接账号')
        result = state/'qq-login-ui-fixture/qq-login-submit.json'
        deadline = time.monotonic()+10
        while not result.exists():
            if proc.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError('No synthetic submission report')
            time.sleep(.1)
        data = json.loads(result.read_text()); assert data['transport'] == 'synthetic_only'
        checks.update(data['checks'])
        remote.wait_for('已连接', 5)
        screenshot('03-after-submit.png')
        report['failed'] = [key for key, val in checks.items() if val is not True]
        report['status'] = 'CHECKS_READY' if not report['failed'] else 'FAIL'
    except Exception as error:
        report.update(status='ERROR', error=str(error))
        report.setdefault('failed', []).append('execution_error')
    finally:
        if proc is not None:
            report['shutdown'] = 'remote_quit'
            if proc.poll() is not None:
                report['shutdown'] = 'exited_before_quit'
            else:
                try:
                    remote.request('/quit')
                except OSError as error:
                    report['shutdown'] = 'terminate'
                    report['shutdown_error'] = str(error)
                    if proc.poll() is None:
                        proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                report['shutdown'] = 'kill'
                proc.kill()
                proc.wait()
            report['exit'] = proc.returncode
            report['unclean_exit'] = proc.returncode != 0 or report['shutdown'] != 'remote_quit'
            # Final scan after exit includes late Script errors during shutdown.
            log_path = out/'runtime.log'
            errors = [line for line in log_path.read_text().splitlines()
                      if '[E]' in line or 'script time budget exceeded' in line]
            report.update(runtime_errors=errors, runtime_log_sha256=sha(log_path.read_bytes()))
            failed = report.setdefault('failed', [])
            if errors: failed.append('runtime_errors')
            if report['unclean_exit']: failed.append('unclean_exit')
            if failed:
                report['status'] = 'FAIL'
            elif report['status'] == 'CHECKS_READY':
                report['status'] = 'FIXTURE_PASS'
        save()
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report['status'] == 'FIXTURE_PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
