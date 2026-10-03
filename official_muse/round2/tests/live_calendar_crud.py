#!/usr/bin/env python3
"""Exact authorized synthetic CRUD through Muse UI in the paired OctoSense Shell."""
import json,sys,time,subprocess,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase2/tests'))
from remote import Remote
from live_calendar_crud import click,text,reach
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'official_muse/app/build/round2';OUT=B/'live-calendar-crud';OUT.mkdir(exist_ok=True)
JAIL=B/'calendar-apps/muse-goals';r=Remote(8500)
candidate=json.loads((ROOT/'official_muse/round2/candidate.json').read_text())
assert hashlib.sha256((JAIL/'bundle/main.splash').read_bytes()).hexdigest()==candidate['bundle_files_sha256']['main.splash']
req=json.loads((B/'c01-request.json').read_text());title=req['test_id']+'-PRECONDITION'
script=Path(__file__).with_name('external_calendar.applescript')
assert subprocess.check_output(['osascript',str(script),'get',title],text=True,timeout=30).strip()=='NOT_FOUND', 'reconcile existing event first'

def receipt(service):
    end=time.monotonic()+40
    while time.monotonic()<end:
        f=JAIL/'calendar-state.json'
        data=json.loads(f.read_text()) if f.exists() else {'receipts':[]}
        rows=[x for x in data['receipts'] if x['service']==service]
        if rows and rows[-1]['status']=='verified':return rows[-1]
        time.sleep(.2)
    raise AssertionError('no verified receipt; inspect UI before any retry: '+service)

def approve(stage):
    click(r,'预览精确日历操作');reach(r,'确认执行这项系统日历操作');r.shot(OUT/(stage+'-approval.png'))
    click(r,'确认执行这项系统日历操作')
    row=receipt('calendar.'+stage);(OUT/(stage+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2))
    reach(r,'刷新宿主授权状态');r.shot(OUT/(stage+'-readback.png'));print(stage,row['status'],row['event_id'],flush=True)
    return row

def select_event():
    text(r,'calendar_range_start','2026-10-04T00:00:00+08:00');text(r,'calendar_range_end','2026-10-05T00:00:00+08:00')
    click(r,'查询选中日历与范围');time.sleep(.8)
    reach(r,title)
    buttons=[w for w in r.widgets() if w.get('ty')=='Button' and w.get('t')=='选中此系统事件']
    # This authorized range is independently checked below to contain only this synthetic event.
    assert len(buttons)==1,'ambiguous event; do not select unrelated calendar data'
    click(r,'选中此系统事件')

r.click('日历');reach(r,'刷新宿主授权状态')
label=next(w['t'] for w in r.widgets() if w.get('t','').startswith('工作 · ') and w['t'].endswith(' · 可写'));click(r,label);click(r,'新建')
for field,value in [('calendar_title',title),('calendar_start',req['start']),('calendar_end',req['end']),('calendar_timezone','Asia/Shanghai'),('calendar_location','Muse synthetic acceptance')]:text(r,field,value)
click(r,'查询当前候选冲突');time.sleep(.5)
created=approve('create')
uid=subprocess.check_output(['osascript',str(script),'get',title],text=True,timeout=30).strip();assert uid!='NOT_FOUND'
select_event();click(r,'修改所选');text(r,'calendar_location','Muse synthetic acceptance updated');click(r,'查询当前候选冲突');time.sleep(.5)
updated=approve('update');assert updated['event_id']==created['event_id']
assert subprocess.check_output(['osascript',str(script),'get',title],text=True,timeout=30).strip()==uid
select_event();click(r,'删除所选');text(r,'calendar_delete_id',title)
deleted=approve('delete');assert deleted['event_id']==created['event_id']
assert subprocess.check_output(['osascript',str(script),'get',title],text=True,timeout=30).strip()=='NOT_FOUND'
state=json.loads((JAIL/'goals.json').read_text());rows=[a for a in state['actions'] if a['service'].startswith('calendar.')]
assert len(rows)==3 and all(a['status']=='verified' for a in rows)
report={'candidate':candidate['muse_commit'],'bundle_version':candidate['bundle_version'],'test_kind':'REAL_EXTERNAL_SERVICE','test_id':title,'create_readback':True,'update_readback':True,'delete_readback_absent':True,'external_calendar_uid':uid,'calendar_host_event_id':created['event_id'],'mutation_count':3,'cleaned':True,'receipts':{'create':created,'update':updated,'delete':deleted}}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('CRUD PASS and cleaned',flush=True)
