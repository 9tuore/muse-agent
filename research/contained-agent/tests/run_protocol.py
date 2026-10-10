#!/usr/bin/env python3
"""Execute isolated prototype logic in a reference VM with synthetic Octos replies.

Agent admission is removed only in the instrumented fixture copy. Native
consent, official Agent/model execution and real tool results remain untested.
"""
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
from runtime_probe import replace_function


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=Path, required=True)
    parser.add_argument('--host-cwd', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8658)
    args = parser.parse_args()
    with socket.socket() as sock:
        assert sock.connect_ex(('127.0.0.1', args.port)) != 0
    output = args.out.resolve()
    assert output.is_relative_to(ROOT / 'build')
    output.mkdir(parents=True, exist_ok=False)
    prototype = Path(__file__).resolve().parents[1] / 'bundle'
    source = (prototype / 'main.splash').read_text()
    marker = 'start_timeout(0.05,|| agent_restore())'
    assert source.count(marker) == 1
    prefix = source.split(marker)[0].replace('host.request(', 'probe_request(')
    prefix = replace_function(prefix, 'agent_render', 'fn agent_render(){}')
    bundle = output / 'bundle'
    shutil.copytree(prototype, bundle)
    manifest = json.loads((bundle / 'manifest.json').read_text())
    manifest.update(agent=None, capabilities=['storage'], integrity={})
    (bundle / 'manifest.json').write_text(json.dumps(manifest) + '\n')
    probe = Path(__file__).with_name('protocol.splash')
    widget = 'View{width:Fill height:Fill flow:Down agent_input := TextInput{width:Fill} Label{text:"Muse 官方Agent协议合成检查"}}\n'
    (bundle / 'main.splash').write_text(prefix + probe.read_text() + widget)
    host = args.host.resolve(strict=True)
    state = output / 'state'
    env = dict(os.environ, MAKEPAD_REMOTE=str(args.port), MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    report = {'status': 'ERROR', 'scope': 'FIXTURE_ONLY; no native Agent admission, model, tool or consent',
              'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'host_sha256': hashlib.sha256(host.read_bytes()).hexdigest(),
              'substitutions': ['Host transport', 'agent_render', 'root widgets', 'fixture manifest agent/capabilities']}
    log_path = output / 'runtime.log'
    with log_path.open('w') as log:
        process = subprocess.Popen([str(host), '--bundle', str(bundle), '--app-data', str(state),
                                    '--allow-unsigned', '--stamp', '--size', '600x700'],
                                   cwd=args.host_cwd.resolve(strict=True), env=env, stdout=log, stderr=log)
        try:
            result = state / 'muse-goals/probe.json'
            deadline = time.monotonic() + 60
            while not result.is_file():
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('No report; original log/state retained')
                time.sleep(.1)
            data = json.loads(result.read_text())
            errors = [s for s in log_path.read_text().splitlines() if '[E]' in s or 'budget exceeded' in s]
            failed = [k for k, v in data['checks'].items() if v is not True]
            if errors:
                failed.append('runtime_errors')
            report.update(status='FIXTURE_PASS' if not failed else 'FAIL', failed=failed, data=data, runtime_errors=errors)
        except Exception as error:
            report['error'] = str(error)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:report.get(k) for k in ('status', 'failed', 'error')}, ensure_ascii=False))
    return 0 if report['status'] == 'FIXTURE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
