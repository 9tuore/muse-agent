#!/usr/bin/env python3
"""Authorized synthetic dynamic precondition test in real Shell, external Calendar actor."""
from pathlib import Path
import sys,time,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase2/tests'))
from remote import Remote
from live_calendar_crud import click,text,reach
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'official_muse/app/build/round2';OUT=B/'live-calendar';OUT.mkdir(exist_ok=True)
candidate=json.loads((ROOT/'official_muse/round2/candidate.json').read_text())
r=Remote(8500);req=json.loads((B/'c01-request.json').read_text());title=req['test_id']+'-PRECONDITION';external=req['test_id']+'-CONFLICT'
r.click('日历');reach(r,'刷新宿主授权状态');time.sleep(.3)
label=next(w['t'] for w in r.widgets() if w.get('t','').startswith('工作 · ') and w['t'].endswith(' · 可写'))
click(r,label)
for field,value in [('calendar_title',title),('calendar_start',req['start']),('calendar_end',req['end']),('calendar_timezone','Asia/Shanghai'),('calendar_location','Muse synthetic acceptance')]:text(r,field,value)
click(r,'查询当前候选冲突');time.sleep(.5);click(r,'预览精确日历操作');reach(r,'确认执行这项系统日历操作');r.shot(OUT/'t0-waiting-user.png')
script=Path(__file__).with_name('external_calendar.applescript')
# One call; a timeout/unknown result is reconciled rather than retried.
assert subprocess.check_output(['osascript',str(script),'get',external],text=True,timeout=30).strip()=='NOT_FOUND'
created=None
try:
    created=subprocess.check_output(['osascript',str(script),'create',external],text=True,timeout=90).strip()
    readback=subprocess.check_output(['osascript',str(script),'get',external],text=True,timeout=30).strip();assert readback==created
    click(r,'确认执行这项系统日历操作');time.sleep(1)
    jail=B/'calendar-apps/muse-goals';store=jail/'goals.json'
    state=json.loads(store.read_text()) if store.exists() else {'actions': []}
    assert not [a for a in state['actions'] if a['service']=='calendar.create'], 'stale approval performed a mutation'
    act=json.loads((jail/'activity.json').read_text());kinds=[x['kind'] for x in act]
    assert all(k in kinds for k in ['PRECONDITION_REFRESH','STALE_APPROVAL','EXTERNAL_STATE_CHANGED'])
    r.scroll(815,440,-10000);r.shot(OUT/'t1-stale-blocked.png')
finally:
    # Reconcile the exact authorized external test, even if a later assertion fails.
    found=subprocess.check_output(['osascript',str(script),'get',external],text=True,timeout=30).strip()
    if found!='NOT_FOUND':
        subprocess.run(['osascript',str(script),'delete',external],check=True,timeout=30,capture_output=True)
    assert subprocess.check_output(['osascript',str(script),'get',external],text=True,timeout=30).strip()=='NOT_FOUND'
report={'candidate':candidate['muse_commit'],'bundle_version':'0.2.16','test_id':req['test_id'],
        'test_kind':'REAL_EXTERNAL_SERVICE','external_actor':'macOS Calendar AppleScript API','external_uid':created,
        'initial_no_conflict':True,'waiting_user_before_external_change':True,'approval_blocked':True,'mutation_count':0,
        'activity_kinds':kinds,'external_conflict_cleaned':True,'system_race_eliminated_claim':False}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False),flush=True)
