#!/usr/bin/env python3
"""Bounded synthetic rc49 Host/model diagnosis. No proxy, paid model or external actions."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
APP = Path('/Users/mima0000/Desktop/Muse-0.3.26-rc49-Intel精简运行与源码-7e2d233b-2026-10-06/Muse 0.3.26-rc49.app')
RES = APP / 'Contents/Resources'
spec = importlib.util.spec_from_file_location('remote', ROOT / 'official_muse/phase2/tests/remote.py')
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)
QUESTIONS = [('请只回答两个汉字：晴朗白天的天空通常是什么颜色？', '蓝色'),
             ('请只回答数字：7加5等于几？', '12')]


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def stop(child):
    if child is None:
        return
    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['baseline', 'baseline-initialized', 'official-nonthinking'], required=True)
    args = parser.parse_args()
    case = E / args.mode
    case.mkdir(exist_ok=False)
    state = case / '.local-state/profile'
    state.mkdir(parents=True)
    if args.mode != 'baseline':
        # Reuse only our earlier synthetic state schema, never Root or production data.
        earlier = ROOT / 'official_muse/rc/submission-ready-20261006-r1/packaging/.local-state/rc48-empty-first-model-r1/apps/muse-goals'
        data = state / 'apps/muse-goals'
        data.mkdir(parents=True)
        for path in earlier.glob('*.json'):
            shutil.copy2(path, data / path.name)
        chats = json.loads((data/'chat-sessions.json').read_text())
        for session in chats['sessions']:
            assert 'focus_owner' in session and 'goal_id' in session
            session['messages'] = []
            session['proposals'] = []
        dump(data/'chat-sessions.json', chats)
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 8492))
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    base = 'http://127.0.0.1:' + str(port)
    alias = 'Qwen3-0.6B-Q4_K_S-pure-offline'
    model_path = RES / 'local-model/Qwen3-0.6B-Q4_K_S-pure.gguf'
    model_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    assert model_sha == 'f755be04e46e7f768edb977e1ffa2ba25295941b69ca943dfb0388cfba4ee71b'
    host_path = RES / 'OctoSense Host.app/Contents/MacOS/octosense'
    assert hashlib.sha256(host_path.read_bytes()).hexdigest() == '1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3'
    sampler = ['--temp', '0.2'] if args.mode.startswith('baseline') else [
        '--temp', '0.7', '--top-p', '0.8', '--top-k', '20', '--min-p', '0', '--presence-penalty', '1.5']
    command = [str(RES / 'local-model/llama/llama-server'), '--model', str(model_path),
        '--host', '127.0.0.1', '--port', str(port), '--alias', alias, '--ctx-size', '4096',
        '--parallel', '1', '--threads', '4', '--gpu-layers', '0', '--offline', '--no-webui',
        *sampler, '--reasoning', 'off', '--chat-template-kwargs', '{"enable_thinking":false}',
        '--log-prompts-dir', str(case / '.local-state/prompts'), '--log-verbosity', '4']
    result = dict(mode=args.mode, carrier_version='0.3.26-rc49', product_commit='e0eb5d82',
        model_sha256=model_sha, model_alias=alias, sampler_arguments=sampler, port=8492,
        scope='existing packaged Host and model, synthetic fresh profile; manual diagnostic server ownership, not automatic launcher test',
        app_state_seed='fresh' if args.mode=='baseline' else 'earlier own synthetic rc48 schema; messages/proposals cleared in copied fixture only',
        paid_models=False, external_actions=False, weights_host_budget_unchanged=True,
        direct=[], host_calls=[], status='FAIL')
    server = host = None
    minimal = {k: os.environ[k] for k in ('HOME', 'USER', 'TMPDIR', 'LANG') if k in os.environ}
    minimal['PATH'] = '/usr/bin:/bin'
    with (case / '.local-state/server.log').open('w') as server_log, (case / '.local-state/host.log').open('w') as host_log:
        try:
            server = subprocess.Popen(command, env=minimal, stdout=server_log, stderr=server_log)
            for _ in range(240):
                if server.poll() is not None:
                    raise RuntimeError('own model server exited')
                try:
                    with urlopen(base + '/health', timeout=1) as reply:
                        if reply.status == 200:
                            break
                except OSError:
                    pass
                time.sleep(.25)
            else:
                raise RuntimeError('model health timeout')
            # The baseline control uses the identical question text, unlike the old direct comparison.
            if args.mode == 'baseline':
                for index, (question, expected) in enumerate(QUESTIONS, 1):
                    body = dict(model=alias, stream=False, messages=[dict(role='user', content=question)])
                    started = time.monotonic()
                    req = Request(base + '/v1/chat/completions', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
                    with urlopen(req, timeout=120) as reply:
                        raw = json.load(reply)
                    text = raw['choices'][0]['message']['content']
                    result['direct'].append(dict(question=question, text=text, semantic_correct=expected in text, format_correct=text.strip() == expected,
                        correct=text.strip()==expected,
                        seconds=round(time.monotonic()-started, 3), usage=raw.get('usage'), raw=raw))
                    dump(case / ('direct-%d.json' % index), result['direct'][-1])
                    print('direct', index, repr(text), flush=True)
            core = state / 'home/octos-home/.octos'
            (core / 'profiles').mkdir(parents=True)
            now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            profile = dict(id='_main', name='Synthetic local model diagnosis', enabled=True,
                created_at=now, updated_at=now, config=dict(env_vars={}, llm=dict(primary=dict(
                    family_id='local', model_id=alias, context_window=4096,
                    route=dict(base_url=base+'/v1', api_type='openai', label='isolated diagnostic')), fallbacks=[])))
            profile_path = core / 'profiles/_main.json'
            dump(profile_path, profile)
            profile_path.chmod(0o600)
            env = dict(minimal, OCTOSENSE_HOME=str(state/'home'), OCTOSENSE_APP_DATA=str(state/'apps'),
                OCTOS_APP_CORE_DIR=str(core), OCTOSENSE_HUB=str(RES/'mirror'),
                OCTOSENSE_HUB_ANCHOR='3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840',
                MAKEPAD_APP_CONFIG='{}', MAKEPAD_REMOTE='8492')
            host = subprocess.Popen([str(host_path), '--test-action', 'launch-apphub'], cwd=host_path.parent,
                                    env=env, stdout=host_log, stderr=host_log)
            r = remote.Remote(8492)
            for _ in range(240):
                if host.poll() is not None:
                    raise RuntimeError('own Host exited')
                try:
                    r.find('action')
                    break
                except (OSError, AssertionError):
                    time.sleep(.25)
            else:
                raise RuntimeError('App Hub timeout')
            r.click('action')
            r.click_scroll('confirm', 'list', attempts=20)
            r.click('library')
            for _ in range(100):
                if r.find('action').get('t') == '打开':
                    break
                time.sleep(.2)
            else:
                raise RuntimeError('install timeout')
            bundle = RES/'mirror/artifacts/muse-goals-0.3.26-rc49.bundle'
            identities = {}
            for p in bundle.rglob('*'):
                if p.is_file():
                    rel=p.relative_to(bundle)
                    data=(state/'apps/muse-goals/bundle'/rel).read_bytes()
                    assert data==p.read_bytes()
                    identities[str(rel)]=hashlib.sha256(data).hexdigest()
            result['installed_bundle_sha256']=identities
            r.click('action')
            r.wait_for('goal_input', seconds=40)
            for index, (question, expected) in enumerate(QUESTIONS, 1):
                r.set_text('goal_input', question)
                started=time.monotonic()
                r.click('send_button')
                for _ in range(600):
                    traces=list(state.rglob('model-last-response.json'))
                    sessions=list(state.rglob('chat-sessions.json'))
                    if traces and sessions:
                        trace=json.loads(traces[0].read_text())
                        rows=json.loads(sessions[0].read_text())['sessions']
                        answers=[m for s in rows for m in s.get('messages',[]) if m.get('role')=='assistant']
                        if len(answers)>=index and trace.get('query_sha256')==hashlib.sha256(question.encode()).hexdigest():
                            break
                    time.sleep(.2)
                else:
                    raise RuntimeError('Host answer timeout')
                call=dict(question=question, answer=answers[-1], trace=trace,
                    semantic_correct=expected in answers[-1]['text'], format_correct=answers[-1]['text'].strip()==expected,
                    correct=answers[-1]['text'].strip()==expected, seconds=round(time.monotonic()-started,3))
                result['host_calls'].append(call)
                dump(case/('host-%d.json' % index),call)
                print('Host model.complete',index,repr(answers[-1]['text']),flush=True)
            ledgers=[p for p in state.rglob('ledger.json') if p.parent.name=='model']
            assert len(ledgers)==1
            result['ledger']=json.loads(ledgers[0].read_text())
            result['status']='PASS' if all(x['correct'] for x in result['host_calls']) else 'PARTIAL'
        except Exception as error:
            result['error']=str(error)
            raise
        finally:
            stop(host)
            stop(server)
            result['own_host_stopped']=host is None or host.poll() is not None
            result['own_model_stopped']=server is None or server.poll() is not None
            result['raw_prompt_log_files']=[str(x.relative_to(case)) for x in (case/'.local-state/prompts').glob('*')]
            dump(case/'RESULT.json',result)
            print(json.dumps({k:result[k] for k in ('status','own_host_stopped','own_model_stopped')},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
