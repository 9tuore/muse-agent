#!/usr/bin/env python3
"""Run existing production-function suites and chat binding against one source snapshot.

FIXTURE only: host transport and visual widgets are replaced, storage is the real
isolated card-host fs. Reports never imply model inference or OS actions passed.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
import runtime_probe as existing


def run_suite(name, source, bundle_source, output, port, probe_path=None):
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', port)) == 0:
            raise RuntimeError('Remote port already in use; existing process untouched.')
    startup = re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)', source, re.MULTILINE)
    if startup is None:
        raise RuntimeError('Production startup marker missing; source not replaced.')
    prefix = source[:startup.start()]
    prefix = prefix.replace('host.request(', 'fixture_request(')
    prefix = existing.replace_function(prefix, 'redraw', 'fn redraw(){}')
    prefix = existing.replace_function(prefix, 'set_page', 'fn set_page(next){ page = next }')
    prefix = existing.replace_function(prefix, 'calendar_enabled', 'fn calendar_enabled(){ return true }')
    widget = existing.WIDGET
    if name in ('three_hour_scheduling', 'calendar_policy'):
        prefix = prefix.replace('fixture_request(', 'three_hour_request(')
    if name == 'mail_calendar_chain':
        prefix = prefix.replace('fixture_request(', 'chain_fixture_request(')
        prefix = existing.replace_function(prefix, 'mail_redraw', 'fn mail_redraw(){}')
    if name in ('incoming_suite', 'mail_monitor'):
        prefix = prefix.replace('fixture_request(', 'incoming_fixture_request(')
        prefix = existing.replace_function(prefix, 'mail_enabled', 'fn mail_enabled(){ return true }')
        prefix = existing.replace_function(prefix, 'mail_watch_refresh', 'fn mail_watch_refresh(){}')
        prefix = existing.replace_function(prefix, 'mail_redraw', 'fn mail_redraw(){ mail_watch_draft_status() }')
        widget = widget.replace('    Label{text:', '    mail_to := TextInput{width: Fill}\n'
                               '    mail_subject := TextInput{width: Fill}\n'
                               '    mail_body := TextInput{width: Fill}\n'
                               '    mail_intent := TextInput{width: Fill}\n    Label{text:', 1)
    if name == 'chat_mutation':
        prefix = existing.replace_function(prefix, 'mail_enabled', 'fn mail_enabled(){ return true }')
        prefix = existing.replace_function(prefix, 'mail_redraw', 'fn mail_redraw(){}')
        widget = widget.replace('    Label{text:', '    mail_to := TextInput{width: Fill}\n'
                               '    mail_subject := TextInput{width: Fill}\n'
                               '    mail_body := TextInput{width: Fill}\n'
                               '    session_focus_project := TextInput{width: Fill}\n'
                               '    session_focus_owner := TextInput{width: Fill}\n    Label{text:', 1)
    own_suites = {'chat_binding': 'regression_chat.splash', 'chat_proposal': 'regression_proposal.splash',
                  'model_preflight': 'regression_preflight.splash', 'model_suite': 'regression_model.splash',
                  'chat_derived': 'regression_derived.splash', 'mail_monitor': 'regression_mail_monitor.splash',
                  'mail_calendar_chain': 'regression_mail_calendar.splash', 'chat_goal_binding': 'regression_chat_goal.splash', 'incoming_suite': 'regression_incoming.splash', 'task_focus': 'regression_task_focus.splash'}
    if probe_path is None and name in ('three_hour_scheduling', 'calendar_policy'):
        probe_path = ROOT / 'official_muse/prelim/tests' / (name + '.splash')
    if probe_path is None:
        probe_path = Path(__file__).with_name(own_suites[name]) if name in own_suites else Path(existing.__file__).with_name(name + '.splash')
    output.mkdir(parents=True)
    bundle, state = output / 'bundle', output / 'state'
    shutil.copytree(bundle_source, bundle)
    manifest_path = bundle / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    # Instrumentation changes the copied bundle; never carry a production signature.
    manifest['integrity'].pop('signature', None)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    transport = 'let fixture_accounts_queue = []\nlet fixture_accounts_deferred = false\n' + existing.TRANSPORT.replace('    if service == "model.complete"',
        '    if service == "mail.accounts" { if fixture_accounts_deferred { fixture_accounts_queue.push(callback) return } callback({is_ok: true data: [{id: "fixture-account" address: "self@example.invalid"} {id: "synthetic-account" address: "synthetic@example.invalid"}]}) return }\n'
        '    if service == "model.complete"')
    probe_source = probe_path.read_text()
    if name == 'calendar_policy':
        fixtures = (ROOT / 'official_muse/prelim/tests/three_hour_scheduling.splash').read_text()
        probe_source = fixtures[:fixtures.index('fn probe(){')] + probe_source
    (bundle / 'main.splash').write_text(prefix + transport + probe_source + widget)
    env = dict(os.environ, MAKEPAD_REMOTE=str(port), MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    with (output / 'runtime.log').open('w') as log:
        proc = subprocess.Popen([str(existing.HOST), '--bundle', str(bundle), '--app-data', str(state),
                                 '--allow-unsigned', '--stamp', '--size', '600x700'],
                                env=env, cwd=existing.HOST.parents[2], stdout=log, stderr=log)
        try:
            report = state / 'muse-goals/probe.json'
            deadline = time.monotonic() + 25
            while not report.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('No probe report; inspect runtime.log')
                time.sleep(.2)
            time.sleep(.1)
            result = json.loads(report.read_text())
            runtime_log = (output / "runtime.log").read_text()
            if "[E]" in runtime_log or "script time budget exceeded" in runtime_log:
                raise RuntimeError("Runtime logged an error; original log/report preserved")
            if not isinstance(result, dict):
                raise RuntimeError('Probe report is not an object; inspect preserved probe.json and runtime.log')
            checks = {k: v for k, v in result.items() if isinstance(v, bool)}
            failed = [k for k, v in checks.items() if not v]
            if result.get('forbidden_calls'):
                failed.append('forbidden_calls')
            result.update(test_kind='FIXTURE_PRODUCTION_FUNCTIONS', source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                          passed=len(checks) - len(failed), failed=failed,
                          suite_sha256=hashlib.sha256(probe_path.read_bytes()).hexdigest(),
                          host_sha256=hashlib.sha256(existing.HOST.read_bytes()).hexdigest(),
                          real_model=False, real_mail=False, real_calendar=False)
            (output / 'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            return {k: result[k] for k in ('passed', 'failed', 'test_kind', 'source_sha256')}
        finally:
            try:
                urlopen(f'http://127.0.0.1:{port}/quit', timeout=2).read()
            except OSError:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8485)
    p.add_argument('--compact-tokenizer', type=Path,
                   help='Use a token-verified compact copy without changing Host budgets.')
    p.add_argument('--suites', nargs='+', default=['selection_suite', 'calendar_suite', 'model_suite', 'incoming_suite', 'chat_binding', 'chat_proposal', 'model_preflight', 'chat_derived'])
    args = p.parse_args()
    args.out = args.out.resolve()
    # Immutable snapshot binds all suites to the same bytes despite concurrent UI edits.
    args.out.mkdir(parents=True, exist_ok=False)
    snapshot = args.out / 'source-bundle'
    shutil.copytree(args.source.resolve().parent, snapshot)
    source = (snapshot / args.source.name).read_text()
    instrumented_source = source
    compact_evidence = None
    if args.compact_tokenizer:
        tokenizer = args.compact_tokenizer.resolve(strict=True)
        compact_bundle = args.out / 'compact-source-bundle'
        compact = subprocess.run([sys.executable, str(ROOT / 'official_muse/ui_memory/compact_bundle.py'),
                                  '--source', str(snapshot), '--out', str(compact_bundle)],
                                 check=True, capture_output=True, text=True)
        tokens = subprocess.run([str(tokenizer), str(snapshot / args.source.name),
                                 str(compact_bundle / args.source.name)],
                                check=True, capture_output=True, text=True)
        compact_evidence = {'compact': json.loads(compact.stdout), 'tokens': json.loads(tokens.stdout),
                            'tokenizer_sha256': hashlib.sha256(tokenizer.read_bytes()).hexdigest()}
        (args.out / 'compact-equivalence.json').write_text(json.dumps(compact_evidence, indent=2) + '\n')
        instrumented_source = (compact_bundle / args.source.name).read_text()
    results = {}
    for name in args.suites:
        try:
            results[name] = run_suite(name, instrumented_source, snapshot, args.out / name, args.port)
        except Exception as error:
            results[name] = {'status': 'ERROR', 'error': str(error)}
        print(name, json.dumps(results[name], ensure_ascii=False), flush=True)
    summary = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
               'created_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'suites': results,
               'instrumented_source_sha256': hashlib.sha256(instrumented_source.encode()).hexdigest(),
               'compact_equivalence': compact_evidence,
               'boundary': 'FIXTURE only; candidate may be intermediate until controller freezes it.'}
    (args.out / 'report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    return 1 if any(v.get('failed') or v.get('status') == 'ERROR' for v in results.values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
