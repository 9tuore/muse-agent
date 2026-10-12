#!/usr/bin/env python3
"""Frozen pure local-run projection in the existing ScriptVM; synthetic records."""
import argparse, copy, hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path
H=Path(__file__).resolve().parent
SHA=lambda b:hashlib.sha256(b).hexdigest()

def cases():
    goal=dict(id='fixture-goal',goal='合成本地资料',version=2,status='completed',project_id='fixture-project',owner_id='fixture-owner',result_path='results/fixture-v2.json',goal_spec=dict(goal_id='fixture-goal',revision=2,steps=[dict(capability='storage.write',args=dict(path='results/fixture-v2.json'))]))
    run=dict(id='fixture-run',goal_id=goal['id'],plan_revision=2,status='completed',result_path=goal['result_path'],started_at=100,finished_at=200)
    activity=dict(kind='readback',goal_id=goal['id'],run_id=run['id'],at=150)
    base=dict(goal=goal,runs=[run],activity=[activity],core_storage_ready=True,core_activity_ready=True,gm_ready=True,project='fixture-project',owner='fixture-owner',accounts=['local','fixture-mail'],page='Chat',sessions=[dict(id='fixture-chat',focus_project='fixture-project',focus_owner='fixture-owner',goal_id=goal['id'])],selected_id='',selected_chat='',actions=[],calendar_links=[],calendar_receipts=[],extra_goals=[])
    rows=[]
    def add(name,mut=lambda x:None,proof=False,visible=True,verified=False,**extra):
        x=copy.deepcopy(base);mut(x); rows.append(dict(name=name,input=x,expected=dict(proof=proof,visible=visible,verified=verified,**({'local_nodes':1 if verified else 0}|extra))))
    add('valid-local-completed-readback',proof=True,verified=True)
    for status in ['planned','failed','unknown','accepted','running']:
        add('goal-status-'+status,lambda x,s=status:x['goal'].update(status=s))
        add('run-status-'+status,lambda x,s=status:x['runs'][0].update(status=s))
    for field,value in [('goal_id','wrong-goal'),('id',''),('plan_revision',1),('plan_revision','2'),('result_path','results/wrong.json'),('started_at','100'),('finished_at','200'),('started_at',201),('started_at',-1)]:
        add('run-'+field+'-'+str(value),lambda x,f=field,v=value:x['runs'][0].update({f:v}))
    for field,value in [('goal_id','wrong-goal'),('run_id','wrong-run'),('kind','write'),('at',99),('at',201),('at','150'),('at',-1)]:
        add('readback-'+field+'-'+str(value),lambda x,f=field,v=value:x['activity'][0].update({f:v}))
    add('missing-readback',lambda x:x.update(activity=[]))
    add('missing-readback-time',lambda x:x['activity'][0].pop('at'))
    add('nil-run',lambda x:x.update(runs=[None]))
    add('missing-run-goal',lambda x:x['runs'][0].pop('goal_id'))
    add('missing-run-version',lambda x:x['runs'][0].pop('plan_revision'))
    add('spec-empty-steps',lambda x:x['goal']['goal_spec'].update(steps=[]))
    add('spec-wrong-steps-type',lambda x:x['goal']['goal_spec'].update(steps={}))
    add('spec-wrong-args-type',lambda x:x['goal']['goal_spec']['steps'][0].update(args=[]))
    add('empty-current-project',lambda x:x.update(project=''),proof=True,visible=False)
    add('empty-current-owner',lambda x:x.update(owner=''),proof=True,visible=False)
    add('activity-unready',lambda x:x.update(core_activity_ready=False))
    add('activity-wrong-type',lambda x:x.update(activity={}))
    for at in [100,200]:add('inclusive-at-'+str(at),lambda x,a=at:x['activity'][0].update(at=a),proof=True,verified=True)
    add('missing-run-time',lambda x:x['runs'][0].pop('finished_at'))
    add('goal-wrong-result-path',lambda x:x['goal'].update(result_path='results/wrong.json'))
    add('goal-empty-result-path',lambda x:x['goal'].update(result_path=''))
    add('goal-bad-version',lambda x:x['goal'].update(version='2'),visible=False)
    add('spec-wrong-goal',lambda x:x['goal']['goal_spec'].update(goal_id='wrong-goal'))
    add('spec-old-revision',lambda x:x['goal']['goal_spec'].update(revision=1))
    add('spec-wrong-path',lambda x:x['goal']['goal_spec']['steps'][0]['args'].update(path='wrong'))
    add('spec-missing-args',lambda x:x['goal']['goal_spec']['steps'][0].pop('args'))
    add('spec-two-steps',lambda x:x['goal']['goal_spec']['steps'].append(copy.deepcopy(x['goal']['goal_spec']['steps'][0])))
    add('spec-missing',lambda x:x['goal'].pop('goal_spec'))
    for cap in ['mail.send','calendar.create','calendar.add_event']:
        add('nonlocal-spec-'+cap,lambda x,c=cap:x['goal']['goal_spec']['steps'][0].update(capability=c),local_nodes=0)
    add('mail-source-never-local',lambda x:x['goal'].update(mail_source=dict(account_id='fixture-mail',message_id='fixture-message')),local_nodes=0)
    for field,val in [('project_id','other-project'),('owner_id','other-owner')]:
        add('scope-'+field,lambda x,f=field,v=val:x['goal'].update({f:v}),proof=True,visible=False)
    add('scope-revoked-local',lambda x:x.update(accounts=['fixture-mail']),proof=True,visible=False)
    add('scope-session-owner',lambda x:x['sessions'][0].update(focus_owner='other-owner'),proof=True,visible=False)
    add('scope-session-project',lambda x:x['sessions'][0].update(focus_project='other-project'),proof=True,visible=False)
    add('scope-wrong-chat-goal',lambda x:x['sessions'][0].update(goal_id='wrong-goal'),proof=True,visible=False)
    add('unready-storage',lambda x:x.update(core_storage_ready=False),proof=True,visible=False)
    add('unready-memory',lambda x:x.update(gm_ready=False),proof=True,visible=False)
    add('scope-selected-forbidden',lambda x:(x.update(selected_id='forbidden',selected_chat='fixture-chat'),x['extra_goals'].append(dict(id='forbidden',goal='不可见',version=1,project_id='fixture-project',owner_id='other-owner',status='completed'))),proof=True,visible=False)
    add('selection-other-chat-ignored',lambda x:x.update(selected_id='forbidden',selected_chat='another-chat'),proof=True,verified=True)
    add('goal-detail-parent-scope',lambda x:(x.update(page='Goal Detail'),x['goal'].update(owner_id='other-owner')),proof=True,visible=False)
    add('activity-last64-bound',lambda x:x['activity'].extend([dict(kind='noise') for _ in range(64)]))
    add('run-last64-bound',lambda x:x.update(runs=x['runs']+[dict(id='other-'+str(i),goal_id='other-goal',plan_revision=2,status='completed') for i in range(64)]),proof=True,verified=False,local_nodes=0,limited=True)
    def many(x):
        x['runs']=[dict(copy.deepcopy(run),id='run-'+str(i)) for i in range(6)]
        x['activity']=[dict(copy.deepcopy(activity),run_id='run-'+str(i)) for i in range(6)]
    add('four-local-runs-and-readbacks',many,proof=True,verified=True,local_nodes=4,execution_nodes=4,node_count=9)
    def capped(x):
        many(x)
        x['actions']=[dict(id='action-'+str(i),goal_id=goal['id'],plan_revision=2,status='accepted',service='fixture') for i in range(6)]
        x['calendar_receipts']=[dict(goal_id=goal['id'],request_id='receipt-'+str(i),status='unknown',service='fixture') for i in range(3)]
    add('global-twelve-node-cap',capped,proof=True,verified=True,node_count=12,local_nodes=2,limited=True)
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--vm',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    (out/'parent-command.json').write_text(json.dumps([sys.executable,*sys.argv],indent=2)+'\n')
    raw=a.source.read_bytes();src=raw.decode();(out/'frozen-main.splash').write_bytes(raw)
    # Same previously inspected repository parser, copied into report by hash.
    parser=H.parents[3]/'official_muse/prelim/tests/calendar_sync/run.py'
    spec=importlib.util.spec_from_file_location('source_parser',parser);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    funcs=mod.functions_in(src)
    adapters={
      'calendar_agent_project':'fn calendar_agent_project(view,goal){fixture_adapter_calls=fixture_adapter_calls+1 return false}',
      'chat_refs_valid':'fn chat_refs_valid(refs){fixture_unexpected=fixture_unexpected+1 return false}',
      'chat_reply_context_valid':'fn chat_reply_context_valid(reply){fixture_unexpected=fixture_unexpected+1 return false}',
      'mail_calendar_current':'fn mail_calendar_current(draft){fixture_unexpected=fixture_unexpected+1 return false}',
      'calendar_link_index':'fn calendar_link_index(goal_id){fixture_unexpected=fixture_unexpected+1 return -1}',
      'mail_reply_matches':'fn mail_reply_matches(intent,body){fixture_unexpected=fixture_unexpected+1 return false}'}
    selected={'ac_local_run_readback','ac_projection'}
    while True:
        more=set(selected)
        for n in selected:more|=set(re.findall(r'(?<!\.)\b([A-Za-z_]\w*)\s*\(',adapters.get(n,funcs[n]))) & funcs.keys()
        if more==selected:break
        selected=more
    glob={}
    for m in re.finditer(r'^let ([A-Za-z_]\w*)\s*=',src,re.M):
        pos=m.end();depth=0;quoted=False;escaped=False
        while pos<len(src):
            c=src[pos]
            if quoted:
                if escaped:escaped=False
                elif c=='\\':escaped=True
                elif c=='"':quoted=False
            elif c=='"':quoted=True
            elif c in '{[(':depth+=1
            elif c in '}])':depth-=1
            elif c=='\n' and depth==0:break
            pos+=1
        glob[m[1]]=src[m.start():pos]
    body='\n'.join(adapters.get(n,funcs[n]) for n in sorted(selected,key=lambda n:src.index(funcs[n])))
    wanted=set(re.findall(r'\b[A-Za-z_]\w*\b',body))&glob.keys()
    while True:
        more=wanted|(set(re.findall(r'\b[A-Za-z_]\w*\b','\n'.join(glob[n] for n in wanted)))&glob.keys())
        if more==wanted:break
        wanted=more
    rows=cases();(out/'cases.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    probe='''
let fixture_rows=__ROWS__.parse_json()
let fixture_results=[]
for row in fixture_rows {
 let x=row.input
 core_storage_ready=x.core_storage_ready core_activity_ready=x.core_activity_ready gm_ready=x.gm_ready
 gm_project=x.project gm_owner=x.owner gm_accounts=x.accounts goals=[x.goal]
 for g in x.extra_goals {goals.push(g)}
 runs=x.runs activity=x.activity actions=x.actions
 calendar_links=x.calendar_links calendar_receipts=x.calendar_receipts calendar_conflicts=[] calendar_selected_goal=""
 chat_sessions=x.sessions chat_selected_id="fixture-chat" page=x.page task=x.goal
 ac_selected_id=x.selected_id ac_selected_chat=x.selected_chat
 mail_draft={account:"" link_goal_id:""} mail_watch={alerts:[]} mail_accounts=[{id:"fixture-mail"}]
 let before={goals:goals runs:runs activity:activity actions:actions sessions:chat_sessions calendar_links:calendar_links calendar_receipts:calendar_receipts}.to_json()
 let direct_run=x.runs[0]
 let proof=ac_local_run_readback(x.goal,direct_run)
 let view=ac_projection()
 let after={goals:goals runs:runs activity:activity actions:actions sessions:chat_sessions calendar_links:calendar_links calendar_receipts:calendar_receipts}.to_json()
 fixture_results.push({name:row.name proof:proof view:view unchanged:before==after})
}
({cases:fixture_results unexpected_branch_calls:fixture_unexpected adapter_calls:fixture_adapter_calls}).to_json()
'''.replace('__ROWS__',json.dumps(json.dumps(rows,ensure_ascii=False),ensure_ascii=False))
    prepared='use mod.math.*\nuse mod.std.*\nlet fixture_unexpected=0 let fixture_adapter_calls=0\n'+'\n'.join(glob[n] for n in sorted(wanted,key=lambda n:src.index(glob[n])))+'\n'+body+'\n'+probe
    executed=out/'executed.splash';executed.write_text(prepared)
    identity=dict(source_path=str(a.source.resolve()),source_sha256=SHA(raw),vm_path=str(a.vm.resolve()),vm_sha256=SHA(a.vm.read_bytes()),executed_sha256=SHA(prepared.encode()),runner_sha256=SHA(Path(__file__).read_bytes()),parser_sha256=SHA(parser.read_bytes()),production_functions={n:SHA(funcs[n].encode()) for n in selected if n not in adapters},production_globals={n:SHA(glob[n].encode()) for n in wanted},fixture_adapters={n:adapters[n] for n in selected&adapters.keys()},fixture_data=True)
    (out/'identity.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n')
    cmd=[str(a.vm.resolve()),str(executed),'--rpc'];(out/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
    proc=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
    (out/'stdout.log').write_text(proc.stdout);(out/'stderr.log').write_text(proc.stderr)
    report=dict(status='ERROR',returncode=proc.returncode,identity=identity,boundary='Pure real Splash VM and synthetic in-memory records. No GUI, Host, timers, storage, Calendar/Mail service, network, or business execution tested.')
    if proc.returncode==0 and not proc.stderr:
        actual=json.loads(proc.stdout.removeprefix('MUSE_VM_RESULT ').strip());fail=[]
        assert len(actual['cases'])==len(rows)
        for row,r in zip(rows,actual['cases']):
            e=row['expected'];v=r['view'];counts=dict(local_nodes=sum(n['title']=='本地结果读回记录' for n in v['nodes']),execution_nodes=sum(n['title']=='执行记录' for n in v['nodes']),node_count=len(v['nodes']))
            checks=dict(name=r['name']==row['name'],proof=r['proof']==e['proof'],visible=bool(v['nodes'])==e['visible'],verified=(bool(v['nodes']) and v['nodes'][0]['state']=='已核验')==e['verified'],pure=r['unchanged'],cap=len(v['nodes'])<=12)
            for k in ['local_nodes','execution_nodes','node_count']:
                if k in e:checks[k]=counts[k]==e[k]
            if 'limited' in e:checks['limited']=v['limited']==e['limited']
            r['checks']=checks
            if not all(checks.values()):fail.append(dict(name=r['name'],failed=[k for k,b in checks.items() if not b]))
        if actual['unexpected_branch_calls']:fail.append(dict(name='unexpected-adapter-branch',calls=actual['unexpected_branch_calls']))
        report.update(status='FIXTURE_PASS' if not fail else 'FAIL',failed=fail,actual=actual,cases=len(rows))
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report.get(k) for k in ['status','cases','failed','returncode']},ensure_ascii=False))
    return 0 if report['status']=='FIXTURE_PASS' else 1
if __name__=='__main__':raise SystemExit(main())
