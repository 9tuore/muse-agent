#!/usr/bin/env python3
"""Source-bound directed Node fixture; not Splash VM or real Mail Host."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
from test_recovery import function, apply
from test_calendar_chain import project as calendar_project

OWN=Path(__file__).resolve().parent
NAMES=['calendar_agent_event_matches','calendar_agent_binding_valid','calendar_agent_binding_current',
 'calendar_agent_project','mail_calendar_link_valid','mail_calendar_verified','mail_calendar_current',
 'mail_calendar_context_current','mail_calendar_hold','mail_calendar_late','mail_compose_from_agent_calendar',
 'mail_draft_valid','mail_save','mail_edit','mail_new_draft','mail_watch_archive_current',
 'mail_preview','mail_send_confirmed','mail_send_step','mail_review_current','mail_compose_before_review',
 'mail_review_host','mail_check_host_status','mail_send_receipt_step','mail_host_receipt_status',
 'mail_verify_received','mail_verify_received_step','mail_finish_linked_result','mail_abort_before_host',
 'mail_payload_pending','ac_projection']

def project(text):
    text=text.replace("chat_reply_context_valid({memory_refs: link.memory_refs})", "chat_reply_context_valid(projection_memory_refs(link))")
    text=calendar_project(text)
    # Only observed statement boundaries, not a general compiler.
    text=re.sub(r'(\w+\([^\n{}]*?\)) (\w+(?:\.\w+)*\s*=|\w+\(|return\b)',r'\1; \2',text)
    text=re.sub(r'(\w+(?:\.\w+)*\s*=\s*[\w.]+) (\w+(?:\.\w+)*\s*=)',r'\1; \2',text)
    text=text.replace('let goal_id = context.goal_id let requested_id','let goal_id = context.goal_id; let requested_id')
    text=text.replace('let requested = mail_draft.request_id let compose','let requested = mail_draft.request_id; let compose')
    text=text.replace('mail_error = mail_reply_error mail_redraw()', 'mail_error = mail_reply_error; mail_redraw()')
    text=text.replace('mail_error = message\n', 'mail_error = message;\n')
    text=re.sub(r'\b(false|true) (\w+\()',r'\1; \2',text)
    text=text.replace('(||', '(()=>')
    text=text.replace('for offset in matching.length {','for (const offset of range(matching.length)) {')
    text=text.replace('calendar_agent_notice = mail_error mail_redraw()', 'calendar_agent_notice = mail_error; mail_redraw()')
    return text

JS=r'''
const fs=require('fs'),root=process.argv[2],clone=v=>JSON.parse(JSON.stringify(v));
fs.exists=name=>fs.existsSync(root+'/'+name);
Object.defineProperty(String.prototype,'parse_json',{value:function(){try{return JSON.parse(this)}catch{return null}}});
const gm_object=v=>v!=null&&typeof v==='object'&&!Array.isArray(v),gm_array=Array.isArray,gm_text=v=>typeof v==='string';
const gm_string=(v,n)=>gm_text(v)&&Buffer.byteLength(v)<=n,gm_number=v=>typeof v==='number'&&Number.isFinite(v),gm_has=(v,k)=>gm_object(v)&&Object.hasOwn(v,k);
const floor=Math.floor,min=Math.min,range=n=>Array.from({length:n},(_,i)=>i),regex=(p,f)=>new RegExp(p,f),time_now=()=>1791686400;
let nextID=0;const random_u32=()=>++nextID;
let gm_user_id,gm_accounts,gm_project,gm_owner,core_storage_ready,gm_ready,chat_selected_id,ac_selected_chat,ac_selected_id,goal,chat_sessions;
let calendar_agent_notice='',calendar_agent_state,mail_account,mail_accounts,mail_draft,mail_draft_writable,mail_draft_last_state,mail_sending,mail_pending,mail_model_pending,mail_verifying;
let mail_error='',mail_notice='',mail_reply_error='',core_error='',actions,requests,timers,events,writeFail,goalMutations=0,opened=0;
let calendar_links=[],calendar_receipts=[],activity=[],core_activity_ready=true,calendar_conflicts=[],calendar_selected_goal='';
const gm_account_allowed=id=>gm_accounts.includes(id),mail_watch_account=id=>mail_accounts.find(a=>a.id===id)||null;
const ac_goal_allowed=g=>g.project_id===gm_project&&g.owner_id===gm_owner,ac_current_goal=()=>goal&&goal.id===ac_selected_id?goal:null;
const chat_session_index=id=>chat_sessions.findIndex(s=>s.id===id),chat_card_scope_current=(s,c)=>s.focus_project===c.project&&s.focus_owner===c.owner;
const chat_reply_context_valid=c=>!c||c.refs_valid!==false,chat_refs_valid=()=>true;
const ac_field=(v,k)=>gm_text(v[k])?v[k]:'',ac_text=v=>v,ac_add=(v,title,status,detail,id)=>v.nodes.push({title,status,detail,id});
const ac_current_alert=()=>null,ac_alert_count=()=>0,calendar_enabled=()=>false,is_calendar_goal=()=>true,calendar_link_index=()=>-1;
const projection_memory_refs=link=>({memory_refs:link.memory_refs});
const redraw=()=>{},mail_redraw=()=>{},set_page=()=>{},mail_compose=()=>opened++,mail_attach_reply_headers=()=>{};
const storage_write=(name,value)=>{if(writeFail)return 'fixture write failure';fs.writeFileSync(root+'/'+name,value);return null};
const storage_read=name=>fs.existsSync(root+'/'+name)?fs.readFileSync(root+'/'+name,'utf8'):'';
const core_action_index=id=>actions.findIndex(a=>a.id===id);
const persistActions=()=>{fs.writeFileSync(root+'/fixture-actions.json',JSON.stringify(actions))};
const core_begin_action=(g,r,rev,service,scope,id,payload)=>{if(g!==''||r!==''||rev!==0)throw Error('Linked Mail must use independent journal');actions.push({id,goal_id:g,run_id:r,plan_revision:rev,service,scope,payload_json:payload,status:'in_flight'});persistActions();return true};
const core_finish_action=(id,status)=>{const i=core_action_index(id);if(i<0)return false;actions[i].status=status;persistActions();return true};
const core_record_event=(kind,detail,g,r,id,scope)=>{events.push({kind,detail,goal_id:g,run_id:r,id,scope});return true};
const core_goal_index=()=>{goalMutations++;throw Error('Unexpected Goal mutation')},core_run_index=()=>-1;
const core_upsert_goal=()=>{goalMutations++;throw Error('Unexpected Goal mutation')},core_replan_goal=core_upsert_goal,core_start_run=core_upsert_goal,core_finish_run=core_upsert_goal;
const is_mail_phase=()=>false,mail_goal_spec=()=>{throw Error('unexpected Mail Goal phase')};
const mail_finish_linked_step=()=>{throw Error('unexpected Goal finish')};
const start_timeout=(seconds,callback)=>timers.push(callback),official_discover=callback=>callback(),official_method_available=()=>true;
const host={request:(method,args,callback)=>requests.push({method,args:clone(args),callback})};
function field(){return {value:'',text(){return this.value},set_text(v){this.value=v}}}
const ui={mail_to:field(),mail_subject:field(),mail_body:field(),mail_test_id:field()};
__FUNCTIONS__
function reset(){
 for(const n of fs.readdirSync(root))fs.unlinkSync(root+'/'+n);
 gm_user_id='user-A';gm_accounts=['local','account-A','account-B'];gm_project='project-A';gm_owner='owner-A';core_storage_ready=true;gm_ready=true;
 chat_selected_id='chat-A';ac_selected_chat='chat-A';ac_selected_id='goal-A';
 goal={id:'goal-A',goal:'Fixture calendar matter',version:3,status:'planned',archived:false,project_id:gm_project,owner_id:gm_owner};
 const card={id:'candidate-A',session_id:'chat-A',account_id:'account-A',project:gm_project,owner:gm_owner,action:'calendar_candidate',state:'opened',revision:2,
  payload:{title:'Fixture appointment',start:'2026-10-12T15:00:00+08:00',end:'2026-10-12T16:00:00+08:00',time_zone:'Asia/Shanghai',location:'Fixture room'}};
 chat_sessions=[{id:'chat-A',focus_project:gm_project,focus_owner:gm_owner,proposals:[card]}];
 const payload={request_id:'cal-request-A',title:card.payload.title,start:'2026-10-12T15:00',end:'2026-10-12T16:00',timezone:'Asia/Shanghai',location:card.payload.location,notes:''};
 const binding={goal_id:goal.id,plan_revision:goal.version,project_id:gm_project,owner_id:gm_owner,user_id:gm_user_id,accounts:JSON.stringify(gm_accounts),account_id:'account-A',session_id:chat_selected_id,candidate_id:card.id,candidate_revision:card.revision,candidate_json:JSON.stringify(card.payload),payload,receipt_status:'verified',
 verification:{status:'verified',event_id:'event-A',add_call_id:'host-add-A',get_call_id:'host-get-A',event:{id:'event-A',...clone(payload)}}};
 calendar_agent_state={request_id:payload.request_id,turn_id:'turn-A',status:'turn_completed',binding};
 mail_accounts=[{id:'account-A'},{id:'account-B'}];mail_account=mail_accounts[0];
 mail_draft={account:'account-A',to:'',subject:'',body:'',status:'DRAFT',preview:'',attempt:'',request_id:'',accepted_at:0,verified_at:0,verified_id:'',link_goal_id:'',link_event_id:'',link_run_id:'',incoming_key:''};
 mail_draft_writable=true;mail_draft_last_state='';mail_sending=false;mail_pending=false;mail_model_pending=false;mail_verifying=false;
 mail_error='';mail_notice='';mail_reply_error='';actions=[];requests=[];timers=[];events=[];writeFail=false;goalMutations=0;opened=0;
 for(const f of Object.values(ui))f.set_text('');
}
function drain(limit=30){while(timers.length){if(--limit<0)throw Error('fixture timer loop');timers.shift()()}}
function answer(data,i=requests.length-1){requests[i].callback(data);drain()}
function draft(){reset();mail_compose_from_agent_calendar();ui.mail_to.set_text('fixture@example.invalid');mail_edit();return mail_draft}
function dispatch(){draft();mail_preview();mail_send_confirmed();drain()}
function composeReply(){return {is_ok:true,data:{compose_id:'compose-fixture-A',revision:1,...clone(requests[0].args)}}}
function review(){dispatch();answer(composeReply())}
function accepted(){review();answer({is_ok:true,data:{accepted:true,status:'accepted',compose_id:'compose-fixture-A',revision:1,operation_id:'op-A'}})}
function unknown(){review();answer({is_ok:false,error:'fixture timeout'})}
function statusReply(status='accepted'){
 const s=JSON.parse(mail_draft.attempt),data={compose_id:mail_draft.host_compose_id,revision:mail_draft.host_revision,...s,status,
  attempts:[{operation_id:'op-A',revision:mail_draft.host_revision,status,payload:{to:s.to,subject:s.subject,body:s.body}}]};
 if(status==='accepted')data.attempts[0].receipt={accepted:true};return {is_ok:true,data};
}
const checks={},check=(name,ok)=>checks[name]=!!ok;
reset();mail_compose_from_agent_calendar();let saved=JSON.parse(storage_read('mail-draft.json'));
check('verified_calendar_creates_draft_without_host',saved.status==='DRAFT'&&requests.length===0&&saved.to===''&&goal.status==='planned');
check('full_scope_and_event_proof_persisted',saved.official_calendar.binding.goal_id==='goal-A'&&saved.official_calendar.binding.plan_revision===3&&saved.official_calendar.binding.session_id==='chat-A'&&saved.official_calendar.binding.candidate_revision===2&&saved.link_event_id==='event-A'&&saved.link_run_id==='');
check('generated_draft_is_valid',mail_draft_valid(saved));
ui.mail_body.set_text('hand edited confirmation');mail_edit();const before=JSON.stringify(mail_draft);mail_compose_from_agent_calendar();
check('reopen_preserves_hand_text_and_status',JSON.stringify(mail_draft)===before&&requests.length===0);
let v=ac_projection();check('chain_has_current_draft_without_old_calendar_dependency',v.nodes.some(n=>n.title==='回复草稿'&&n.status==='DRAFT')&&!v.nodes.some(n=>n.title==='关联日程已变化'));
draft();mail_preview();check('preview_only_waiting_user_no_host',mail_draft.status==='waiting_user'&&requests.length===0);
mail_send_confirmed();drain();check('explicit_confirmation_uses_existing_compose',requests.length===1&&requests[0].method==='mail.compose'&&actions.length===1&&actions[0].goal_id===''&&goalMutations===0);
answer(composeReply());check('exact_compose_enters_native_review',requests.length===2&&requests[1].method==='mail.review_send'&&requests[1].args.expected_revision===1&&mail_draft.host_compose_id==='compose-fixture-A');
answer({is_ok:true,data:{accepted:true,status:'accepted',compose_id:'compose-fixture-A',revision:1,operation_id:'op-A'}});
check('accepted_is_not_received_or_goal_complete',mail_draft.status==='accepted'&&mail_draft.verified_at===0&&goal.status==='planned'&&goal.version===3&&goalMutations===0);
mail_verify_received();drain();check('user_receipt_declaration_keeps_goal_planned',mail_draft.status==='verified'&&events.some(e=>e.kind==='MAIL_DELIVERY_USER_CONFIRMED')&&goal.status==='planned'&&goal.version===3&&goalMutations===0);
const mutations={
 user:()=>gm_user_id='user-B',accounts:()=>gm_accounts=['local','account-A'],project:()=>gm_project='project-B',owner:()=>gm_owner='owner-B',
 chat:()=>chat_selected_id='chat-B',selection:()=>ac_selected_id='goal-B',plan_revision:()=>goal.version++,archived:()=>goal.archived=true,
 candidate_revision:()=>chat_sessions[0].proposals[0].revision++,candidate_payload:()=>chat_sessions[0].proposals[0].payload.title='new',
 event:()=>calendar_agent_state.binding.verification.event.id='event-B',request:()=>calendar_agent_state.request_id='cal-other',
 turn:()=>calendar_agent_state.turn_id='turn-B',readback_unknown:()=>calendar_agent_state.binding.receipt_status='unknown',
 sender:()=>mail_account=mail_accounts[1],grant_removed:()=>mail_accounts=[],draft_binding:()=>mail_draft.official_calendar.binding.plan_revision=99
};
for(const [name,mutate] of Object.entries(mutations)){
 draft();mutate();const body=mail_draft.body;mail_preview();check(name+'_blocks_preview_preserves_body',mail_draft.status==='DRAFT'&&requests.length===0&&mail_draft.body===body);
 draft();mail_preview();mutate();mail_send_confirmed();drain();check(name+'_blocks_send',requests.length===0&&actions.length===0&&goalMutations===0);
 v=ac_projection();check(name+'_old_draft_not_current',!v.nodes.some(n=>n.title==='回复草稿'));
}
dispatch();goal.version++;answer(composeReply());
check('late_compose_keeps_unknown_exact_host_id_no_review',mail_draft.status==='unknown'&&mail_draft.host_compose_id==='compose-fixture-A'&&requests.length===1&&actions[0].status==='unknown'&&gm_text(mail_draft.calendar_late_host_receipt));
review();gm_project='project-B';answer({is_ok:true,data:{accepted:true,status:'accepted',compose_id:'compose-fixture-A',revision:1,operation_id:'op-A'}});
check('late_native_acceptance_is_historical_not_current',mail_draft.status==='unknown'&&actions[0].status==='unknown'&&goal.status==='planned'&&JSON.parse(mail_draft.calendar_late_host_receipt).data.accepted===true);
accepted();goal.version++;mail_verify_received();drain();check('changed_version_blocks_user_received',mail_draft.status==='accepted'&&!events.some(e=>e.kind==='MAIL_DELIVERY_USER_CONFIRMED')&&goalMutations===0);
accepted();mail_verify_received();goal.version++;drain();check('queued_user_received_rechecks_binding',mail_draft.status==='accepted'&&actions[0].status==='accepted'&&goalMutations===0);
unknown();const count=requests.length;mail_check_host_status();check('unknown_only_readonly_original_composer',requests.length===count+1&&requests.at(-1).method==='mail.compose_status'&&requests.at(-1).args.compose_id==='compose-fixture-A');
answer(statusReply());check('readonly_acceptance_not_delivery_or_goal_complete',mail_draft.status==='accepted'&&actions[0].status==='accepted'&&goal.status==='planned'&&goalMutations===0);
unknown();mail_check_host_status();const bad=statusReply();bad.data.body+=' mismatch';answer(bad);check('status_payload_mismatch_remains_unknown',mail_draft.status==='unknown'&&actions[0].status==='unknown');
unknown();mail_check_host_status();goal.version++;answer(statusReply());check('late_status_after_version_change_preserved_unknown',mail_draft.status==='unknown'&&actions[0].status==='unknown');
unknown();mail_check_host_status();answer(statusReply('failed_before_delivery'));check('definite_unsent_reconciles_draft_without_goal_replan',mail_draft.status==='DRAFT'&&actions[0].status==='failed'&&goalMutations===0);
unknown();const payload=mail_draft.attempt;mail_sending=false;mail_draft.status='DRAFT';mail_draft.attempt='';ui.mail_to.set_text(mail_draft.to);mail_preview();check('journal_blocks_unknown_payload_replay',mail_draft.status==='DRAFT'&&mail_payload_pending(payload)&&requests.length===2);
reset();calendar_agent_state.binding.receipt_status='accepted';mail_compose_from_agent_calendar();check('calendar_add_only_cannot_generate_confirmation',mail_draft.subject===''&&requests.length===0);
reset();mail_account=mail_accounts[1];mail_compose_from_agent_calendar();check('source_account_mismatch_no_draft',mail_draft.subject===''&&requests.length===0);
reset();calendar_agent_state.binding.account_id='local';chat_sessions[0].proposals[0].account_id='';mail_account=mail_accounts[1];mail_compose_from_agent_calendar();check('local_candidate_uses_explicit_authorized_sender',mail_draft.official_calendar.mail_account==='account-B');
reset();mail_draft.body='old private hand draft';mail_compose_from_agent_calendar();check('old_hand_draft_archived_exactly',JSON.parse(storage_read('mail-draft-archive.json')).drafts[0].draft.body==='old private hand draft');
reset();mail_draft.body='pending original';mail_draft.status='unknown';const old=JSON.stringify(mail_draft);mail_compose_from_agent_calendar();check('unrelated_unknown_preserved',JSON.stringify(mail_draft)===old&&requests.length===0);
reset();writeFail=true;mail_compose_from_agent_calendar();check('write_failure_no_host_or_goal_mutation',requests.length===0&&goalMutations===0&&!mail_draft_writable);
draft();const invalid=clone(mail_draft);invalid.official_calendar.binding.verification.event_id='wrong';check('malformed_calendar_proof_rejected_on_save',!mail_draft_valid(invalid));
unknown();const original=JSON.parse(storage_read('mail-draft.json'));mail_draft=clone(original);const oldRequests=requests.length;mail_check_host_status();check('json_restore_reconciles_without_replay',requests.length===oldRequests+1&&requests.at(-1).method==='mail.compose_status');
check('actual_temp_action_json_matches_journal',JSON.stringify(JSON.parse(storage_read('fixture-actions.json')))===JSON.stringify(actions));

for(const key of ['request_id','title','start','end','timezone','location','notes']){
 draft();calendar_agent_state.binding.verification.event[key]='different';mail_preview();
 check('changed_verified_'+key+'_blocks_preview',mail_draft.status==='DRAFT'&&requests.length===0);
}
for(const state of ['idle','in_flight','unknown','blocked']){
 reset();calendar_agent_state.status=state;mail_compose_from_agent_calendar();
 check('calendar_'+state+'_cannot_create_confirmation',mail_draft.subject===''&&requests.length===0);
}
for(const state of ['waiting_user','sending','accepted','unknown']){
 reset();mail_draft.body='preserved '+state;mail_draft.status=state;const old=JSON.stringify(mail_draft);mail_compose_from_agent_calendar();
 check('other_'+state+'_not_overwritten',JSON.stringify(mail_draft)===old&&requests.length===0);
}
unknown();goal.version++;const staleCount=requests.length;mail_check_host_status();check('stale_unknown_does_not_query_or_resend',requests.length===staleCount&&mail_draft.status==='unknown');
review();const exactBody=mail_draft.body,exactID=mail_draft.host_compose_id;goal.version++;answer({is_ok:false,error:'Review cancelled; nothing was sent'});
check('stale_cancel_does_not_clear_original_attempt',mail_draft.status==='unknown'&&mail_draft.attempt!==''&&mail_draft.body===exactBody&&mail_draft.host_compose_id===exactID);
review();answer({is_ok:false,error:'Review cancelled; nothing was sent'});check('current_native_cancel_retains_editable_body',mail_draft.status==='DRAFT'&&mail_draft.body!==''&&actions[0].status==='failed');
unknown();mail_check_host_status();const missing=statusReply('failed_before_delivery');missing.data.attempts=[];answer(missing);check('missing_status_attempt_does_not_release_unknown',mail_draft.status==='unknown'&&actions[0].status==='unknown');
reset();ui.mail_to.set_text('fixture@example.invalid');ui.mail_subject.set_text('ordinary');ui.mail_body.set_text('ordinary hand text');mail_edit();mail_preview();mail_send_confirmed();drain();
check('ordinary_mail_pipeline_still_uses_existing_compose',requests.length===1&&requests[0].method==='mail.compose'&&!gm_has(mail_draft,'official_calendar'));

console.log(JSON.stringify({checks,failed:Object.keys(checks).filter(k=>!checks[k]),external_calls:0,boundary:'Actual source functions projected into Node with synthetic UI/Host/scope/journal adapters and temporary JSON readback. NOT Splash VM, native Host, SMTP or Calendar creation proof.'}));
'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    original=a.source.read_text();identity=json.loads((OWN/'calendar-mail-identity.json').read_text());sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
    assert sha(original)==identity['source_sha256']
    source=apply(original,(OWN/'calendar-mail.patch').read_text());assert sha(source)==identity['expected_source_sha256']
    baseline={'verified_calendar_not_in_legacy_links':'calendar_link_index(goal_id)' in function(original,'mail_compose_from_calendar'),
              'no_official_calendar_mail_bridge':'fn mail_compose_from_agent_calendar(' not in original}
    assert all(baseline.values())
    program=JS.replace('__FUNCTIONS__','\n'.join(project(function(source,n)) for n in NAMES))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gpt02-calendar-mail-') as d:
        run=subprocess.run([shutil.which('node') or 'node','-',d],input=program,text=True,capture_output=True)
        if run.returncode:
            a.out.with_suffix('.adapter-error.txt').write_text(run.stderr)
            Path('build/gpt02-calendar-mail-source-r1/projected.js').write_text(program)
            raise RuntimeError(run.stderr)
        result=json.loads(run.stdout)
    result.update(total=len(result['checks']),passed=sum(result['checks'].values()),baseline=baseline,source_sha256=identity['source_sha256'],expected_source_sha256=identity['expected_source_sha256'],projected_functions=NAMES)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','total','failed','external_calls']}))
    raise SystemExit(bool(result['failed']))

if __name__=='__main__':main()
