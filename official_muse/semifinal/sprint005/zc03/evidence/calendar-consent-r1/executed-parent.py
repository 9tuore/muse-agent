#!/usr/bin/env python3
"""Exact consent notice + real create dispatch/guard, explicit synthetic transport."""
import argparse,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
SHA=lambda b:hashlib.sha256(b).hexdigest()
NO="Waiting for the person to allow this app's agent (OctoSense asks the first time)"
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--vm',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=a.source.read_bytes();assert SHA(raw)=='c09836478cdd5fe58f34634002400ebc517185deb30fe4a29a469705c1ac6bd7'
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);(out/'frozen-main.splash').write_bytes(raw)
 spec=importlib.util.spec_from_file_location('parser',H.parents[3]/'official_muse/prelim/tests/calendar_sync/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 f=m.functions_in(raw.decode());old=m.functions_in((H/'evidence/local-projection/r4/frozen-main.splash').read_text())
 sites=['calendar_agent_submit_bound','calendar_agent_update_confirm','calendar_agent_delete_confirm']
 static={n:re.sub(r'calendar_agent_session_notice\(opened,"[^"]*",("[^"]*")\)',r'\1',f[n])==old[n] for n in sites}
 assert all(static.values())
 direct=[]
 def add(name,opened,consent=False):direct.append(dict(name=name,opened=opened,consent=consent))
 add('exact-no-consent',dict(is_ok=False,error=NO),True)
 for name,opened in [('turned-off',dict(is_ok=False,error='Agent is turned off')),('signin',dict(is_ok=False,error='Sign in required')),('unknown',dict(is_ok=False,error='fixture-private-diagnostic')),('nil',None),('array',[]),('missing-is_ok',dict(error=NO)),('is_ok-string',dict(is_ok='false',error=NO)),('is_ok-true',dict(is_ok=True,error=NO)),('error-object',dict(is_ok=False,error=dict(message=NO))),('error-number',dict(is_ok=False,error=12)),('error-too-long',dict(is_ok=False,error='X'*513)),('near-prefix',dict(is_ok=False,error=NO+' ')),('near-case',dict(is_ok=False,error=NO.lower())),('success',dict(is_ok=True,data=dict(open=True))),('malformed-data',dict(is_ok=False,error=NO,data='malformed'))]:add(name,opened,name=='malformed-data')
 dispatch=[]
 def create(name,opened,services,status,consent=False,identity=False,busy=False):dispatch.append(dict(name=name,opened=opened,services=services,status=status,consent=consent,identity=identity,busy=busy))
 create('create-no-consent',dict(is_ok=False,error=NO),['octos.session.open'],'blocked',True)
 create('create-unknown-refusal',dict(is_ok=False,error='fixture-private-diagnostic'),['octos.session.open'],'blocked')
 create('create-turned-off',dict(is_ok=False,error='Agent is turned off'),['octos.session.open'],'blocked')
 create('create-signin',dict(is_ok=False,error='Sign in required'),['octos.session.open'],'blocked')
 create('create-open-false',dict(is_ok=True,data=dict(open=False)),['octos.session.open'],'blocked')
 create('create-malformed-data',dict(is_ok=True,data=[]),['octos.session.open'],'blocked')
 create('create-success',dict(is_ok=True,data=dict(open=True)),['octos.session.open','octos.turn.start','octos.session.history'],'turn_completed')
 create('create-identity-changed',dict(is_ok=True,data=dict(open=True)),['octos.session.open'],'blocked',identity=True)
 create('create-busy-prevented',dict(is_ok=True,data=dict(open=True)),[],'idle',busy=True)
 direct_src=json.dumps(json.dumps(direct,ensure_ascii=False),ensure_ascii=False);dispatch_src=json.dumps(json.dumps(dispatch,ensure_ascii=False),ensure_ascii=False)
 selected=['gm_object','gm_text','gm_string','calendar_agent_session_notice','calendar_agent_submit_bound','calendar_agent_history']
 # Real original functions; only host request receiver is a transport port.
 production='\n'.join(f[n].replace('host.request(','fixture_transport(') for n in selected)
 boundary='''
use mod.math.*
use mod.std.*
let calendar_agent_busy=false let calendar_agent_writable=true let calendar_agent_state={}
let calendar_agent_notice="" let calendar_agent_reply="" let calendar_agent_evidence="" let calendar_agent_details=false
let calendar_agent_preflight={status:"empty"} let calendar_agent_history_settle=false let calendar_agent_history_epoch=0
let gm_user_id="fixture-user" let gm_accounts=["local"]
let fixture_row={} let fixture_services=[] let fixture_saves=[] let fixture_unexpected=0
fn calendar_agent_save(){fixture_saves.push(calendar_agent_state.to_json()) return true}
fn calendar_agent_binding_current(binding){fixture_unexpected=fixture_unexpected+1 return false}
fn calendar_agent_tool_name(name){fixture_unexpected=fixture_unexpected+1 return ""}
fn calendar_agent_receipt_status(row){fixture_unexpected=fixture_unexpected+1 return "unverified"}
fn calendar_agent_link_result(rows){fixture_unexpected=fixture_unexpected+1 return {status:"unknown"}}
fn redraw(){}
fn time_now(){return 100}
fn random_u32(){return 23}
fn fixture_transport(method,args,cb){
 fixture_services.push(method)
 if method=="octos.session.open" {
   if fixture_row.identity {gm_user_id="changed-user"}
   cb(fixture_row.opened) return
 }
 if method=="octos.turn.start" {cb({is_ok:true data:{turn_id:"fixture-turn" text:"synthetic response"}}) return}
 if method=="octos.session.history" {cb({is_ok:false data:nil}) return}
 fixture_unexpected=fixture_unexpected+1
}
'''
 probe='''
let direct_rows=__DIRECT__.parse_json() let create_rows=__DISPATCH__.parse_json() let results=[] let calls=[]
for row in direct_rows {
 let before=row.opened.to_json()
 let notice=calendar_agent_session_notice(row.opened,"提交合成请求","fixture-fallback")
 results.push({name:row.name notice:notice unchanged:before==row.opened.to_json()})
}
for row in create_rows {
 fixture_row=row fixture_services=[] fixture_saves=[]
 calendar_agent_busy=row.busy calendar_agent_writable=true
 calendar_agent_state={schema:1 request_id:"" turn_id:"" status:"idle" user_id:"fixture-user" accounts:["local"].to_json() previous_requests:[]}
 calendar_agent_preflight={status:"empty"} calendar_agent_history_settle=false calendar_agent_history_epoch=0
 calendar_agent_notice="" gm_user_id="fixture-user" gm_accounts=["local"]
 calendar_agent_submit_bound("合成查询请求",nil)
 let before=fixture_services.to_json()
 // Allowing consent later has no handler that replays this declined request.
 gm_user_id="fixture-user"
 let unchanged=before==fixture_services.to_json()
 calls.push({name:row.name notice:calendar_agent_notice services:fixture_services saves:fixture_saves state:calendar_agent_state busy:calendar_agent_busy no_auto_replay:unchanged})
}
({direct:results create:calls unexpected:fixture_unexpected}).to_json()
'''.replace('__DIRECT__',direct_src).replace('__DISPATCH__',dispatch_src)
 executed=boundary+production+'\n'+probe;(out/'executed.splash').write_text(executed)
 identity=dict(source_sha256=SHA(raw),vm_sha256=SHA(a.vm.read_bytes()),runner_sha256=SHA(Path(__file__).read_bytes()),executed_sha256=SHA(executed.encode()),production_functions={n:SHA(f[n].encode()) for n in selected},static_original_guard_and_body_unchanged_after_notice_normalization=static,altered_transport_only=True,synthetic_in_memory_save_adapter=True)
 (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');(out/'cases.json').write_text(json.dumps(dict(direct=direct,create=dispatch),ensure_ascii=False,indent=2)+'\n');(out/'parent-command.json').write_text(json.dumps([sys.executable,*sys.argv],indent=2)+'\n')
 cmd=[str(a.vm.resolve()),str(out/'executed.splash'),'--rpc'];(out/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
 proc=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/'stdout.log').write_text(proc.stdout);(out/'stderr.log').write_text(proc.stderr)
 report=dict(status='ERROR',returncode=proc.returncode,identity=identity,boundary='Actual CLI Splash VM, synthetic open/turn/history transport and in-memory save recorder. Not GUI/Kernel consent, storage, Calendar execution, or real session acceptance.')
 if proc.returncode==0 and not proc.stderr:
  actual=json.loads(proc.stdout.removeprefix('MUSE_VM_RESULT ').strip());failed=[]
  for row,r in zip(direct,actual['direct']):
   expected='宿主已发出启用 Muse 助手的申请；授权完成后，请重新提交合成请求。本次尚未派发日历操作，不会自动重发。' if row['consent'] else 'fixture-fallback'
   r['passed']=r['name']==row['name'] and r['notice']==expected and r['unchanged']
   if not r['passed']:failed.append(row['name'])
  fallback='官方会话未打开或账号已变化；未派发日历请求。请检查宿主助手授权与模型。'
  for row,r in zip(dispatch,actual['create']):
   notice='宿主已发出启用 Muse 助手的申请；授权完成后，请重新提交所选日历请求。本次尚未派发日历操作，不会自动重发。' if row['consent'] else fallback
   ok=r['name']==row['name'] and r['services']==row['services'] and r['state']['status']==row['status'] and r['no_auto_replay'] and r['busy']==row['busy']
   if row['status']=='blocked':ok=ok and r['notice']==notice and r['state']['turn_id']=='' and len(r['saves'])==2
   if row['status']=='turn_completed':ok=ok and r['state']['turn_id']=='fixture-turn'
   r['passed']=ok
   if not ok:failed.append(row['name'])
  if actual['unexpected']:failed.append('unexpected-fixture-dependency-called')
  report.update(status='FIXTURE_PASS' if not failed else 'FAIL',failed=failed,actual=actual,cases=len(direct)+len(dispatch))
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report.get(k) for k in ['status','cases','failed','returncode']},ensure_ascii=False))
 return 0 if report['status']=='FIXTURE_PASS' else 1
if __name__=='__main__':raise SystemExit(main())
