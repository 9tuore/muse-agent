#!/usr/bin/env python3
"""Complete the second real call after preserving the first Q4 quality failure.

The initial fresh-profile trace remains part of the final result. A wrong answer
does not become a passing accuracy test merely because transport succeeded.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('first_model', E / 'verify_first_model.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def main():
    result = json.loads((E / 'FIRST_MODEL_LIVE.json').read_text())
    assert len(result['calls']) == 1
    result['calls'][0]['answer_correct'] = '蓝色' in result['calls'][0]['answer']['text']
    env = {k: os.environ[k] for k in ('HOME', 'PATH', 'USER', 'TMPDIR', 'LANG') if k in os.environ}
    env.update(MUSE_REPRO_STATE=str(t.STATE), MUSE_REPRO_REMOTE='8492')
    question = '请只回答数字：7加5等于几？'
    r = t.remote.Remote(8492)
    pid = None
    with (E / 'second-model-launcher.txt').open('w') as log:
        child = subprocess.Popen([str(t.APP / 'Contents/MacOS/muse-launcher')], cwd=t.APP.parent,
                                 env=env, stdout=log, stderr=log)
        try:
            for _ in range(240):
                if child.poll() is not None:
                    raise RuntimeError('launcher exited before the remote became available')
                try:
                    r.find('library')
                    break
                except Exception:
                    time.sleep(.2)
            else:
                raise RuntimeError('App Hub remote was not ready')
            r.wait_for('library', seconds=45)
            pid = json.loads((t.STATE / 'local-model.json').read_text())['pid']
            r.click('library')
            r.wait_for('打开', seconds=10)
            r.click('action')
            r.wait_for('goal_input', seconds=40)
            r.set_text('goal_input', question)
            started = time.monotonic()
            r.click('send_button')
            for _ in range(300):
                trace = json.loads(t.one_file('model-last-response.json').read_text())
                sessions = json.loads(t.one_file('chat-sessions.json').read_text())
                answers = [m for s in sessions['sessions'] for m in s['messages'] if m['role'] == 'assistant']
                if len(answers) >= 2 and trace['query_sha256'] == hashlib.sha256(question.encode()).hexdigest():
                    break
                time.sleep(.2)
            else:
                raise RuntimeError('second actual reply was not persisted')
            answer = answers[-1]
            call = dict(question=question, answer=answer, elapsed_seconds=round(time.monotonic()-started, 3),
                        trace=trace, answer_correct='12' in answer['text'])
            result['calls'].append(call)
            t.dump('model-call-2.json', call)
            r.shot(E / 'first-model-reply-2.png')
            assert trace['is_ok'] and trace['known_usage'] and answer['state'] == 'success'
            assert answer['text'] != result['calls'][0]['answer']['text']
            result['ledger'] = json.loads(t.one_file('ledger.json').read_text())
            result['model_complete_status'] = 'PASS'
            result['answer_quality_status'] = 'PASS' if all(c['answer_correct'] for c in result['calls']) else 'FAIL'
            result['status'] = 'PASS' if result['answer_quality_status'] == 'PASS' else 'PARTIAL'
            result.pop('error', None)
        except Exception as error:
            result['error'] = str(error)
            raise
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=25)
            result['launcher_exit_code'] = child.returncode
            result['own_model_stopped'] = not t.process_exists(pid) if pid else None
            t.dump('FIRST_MODEL_LIVE.json', result)
            print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
