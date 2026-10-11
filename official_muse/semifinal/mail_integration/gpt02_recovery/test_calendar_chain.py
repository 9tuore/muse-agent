#!/usr/bin/env python3
"""Source-bound Node projection fixture. No official VM, GUI or external calls."""
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

OWN = Path(__file__).resolve().parent
NAMES = ['calendar_agent_event_matches','calendar_agent_binding_valid','calendar_agent_binding_current',
 'calendar_agent_wall','calendar_agent_prepare_candidate','calendar_agent_same_candidate',
 'calendar_agent_submit_candidate','calendar_agent_link_result','calendar_agent_project',
 'calendar_agent_tool_name','calendar_agent_receipt_status','calendar_agent_save',
 'calendar_agent_boot','calendar_agent_submit','calendar_agent_submit_bound','calendar_agent_keep_previous',
 'calendar_agent_history']


def project(text):
    # Closed observed subset only: this adapter is not an OctoScript compiler.
    text = re.sub(r'\bfn\s+(\w+)\(',r'function \1(',text)
    text = re.sub(r'\bfn\(', 'function(', text).replace(',||', ',()=>')
    text = text.replace('nil','null').replace('.search(','.indexOf(')
    text = re.sub(r'for (\w+) in min\(([^\n{]+)\) \{',r'for (const \1 of range(min(\2))) {',text)
    text = re.sub(r'for (\w+) in (\[[^\n]+\]) \{',r'for (const \1 of \2) {',text)
    text = re.sub(r'for (\w+) in ([\w.\[\]"]+) \{',r'for (const \1 of \2) {',text)
    text = re.sub(r'\bif ([^{}]+)\{',lambda m:'if ('+m.group(1).strip()+') {',text)
    atom = r'(?:\b\w+(?:\.\w+|\["\w+"\])*)'
    text = re.sub('('+atom+r')\.is_object\(\)',r'gm_object(\1)',text)
    text = re.sub('('+atom+r')\.is_array\(\)',r'gm_array(\1)',text)
    text = re.sub('('+atom+r')\.is_string\(\)',r'gm_text(\1)',text)
    text = re.sub('('+atom+r')\.to_json\(\)',r'JSON.stringify(\1)',text)
    text = text.replace('.len()', '.length')
    # Source contains adjacent declarations/statements and unpunctuated object keys.
    text = re.sub(r'([^\s{}]) (let |return )',r'\1; \2',text)
    text = re.sub(r'([\w."\]\)])\s+([a-zA-Z_]\w*:\s)',r'\1, \2',text)
    text = re.sub(r'("(?:[^"\\]|\\.)*"|true|false|\]) ((?:\w+\.)*\w+\s*=)',r'\1; \2',text)
    text = re.sub(r'("(?:[^"\\]|\\.)*") (\w+\()',r'\1; \2',text)
    text = text.replace('redraw() return', 'redraw(); return').replace('calendar_agent_save() redraw()', 'calendar_agent_save(); redraw()')
    text = text.replace('ui_error = error redraw()', 'ui_error = error; redraw()')
    text = text.replace('added = data.id add_call =', 'added = data.id; add_call =')
    text = text.replace('readback = event get_call =', 'readback = event; get_call =')
    text = text.replace('evidence count =','evidence; count =')
    text = text.replace('let epoch = calendar_agent_history_epoch let binding', 'let epoch = calendar_agent_history_epoch; let binding')
    text = text.replace('let user = gm_user_id let accounts', 'let user = gm_user_id; let accounts')
    return text

