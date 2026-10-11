"""Real-service/Relay failure cases on owned marked state; all consent is fixture."""
from pathlib import Path
import hashlib,json,select,subprocess
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
BINARY=OWN/'build/gpt01-calendar-history/target/debug/gpt01-night004-relay-jsonl'
OWNER=OWN/'build/gpt01-calendar-history/target/debug/gpt01-night004-calendar'
OUT=OWN/'build/night-004/gpt01-night004-l4-r1'
OUT.mkdir(parents=True,exist_ok=False)
(OUT/'FIXTURE_ONLY').write_text('Synthetic L4 fixture only; no user consent\n')
STORE=OUT/'calendar/events.json'
rows=[];processes=[]
def sha():return hashlib.sha256(STORE.read_bytes()).hexdigest() if STORE.is_file() else None
def start():
 p=subprocess.Popen([str(BINARY),str(OUT)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
 processes.append(p.pid);return p
def stop(p):
 p.stdin.close();assert p.wait(timeout=10)==0
 err=p.stderr.read();assert not err,err
 p.stdout.close();p.stderr.close()
def call(p,label,method,args,**extra):
 req={'method':method,'args':args,'scope':{'caller':'card.muse-goals','owner':'os.calendar','account':'fixture-account','fixture_consent':True,'granted':True}}
 if method in ['calendar.add_event','calendar.update_event','calendar.remove_event']:req['fixture_approval']='once'
 req.update(extra);before=sha()
 p.stdin.write(json.dumps(req)+'\n');p.stdin.flush();assert select.select([p.stdout],[],[],10)[0],label
 line=p.stdout.readline();assert line,line
 reply=json.loads(line);rows.append({'step':label,'request':req,'reply':reply,'before_store_sha256':before,'after_store_sha256':sha(),'process_id':p.pid})
 return reply
def ok(r):assert r['is_ok'],r;return r['data']
def fails(r,kind=None):
 assert not r['is_ok'],r
 if kind:assert r['error']['kind']==kind,r
 return r['error']['message']
def unchanged(r):
 assert rows[-1]['before_store_sha256']==rows[-1]['after_store_sha256'],rows[-1]
 return r
add={'title':'L4 synthetic','start':'2026-10-13T15:00','end':'2026-10-13T15:30','timezone':'Asia/Shanghai','location':'Fixture room A','notes':'Fixture initial notes','request_id':'night004-l4-stable'}
p=start()
created=ok(call(p,'create','calendar.add_event',add));event_id=created['id']
old=ok(call(p,'get_created','calendar.get_event',{'id':event_id}))['event']
retry=ok(unchanged(call(p,'same_process_stable_retry','calendar.add_event',add)));assert retry['reused'] and retry['id']==event_id
assert rows[-1]['reply']['store_event_count']==1
stop(p);p=start()
retry=ok(unchanged(call(p,'restart_stable_retry','calendar.add_event',add)));assert retry['reused'] and retry['id']==event_id
assert rows[-1]['reply']['store_event_count']==1
# Another real owner-service process edits the same marked store, no fabricated event JSON.
external={'id':event_id,'expected':old,'title':'L4 external edit','start':'2026-10-13T16:00','end':'2026-10-13T16:45','timezone':'Asia/Shanghai','location':'Fixture room B','notes':'Fixture external notes'}
req={'owner':'os.calendar','method':'update_event','args':external};before=sha()
r=subprocess.run([str(OWNER),str(OUT)],input=json.dumps(req),text=True,capture_output=True,timeout=10)
assert r.returncode==0,r.stderr
reply=json.loads(r.stdout);assert reply['result']['ok'],reply
rows.append({'step':'external_real_owner_service_update','request':req,'reply':reply,'before_store_sha256':before,'after_store_sha256':sha()})
current=ok(call(p,'get_external_edit','calendar.get_event',{'id':event_id}))['event']
assert current['id']==event_id and current['request_id']==add['request_id']
assert all(current[k]==external[k] for k in ['title','start','end','timezone','location','notes'])
fails(unchanged(call(p,'old_expected_update_refused','calendar.update_event',external)),'calendar_error')
fails(unchanged(call(p,'old_expected_remove_refused','calendar.remove_event',{'id':event_id,'expected':old})),'calendar_error')
assert 'different saved event' in fails(unchanged(call(p,'old_request_data_conflict_no_duplicate','calendar.add_event',add)),'calendar_error')
remove={'id':event_id,'expected':current}
fails(unchanged(call(p,'revoke_grant_after_router_approval','calendar.remove_event',remove,revoke_after_approval=True)),'not_granted')
assert rows[-1]['reply']['executor_calls']==[] and rows[-1]['reply']['approval_trace'][0]['approved'] is True
fails(unchanged(call(p,'router_denied_remove','calendar.remove_event',remove,fixture_approval='deny')),'fixture_approval_refused')
assert rows[-1]['reply']['executor_calls']==[] and rows[-1]['reply']['approval_trace'][0]['approved'] is False
for label,scope,kind in [
 ('missing_consent',{'caller':'card.muse-goals','fixture_consent':False,'granted':True},'consent_pending'),
 ('revoked_grant',{'caller':'card.muse-goals','fixture_consent':True,'granted':False},'not_granted'),
 ('wrong_caller',{'caller':'card.other-fixture','fixture_consent':True,'granted':True},'not_granted'),
 ('owner_withdrawn',{'caller':'card.muse-goals','fixture_consent':True,'granted':True,'withdrawn':['os.calendar']},'app_unavailable')]:
 fails(unchanged(call(p,label,'calendar.get_event',{'id':event_id},scope=scope)),kind)
 assert rows[-1]['reply']['executor_calls']==[]
fails(unchanged(call(p,'missing_expected_before_dispatch','calendar.remove_event',{'id':event_id})),'invalid_args')
assert rows[-1]['reply']['executor_calls']==[]
before=sha();p.stdin.write('{broken transport\n');p.stdin.flush();assert select.select([p.stdout],[],[],10)[0]
reply=json.loads(p.stdout.readline());assert reply['error']['kind']=='bad_json' and sha()==before
rows.append({'step':'bad_transport_json','raw_input':'{broken transport','reply':reply,'before_store_sha256':before,'after_store_sha256':sha()})
assert ok(call(p,'alive_after_bad_transport_json','calendar.get_event',{'id':event_id}))['event']==current
# Corrupt only the synthetic fixture store and retain both exact byte hashes.
saved=STORE.read_bytes();STORE.write_bytes(b'[broken synthetic store')
fails(unchanged(call(p,'bad_store_read_refused','calendar.get_event',{'id':event_id})),'calendar_error')
new_add={**add,'request_id':'night004-l4-while-broken'}
fails(unchanged(call(p,'bad_store_write_refused','calendar.add_event',new_add)),'calendar_error')
assert STORE.read_bytes()==b'[broken synthetic store';STORE.write_bytes(saved)
# The actual service writes .events-PID.json; an owned directory here forces a real filesystem error.
blocker=OUT/f'calendar/.events-{p.pid}.json';blocker.mkdir()
edit={**external,'expected':current,'title':'L4 recovered edit','start':'2026-10-13T17:00','end':'2026-10-13T17:30','location':'Fixture room C','notes':'Fixture recovered notes'}
assert 'cannot keep events' in fails(unchanged(call(p,'actual_filesystem_write_failure','calendar.update_event',edit)),'calendar_error')
blocker.rmdir()
updated=ok(call(p,'retry_after_write_failure','calendar.update_event',edit))['event'];assert updated['id']==event_id and updated['request_id']==add['request_id']
assert all(updated[k]==edit[k] for k in ['title','start','end','timezone','location','notes'])
assert rows[-1]['reply']['store_event_count']==1
assert ok(call(p,'remove_current','calendar.remove_event',{'id':event_id,'expected':updated}))['removed']
assert rows[-1]['reply']['store_event_count']==0
stop(p);p=start()
assert ok(call(p,'restart_get_absent','calendar.get_event',{'id':event_id}))=={'found':False,'event':None}
assert rows[-1]['reply']['store_event_count']==0;stop(p)
# Reject an unmarked path before a process can take a request.
unmarked=OWN/'build/night-004/gpt01-night004-unmarked-r1';unmarked.mkdir(exist_ok=False)
r=subprocess.run([str(BINARY),str(unmarked)],input='',capture_output=True,text=True,timeout=10)
assert r.returncode==2 and not unmarked.joinpath('calendar').exists()
rows.append({'step':'unmarked_root_refused','exit_code':r.returncode,'stderr':r.stderr.strip(),'side_effect_count':0})
receipt={'state':'REAL_CALENDAR_RELAY_L4_SYNTHETIC_FIXTURE_PASS','level':'L4 failure component fixture','helper_binary':str(BINARY),'helper_sha256':hashlib.sha256(BINARY.read_bytes()).hexdigest(),'owner_binary_sha256':hashlib.sha256(OWNER.read_bytes()).hexdigest(),'host_dir':str(OUT),'steps':rows,'distinct_jsonl_processes':processes,'final_event_count':0,'stable_retry_event_count':1,'duplicate_records_created':0,'kernel':False,'gui':False,'fixture_authorization':True,'fixture_external_editor':'separate actual CalendarService process','write_failure':'Actual std::fs::write error caused by owned .events-PID.json directory; original events.json bytes preserved','scope':'Real Relay/Schema/Router and owner CalendarService. Installed admission/consent/grants/sheet gestures and transport IDs are synthetic. No fabricated KernelHistory/Muse receipt; no shared SDK/target writes.'}
(HERE/'L4_RESULT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'state':receipt['state'],'steps':len(rows),'processes':processes,'duplicate_records_created':0,'final_event_count':0,'helper_sha256':receipt['helper_sha256']}))
