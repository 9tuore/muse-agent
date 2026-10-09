#!/usr/bin/env python3
"""Lost-review callback + independent process recovery; synthetic protocol only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time

from run_official_api import ROOT, sha, replace_function, functions_in, WIDGET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', type=Path, required=True)
    parser.add_argument('--host-cwd', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8658)
    args = parser.parse_args()
    host = args.host.resolve(strict=True)
    cwd = args.host_cwd.resolve(strict=True)
    assert not host.is_relative_to(Path('/Applications'))
    with socket.socket() as sock:
        assert sock.connect_ex(('127.0.0.1', args.port)) != 0
    output = args.out.resolve()
    assert output.is_relative_to(ROOT / 'build')
    output.mkdir(parents=True, exist_ok=False)
    source_path = ROOT / 'official_muse/app/source/main.splash'
    source = source_path.read_text()
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    assert marker
    prefix = source[:marker.start()]
    before = functions_in(prefix)
    prefix = prefix.replace('host.request(', 'restart_transport(')
    changes = {'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}', 'set_page': 'fn set_page(next){page=next}'}
    for name, replacement in changes.items():
        prefix = replace_function(prefix, name, replacement)
    after = functions_in(prefix)
    altered = [name for name in before if before[name] != after[name].replace('restart_transport(', 'host.request(')]
    assert sorted(altered) == sorted(changes)
    probe_path = Path(__file__).with_name('mail_restart.splash')
    widget = WIDGET.replace('    Label{text:', '    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n    mail_body := TextInput{width: Fill}\n    Label{text:', 1)
    widget = widget.replace('    Label{text:', '    right_content := View{width: Fill height: Fit on_render: || {}}\n    right_page_content := View{width: Fill height: Fit on_render: || {}}\n    chat_list := View{width: Fill height: Fit on_render: || {}}\n    Label{text:', 1)
    home = output / 'home'
    core = home / 'octos-home/.octos'
    core.mkdir(parents=True)
    record = {'kind': 'TWO_REAL_VM_PROCESS_RESTART_SYNTHETIC_OFFICIAL_PROTOCOL', 'status': 'ERROR',
              'source_sha256': sha(source_path), 'host_sha256': sha(host), 'probe_sha256': sha(probe_path),
              'runner_sha256': sha(Path(__file__)), 'substitutions': altered, 'all_other_functions_byte_equal': True,
              'external_service_calls': 0, 'cases': [],
              'boundary': 'Real jailed storage/process recovery, mocked Host replies. Not native review, admission, SMTP or delivery acceptance.'}

    def execute(case, state):
        folder = output / case
        folder.mkdir()
        bundle = folder / 'bundle'
        shutil.copytree(ROOT / 'bundle', bundle)
        manifest = json.loads((bundle / 'manifest.json').read_text())
        manifest['integrity'] = {}
        (bundle / 'manifest.json').write_text(json.dumps(manifest) + '\n')
        text = prefix + probe_path.read_text().replace('__CASE__', case) + widget
        assert 'host.request(' not in text
        (bundle / 'main.splash').write_text(text)
        report_path = state / 'muse-goals/restart-probe.json'
        if report_path.exists():
            report_path.unlink()  # Fixture output marker only, never business state.
        env = dict(os.environ, MAKEPAD_REMOTE=str(args.port), MAKEPAD_HIDE_WINDOWS='1',
                   OCTOSENSE_HOME=str(home), OCTOSENSE_APP_DATA=str(state), OCTOS_APP_CORE_DIR=str(core), MAKEPAD_APP_CONFIG='{}')
        env.pop('MAKEPAD_FOCUS', None)
        log = folder / 'runtime.log'
        item = {'case': case, 'status': 'ERROR', 'executed_sha256': sha(bundle / 'main.splash')}
        process = None
        try:
            with log.open('w') as stream:
                process = subprocess.Popen([str(host), '--bundle', str(bundle), '--app-data', str(state), '--allow-unsigned', '--stamp', '--size', '600x700'], cwd=cwd, env=env, stdout=stream, stderr=stream)
                item['pid'] = process.pid
                deadline = time.monotonic() + 90
                while not report_path.exists():
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('No fresh VM report; evidence retained')
                    time.sleep(.1)
                time.sleep(.2)
                data = json.loads(report_path.read_text())
                errors = [line for line in log.read_text().splitlines() if '[E]' in line or 'script time budget exceeded' in line]
                failed = [name for name, passed in data['checks'].items() if passed is not True]
                item.update(data, status='FIXTURE_PASS' if not failed and not errors else 'FAIL', failed=failed, runtime_errors=errors)
        except Exception as error:
            item['error'] = str(error)
        finally:
            if process is not None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        item['runtime_log_sha256'] = sha(log)
        record['cases'].append(item)
        print(json.dumps({key: item.get(key) for key in ['case', 'status', 'failed', 'error']}, ensure_ascii=False), flush=True)
        return item

    interrupted_state = output / 'interrupted-state'
    prepared = execute('prepare', interrupted_state)
    if prepared['status'] == 'FIXTURE_PASS':
        for case in ['accepted', 'wrong_revision', 'wrong_account', 'wrong_body', 'still_draft', 'host_error']:
            state = output / (case + '-state')
            shutil.copytree(interrupted_state, state)
            execute(case, state)
    passed = all(item['status'] == 'FIXTURE_PASS' for item in record['cases']) and len(record['cases']) == 7
    record['status'] = 'FIXTURE_PASS' if passed else 'FAIL'
    (output / 'report.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
