#!/usr/bin/env python3
"""Run input-isolation/scale probes on explicitly pinned production functions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_SHA = 'e7d665dd7f466e454aeca071895273e81549af169f8613c3490671a3cf8cca20'
HEADER = '''use mod.math.*
use mod.std.*
let fixture_files={} let fixture_pending=[] let fixture_timers=[] let fixture_trace=[]
let fixture_write_fail=false let fixture_write_fail_path="" let fixture_read_fail=false
let fixture_clock=1700000000 let fixture_serial=0 let fixture_stage="fixture_input"
let fixture_values={} let fixture_visibility={}
fn time_now(){return fixture_clock}
fn random_u32(){fixture_serial=fixture_serial+1 return fixture_serial}
fn fixture_write(path,data){if fixture_write_fail || path==fixture_write_fail_path{return "fixture_write_failed"} fixture_files[path]=data return nil}
fn fixture_read(path){if fixture_read_fail{return ""} let value=fixture_files[path] if value==nil{return ""} return value}
let fs={exists:|path|fixture_files[path]!=nil write:|path,value|fixture_write(path,value)
    read:|path|fixture_read(path) mkdir:|path|nil sha256:|value|mod.fixture.sha256(value)
    sha256_file:|path|{if fixture_files[path]==nil{return ""} return mod.fixture.sha256(fixture_read(path))}}
fn start_timeout(delay,callback){fixture_timers.push(callback)}
fn fixture_transport(method,args,callback){
    let payload=args.to_json().parse_json()
    fixture_trace.push({stage:fixture_stage method:method args:payload})
    fixture_pending.push({method:method payload:payload callback:callback})
}
fn fixture_widget(name){return {text:||{let value=fixture_values[name] if value==nil{return ""} return value}
    set_text:|value|{fixture_values[name]=value} render:||{} set_visible:|value|{fixture_visibility[name]=value}
    is_visible:||fixture_visibility[name]==true set_focus:||{} set_enabled:|value|{}}}
let host={capabilities:||["mail"]}
let ui={}
__UI__
'''


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--expected-sha256', default=SOURCE_SHA,
                        help='Expected source SHA-256 (default: %(default)s)')
    parser.add_argument('--runner', type=Path, required=True)
    parser.add_argument('--probe', choices=['inputs', 'scale'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.read_text()
    source_sha256 = digest(source)
    assert source_sha256 == args.expected_sha256, 'Source SHA-256 does not match --expected-sha256'
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=False)
    helper = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/tests/run_official_api.py')
    spec = importlib.util.spec_from_file_location('verified_helpers', helper)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    assert marker
    prefix = source[:marker.start()] + source[source.index('// BEGIN ACTION_CHAIN_PROJECTION'):source.index('// END ACTION_CHAIN_PROJECTION')]
    original = h.functions_in(prefix)
    replacements = {
        'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}',
        'set_page': 'fn set_page(next){page=next}', 'ac_refresh': 'fn ac_refresh(){}',
        'ui_layout_save': 'fn ui_layout_save(){}',
        'storage_write': 'fn storage_write(path,data){return fixture_write(path,data)}',
        'storage_read': 'fn storage_read(path){return fixture_read(path)}',
    }
    for name, body in replacements.items():
        prefix = h.replace_function(prefix, name, body)
    prefix = prefix.replace('host.request(', 'fixture_transport(')
    executed_functions = h.functions_in(prefix)
    changed = sorted(k for k in original if original[k] != executed_functions[k].replace('fixture_transport(', 'host.request('))
    assert changed == sorted(replacements)
    names = sorted(set(re.findall(r'\bui\.([a-zA-Z_][a-zA-Z_0-9]*)', prefix)))
    ports = '\n'.join(f'ui.{name}=fixture_widget("{name}")' for name in names)
    probe_path = HERE / (args.probe + '.splash')
    executed = HEADER.replace('__UI__', ports) + prefix + '\n' + probe_path.read_text()
    script = out / 'executed.splash'
    script.write_text(executed)
    timed_out = False
    try:
        result = subprocess.run([str(args.runner.resolve(strict=True)), str(script)], capture_output=True, text=True, timeout=120)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        timed_out = True
        stdout = error.stdout or b''
        stderr = error.stderr or b''
        stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
        stderr += '\nFixture execution exceeded 120 seconds.\n'
        code = 124
    (out / 'stdout.log').write_text(stdout)
    (out / 'stderr.log').write_text(stderr)
    data = json.loads(stdout) if code == 0 else None
    checks = data.get('checks', {}) if data else {}
    failed = [k for k, value in checks.items() if value is not True]
    report = {'kind': 'REAL_OFFICIAL_SPLASH_VM_L4_WITH_FIXTURE_INPUTS',
              'status': 'PASS' if data and checks and not failed else 'FAIL',
              'exit_code': code, 'timed_out': timed_out, 'failed': failed, 'probe': data,
              'source_sha256': source_sha256, 'expected_source_sha256': args.expected_sha256,
              'executed_sha256': digest(executed),
              'probe_sha256': digest(probe_path.read_text()),
              'runner_sha256': hashlib.sha256(args.runner.read_bytes()).hexdigest(),
              'production_function_sha256': {k: digest(v) for k, v in original.items()},
              'boundary_replacements': changed,
              'all_other_functions_byte_equal_after_transport_normalization': True,
              'actual_external_calls': 0,
              'boundary': 'No Host/Kernel/Mail/model/GUI process or network call. Input/transport/timer/UI/IO are explicit fixtures; production functions execute in the official VM.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'failed': failed,
                      'exit_code': code, 'source_sha256': source_sha256}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
