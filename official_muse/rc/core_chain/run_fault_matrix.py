#!/usr/bin/env python3
"""Twenty isolated fault reactions in production Splash functions.
Synthetic Host transport, real card-host storage, no real accounts or inference.
Each case uses a fresh process/data directory. Restart cases use a second process.
"""
import argparse, hashlib, json, os, re, shutil, socket, subprocess, sys, time
from pathlib import Path
from urllib.request import urlopen
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'))
import regression_run
existing=regression_run.existing
CASES=['model_unavailable','model_timeout','invalid_json','schema_violation','mail_unavailable','mail_timeout','calendar_unavailable','calendar_permission_lost','storage_write_fail','storage_read_fail','corrupt_json','late_callback','duplicate_callback','restart_pending_model','restart_pending_calendar','restart_after_service_accepted','stale_approval','stale_memory','external_calendar_changed','duplicate_mail_id']
COMMON='''
let fault_active = false
let fault_pending = []
fn fault_finish(checks){
    checks.boundary = "Synthetic Host faults; production functions and real isolated fs; no live model/account/system actions."
    checks.calls = chain_calls
    fs.write("probe.json",checks.to_json())
}
fn chain_fixture_request(service,args,cb){
    if fault_active {
        if fault_case == "calendar_unavailable" && service == "calendar.status" {
            chain_calls.push({service: service args: args}) cb({is_ok: false error: "synthetic calendar unavailable"}) return
        }
        if fault_case == "calendar_permission_lost" && service == "calendar.status" {
            chain_calls.push({service: service args: args}) cb({is_ok: true data: {permission: "denied" calendars: []}}) return
        }
        if fault_case == "restart_pending_calendar" && service == "calendar.create" {
            chain_calls.push({service: service args: args}) chain_write_count += 1 fault_pending.push(cb) return
        }
        if fault_case == "restart_after_service_accepted" && service == "calendar.get" {
            chain_calls.push({service: service args: args}) fault_pending.push(cb) return
        }
        if fault_case == "mail_unavailable" && service == "mail.accounts" {
            chain_calls.push({service: service args: args}) cb({is_ok: false error: "synthetic mail unavailable"}) return
        }
        if fault_case == "mail_timeout" && service == "mail.sync" {
            chain_calls.push({service: service args: args}) fault_pending.push(cb) return
        }
    }
    chain_base_request(service,args,cb)
}
fn fault_wait_disk(){
    if !fs.exists("fault-go.json") { start_timeout(0.03,|| fault_wait_disk()) return }
    start_timeout(0.5,|| fault_disk_inspect())
    if fault_case == "storage_write_fail" {
        let before = fs.read("goals.json")
        calendar_confirm_action()
        fault_finish({safe_failure: chain_write_count == 0 && core_error != ""
            old_primary_preserved: fs.read("goals.json") == before no_false_success: actions.len() == 0 not_stuck_pending: !calendar_pending})
    }
    if fault_case == "storage_read_fail" {
        let loaded = calendar_boot()
        fault_finish({safe_failure: !loaded && !calendar_ready && calendar_error != ""
            no_action: chain_write_count == 0 no_false_success: calendar_links[0].status != "verified"})
    }
    if fault_case == "corrupt_json" {
        let loaded = core_boot_goals()
        let raw = fs.read("goals.json")
        let attempted = core_commit_goals(goals,runs,actions,selected_id)
        fault_finish({safe_failure: !loaded && !core_storage_ready && !attempted
            corrupt_evidence_preserved: fs.read("goals.json") == raw no_action: chain_write_count == 0})
    }
}
fn fault_disk_inspect(){
    if fs.exists("probe.json") { return }
    fault_finish({safe_failure: false fault_callback_did_not_complete: true no_action: chain_write_count == 0
        no_false_success: actions.len() == 0 pending_after_fault: calendar_pending})
}
fn fault_calendar_stage(){
    fault_active = true
    if fault_case == "storage_write_fail" || fault_case == "storage_read_fail" || fault_case == "corrupt_json" {
        fs.write("fault-ready.json",{case: fault_case}.to_json())
        start_timeout(0.03,|| fault_wait_disk()) return
    }
    if fault_case == "stale_approval" { goals[core_goal_index(chain_goal)].version += 1 }
    if fault_case == "stale_memory" {
        let mi = core_memory_index(calendar_links[0].source_claim_id,"synthetic-account")
        calendar_context_refs = [{id: memory[mi].document.id revision: memory[mi].document.revision
            account: "synthetic-account" source_ids: memory[mi].document.payload.source_ids}].to_json().parse_json()
        let changed = memory.to_json().parse_json()
        changed[mi].document.revision += 1
        if !core_commit_memory(changed,memory_sources,memory_forget) { fault_finish({setup_ok: false error: core_error}) return }
    }
    if fault_case == "external_calendar_changed" { chain_conflict = true }
    calendar_confirm_action()
    if fault_case == "restart_pending_calendar" || fault_case == "restart_after_service_accepted" {
        fault_finish({pending_persisted: (calendar_links[0].status == "in_flight" || (fault_case == "restart_after_service_accepted" && calendar_links[0].status == "accepted")) && (fault_case == "restart_after_service_accepted" || calendar_pending)
            single_submission: chain_write_count == 1 && chain_count("calendar.create") == 1
            unverified_before_restart: actions.len() == 1 && actions[0].status != "verified"
            accepted_before_restart: fault_case != "restart_after_service_accepted" || actions[0].status == "accepted"})
        return
    }
    fault_finish({safe_failure: calendar_error != "" && calendar_preview == "" && !calendar_pending
        no_action: chain_write_count == 0 && chain_count("calendar.create") == 0
        no_false_success: goals[0].status != "completed" && actions.len() == 0})
}
fn fault_chat_start(){
    fixture_seed() chat_boot() gm_boot()
    ui.goal_input.set_text("合成故障测试普通问题。") send_chat()
    let cb = chain_models[0]
    if fault_case == "restart_pending_model" {
        fault_finish({pending_persisted: messages.len() == 1 && chat_requests.len() == 1
            no_false_reply: messages[0].role == "user" no_action: chain_write_count == 0}) return
    }
    if fault_case == "late_callback" {
        chat_stop()
        let disk = fs.read("chat-sessions.json") let count = activity.len()
        cb({is_ok: true data: {output: {reply: "迟到回复不得写入"}}})
        fault_finish({late_ignored: fs.read("chat-sessions.json") == disk && activity.len() == count
            no_false_reply: messages.len() == 2 && messages[1].state == "cancelled" no_action: chain_write_count == 0}) return
    }
    cb({is_ok: true data: {output: {reply: "第一次合成回复"}}})
    let disk = fs.read("chat-sessions.json") let count = activity.len()
    cb({is_ok: true data: {output: {reply: "重复回调不得追加"}}})
    fault_finish({duplicate_ignored: fs.read("chat-sessions.json") == disk && activity.len() == count
        one_reply: messages.len() == 2 && messages[1].text == "第一次合成回复" no_action: chain_write_count == 0})
}
fn fault_model_stage(){
    if fault_case == "duplicate_mail_id" {
        let count = goals.len() let claims = memory.len() let links = calendar_links.len()
        mail_link_calendar()
        fault_finish({one_goal: goals.len() == count && count == 1 one_claim: memory.len() == claims
            one_link: calendar_links.len() == links && links == 1 no_action: chain_write_count == 0}) return
    }
    let why = "no_provider: synthetic unavailable"
    if fault_case == "model_timeout" { start_timeout(0.25,|| fault_model_timeout()) return }
    if fault_case == "invalid_json" { why = "invalid_output: invalid JSON" }
    if fault_case == "schema_violation" { why = "invalid_output: schema missing field / wrong type" }
    chain_models[0]({is_ok: false error: why})
    fault_model_assert()
}
fn fault_model_timeout(){
    chain_models[0]({is_ok: false error: "provider: synthetic timeout"}) fault_model_assert()
}
fn fault_model_assert(){
    fault_finish({safe_failure: calendar_error != "" && calendar_links[0].active_generation == nil
        no_action: chain_write_count == 0 no_false_success: calendar_links[0].status != "verified"
        recoverable_candidate: goals[0].status == "planned"})
}
fn fault_mail_start(){
    fixture_seed() chat_boot() gm_boot()
    mail_watch.accounts = [{id: "synthetic-account" ready: true seen: ["prior"]}]
    mail_watch.alerts = [{key: "synthetic-account:prior" account_id: "synthetic-account" message_id: "prior" status: "new" intent: ""}]
    mail_watch_save()
    let before = mail_watch.alerts.to_json()
    fs.write("fault-alerts-before.json",before)
    fault_active = true mail_watch_poll()
    if fault_case == "mail_timeout" {
        start_timeout(0.25,|| { fault_pending[0]({is_ok: false error: "synthetic timeout"}) fault_mail_assert() }) return
    }
    fault_mail_assert()
}
fn fault_mail_assert(){
    fault_finish({safe_failure: !mail_watch_busy && (mail_watch_notice.search("失败") >= 0)
        alerts_preserved: mail_watch.alerts.len() == 1 && mail_watch.alerts[0].key == "synthetic-account:prior" && mail_watch.alerts[0].message_id == "prior" && mail_watch.alerts[0].status == "new"
        no_send: chain_count("mail.send") == 0 no_model: chain_models.len() == 0})
}
fn fault_restart(){
    core_boot_goals() core_boot_activity() core_boot_memory() gm_boot() chat_boot() calendar_boot()
    if fault_case == "restart_pending_model" {
        fault_finish({history_preserved: messages.len() >= 1 && messages[0].role == "user"
            request_not_reissued: chain_models.len() == 0 && chat_requests.len() == 0
            no_fake_success: messages.len() == 1 || (messages.len() == 2 && messages[1].state != "success") no_action: chain_write_count == 0}) return
    }
    fault_finish({uncertain_or_accepted_link: calendar_links.len() == 1 && (calendar_links[0].status == "unknown" || calendar_links[0].status == "accepted")
        journal_safe: actions.len() == 1 && (actions[0].status == "unknown" || actions[0].status == "accepted")
        no_reissue: chain_count("calendar.create") == 0 && chain_count("calendar.update") == 0
        no_fake_verified: calendar_links[0].status != "verified"})
}
'''

