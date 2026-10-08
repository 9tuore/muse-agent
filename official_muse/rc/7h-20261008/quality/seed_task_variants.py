#!/usr/bin/env python3
"""Exact pinned Shell bundle, isolated synthetic nonempty task-store variants."""
import argparse, copy, hashlib, json, shutil
from pathlib import Path
Q = Path(__file__).resolve().parent
SHA = 'cceeaa009f029c951d8e0a61a8a1cf0ac91802746868d2f38d3de892a889be78'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--case', choices=['valid','backup','bad-run','bad-action','run-backup','action-backup'], required=True)
    a = p.parse_args()
    base = a.base.resolve(); out = Q/'runtime'/a.name
    assert base.is_relative_to(Q/'runtime') and not out.exists()
    m = json.loads((base/'candidate.json').read_text())
    assert m['source_sha256'] == SHA and m['profile_kind'] == 'LOCAL_MODEL_ONLY_SYNTHETIC'
    shutil.copytree(base, out, ignore=shutil.ignore_patterns('build','run'))
    jail = out/'private/apps/muse-goals'
    assert hashlib.sha256((jail/'bundle/main.splash').read_bytes()).hexdigest() == SHA
    gid = 'quality-goal-persisted'; path = 'results/result-quality-goal-persisted.json'
    title = '质量验收：恢复非空中文目标'
    spec = dict(schema_version='muse.goal/0.1',goal_id=gid,revision=1,title=title,objective=title,
        priority='normal',deadline=None,timezone='UTC',
        triggers=[dict(kind='event',topic='user.message',source_ref='muse.ui')],
        context_refs=[dict(ref='ui.source_input',purpose='用户在当前任务输入的资料')],
        steps=[dict(id='write-result',capability='storage.write',args=dict(path=path),input_refs=['ui.source_input'])],
        permissions=dict(capabilities=['storage.write'],resource_refs=[path],send_message='deny',send_rule_ref=None,cloud_context='none'),
        budget=dict(period='goal',money=dict(mode='capped',currency='CNY',amount=0),max_model_tokens=0,max_searches=0,max_run_seconds=60),
        verification=[dict(type='file_content',target_ref=path,expected=dict(task_id=gid))],
        notify=dict(on_major_update=False,on_need_decision=True,on_complete=True),failure_policy=dict(max_retries=1,escalate=True))
    chat = json.loads((jail/'chat-sessions.json').read_text())
    current = next(s for s in chat['sessions'] if s['id']==chat['selected_id'])
    goal = dict(schema=1,id=gid,version=1,goal=title,project_id=current['focus_project'],owner_id=current['focus_owner'],
        source='中文资料甲；中文资料乙',items=['中文资料甲','中文资料乙'],status='planned',approved_at=0,
        model_summary='',result_path=path,updated_at=1,archived=False,goal_spec=spec)
    run = dict(id='quality-prior-run',goal_id=gid,request_id='quality-no-external-action',status='failed',
        result_path=path,plan_revision=1,started_at=1,finished_at=2)
    action = dict(id='quality-prior-action',goal_id=gid,run_id=run['id'],service='storage.write',
        target_scope=path,payload_json='{}',status='failed',plan_revision=1,started_at=1,finished_at=2)
    good = dict(schema=2,goals=[goal],runs=[run],actions=[action],selected_id=gid)
    bad = copy.deepcopy(good)
    if a.case == 'backup': bad['goals'] = 'not-an-array'
    if a.case in ['bad-run','run-backup']: bad['runs'][-1]['plan_revision'] = 'not-a-number'
    if a.case in ['bad-action','action-backup']: bad['actions'][-1]['payload_json'] = {}
    backup = a.case in ['backup','run-backup','action-backup']
    (jail/'goals.json').write_text(json.dumps(good if a.case=='valid' else bad,ensure_ascii=False,separators=(',',':')))
    (jail/'goals.backup.json').write_text(json.dumps(good if backup or a.case=='valid' else bad,ensure_ascii=False,separators=(',',':')))
    current['goal_id'] = gid
    for name in ['chat-sessions.json','chat-sessions.backup.json']:
        (jail/name).write_text(json.dumps(chat,ensure_ascii=False,separators=(',',':')))
    m.update(runtime_private_path=str(out/'private'),test_case=a.case,expected_goal_title=title if a.case=='valid' or backup else None,
             expected_goal_card=a.case=='valid' or backup,seed_kind='SYNTHETIC_ONLY',seed_description='One planned goal, one prior failed run/action; no executable approvals or in-flight actions')
    (out/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(candidate=str(out),case=a.case,source_sha256=SHA),ensure_ascii=False))

if __name__ == '__main__': main()
