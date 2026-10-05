#!/usr/bin/env python3
"""Actual locked CardHost + production receipt, synthetic isolated profile only."""
import argparse, copy, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HOST=ROOT/'official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':'))
def profile(case):
    if case=='commitphase':
        own=HERE/'capacity-canonical-header-r1/first/state/muse-goals'
        return {name:json.loads((own/name).read_text()) for name in ['memory.json','memory.backup.json','global-memory-settings.json','activity.json']}
    # All templates originate in this chat's synthetic fixture. Never read live profiles.
    own=json.loads((HERE/'capacity-r1/first/state/muse-goals/memory.json').read_text())
    count=2 if case.startswith('relation_') or case in ('cowguard','pairguard','preserveguard','scopeguard') else (63 if case.startswith('linked63') else 64)
    memory={'schema':1,'claims':[],'sources':[],'forget':[]}
    for n in range(count):
        source=copy.deepcopy(own['sources'][0]);claim=copy.deepcopy(own['claims'][0])
        sid=f'a2-source-{n}';value=f'合成收件恢复容量记录{n}'
        source.update(source_id=sid,locator=f'a2-synthetic:receipt:{n}',support_excerpt=value,content_sha256=hashlib.sha256(value.encode()).hexdigest())
        source['scope'].update(account='synthetic-account',project_id='a2-project',owner_id='a2-owner')
        claim['document'].update(id=f'a2-memory-{n}',scope=copy.deepcopy(source['scope']))
        claim['document']['payload'].update(subject_id=f'a2-subject-{n}',value=value,source_ids=[sid])
        claim['source_history']=[sid]
        if n==0:source['source_id']='a2-mail-source'
        if n==1:source['source_id']='source:calendar:a2-calendar-run'
        claim['document']['payload']['source_ids']=[source['source_id']];claim['source_history']=[source['source_id']]
        if case=='linked64' and n==63:
            claim['document']['id']='memory:result:a2-run'
            claim['document']['payload'].update(subject_id='a2-goal',predicate='verified_result')
        memory['sources'].append(source);memory['claims'].append(claim)
    if case=='relation_cross_scope':
        memory['claims'][0]['document']['scope']['project_id']='other-project';memory['sources'][0]['scope']['project_id']='other-project'
    if case=='relation_unauthorized':
        memory['claims'][0]['document']['scope']['account']='not-authorized';memory['sources'][0]['scope']['account']='not-authorized'
    if case=='relation_foreign_user':
        memory['claims'][0]['document']['scope']['user_id']='another-synthetic-user';memory['sources'][0]['scope']['user_id']='another-synthetic-user'
    if case=='relation_deleted':
        memory['claims'][0]['document']['payload'].update(deleted=True,value='',source_ids=[],relations=[]);memory['claims'][0]['source_history']=[]
    if case=='relation_expired':memory['claims'][0]['document']['payload']['valid_until']='2000-01-01T00:00:00Z'
    if case=='relation_forgotten':
        s=memory['sources'][0];d=memory['claims'][0]['document']
        memory['forget']=[{'source_id':s['source_id'],'subject_id':d['payload']['subject_id'],'predicate':'status','account_scope':'synthetic-account','at':s['observed_at'],'content_sha256':s['content_sha256'],'scope':copy.deepcopy(s['scope'])}]
    goal={'id':'a2-goal','version':1,'status':'running','archived':False,'updated_at':1,'project_id':'a2-project','owner_id':'a2-owner','result_path':'results/a2-linked.json'}
    run={'id':'a2-run','goal_id':'a2-goal','plan_revision':1,'status':'running','result_path':goal['result_path'],'started_at':1,'finished_at':0,'request_id':'a2-mail-request'}
    action={'id':'a2-mail-request','goal_id':'','run_id':'','plan_revision':0,'service':'mail.send','target_scope':'synthetic-account','payload_json':encoded({'to':'self@example.invalid','subject':'MUSE-R2-A2-RECEIPT'}),'status':'accepted','started_at':1,'finished_at':2}
    if case in ('recover64','stale_memory64'):action['status']='verified'
    linked=case.startswith('linked')
    if linked:action.update(goal_id='a2-goal',run_id='a2-run',plan_revision=1)
    goals={'schema':2,'goals':[goal] if linked else [],'runs':[run] if linked else [],'actions':[action],'selected_id':'a2-goal' if linked else ''}
    if case.endswith('_dense'):
        for n in range(1,32):
            previous=copy.deepcopy(goal);previous.update(id=f'a2-historical-goal-{n}',status='completed',result_path=f'results/a2-historical-{n}.json');goals['goals'].append(previous)
        for n in range(1,128):
            previous=copy.deepcopy(run);previous.update(id=f'a2-historical-run-{n}',goal_id=f'a2-historical-goal-{1+n%31}',status='completed',request_id=f'a2-historical-request-{n}',finished_at=2);goals['runs'].append(previous)
            previous=copy.deepcopy(action);previous.update(id=f'a2-historical-request-{n}',goal_id=f'a2-historical-goal-{1+n%31}',run_id=f'a2-historical-run-{n}',status='verified');goals['actions'].append(previous)
    draft={'account':'synthetic-account','to':'self@example.invalid','subject':'MUSE-R2-A2-RECEIPT 合成收件声明','body':'这是独立 fixture 合成邮件，没有实际投递。','status':'accepted','preview':'','attempt':'a2-attempt','request_id':'a2-mail-request','accepted_at':2,'verified_at':0,'verified_id':'','link_goal_id':'a2-goal' if linked else '','link_event_id':'a2-event' if linked else '','link_run_id':'a2-run' if linked else '','incoming_key':''}
    if case.startswith('send_'):
        goals['actions']=goals['actions'][1:]
        draft.update(status='waiting_user',attempt='',request_id='',accepted_at=0)
        draft['preview']=encoded({k:draft[k] for k in ('account','to','subject','body')})
    sessions=[{'id':f'a2-chat-{n}','title':f'合成对话{n}','created_at':1,'updated_at':1,'focus_project':'a2-project','focus_owner':'a2-owner','goal_id':'','proposals':[],
               'messages':[{'role':'user','text':f'合成用户消息{n}','state':'success','at':1},{'role':'assistant','text':f'合成助手消息{n}','state':'success','at':1}]} for n in range(16)]
    links=[{'goal_id':'a2-goal','account_id':'synthetic-account','message_id':'a2-mail-message','source_id':'a2-mail-source','source_claim_id':'a2-memory-0','status':'verified','event_id':'a2-event','calendar_id':'a2-calendar','run_id':'a2-calendar-run','candidate_revision':1,
            'candidate':{'title':'合成日程','start':'2026-10-06T15:00:00+08:00','end':'2026-10-06T16:00:00+08:00','time_zone':'Asia/Shanghai','location':'合成地点'}}] if linked else []
    return {'memory.json':memory,'global-memory-settings.json':{'schema':1,'enabled':True,'user_id':own['sources'][0]['scope']['user_id'],'forget_pending':False},'goals.json':goals,'mail-draft.json':draft,
            'chat-sessions.json':{'schema':1,'selected_id':'a2-chat-0','sessions':sessions},'activity.json':[{'kind':'synthetic_seed','detail':f'合成初始事件{n}','at':1} for n in range(8)],
            'calendar-state.json':{'schema':1,'links':links,'receipts':[],'local_states':[]}}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--cases',nargs='+',default=['accepted64','recover64','stale_memory64','wrong_id','stale_request','linked63','linked64']);args=ap.parse_args()
    assert sha(HOST)=='52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837'
    out=HERE/args.out;assert out.parent==HERE and not out.exists();out.mkdir()
    readable=out/'readable';shutil.copytree(ROOT/'official_muse/rc/improvement-20261005-r1/readable-rc27-r1',readable)
    shutil.copyfile(args.source,readable/'main.splash')
    compact=out/'compact'
    compact_run=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/compact_bundle.py'),'--source',str(readable),'--out',str(compact)],capture_output=True,text=True,check=True)
    (out/'compact-binding.json').write_text(compact_run.stdout)
    os.environ['MUSE_CARD_HOST']=str(HOST)
    sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'));sys.path.insert(0,str(ROOT/'official_muse/rc/core_chain'))
    import regression_run
    from run_calendar_clarification import restart
    regression_run.existing.WIDGET=regression_run.existing.WIDGET.replace('    Label{text:',
        '    mail_test_id := TextInput{width: Fill}\n    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n    mail_body := TextInput{width: Fill}\n    Label{text:',1)
    real_popen=subprocess.Popen
    report={'source_sha256':sha(readable/'main.splash'),'compact_sha256':sha(compact/'main.splash'),'host_sha256':sha(HOST),'test_kind':'SYNTHETIC_PROFILE_PRODUCTION_FUNCTIONS','real_model':False,'real_mail':False,'real_calendar':False,'default_budget_unchanged':True,
            'profile_origin':'Clones of a2 capacity-r1 synthetic records; generated 16 chat sessions, 64/63 claims, valid sources, Goal/Run/action/link; no production data read. Render and transport instrumented by existing harness.','cases':{}}
    for case in args.cases:
        case_out=out/case;case_out.mkdir();seed=profile(case)
        (case_out/'seed-profile.json').write_text(encoded(seed)+'\n')
        probes={'cowguard':'cow_guard.splash','pairguard':'pair_validation.splash','commitphase':'commit_phases.splash','preserveguard':'preserve_guards.splash','scopeguard':'scope_cache.splash'}
        template=HERE/('relation_loop.splash' if case.startswith('relation_') else probes.get(case,'receipt.splash'))
        probe_text=template.read_text()
        if case=='scopeguard':
            previous=(HERE/'capacity-preserve-fast-r1/readable/main.splash').read_text()
            stripped=regression_run.existing.replace_function(previous,'gm_scope_valid','@@')
            start=previous.index('fn gm_scope_valid(')
            definition=previous[start:start+len(previous)-len(stripped)+2]
            probe_text=definition.replace('fn gm_scope_valid(', 'fn a2_old_scope_valid(',1)+'\n'+probe_text
        probe=case_out/'probe.splash';probe.write_text(probe_text.replace('__CASE__',case).replace('__MEMORY_COUNT__',str(len(seed['memory.json']['claims']))).replace('__ACTION_COUNT__',str(len(seed.get('goals.json',{}).get('actions',[])))))
        def seeded_popen(command,*a,**kw):
            state=Path(command[command.index('--app-data')+1]).resolve()/ 'muse-goals'
            assert state.is_relative_to(case_out)
            if not state.exists():
                state.mkdir(parents=True)
                for name,obj in seed.items():(state/name).write_text(encoded(obj))
            return real_popen(command,*a,**kw)
        regression_run.subprocess.Popen=seeded_popen
        try:
            first=regression_run.run_suite('mail_calendar_chain',(compact/'main.splash').read_text(),compact,case_out/'first',8509,probe)
            second=restart(case_out/'first',case_out) if not first['failed'] and (case=='recover64' or case.startswith('linked')) else None
            result={'status':'PASS' if not first['failed'] and not (second or {}).get('failed') else 'FAIL','initial':first,'restart':second}
        except Exception as exc:result={'status':'ERROR','error':str(exc)}
        finally:regression_run.subprocess.Popen=real_popen
        report['cases'][case]=result;(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(case,result['status'],flush=True)
    report['status']='FIXTURE_PASS' if all(x['status']=='PASS' for x in report['cases'].values()) else 'FAIL'
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return int(report['status']!='FIXTURE_PASS')
if __name__=='__main__':raise SystemExit(main())
