#!/usr/bin/env python3
"""Narrow Calendar approval callback probes; own synthetic jail and locked Host."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from run_receipt import HOST,profile,encoded

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def seed(case):
    data=profile('linked63_dense')
    state=data['goals.json'];g=state['goals'][0]
    g.update(status='planned',kind='calendar',schema=1,goal='合成Calendar分段回调测试',source='synthetic only',items=['合成邀请'],approved_at=0,model_summary='',mail_source={'account_id':'synthetic-account','message_id':'a2-mail-message','source_id':'a2-mail-source','observed_at':'2026-10-05T00:00:00Z'})
    state['runs']=state['runs'][1:];state['actions']=state['actions'][1:]
    links=data['calendar-state.json']['links'];link=links[0]
    link.update(status='waiting_user',event_id='',run_id='',operation='create')
    link['candidate'].update(calendar_id='a2-calendar',start='2026-12-15T15:00:00+08:00',end='2026-12-15T16:00:00+08:00')
    for n in range(1,32):
        other=copy.deepcopy(link);other.update(goal_id=f'a2-historical-goal-{n}',status='verified',event_id=f'a2-history-event-{n}',run_id=f'a2-historical-run-{n}')
        links.append(other)
    data['calendar-state.json']['receipts']=[{'request_id':f'a2-history-calendar-receipt-{n}','goal_id':f'a2-historical-goal-{1+n%31}','run_id':f'a2-historical-run-{n+1}','service':'calendar.create','payload_json':'{}','calendar_id':'a2-calendar','event_id':f'a2-history-event-{n}','version':'v1','status':'verified','verified_at':1} for n in range(64)]
    if case in ('restart_no_action','recover_create','recover_update'):
        g['status']='running'
        new_run={'id':'a2-new-calendar-run','goal_id':'a2-goal','plan_revision':1,'status':'running','result_path':g['result_path'],'started_at':1,'finished_at':0,'request_id':'a2-new-calendar-request'}
        if case=='restart_no_action':state['runs'][0]=new_run
        else:state['runs'].append(new_run)
        if case=='recover_update':link['operation']='update'
    return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--cases',nargs='+',choices=['dense','duplicate','request_changed','version_changed','restart_no_action','recover_create','recover_update','owner_after_accept','payload_during_get'],default=['dense','duplicate','request_changed','version_changed','restart_no_action'])
    args=ap.parse_args();assert sha(args.source)==args.expected_sha256
    assert sha(HOST)=='52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837'
    out=HERE/args.out;assert out.parent==HERE and not out.exists();out.mkdir()
    readable=out/'readable';shutil.copytree(HERE/'capacity-relation-short-circuit-r1/readable',readable)
    shutil.copyfile(args.source,readable/'main.splash');compact=out/'compact'
    c=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/compact_bundle.py'),'--source',str(readable),'--out',str(compact)],capture_output=True,text=True,check=True)
    (out/'compact-binding.json').write_text(c.stdout)
    os.environ['MUSE_CARD_HOST']=str(HOST);sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'))
    import regression_run
    regression_run.existing.WIDGET=regression_run.existing.WIDGET.replace('    Label{text:',
        '    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n'
        '    mail_body := TextInput{width: Fill}\n    right_content := View{width: Fill height: Fit on_render: || {}}\n    right_page_content := View{width: Fill height: Fit on_render: || {}}\n    chat_list := View{width: Fill height: Fit on_render: || {}}\n    Label{text:',1)
    real_popen=subprocess.Popen
    report={'status':'RUNNING','source_sha256':sha(readable/'main.splash'),'compact_sha256':sha(compact/'main.splash'),'host_sha256':sha(HOST),'fixture_only':True,'default_budget_unchanged':True,'real_model':False,'real_os_action':False,'production_data_used':False,'profile':'Own synthetic 63-memory/16-chat/32-goal/127-run/127-action/32-link/64-receipt seed; never read live profile','cases':{}}
    for case in args.cases:
        co=out/case;co.mkdir();data=seed(case)
        (co/'seed-profile.json').write_text(encoded(data)+'\n')
        probe=co/'probe.splash';probe.write_text((HERE/'calendar_callbacks.splash').read_text().replace('__CASE__',case).replace('__RUNCOUNT__',str(len(data['goals.json']['runs']))))
        def seeded(command,*a,**kw):
            state=Path(command[command.index('--app-data')+1]).resolve()/'muse-goals';assert state.is_relative_to(co)
            if not state.exists():
                state.mkdir(parents=True)
                for name,obj in data.items():(state/name).write_text(encoded(obj))
            return real_popen(command,*a,**kw)
        regression_run.subprocess.Popen=seeded
        try:
            r=regression_run.run_suite('mail_calendar_chain',(compact/'main.splash').read_text(),compact,co/'first',8509,probe)
            result={'status':'PASS' if not r['failed'] else 'FAIL','initial':r}
        except Exception as e:result={'status':'ERROR','error':str(e)}
        finally:regression_run.subprocess.Popen=real_popen
        report['cases'][case]=result;(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(case,result['status'],flush=True)
        if result['status']!='PASS':break
    report['status']='FIXTURE_PASS' if all(r['status']=='PASS' for r in report['cases'].values()) else 'FAIL'
    report['passed_checks']=sum(r.get('initial',{}).get('passed',0) for r in report['cases'].values())
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return int(report['status']!='FIXTURE_PASS')

if __name__=='__main__':raise SystemExit(main())
