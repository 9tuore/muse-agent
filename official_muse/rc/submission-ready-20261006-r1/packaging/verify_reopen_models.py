#!/usr/bin/env python3
"""Verify portable reopen, official AI settings, and custom-profile preservation.

Reuses only the synthetic first-model test state on port 8492. A second fresh
state holds a credential-free fixture provider. No real accounts are accessed.
"""
import importlib.util
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
PRIVATE_SCREENSHOTS = False
spec = importlib.util.spec_from_file_location('first_model', E / 'verify_first_model.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def run_settings(state, model_id):
    env = {k: os.environ[k] for k in ('HOME', 'PATH', 'USER', 'TMPDIR', 'LANG') if k in os.environ}
    env.update(MUSE_REPRO_STATE=str(state), MUSE_REPRO_REMOTE='8492')
    log_path = E / ('models-' + state.name + '.txt')
    with log_path.open('w') as log:
        child = subprocess.Popen([str(t.APP / 'Contents/MacOS/muse-launcher'), '--models'],
                                 cwd=t.APP.parent, env=env, stdout=log, stderr=log)
        try:
            remote = t.remote.Remote(8492)
            for _ in range(200):
                if child.poll() is not None:
                    raise RuntimeError('settings launcher exited')
                try:
                    widgets = remote.widgets()
                    labels = [w.get('t', '') for w in widgets if w.get('t') and w.get('ty') != 'Splash']
                    if 'AI 模型设置' in labels and model_id in labels:
                        return labels, remote
                except Exception:
                    pass
                time.sleep(.25)
            raise RuntimeError('official AI providers settings did not render')
        finally:
            # Snapshot while the actual settings UI is alive, without entering a key.
            try:
                images = E / '.local-state/screenshots' if PRIVATE_SCREENSHOTS else E
                images.mkdir(parents=True, exist_ok=True)
                remote.shot(images / ('models-' + state.name + '.png'))
            except Exception:
                pass
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=25)


def main():
    global E, PRIVATE_SCREENSHOTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, default=t.APP)
    parser.add_argument('--state', type=Path, default=t.STATE)
    parser.add_argument('--evidence', type=Path, default=E)
    parser.add_argument('--private-screenshots', action='store_true')
    args = parser.parse_args()
    E = args.evidence.resolve()
    E.relative_to(Path(__file__).resolve().parent)
    E.mkdir(parents=True, exist_ok=True)
    t.APP, t.STATE, t.EVIDENCE = args.app.resolve(), args.state.resolve(), E
    PRIVATE_SCREENSHOTS = args.private_screenshots
    result = dict(status='FAIL', port=8492, external_actions=False)
    try:
        path = t.STATE / 'home/octos-home/.octos/profiles/_main.json'
        before = json.loads(path.read_text())
        session = t.one_file('chat-sessions.json').read_bytes()
        before_model = json.loads((t.STATE / 'local-model.json').read_text())
        labels, _ = run_settings(t.STATE, before['config']['llm']['primary']['model_id'])
        after = json.loads(path.read_text())
        after_model = json.loads((t.STATE / 'local-model.json').read_text())
        assert after['created_at'] == before['created_at']
        assert after['config']['llm']['primary']['model_id'] == before['config']['llm']['primary']['model_id']
        assert session == t.one_file('chat-sessions.json').read_bytes()
        assert after_model['pid'] != before_model['pid']
        assert not t.process_exists(after_model['pid'])
        result['reopen'] = dict(same_profile=True, created_at_preserved=True, chat_history_bytes_preserved=True,
            local_route=after['config']['llm']['primary']['route'], own_model_stopped=True,
            official_settings_labels=labels)
        state = E / '.local-state/custom-profile-preservation-r2'
        if state.exists():
            raise RuntimeError('custom fixture state already exists')
        path = state / 'home/octos-home/.octos/profiles/_main.json'
        path.parent.mkdir(parents=True)
        fixture = dict(id='_main', name='synthetic custom local provider', enabled=True,
            config=dict(llm=dict(primary=dict(family_id='local', model_id='fixture-custom-model',
                route=dict(base_url='http://127.0.0.1:1/v1', api_type='openai')), fallbacks=[]), env_vars={}))
        original = (json.dumps(fixture, ensure_ascii=False) + '\n').encode()
        path.write_bytes(original)
        path.chmod(0o600)
        labels, _ = run_settings(state, 'fixture-custom-model')
        assert path.read_bytes() == original
        assert not (state / 'local-model.json').exists()
        result['custom_profile'] = dict(fixture=True, unchanged_bytes=True,
            bundled_model_not_started=True, official_settings_labels=labels, model_requests_performed=False)
        result['status'] = 'PASS'
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        t.dump('REOPEN_MODELS.json', result)
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