def make_probe(case,restart=False):
    chain=(HERE/'t18_chain.splash').read_text().replace('fn chain_fixture_request(','fn chain_base_request(')
    chain=chain.replace('start_timeout(0.1,|| probe())','')
    if case in ['model_unavailable','model_timeout','invalid_json','schema_violation','duplicate_mail_id']:
        chain=existing.replace_function(chain,'chain_assert_source','''fn chain_assert_source(){
            chain_goal = selected_id
            if goals.len() != 1 || chain_models.len() != 1 { fault_finish({setup_ok: false}) return }
            fault_model_stage()
        }''')
    else:
        chain=existing.replace_function(chain,'chain_waiting_preview','''fn chain_waiting_preview(){
            calendar_preview_action()
            if calendar_preview == "" { fault_finish({setup_ok: false error: calendar_error}) return }
            fault_calendar_stage()
        }''')
    entry='probe()'
    if case in ['late_callback','duplicate_callback','restart_pending_model']:entry='fault_chat_start()'
    if case in ['mail_unavailable','mail_timeout']:entry='fault_mail_start()'
    if restart:entry='fault_restart()'
    return 'let fault_case = '+json.dumps(case)+'\n'+chain+COMMON+'\nstart_timeout(0.1,|| '+entry+')\n'

def prepare_prefix(source):
    match=re.search(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)',source,re.M)
    if not match:raise RuntimeError('Production startup marker missing')
    prefix=source[:match.start()].replace('host.request(','chain_fixture_request(')
    for name,replacement in [('redraw','fn redraw(){}'),('set_page','fn set_page(next){ page = next }'),('calendar_enabled','fn calendar_enabled(){ return true }'),('mail_enabled','fn mail_enabled(){ return true }'),('mail_watch_refresh','fn mail_watch_refresh(){}'),('mail_redraw','fn mail_redraw(){ mail_watch_draft_status() }')]:
        prefix=existing.replace_function(prefix,name,replacement)
    return prefix

