#!/usr/bin/env python3
"""Real VM, existing production projection; synthetic data, no external calls."""
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
sys.path.insert(0, str(ROOT / 'official_muse/semifinal/tests'))
from run_official_api import functions_in, replace_function, WIDGET, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', type=Path, required=True)
    p.add_argument('--host-cwd', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8658)
    a = p.parse_args()
    host = a.host.resolve(strict=True)
    out = a.out.resolve()
    assert out.is_relative_to(ROOT / 'build')
    with socket.socket() as sock:
        assert sock.connect_ex(('127.0.0.1', a.port)) != 0
    out.mkdir(parents=True, exist_ok=False)
    source_path = ROOT / 'official_muse/app/source/main.splash'
    source = source_path.read_text()
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    assert marker
    # Projection helpers live after the widget styles; move only these helpers
    # into the prefix so the same functions run without the full UI harness.
    block = source[source.index('// BEGIN ACTION_CHAIN_PROJECTION'):source.index('// END ACTION_CHAIN_PROJECTION')]
    prefix = source[:marker.start()] + block
    before = functions_in(prefix)
    prefix = prefix.replace('host.request(', 'ac_fixture_transport(')
    replacements = {'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}', 'set_page': 'fn set_page(next){page=next}'}
    for key, value in replacements.items():
        prefix = replace_function(prefix, key, value)
    after = functions_in(prefix)
    altered = [name for name in before if before[name] != after[name].replace('ac_fixture_transport(', 'host.request(')]
    assert sorted(altered) == sorted(replacements)
    bundle = out / 'bundle'
    shutil.copytree(ROOT / 'bundle', bundle)
    m = json.loads((bundle / 'manifest.json').read_text()); m['integrity'] = {}
    (bundle / 'manifest.json').write_text(json.dumps(m) + '\n')
    probe = Path(__file__).with_name('projection.splash')
    (bundle / 'main.splash').write_text(prefix + probe.read_text() + WIDGET)
    state = out / 'state'; home = out / 'home'; core = home / 'octos-home/.octos'; core.mkdir(parents=True)
    env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_HIDE_WINDOWS='1', OCTOSENSE_HOME=str(home),
               OCTOSENSE_APP_DATA=str(state), OCTOS_APP_CORE_DIR=str(core), MAKEPAD_APP_CONFIG='{}')
    env.pop('MAKEPAD_FOCUS', None)
    result = {'kind': 'REAL_REFERENCE_VM_PROJECTION_FIXTURE', 'status': 'ERROR', 'source_sha256': sha(source_path),
              'host_sha256': sha(host), 'executed_sha256': sha(bundle / 'main.splash'), 'probe_sha256': sha(probe),
              'substitutions': altered, 'all_other_functions_byte_equal': True, 'external_calls': 0,
              'boundary': 'Synthetic projection states; not real Mail/Calendar/model execution or visible UI acceptance.'}
    log = out / 'runtime.log'
    proc = None
    try:
        with log.open('w') as stream:
            proc = subprocess.Popen([str(host), '--bundle', str(bundle), '--app-data', str(state), '--allow-unsigned', '--stamp', '--size', '600x700'], cwd=a.host_cwd.resolve(strict=True), env=env, stdout=stream, stderr=stream)
            output = state / 'muse-goals/ac-probe.json'
            deadline = time.monotonic() + 90
            while not output.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('No fresh VM result; failure retained')
                time.sleep(.1)
            time.sleep(.2)
            data = json.loads(output.read_text())
            errors = [line for line in log.read_text().splitlines() if '[E]' in line or 'script time budget exceeded' in line]
            failed = [key for key, value in data['checks'].items() if value is not True]
            result.update(data, status='FIXTURE_PASS' if not errors and not failed else 'FAIL', failed=failed, runtime_errors=errors)
    except Exception as error:
        result['error'] = str(error)
    finally:
        if proc is not None:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()
    result['runtime_log_sha256'] = sha(log)
    result['runtime_errors'] = [line for line in log.read_text().splitlines() if '[E]' in line or 'script time budget exceeded' in line]
    (out / 'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result.get(k) for k in ('status', 'failed', 'error', 'runtime_errors')}, ensure_ascii=False))
    return 0 if result['status'] == 'FIXTURE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
