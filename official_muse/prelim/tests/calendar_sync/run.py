#!/usr/bin/env python3
"""Frozen production Calendar functions, synthetic transport, isolated card-host fs."""
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

ROOT = Path(__file__).resolve().parents[4]
OWN = ROOT / 'official_muse/app/build/repair-delivery-20261004-115054/thread-calendar'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def functions_in(text):
    found = {}
    for match in re.finditer(r'^fn ([A-Za-z_][A-Za-z_0-9]*)\(', text, re.MULTILINE):
        name = match[1]
        start = text.index('{', match.start())
        depth, quoted, escaped = 1, False, False
        pos = start + 1
        while depth:
            c = text[pos]
            if quoted:
                if escaped:
                    escaped = False
                elif c == '\\':
                    escaped = True
                elif c == '"':
                    quoted = False
            elif c == '"':
                quoted = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            pos += 1
        assert name not in found
        found[name] = text[match.start():pos]
    return found


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-bundle', type=Path, required=True)
    p.add_argument('--host', type=Path, required=True)
    p.add_argument('--host-cwd', type=Path, help='Resource workspace for a preserved/moved Host binary.')
    p.add_argument('--proposed-helpers', type=Path, help='Own proposed definitions; marks run PROPOSAL_FIXTURE.')
    p.add_argument('--proposed-list', type=Path, help='Own proposed calendar_list_events replacement; marks run PROPOSAL_FIXTURE.')
    p.add_argument('--state-seed', type=Path, help='Synthetic state from an earlier owned run; copied to a new process HOME/app-data.')
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8651)
    args = p.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(OWN)
    assert args.host.is_file() and args.probe.is_file()
    host_cwd = (args.host_cwd or args.host.resolve().parents[2]).resolve()
    assert host_cwd.is_dir()
    with socket.socket() as check:
        assert check.connect_ex(('127.0.0.1', args.port)) != 0, 'Port in use; other instance untouched.'
    sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
    import runtime_probe
    out.mkdir(parents=True, exist_ok=False)
    state_seed_hashes = {}
    if args.state_seed:
        state_seed = args.state_seed.resolve()
        assert state_seed.is_relative_to(OWN) and state_seed.is_dir()
        for path in sorted(state_seed.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                state_seed_hashes[str(path.relative_to(state_seed))] = sha(path)
        shutil.copytree(state_seed, out / 'state')
        # The next process must produce a fresh report. Preserve the seed itself.
        (out / 'state/muse-goals/probe.json').unlink(missing_ok=True)
    snapshot = out / 'source-bundle'
    shutil.copytree(args.source_bundle, snapshot)
    compact = out / 'compact-source-bundle'
    command = [sys.executable, str(ROOT / 'official_muse/ui_memory/compact_bundle.py'), '--source', str(snapshot), '--out', str(compact)]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    tokenizer = ROOT / 'official_muse/app/build/ui-memory-20261003/incoming-startup-host-r2/bundle-tokens'
    equal = subprocess.run([str(tokenizer), str(snapshot / 'main.splash'), str(compact / 'main.splash')], check=True, capture_output=True, text=True)
    tokens = json.loads(equal.stdout)
    assert tokens['tokens_equal']
    source = (compact / 'main.splash').read_text()
    startup = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.MULTILINE)
    assert startup
    prefix = source[:startup.start()].replace('host.request(', 'cal_sync_request(')
    substitutions = {
        'redraw': 'fn redraw(){}', 'set_page': 'fn set_page(next){ page = next }',
        'calendar_enabled': 'fn calendar_enabled(){ return true }',
        'mail_enabled': 'fn mail_enabled(){ return true }', 'mail_redraw': 'fn mail_redraw(){}',
    }
    if args.proposed_list:
        assert args.proposed_list.resolve().is_relative_to(OWN) and args.proposed_helpers
        replacement = args.proposed_list.read_text().replace('host.request(', 'cal_sync_request(')
        assert set(functions_in(replacement)) == {'calendar_list_events'}
        substitutions['calendar_list_events'] = replacement
    for name, replacement in substitutions.items():
        prefix = runtime_probe.replace_function(prefix, name, replacement)
    original_functions = functions_in(source[:startup.start()])
    retained_functions = functions_in(prefix)
    assert original_functions.keys() == retained_functions.keys()
    changed = [name for name, body in original_functions.items()
               if body != retained_functions[name].replace('cal_sync_request(', 'host.request(')]
    assert sorted(changed) == sorted(substitutions), changed
    function_audit = {'production_function_count': len(original_functions),
                      'retained_function_count': len(retained_functions),
                      'only_allowed_substitutions_changed': sorted(changed),
                      'all_other_functions_byte_equal_after_transport_normalization': True}
    (out / 'function-audit.json').write_text(json.dumps(function_audit, indent=2) + '\n')
    probe = out / 'probe.splash'
    shutil.copy2(args.probe, probe)
    widget = runtime_probe.WIDGET.replace('    Label{text:',
        '    calendar_range_start := TextInput{width: Fill}\n'
        '    calendar_range_end := TextInput{width: Fill}\n'
        '    calendar_panel := View{width: Fill height: Fit on_render: || {}}\n    Label{text:', 1)
    bundle = out / 'bundle'
    shutil.copytree(compact, bundle)
    manifest = json.loads((bundle / 'manifest.json').read_text())
    manifest['integrity'].pop('signature', None)
    (bundle / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    helpers = ''
    if args.proposed_helpers:
        assert args.proposed_helpers.resolve().is_relative_to(OWN)
        helpers = args.proposed_helpers.read_text()
        assert not set(functions_in(helpers)).intersection(original_functions)
    (bundle / 'main.splash').write_text(prefix + helpers + runtime_probe.TRANSPORT + probe.read_text() + widget)
    fixture_home = out / 'home'
    fixture_home.mkdir()
    env = dict(os.environ, HOME=str(fixture_home), MAKEPAD_REMOTE=str(args.port), MAKEPAD_HIDE_WINDOWS='1', PYTHONDONTWRITEBYTECODE='1')
    env.pop('MAKEPAD_FOCUS', None)
    log_path = out / 'runtime.log'
    summary = {'kind': 'PROPOSAL_FIXTURE' if helpers else 'FIXTURE', 'readable_source_sha256': sha(snapshot / 'main.splash'),
               'compact_source_sha256': sha(compact / 'main.splash'), 'host_sha256': sha(args.host),
               'probe_sha256': sha(probe), 'executed_bundle_sha256': sha(bundle / 'main.splash'),
               'tokens': tokens, 'compact': json.loads(result.stdout), 'all_production_functions_retained': True,
               'substituted_functions': sorted(substitutions), 'transport': 'Every host.request redirected to synthetic cal_sync_request.',
               'budget': 'Official unchanged 64ms.', 'boundary': 'Not app boot/UI/EKEvent/native/model acceptance; only actual selected production functions with fixture state.',
               'real_external_calls': 0, 'private_profile_reads': 0, 'command': sys.argv}
    summary['host_cwd'] = str(host_cwd)
    summary['isolated_home'] = str(fixture_home)
    summary['function_audit'] = function_audit
    summary['state_seed_hashes'] = state_seed_hashes
    summary['state_seed_excluded_from_copy_for_fresh_report'] = ['muse-goals/probe.json'] if args.state_seed else []
    if helpers:
        summary['proposed_helpers_sha256'] = sha(args.proposed_helpers)
        summary['boundary'] = 'PROPOSED candidate only, not integrated product. Other functions retained from frozen production source; no real Calendar/app boot acceptance.'
    if args.proposed_list:
        summary['proposed_list_sha256'] = sha(args.proposed_list)
    proc = None
    try:
        with log_path.open('w') as log:
            proc = subprocess.Popen([str(args.host.resolve()), '--bundle', str(bundle), '--app-data', str(out / 'state'), '--allow-unsigned', '--stamp', '--size', '600x700'],
                                    cwd=host_cwd, env=env, stdout=log, stderr=log)
            report_path = out / 'state/muse-goals/probe.json'
            deadline = time.monotonic() + 35
            while not report_path.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('No probe report; original runtime log retained.')
                time.sleep(.2)
            report = json.loads(report_path.read_text())
            time.sleep(.1)
            if '[E]' in log_path.read_text() or 'script time budget exceeded' in log_path.read_text():
                raise RuntimeError('Runtime error; original log and state report retained.')
            checks = {k: v for k, v in report.items() if isinstance(v, bool)}
            report.update(kind=summary['kind'], readable_source_sha256=summary['readable_source_sha256'],
                          compact_source_sha256=summary['compact_source_sha256'], host_sha256=summary['host_sha256'],
                          probe_sha256=summary['probe_sha256'], passed=sum(checks.values()),
                          failed=[k for k, v in checks.items() if not v])
            if report.get('forbidden_calls'):
                report['failed'].append('forbidden_calls')
            (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            summary['result'] = {k: report[k] for k in ['passed', 'failed']}
    except Exception as error:
        summary['result'] = {'status': 'ERROR', 'error': str(error)}
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    summary['runtime_log_sha256'] = sha(log_path)
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary['result'], ensure_ascii=False), flush=True)
    return 1 if summary['result'].get('failed') or summary['result'].get('status') == 'ERROR' else 0


if __name__ == '__main__':
    raise SystemExit(main())
