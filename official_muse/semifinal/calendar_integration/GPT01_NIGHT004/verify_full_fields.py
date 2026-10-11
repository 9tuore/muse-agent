"""Narrow actual CalendarService sanity for NIGHT004 Kernel fixture arguments."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
binary=OWN/'build/gpt01-calendar-history/target/debug/gpt01-night004-calendar'
rows=[]
with tempfile.TemporaryDirectory(prefix='gpt01-night004-fields-') as name:
 root=Path(name);(root/'FIXTURE_ONLY').write_text('Synthetic fixture only\n')
 def call(method,args):
  request={'owner':'os.calendar','method':method,'args':args}
  r=subprocess.run([str(binary),name],input=json.dumps(request),text=True,capture_output=True,timeout=10)
  assert r.returncode==0,r.stderr
  response=json.loads(r.stdout);assert response['result']['ok'],response
  rows.append({'request':request,'response':response});return response['result']['data']
 request_id='night004-real-kernel-synthetic'
 add={'title':'NIGHT004 synthetic','start':'2026-10-13T15:00','end':'2026-10-13T15:30','timezone':'Asia/Shanghai','location':'Synthetic room A','notes':'Synthetic initial notes','request_id':request_id}
 created=call('add_event',add);old=call('get_event',{'request_id':request_id})['event']
 assert all(old[k]==v for k,v in add.items())
 before=(root/'calendar/events.json').read_bytes()
 retry=call('add_event',add);assert retry['id']==created['id'] and retry['reused'] is True
 assert (root/'calendar/events.json').read_bytes()==before
 stored=call('events',{})['events'];assert stored==[old]
 update={'id':created['id'],'expected':old,'title':'NIGHT004 revised','start':'2026-10-13T16:00','end':'2026-10-13T16:45','timezone':'Asia/Shanghai','location':'Synthetic room B','notes':'Synthetic revised notes'}
 call('update_event',update)
 current=call('get_event',{'id':created['id']})['event']
 assert current['id']==created['id'] and current['request_id']==request_id
 assert all(current[k]==update[k] for k in ['title','start','end','timezone','location','notes'])
 assert len(call('events',{})['events'])==1
receipt={'state':'REAL_CALENDAR_SERVICE_FULL_FIELDS_AND_STABLE_REQUEST_RETRY_PASS','level':'L1 owner-service','binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'steps':rows,'side_effect_event_count':1,'retry_store_bytes_unchanged':True,'id_and_request_id_preserved':True,'kernel':False,'fixture_authorization':True,'scope':'Seven independent actual CalendarService calls on an empty marked temporary fixture. No Cargo/GUI/shared SDK writes; not the newly prepared Kernel test.'}
(HERE/'OWNER_FULL_FIELDS_RESULT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'state':receipt['state'],'steps':len(rows),'side_effect_event_count':1}))