JS = r'''
const fs=require('fs');const root=process.argv[2];
fs.exists=name=>fs.existsSync(root+'/'+name);
const clone=v=>JSON.parse(JSON.stringify(v));
const gm_object=v=>v!==null && typeof v==='object' && !Array.isArray(v),gm_array=Array.isArray;
const gm_text=v=>typeof v==='string',gm_string=(v,n)=>typeof v==='string'&&Buffer.byteLength(v)<=n,gm_number=v=>typeof v==='number'&&Number.isFinite(v);
const gm_has=(v,key)=>gm_object(v)&&Object.hasOwn(v,key);
Object.defineProperty(String.prototype,'parse_json',{value:function(){try{return JSON.parse(this)}catch{return null}}});
const floor=Math.floor,min=Math.min,range=n=>Array.from({length:n},(_,i)=>i);
let gm_user_id='user-A',gm_accounts=['local','account-A'],gm_project='project-A',gm_owner='owner-A';
let core_storage_ready=true,gm_ready=true,chat_selected_id='chat-A',ac_selected_chat='chat-A',ac_selected_id='goal-A';
let calendar_agent_candidate=null,calendar_agent_state,calendar_agent_writable=true,calendar_agent_busy=false,calendar_agent_history_epoch=0;
let calendar_agent_reply='',calendar_agent_evidence='',calendar_agent_input_text='',calendar_agent_details=false,calendar_agent_notice='',ui_error='';
let goal,chat_sessions,requests=[],timer=0,writeFail=false,apiCount=0;
const redraw=()=>{},time_now=()=>1791686400,random_u32=()=>++timer;
const gm_account_allowed=id=>gm_accounts.includes(id),ac_goal_allowed=g=>g.project_id===gm_project&&g.owner_id===gm_owner;
const ac_current_goal=()=>goal&&goal.id===ac_selected_id?goal:null;
const chat_session_index=id=>chat_sessions.findIndex(s=>s.id===id);
const chat_card_scope_current=(s,c)=>s.focus_project===c.project&&s.focus_owner===c.owner;
const chat_reply_context_valid=c=>c.refs_valid!==false;
const chat_payload_error=(action,p)=>!gm_object(p)||!p.title||!p.start||!p.end||!p.time_zone||Date.parse(p.start)<=time_now()*1000||Date.parse(p.end)<=Date.parse(p.start)?'fixture invalid candidate':'';
const calendar_iso_epoch=v=>Date.parse(v)/1000;
const calendar_display_time=v=>new Date(Date.parse(v)+28800000).toISOString().slice(0,16).replace('T',' ');
const storage_write=(name,data)=>{if(writeFail)return 'fixture fail';fs.writeFileSync(root+'/'+name,data);return null};
const storage_read=name=>fs.existsSync(root+'/'+name)?fs.readFileSync(root+'/'+name,'utf8'):'';
const host={request:(method,args,callback)=>{apiCount++;requests.push({method,args:clone(args),callback})}};
const ac_add=(view,title,status,detail,id)=>view.nodes.push({title,status,detail,id});
__FUNCTIONS__
function reset(){
 gm_user_id='user-A';gm_accounts=['local','account-A'];gm_project='project-A';gm_owner='owner-A';
 chat_selected_id='chat-A';ac_selected_chat='chat-A';ac_selected_id='goal-A';writeFail=false;
 goal={id:'goal-A',version:1,status:'planned',archived:false,project_id:gm_project,owner_id:gm_owner};
 const card={id:'candidate-A',session_id:'chat-A',account_id:'account-A',project:gm_project,owner:gm_owner,action:'calendar_candidate',state:'candidate',revision:1,
  payload:{title:'Fixture appointment',start:'2026-10-12T15:00:00+08:00',end:'2026-10-12T16:00:00+08:00',time_zone:'Asia/Shanghai',location:'Fixture room'}};
 chat_sessions=[{id:'chat-A',focus_project:gm_project,focus_owner:gm_owner,proposals:[card]}];
 calendar_agent_candidate=null;calendar_agent_state={schema:1,request_id:'',turn_id:'',status:'idle',user_id:'',accounts:'',previous_requests:[]};
 calendar_agent_writable=true;calendar_agent_busy=false;calendar_agent_reply='';calendar_agent_evidence='';calendar_agent_notice='';requests=[];
 return card;
}
const checks={};const check=(name,ok)=>checks[name]=!!ok;
const answer=(i,data)=>requests[i].callback(data);
function started(){const card=reset();calendar_agent_prepare_candidate(card);calendar_agent_submit_candidate();return card}
function completed(){started();answer(0,{is_ok:true,data:{open:true}});answer(1,{is_ok:true,data:{turn_id:'turn-A',text:'MODEL CLAIM: complete'}})}
function rows(){
 const p=calendar_agent_state.binding.payload,event={id:'event-A',...clone(p)};
 const make=(tool,id,data)=>({role:'tool',lane:'person',turn_id:'turn-A',thread_id:'turn-A',tool_name:tool,tool_call_id:id,
  host_calendar_receipt:{source:'broker_tool_result',owner:'os.calendar',caller:'card.muse-goals',kernel_persisted:true,turn_id:'turn-A',tool_call_id:id,call_id:'host-'+id,tool:calendar_agent_tool_name(tool),terminal:'ok',result:{ok:true,data}}});
 return [make('calendar_add_event','add-A',{id:'event-A',start:p.start}),make('calendar_get_event','get-A',{found:true,event})];
}
let card=reset();check('selected_candidate_prepares',calendar_agent_prepare_candidate(card));
check('payload_maps_timezone_and_wall_time',calendar_agent_candidate.payload.timezone==='Asia/Shanghai'&&calendar_agent_candidate.payload.start==='2026-10-12T15:00'&&calendar_agent_candidate.payload.notes==='');
calendar_agent_submit_candidate();let persisted=JSON.parse(storage_read('calendar-agent-state.json'));
check('binding_persisted_before_open',requests.length===1&&requests[0].method==='octos.session.open'&&persisted.binding.goal_id==='goal-A'&&persisted.binding.plan_revision===1&&persisted.binding.project_id===gm_project&&persisted.binding.owner_id===gm_owner&&persisted.binding.payload.request_id===persisted.request_id);
answer(0,{is_ok:true,data:{open:true}});
check('only_official_relay_turn',requests.length===2&&requests[1].method==='octos.turn.start'&&requests[1].args.text.includes(calendar_agent_state.request_id)&&requests[1].args.text.includes('calendar.get_event')&&requests[1].args.text.includes('Fixture appointment'));
answer(1,{is_ok:true,data:{turn_id:'turn-A',text:'MODEL CLAIM: complete'}});
check('turn_id_persisted_model_claim_not_verified',calendar_agent_state.turn_id==='turn-A'&&calendar_agent_state.binding.receipt_status==='unknown'&&goal.status==='planned');
answer(2,{is_ok:true,data:{messages:rows()}});
check('exact_add_get_host_pair_verified',calendar_agent_state.binding.receipt_status==='verified'&&calendar_agent_state.binding.verification.event_id==='event-A');
check('receipt_binding_saved_readback',JSON.parse(storage_read('calendar-agent-state.json')).binding.verification.get_call_id==='host-get-A');
let view={nodes:[],next:''};check('verified_projects_selected_current_chain',calendar_agent_project(view,goal)&&view.nodes.some(n=>n.status==='verified')&&view.next.includes('尚未接通'));
check('goal_not_falsely_completed',goal.status==='planned');
completed();let threadRows=rows();for(const r of threadRows)delete r.turn_id;
check('thread_only_kernel_rows_use_existing_fallback',calendar_agent_link_result(threadRows).status==='verified');
for(const [name,mutate] of [
 ['goal_revision',()=>goal.version++],['project',()=>gm_project='project-B'],['owner',()=>gm_owner='owner-B'],
 ['user',()=>gm_user_id='user-B'],['accounts',()=>gm_accounts=['local','account-B']],['matter_selection',()=>ac_selected_id='goal-B'],
 ['chat',()=>chat_selected_id='chat-B'],['candidate_revision',()=>chat_sessions[0].proposals[0].revision++],
 ['candidate_text',()=>chat_sessions[0].proposals[0].payload.title='Changed'],['candidate_account',()=>chat_sessions[0].proposals[0].account_id='local']]){
 completed();const rs=rows();mutate();answer(2,{is_ok:true,data:{messages:rs}});
 check(name+'_late_history_not_verified',calendar_agent_state.binding.receipt_status==='unknown');
 view={nodes:[],next:''};check(name+'_not_projected_current',!calendar_agent_project(view,goal));
}
started();goal.version++;answer(0,{is_ok:true,data:{open:true}});
check('changed_plan_before_open_blocks_turn',requests.length===1&&calendar_agent_state.status==='blocked');
started();answer(0,{is_ok:true,data:{open:true}});gm_owner='owner-B';answer(1,{is_ok:true,data:{turn_id:'late-turn',text:'wrong identity'}});
check('late_turn_id_preserved_without_current_success',calendar_agent_state.status==='unknown'&&calendar_agent_state.turn_id==='late-turn'&&calendar_agent_reply===''&&requests.length===2);
for(const [name,mutate] of [
 ['model_only',r=>[]],['add_only',r=>[r[0]]],['get_only',r=>[r[1]]],
 ['wrong_event_id',r=>{r[1].host_calendar_receipt.result.data.event.id='event-B';return r}],
 ['wrong_request',r=>{r[1].host_calendar_receipt.result.data.event.request_id='another';return r}],
 ['wrong_title',r=>{r[1].host_calendar_receipt.result.data.event.title='different';return r}],
 ['wrong_end',r=>{r[1].host_calendar_receipt.result.data.event.end='2026-10-12T17:00';return r}],
 ['wrong_timezone',r=>{r[1].host_calendar_receipt.result.data.event.timezone='UTC';return r}],
 ['unexpected_notes',r=>{r[1].host_calendar_receipt.result.data.event.notes='MODEL-added notes';return r}],
 ['absent_event',r=>{r[1].host_calendar_receipt.result.data={found:false,event:null};return r}],
 ['unpersisted',r=>{r[0].host_calendar_receipt.kernel_persisted=false;return r}],
 ['wrong_call',r=>{r[0].host_calendar_receipt.tool_call_id='another';return r}],
 ['wrong_owner',r=>{r[0].host_calendar_receipt.owner='another';return r}],
 ['other_lane',r=>{r[0].lane='system_agent';return r}],
 ['conflicting_thread',r=>{r[0].thread_id='another';return r}],
 ['old_turn',r=>{r[0].turn_id='another';return r}],
 ['omitted_result',r=>{r[1].host_calendar_receipt.result_omitted=true;return r}],
 ['oversized_host_call',r=>{r[1].host_calendar_receipt.call_id='x'.repeat(257);return r}],
 ['too_many_rows',r=>Array(201).fill(r[0])],
 ['duplicate_conflict',r=>{const bad=clone(r[0]);bad.host_calendar_receipt.result.data.id='event-B';return [...r,bad]}]]){
 completed();let rs=mutate(rows());check(name+'_not_verified',calendar_agent_link_result(rs).status!=='verified');
}
completed();let rs=rows();rs[0].host_calendar_receipt.terminal='error';rs[0].host_calendar_receipt.result={ok:false,error:{kind:'not_granted'}};rs=[rs[0]];
check('authoritative_error_is_failed',calendar_agent_link_result(rs).status==='failed');
completed();rs=rows();rs[0].host_calendar_receipt.terminal='cancelled';delete rs[0].host_calendar_receipt.result;
check('cancel_is_not_success',calendar_agent_link_result([rs[0]]).status==='failed');
completed();rs=rows();rs[1].host_calendar_receipt.terminal='error';rs[1].host_calendar_receipt.result={ok:false};
check('add_without_successful_readback_only_accepted',calendar_agent_link_result(rs).status==='accepted');
started();answer(0,{is_ok:false,error:'fixture refusal'});check('open_refusal_never_starts_turn',requests.length===1&&calendar_agent_state.status==='blocked');
started();answer(0,{is_ok:true,data:{open:true}});answer(1,{is_ok:false,error:'fixture timeout'});const count=requests.length;
calendar_agent_boot();calendar_agent_submit_candidate();check('unknown_not_replayed',requests.length===count&&calendar_agent_state.status==='unknown');
const original=calendar_agent_state.request_id;calendar_agent_keep_previous();
check('archive_preserves_full_binding',calendar_agent_state.previous_requests[0].request_id===original&&calendar_agent_state.previous_requests[0].binding.goal_id==='goal-A');
calendar_agent_submit_candidate();check('archived_same_candidate_not_replayed',requests.length===count);
card=reset();calendar_agent_prepare_candidate(card);writeFail=true;calendar_agent_submit_candidate();check('persistence_failure_blocks_open',requests.length===0&&!calendar_agent_writable);
card=reset();ac_selected_id='';check('explicit_matter_selection_required',!calendar_agent_prepare_candidate(card)&&requests.length===0);
card=reset();card.payload.time_zone='UTC';check('unsupported_zone_honestly_blocks_candidate_bridge',!calendar_agent_prepare_candidate(card));
card=reset();card.payload.start='2026-10-12T15:00:30+08:00';check('seconds_not_silently_truncated',!calendar_agent_prepare_candidate(card));
completed();calendar_agent_state.status='in_flight';calendar_agent_save();const requestCount=requests.length;calendar_agent_boot();
check('restart_keeps_binding_unknown_no_dispatch',calendar_agent_state.status==='unknown'&&calendar_agent_state.binding.goal_id==='goal-A'&&requests.length===requestCount);
completed();rs=rows();answer(2,{is_ok:true,data:{messages:rs}});calendar_agent_state.binding.verification=null;calendar_agent_save();calendar_agent_boot();
check('malformed_verified_record_blocks_new_requests',!calendar_agent_writable);
console.log(JSON.stringify({checks,failed:Object.keys(checks).filter(k=>!checks[k]),external_calls:0,boundary:'Actual source functions projected into Node with fixture scope/UI/time/Host adapters and temporary JSON readback; NOT actual Splash VM/Host or Calendar creation proof.'}));
'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    source=a.source.read_text();identity=json.loads((OWN/'calendar-chain-identity.json').read_text());sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
    assert sha(source)==identity['source_sha256']
    patched=apply(source,(OWN/'calendar-chain.patch').read_text());assert sha(patched)==identity['expected_source_sha256']
    baseline={'chat_calendar_still_opens_private_disabled_form':'if !calendar_enabled()' not in function(source,'chat_apply_proposal'),
              'agent_request_has_no_matter_binding':'goal_id' not in function(source,'calendar_agent_submit'),
              'chain_has_only_old_calendar_block':'calendar_agent_project' not in function(source,'ac_projection')}
    assert all(baseline.values()),baseline
    program=JS.replace('__FUNCTIONS__','\n'.join(project(function(patched,name)) for name in NAMES))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gpt02-calendar-chain-') as d:
        run=subprocess.run([shutil.which('node') or 'node','-',d],input=program,text=True,capture_output=True)
        if run.returncode:
            a.out.with_suffix('.adapter-error.txt').write_text(run.stderr)
            raise RuntimeError(run.stderr)
        result=json.loads(run.stdout)
    result.update(total=len(result['checks']),passed=sum(result['checks'].values()),baseline=baseline,source_sha256=identity['source_sha256'],expected_source_sha256=identity['expected_source_sha256'],projected_functions=NAMES)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','total','failed','external_calls']},ensure_ascii=False))
    raise SystemExit(bool(result['failed']))


if __name__=='__main__':main()