def launch(case,prefix,template,out,state,restart=False):
    if socket.socket().connect_ex(('127.0.0.1',8509))==0:raise RuntimeError('Port 8509 busy; existing process untouched')
    out.mkdir(parents=True,exist_ok=False)
    bundle=out/'bundle';shutil.copytree(template,bundle)
    manifest=json.loads((bundle/'manifest.json').read_text());manifest['integrity'].pop('signature',None)
    (bundle/'manifest.json').write_text(json.dumps(manifest)+'\n')
    probe=make_probe(case,restart);(out/'probe.splash').write_text(probe)
    widget=existing.WIDGET.replace('    Label{text:','    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n    mail_body := TextInput{width: Fill}\n    mail_intent := TextInput{width: Fill}\n    Label{text:',1)
    code=prefix+existing.TRANSPORT+probe+widget
    (bundle/'main.splash').write_text(code)
    env=dict(os.environ,MAKEPAD_REMOTE='8509',MAKEPAD_HIDE_WINDOWS='1');env.pop('MAKEPAD_FOCUS',None)
    jail=state/'muse-goals';ready=jail/'fault-ready.json';reportpath=jail/'probe.json'
    if reportpath.exists():reportpath.rename(jail/'probe-before-restart.json')
    changed=[];disk_evidence={}
    with (out/'runtime.log').open('w') as log:
        proc=subprocess.Popen([str(existing.HOST),'--bundle',str(bundle),'--app-data',str(state),'--allow-unsigned','--stamp','--size','600x700'],env=env,cwd=existing.HOST.parents[2],stdout=log,stderr=log)
        try:
            deadline=time.monotonic()+25;injected=False
            while not reportpath.exists():
                if ready.exists() and not injected:
                    injected=True
                    paths={'storage_write_fail':['goals.backup.json'],'storage_read_fail':['calendar-state.json','calendar-state.backup.json'],'corrupt_json':['goals.json','goals.backup.json']}[case]
                    for rel in paths:
                        target=jail/rel;present=target.exists();raw=target.read_bytes() if present else (jail/'goals.json').read_bytes();disk_evidence[rel]={'originally_existed':present,'before_sha256':hashlib.sha256(raw).hexdigest() if present else None,'reference_sha256':hashlib.sha256(raw).hexdigest()}
                        (out/(rel+'.preserved')).write_bytes(raw)
                        if case=='storage_write_fail':
                            if present:target.rename(jail/(rel+'.preserved'))
                            target.mkdir();changed.append((target,None))
                        elif case=='storage_read_fail':changed.append((target,target.stat().st_mode));target.chmod(0)
                        else:target.write_text('{ corrupt synthetic JSON')
                    (jail/'fault-go.json').write_text('{}')
                if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('No report: inspect preserved runtime.log')
                time.sleep(.05)
            report=json.loads(reportpath.read_text());text=(out/'runtime.log').read_text()
            runtime_error='[E]' in text or 'script time budget exceeded' in text
            checks={k:v for k,v in report.items() if isinstance(v,bool)}
            if not checks:raise RuntimeError('No checks')
            result={'status':'PASS' if all(checks.values()) and not runtime_error else 'FAIL','runtime_error':runtime_error,'checks':checks,'calls':report.get('calls',[]),'instrumented_sha256':hashlib.sha256(code.encode()).hexdigest(),'probe_sha256':hashlib.sha256(probe.encode()).hexdigest(),'disk_fault':disk_evidence}
        except Exception as e:result={'status':'ERROR','error':str(e),'disk_fault':disk_evidence}
        finally:
            try:urlopen('http://127.0.0.1:8509/quit',timeout=2).read()
            except OSError:proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            for target,mode in changed:
                if mode is not None:target.chmod(mode)
            for rel,d in disk_evidence.items():
                target=jail/rel
                if target.is_file():d['after_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
                d['preserved_copy_sha256']=hashlib.sha256((out/(rel+'.preserved')).read_bytes()).hexdigest()
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cases',nargs='+',choices=CASES,default=CASES);p.add_argument('--storage-wrappers',action='store_true',help='Test A2 patch suggestion in copied prefix only; not production PASS');a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(HERE);out.mkdir(parents=True,exist_ok=False)
    source=a.source.read_bytes();snapshot=out/'source-bundle';shutil.copytree(ROOT/'official_muse/app/bundle',snapshot);(snapshot/'main.splash').write_bytes(source)
    prefix=prepare_prefix(source.decode());results={}
    if a.storage_wrappers:
        prefix=prefix.replace('fs.write(', 'a2_storage_write(').replace('fs.read(', 'a2_storage_read(')+(HERE/'storage_wrappers.splash').read_text()
    summary={'kind':'FAULT_INJECTION_PRODUCTION_SPLASH_SYNTHETIC_TRANSPORT','source_sha256':hashlib.sha256(source).hexdigest(),'host_sha256':hashlib.sha256(existing.HOST.read_bytes()).hexdigest(),'captured_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'storage_wrapper_patch_test':a.storage_wrappers,'cases':results,'boundary':'No live mail/calendar/model; headless logic evidence is not visual acceptance.'}
    for case in a.cases:
        state=out/case/'state';r=launch(case,prefix,snapshot,out/case/'first',state)
        if case.startswith('restart_') and r['status']=='PASS':r['restart']=launch(case,prefix,snapshot,out/case/'restart',state,True)
        results[case]=r
        (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
        print(case,r['status'],r.get('restart',{}).get('status',''),flush=True)
    summary['passed_cases']=sum(r['status']=='PASS' and r.get('restart',{'status':'PASS'})['status']=='PASS' for r in results.values())
    summary['failed_cases']=[name for name,r in results.items() if r['status']!='PASS' or r.get('restart',{'status':'PASS'})['status']!='PASS']
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return int(bool(summary['failed_cases']))
if __name__=='__main__':raise SystemExit(main())
