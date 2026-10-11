#!/usr/bin/env python3
"""Run frozen production Splash functions in the official windowless VM."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HELPERS = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/tests/run_official_api.py')
sys.dont_write_bytecode = True

HEADER = '''use mod.math.*
use mod.std.*
let fixture_files = {}
let fixture_write_fail = false
let fixture_write_fail_path = ""
let fixture_read_fail = false
let fixture_pending = []
fn fixture_write(path,data){if fixture_write_fail || path==fixture_write_fail_path{return "fixture_write_failed"} fixture_files[path]=data return nil}
fn fixture_read(path){if fixture_read_fail{return ""} let value=fixture_files[path] if value==nil{return ""} return value}
fn fixture_transport(method,payload,callback){fixture_pending.push({method:method payload:payload callback:callback})}
'''


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--runner', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--probe', type=Path, default=HERE / 'probe.splash')
    args = parser.parse_args()
    source = args.source.read_text()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('verified_vm_helpers', HELPERS)
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    assert marker
    prefix = source[:marker.start()] + source[source.index('// BEGIN ACTION_CHAIN_PROJECTION'):source.index('// END ACTION_CHAIN_PROJECTION')]
    original = helpers.functions_in(prefix)
    replacements = {
        'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}',
        'set_page': 'fn set_page(next){page=next}', 'ac_refresh': 'fn ac_refresh(){}',
        'ui_layout_save': 'fn ui_layout_save(){}',
        'storage_write': 'fn storage_write(path,data){return fixture_write(path,data)}',
        'storage_read': 'fn storage_read(path){return fixture_read(path)}',
    }
    for name, body in replacements.items():
        prefix = helpers.replace_function(prefix, name, body)
    prefix = prefix.replace('host.request(', 'fixture_transport(')
    executed = helpers.functions_in(prefix)
    changed = sorted(name for name in original if original[name] != executed[name].replace('fixture_transport(', 'host.request('))
    assert changed == sorted(replacements)
    prepared = HEADER + prefix + '\n' + args.probe.read_text()
    path = out / 'executed.splash'
    path.write_text(prepared)
    result = subprocess.run([str(args.runner.resolve(strict=True)), str(path)],
                            capture_output=True, text=True, timeout=60)
    (out / 'stdout.log').write_text(result.stdout)
    (out / 'stderr.log').write_text(result.stderr)
    data = json.loads(result.stdout) if result.returncode == 0 else None
    failed = [name for name, value in data['checks'].items() if value is not True] if data else []
    report = {'kind': 'OFFICIAL_SPLASH_VM_WITH_MOCK_BOUNDARIES',
              'status': 'PASS' if result.returncode == 0 and not failed else 'FAIL',
              'exit_code': result.returncode, 'failed': failed, 'probe': data,
              'source_sha256': digest(source), 'executed_sha256': digest(prepared),
              'runner_sha256': hashlib.sha256(args.runner.read_bytes()).hexdigest(),
              'boundary_replacements': changed,
              'production_function_sha256': {name: digest(body) for name, body in original.items()},
              'all_other_functions_byte_equal_after_transport_normalization': True,
              'boundary': 'No window/Host/EventKit/Mail/model invocation. Clock, storage and transport are synthetic; not a full-chain or GUI PASS.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({key: report[key] for key in ('status', 'exit_code', 'failed')}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
