#!/usr/bin/env python3
"""Observe a declared subset of frozen semantic cases through actual Shell UI.

Root must supply an already authorized, running model-only synthetic candidate.
One /click is sent per prompt. A remote error never triggers repeat submission.
Semantic answers require manual review; a terminal success is not semantic PASS.
No profile, mail, calendar or goal confirmation is written by this driver.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import shot


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--case-ids', nargs='+', required=True)
    a = ap.parse_args()
    candidate = a.candidate.resolve(strict=True)
    assert not a.out.exists(), 'Retain old failures; use a fresh output'
    a.out.mkdir(parents=True, mode=0o700)
    meta = read(candidate / 'candidate.json')
    assert meta['profile_kind'] == 'AUTHORIZED_MODEL_ONLY_SYNTHETIC'
    llm = read(candidate / 'private/home/octos-home/.octos/profiles/_main.json')['config']['llm']
    selected_model = llm['primary']
    safe_model = {'family_id': selected_model['family_id'], 'model_id': selected_model['model_id'],
                  'base_url': selected_model['route']['base_url'], 'api_type': selected_model['route']['api_type']}
    assert safe_model == meta['model_metadata'] and llm['fallbacks'] == []
    assert not (candidate / 'private/apps/.host/mail').exists()
    jail = candidate / 'private/apps/muse-goals'
    host = Path(meta['host_app_path']) / 'Contents/MacOS/octosense'
    assert sha(host) == meta['host_sha256']
    assert sha(jail / 'bundle/main.splash') == meta['source_sha256']
    pids = subprocess.check_output(['lsof', '-t', '-iTCP:'+str(a.port),
                                    '-sTCP:LISTEN'], text=True).splitlines()
    assert len(set(pids)) == 1
    corpus = ROOT / 'official_muse/prelim/tests/semantic_expectations.json'
    cases = {c['id']: c for c in read(corpus)['cases']}
    assert len(a.case_ids) == len(set(a.case_ids))
    selected = [cases[key] for key in a.case_ids]
    assert all(c['execution'] == 'model' and not c.get('memory_operation')
               for c in selected), 'No memory mutation in this subset'
    protected = {n: sha(jail / n) for n in [
        'goals.json', 'goals.backup.json', 'calendar-state.json',
        'mail-draft.json', 'mail-watch.json', 'memory.json']}
    usage_path = candidate / 'private/apps/.host/model/ledger.json'
    report = {'status': 'RUNNING', 'kind': 'ACTUAL_VISIBLE_SHELL_CHAT_SUBSET',
              'version': meta['version'], 'source_sha256': meta['source_sha256'],
              'host_sha256': meta['host_sha256'], 'code_commit': meta['commit'],
              'application_commit': meta.get('application_commit', meta['commit']),
              'model_metadata': safe_model, 'fallbacks': [],
              'expectations_sha256': sha(corpus), 'case_ids': a.case_ids,
              'driver_sha256': sha(Path(__file__)), 'cases': [],
              'usage_before': read(usage_path)['apps']['muse-goals'],
              'semantic_review': 'PENDING_MANUAL_REVIEW',
              'not_original20_complete': True, 'external_action_confirmation': False}
    r = Remote(a.port)

    def save():
        (a.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False,
                                                   indent=2)+'\n')

    def current():
        d = read(jail / 'chat-sessions.json')
        return next(s for s in d['sessions'] if s['id'] == d['selected_id'])

    flow = None
    last_request = 0
    save()
    try:
        for case in selected:
            if flow != case['flow']:
                before = current()['id']
                r.click('＋ 新对话')
                assert current()['id'] != before
                flow = case['flow']
            if case.get('focus'):
                wanted = case['focus']
                if not any(w.get('i') == 'session_focus_project' for w in r.widgets()):
                    r.click('切换')
                r.set_text('session_focus_project', wanted['project'])
                r.set_text('session_focus_owner', wanted['owner'])
                r.click('使用这个项目')
                assert current()['focus_project'] == wanted['project']
                assert current()['focus_owner'] == wanted['owner']
            gap = 32 - (time.monotonic() - last_request)
            if gap > 0:
                time.sleep(gap)
            origin = current()
            sid, count = origin['id'], len(origin['messages'])
            usage_before = read(usage_path)['apps']['muse-goals']
            r.set_text('goal_input', case['input'])
            button = r.find('send_button')['r']
            assert button[2] > 2 and button[3] >= 24
            submit_error = None
            last_request = time.monotonic()
            try:
                r.request('/click', x=int(button[0]+button[2]/2),
                          y=int(button[1]+button[3]/2))
            except Exception as error:
                submit_error = repr(error)
            deadline = time.monotonic()+90
            while time.monotonic() < deadline:
                session = next(s for s in read(jail / 'chat-sessions.json')['sessions']
                               if s['id'] == sid)
                added = session['messages'][count:]
                terminal = [m for m in added if m['role'] == 'assistant'
                            and m['state'] in ['success', 'waiting_user', 'error', 'cancelled']]
                if terminal:
                    break
                time.sleep(.25)
            else:
                raise AssertionError('One request did not finish; no repeat permitted')
            users = [m for m in added if m['role'] == 'user']
            assert len(users) == 1 and users[0]['text'] == case['input']
            row = {'id': case['id'], 'input': case['input'],
                   'requirements': case['semantic_requirements'],
                   'reply': terminal[-1], 'session_id': sid,
                   'seconds': time.monotonic()-last_request,
                   'single_input': True, 'submit_remote_error': submit_error,
                   'usage_before': usage_before,
                   'usage_after': read(usage_path)['apps']['muse-goals'],
                   'proposals_before': origin['proposals'],
                   'proposals_after': session['proposals']}
            report['cases'].append(row)
            save()
            print(json.dumps({'id': case['id'], 'state': terminal[-1]['state']},
                             ensure_ascii=False), flush=True)
            shot(r, a.out / (case['id']+'.png'))
            assert terminal[-1]['state'] in ['success', 'waiting_user'], 'Retain actual error response'
        assert all(sha(jail / n) == h for n, h in protected.items())
        report['protected_external_state_unchanged'] = True
        report['status'] = 'OBSERVED_REQUIRES_MANUAL_SEMANTIC_REVIEW'
    except Exception:
        report['status'] = 'FAIL_RETAINED'
        (a.out / 'exception.txt').write_text(traceback.format_exc())
        raise
    finally:
        report['usage_after'] = read(usage_path)['apps']['muse-goals']
        (a.out / 'log.json').write_bytes(r.request('/log', n=400))
        (a.out / 'snap.json').write_bytes(r.request('/snap'))
        save()


if __name__ == '__main__':
    main()
