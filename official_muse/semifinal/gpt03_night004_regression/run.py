#!/usr/bin/env python3
"""Run existing Splash regressions on one frozen source without launching a Host."""
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
CENTRAL = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
SOURCE_SHA = 'd065ad15ebeef1e67d69ef4e3c722f2b76cf03e7a0ab325fc2b29073b10dfba5'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('verified_helpers', CENTRAL / 'official_muse/semifinal/tests/run_official_api.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

CASES = {
    'goal_bounds': ('official_muse/prelim/tests/goal_byte_bounds.splash', 'probe.json', ''),
    'memory': ('official_muse/prelim/tests/memory_regression_suite.splash', 'memory_regression_suite-report.json', ''),
    'memory_restart': ('official_muse/prelim/tests/memory_regression_restart.splash', 'memory_regression_restart-report.json', ''),
    'mail': ('official_muse/semifinal/tests/official_api.splash', 'probe.json', 'probe_transport'),
    'mail_receipts': ('official_muse/semifinal/mail_integration/gpt02_recovery/host_receipt_status_probe.splash', 'probe.json', 'probe_transport'),
    'calendar_restore': ('official_muse/semifinal/tests/calendar_restore.splash', 'probe.json', 'probe_transport'),
    'action_chain': ('official_muse/action_chain/tests/projection.splash', 'ac-probe.json', 'ac_fixture_transport'),
}

HEADER = '''use mod.math.*
use mod.std.*
let fixture_files = __FILES__.parse_json()
let fixture_timers = [] let fixture_tick = 0 let fixture_serial = 0
let fixture_ui_values = {} let fixture_ui_visibility = {} let fixture_forbidden = []
fn fixture_write(path,value){fixture_files[path]=value return nil}
fn fixture_read(path){let value=fixture_files[path] if value==nil{return ""} return value}
let fs={exists:|path|fixture_files[path]!=nil write:|path,value|fixture_write(path,value)
    read:|path|fixture_read(path) mkdir:|path|nil sha256:|value|mod.fixture.sha256(value)
    sha256_file:|path|{if fixture_files[path]==nil{return ""} return mod.fixture.sha256(fixture_read(path))}}
fn time_now(){return 1700000000+fixture_tick}
fn random_u32(){fixture_serial=fixture_serial+1 return fixture_serial}
fn start_timeout(delay,callback){fixture_timers.push({due:fixture_tick+delay callback:callback})}
fn fixture_transport(method,args,callback){fixture_forbidden.push(method) callback({is_ok:false error:"Fixture forbids external transport"})}
fn fixture_widget(name){return {text:||{let value=fixture_ui_values[name] if value==nil{return ""} return value}
    set_text:|value|{fixture_ui_values[name]=value} render:||{} set_visible:|value|{fixture_ui_visibility[name]=value}
    is_visible:||fixture_ui_visibility[name]==true set_focus:||{} set_enabled:|value|{}}}
let ui = {}
__UI__
'''


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--expected-sha', default=SOURCE_SHA)
    parser.add_argument('--runner', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', choices=CASES, default=list(CASES))
    parser.add_argument('--seed-files', type=Path)
    parser.add_argument('--mail-terminal-fixture', action='store_true')
    args = parser.parse_args()
    source = args.source.read_text()
    assert digest(source) == args.expected_sha, 'Use the explicit frozen candidate'
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'source.splash').write_text(source)
    files = json.loads(args.seed_files.read_text()) if args.seed_files else {}
    marker = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.M)
    prefix = source[:marker.start()] + source[source.index('// BEGIN ACTION_CHAIN_PROJECTION'):source.index('// END ACTION_CHAIN_PROJECTION')]
    original = helpers.functions_in(prefix)
    ui = '\n'.join(f'ui.{name}=fixture_widget("{name}")' for name in sorted(set(re.findall(r'\bui\.([a-zA-Z_][a-zA-Z_0-9]*)', prefix))))
    summaries = []
    for name in args.cases:
        path, output, transport = CASES[name]
        folder = out / name
        folder.mkdir()
        probe = (CENTRAL / path).read_text()
        probe_sha = digest(probe)
        # Standalone dummy widget roots are irrelevant to windowless execution.
        probe = re.sub(r'^View\{[\s\S]*$', '', probe, flags=re.M).replace('__SUITE__', 'production')
        adaptations = ['remove_dummy_widget_root', 'production_suite_placeholder']
        if args.mail_terminal_fixture and name == 'mail':
            old = '    if method == "mail.compose_status" { cb({is_ok: true data: probe_compose}) return }'
            new = '''    if method == "mail.compose_status" {
        probe_compose.attempts = [{operation_id: "synthetic-op" revision: probe_compose.revision status: probe_compose.status
            payload: {to: probe_compose.to subject: probe_compose.subject body: probe_compose.body} receipt: {accepted: probe_compose.status == "accepted"}}]
        cb({is_ok: true data: probe_compose}) return
    }'''
            assert probe.count(old) == 1
            probe = probe.replace(old, new)
            adaptations.append('add_current_host_attempt_evidence_to_compose_status_fixture')
        replacements = {
            'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}',
            'set_page': 'fn set_page(next){page=next}',
            'storage_write': 'fn storage_write(path,data){return fixture_write(path,data)}',
            'storage_read': 'fn storage_read(path){return fixture_read(path)}',
        }
        if name == 'calendar_restore':
            replacements['mail_watch_boot'] = 'fn mail_watch_boot(){}'
        prepared = prefix
        for function, body in replacements.items():
            prepared = helpers.replace_function(prepared, function, body)
        prepared = prepared.replace('host.request(', (transport or 'fixture_transport') + '(')
        executed_functions = helpers.functions_in(prepared)
        changed = sorted(function for function, body in original.items()
                         if body != executed_functions[function].replace((transport or 'fixture_transport') + '(', 'host.request('))
        assert changed == sorted(replacements), changed
        # Memory restart carries the first VM's exact serialized file strings to
        # a new process; other cases use fresh synthetic files.
        initial = files if name == 'memory_restart' else {}
        header = HEADER.replace('__FILES__', json.dumps(json.dumps(initial, ensure_ascii=False), ensure_ascii=False)).replace('__UI__', ui)
        footer = '''
let fixture_steps = 0
while fixture_timers.len()>0 && fixture_files[__OUTPUT__]==nil && fixture_steps<2000 {
    let next=0
    for i in fixture_timers.len(){if fixture_timers[i].due<fixture_timers[next].due{next=i}}
    let timer=fixture_timers[next] let remaining=[]
    for i in fixture_timers.len(){if i!=next{remaining.push(fixture_timers[i])}}
    fixture_timers=remaining fixture_tick=timer.due fixture_steps=fixture_steps+1 timer.callback()
}
({output:fixture_read(__OUTPUT__) files:fixture_files steps:fixture_steps forbidden:fixture_forbidden}).to_json()
'''.replace('__OUTPUT__', json.dumps(output))
        executed = header + prepared + '\n' + probe + footer
        script = folder / 'executed.splash'
        script.write_text(executed)
        result = subprocess.run([str(args.runner.resolve(strict=True)), str(script)], capture_output=True, text=True, timeout=60)
        (folder / 'stdout.log').write_text(result.stdout)
        (folder / 'stderr.log').write_text(result.stderr)
        data = json.loads(result.stdout) if result.returncode == 0 else None
        raw = json.loads(data['output']) if data and data.get('output') else None
        checks = (raw.get('checks', raw) if raw else {})
        checks = {key: value for key, value in checks.items() if type(value) is bool}
        failed = [key for key, value in checks.items() if not value]
        entry = {'case': name, 'exit_code': result.returncode, 'passed': sum(checks.values()), 'failed': failed,
                 'status': 'PASS' if data and checks and not failed else 'FAIL', 'probe_path': path,
                 'original_probe_sha256': probe_sha, 'executed_sha256': digest(executed),
                 'boundary_replacements': changed, 'probe_adaptations': adaptations,
                 'source_sha256': args.expected_sha, 'raw_logs': str(folder)}
        summaries.append(entry)
        if name == 'memory' and data:
            files = data['files']
            (folder / 'serialized-files.json').write_text(json.dumps(files, ensure_ascii=False) + '\n')
        print(json.dumps(entry, ensure_ascii=False), flush=True)
    (out / 'command.log').write_text(' '.join(sys.argv) + '\n' + '\n'.join(json.dumps(entry, ensure_ascii=False) for entry in summaries) + '\n')
    return 0 if all(entry['status'] == 'PASS' for entry in summaries) else 1


if __name__ == '__main__':
    raise SystemExit(main())
