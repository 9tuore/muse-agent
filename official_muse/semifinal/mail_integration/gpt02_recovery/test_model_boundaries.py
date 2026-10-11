#!/usr/bin/env python3
"""Actual six call argument objects and current guards, synthetic Node fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
from test_recovery import function
from test_model_input import JS, NAMES, project_model

OWN = Path(__file__).resolve().parent
CALLERS = ['mail_analysis_pump','schedule_auto_reply','calendar_model_candidate','mail_model_draft','send_chat','ask_model']
GUARDS = ['gm_get','gm_has','chat_candidate_current','chat_model_request_current',
          'goal_model_request_current','mail_model_request_current','calendar_generation_current','mail_watch_alert_index']

def object_at(text, start):
    depth = 0
    quoted = escaped = False
    for i in range(start,len(text)):
        c = text[i]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return text[start:i+1]
    raise AssertionError('unclosed source object')

EXTRA = r'''
let mail_model_pending,mail_account,mail_selected,mail_watch,calendar_links,memory_sources,guardConflict,guardForgotten;
let mail_analysis={enabled:true,permitted:true},mail_analysis_epoch=1,epoch=1,gi=0,li=0,i=0,revision=3;
let alert={account_id:'account-A',key:'alert-A',subject:'Synthetic invitation',source_body:'Synthetic source',source_message:{date:'2026-10-11'}};
let link={account_id:'account-A',message_id:'message-A'},event={id:'event-A',title:'Synthetic event',start:'2026-10-12T15:00',end:'2026-10-12T16:00',version:2};
let message={body:'Synthetic original',address:'self@example.invalid'},project='project-A',owner='owner-A';
let subject='Synthetic subject',body='Synthetic original',reference_time='2026-10-11',automatic_creation=null,goal_id='goal-A';
let reply_task='Synthetic draft instruction',model_input={intent:'synthetic intent',source_account:'account-A',recipient:'self@example.invalid'};
let config={task:'Synthetic Chat task',schema:clone(schema),class:'strong'},task={goal:'Synthetic Goal',source:'Synthetic Goal source',items:['Synthetic item']};
const calendar_link_index=id=>calendar_links.findIndex(l=>l.goal_id===id),core_source_index=(id,a)=>memory_sources.findIndex(s=>s.source_id===id&&s.account===a);
const core_memory_index=(id,a)=>memory.findIndex(m=>m.document.id===id&&m.account===a);
const gm_hit_conflicts=()=>guardConflict?[{}]:[],core_is_forgotten=()=>guardForgotten;
const mail_watch_account=a=>a==='account-A'?{id:a}:null;
function guardReset(){
 reset();guardConflict=false;guardForgotten=false;
 mail_model_pending=true;mail_account={id:'account-A'};mail_selected={id:'message-A'};
 mail_watch={alerts:[{key:'alert-A',status:'new'}]};
 mail_analysis={enabled:true,permitted:true};mail_analysis_epoch=1;epoch=1;
 goals=[{id:'goal-A',version:3,status:'planned',archived:false,project_id:'project-A',owner_id:'owner-A',mail_source:{source_id:'source-A',account_id:'account-A',message_id:'message-A'}}];
 calendar_links=[{goal_id:'goal-A',status:'candidate',version:2,account_id:'account-A',message_id:'message-A',source_id:'source-A',source_claim_id:'claim-A',candidate_revision:4,active_generation:{request_id:'generation-A'},candidate:{title:'Synthetic'},original_event:null,user_clarification:null}];
 memory_sources=[{source_id:'source-A',account:'account-A',content_sha256:'digest-A',updated_at:'revision-A'}];
 memory=[{account:'account-A',document:{id:'claim-A',revision:5,payload:{deleted:false,predicate:'synthetic'}}}];
 chat_sessions[0].focus_project='project-A';chat_sessions[0].focus_owner='owner-A';chat_sessions[0].proposals=[{id:'candidate-A',state:'candidate',payload:{title:'Synthetic'}}];
 chat_requests=[{id:'request-A',session_id:'chat-A',status:'running',project:'project-A',owner:'owner-A',candidate_id:'candidate-A',candidate_payload:JSON.stringify({title:'Synthetic'}),candidate_state:'candidate'}];
}
const generation={goal_id:'goal-A',goal_revision:3,account_id:'account-A',message_id:'message-A',source_id:'source-A',source_digest:'digest-A',source_revision:'revision-A',claim_revision:5,candidate_revision:4,request_id:'generation-A'};
const cases=__CALL_CASES__;
check('all_six_actual_call_sites_extracted',cases.length===6);
for(const c of cases){
 guardReset();const args=c.args(),original=JSON.stringify(args);muse_model_request('current-question',c.chat?'chat-A':'',c.bound?'goal-A':'',()=>true,args,r=>replies.push(r));flush();
 const wire=requests[0]?.args;
 check(c.name+'_official_wire',requests.length===1&&requests[0].method==='model.complete'&&Object.keys(wire).every(k=>allowed.includes(k))&&wire.class===args.class&&JSON.stringify(wire.schema)===JSON.stringify(args.schema)&&wire.task.startsWith(args.task));
 check(c.name+'_input_and_original_preserved',c.chat?Array.isArray(wire.input.messages)&&wire.input.messages.at(-1).content.startsWith('current-question'):JSON.stringify(wire.input.current)===JSON.stringify(args.input)&&wire.input.related_memory===context.text);
 check(c.name+'_args_unmodified',JSON.stringify(args)===original);
}
for(const [name,optional] of Object.entries({absent:{},nil:{class:null,allow_urls:null},class_only:{class:'strong'},urls_false:{allow_urls:false},urls_true:{allow_urls:true}})){
 reset();dispatch({task:'Synthetic optional fields',input:{source:'synthetic'},schema:clone(schema),...optional});flush();const wire=requests[0].args;
 check('optional_'+name+'_exact',Object.keys(wire).every(k=>allowed.includes(k))&&['class','allow_urls'].every(k=>optional[k]==null?!Object.hasOwn(wire,k):Object.hasOwn(wire,k)&&wire[k]===optional[k]));
}
reset();dispatch({task:'String input',input:'synthetic string',schema:clone(schema)});flush();check('string_input_preserved',requests[0].args.input.current==='synthetic string');
reset();dispatch({task:'Nil input',input:null,schema:clone(schema)});flush();check('nil_input_preserved',requests[0].args.input.current===null);
reset();dispatch({task:'Unauthorized source',input:{source_account:'revoked'},schema:clone(schema)});flush();check('source_account_guard_no_transport',requests.length===0&&!replies[0].is_ok);
guardReset();goals[0].mail_source.account_id='revoked';muse_model_request('synthetic','','goal-A',()=>true,{task:'Bound source',input:{},schema:clone(schema)},r=>replies.push(r));flush();check('bound_goal_source_guard_no_transport',requests.length===0&&!replies[0].is_ok);
reset();memory=[{memory_type:'preference',document:{id:'omitted'}}];context.hits=[];dispatch({task:'Schedule',input:{},schema:{properties:{policy:{}}}});flush();check('missing_schedule_preference_blocks_transport',requests.length===0&&replies[0].error.startsWith('memory_scope_incomplete:'));
function guarded(name,valid,change){
 guardReset();check(name+'_initially_current',valid());
 muse_model_request('current-question','chat-A','',valid,{task:'Guard fixture',messages:[],schema:clone(schema)},r=>replies.push(r));flush();change();requests[0].cb(clone(response));
 check(name+'_late_rejected',!replies[0].is_ok&&replies[0].error.startsWith('cancelled:'));
 guardReset();valid();muse_model_request('current-question','chat-A','',valid,{task:'Guard fixture',messages:[],schema:clone(schema)},r=>replies.push(r));change();flush();
 check(name+'_before_transport_rejected',requests.length===0&&replies.length===1&&!replies[0].is_ok&&replies[0].error.startsWith('cancelled:'));
}
guarded('chat_status',()=>chat_model_request_current('request-A','chat-A'),()=>chat_requests[0].status='cancelled');
guarded('chat_scope',()=>chat_model_request_current('request-A','chat-A'),()=>chat_sessions[0].focus_project='project-B');
guarded('chat_candidate_payload',()=>chat_model_request_current('request-A','chat-A'),()=>chat_sessions[0].proposals[0].payload.title='Changed');
guarded('goal_revision',()=>goal_model_request_current('goal-A',3),()=>goals[0].version=4);
guarded('goal_status',()=>goal_model_request_current('goal-A',3),()=>goals[0].status='running');
guarded('mail_account',()=>mail_model_request_current('account-A','message-A','alert-A'),()=>mail_account.id='account-B');
guarded('mail_message',()=>mail_model_request_current('account-A','message-A','alert-A'),()=>mail_selected.id='message-B');
guarded('mail_dismissed',()=>mail_model_request_current('account-A','message-A','alert-A'),()=>mail_watch.alerts[0].status='dismissed');
guarded('mail_pending',()=>mail_model_request_current('account-A','message-A','alert-A'),()=>mail_model_pending=false);
guarded('generation_revision',()=>calendar_generation_current(generation),()=>goals[0].version=4);
guarded('generation_source',()=>calendar_generation_current(generation),()=>memory_sources[0].content_sha256='changed');
guarded('generation_claim',()=>calendar_generation_current(generation),()=>memory[0].document.revision=6);
guarded('generation_request',()=>calendar_generation_current(generation),()=>calendar_links[0].active_generation.request_id='changed');
guarded('generation_conflict',()=>calendar_generation_current(generation),()=>guardConflict=true);
guarded('generation_forgotten',()=>calendar_generation_current(generation),()=>guardForgotten=true);
guarded('analysis_epoch',()=>boundary_analysis_current(),()=>mail_analysis_epoch=2);
guarded('analysis_dismissed',()=>boundary_analysis_current(),()=>mail_watch.alerts[0].status='dismissed');
guarded('auto_reply_version',()=>{calendar_links[0].status='verified';return boundary_auto_reply_current()},()=>calendar_links[0].version=3);
guarded('auto_reply_epoch',()=>{calendar_links[0].status='verified';return boundary_auto_reply_current()},()=>mail_analysis_epoch=2);
'''

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--sdk-contract',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a = p.parse_args()
    source = a.source.read_text()
    identity = json.loads((OWN/'model-input-identity.json').read_text())
    sha = lambda s:hashlib.sha256(s.encode()).hexdigest()
    assert sha(source)==identity['expected_source_sha256']
    sdk = a.sdk_contract.read_text()
    assert sha(sdk)==identity['sdk_contract_sha256']
    allowed = json.loads('['+re.search(r'!\[("task"[^\]]+)\]\.contains',sdk).group(1)+']')
    assert len(re.findall(r'\bmuse_model_request\(',source))==len(CALLERS)+1
    assert source.count('host.request("model.complete",')==1
    inventory = []
    cases = []
    inline = []
    for name in CALLERS:
        body = function(source,name)
        call = body.index('muse_model_request(')
        args = object_at(body,body.index('{',call))
        inventory.append(dict(caller=name,caller_sha256=sha(body),args_sha256=sha(args),args_source=args))
        projected_args = re.sub(r'([}\]])\s+(\w+:\s)',r'\1, \2',project_model(args))
        cases.append('{name:'+json.dumps(name)+',chat:'+str(name=='send_chat').lower()+',bound:'+str(name in ['ask_model','schedule_auto_reply','calendar_model_candidate']).lower()+',args:()=>('+projected_args+')}')
        if name in ['mail_analysis_pump','schedule_auto_reply']:
            expression = body[body.index('let current = ||')+len('let current = ||'):call]
            if name=='schedule_auto_reply': expression=expression[:expression.index('    mail_analysis_busy = true')]
            label='boundary_analysis_current' if name=='mail_analysis_pump' else 'boundary_auto_reply_current'
            inline.append(project_model('fn '+label+'(){ return '+expression.strip()+' }'))
            inventory[-1]['current_expression_source']=expression.strip()
    program = JS.replace(',gm_has=(v,k)=>gm_object(v)&&v[k]!=null','')
    program = program.replace('body=JSON.stringify(turns)', 'fixtureHistoryBody=JSON.stringify(turns)').replace('!body.includes(s)', '!fixtureHistoryBody.includes(s)')
    program = program.replace('__FUNCTIONS__','\n'.join(project_model(function(source,n)) for n in NAMES+GUARDS)+'\n'+'\n'.join(inline))
    program = program.replace('__ALLOWED__',json.dumps(allowed)).replace('__CHAT_INPUT__','messages:[]')
    program = program.replace('console.log(JSON.stringify(',EXTRA.replace('__CALL_CASES__','['+','.join(cases)+']')+'\nconsole.log(JSON.stringify(')
    run = subprocess.run([shutil.which('node') or 'node','-'],input=program,text=True,capture_output=True)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if run.returncode:
        a.out.with_suffix('.adapter-error.txt').write_text(run.stderr)
        raise RuntimeError(run.stderr)
    result=json.loads(run.stdout)
    result.update(source_sha256=sha(source),sdk_contract_sha256=sha(sdk),projected_functions=NAMES+GUARDS,
        call_inventory=inventory,official_parser_executed=False,full_caller_functions_executed=False,
        boundary='Six actual argument expressions and real current guards; argument variables, transport, retrieval and storage are synthetic. No VM, GUI, provider or external actions.',
        total=len(result['checks']),passed=sum(result['checks'].values()))
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','total','failed','external_calls']}))
    raise SystemExit(bool(result['failed']))

if __name__=='__main__':
    main()
