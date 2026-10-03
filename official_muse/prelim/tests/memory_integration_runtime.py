#!/usr/bin/env python3
"""Frozen full-main functions; real card-host storage, explicitly mocked transport/widgets."""
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
from runtime_probe import HOST, WIDGET, replace_function

TRANSPORT = '''
let integration_calls = [] let integration_queue = [] let integration_account_queue = []
let integration_defer_accounts = false let integration_forbidden = []
fn integration_request(service,payload,callback){
    integration_calls.push({service: service payload: payload})
    if service == "model.complete" { integration_queue.push(callback) return }
    if service == "mail.accounts" {
        if integration_defer_accounts { integration_account_queue.push(callback) return }
        callback({is_ok: true data: []}) return
    }
    integration_forbidden.push(service)
    callback({is_ok: false error: "fixture: forbidden external service"})
}
'''


def run(source_path, output, probe):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', 8482)) == 0:
            raise RuntimeError('8482 already owned; existing process untouched')
    source = source_path.read_text()
    prefix = source[:source.index('start_timeout(0.05, || boot())')]
    prefix = prefix.replace('host.request(', 'integration_request(')
    for name, replacement in [
            ('redraw', 'fn redraw(){}'), ('set_page', 'fn set_page(next){ page = next }'),
            ('mail_redraw', 'fn mail_redraw(){}'), ('mail_enabled', 'fn mail_enabled(){ return true }')]:
        prefix = replace_function(prefix, name, replacement)
    widget = WIDGET.replace('    Label{text:',
        '    session_focus_project := TextInput{width: Fill}\n'
        '    session_focus_owner := TextInput{width: Fill}\n    Label{text:', 1)
    probe_path = Path(__file__).with_name(probe + '.splash')
    bundle, state = output / 'bundle', output / 'state'
    shutil.copytree(ROOT / 'official_muse/app/bundle', bundle)
    instrumented = prefix + TRANSPORT + probe_path.read_text() + widget
    assert 'host.request(' not in instrumented
    (bundle / 'main.splash').write_text(instrumented)
    env = dict(os.environ, MAKEPAD_REMOTE='8482', MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    log_path = output / 'runtime.log'
    with log_path.open('w') as log:
        proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(state),
                                 '--allow-unsigned', '--stamp', '--size', '600x700'],
                                env=env, cwd=HOST.parents[2], stdout=log, stderr=log)
        try:
            report = state / 'muse-goals/probe.json'
            deadline = time.monotonic() + 25
            while not report.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(log_path.read_text()[-8000:])
                time.sleep(.1)
            time.sleep(.1)
            result = json.loads(report.read_text())
            result.update(main_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                          instrumented_sha256=hashlib.sha256(instrumented.encode()).hexdigest(),
                          probe_sha256=hashlib.sha256(probe_path.read_bytes()).hexdigest(),
                          host_sha256=hashlib.sha256(HOST.read_bytes()).hexdigest(),
                          scope='FULL_MAIN_FUNCTIONS/FIXTURE: mocked Host transport and render; actual card-host isolated storage; no model or external services')
            checks = {key: value for key, value in result.items() if isinstance(value, bool)}
            result.update(passed=sum(checks.values()), failed=[key for key, value in checks.items() if not value])
            (output / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            if '[E]' in log_path.read_text():
                raise RuntimeError(log_path.read_text()[-8000:])
            print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
            return result
        finally:
            try:
                urlopen('http://127.0.0.1:8482/quit', timeout=2).read()
            except OSError:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--probe', required=True)
    args = parser.parse_args()
    result = run(args.source, args.output.resolve(), args.probe)
    raise SystemExit(1 if result['failed'] else 0)
