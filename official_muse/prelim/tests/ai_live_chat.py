#!/usr/bin/env python3
"""Frozen original20 + local setup + holdout in a real visible isolated Shell.

Does not launch a Host, prepare a candidate, edit a profile or confirm actions.
Root supplies the immutable candidate, running isolated port and synthetic wire.
All semantic scores remain pending manual review of actual replies and payloads.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import navigate, shot, type_multiline
from ai_paid_guard import KIND as PAID_KIND, PaidGuard, PaidPause, input_bound_check

EXPECTATIONS = Path(__file__).with_name('semantic_expectations.json')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proposal_diff(before, after):
    old = {c['id']: c for c in before}
    new = {c['id']: c for c in after}
    return {'added_ids': sorted(set(new)-set(old)),
            'removed_ids': sorted(set(old)-set(new)),
            'changed_existing': [{'id': key, 'before': old[key], 'after': new[key]}
                                 for key in sorted(set(old)&set(new)) if old[key] != new[key]],
            'unchanged_ids': sorted(key for key in set(old)&set(new) if old[key] == new[key])}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--port', type=int, default=8412)
    ap.add_argument('--wire', type=Path,
                    help='Dedicated synthetic relay log inside this run output; never user wire')
    ap.add_argument('--authorized-model', action='store_true',
                    help='Explicit MiniMax-only authorization mode; no relay or direct provider requests')
    ap.add_argument('--cost-ledger', type=Path,
                    help='Existing Root-initialized global paid accounting table; CNY30 maximum')
    ap.add_argument('--host-app', type=Path)
    ap.add_argument('--host-source', type=Path, help='Root-attested frozen SDK source directory matching --host-app')
    ap.add_argument('--input-contract', type=Path,
                    default=ROOT / 'official_muse/prelim/evidence/ai/paid-runner-preparation/input-bound-contract.json',
                    help='Reviewed immutable chat-only input contract for this candidate')
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--supplemental', type=Path,
                    help='Frozen extra variants appended after all original/setup/holdout cases')
    ap.add_argument('--diagnostic-extra-only', action='store_true',
                    help='Run only the separate frozen repair variants; never counts as original28 acceptance')
    a = ap.parse_args()
    if a.diagnostic_extra_only and not a.supplemental:
        ap.error('--diagnostic-extra-only needs a separately frozen --supplemental file')
    assert a.port not in [8414, 8401], 'User windows are excluded'
    paid = a.authorized_model
    if paid and (a.wire or not a.cost_ledger or not a.host_source):
        ap.error('Authorized mode needs --cost-ledger/--host-source and forbids --wire/relay')
    if not paid and (not a.wire or a.cost_ledger or a.host_source):
        ap.error('Local mode needs --wire and does not use the paid table')
    if paid:
        assert a.port != 8413, 'Root configuration window is excluded'
    candidate, out = a.candidate.resolve(), a.out.resolve()
    wire_path = a.wire.resolve() if a.wire else None
    if not paid:
        assert out in wire_path.parents, 'Wire must belong to this synthetic run output'
    meta = read(candidate / 'candidate.json')
    assert meta['profile_kind'] == (PAID_KIND if paid else 'LOCAL_MODEL_ONLY_SYNTHETIC')
    jail = candidate / 'private/apps/muse-goals'
    host_app = (a.host_app or Path(meta['host_app_path'])).resolve()
    host_binary = host_app / 'Contents/MacOS/octosense'
    assert sha(host_binary) == meta['host_sha256'], 'Host differs from candidate metadata'
    assert not (candidate / 'private/apps/.host/mail').exists(), 'No mailbox state permitted'
    contract_path = a.input_contract.resolve()
    input_contract = read(contract_path) if paid else None
    guard_sha = sha(Path(__file__).with_name('ai_paid_guard.py'))
    contract_sha = sha(contract_path) if paid else None
    paid_guard = PaidGuard(candidate, a.cost_ledger, str(out)) if paid else None
    if paid:
        provider_fields = paid_guard.fields
        assert meta['model_metadata'] == {
            'family_id': provider_fields['family'], 'model_id': provider_fields['model'],
            'base_url': provider_fields['base_url'], 'api_type': provider_fields['api_type']}, 'Frozen model metadata differs from isolated profile'
    else:
        profile = read(candidate / 'private/home/octos-home/.octos/profiles/_main.json')
        llm = profile['config']['llm']
        provider = llm['primary']
        base = urlsplit(provider['route']['base_url'])
        assert provider['family_id'] == 'local' and not llm.get('fallbacks')
        assert base.scheme == 'http' and base.hostname == '127.0.0.1'
        assert not base.username and not base.password and not base.query
        provider_fields = {'family': provider['family_id'], 'model': provider['model_id'],
                           'base_url': provider['route']['base_url']}
    plan = read(EXPECTATIONS)
    original = read(ROOT / plan['original_corpus'])['cases']
    assert sha(ROOT / plan['original_corpus']) == plan['original_corpus_sha256']
    assert [(c['id'], c['input']) for c in plan['cases'] if c['suite'] != 'holdout'] == [
        (c['id'], c['input']) for c in original], 'Original corpus changed or cases omitted'
    assert sum(c['suite'] == 'original20' for c in plan['cases']) == 20
    assert sum(c['suite'] == 'setup' for c in plan['cases']) == 2
    assert sum(c['suite'] == 'holdout' for c in plan['cases']) == 6
    assert len({c['id'] for c in plan['cases']}) == 28
    supplemental_path = a.supplemental.resolve() if a.supplemental else None
    supplemental_sha = sha(supplemental_path) if supplemental_path else None
    if supplemental_path:
        extra = read(supplemental_path)
        assert extra['status'] == 'FROZEN_BEFORE_LIVE_RUN' and extra['cases']
        assert all(c['suite'] == 'supplemental' and c['execution'] == 'model' for c in extra['cases'])
        plan['cases'] = extra['cases'] if a.diagnostic_extra_only else plan['cases'] + extra['cases']
        assert len({c['id'] for c in plan['cases']}) == len(plan['cases']), 'Extra cases cannot replace frozen cases'
    suites = ['supplemental'] if a.diagnostic_extra_only else ['original20', 'setup', 'holdout'] + (['supplemental'] if supplemental_path else [])
    manifest_sha = sha(jail / 'bundle/manifest.json')
    driver_sha = sha(Path(__file__))
    runtime_pids = subprocess.check_output(
        ['lsof', '-t', '-iTCP:'+str(a.port), '-sTCP:LISTEN'], text=True).splitlines()
    assert len(set(runtime_pids)) == 1, 'Expected one isolated Shell listener'
    runtime_pid = runtime_pids[0]
    runtime_executable = subprocess.check_output(
        ['ps', '-p', runtime_pid, '-o', 'comm='], text=True,
        env=dict(os.environ, LC_ALL='en_US.UTF-8', LANG='en_US.UTF-8')).strip()
    assert Path(runtime_executable).resolve() == host_binary.resolve(), 'Port belongs to a different Host'

    def binding_check():
        assert sha(candidate / 'bundle/main.splash') == meta['source_sha256']
        assert sha(jail / 'bundle/main.splash') == meta['source_sha256']
        assert sha(jail / 'bundle/manifest.json') == manifest_sha
        assert sha(host_binary) == meta['host_sha256']
        assert sha(EXPECTATIONS) == expectations_sha
        if supplemental_path:
            assert sha(supplemental_path) == supplemental_sha
        assert sha(Path(__file__)) == driver_sha
        if paid_guard:
            assert sha(Path(__file__).with_name('ai_paid_guard.py')) == guard_sha
            assert sha(contract_path) == contract_sha
            paid_guard.check_profile()

    expectations_sha = sha(EXPECTATIONS)
    binding_check()
    if a.resume:
        report = read(out / 'report.json')
        assert report['source_sha256'] == meta['source_sha256']
        assert report['host_sha256'] == meta['host_sha256']
        assert report['expectations_sha256'] == expectations_sha
        assert report['driver_sha256'] == driver_sha
        assert report.get('supplemental_sha256') == supplemental_sha
        assert report.get('diagnostic_extra_only', False) == a.diagnostic_extra_only
        assert report['port'] == a.port and report['wire_path'] == (str(wire_path) if wire_path else None)
        assert report.get('authorized_model', False) == paid
        if paid:
            assert report['cost_ledger'] == str(a.cost_ledger.resolve())
            assert report['host_source_root_attested'] == str(a.host_source.resolve())
            assert report['input_bound_contract_sha256'] == contract_sha
            assert report['paid_guard_sha256'] == guard_sha
        report['status'] = 'RUNNING'
    else:
        # A Root-owned dedicated relay may already have created the directory;
        # reject previous driver evidence, while retaining relay logs.
        assert not (out / 'report.json').exists() and not (out / 'semantic_expectations.json').exists()
        out.mkdir(parents=True, exist_ok=True)
        (out / 'semantic_expectations.json').write_bytes(EXPECTATIONS.read_bytes())
        if supplemental_path:
            (out / 'supplemental_expectations.json').write_bytes(supplemental_path.read_bytes())
        report = {'kind': 'LIVE_AUTHORIZED_MODEL_VISIBLE_SHELL_SYNTHETIC_DATA' if paid else 'LIVE_LOCAL_MODEL_VISIBLE_SHELL_SYNTHETIC_DATA',
                  'status': 'RUNNING', 'version': meta['version'],
                  'source_sha256': meta['source_sha256'], 'host_sha256': meta['host_sha256'],
                  'manifest_sha256': manifest_sha, 'expectations_sha256': expectations_sha,
                  'supplemental_sha256': supplemental_sha,
                  'diagnostic_extra_only': a.diagnostic_extra_only,
                  'driver_sha256': driver_sha, 'candidate': str(candidate),
                  'runtime_pid': int(runtime_pid), 'runtime_executable': runtime_executable,
                  'helper_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [
                      ROOT / 'official_muse/phase2/tests/remote.py',
                      ROOT / 'official_muse/ui_memory/tests/visual_capture.py',
                      ROOT / 'official_muse/prelim/tests/ai_paid_guard.py']},
                  'port': a.port, 'wire_path': str(wire_path) if wire_path else None,
                  'provider_nonsecret': provider_fields,
                  'cases': [], 'flow_sessions': {}, 'focus_changes': [],
                  'memory_operations': {}, 'started_at': time.time(),
                  'mail_send': False, 'calendar_write': False,
                  'semantic_review': 'PENDING_MANUAL_REVIEW',
                  'count_note': ('Repair diagnostics only. Original28 and T01-T20 acceptance are NOT_RUN in this report.' if a.diagnostic_extra_only else '20 original functional cases include S06 local cancellation; 19 expect model calls. Two setup and six frozen holdout are separate.')}
        if paid:
            report.update({'authorized_model': True, 'cost_ledger': str(a.cost_ledger.resolve()),
                           'profile_sha256': paid_guard.profile_sha,
                           'host_source_root_attested': str(a.host_source.resolve()),
                           'input_bound_contract_sha256': contract_sha, 'paid_guard_sha256': guard_sha,
                           'acceptance_rule': ('Diagnostic results cannot count as original28 or product acceptance.' if a.diagnostic_extra_only else 'All original20 must receive manual semantic PASS; a completed run or partial score is not PASS'),
                           'billing_note': 'CNY30 global cap; conservative usage upper bounds, never an actual invoice'})
    r = Remote(a.port)
    last_model = time.monotonic() if a.resume else 0

    def save():
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def session(sid):
        return next(s for s in read(jail / 'chat-sessions.json')['sessions'] if s['id'] == sid)

    def current():
        value = read(jail / 'chat-sessions.json')
        return next(s for s in value['sessions'] if s['id'] == value['selected_id'])

    def top(area='page_content'):
        x, y, w, h = r.find(area)['r']
        r.scroll(int(x+w-4), int(y+h/2), -10000)

    def switch(sid):
        navigate(r, '对话')
        if current()['id'] == sid:
            return
        title = session(sid)['title']
        top('history_list')
        r.click_scroll(title, 'history_list')
        assert current()['id'] == sid, 'History click did not select intended session'

    def new(label):
        if label in report['flow_sessions']:
            switch(report['flow_sessions'][label])
            return
        navigate(r, '对话')
        previous = current()['id']
        r.click('＋ 新对话')
        deadline = time.monotonic()+5
        while current()['id'] == previous and time.monotonic() < deadline:
            time.sleep(.1)
        assert current()['id'] != previous, 'New session was not saved'
        report['flow_sessions'][label] = current()['id']
        save()

    def focus(case):
        if 'focus' not in case:
            return
        wanted = case['focus']
        before = current()
        # Use actual Chat controls even if this scope was selected earlier.
        if not any(w.get('i') == 'session_focus_project' for w in r.widgets()):
            r.click('切换')
        r.set_text('session_focus_project', wanted['project'])
        r.set_text('session_focus_owner', wanted['owner'])
        controls = [w for w in r.widgets() if w.get('i') in ['session_focus_project', 'session_focus_owner']]
        r.click('使用这个项目')
        after = current()
        assert after['focus_project'] == wanted['project'] and after['focus_owner'] == wanted['owner']
        event = {'case': case['id'], 'session_id': after['id'], 'via': 'REAL_CHAT_FOCUS_UI',
                 'before': {k: before.get(k) for k in ['focus_project', 'focus_owner']},
                 'after': {k: after.get(k) for k in ['focus_project', 'focus_owner']},
                 'input_readback': controls}
        report['focus_changes'].append(event)
        shot(r, out / (case['id']+'-focus.png'))
        save()

    def edit_memory(case):
        key = case['id']
        if key in report['memory_operations']:
            return
        op = case['memory_operation']
        before = read(jail / 'memory.json')
        navigate(r, '记忆')
        r.set_text('memory_search', op['search'])
        top()
        r.click_scroll('更正 / 遗忘', 'page_content')
        top()
        if op['kind'] == 'forget':
            r.click('遗忘…')
            r.click_scroll('确认遗忘这条记忆', 'page_content')
        else:
            type_multiline(r, 'memory_correction', op['replacement'])
            r.click('保存更正')
        after = read(jail / 'memory.json')
        assert before != after, 'Memory UI did not persist a change'
        proof = {'via': 'REAL_MEMORY_UI', 'operation': op, 'before': before, 'after': after}
        (out / (key+'-memory-operation.json')).write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
        report['memory_operations'][key] = {'evidence': key+'-memory-operation.json', 'at': time.time()}
        save()
        navigate(r, '对话')

    def turn(case):
        nonlocal last_model
        key, text = case['id'], case['input']
        binding_check()
        is_model = case['execution'] == 'model'
        if is_model:
            remaining = 32-(time.monotonic()-last_model)
            if remaining > 0:
                time.sleep(remaining)
        origin = current()
        n = len(origin['messages'])
        before_proposals = origin.get('proposals', [])
        wire_before = len(wire_path.read_text().splitlines()) if wire_path and wire_path.exists() else 0
        input_bound = input_bound_check(candidate, origin, text, a.host_source.resolve(), input_contract) if paid else None
        type_multiline(r, 'goal_input', text)
        paid_before = paid_guard.begin(key) if paid_guard else None
        if paid:
            report['remote_inflight'] = {'id': key, 'input': text, 'session_id': origin['id'],
                                         'suite': case['suite'], 'category': case['category'],
                                         'execution_expected': case['execution'], 'transport_expectation_met': False,
                                         'state': 'error', 'wire_requests': 0,
                                         'ledger_before': paid_before, 'input_bound_before_send': input_bound, 'usage_known': False}
            save()
        start = time.monotonic()
        if is_model:
            last_model = start
        warning = None
        try:
            r.click('发送')
        except AssertionError as error:
            accepted = session(origin['id'])
            if len(accepted['messages']) <= n or accepted['messages'][n]['text'] != text:
                raise
            warning = str(error)
        while time.monotonic()-start < 150:
            if paid_guard:
                paid_guard.check_profile()
            after = session(origin['id'])
            if len(after['messages']) >= n+2:
                break
            time.sleep(.25)
        else:
            raise TimeoutError(key+' did not return; remaining cases NOT_RUN, never marked skipped/PASS')
        submitted, answer = after['messages'][n:n+2]
        assert submitted['role'] == 'user' and submitted['text'] == text
        assert answer['role'] == 'assistant'
        records = [json.loads(line) for line in wire_path.read_text().splitlines()[wire_before:]] if wire_path and wire_path.exists() else []
        records = [row for row in records if row['at'] >= submitted['at'] and any(
            m.get('role') == 'user' and m.get('content', '').startswith(text) for m in row.get('messages', []))]
        # user content begins with input, then app context. Never assume context
        # appears inside the task/system message or strip it from saved wire.
        if not paid:
            (out / (key+'-wire.json')).write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')
        trace_path = jail / 'memory-retrieval-last.json'
        trace = read(trace_path) if is_model and trace_path.exists() else None
        after_proposals = after.get('proposals', [])
        delta = proposal_diff(before_proposals, after_proposals)
        item = {'id': key, 'suite': case['suite'], 'category': case['category'],
                'input': text, 'expected': case['expected'],
                'semantic_requirements': case['semantic_requirements'],
                'execution_expected': case['execution'],
                'execution_observed': 'PENDING_OFFICIAL_LEDGER_CALLBACK_PROOF' if paid else 'MODEL_WIRE_OBSERVED' if records else 'NO_MODEL_WIRE_OBSERVED',
                'actual': answer['text'], 'state': answer['state'], 'session_id': origin['id'],
                'focus': {k: after.get(k) for k in ['focus_project', 'focus_owner']},
                'user_at': submitted['at'], 'assistant_at': answer['at'],
                'elapsed_seconds': round(answer['at']-submitted['at'], 3),
                'harness_click_warning': warning, 'wire_requests': len(records),
                'wire_status': [row.get('status') for row in records],
                'wire_evidence': None if paid else key+'-wire.json', 'memory_refs': answer.get('memory_refs', []),
                'retrieval_trace': trace, 'proposals_before': before_proposals,
                'proposals_after': after_proposals, 'proposal_delta': delta,
                'semantic_status': 'PENDING_REVIEW', 'classification': 'pending'}
        if key == 'E04':
            item['same_card_payload_updates'] = [c for c in delta['changed_existing']
                if c['before'].get('payload') != c['after'].get('payload')]
            item['prior_mail_card_ids'] = [c['id'] for c in before_proposals if c.get('action') == 'mail_compose']
        if key == 'D01':
            local_date = datetime.datetime.fromtimestamp(submitted['at'], ZoneInfo('Asia/Shanghai')).date()
            tomorrow = local_date+datetime.timedelta(days=1)
            item['expected_absolute_time'] = {'start': str(tomorrow)+'T15:00:00+08:00',
                                              'end': str(tomorrow)+'T16:00:00+08:00'}
        item['transport_expectation_met'] = bool(records) if is_model else not records
        report['cases'].append(item)
        save()
        if paid_guard:
            try:
                proof = paid_guard.finish(paid_before, text, origin['id'], submitted['at'], is_model)
                item['input_bound_before_send'] = input_bound
                item['official_usage_evidence'] = proof
                item['execution_observed'] = 'OFFICIAL_MODEL_LEDGER_CALLBACK_OBSERVED' if is_model else 'LOCAL_ZERO_LEDGER_INCREMENT'
                item['transport_expectation_met'] = True
                item['model_calls'] = proof['usage_proof']['delta']['calls']
                item['provider_attempts'] = proof['usage_proof'].get('attempts', 0)
                report.pop('remote_inflight', None)
                (out / (key+'-official-usage.json')).write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
                save()
            except PaidPause as error:
                item.update({'semantic_status': 'FAIL', 'classification': 'unverified paid usage',
                             'transport_expectation_met': False, 'usage_known': False,
                             'remote_usage_error': str(error)})
                item['official_usage_evidence'] = paid_guard.last_observation or {'before': paid_before, 'known_usage': False}
                (out / (key+'-official-usage.json')).write_text(json.dumps(item['official_usage_evidence'], ensure_ascii=False, indent=2)+'\n')
                save()
                raise
        shot(r, out / (key+'-chat.png'))
        print(json.dumps({k: item[k] for k in ['id', 'suite', 'actual', 'state', 'wire_requests',
                                             'execution_observed', 'transport_expectation_met']}, ensure_ascii=False), flush=True)

    try:
        save()
        for case in plan['cases']:
            if any(c['id'] == case['id'] for c in report['cases']):
                continue  # Resume retains actual evidence; no original/holdout skip option.
            new(case['flow'])
            focus(case)
            if 'memory_operation' in case:
                edit_memory(case)
            turn(case)
        assert [c['id'] for c in report['cases']] == [c['id'] for c in plan['cases']]
        binding_check()
        state = read(jail / 'goals.json') if (jail / 'goals.json').exists() else {}
        report['actions_after'] = state.get('actions', [])
        report['calendar_receipts_after'] = read(jail / 'calendar-state.json').get('receipts', []) if (jail / 'calendar-state.json').exists() else []
        if paid:
            report['counts'] = {suite: {'cases': sum(c['suite'] == suite for c in report['cases']),
                'model_turns_with_ledger_callback': sum(c['suite'] == suite and c['execution_expected'] == 'model' and c['transport_expectation_met'] for c in report['cases']),
                'local_turns_zero_increment': sum(c['suite'] == suite and c['execution_expected'] != 'model' and c['transport_expectation_met'] for c in report['cases']),
                'model_calls': sum(c.get('model_calls', 0) for c in report['cases'] if c['suite'] == suite),
                'provider_attempts': sum(c.get('provider_attempts', 0) for c in report['cases'] if c['suite'] == suite)}
                for suite in suites}
        else:
            report['counts'] = {suite: {'cases': sum(c['suite'] == suite for c in report['cases']),
                                   'model_turns_with_wire': sum(c['suite'] == suite and c['execution_expected'] == 'model' and c['wire_requests'] > 0 for c in report['cases']),
                                   'local_turns_without_wire': sum(c['suite'] == suite and c['execution_expected'] != 'model' and c['wire_requests'] == 0 for c in report['cases']),
                                   'backend_wire_requests': sum(c['wire_requests'] for c in report['cases'] if c['suite'] == suite)}
                            for suite in suites}
        report['status'] = 'COMPLETED_AWAITING_SEMANTIC_REVIEW'
        report['ended_at'] = time.time()
        report['not_run_cases'] = []
        shot(r, out / 'final-chat.png')
        save()
    except Exception as error:
        if paid_guard:
            had_pending = paid_guard.pending is not None
            try:
                paid_guard.unknown()
            except Exception:
                report['global_accounting_error'] = 'Unsettled reservation; stop all further paid sends and reconcile existing history'
            report['cost_usage_unknown'] = had_pending
            inflight = report.get('remote_inflight')
            if inflight and not any(c['id'] == inflight['id'] for c in report['cases']):
                report['cases'].append(dict(inflight, semantic_status='FAIL', classification='interrupted paid turn; usage unknown', actual=None))
        report['status'] = 'PAUSED_REMOTE_EVIDENCE_OR_BUDGET' if paid else 'ERROR'
        report['error'] = str(error)
        report['not_run_cases'] = [c['id'] for c in plan['cases'] if not any(x['id'] == c['id'] for x in report['cases'])]
        save()
        raise


if __name__ == '__main__':
    main()
