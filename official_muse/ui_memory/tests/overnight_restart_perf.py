#!/usr/bin/env python3
"""Restart and idle checks confined to one signed synthetic candidate Shell."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'official_muse/phase2/tests'))
from remote import Remote
sys.path.insert(0,str(Path(__file__).parent))
from visual_capture import shot


def load(p,default):
    return json.loads(p.read_text()) if p.exists() else default


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--wire',type=Path,required=True)
    p.add_argument('--port',type=int,default=8412);p.add_argument('--cycles',type=int,default=10)
    p.add_argument('--idle-seconds',type=int,default=1200);a=p.parse_args()
    assert 10<=a.cycles<=20 and 0<=a.idle_seconds<=1800
    meta=load(a.candidate/'candidate.json',{});assert meta['profile_kind']=='LOCAL_MODEL_ONLY_SYNTHETIC'
    jail=a.candidate/'private/apps/muse-goals';a.out.mkdir(parents=True,exist_ok=False)
    report={'version':meta['version'],'source_sha256':meta['source_sha256'],'host_sha256':meta['host_sha256'],
            'kind':'LIVE_SYNTHETIC_SHELL_RESTART_IDLE','cycles':[],'samples':[],'status':'RUNNING',
            'real_mail_account_count':0,'mail_send':False,'calendar_write':False,'started_at':time.time()}
    r=Remote(a.port)
    def save():
        (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def wires():return len(a.wire.read_text().splitlines()) if a.wire.exists() else 0
    def snapshot():
        names=['goals.json','memory.json','chat-sessions.json','ui-layout.json','global-memory-settings.json',
               'mail-watch.json','mail-draft.json','calendar-state.json']
        if (jail/'results').exists():names += [str(x.relative_to(jail)) for x in (jail/'results').glob('*.json')]
        hashes={n:hashlib.sha256((jail/n).read_bytes()).hexdigest() for n in names if (jail/n).exists()}
        g=load(jail/'goals.json',{});m=load(jail/'memory.json',{});watch=load(jail/'mail-watch.json',{})
        c=load(jail/'chat-sessions.json',{});activity=load(jail/'activity.json',[])
        return {'hashes':hashes,'counts':{**{k:len(g.get(k,[])) for k in ['goals','runs','actions']},
                'memory':len(m.get('claims',[])),'sources':len(m.get('sources',[])),
                'mail_alerts':len(watch.get('alerts',[])),'mail_accounts':len(watch.get('accounts',[]))},
                'selected_chat':c.get('selected_id'),'activity':activity,'model_requests':wires()}
    def ready():
        deadline=time.monotonic()+35
        while time.monotonic()<deadline:
            try:
                r.find('打开');r.click('打开');r.wait_for('goal_input',20)
                time.sleep(1);return
            except (OSError,AssertionError):time.sleep(.3)
        raise TimeoutError('Muse did not become ready after isolated restart')
    try:
        baseline=snapshot();report['baseline']=baseline;save();assert baseline['counts']['mail_accounts']==0
        for cycle in range(a.cycles):
            before=snapshot()
            completed=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/launch_candidate.py'),
                '--candidate',str(a.candidate.resolve()),'--port',str(a.port),'--model-port','8083','--restart'],
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
            (a.out/f'cycle-{cycle+1:02d}.log').write_text(completed.stdout)
            assert completed.returncode==0,completed.stdout[-1000:]
            ready();after=snapshot()
            extra=after['activity'][len(before['activity']):]
            unchanged=before['hashes']==after['hashes']
            item={'cycle':cycle+1,'durable_files_unchanged':unchanged,'counts_unchanged':before['counts']==after['counts'],
                  'selected_chat_unchanged':before['selected_chat']==after['selected_chat'],
                  'no_model_resend':before['model_requests']==after['model_requests'],
                  'activity_only_restore':all(e.get('kind')=='restart restore' for e in extra),
                  'extra_activity_kinds':[e.get('kind') for e in extra],
                  'changed_files':[n for n in set(before['hashes'])|set(after['hashes']) if before['hashes'].get(n)!=after['hashes'].get(n)]}
            report['cycles'].append(item);save();print(json.dumps(item),flush=True)
            if not all(item[k] for k in ['durable_files_unchanged','counts_unchanged','selected_chat_unchanged','no_model_resend','activity_only_restore']):
                report['status']='PARTIAL';save();raise AssertionError('Restart invariant failed; stop repeated cycles')
        report['idle_before']=snapshot();pid=json.loads(r.request('/s'))['pid']
        deadline=time.monotonic()+a.idle_seconds
        while True:
            values=subprocess.check_output(['ps','-p',str(pid),'-o','pcpu=,rss=,time='],text=True).strip().split()
            report['samples'].append({'at':time.time(),'pid':pid,'cpu_percent':float(values[0]),'rss_kib':int(values[1]),'cpu_time':values[2]})
            save()
            if time.monotonic()>=deadline:break
            time.sleep(min(30,max(0,deadline-time.monotonic())))
        report['idle_after']=snapshot()
        report['idle_no_model_requests']=report['idle_before']['model_requests']==report['idle_after']['model_requests']
        report['idle_counts_unchanged']=report['idle_before']['counts']==report['idle_after']['counts']
        report['idle_watch_enabled']=load(jail/'mail-watch.json',{}).get('enabled') is True
        report['idle_no_new_activity']=report['idle_before']['activity']==report['idle_after']['activity']
        report['status']='PASS' if all(report[k] for k in ['idle_no_model_requests','idle_counts_unchanged','idle_watch_enabled','idle_no_new_activity']) else 'PARTIAL'
        report['ended_at']=time.time();shot(r, a.out/'after-soak.png');save()
    except Exception as e:
        report['status']='PARTIAL';report['error']=str(e);save();raise

if __name__=='__main__':main()
