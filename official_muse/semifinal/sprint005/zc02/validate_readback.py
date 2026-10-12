#!/usr/bin/env python3
"""New validator unit fixtures only; never seed the reserved GUI profile."""
import argparse,copy,json
from pathlib import Path
from fixture_scope import PROFILE_MARKER,OWNER_MARKER,atomic_json
from readback import projection,assert_expected
from planner import decision,plan_from_prompt
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]

def main(root):
    root=Path(root).absolute();root.relative_to(REPO/'build');root.mkdir(exist_ok=False)
    (root/'apps/.host').mkdir(parents=True);(root/'FIXTURE_ONLY').write_bytes(PROFILE_MARKER);(root/'apps/.host/FIXTURE_ONLY').write_bytes(OWNER_MARKER)
    app=root/'apps/muse-goals';app.mkdir();checks={}
    def mem(project,cid,sid):
        scope={'project':'muse-goals','account':'local','visibility':'personal','user_id':'sprint005-user','project_id':project,'owner_id':'sprint005-owner'}
        src={'source_id':sid,'scope':scope,'content_sha256':'a'*64,'locator':'SPRINT005 synthetic unit locator'}
        claim={'document':{'id':cid,'scope':scope,'revision':1,'payload':{'deleted':False,'value':'SPRINT005 synthetic unit value','source_ids':[sid],'relations':[],'epistemic_type':'external_claim'}},'pinned':False,'source_history':[sid],'history':[]}
        return src,claim
    sa,ca=mem('project-A','claim-A','source-A');sb,cb=mem('project-B','claim-B','source-B')
    memory={'schema':1,'claims':[ca,cb],'sources':[sa,sb],'forget':[]};atomic_json(app/'memory.json',memory)
    atomic_json(app/'goals.json',{'schema':2,'goals':[{'id':'g-A'}],'runs':[{'id':'r-A','goal_id':'g-A'}],'actions':[{'id':'a-A','goal_id':'g-A','run_id':'r-A','plan_revision':1,'status':'unknown'}]})
    atomic_json(app/'memory-retrieval-last.json',{'hits':[{'id':'claim-A'}],'conflicts':[]})
    docs,snap=projection(root);rules={'retrieval_scope':{'project_id':'project-A'},'retrieval_expected_ids':['claim-A']}
    checks['scope_A_actual_trace_positive']=all(assert_expected(docs,snap,rules).values())
    atomic_json(app/'memory-retrieval-last.json',{'hits':[{'id':'claim-B'}],'conflicts':[]})
    docs,snap=projection(root);checks['scope_B_leak_and_wrong_hit_refused']=not all(assert_expected(docs,snap,rules).values())
    forgotten=copy.deepcopy(memory);entry=forgotten['claims'][0];entry['document']['payload'].update(deleted=True,value='',source_ids=[],relations=[]);entry['source_history']=[]
    atomic_json(app/'memory.json',forgotten);docs,snap=projection(root)
    checks['forgotten_content_cleared']=all(assert_expected(docs,snap,{'forgotten_claim_ids':['claim-A']}).values())
    forgotten['claims'][0]['history']=[{'old':'content'}];atomic_json(app/'memory.json',forgotten);docs,snap=projection(root)
    checks['forgotten_history_retention_refused']=not all(assert_expected(docs,snap,{'forgotten_claim_ids':['claim-A']}).values())
    atomic_json(app/'memory.json',memory)
    bad=copy.deepcopy(memory);bad['sources'][0]['scope']=sb['scope'];atomic_json(app/'memory.json',bad);_,snap=projection(root);checks['cross_scope_source_ref_refused']=not all(snap['checks'].values())
    duplicate=copy.deepcopy(memory);duplicate['claims'].append(ca);atomic_json(app/'memory.json',duplicate)
    try:projection(root);checks['duplicate_claim_refused']=False
    except ValueError:checks['duplicate_claim_refused']=True
    atomic_json(app/'memory.json',memory)
    draft=root/'apps/.host/mail'/('drafts-'+'a'*64)/'synthetic-draft.json'
    record={'schema':1,'draft_id':'synthetic-draft','compose_id':'synthetic-compose','account':'synthetic-account','publisher':'muse-goals','revision':1,'status':'unknown','body':'SPRINT005','attempts':[{'operation_id':'synthetic-operation','status':'unknown','payload':{'message_id':'synthetic-message'}}]}
    atomic_json(draft,record);docs,before=projection(root)
    checks['unknown_same_before_after_positive']=all(assert_expected(docs,before,{'unknown_no_resubmit':True},before).values())
    changed=copy.deepcopy(record);changed['attempts'].append(changed['attempts'][0]);atomic_json(draft,changed);docs,after=projection(root)
    checks['unknown_extra_attempt_refused']=not all(assert_expected(docs,after,{'unknown_no_resubmit':True},before).values())
    atomic_json(draft,record);(root/'receiver').mkdir();(root/'receiver/messages.jsonl').write_text(json.dumps({'message_id':'extra-delivery'})+'\n');docs,after=projection(root)
    checks['unknown_extra_receiver_delivery_refused']=not all(assert_expected(docs,after,{'unknown_no_resubmit':True},before).values())
    wrong=copy.deepcopy(before);wrong['fixture_root']='wrong-profile'
    try:assert_expected(docs,after,{'unknown_no_resubmit':True},wrong);checks['wrong_profile_snapshot_refused']=False
    except ValueError:checks['wrong_profile_snapshot_refused']=True
    try:assert_expected(docs,after,{});checks['empty_expectations_cannot_pass']=False
    except ValueError:checks['empty_expectations_cannot_pass']=True
    checks['missing_expected_file_refused']=not all(assert_expected(docs,after,{'assertions':[{'file':'activity.json','pointer':'','op':'present'}]}).values())
    (app/'activity.json').symlink_to(app/'memory.json')
    try:projection(root);checks['linked_business_file_refused']=False
    except ValueError:checks['linked_business_file_refused']=True
    (app/'activity.json').unlink()
    events='精确 calendar.events 参数：{"limit":200}'
    offered=[{'function':{'name':'calendar_events'}}]
    body={'messages':[{'role':'user','content':events}],'tools':offered}
    checks['actual_offered_limit200_plan']=decision(body)['args']=={'limit':200}
    try:decision(dict(body,tools=[]));checks['unoffered_tool_refused']=False
    except ValueError:checks['unoffered_tool_refused']=True
    failed={'messages':[{'role':'user','content':events},{'role':'tool','content':'{"ok":false,"error":"synthetic"}'}],'tools':offered}
    try:decision(failed);checks['actual_error_stops_plan']=False
    except ValueError:checks['actual_error_stops_plan']=True
    try:plan_from_prompt(events+' '+events);checks['mixed_duplicate_marker_refused']=False
    except ValueError:checks['mixed_duplicate_marker_refused']=True
    checks['kernel_planning_does_not_mint_approval']=all(k not in decision(body) for k in ('receipt','approval','kernel_persisted'))
    # SDK mailbox SHA consistency is exercised in this unit root, not the GUI root.
    from fixture_scope import digest
    account='b'*24;locator='mail:'+account+':synthetic-mail'
    actual_body='SPRINT005 actual cached body'
    material=copy.deepcopy(memory);material['sources'][0].update(locator=locator,content_sha256=digest(actual_body.encode()))
    atomic_json(app/'memory.json',material);mailbox=root/'apps/.host/mail'/('box-'+account+'.json')
    atomic_json(mailbox,{'messages':[{'id':'synthetic-mail','body':actual_body,'subject':'SPRINT005'}]})
    docs,snap=projection(root)
    checks['actual_mail_cache_source_hash_positive']=all(assert_expected(docs,snap,{'mail_source_ids':['source-A']}).values())
    atomic_json(mailbox,{'messages':[{'id':'synthetic-mail','body':actual_body+' changed','subject':'SPRINT005'}]});docs,snap=projection(root)
    checks['changed_actual_mail_body_hash_refused']=not all(assert_expected(docs,snap,{'mail_source_ids':['source-A']}).values())
    mailbox.unlink();docs,snap=projection(root)
    checks['required_actual_mail_cache_missing_refused']=not all(assert_expected(docs,snap,{'mail_source_ids':['source-A']}).values())
    result={'kind':'SPRINT005_READBACK_AND_PLANNER_UNIT_ONLY','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'sdk_gui_status':'NOT_TESTED','business_seed_only_in_unit_root':str(root),'reserved_gui_profile_written':False,'kernel_gui_cargo_calls':0}
    atomic_json(HERE/'evidence/readback-planner-unit.json',result)
    print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v]}))
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out-root',type=Path,default=REPO/'build/gpt02-sprint005-readback-unit-r1');a=p.parse_args();raise SystemExit(main(a.out_root))
