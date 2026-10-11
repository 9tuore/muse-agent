#!/usr/bin/env python3
"""Source-bound deletion Node fixture; no real Calendar, GUI, model or VM."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
from test_recovery import function,apply
from test_calendar_chain import project

OWN=Path(__file__).resolve().parent
NAMES=['calendar_agent_tool_name','calendar_agent_event_matches','calendar_agent_binding_valid',
 'calendar_agent_binding_current','calendar_agent_save','calendar_agent_boot','calendar_agent_project','mail_calendar_verified']

def projection(text):
    text=project(text)
    text=re.sub(r'for (\w+) in ([\w.]+)\.length \{',r'for (const \1 of range(\2.length)) {',text)
    text=text.replace(') return','); return')
    text=text.replace('false return','false; return').replace('true return','true; return')
    # Closed observed adjacent statements, no general language/compiler claim.
    text=re.sub(r'(\w+(?:\.\w+)*\([^\n;{}]*?\)) (\w+(?:\.\w+)*\s*=|\w+\(|return\b)',r'\1; \2',text)
    text=re.sub(r'(\w+(?:\.\w+)*\s*=\s*[\w.]+) (\w+(?:\.\w+)*\s*=)',r'\1; \2',text)
    text=text.replace('record.status if ', 'record.status; if ')
    text=text.replace('row["turn_id"] if ', 'row["turn_id"]; if ')
    text=text.replace('record.get_digest if ', 'record.get_digest; if ')
    text=text.replace('calendar_agent_delete_state.records[i].status = "unknown" interrupted', 'calendar_agent_delete_state.records[i].status = "unknown"; interrupted')
    text=text.replace('calendar_agent_delete_selected = "" calendar_agent_notice', 'calendar_agent_delete_selected = ""; calendar_agent_notice')
    text=text.replace('calendar_agent_busy = false calendar_agent_delete_state','calendar_agent_busy = false; calendar_agent_delete_state')
    text=text.replace('result.status = "verified" result.event_id', 'result.status = "verified"; result.event_id')
    text=text.replace('result.event_id = record.expected.id result.found', 'result.event_id = record.expected.id; result.found')
    text=text.replace('result.remove_call_id = removed result.after_get_call_id', 'result.remove_call_id = removed; result.after_get_call_id')
    text=text.replace('before = receipt.call_id before_tool', 'before = receipt.call_id; before_tool')
    text=text.replace('removed = receipt.call_id remove_tool', 'removed = receipt.call_id; remove_tool')
    text=text.replace('after = receipt.call_id after_tool', 'after = receipt.call_id; after_tool')
    text=text.replace('row.tool_call_id phase', 'row.tool_call_id; phase')
    return text

JS=r'''
const disk=require('fs'),crypto=require('crypto'),root=process.argv[2],clone=v=>JSON.parse(JSON.stringify(v));
Object.defineProperty(Object.prototype,'to_json',{value:function(){return JSON.stringify(this)}});
Object.defineProperty(String.prototype,'parse_json',{value:function(){try{return JSON.parse(this)}catch{return null}}});
const gm_object=v=>v!=null&&typeof v==='object'&&!Array.isArray(v),gm_array=Array.isArray;
const gm_string=(v,n)=>typeof v==='string'&&Buffer.byteLength(v)<=n,gm_number=v=>typeof v==='number'&&Number.isFinite(v),gm_has_key=(v,k)=>gm_object(v)&&Object.hasOwn(v,k);
const floor=Math.floor,min=Math.min,range=n=>Array.from({length:n},(_,i)=>i),time_now=()=>1791766800;
let seed=0;const random_u32=()=>++seed;
const fs={exists:p=>disk.existsSync(root+'/'+p),sha256:s=>crypto.createHash('sha256').update(s).digest('hex')};
let writeFail=false;const storage_read=p=>fs.exists(p)?disk.readFileSync(root+'/'+p,'utf8'):'';
const storage_write=(p,v)=>{if(writeFail)return 'fixture write failure';disk.writeFileSync(root+'/'+p,v);return null};
let gm_user_id,gm_accounts,gm_project,gm_owner,core_storage_ready,gm_ready,chat_selected_id,ac_selected_chat,ac_selected_id,goal,chat_sessions;
let calendar_agent_state,calendar_agent_busy,calendar_agent_writable,calendar_agent_notice,calendar_agent_reply,calendar_agent_evidence,calendar_agent_details;
let calendar_agent_delete_state,calendar_agent_delete_writable,calendar_agent_delete_selected,calendar_agent_delete_epoch,requests,events;
const gm_account_allowed=a=>gm_accounts.includes(a),ac_current_goal=()=>goal&&goal.id===ac_selected_id?goal:null;
const ac_goal_allowed=g=>g.project_id===gm_project&&g.owner_id===gm_owner,chat_session_index=id=>chat_sessions.findIndex(s=>s.id===id);
const chat_card_scope_current=(s,c)=>s.focus_project===c.project&&s.focus_owner===c.owner,chat_reply_context_valid=c=>c.invalid!==true;
const redraw=()=>{},ac_state=s=>s,ac_add=(v,title,status,detail,id)=>v.nodes.push({title,status,detail,id});
const host={request:(method,args,cb)=>requests.push({method,args:clone(args),cb})};
let unexpectedGoalWrites=0;const core_upsert_goal=()=>{unexpectedGoalWrites++;throw Error('Unexpected Goal write')},core_finish_run=core_upsert_goal,core_begin_action=core_upsert_goal;
__FUNCTIONS__
const checks={},check=(name,value)=>checks[name]=!!value;
function reset(){
 for(const n of disk.readdirSync(root))disk.unlinkSync(root+'/'+n);
 gm_user_id='user-A';gm_accounts=['local','account-A'];gm_project='project-A';gm_owner='owner-A';core_storage_ready=true;gm_ready=true;
 chat_selected_id='chat-A';ac_selected_chat='chat-A';ac_selected_id='goal-A';
 goal={id:'goal-A',version:3,status:'planned',archived:false,project_id:gm_project,owner_id:gm_owner};
 const card={id:'candidate-A',session_id:'chat-A',account_id:'account-A',project:gm_project,owner:gm_owner,action:'calendar_candidate',state:'opened',revision:2,payload:{title:'Synthetic event',start:'2026-10-12T15:00:00+08:00',end:'2026-10-12T15:30:00+08:00',time_zone:'Asia/Shanghai',location:'Synthetic room'}};
 chat_sessions=[{id:'chat-A',focus_project:gm_project,focus_owner:gm_owner,proposals:[card]}];
 const payload={request_id:'create-request-A',title:card.payload.title,start:'2026-10-12T15:00',end:'2026-10-12T15:30',timezone:'Asia/Shanghai',location:card.payload.location,notes:'合成 "引号" \\ 路径\n换行'};
 const event={id:'event-A',...clone(payload)};
 const binding={goal_id:goal.id,plan_revision:goal.version,project_id:gm_project,owner_id:gm_owner,user_id:gm_user_id,accounts:JSON.stringify(gm_accounts),account_id:'account-A',session_id:chat_selected_id,candidate_id:card.id,candidate_revision:card.revision,candidate_json:JSON.stringify(card.payload),payload,receipt_status:'verified',verification:{event_id:event.id,add_call_id:'create-host-A',get_call_id:'create-read-A',event}};
 calendar_agent_state={schema:1,request_id:payload.request_id,turn_id:'create-turn-A',status:'turn_completed',user_id:gm_user_id,accounts:JSON.stringify(gm_accounts),previous_requests:[],binding};
 calendar_agent_busy=false;calendar_agent_writable=true;calendar_agent_notice='';calendar_agent_reply='';calendar_agent_evidence='';calendar_agent_details=false;
 calendar_agent_delete_state={schema:1,records:[]};calendar_agent_delete_writable=true;calendar_agent_delete_selected='';calendar_agent_delete_epoch=0;requests=[];events=[];writeFail=false;
 return binding;
}
const answer=(n,r)=>requests[n].cb(clone(r));
function started(){reset();calendar_agent_delete_select();calendar_agent_delete_confirm();return calendar_agent_delete_state.records[0]}
function completed(){const r=started();answer(0,{is_ok:true,data:{open:true}});answer(1,{is_ok:true,data:{turn_id:'delete-turn-A',text:'Synthetic reply does not prove deletion'}});return r}
function row(tool,id,data,record){return {role:'tool',lane:'person',turn_id:record.turn_id,thread_id:record.turn_id,tool_name:tool,tool_call_id:'tool-'+id,host_calendar_receipt:{source:'broker_tool_result',owner:'os.calendar',caller:'card.muse-goals',kernel_persisted:true,turn_id:record.turn_id,session_id:'session-A',tool_call_id:'tool-'+id,call_id:'host-'+id,tool,args_digest:tool==='calendar.remove_event'?record.remove_digest:record.get_digest,terminal:'ok',result:{ok:true,data}}}}
function rows(record){return [row('calendar.get_event','before',{found:true,event:clone(record.expected)},record),row('calendar.remove_event','remove',{removed:true},record),row('calendar.get_event','after',{found:false,event:null},record)]}
function canonical(v){return v&&typeof v==='object'?Array.isArray(v)?v.map(canonical):Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v}
const digest=v=>'sha256:'+fs.sha256(JSON.stringify(canonical(v)));
let binding=reset();check('verified_existing_creation_is_required',calendar_agent_delete_target()!=null);
calendar_agent_delete_select();check('selection_has_no_host_call',requests.length===0&&calendar_agent_delete_state.records.length===0);
const selection=JSON.parse(calendar_agent_delete_selected),expected=selection.expected;
check('stable_id_and_all_eight_expected_fields',Object.keys(expected).sort().join(',')==='end,id,location,notes,request_id,start,timezone,title'&&expected.id===binding.verification.event_id&&expected.request_id===binding.payload.request_id);
const hashes=calendar_agent_delete_args(expected);check('canonical_get_digest_matches_kernel_algorithm',hashes.get_digest===digest({id:expected.id}));check('canonical_remove_digest_matches_kernel_algorithm',hashes.remove_digest===digest({id:expected.id,expected}));
check('creation_binding_and_goal_not_changed',JSON.stringify(calendar_agent_state.binding)===JSON.stringify(binding)&&goal.version===3&&goal.status==='planned');
reset();calendar_agent_delete_confirm();check('no_selection_no_dispatch',requests.length===0);
const mutations={user:()=>gm_user_id='user-B',accounts:()=>gm_accounts=['local'],account_revoked:()=>gm_accounts=[],project:()=>gm_project='project-B',owner:()=>gm_owner='owner-B',chat:()=>chat_selected_id='chat-B',matter:()=>ac_selected_id='goal-B',plan:()=>goal.version=4,candidate:()=>chat_sessions[0].proposals[0].revision=3,expected:()=>calendar_agent_state.binding.verification.event.location='Changed',creation_turn:()=>calendar_agent_state.turn_id='other-turn',unverified:()=>calendar_agent_state.binding.receipt_status='accepted',archived:()=>goal.archived=true};
for(const [name,change] of Object.entries(mutations)){reset();calendar_agent_delete_select();change();calendar_agent_delete_confirm();check('selected_'+name+'_change_blocks_dispatch',requests.length===0)}
started();const initial=JSON.parse(storage_read('calendar-agent-delete.json'));check('journal_saved_before_session_open',requests.length===1&&initial.records[0].status==='in_flight'&&calendar_agent_delete_selected==='');
check('pending_delete_blocks_calendar_mail',!mail_calendar_verified());
answer(0,{is_ok:true,data:{open:true}});const prompt=requests[1].args;
check('official_relay_only_and_app_trigger',requests[0].method==='octos.session.open'&&requests[1].method==='octos.turn.start'&&prompt.trigger==='app');
check('prompt_exact_target_expected_and_order',prompt.text.includes(JSON.stringify({id:expected.id}))&&prompt.text.includes(JSON.stringify({id:expected.id,expected}))&&prompt.text.indexOf('1. calendar.get_event')<prompt.text.indexOf('2. calendar.remove_event')&&prompt.text.includes('3. 仅removed=true'));
let record=completed(),rs=rows(record);check('three_matching_real_receipts_verify',calendar_agent_delete_result(rs,record).status==='verified');
answer(2,{is_ok:true,data:{messages:rs}});check('receipt_status_and_disk_readback_verified',calendar_agent_delete_state.records[0].receipt_status==='verified'&&JSON.parse(storage_read('calendar-agent-delete.json')).records[0].verification.found===false);
const view={nodes:[],next:''};calendar_agent_project(view,goal);check('chain_only_projects_exact_delete_receipt',view.nodes.some(n=>n.title==='官方日历删除精确核验'&&n.status==='verified')&&view.next.includes('未整体完成'));
check('verified_delete_blocks_old_mail_premise',!mail_calendar_verified());check('whole_goal_not_completed_or_replanned',goal.status==='planned'&&goal.version===3&&unexpectedGoalWrites===0);
const bad={missing_receipt:r=>delete r[1].host_calendar_receipt,wrong_owner:r=>r[1].host_calendar_receipt.owner='other',wrong_caller:r=>r[1].host_calendar_receipt.caller='other',wrong_receipt_turn:r=>r[1].host_calendar_receipt.turn_id='other',wrong_lane:r=>r[1].lane='system',wrong_session:r=>r[2].host_calendar_receipt.session_id='other',wrong_target_digest:r=>r[2].host_calendar_receipt.args_digest=digest({id:'other-event'}),wrong_expected_digest:r=>r[1].host_calendar_receipt.args_digest=digest({id:'event-A',expected:{...record.expected,location:'Changed'}}),wrong_expected_event:r=>r[0].host_calendar_receipt.result.data.event.location='Changed',changed_stable_id:r=>r[0].host_calendar_receipt.result.data.event.id='other-event',missing_expected_field:r=>delete r[0].host_calendar_receipt.result.data.event.notes,nonpersisted:r=>r[1].host_calendar_receipt.kernel_persisted=false,omitted:r=>r[1].host_calendar_receipt.result_omitted=true,duplicate_call_id:r=>r[2].host_calendar_receipt.call_id=r[1].host_calendar_receipt.call_id,duplicate_tool_call_id:r=>{r[2].tool_call_id=r[1].tool_call_id;r[2].host_calendar_receipt.tool_call_id=r[1].tool_call_id},missing_null_event:r=>delete r[2].host_calendar_receipt.result.data.event,present_after:r=>r[2].host_calendar_receipt.result.data={found:true,event:clone(record.expected)},wrong_order:r=>r.reverse(),removed_false:r=>r[1].host_calendar_receipt.result.data.removed=false,model_claim_only:r=>r.splice(0,3,{role:'assistant',content:'deleted'})};
for(const [name,change] of Object.entries(bad)){const altered=clone(rs);change(altered);check(name+'_cannot_verify',calendar_agent_delete_result(altered,record).status!=='verified')}
for(const key of ['id','request_id','title','start','end','timezone','location','notes']){const altered=clone(rs);altered[0].host_calendar_receipt.result.data.event[key]='Changed';check('expected_'+key+'_change_not_verified',calendar_agent_delete_result(altered,record).status!=='verified')}
const alias=clone(rs);alias[1].tool_name='calendar_remove_event';check('official_underscore_alias_with_canonical_receipt',calendar_agent_delete_result(alias,record).status==='verified');
const wrongDelete=clone(rs);wrongDelete[1].host_calendar_receipt.args_digest=digest({id:'other-event',expected:record.expected});check('wrong_remove_id_digest_not_verified',calendar_agent_delete_result(wrongDelete,record).status!=='verified');
const omittedExpected=clone(rs);omittedExpected[1].host_calendar_receipt.args_digest=digest({id:record.expected.id});check('remove_without_expected_digest_not_verified',calendar_agent_delete_result(omittedExpected,record).status!=='verified');
check('history_over_200_rows_not_verified',calendar_agent_delete_result(Array.from({length:201},()=>rs[0]),record).status==='unknown');
const onlyRemove=rs.slice(1,2);check('remove_alone_not_verified',calendar_agent_delete_result(onlyRemove,record).status==='unknown');
check('remove_without_absence_only_accepted',calendar_agent_delete_result(rs.slice(0,2),record).status==='accepted');
const cancel=clone(rs.slice(0,2));cancel[1].host_calendar_receipt.terminal='cancelled';cancel[1].host_calendar_receipt.result={ok:false};check('cancelled_delete_failed_without_success',calendar_agent_delete_result(cancel,record).status==='failed');
const extra=clone(rs);extra.push(row('calendar.get_event','duplicate',{found:false,event:null},record));check('extra_duplicate_sequence_not_verified',calendar_agent_delete_result(extra,record).status==='unknown');
for(const [name,change] of Object.entries(mutations)){record=completed();rs=rows(record);change();answer(2,{is_ok:true,data:{messages:rs}});check('late_history_'+name+'_not_projected',calendar_agent_delete_state.records[0].receipt_status==='unknown')}
record=started();gm_user_id='user-B';answer(0,{is_ok:true,data:{open:true}});check('identity_changed_before_turn_blocks_turn',requests.length===1&&calendar_agent_delete_state.records[0].status==='blocked');
record=started();answer(0,{is_ok:true,data:{open:true}});goal.version=4;answer(1,{is_ok:true,data:{turn_id:'late-delete-turn'}});check('late_turn_keeps_id_unknown_no_history',calendar_agent_delete_state.records[0].turn_id==='late-delete-turn'&&calendar_agent_delete_state.records[0].status==='unknown'&&requests.length===2);
record=started();answer(0,{is_ok:true,data:{open:true}});answer(1,{is_ok:false,error:'synthetic timeout'});const count=requests.length;
calendar_agent_delete_select();calendar_agent_delete_confirm();check('unknown_delete_not_replayed',requests.length===count&&calendar_agent_delete_state.records.length===1);
record=started();calendar_agent_delete_state={schema:1,records:[]};calendar_agent_boot();check('restart_inflight_becomes_unknown_no_dispatch',calendar_agent_delete_state.records.length===1&&calendar_agent_delete_state.records[0].status==='unknown'&&requests.length===1);
calendar_agent_delete_select();calendar_agent_delete_confirm();check('restart_unknown_not_replayed',requests.length===1);
reset();calendar_agent_delete_select();writeFail=true;calendar_agent_delete_confirm();check('journal_failure_blocks_host',requests.length===0&&!calendar_agent_delete_writable);
record=completed();const snapshot=JSON.stringify(calendar_agent_delete_state);calendar_agent_delete_history(0);answer(2,{is_ok:true,data:{messages:rows(record)}});answer(3,{is_ok:true,data:{messages:[]}});check('older_history_callback_epoch_ignored',JSON.stringify(calendar_agent_delete_state)===snapshot);
record=completed();calendar_agent_delete_state.records[0].expected.id='other';storage_write('calendar-agent-delete.json',JSON.stringify(calendar_agent_delete_state));calendar_agent_delete_writable=true;calendar_agent_delete_boot();check('corrupt_binding_preserved_and_blocks_new_requests',!calendar_agent_delete_writable&&JSON.parse(storage_read('calendar-agent-delete.json')).records[0].expected.id==='other');
const template=clone(started());reset();calendar_agent_delete_state.records=Array.from({length:32},(_,n)=>{const old=clone(template);old.request_id='old-delete-'+n;old.expected.id='old-event-'+n;old.binding.verification.event_id=old.expected.id;old.binding.verification.event.id=old.expected.id;const d=calendar_agent_delete_args(old.expected);old.get_digest=d.get_digest;old.remove_digest=d.remove_digest;return old});calendar_agent_delete_select();calendar_agent_delete_confirm();check('bounded_journal_no_new_dispatch',requests.length===0);
check('no_direct_calendar_model_or_mail_transport',requests.every(r=>['octos.session.open','octos.turn.start','octos.session.history'].includes(r.method)));
console.log(JSON.stringify({checks,failed:Object.keys(checks).filter(k=>!checks[k]),external_calls:0,goal_writes:unexpectedGoalWrites,kind:'SOURCE_BOUND_NODE_PROJECTION_FIXTURE'}));
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    source=a.source.read_text();identity=json.loads((OWN/'calendar-delete-identity.json').read_text());sha=lambda t:hashlib.sha256(t.encode()).hexdigest()
    assert sha(source)==identity['source_sha256']
    patched=apply(source,(OWN/'calendar-delete.patch').read_text());assert sha(patched)==identity['expected_source_sha256']
    names=NAMES+identity['added_functions']
    program=JS.replace('__FUNCTIONS__','\n'.join(projection(function(patched,n)) for n in names))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gpt02-calendar-delete-') as d:
        run=subprocess.run([shutil.which('node') or 'node','-',d],input=program,text=True,capture_output=True)
        if run.returncode:
            a.out.with_suffix('.adapter-error.txt').write_text(run.stderr);raise RuntimeError(run.stderr)
        result=json.loads(run.stdout)
    result.update(source_sha256=identity['source_sha256'],expected_source_sha256=identity['expected_source_sha256'],projected_functions=names,total=len(result['checks']),passed=sum(result['checks'].values()),boundary='Actual proposed functions projected into Node. Synthetic scope/time/Host receipts and temporary storage. No VM, legal fifth-tool admission, native consent or real deletion proof.')
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['passed','total','failed','external_calls','goal_writes']}));raise SystemExit(bool(result['failed']))

if __name__=='__main__':main()
