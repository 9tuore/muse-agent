#!/usr/bin/env python3
"""Sequential real-process fault/restart pairs; synthetic services only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def audit(fault, recovery):
    before, after = fault/'state/muse-goals', recovery/'state/muse-goals'
    fs, rs = read(fault/'summary.json'), read(recovery/'summary.json')
    cp = read(before/'failure-checkpoint.json')
    g, old = read(after/'goals.json'), read(before/'goals.json')
    cal = read(after/'calendar-state.json')
    activity, old_activity = read(after/'activity.json'), read(before/'activity.json')
    request = cp['request']
    action = next(a for a in g['actions'] if a['id']==request)
    old_action = next(a for a in old['actions'] if a['id']==request)
    receipts = [r for r in cal['receipts'] if r['request_id']==request]
    calls = rs['result']['observation']['calls']
    checks = {
        'distinct_host_processes': fs['host_pid'] != rs['host_pid'],
        'fault_host_stopped_before_restart': fs['host_stopped_epoch'] <= rs['host_started_epoch'],
        'same_frozen_candidate': fs['source_sha256']==rs['source_sha256'],
        'same_host_binary': fs['host_sha256']==rs['host_sha256'],
        'seed_exact_failed_goals_bytes': rs['seed_hashes']['muse-goals/goals.json']==sha(before/'goals.json'),
        'no_new_goal_run_action_ids': all([r['id'] for r in g[k]]==[r['id'] for r in old[k]] for k in ['goals','runs','actions']),
        'original_action_payload_unchanged': all(action[k]==old_action[k] for k in ['id','goal_id','run_id','service','target_scope','payload_json','plan_revision']),
        'action_verified': action['status']=='verified',
        'one_exact_persisted_receipt': len(receipts)==1 and receipts[0]['status']=='verified' and receipts[0]['persisted'] is True,
        'only_exact_independent_event_get': bool(calls) and all(c['service']=='calendar.get' and c['payload']=={'calendar_id':'test-calendar','event_id':'test-event'} for c in calls),
        'activity_preserves_old_prefix': activity[:len(old_activity)]==old_activity,
        'one_readback_activity_for_original_request': sum(a['request_id']==request and a['kind']=='calendar readback' for a in activity)==1,
        'existing_artifacts_byte_equal': all((after/p.relative_to(before)).is_file() and sha(p)==sha(after/p.relative_to(before)) for p in (before/'results').glob('*') if p.is_file()),
    }
    receipt=receipts[0] if len(receipts)==1 else {}
    payload=json.loads(action['payload_json'])
    checks['receipt_exact_action_identity']=all(receipt.get(k)==action[k] for k in ['goal_id','run_id','service']) and receipt.get('calendar_id')==action['target_scope'] and receipt.get('event_id')==payload['event_id']
    if cp['case'].startswith('delete_'):
        checks['delete_receipt_payload_exact']=receipt.get('payload_json')==action['payload_json']
        checks['delete_memory_bytes_unchanged']=sha(before/'memory.json')==sha(after/'memory.json')
        checks['delete_goal_run_records_unchanged']=old['goals']==g['goals'] and old['runs']==g['runs']
        checks['delete_only_one_missing_activity_added']=len(activity)-len(old_activity)==1
    else:
        run=next(r for r in g['runs'] if r['id']==cp['run_id'])
        goal=next(r for r in g['goals'] if r['id']==cp['goal'])
        artifact=read(after/goal['result_path']);event=cp['event']
        memory=read(after/'memory.json')
        claims=[c['document'] for c in memory['claims'] if c['document']['id']=='memory:result:'+cp['run_id']]
        sources=[s for s in memory['sources'] if s['source_id']=='source:calendar:'+cp['run_id']]
        checks['artifact_exact_ids']=artifact['task_id']==goal['id'] and artifact['run_id']==run['id'] and artifact['request_id']==request
        checks['artifact_exact_event_fields']=artifact['event_id']==event['id'] and all(artifact[k]==event[k] for k in ['calendar_id','version','title','start','end','time_zone','location'])
        checks['goal_run_artifact_path_agree']=goal['status']==run['status']=='completed' and goal['result_path']==run['result_path']
        checks['one_result_claim_and_source']=len(claims)==len(sources)==1
        checks['result_claim_exact_binding']=len(claims)==1 and claims[0]['origin']['ref']==run['id'] and claims[0]['payload']['subject_id']==goal['id'] and claims[0]['scope']['account']=='test-account' and artifact['source_id'] in claims[0]['payload']['source_ids'] and 'source:calendar:'+run['id'] in claims[0]['payload']['source_ids']
        checks['result_source_exact_artifact_digest']=len(sources)==1 and sources[0]['content_sha256']==sha(after/goal['result_path'])
        checks['one_memory_activity_for_original_request']=sum(a['request_id']==request and a['kind']=='memory saved' for a in activity)==1
        checks['linked_only_missing_memory_activity_added']=len(activity)-len(old_activity)==1
    return dict(checks=checks,passed=sum(checks.values()),failed=[k for k,v in checks.items() if not v],host_pids=[fs['host_pid'],rs['host_pid']],file_sha256={n:dict(before=sha(before/n),after=sha(after/n)) for n in ['goals.json','memory.json','activity.json','calendar-state.json']})

def main(a):
    out=a.out.resolve();assert out.is_relative_to(HERE);out.mkdir(parents=True,exist_ok=False)
    source=a.source_bundle.resolve();expected=sha(source/'main.splash')
    rows=[]
    cases=a.case or ['linked_memory_failure','linked_result_failure','delete_receipt_failure','delete_accept_failure']
    for case in cases:
        pair={ 'case':case }
        fault=out/(case+'-fault');recovery=out/(case+'-restart')
        for label,probe,target,seed in [('fault','failure.splash',fault,a.seed.resolve()),('restart','recovery_restart.splash',recovery,fault/'state')]:
            cmd=[sys.executable,str(HERE/'run.py'),'--source-bundle',str(source),'--host',str(a.host.resolve()),'--host-cwd',str(a.host_cwd.resolve()),'--probe',str(HERE/probe),'--out',str(target),'--port',str(a.port),'--seed',str(seed),'--case',case,'--delete-reconcile','--require-settlement']
            if label=='fault':cmd+=['--fault-storage','--stop-after-fault']
            proc=subprocess.run(cmd,capture_output=True,text=True)
            (out/(target.name+'.runner.log')).write_text(proc.stdout+proc.stderr)
            report=target/'summary.json'
            if report.exists():
                summary=read(report);pair[label]={k:summary.get(k) for k in ['status','checks','passed','failed','error','runtime_errors','source_sha256','host_sha256','probe_sha256','host_pid','host_started_epoch','host_stopped_epoch']};pair[label]['summary_sha256']=sha(report)
                assert summary['source_sha256']==expected
            else:pair[label]={'status':'HARNESS_ERROR','exit_code':proc.returncode}
            print(case,label,pair[label]['status'],flush=True)
            if pair[label]['status']!='DRY_RUN_PASS':break
        if pair.get('restart',{}).get('status')=='DRY_RUN_PASS':
            try:pair['independent_disk_audit']=audit(fault,recovery)
            except Exception as e:pair['audit_error']=repr(e)
        pair['status']='DRY_RUN_PASS' if pair.get('independent_disk_audit',{}).get('failed')==[] else 'PARTIAL'
        rows.append(pair)
        (out/'aggregate.json').write_text(json.dumps(dict(source_sha256=expected,pairs=rows,external_service_calls=0,real_model_inference=False),ensure_ascii=False,indent=2)+'\n')
        print(case,pair['status'],pair.get('independent_disk_audit',{}).get('failed',pair.get('audit_error')),flush=True)
    return 0 if len(rows)==len(cases) and all(r['status']=='DRY_RUN_PASS' for r in rows) else 1

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['source-bundle','host','host-cwd','seed','out']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--port',type=int,default=8661)
    p.add_argument('--case',action='append',choices=['linked_memory_failure','linked_result_failure','delete_receipt_failure','delete_accept_failure'])
    raise SystemExit(main(p.parse_args()))
