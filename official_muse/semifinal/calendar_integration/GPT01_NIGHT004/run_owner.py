from pathlib import Path
import hashlib,json,subprocess,tempfile,time
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
MANIFEST=OWN/'build/gpt01-night004-calendar/service/Cargo.toml'
TARGET=OWN/'build/gpt01-calendar-history/target'
binary=TARGET/'debug/gpt01-night004-calendar'
subprocess.run(['cargo','generate-lockfile','--offline','--manifest-path',str(MANIFEST)],check=True)
cmd=['nice','-n','10','cargo','build','--offline','--locked','--manifest-path',str(MANIFEST),'--target-dir',str(TARGET),'-j','1','--bin','gpt01-night004-calendar']
start=time.monotonic()
with (HERE/'owner-build.log').open('w') as log: build=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
assert build.returncode==0,(HERE/'owner-build.log').read_text()[-6000:]
rows=[]
with tempfile.TemporaryDirectory(prefix='gpt01-night004-') as name:
    root=Path(name);(root/'FIXTURE_ONLY').write_text('Synthetic fixture only; never user authorization.\n')
    def call(label,method,args,owner='os.calendar'):
        request={'owner':owner,'method':method,'args':args}
        r=subprocess.run([str(binary),name],input=json.dumps(request),text=True,capture_output=True,timeout=10)
        assert r.returncode==0,r.stderr
        response=json.loads(r.stdout);rows.append({'step':label,'request':request,'response':response})
        return response['result']
    created=call('create','add_event',{'title':'NIGHT004 synthetic','start':'2026-10-13T15:00','timezone':'Asia/Shanghai','request_id':'night004-synthetic-1'})
    assert created['ok']; event_id=created['data']['id']
    read=call('restart_read_same_id','get_event',{'id':event_id});assert read['ok'] and read['data']['found'] and read['data']['event']['id']==event_id
    old=read['data']['event']
    edit={'id':event_id,'expected':old,'title':'NIGHT004 revised','start':'2026-10-13T16:00','timezone':'Asia/Shanghai'}
    updated=call('update_same_id','update_event',edit);assert updated['ok'] and updated['data']['event']['id']==event_id
    current=call('restart_read_updated','get_event',{'id':event_id})['data']['event'];assert current['start']=='2026-10-13T16:00' and current['request_id']==old['request_id']
    before=hashlib.sha256((root/'calendar/events.json').read_bytes()).hexdigest()
    stale=call('old_expected_rejected','remove_event',{'id':event_id,'expected':old});assert not stale['ok'] and 'changed' in stale['error']
    assert hashlib.sha256((root/'calendar/events.json').read_bytes()).hexdigest()==before
    foreign=call('foreign_owner_rejected','remove_event',{'id':event_id,'expected':current},'muse-goals');assert not foreign['ok']
    assert hashlib.sha256((root/'calendar/events.json').read_bytes()).hexdigest()==before
    removed=call('remove_current_snapshot','remove_event',{'id':event_id,'expected':current});assert removed['ok'] and removed['data']['removed'] is True
    for label in ['get_absent','restart_get_absent']:
        absent=call(label,'get_event',{'id':event_id});assert absent['ok'] and absent['data']=={'found':False,'event':None}
    assert json.loads((root/'calendar/events.json').read_text())==[]
    pids=[row['response']['process_id'] for row in rows];assert len(pids)==len(set(pids))
receipt={'state':'REAL_CALENDAR_SERVICE_ISOLATED_RESTART_PASS','command':cmd,'exit_code':build.returncode,'elapsed_seconds':round(time.monotonic()-start,3),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'steps':rows,'distinct_processes':len(rows),'authorization':'Synthetic fixture only; not real Agent/person consent','scope':'Actual unchanged SDK CalendarService::call/handle/storage/ui/cards. Replier/ServiceHost and transport are explicit fixture adapters. No GUI/Host/Kernel/provider build or production profile.'}
(HERE/'OWNER_RESULT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'state':receipt['state'],'distinct_processes':len(rows),'elapsed_seconds':receipt['elapsed_seconds'],'binary_sha256':receipt['binary_sha256']}))
