#!/usr/bin/env python3
"""Independent synthetic inputs/oracles; production code and prompts are untouched."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json
OWN=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--schemas',type=Path,default=OWN/'PUBLIC_CONTRACT_SCHEMAS.json')
args=parser.parse_args()
OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
capture=args.schemas
schemas=json.loads(capture.read_text())
def j(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
wire=[];seen=set()
def addwire(category,schema,raw,expected):
 signature=hashlib.sha256(j([schema,raw,expected]).encode()).hexdigest()
 if signature in seen:return
 seen.add(signature);wire.append({'id':'W%04d'%(len(wire)+1),'category':category,'schema':copy.deepcopy(schema),'raw':raw,'expected':expected,'input_sha256':signature})
bases={'reply':{'reply':'合成回答仅作候选。'},'mail':{'to':'recipient@example.invalid','subject':'合成主题','body':'仅起草，等待单独确认。'},'calendar':{'title':'合成讨论','start':'2032-03-01T15:00:00+08:00','end':'2032-03-01T16:00:00+08:00','time_zone':'Asia/Shanghai','location':''},'goal':{'objective':'整理本轮合成资料','source':'仅本轮用户给出的合成资料'}}
for action,schema in schemas.items():
 base=bases[action];addwire('valid_'+action,schema,j(base),'VALID')
 for field,rule in schema['properties'].items():
  value=copy.deepcopy(base);value.pop(field);addwire('missing_'+field,schema,j(value),'SCHEMA_ERROR')
  for wrong in [None,True,False,7,[],{}]:
   value=copy.deepcopy(base);value[field]=wrong;addwire('wrong_type_'+field,schema,j(value),'SCHEMA_ERROR')
  limit=rule['maxLength']
  for char in ['a','中','😀']:
   for size in [0,limit-1,limit,limit+1]:
    value=copy.deepcopy(base);value[field]=char*size;addwire('unicode_boundary_'+field,schema,j(value),'VALID' if size<=limit else 'SCHEMA_ERROR')
 for field in ['event_id','source_id','source_quote','sender','message_id','account','calendar_id','memory_refs','sent','executed','approval','intent','unknown','provider']:
  value=copy.deepcopy(base);value[field]='hallucinated:'+field;addwire('untrusted_extra_'+field,schema,j(value),'SCHEMA_ERROR')
 for root in [None,True,1,[],[base],'string']:
  addwire('wrong_root_'+action,schema,j(root),'SCHEMA_ERROR')
 raw=j(base)
 for malformed in [raw[:-1],raw[:len(raw)//2],raw+',',raw+' trailing',"{",'{"broken":',raw.replace(':',':,',1),'not JSON']:
  addwire('invalid_or_truncated_'+action,schema,malformed,'JSON_ERROR')
# Schema compilation failures are explicit, rather than pretending unsupported rules run.
for keyword,value in [('oneOf',[]),('pattern','x'),('format','date-time'),('const','x')]:
 schema=copy.deepcopy(schemas['reply']);schema[keyword]=value;addwire('unsupported_schema_'+keyword,schema,j(bases['reply']),'SCHEMA_COMPILE_ERROR')
(OUT/'wire-cases.json').write_text(j(wire)+'\n')
app=[];app_seen=set()
def addapp(category,kind,data,expected):
 signature=hashlib.sha256(j([kind,data,expected]).encode()).hexdigest()
 if signature in app_seen:return
 app_seen.add(signature);app.append(dict(id='A%04d'%(len(app)+1),category=category,kind=kind,data=data,expected=expected,input_sha256=signature))
# Epoch arithmetic is computed by Python's independent timezone/datetime implementation.
anchors=[datetime.datetime(2029,12,31,23,59,59),datetime.datetime(2032,2,28,23,59,59),datetime.datetime(2032,2,29,23,59,59),datetime.datetime(2032,3,31,23,59,59),datetime.datetime(2030,4,30,23,59,59),datetime.datetime(2099,12,31,23,59,59)]
for anchor in anchors:
 for shift in [-1,0,1,60,3600]:
  for offset in [-720,0,330,480,840]:
   dt=(anchor+datetime.timedelta(seconds=shift)).replace(tzinfo=datetime.timezone(datetime.timedelta(minutes=offset)))
   iso=dt.isoformat(timespec='seconds');addapp('date_month_year_timezone','epoch',{'value':iso},dt.timestamp())
for fraction in [0.1,0.123,0.123456]:
 dt=datetime.datetime(2032,3,1,0,0,0,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=fraction)
 addapp('fractional_seconds','epoch',{'value':dt.isoformat()},dt.timestamp())
invalid=['2031-02-29T15:00:00+08:00','2032-02-30T15:00:00+08:00','2032-04-31T15:00:00+08:00','2032-00-10T15:00:00Z','2032-13-10T15:00:00Z','2032-03-00T15:00:00Z','2032-03-32T15:00:00Z','2032-03-01T24:00:00Z','2032-03-01T15:60:00Z','2032-03-01T15:00:60Z','2032-03-01T15:00:00+24:00','2032-03-01T15:00:00-24:00','2032-03-01T15:00:00+08:60','2032-03-01T15:00:00+99:00','2032-03-01T15:00:00.','2032-03-01T15:00:00Z junk','2032-03-01 15:00:00Z','2032-3-1T15:00:00Z','2032-03-01T15:00Z','2032-03-01T15:00:00']
for value in invalid:addapp('invalid_calendar_time','epoch',{'value':value},None)
for value in invalid[:14]:addapp('memory_timestamp_validity','memory_time',{'value':value},False)
for hour in [0,1,8,12,15,19,23]:
 for relative in ['明天','后天','大后天']:
  intent='%s%d点再讨论'%(relative,hour)
  addapp('relative_reply_time_preserved','reply_match',{'intent':intent,'body':'那就%s%d点再讨论。'%(relative,hour)},True)
  wrong='今天' if relative!='今天' else '明天'
  addapp('relative_reply_time_invented','reply_match',{'intent':intent,'body':'那就%s%d点再讨论。'%(wrong,hour)},False)
  addapp('reply_hour_changed','reply_match',{'intent':intent,'body':'那就%s%d点再讨论。'%(relative,(hour+1)%24)},False)
for text in ['拒绝','算了','不方便','不参加','不同意']:
 addapp('refusal_not_flipped','reply_match',{'intent':text,'body':'好的，我会参加。'},False)
 addapp('refusal_preserved','reply_match',{'intent':text,'body':'不好意思，这次不方便，先不约了。'},True)
for text in ['不用了','不用了。','取消','取消这个任务','算了','停止这个任务','不要继续']:
 addapp('explicit_cancel','cancel',{'text':text},True)
for text in ['不要取消','不用了，改到后天','不要取消原来的安排']:
 addapp('cancel_negation_or_compound','cancel',{'text':text},False)
# Source/IDs are injected as untrusted metadata; they must never become system facts.
for action in ['mail_compose','calendar_candidate','goal_plan']:
 for extra in ['event_id','source_id','sender','source_quote','message_id','approval','executed']:
  payload=copy.deepcopy(bases[{'mail_compose':'mail','calendar_candidate':'calendar','goal_plan':'goal'}[action]])
  payload[extra]='hallucinated:'+extra
  messages={'mail_compose':'请起草邮件给recipient@example.invalid，内容只是合成资料。','calendar_candidate':'请安排2032年3月1日15点到16点的合成讨论。','goal_plan':'请整理本轮合成资料并准备任务计划。'}
  addapp('untrusted_metadata_not_fact','proposal_metadata',{'action':action,'message':messages[action],'output':{'intent':action,'proposal':payload},'extra':extra},True)
for action in ['mail.send','calendar.delete','execute','run_shell','system_fact','confirmed','unknown_action','memory_write']:
 addapp('unknown_action_enum','proposal_reject',{'message':'请安排日程并起草邮件。','output':{'intent':action,'proposal':{}}},True)
for action,texts in [('calendar_candidate',['先别改','不要修改','不用调整','暂时别改时间','现在先不要推迟','先别提前','不要调整原来的安排','保持原来的安排']),('mail_compose',['先别改收件人','不要修改这封邮件','不用重新起草','不要回复','先别回复','暂时不要发邮件','不要改正文','保持原来的邮件'])]:
 for text in texts:addapp('negative_edit_preserves_candidate','no_change',{'action':action,'message':text},True)
(OUT/'app-cases.json').write_text(j(app)+'\n')
manifest={'wire_cases':len(wire),'app_cases':len(app),'total_distinct_inputs':len(wire)+len(app),'captured_source_sha256':'f05de20e1d83957758cc761b560887ffc30efc31affe31c33d7832c49feb4605','schemas_sha256':hashlib.sha256(capture.read_bytes()).hexdigest(),'wire_sha256':hashlib.sha256((OUT/'wire-cases.json').read_bytes()).hexdigest(),'app_sha256':hashlib.sha256((OUT/'app-cases.json').read_bytes()).hexdigest(),'oracle':'Schema expectations are derived from declared contracts/mutations, not production answers. Dates use Python datetime, not copied Splash arithmetic. Reply/candidate expectations follow user intent and no-side-effect requirements. No production prompts or outputs are hardcoded for benchmark.'}
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(manifest,ensure_ascii=False,indent=2))
