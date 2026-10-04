#!/usr/bin/env python3
"""Real card-host with copied production memory core and synthetic app-jail only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
HOST = Path(os.environ.get('MUSE_CARD_HOST', '/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/release/card-host'))

def run(output, port=8482, probe='memory_suite', module_source=None, main_source=None, visible=False):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', port)) == 0:
            raise RuntimeError(f'port {port} belongs to another process')
    source = main_source.read_text() if main_source else subprocess.check_output(['git','show','b02d103:official_muse/app/bundle/main.splash'],cwd=ROOT,text=True)
    # Capture the exact production core independently of changing UI/functions.
    core = source[source.index('let runs = []'):source.index('// BEGIN GLOBAL_MEMORY')]
    core = 'let goals = []\nlet selected_id = ""\nlet task = nil\nlet activity = []\nlet memory = []\n' + core
    module = (module_source or ROOT / 'official_muse/global_memory.splash').read_text()
    script = (Path(__file__).parent / (probe + '.splash')).read_text()
    bundle, state = output / 'bundle', output / 'state'
    shutil.copytree(ROOT / 'official_muse/app/bundle', bundle, dirs_exist_ok=True)
    # The copied probe changes the payload; keep its admission explicitly unsigned.
    manifest_path = bundle / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest.get('integrity', {}).pop('signature', None)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    if main_source:
        # Current memory core depends on task scope helpers elsewhere in main.
        # Keep every production function; replace only rendering and transport.
        import sys
        sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
        from runtime_probe import replace_function
        assert module in source, 'Module differs from the frozen main embedding'
        prefix = source[:source.index('start_timeout(0.05, || boot())')]
        prefix = prefix.replace('host.request(', 'memory_fixture_request(')
        prefix = replace_function(prefix, 'redraw', 'fn redraw(){}')
        prefix = replace_function(prefix, 'set_page', 'fn set_page(next){ page = next }')
        transport = '\nlet memory_forbidden_calls = []\nfn memory_fixture_request(service,args,cb){ memory_forbidden_calls.push(service) fs.write("memory-forbidden-calls.json",memory_forbidden_calls.to_json()) cb({is_ok: false error: "fixture: external service forbidden"}) }\n'
        instrumented = prefix + transport + script
    else:
        instrumented = core + '\n' + module + '\n' + script
    (bundle / 'main.splash').write_text(instrumented)
    report_name = 'memory-report.json' if probe == 'memory_suite' else probe + '-report.json'
    report = state / 'muse-goals' / report_name
    report.unlink(missing_ok=True)
    env = dict(os.environ, MAKEPAD_REMOTE=str(port), MAKEPAD_HIDE_WINDOWS='0' if visible else '1')
    env.pop('MAKEPAD_FOCUS', None)
    with (output / (probe + '.log')).open('w') as log:
        proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(state),
                                 '--allow-unsigned', '--stamp', '--size', '600x700'],
                                env=env, cwd=HOST.parents[2], stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 25
            while not report.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError((output / (probe + '.log')).read_text()[-10000:])
                time.sleep(.1)
            result = json.loads(report.read_text())
            time.sleep(.05)
            if '[E]' in (output / (probe + '.log')).read_text():
                raise RuntimeError((output / (probe + '.log')).read_text()[-6000:])
            result['main_source_sha256'] = hashlib.sha256(source.encode()).hexdigest()
            result['core_sha256'] = hashlib.sha256(core.encode()).hexdigest()
            result['module_sha256'] = hashlib.sha256(module.encode()).hexdigest()
            result['host_sha256'] = hashlib.sha256(HOST.read_bytes()).hexdigest()
            result['scope'] = 'FULL_MAIN_FUNCTIONS/FIXTURE: actual card-host, frozen main, synthetic data, mocked render/transport' if main_source else 'LOCAL/FIXTURE: actual card-host, production memory core, synthetic data; no Host services/model'
            result['source_mode'] = 'frozen_full_main' if main_source else 'baseline_core_current_module'
            if main_source:
                forbidden = state / 'muse-goals/memory-forbidden-calls.json'
                result['no_external_transport'] = not forbidden.exists() or json.loads(forbidden.read_text()) == []
                result['instrumented_sha256'] = hashlib.sha256(instrumented.encode()).hexdigest()
            (output / (probe + '-result.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result
        finally:
            try: urlopen(f'http://127.0.0.1:{port}/quit', timeout=2).read()
            except Exception: proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8482)
    parser.add_argument('--probe', default='memory_suite')
    parser.add_argument('--module-source', type=Path)
    parser.add_argument('--main-source', type=Path, help='Frozen full main with mocked render/transport; baseline remains the default')
    parser.add_argument('--visible', action='store_true', help='Use the actual rendered window when hidden startup/timers are unreliable')
    args = parser.parse_args()
    run(args.output, args.port, args.probe, args.module_source, args.main_source, args.visible)
