#!/usr/bin/env python3
"""Test real Splash relay routing and receipt interpretation with synthetic transport."""
import argparse,hashlib,importlib.util,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--vm',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
source=(ROOT/'official_muse/app/source/main.splash').read_text();spec=importlib.util.spec_from_file_location('parser',ROOT/'official_muse/prelim/tests/calendar_sync/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);f=m.functions_in(source)
names='gm_object gm_array gm_text gm_string calendar_receipt_persisted calendar_agent_tool_name calendar_agent_receipt_status calendar_agent_delete_receipt calendar_history_request calendar_relay_run calendar_relay_query calendar_relay_wall_offset calendar_relay_normalize calendar_relay_plan calendar_agent_event_matches calendar_agent_add_digest_matches calendar_agent_creation_proof'.split()
code='''let fs={sha256: |value| mod.fixture.sha256(value)}
let calls=[] let checks=[] let answer=nil let model=nil
let calendar_agent_state={request_id:"request-1" turn_id:"calendar-relay-one" binding:{payload:{title:"Test" start:"2030-12-12T15:00"}} previous_requests:[]}
let calendar_agent_update_state={records:[]} let calendar_agent_delete_state={records:[]}
let calendar_agent_preflight={status:"empty" request_id:""} let chat_selected_id="chat-1"
fn fixture_transport(method,args,callback){calls.push({method:method args:args callback:callback})}
fn time_now(){return 1791864000}
fn page_time_floor(v){return 20739}
fn page_date_parts(day){return {date:"2026-10-13"}}
fn muse_model_request(text,session,goal,current,args,callback){model={text:text callback:callback current:current args:args}}
fn chat_calendar_reference(){return "今天2026-10-13"}
fn chat_payload_error(kind,payload){if payload.title == "" || payload.start == "" {return "请补充标题和时间"} return ""}
fn calendar_agent_wall(value){return value}
fn check(name,passed){checks.push({name:name passed:passed})}
fn receive(r){answer=r}
'''+ '\n'.join(f[n].replace('host.request(', 'fixture_transport(') for n in names)+'''
calendar_relay_plan("create","request-1",{},receive)
check("bound_create_calls_native_without_model",calls[0].method=="calendar_bridge.run" && calls[0].args.operation=="add" && model==nil)
check("bound_payload_is_exact",calls[0].args.args.title=="Test" && calls[0].args.request_id=="request-1")
calls=[] calendar_relay_plan("查看日程","request-2",nil,receive)
check("query_uses_relay",calls[0].args.operation=="query" && calls[0].args.args.limit==200)
calls[0].callback({is_ok:true data:{status:"completed" messages:[{tool_name:"calendar.events" host_calendar_receipt:{terminal:"ok" result:{data:{events:[]}}}}]}})
check("empty_query_display",answer.data.text=="这个时间范围没有日程。")
calls=[] calendar_relay_plan("安排会议2030年12月12日15点","request-3",nil,receive)
check("natural_create_requires_model_parameters",calls.len()==0 && model!=nil)
model.callback({is_ok:true data:{output:{title:"会议" start:"2030-12-12T15:00" end:"2030-12-12T16:00" time_zone:"Asia/Shanghai" location:""}}})
check("parsed_create_reaches_native",calls.len()==1 && calls[0].args.operation=="add" && calls[0].args.args.request_id=="request-3")
calls=[] model.callback({is_ok:true data:{output:{title:"" start:""}}})
check("incomplete_model_output_does_not_write",calls.len()==0 && answer.is_ok==false)
calls=[] calendar_history_request(calendar_agent_state,receive)
check("bridge_history_never_reads_kernel",calls[0].method=="calendar_bridge.history" && calls[0].args.request_id=="request-1")
calls=[] calendar_history_request({turn_id:"old-kernel-turn" request_id:"old"},receive)
check("old_kernel_history_remains_supported",calls[0].method=="octos.session.history")
let row={tool_name:"calendar.get_event" tool_call_id:"tc" host_calendar_receipt:{source:"host_calendar_relay" bridge_persisted:true owner:"os.calendar" caller:"muse-goals" turn_id:"calendar-relay-one" tool_call_id:"tc" call_id:"call" tool:"calendar.get_event" terminal:"ok" result:{"ok":true data:{found:true}}}}
check("durable_real_bridge_receipt_supported",calendar_agent_receipt_status(row)=="ok")
row.host_calendar_receipt.bridge_persisted=false
check("unpersisted_bridge_not_success",calendar_agent_receipt_status(row)=="unverified")
row.host_calendar_receipt.source="model" row.host_calendar_receipt.bridge_persisted=true
check("model_text_not_receipt",calendar_agent_receipt_status(row)=="unverified")
row.host_calendar_receipt.source="broker_tool_result" row.host_calendar_receipt.kernel_persisted=true
check("original_kernel_receipt_still_supported",calendar_agent_receipt_status(row)=="ok")
row.host_calendar_receipt.caller="other-app"
check("foreign_caller_rejected",calendar_agent_receipt_status(row)=="unverified")
calls=[] calendar_history_request({transport:"host_calendar_relay" turn_id:"" request_id:"interrupted"},receive)
check("interrupted_request_recovers_by_id",calls[0].method=="calendar_bridge.history" && calls[0].args.request_id=="interrupted")
let normalized=calendar_relay_normalize({start:"2030-12-12T15:00:00" end:"2030-12-12T16:00" time_zone:"Asia/Shanghai"})
check("explicit_shanghai_missing_offset_normalized",normalized.start=="2030-12-12T15:00:00+08:00" && normalized.end=="2030-12-12T16:00:00+08:00")
let payload={title:"Test" start:"2030-12-12T15:00" end:"2030-12-12T16:00" timezone:"Asia/Shanghai" location:"" notes:"" request_id:"request-1"}
let event=payload.to_json().parse_json() event.id="event-1"
let add_digest="sha256:"+fs.sha256("{\\"end\\":\\"2030-12-12T16:00\\",\\"location\\":\\"\\",\\"notes\\":\\"\\",\\"request_id\\":\\"request-1\\",\\"start\\":\\"2030-12-12T15:00\\",\\"timezone\\":\\"Asia/Shanghai\\",\\"title\\":\\"Test\\"}")
let get_digest="sha256:"+fs.sha256("{\\"id\\":\\"event-1\\"}")
fn proof_row(tool,id,digest,data){return {role:"tool" lane:"person" turn_id:"calendar-relay-one" tool_name:tool tool_call_id:id
 host_calendar_receipt:{source:"host_calendar_relay" bridge_persisted:true owner:"os.calendar" caller:"muse-goals"
 turn_id:"calendar-relay-one" session_id:"calendar-relay:muse:device" call_id:id tool_call_id:id tool:tool args_digest:digest terminal:"ok" result:{"ok":true data:data}}}}
let proof_rows=[proof_row("calendar.add_event","add",add_digest,{id:"event-1" start:payload.start}),proof_row("calendar.get_event","get",get_digest,{found:true event:event})]
check("create_proof_requires_actual_matching_readback",calendar_agent_creation_proof(proof_rows,payload,false).status=="verified")
proof_rows[1].host_calendar_receipt.result.data.event.title="Different"
check("mismatched_readback_never_verified",calendar_agent_creation_proof(proof_rows,payload,false).status!="verified")
mod.std.print("MUSE_VM_RESULT "+checks.to_json())
'''
(a.out/'executed.splash').write_text(code);r=subprocess.run([str(a.vm),str((a.out/'executed.splash').resolve()),'--rpc'],capture_output=True,text=True,timeout=30);(a.out/'stdout.log').write_text(r.stdout);(a.out/'stderr.log').write_text(r.stderr)
report={'boundary':'SPLASH_VM_FIXTURE_NOT_GUI','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'exit':r.returncode,'status':'ERROR'}
if not r.returncode and not r.stderr:
 checks=json.loads(r.stdout.removeprefix('MUSE_VM_RESULT ').strip());report.update(checks=checks,count=len(checks),failed=[x['name'] for x in checks if not x['passed']]);report['status']='FIXTURE_PASS' if not report['failed'] else 'FAIL'
(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'}));raise SystemExit(report['status']!='FIXTURE_PASS')
