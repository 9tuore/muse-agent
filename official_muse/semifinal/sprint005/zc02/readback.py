#!/usr/bin/env python3
"""Independent read-only public business-state assertions. Never enumerate credential files."""
import argparse,collections,json,re
from pathlib import Path
from fixture_scope import scope,atomic_json,digest
FILES=('memory.json','goals.json','activity.json','memory-retrieval-last.json','memory-forget-commit.json','mail-draft.json','calendar-agent.json','calendar-agent-updates.json','calendar-agent-delete.json','chat-sessions.json')

def safe_read(root,path):
    if not path.is_file():return None
    if path.resolve()!=path or path.stat().st_nlink!=1:raise ValueError('Linked business file refused')
    for parent in path.parents:
        if parent==root.parent:break
        if parent.is_symlink():raise ValueError('Linked business directory refused')
    raw=path.read_bytes()
    if len(raw)>2_000_000:raise ValueError('Bounded business file required')
    return raw,json.loads(raw)

def projection(root):
    root=scope(root);documents={};hashes={}
    for name in FILES:
        result=safe_read(root,root/'apps/muse-goals'/name)
        if result:raw,data=result;documents[name]=data;hashes[name]=digest(raw)
    mem=documents.get('memory.json',{});goals=documents.get('goals.json',{})
    claims={};sources={};checks={}
    for src in mem.get('sources',[]):
        sid=src['source_id']
        if sid in sources:raise ValueError('Duplicate source ID')
        sources[sid]={'scope':src['scope'],'content_sha256':src['content_sha256'],'locator_sha256':digest(src['locator'].encode())}
    for entry in mem.get('claims',[]):
        d=entry['document'];cid=d['id']
        if cid in claims:raise ValueError('Duplicate claim ID')
        claims[cid]={'scope':d['scope'],'revision':d['revision'],'deleted':d['payload']['deleted'],'source_ids':d['payload']['source_ids'],'value_sha256':digest(d['payload']['value'].encode()),'epistemic_type':d['payload']['epistemic_type'],'history_count':len(entry.get('history',[]))}
        checks['source_refs_'+cid]=all(s in sources and sources[s]['scope']==d['scope'] for s in d['payload']['source_ids'])
        if d['payload']['deleted']:
            checks['forgotten_content_'+cid]=d['payload']['value']=='' and not d['payload']['source_ids'] and not d['payload']['relations'] and not entry.get('history') and not entry.get('source_history') and not entry['pinned']
    goal_ids={g['id'] for g in goals.get('goals',[])};run_ids={r['id'] for r in goals.get('runs',[])}
    checks['unique_goal_run_action_ids']=all(len({r['id'] for r in goals.get(name,[])})==len(goals.get(name,[])) for name in ('goals','runs','actions'))
    checks['run_goal_links']=all(r['goal_id'] in goal_ids for r in goals.get('runs',[]))
    checks['action_goal_run_links']=all((not a['goal_id'] and not a['run_id'] and a['plan_revision']==0) or (a['goal_id'] in goal_ids and a['run_id'] in run_ids) for a in goals.get('actions',[]))
    drafts={};directory=root/'apps/.host/mail'
    if directory.is_dir():
        if directory.is_symlink():raise ValueError('Linked Mail store refused')
        for folder in directory.glob('drafts-*'):
            if not re.fullmatch(r'drafts-[0-9a-f]{64}',folder.name):continue
            for file in folder.glob('*.json'):
                if not re.fullmatch(r'[A-Za-z0-9-]{1,96}\.json',file.name):raise ValueError('Unexpected draft file')
                result=safe_read(root,file)
                if not result:continue
                _,d=result
                drafts[str(file.relative_to(root))]={'draft_id':d['draft_id'],'compose_id':d.get('compose_id'),'account':d['account'],'publisher':d['publisher'],'revision':d['revision'],'status':d['status'],
                    'body_sha256':digest(d.get('body','').encode()),'attempts':[{'operation_id':a.get('operation_id'),'status':a.get('status'),'message_id':a.get('payload',{}).get('message_id')} for a in d.get('attempts',[])]}
    receiver=[];file=root/'receiver/messages.jsonl'
    if file.exists():
        if file.is_symlink() or file.stat().st_nlink!=1:raise ValueError('Linked receiver log refused')
        receiver=[json.loads(line) for line in file.read_text().splitlines()]
    summary={'kind':'SPRINT005_INDEPENDENT_READBACK','fixture_root':str(root),'file_sha256':hashes,'claims':claims,'sources':sources,'goal_ids':sorted(goal_ids),'run_ids':sorted(run_ids),
             'action_status_counts':dict(collections.Counter(a['status'] for a in goals.get('actions',[]))),'host_mail_drafts':drafts,'retrieval':documents.get('memory-retrieval-last.json'),
             'receiver_count':len(receiver),'receiver_message_ids':[r['message_id'] for r in receiver],'checks':checks,'sdk_gui_status':'NOT_ASSERTED'}
    return documents,summary

