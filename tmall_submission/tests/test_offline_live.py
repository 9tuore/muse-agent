#!/usr/bin/env python3
"""Fresh local profile, real packaged Host -> model.complete -> bundled Qwen.

Uses only a new test directory and Makepad port 8492. No credentials, external
actions, host rebuild, model proxy, or fabricated response are involved.
"""
import hashlib
import argparse
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'tmall_submission/.local-state/model-live'
APP = ROOT / 'tmall_submission/.local-state/offline-r1/Muse-Tmall-Submission/Muse.app'
STATE = EVIDENCE / 'fresh-state'
spec = importlib.util.spec_from_file_location('remote', ROOT / 'official_muse/phase2/tests/remote.py')
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)


def dump(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def one_file(name):
    found = list(STATE.rglob(name))
    if name == 'ledger.json':
        found = [p for p in found if p.parent.name == 'model']
    if len(found) != 1:
        raise RuntimeError('%s: expected one test file, found %d' % (name, len(found)))
    return found[0]


def process_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def main():
    global APP, STATE, EVIDENCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, default=APP)
    parser.add_argument('--state', type=Path, default=STATE)
    parser.add_argument('--evidence', type=Path, default=EVIDENCE)
    parser.add_argument('--version', default='0.3.26-rc51')
    parser.add_argument('--commit', default='6b46c3c8cc3ea5b5d5d9073224a3b303b8b1d109')
    parser.add_argument('--private-screenshots', action='store_true')
    args = parser.parse_args()
    APP, STATE, EVIDENCE = args.app.resolve(), args.state.resolve(), args.evidence.resolve()
    EVIDENCE.relative_to(ROOT / 'tmall_submission/.local-state')
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    images = EVIDENCE / '.local-state/screenshots' if args.private_screenshots else EVIDENCE
    images.mkdir(parents=True, exist_ok=True)
    image_records = {}
    def shot(name):
        path = images / name
        r.shot(path)
        image_records[name] = dict(path=str(path.relative_to(EVIDENCE)), bytes=path.stat().st_size,
                                   sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if STATE.exists():
        raise RuntimeError('requires a fresh empty profile; prior evidence is preserved')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 8492))
    env = {k: os.environ[k] for k in ('HOME', 'PATH', 'USER', 'TMPDIR', 'LANG') if k in os.environ}
    env.update(MUSE_TMALL_STATE=str(STATE), MUSE_TMALL_REMOTE='8492')
    r = remote.Remote(8492)
    result = dict(status='FAIL', carrier_version=args.version, carrier_commit=args.commit,
                  scope='isolated candidate model verification; not final delivery archive',
                  port=8492, profile_initially_absent=True, fixture=False,
                  real_host_model_complete=False, quality='basic offline fallback; not strong',
                  model='Qwen2.5-0.5B-Instruct-Q4_0-offline', external_actions_performed=False,
                  recipient_machines_tested=False, calls=[])
    child = None
    pid = None
    with (EVIDENCE / 'native-model-launcher.txt').open('w') as log:
        try:
            child = subprocess.Popen([str(APP / 'Contents/MacOS/muse-launcher')],
                                     cwd=APP.parent, env=env, stdout=log, stderr=log)
            for _ in range(240):
                if child.poll() is not None:
                    raise RuntimeError('launcher exited before App Hub appeared')
                try:
                    r.find('action')
                    break
                except Exception:
                    time.sleep(.25)
            else:
                raise RuntimeError('App Hub did not appear')
            metadata = json.loads((STATE / 'local-model.json').read_text())
            pid = metadata['pid']
            profile_path = STATE / 'home/octos-home/.octos/profiles/_main.json'
            profile = json.loads(profile_path.read_text())
            primary = profile['config']['llm']['primary']
            assert primary['model_id'] == result['model']
            assert primary['route']['base_url'] == metadata['base_url'] + '/v1'
            assert profile['config']['env_vars'] == {}
            assert profile_path.stat().st_mode & 0o777 == 0o600
            result['first_configuration'] = dict(primary=primary, enabled=profile['enabled'],
                timestamps_present=all(k in profile for k in ('created_at', 'updated_at')),
                empty_credentials=True, profile_mode='0600', loopback_only=True)
            shot('first-model-apphub.png')
            r.click('action')
            r.click_scroll('confirm', 'list', attempts=20)
            r.click('library')
            for _ in range(60):
                if r.find('action').get('t') == '打开':
                    break
                time.sleep(.2)
            else:
                raise RuntimeError('App Hub install did not reach Open')
            manifest = APP / ('Contents/Resources/mirror/artifacts/muse-goals-' + args.version + '.bundle')
            assert json.loads((manifest / 'manifest.json').read_text())['version'] == args.version
            installed = STATE / 'apps/muse-goals/bundle'
            identities = {}
            for source in manifest.rglob('*'):
                if source.is_file():
                    rel = source.relative_to(manifest)
                    digest = hashlib.sha256((installed / rel).read_bytes()).hexdigest()
                    assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
                    identities[rel.as_posix()] = digest
            result['installed_bundle_sha256'] = identities
            r.click('action')
            r.wait_for('goal_input', seconds=40)
            for index, (question, expected) in enumerate([
                ('请只回答两个汉字：晴朗白天的天空通常是什么颜色？', '蓝色'),
                ('请只回答数字：7加5等于几？', '12')
            ], 1):
                r.set_text('goal_input', question)
                started = time.monotonic()
                r.click('send_button')
                for _ in range(300):
                    traces = list(STATE.rglob('model-last-response.json'))
                    sessions = list(STATE.rglob('chat-sessions.json'))
                    if traces and sessions:
                        trace = json.loads(traces[0].read_text())
                        chats = json.loads(sessions[0].read_text())
                        # Derive the format from the app's real stored session envelope.
                        rows = chats.get('sessions', []) if isinstance(chats, dict) else chats
                        answers = [m for s in rows for m in s.get('messages', []) if m.get('role') == 'assistant']
                        if len(answers) >= index and trace.get('query_sha256') == hashlib.sha256(question.encode()).hexdigest():
                            break
                    time.sleep(.2)
                else:
                    raise RuntimeError('model response was not persisted')
                answer = answers[-1]
                call = dict(question=question, answer=answer, elapsed_seconds=round(time.monotonic()-started, 3), trace=trace)
                result['calls'].append(call)
                result['real_host_model_complete'] = True
                dump('model-call-%d.json' % index, call)
                shot('first-model-reply-%d.png' % index)
                assert trace['is_ok'] and trace['known_usage'], trace
                assert answer['state'] == 'success', answer
                call['answer_correct'] = expected in answer['text']
                dump('model-call-%d.json' % index, call)
                print('model.complete call', index, answer['text'], call['elapsed_seconds'], flush=True)
            result['ledger'] = json.loads(one_file('ledger.json').read_text())
            assert result['calls'][0]['answer']['text'] != result['calls'][1]['answer']['text']
            result['model_complete_status'] = 'PASS'
            result['answer_quality_status'] = 'PASS' if all(c['answer_correct'] for c in result['calls']) else 'FAIL'
            result['status'] = 'PASS' if result['answer_quality_status'] == 'PASS' else 'PARTIAL'
        except Exception as error:
            result['error'] = str(error)
            try:
                dump('first-model-failure.snap.json', r.widgets())
                shot('first-model-failure.png')
            except Exception:
                pass
            raise
        finally:
            if child and child.poll() is None:
                child.terminate()
                child.wait(timeout=25)
            result['launcher_exit_code'] = child.returncode if child else None
            result['own_model_stopped'] = not process_exists(pid) if pid else None
            result['screenshots'] = image_records
            dump('FIRST_MODEL_LIVE.json', result)
            print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
