#!/usr/bin/env python3
"""Frozen production mail module in real card-host/storage; synthetic Host only."""
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
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
import runtime_probe as runtime


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--module', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--suite', type=Path, default=Path(__file__).with_name('mail_stability.splash'))
    p.add_argument('--port', type=int, default=8485)
    p.add_argument('--timeout', type=float, default=50)
    a = p.parse_args()
    with socket.socket() as s:
        if s.connect_ex(('127.0.0.1', a.port)) == 0:
            raise RuntimeError('Port occupied; existing process untouched')
    a.out = a.out.resolve()
    a.out.mkdir(parents=True, exist_ok=False)
    baseline = ROOT / 'official_muse/app/build/prelim-mail-b02d103/source-bundle'
    source = (baseline / 'main.splash').read_text()
    start = source.index('// Inbox polling')
    end = source.index('fn mail_redraw(', start)
    module = a.module.read_text()
    source = source[:start] + module + '\n' + source[end:]
    prefix = source[:source.index('start_timeout(0.05, || boot())')]
    transport = 'incoming_fixture_request' if a.suite.name != 'mail_stability.splash' else 'mail_fixture_request'
    prefix = prefix.replace('host.request(', transport + '(')
    for name, definition in [
        ('redraw', 'fn redraw(){}'), ('set_page', 'fn set_page(next){page = next}'),
        ('mail_enabled', 'fn mail_enabled(){return true}'),
        ('mail_watch_refresh', 'fn mail_watch_refresh(){}'),
        ('mail_redraw', 'fn mail_redraw(){mail_watch_draft_status()}'),
        ('muse_notify', 'fn muse_notify(kind){}')]:
        prefix = runtime.replace_function(prefix, name, definition)
    bundle, state = a.out / 'bundle', a.out / 'state'
    shutil.copytree(baseline, bundle)
    widget = runtime.WIDGET.replace('    Label{text:', '    mail_to := TextInput{width: Fill}\n'
        '    mail_subject := TextInput{width: Fill}\n    mail_body := TextInput{width: Fill}\n'
        '    mail_intent := TextInput{width: Fill}\n    Label{text:', 1)
    (bundle / 'main.splash').write_text(prefix + runtime.TRANSPORT + a.suite.read_text() + widget)
    (a.out / 'module.splash').write_text(module)
    env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    with (a.out / 'runtime.log').open('w') as log:
        proc = subprocess.Popen([str(runtime.HOST), '--bundle', str(bundle), '--app-data', str(state),
            '--allow-unsigned', '--stamp', '--size', '600x700'], env=env,
            cwd=runtime.HOST.parents[2], stdout=log, stderr=log)
        try:
            report = state / 'muse-goals/probe.json'
            deadline = time.monotonic() + a.timeout
            while not report.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('No report; original runtime log retained')
                time.sleep(.2)
            result = json.loads(report.read_text())
            checks = {k: v for k, v in result.items() if isinstance(v, bool)}
            failed = [k for k, v in checks.items() if not v]
            result.update(kind='FIXTURE_PRODUCTION_MAIL_REAL_STORAGE', passed=len(checks)-len(failed),
                failed=failed, module_sha256=hashlib.sha256(module.encode()).hexdigest(),
                baseline_commit='b02d103', suite_sha256=hashlib.sha256(a.suite.read_bytes()).hexdigest(),
                host_sha256=hashlib.sha256(runtime.HOST.read_bytes()).hexdigest(),
                real_mail=False, real_calendar=False, real_model=False)
            (a.out / 'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps({k: result[k] for k in ['passed', 'failed', 'module_sha256']}, ensure_ascii=False))
            return int(bool(failed))
        finally:
            try: urlopen(f'http://127.0.0.1:{a.port}/quit', timeout=2).read()
            except OSError: proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()


if __name__ == '__main__':
    raise SystemExit(main())