def pointer(data,value):
    for key in value.strip('/').split('/') if value else []:
        key=key.replace('~1','/').replace('~0','~')
        if key in ('password','secret','token','api_key','env_vars','approval_grant'):raise ValueError('Credential/capability pointer refused')
        data=data[int(key)] if isinstance(data,list) else data[key]
    return data

def assert_expected(documents,snapshot,expected,before=None):
    checks=dict(snapshot['checks'])
    for i,rule in enumerate(expected.get('assertions',[])):
        if rule['file'] not in FILES:raise ValueError('Business file whitelist required')
        try:
            value=pointer(documents[rule['file']],rule.get('pointer',''));op=rule['op']
            if op=='eq':ok=value==rule['value']
            elif op=='len':ok=len(value)==rule['value']
            elif op=='contains':ok=rule['value'] in value
            elif op=='present':ok=True
            else:raise ValueError('Unsupported assertion operator')
        except (KeyError,IndexError,TypeError):ok=False
        checks['assertion_'+str(i)]=ok
    if expected.get('retrieval_scope') is not None:
        trace=snapshot['retrieval'];checks['actual_retrieval_trace_present']=isinstance(trace,dict)
        for hit in trace.get('hits',[]) if isinstance(trace,dict) else []:
            record=snapshot['claims'].get(hit['id']);wanted=expected['retrieval_scope']
            checks['retrieval_scope_'+hit['id']]=record is not None and not record['deleted'] and all(record['scope'].get(k) in (v if isinstance(v,list) else [v]) for k,v in wanted.items())
    for cid in expected.get('forgotten_claim_ids',[]):checks['requested_forget_'+cid]=cid in snapshot['claims'] and snapshot['claims'][cid]['deleted'] and checks.get('forgotten_content_'+cid) is True
    if expected.get('unknown_no_resubmit'):
        if before is None:raise ValueError('Actual before snapshot required')
        unknown={k:v for k,v in before['host_mail_drafts'].items() if v['status']=='unknown'}
        checks['actual_unknown_before_present']=bool(unknown)
        checks['unknown_same_draft_attempt_payload_no_resubmit']=all(snapshot['host_mail_drafts'].get(k)==v for k,v in unknown.items())
        checks['independent_receiver_count_not_increased']=snapshot['receiver_count']==before['receiver_count'] and snapshot['receiver_message_ids']==before['receiver_message_ids']
    return checks

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--expected',type=Path);p.add_argument('--before',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    docs,snapshot=projection(a.root)
    if a.expected:
        rules=json.loads(a.expected.read_text());checks=assert_expected(docs,snapshot,rules,json.loads(a.before.read_text()) if a.before else None)
        snapshot['checks']=checks;snapshot['status']='PASS' if checks and all(checks.values()) else 'FAIL'
    else:snapshot['status']='SNAPSHOT_ONLY'
    atomic_json(a.out,snapshot);print(json.dumps({'status':snapshot['status'],'checks':len(snapshot['checks']),'failed':[k for k,v in snapshot['checks'].items() if not v],'sdk_gui':'NOT_ASSERTED'}))
    raise SystemExit(1 if snapshot['status']=='FAIL' else 0)
