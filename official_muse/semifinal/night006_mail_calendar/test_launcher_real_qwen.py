#!/usr/bin/env python3
"""Compile Launcher, bootstrap a fresh profile and infer twice on actual Qwen.

Host is an explicit signed stub with no window; duplicate process/mutex checks
are isolated only for this fixture. No real Host or production data is touched.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen
import uuid

p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--original-tests', type=Path, required=True)
p.add_argument('--resources', type=Path, required=True)
p.add_argument('--request', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
source = a.source.read_text()
receipt = {'level': 'ACTUAL_LAUNCHER_AND_REAL_QWEN_STUB_HOST_NOT_GUI_NOT_NATIVE_MODEL_SERVICE',
           'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'rounds': [], 'status': 'RUNNING'}
spec = importlib.util.spec_from_file_location('original_launcher_fixture', a.original_tests)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
with tempfile.TemporaryDirectory(prefix='muse-real-qwen-launcher-source-') as temp:
    snapshot = Path(temp)
    private = source.replace('@"/Contents/Resources/host-runtime/muse-host"', '@"/fixture-no-real-host-probe"')
    private = private.replace('@"muse-integrated-host.flock"', f'@"muse-real-qwen-fixture-{uuid.uuid4().hex}.flock"')
    receipt['fixture_source_sha256'] = hashlib.sha256(private.encode()).hexdigest()
    (snapshot/'muse_launcher.m').write_text(private)
    shutil.copy2(a.original_tests.parent/'workbuddy_launcher.sh', snapshot)
    fixture.HERE = snapshot
    cls = fixture.LauncherTests
    cls.setUpClass()
    test = cls('runTest')
    test.setUp()
    app = test.hybrid_app
    local = app/'Contents/Resources/local-model'
    shutil.rmtree(local/'llama')
    shutil.copytree(a.resources/'local-model/llama', local/'llama', symlinks=True)
    (local/'qwen2.5-0.5b-instruct-q4_0.gguf').unlink()
    os.link(a.resources/'local-model/qwen2.5-0.5b-instruct-q4_0.gguf', local/'qwen2.5-0.5b-instruct-q4_0.gguf')
    subprocess.run(['codesign', '--force', '--sign', '-', str(app)], check=True, capture_output=True)
    process = None
    try:
        original_profile = None
        original_route = None
        for index in (1, 2):
            pid_file = test.state/f'host-{index}.pid'
            env = test.launch_env({'MUSE_FIXTURE_HOST_DELAY': '30', 'MUSE_FIXTURE_PID_FILE': str(pid_file)})
            begin = time.monotonic()
            with (out/f'round-{index}-launcher-process.log').open('wb') as log:
                process = subprocess.Popen([str(app/'Contents/MacOS/Launcher')], env=env, stdout=log, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 60
                while not pid_file.exists() and time.monotonic() < deadline:
                    if process.poll() is not None:
                        raise RuntimeError(f'Launcher ended before stub Host: {process.returncode}')
                    time.sleep(0.1)
                if not pid_file.exists():
                    raise TimeoutError('Host handoff not ready')
                profile = test.profile.read_bytes()
                parsed = json.loads(profile)
                route = parsed['config']['llm']['primary']['route']['base_url']
                status = json.loads((test.state/'local-model.json').read_text())
                if route != status['route_base_url']:
                    raise AssertionError('Profile route differs from running model endpoint')
                payload = json.loads(a.request.read_text())
                (out/f'round-{index}-request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2))
                started = time.monotonic()
                request = Request(route+'/chat/completions', data=json.dumps(payload).encode(), method='POST', headers={'Content-Type': 'application/json'})
                with urlopen(request, timeout=25) as response:
                    body = json.load(response)
                (out/f'round-{index}-response.json').write_text(json.dumps(body, ensure_ascii=False, indent=2))
                decoded = json.loads(body['choices'][0]['message']['content'])
                if set(decoded) != {'reply'} or not isinstance(decoded['reply'], str) or not decoded['reply']:
                    raise AssertionError('Actual Qwen did not produce the Muse reply schema')
                same = index == 1 or (profile == original_profile and route == original_route)
                if not same:
                    raise AssertionError('Restart changed profile or endpoint')
                receipt['rounds'].append({'round': index, 'ready_seconds': round(started-begin, 3),
                    'inference_seconds': round(time.monotonic()-started, 3), 'reply': decoded['reply'],
                    'profile_and_route_preserved': same, 'status': 'PASS'})
                original_profile, original_route = profile, route
                (out/f'round-{index}-fresh-profile.json').write_bytes(profile)
                process.terminate()
                process.wait(timeout=5)
                process = None
                deadline = time.monotonic()+15
                while list(test.state.glob('launch-*.ready')) and time.monotonic()<deadline:
                    time.sleep(0.1)
                if list(test.state.glob('launch-*.ready')):
                    raise TimeoutError('Owned guardian did not finish cleanup')
                final_status = json.loads((test.state/'local-model.json').read_text())
                if final_status['service_status'] != 'stopped':
                    raise AssertionError('Owned local model not stopped')
                (out/f'round-{index}-stopped-status.json').write_text(json.dumps(final_status, indent=2))
        receipt['status'] = 'PASS'
    except Exception as e:
        receipt['status'] = 'FAIL'
        receipt['error'] = f'{type(e).__name__}: {e}'
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        for name in ('launcher.log', 'host.log', 'model.log'):
            path = test.state/'logs'/name
            if path.exists():
                shutil.copy2(path, out/name)
        test.tearDown()
        cls.tearDownClass()
        (out/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
        print(json.dumps(receipt, ensure_ascii=False))
raise SystemExit(0 if receipt['status']=='PASS' else 1)
