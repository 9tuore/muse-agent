#!/usr/bin/env python3
"""Real Splash VM + jailed persistence; synthetic official protocol, zero external calls."""
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
from runtime_probe import replace_function, WIDGET
sys.path.insert(0, str(ROOT / 'official_muse/prelim/tests/calendar_sync'))
from run import functions_in


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', type=Path, required=True)
    p.add_argument('--host-cwd', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8658)
    p.add_argument('--source', type=Path, help='Explicit frozen research source; default is production readable source')
    p.add_argument('--suite', choices=['production', 'device-research', 'calendar-restore'], default='production')
    a = p.parse_args()
    host = a.host.resolve(strict=True)
    assert not host.is_relative_to(Path('/Applications'))
    out = a.out.resolve()
    assert out.is_relative_to(ROOT / 'build')
    with socket.socket() as s:
        assert s.connect_ex(('127.0.0.1', a.port)) != 0
    out.mkdir(parents=True, exist_ok=False)
    bundle = out / 'bundle'
    shutil.copytree(ROOT / 'bundle', bundle)
    manifest = json.loads((bundle / 'manifest.json').read_text())
    manifest['integrity'] = {}
    (bundle / 'manifest.json').write_text(json.dumps(manifest) + '\n')
    source_path = (a.source or ROOT / 'official_muse/app/source/main.splash').resolve(strict=True)
    source = source_path.read_text()
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    assert marker
    prefix = source[:marker.start()]
    before = functions_in(prefix)
    prefix = prefix.replace('host.request(', 'probe_transport(')
    replacements = {
        'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}',
        'set_page': 'fn set_page(next){page=next}',
    }
    if a.suite == 'device-research':
        replacements['calendar_enabled'] = 'fn calendar_enabled(){return true}'
    if a.suite == 'calendar-restore':
        # Independent inbox startup is covered by Mail tests. Keep actual boot
        # result recovery and chat binding; this fixture sends no Host request.
        replacements['mail_watch_boot'] = 'fn mail_watch_boot(){}'
    for name, body in replacements.items():
        prefix = replace_function(prefix, name, body)
    after = functions_in(prefix)
    changed = [n for n in before if before[n] != after[n].replace('probe_transport(', 'host.request(')]
    assert sorted(changed) == sorted(replacements)
    probe = Path(__file__).with_name('calendar_restore.splash' if a.suite == 'calendar-restore' else 'official_api.splash')
    widget = WIDGET.replace('    Label{text:', '''    mail_to := TextInput{width: Fill}
    mail_subject := TextInput{width: Fill}
    mail_body := TextInput{width: Fill}
    Label{text:''', 1)
    instrumented = prefix + probe.read_text().replace('__SUITE__', a.suite) + widget
    assert 'host.request(' not in instrumented
    (bundle / 'main.splash').write_text(instrumented)
    state = out / 'state'
    home = out / 'home'
    core = home / 'octos-home/.octos'
    core.mkdir(parents=True)
    env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_HIDE_WINDOWS='1',
               OCTOSENSE_HOME=str(home), OCTOSENSE_APP_DATA=str(state),
               OCTOS_APP_CORE_DIR=str(core), MAKEPAD_APP_CONFIG='{}')
    env.pop('MAKEPAD_FOCUS', None)
    report = {'kind': 'OFFICIAL_PROTOCOL_FIXTURE_REAL_SPLASH_VM', 'status': 'ERROR', 'suite': a.suite,
              'source_sha256': sha(source_path), 'host_sha256': sha(host),
              'runner_sha256': sha(Path(__file__)), 'probe_sha256': sha(probe),
              'executed_sha256': sha(bundle / 'main.splash'), 'substitutions': changed,
              'all_other_functions_byte_equal': True, 'external_service_calls': 0,
              'boundary': 'Old reference VM validates Muse logic and persistence. Synthetic protocol responses do not prove new official Host admission, native consent, EventKit or SMTP.'}
    log = out / 'runtime.log'
    proc = None
    try:
        with log.open('w') as f:
            proc = subprocess.Popen([str(host), '--bundle', str(bundle), '--app-data', str(state),
                                     '--allow-unsigned', '--stamp', '--size', '600x700'],
                                    cwd=a.host_cwd.resolve(strict=True), env=env, stdout=f, stderr=f)
            result = state / 'muse-goals/probe.json'
            deadline = time.monotonic() + 90
            while not result.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('No fresh VM report; failed log/state retained')
                time.sleep(.1)
            time.sleep(.2)
            data = json.loads(result.read_text())
            failed = [n for n, value in data['checks'].items() if value is not True]
            errors = [line for line in log.read_text().splitlines() if '[E]' in line or 'script time budget exceeded' in line]
            if errors:
                failed.append('runtime_errors')
            report.update(status='FIXTURE_PASS' if not failed else 'FAIL',
                          failed=failed, checks=data['checks'], calls=data['calls'], observations=data.get('observations', {}), runtime_errors=errors)
    except Exception as e:
        report['error'] = str(e)
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    report['runtime_log_sha256'] = sha(log)
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report.get(k) for k in ['status', 'failed', 'error']}, ensure_ascii=False))
    return 0 if report['status'] == 'FIXTURE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
