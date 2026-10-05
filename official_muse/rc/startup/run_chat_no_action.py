#!/usr/bin/env python3
"""Observe frozen semantic cases through actual Shell UI.

Root must supply an already authorized, running model-only synthetic candidate.
One /click is sent per prompt. A remote error never triggers repeat submission.
Semantic answers require manual review; a terminal success is not semantic PASS.
Full-corpus mode also uses the existing real synthetic-memory setup/edit UI.
No profile, mail, calendar or goal confirmation is written by this driver.
"""
import argparse
import ctypes
import ctypes.util
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
from visual_capture import navigate, shot, type_multiline


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    choice = ap.add_mutually_exclusive_group(required=True)
    choice.add_argument('--case-ids', nargs='+')
    choice.add_argument('--full-frozen-corpus', action='store_true',
                        help='Original20 + two real UI memory setup steps + six holdouts')
    ap.add_argument('--resume-report', type=Path,
                    help='Resume only the unobserved suffix; preserve the original failed report')
    ap.add_argument('--continue-on-model-error', action='store_true',
                    help='Record a bound Host error as FAIL and observe later cases without replay')
    ap.add_argument('--no-case-screenshots', action='store_true',
                    help='Retain disk-backed semantics/trace; take final native page shots separately')
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
    r = Remote(a.port)
    assert str(json.loads(r.request('/s'))['pid']) == pids[0]
    # macOS ps/lsof escape non-ASCII paths; libproc returns the real UTF-8 path.
    library = ctypes.CDLL(ctypes.util.find_library('proc'))
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    executable = ctypes.create_string_buffer(4096)
    assert library.proc_pidpath(int(pids[0]), executable, len(executable)) > 0
    assert Path(executable.value.decode('utf8')).resolve() == host.resolve()
    corpus = ROOT / 'official_muse/prelim/tests/semantic_expectations.json'
    plan = read(corpus)
    cases = {c['id']: c for c in plan['cases']}
    if a.full_frozen_corpus:
        original_path = Path(__file__).with_name('frozen_original_chat_inputs.json')
        original = read(original_path)
        assert original['original_corpus_sha256'] == plan['original_corpus_sha256']
        assert [(c['id'], c['input']) for c in plan['cases'] if c['suite'] != 'holdout'] == [
            (c['id'], c['input']) for c in original['cases']]
        assert len(cases) == 28
        assert {suite: sum(c['suite'] == suite for c in plan['cases'])
                for suite in ['original20', 'setup', 'holdout']} == {
                    'original20': 20, 'setup': 2, 'holdout': 6}
        selected = plan['cases']
    else:
        assert len(a.case_ids) == len(set(a.case_ids))
        selected = [cases[key] for key in a.case_ids]
        assert all(c['execution'] == 'model' and not c.get('memory_operation')
                   for c in selected), 'No memory mutation in this subset'
    previous = None
    prior_rows = []
    prior_paths = []
    if a.resume_report:
        assert a.full_frozen_corpus, 'Resume uses the fixed original corpus order'
        previous_path = a.resume_report.resolve(strict=True)
        assert previous_path.is_relative_to(candidate)
        previous = read(previous_path)
        chain_path = previous_path
        while True:
            assert chain_path.is_relative_to(candidate) and chain_path not in prior_paths
            prior_paths.append(chain_path)
            segment = read(chain_path)
            for key in ['version', 'source_sha256', 'host_sha256']:
                assert segment[key] == meta[key]
            assert segment['model_metadata'] == safe_model
            assert segment['expectations_sha256'] == sha(corpus)
            assert segment['original_inputs_fixture_sha256'] == sha(original_path)
            assert not segment.get('pending_input'), 'Do not replay an uncertain pending input'
            prior_rows = segment['cases'] + prior_rows
            parent = segment.get('prior_report')
            if not parent:
                break
            chain_path = (candidate / parent['path']).resolve(strict=True)
            assert sha(chain_path) == parent['sha256']
        seen = [row['id'] for row in prior_rows]
        assert seen == [c['id'] for c in selected[:len(seen)]]
        assert all(row['input'] == case['input'] for row, case in
                   zip(prior_rows, selected))
        selected = selected[len(seen):]
        assert selected, 'All fixed inputs have already been observed'
    protected = {n: sha(jail / n) for n in [
        'goals.json', 'goals.backup.json', 'calendar-state.json',
        'mail-draft.json', 'mail-watch.json'] + ([] if a.full_frozen_corpus else ['memory.json'])}
    usage_path = candidate / 'private/apps/.host/model/ledger.json'
    report = {'status': 'RUNNING', 'kind': 'ACTUAL_VISIBLE_SHELL_FROZEN28' if a.full_frozen_corpus else 'ACTUAL_VISIBLE_SHELL_CHAT_SUBSET',
              'version': meta['version'], 'source_sha256': meta['source_sha256'],
              'host_sha256': meta['host_sha256'], 'code_commit': meta['commit'],
              'application_commit': meta.get('application_commit', meta['commit']),
              'model_metadata': safe_model, 'fallbacks': [],
              'expectations_sha256': sha(corpus), 'case_ids': [c['id'] for c in selected],
              'driver_sha256': sha(Path(__file__)), 'cases': [],
              'runtime_pid': int(pids[0]), 'runtime_host_path_verified': True,
              'original_inputs_fixture_sha256': sha(Path(__file__).with_name('frozen_original_chat_inputs.json')),
              'usage_before': read(usage_path)['apps']['muse-goals'],
              'semantic_review': 'PENDING_MANUAL_REVIEW',
              'not_original20_complete': True,
              'not_original20_complete_scope': 'Semantic acceptance is not claimed by this observer',
              'original20_transport_complete': False, 'external_action_confirmation': False,
              'case_screenshots': not a.no_case_screenshots,
              'full_frozen_corpus': a.full_frozen_corpus,
              'flow_sessions': previous['flow_sessions'] if previous else {},
              'memory_operations': previous['memory_operations'] if previous else {},
              'prior_report': {'path': str(previous_path.relative_to(candidate)),
                               'sha256': sha(previous_path)} if previous else None,
              'continue_on_model_error': a.continue_on_model_error,
              'retained_model_errors': []}
    def save():
        pending = a.out / 'report.json.pending'
        pending.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        pending.replace(a.out / 'report.json')

    def current():
        d = read(jail / 'chat-sessions.json')
        return next(s for s in d['sessions'] if s['id'] == d['selected_id'])

    def top(area):
        x, y, width, height = r.find(area)['r']
        r.scroll(int(x+width-4), int(y+height/2), -10000)

    def select_flow(flow):
        navigate(r, '对话')
        if flow in report['flow_sessions']:
            sid = report['flow_sessions'][flow]
            if current()['id'] != sid:
                old = next(s for s in read(jail / 'chat-sessions.json')['sessions']
                           if s['id'] == sid)
                top('history_list')
                r.click_scroll(old['title'], 'history_list')
                assert current()['id'] == sid
            return
        before = current()['id']
        r.click('＋ 新对话')
        assert current()['id'] != before
        report['flow_sessions'][flow] = current()['id']
        save()

    def memory_operation(case):
        op = case['memory_operation']
        before = read(jail / 'memory.json')
        navigate(r, '记忆')
        r.set_text('memory_search', op['search'])
        top('page_content')
        action_errors = []
        def click_once(key):
            for _ in range(16):
                try:
                    widget = r.find(key)
                    x, y, width, height = widget['r']
                    if width >= 2 and height >= 24:
                        break
                except AssertionError:
                    pass
                x, y, width, height = r.find('page_content')['r']
                r.scroll(int(x+width-4), int(y+height/2), 80)
            else:
                raise AssertionError('Memory control not reachable: '+key)
            try:
                r.request('/click', x=int(x+width/2), y=int(y+height/2), wait=1)
            except Exception as error:
                action_errors.append({'control': key, 'error': repr(error), 'no_repeat': True})
        def selected_matches():
            return any(w.get('i') == 'memory_correction' and op['search'] in w.get('val', '')
                       for w in r.widgets())
        if not selected_matches():
            click_once('更正 / 遗忘')
        r.wait_for('memory_correction')
        assert selected_matches(), 'Memory selection does not match the requested record'
        top('page_content')
        if op['kind'] == 'forget':
            click_once('遗忘…')
            r.wait_for('确认遗忘这条记忆')
            click_once('确认遗忘这条记忆')
        else:
            assert op['kind'] == 'correct'
            type_multiline(r, 'memory_correction', op['replacement'])
            click_once('保存更正')
        after = read(jail / 'memory.json')
        assert before != after, 'Actual memory UI did not persist the change'
        proof = a.out / (case['id']+'-memory-operation.json')
        proof.write_text(json.dumps({'via': 'REAL_MEMORY_UI', 'operation': op,
                                    'before': before, 'after': after,
                                    'single_click_errors': action_errors},
                                   ensure_ascii=False, indent=2)+'\n')
        report['memory_operations'][case['id']] = {'path': proof.name, 'sha256': sha(proof)}
        save()
        navigate(r, '对话')

    last_request = 0
    save()
    try:
        for case in selected:
            select_flow(case['flow'])
            if case.get('focus'):
                wanted = case['focus']
                if (current()['focus_project'], current()['focus_owner']) != (
                        wanted['project'], wanted['owner']):
                    if not any(w.get('ty') == 'Button' and w.get('t') == '使用这个项目'
                               for w in r.widgets()):
                        r.click('切换')
                    r.wait_for('使用这个项目')
                    r.set_text('session_focus_project', wanted['project'])
                    r.set_text('session_focus_owner', wanted['owner'])
                    r.click('使用这个项目')
                assert current()['focus_project'] == wanted['project']
                assert current()['focus_owner'] == wanted['owner']
            if case.get('memory_operation'):
                if previous and case['id'] in previous['memory_operations']:
                    op = previous['memory_operations'][case['id']]
                    proof = next(path.parent / op['path'] for path in prior_paths
                                 if sha(path.parent / op['path']) == op['sha256'])
                    assert sha(proof) == op['sha256']
                    assert read(jail / 'memory.json') == read(proof)['after']
                else:
                    memory_operation(case)
            is_model = case['execution'] == 'model'
            if is_model:
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
            submit_ack = None
            report['pending_input'] = {'id': case['id'], 'session_id': sid,
                'messages_before': count, 'usage_before': usage_before,
                'input_sha256': hashlib.sha256(case['input'].encode()).hexdigest(),
                'button_rect': button, 'single_attempt': True}
            save()
            submitted_at = time.monotonic()
            if is_model:
                last_request = submitted_at
            try:
                submit_ack = json.loads(r.request('/click', x=int(button[0]+button[2]/2),
                          y=int(button[1]+button[3]/2), wait=1))
            except Exception as error:
                submit_error = repr(error)
            report['pending_input']['submit_ack'] = submit_ack
            report['pending_input']['submit_remote_error'] = submit_error
            save()
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
                   'seconds': time.monotonic()-submitted_at,
                   'suite': case['suite'], 'execution': case['execution'],
                   'focus': {key: session.get(key) for key in ['focus_project', 'focus_owner']},
                   'single_input': True, 'submit_remote_error': submit_error,
                   'submit_ack': submit_ack,
                   'usage_before': usage_before,
                   'usage_after': read(usage_path)['apps']['muse-goals'],
                   'proposals_before': origin['proposals'],
                   'proposals_after': session['proposals']}
            retrieval_path = jail / 'memory-retrieval-last.json'
            row['retrieval_trace'] = read(retrieval_path) if is_model and retrieval_path.is_file() else None
            trace_path = jail / 'model-last-response.json'
            trace = read(trace_path) if trace_path.is_file() else None
            if is_model and trace and trace.get('query_sha256') == hashlib.sha256(case['input'].encode()).hexdigest() and trace.get('session_id') == sid:
                row['actual_host_trace'] = trace
                row['actual_host_trace_sha256'] = sha(trace_path)
            else:
                row['actual_host_trace'] = None
            report['cases'].append(row)
            report.pop('pending_input', None)
            save()
            print(json.dumps({'id': case['id'], 'state': terminal[-1]['state']},
                             ensure_ascii=False), flush=True)
            if not a.no_case_screenshots:
                shot(r, a.out / (case['id']+'.png'))
            if is_model:
                if terminal[-1]['state'] == 'error' and a.continue_on_model_error:
                    assert row['actual_host_trace'] is not None, 'Bound failure trace missing'
                    assert row['actual_host_trace']['is_ok'] is False
                    report['retained_model_errors'].append(case['id'])
                    save()
                    continue
                assert terminal[-1]['state'] in ['success', 'waiting_user'], 'Retain actual error response'
                assert row['actual_host_trace'] is not None, 'Actual official callback proof missing'
                assert row['actual_host_trace']['is_ok'] is True
                assert row['actual_host_trace']['known_usage'] is True
            else:
                assert row['usage_before'] == row['usage_after'], 'Local mechanism called a model'
                assert terminal[-1]['state'] in ['success', 'waiting_user', 'cancelled']
        assert all(sha(jail / n) == h for n, h in protected.items())
        report['protected_external_state_unchanged'] = True
        all_rows = prior_rows + report['cases']
        report['original20_transport_complete'] = (a.full_frozen_corpus and
            sum(row['suite'] == 'original20' for row in all_rows) == 20)
        report['status'] = ('OBSERVED_WITH_RETAINED_MODEL_ERRORS_REQUIRES_MANUAL_REVIEW'
            if report['retained_model_errors'] or (previous and previous['status'] == 'FAIL_RETAINED')
            else 'OBSERVED_REQUIRES_MANUAL_SEMANTIC_REVIEW')
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
