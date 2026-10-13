#!/usr/bin/env python3
"""Exercise real transaction functions; transport and storage boundaries are fixtures."""
import argparse,hashlib,importlib.util,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--vm',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
source=(root/'official_muse/app/source/main.splash').read_text();spec=importlib.util.spec_from_file_location('parser',root/'official_muse/prelim/tests/calendar_sync/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);f=m.functions_in(source)
names=[n for n in f if n.startswith('showcase_') and n not in ['showcase_paint','showcase_switch']]+['gm_object','gm_array','gm_text','gm_number','page_time_floor','page_two','page_month_days','page_date_parts','page_parse_date','page_day_number']
code='''use mod.std.*
use mod.math.*
let files={} let calls=[] let checks=[] let fail_write=false
let fs={exists: |p| files[p]!=nil}
fn storage_write(p,v){if fail_write {return "disk"} files[p]=v return nil}
fn storage_read(p){if files[p]==nil {return ""} return files[p]}
fn time_now(){return 1791888000}
fn random_u32(){return 1234}
fn start_timeout(t,callback){callback()}
fn showcase_paint(){}
fn transport(method,args,callback){calls.push({method:method args:args callback:callback})}
fn check(name,passed){checks.push({name:name passed:passed})}
let showcase_open=true let showcase_busy=false let showcase_restored=false let showcase_detail=false
let showcase_notice="" let showcase_model_epoch=0
'''+ '\n'.join(f[n].replace('host.request(', 'transport(') for n in names)+'''
let showcase_state=showcase_empty()
showcase_start()
check("memory_saved_before_model",files["showcase-memory.json"]!=nil && calls.len()==1 && calls[0].method=="model.complete")
calls[0].callback({is_ok:true data:{output:{tool:"calendar.events"}}})
check("model_choice_opens_real_session",calls[1].method=="octos.session.open")
calls[1].callback({is_ok:true data:{open:true}})
check("query_calls_native_bridge",calls[2].method=="calendar_bridge.run" && calls[2].args.operation=="query" && calls[2].args.args.from!=calls[2].args.args.to)
fn receipt(tool,data){return {tool_name:tool tool_call_id:"one" host_calendar_receipt:{source:"host_calendar_relay" bridge_persisted:true owner:"os.calendar" caller:"muse-goals" tool:tool tool_call_id:"one" terminal:"ok" result:{"ok":true data:data}}}}
calls[2].callback({is_ok:true data:{status:"completed" messages:[receipt("calendar.events",{events:[]})]}})
check("draft_written_after_query",showcase_state.phase=="ready_for_review" && files["showcase-draft.json"].parse_json().sent==false && showcase_state.draft.search("15:00")>=0)
showcase_calendar_write()
let write=calls[calls.len()-1]
check("explicit_add_uses_correct_native_dto",write.args.operation=="add" && write.args.args.start==showcase_state.date+"T15:00" && write.args.args.timezone=="Asia/Shanghai")
let ev=write.args.args.to_json().parse_json() ev.id="real-owner-id" ev.request_id=write.args.request_id
write.callback({is_ok:true data:{status:"completed" messages:[receipt("calendar.get_event",{found:true event:ev})]}})
check("write_requires_matching_owner_readback",showcase_state.calendar_status=="saved" && showcase_state.calendar_event.id=="real-owner-id")
let before=calls.len() showcase_calendar_write()
check("saved_button_does_not_repeat_write",calls.len()==before)
showcase_change()
check("new_information_invalidates_old_draft",files["showcase-draft.json"].parse_json().status=="superseded" && showcase_state.revision==2 && showcase_state.calendar_status=="outdated")
check("goal_memory_and_original_event_kept",showcase_state.calendar_event.id=="real-owner-id" && files["showcase-memory.json"].parse_json().preference==showcase_state.preference)
calls[calls.len()-1].callback({is_ok:true data:{output:{tool:"draft.prepare"}}})
check("new_draft_uses_new_time",showcase_state.draft.search("16:00—17:00")>=0 && showcase_state.draft.search("15:00")<0)
showcase_calendar_write() let update=calls[calls.len()-1]
check("update_targets_same_id_and_expected_snapshot",update.args.operation=="update" && update.args.args.id=="real-owner-id" && update.args.args.expected.start==ev.start && update.args.args.start==showcase_state.date+"T16:00")
let updated=ev.to_json().parse_json() updated.start=update.args.args.start updated.end=update.args.args.end
update.callback({is_ok:true data:{status:"completed" messages:[receipt("calendar.get_event",{found:true event:updated})]}})
check("update_success_only_after_new_time_readback",showcase_state.calendar_status=="saved" && showcase_state.calendar_event.start==updated.start)
let original_calls=calls.len() showcase_state=showcase_empty() showcase_load()
check("restart_restores_same_transaction_without_replay",showcase_restored && showcase_state.revision==2 && showcase_state.calendar_event.id=="real-owner-id" && calls.len()==original_calls)
let bad=receipt("calendar.get_event",{found:true event:updated}) bad.host_calendar_receipt.owner="other"
showcase_calendar_result({is_ok:true data:{status:"completed" messages:[bad]}})
check("foreign_receipt_not_success",showcase_state.calendar_status=="unresolved")
showcase_new() fail_write=true showcase_start()
check("storage_failure_stops_model_dispatch",calls.len()==original_calls && showcase_state.phase=="ready")
mod.std.print("MUSE_VM_RESULT "+checks.to_json())
'''
(a.out/'executed.splash').write_text(code);r=subprocess.run([str(a.vm),str((a.out/'executed.splash').resolve()),'--rpc'],capture_output=True,text=True,timeout=30);(a.out/'stdout.log').write_text(r.stdout);(a.out/'stderr.log').write_text(r.stderr)
report={'boundary':'SPLASH_VM_FIXTURE_NOT_GUI','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'exit':r.returncode,'status':'ERROR'}
if not r.returncode and not r.stderr:
 checks=json.loads(r.stdout.removeprefix('MUSE_VM_RESULT ').strip());report.update(checks=checks,count=len(checks),failed=[x['name'] for x in checks if not x['passed']]);report['status']='FIXTURE_PASS' if not report['failed'] else 'FAIL'
(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'}));raise SystemExit(report['status']!='FIXTURE_PASS')
