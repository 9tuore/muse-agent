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
from run_receipt import HOST,encoded
from manual_replan_profile import profile as small_profile

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def seed(case):
    data=small_profile()
    if case=='legal_dense':
        origin=HERE/'calendar-binding-final-r1/dense/first/state/muse-goals'
        for name in ['goals.json','calendar-state.json','memory.json']:
            data[name]=json.loads((origin/name).read_text())
        m=data['memory.json'];m['claims']=m['claims'][:62]+[m['claims'][-1]]
        ids=set()
        for claim in m['claims']:
            ids.update(claim['document']['payload']['source_ids']);ids.update(claim['source_history'])
        m['sources']=[source for source in m['sources'] if source['source_id'] in ids]
    return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--cases',nargs='+',choices=['legal','legal_dense','account','project','owner','message','not_verified','message_late','scope_after_source','focus_after_retrieval'],default=['legal','legal_dense','account','project','owner','message','not_verified'])
    args=ap.parse_args();assert sha(args.source)==args.expected_sha256
    assert sha(HOST)=='52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837'
    out=HERE/args.out;assert out.parent==HERE and not out.exists();out.mkdir()
    readable=out/'readable';shutil.copytree(HERE/'capacity-relation-short-circuit-r1/readable',readable)
    shutil.copyfile(args.source,readable/'main.splash');assert sha(readable/'main.splash')==args.expected_sha256;compact=out/'compact'
    c=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/compact_bundle.py'),'--source',str(readable),'--out',str(compact)],capture_output=True,text=True,check=True)
    (out/'compact-binding.json').write_text(c.stdout)
    os.environ['MUSE_CARD_HOST']=str(HOST);sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'))
    import regression_run
    regression_run.existing.WIDGET=regression_run.existing.WIDGET.replace('    Label{text:',
        '    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n'
        '    mail_body := TextInput{width: Fill}\n    right_content := View{width: Fill height: Fit on_render: || {}}\n    right_page_content := View{width: Fill height: Fit on_render: || {}}\n    chat_list := View{width: Fill height: Fit on_render: || {}}\n    Label{text:',1)
    real_popen=subprocess.Popen
    report={'status':'RUNNING','source_sha256':sha(readable/'main.splash'),'compact_sha256':sha(compact/'main.splash'),'host_sha256':sha(HOST),'fixture_only':True,'default_budget_unchanged':True,'real_model':False,'real_os_action':False,'production_data_used':False,'profile':'Own prior verified synthetic CardHost Goal/action/link/receipt; small2-memory profile or63-memory/32Goal/128Run/action dense profile. No production data.','cases':{}}
    for case in args.cases:
        co=out/case;co.mkdir();data=seed(case)
        (co/'seed-profile.json').write_text(encoded(data)+'\n')
        probe=co/'probe.splash';probe.write_text((HERE/'manual_replan.splash').read_text().replace('__CASE__',case).replace('__RUN_COUNT__',str(len(data['goals.json']['runs']))).replace('__ACTION_COUNT__',str(len(data['goals.json']['actions']))).replace('__GOAL_COUNT__',str(len(data['goals.json']['goals']))).replace('__MEMORY_COUNT__',str(len(data['memory.json']['claims']))))
        def seeded(command,*a,**kw):
            state=Path(command[command.index('--app-data')+1]).resolve()/'muse-goals';assert state.is_relative_to(co)
            if not state.exists():
                state.mkdir(parents=True)
                for name,obj in data.items():
                    target=state/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(encoded(obj))
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
