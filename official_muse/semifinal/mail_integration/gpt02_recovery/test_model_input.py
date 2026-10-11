#!/usr/bin/env python3
"""Directed Node projection of production wrapper; no Splash VM/model/Host."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
from test_recovery import function, apply
from test_calendar_chain import project

OWN = Path(__file__).resolve().parent
NAMES = ['muse_model_request', 'chat_model_history', 'chat_history_scope_current', 'chat_reply_is_context']

def project_model(text):
    text = text.replace('chat_reply_context_valid({memory_refs: captured_refs})', 'fixture_refs_valid(captured_refs)')
    text = project(text)
    # Observed adjacent statements only; this is not an OctoScript compiler.
    text = text.replace(') return', '); return')
    text = re.sub(r'for (\w+) in ([\w.]+)\.length \{', r'for (const \1 of range(\2.length)) {', text)
    text = text.replace('project = args.input.project_id owner =', 'project = args.input.project_id; owner =')
    text = text.replace('project = goals[bound_goal].project_id owner =', 'project = goals[bound_goal].project_id; owner =')
    text = text.replace('gm_set_accounts(ids) gm_set_focus', 'gm_set_accounts(ids); gm_set_focus')
    text = text.replace('gm_set_focus(saved_project,saved_owner) return', 'gm_set_focus(saved_project,saved_owner); return')
    text = text.replace('first_recent = i pairs.push', 'first_recent = i; pairs.push')
    text = text.replace('statements.push(statement) bytes =', 'statements.push(statement); bytes =')
    text = text.replace('turns.push({role: "user", content: pair.user}) turns.push', 'turns.push({role: "user", content: pair.user}); turns.push')
    return text

JS = r'''
const crypto=require('crypto'),checks={},clone=v=>JSON.parse(JSON.stringify(v));
Object.defineProperty(Object.prototype,'to_json',{value:function(){return JSON.stringify(this)}});
Object.defineProperty(String.prototype,'parse_json',{value:function(){return JSON.parse(this)}});
const gm_object=v=>v!=null&&typeof v==='object'&&!Array.isArray(v),gm_has=(v,k)=>gm_object(v)&&v[k]!=null;
const range=n=>Array.from({length:n},(_,i)=>i),min=Math.min;
const time_now=()=>1791686400,core_utc_iso=()=> '2026-10-11T00:00:00Z';
const fs={sha256:s=>crypto.createHash('sha256').update(s).digest('hex')};
let gm_project,gm_owner,gm_accounts,gm_user_id,gm_enabled,core_last_memory,memory,goals,chat_sessions,chat_requests;
let queued,requests,replies,traces,context,refsValid,current;
const gm_set_focus=(p,o)=>{gm_project=p;gm_owner=o},gm_set_accounts=a=>gm_accounts=clone(a);
const gm_account_allowed=a=>gm_accounts.includes(a),core_goal_index=id=>goals.findIndex(g=>g.id===id);
const gm_context_ranked=()=>context,chat_context_refs=hits=>clone(hits),chat_reply_context_valid=r=>refsValid&&r.invalid!==true;
const fixture_refs_valid=refs=>chat_reply_context_valid({memory_refs:refs});
const gm_retired_text=t=>t==='forgotten',chat_task_focus=()=> '\n当前会话相关任务资料：合成待核对事项';
const chat_session_index=id=>chat_sessions.findIndex(s=>s.id===id),chat_request_index=()=>0;
const gm_entry_field=(e,k,f)=>e[k]||f,gm_score=()=>1,mail_enabled=()=>true;
const start_timeout=(s,cb)=>queued.push(cb),storage_write=(name,text)=>traces.push(JSON.parse(text));
const model_error_code=s=>s.split(':')[0];
const allowed=__ALLOWED__;
const host={request:(method,args,cb)=>{
 if(method==='mail.accounts'){cb({is_ok:true,data:[{id:'account-A'}]});return}
 requests.push({method,args:clone(args),cb});
}};
__FUNCTIONS__
const check=(name,value)=>checks[name]=!!value;
function reset(){
 gm_project='project-A';gm_owner='owner-A';gm_accounts=['account-A'];gm_user_id='user-A';gm_enabled=true;core_last_memory='memory-v1';
 memory=[];goals=[];chat_requests=[{}];queued=[];requests=[];replies=[];traces=[];refsValid=true;current=true;
 context={hits:[{id:'memory-A',revision:1,source_ids:['source-A']}],text:'相关记忆：合成偏好',requires_resolution:false};
 const msg=(role,text,state='success',project=gm_project)=>({role,text,state,project,owner:gm_owner,at:1});
 chat_sessions=[{id:'chat-A',messages:[msg('user','older-original'),msg('assistant','older-answer'),
  msg('user','failed-user'),msg('assistant','failed-answer','error'),
  msg('user','other-project','success','project-B'),msg('assistant','other-answer','success','project-B'),
  msg('user','forgotten'),msg('assistant','forgotten-answer'),
  msg('user','history-1'),msg('assistant','answer-1'),msg('user','history-2'),msg('assistant','answer-2'),
  msg('user','history-3'),msg('assistant','answer-3'),msg('user','current-question')]}];
}
const schema={type:'object',properties:{reply:{type:'string'}},required:['reply'],additionalProperties:false};
function argsForChat(){return {task:'Answer the current question using conversation data.',__CHAT_INPUT__,schema:clone(schema),class:'strong',allow_urls:true}}
function dispatch(args=argsForChat()){muse_model_request('current-question','chat-A','',()=>current,args,r=>replies.push(r))}
const flush=()=>{while(queued.length)queued.shift()()};
const response={is_ok:true,data:{output:{reply:'synthetic'},meta:{class:'strong',requested:'strong',attempts:1,usage:{input_tokens:23,output_tokens:5,estimated:false},budget:{remaining:99}}}};
reset();const original=argsForChat(),before=JSON.stringify(original);dispatch(original);flush();const wire=requests[0].args;
check('official_top_level_keys',Object.keys(wire).every(k=>allowed.includes(k)));
check('chat_history_is_inside_input',wire.input!=null&&Array.isArray(wire.input.messages)&&!Object.hasOwn(wire,'messages'));
const turns=wire.input?.messages||wire.messages,body=JSON.stringify(turns);
check('history_order_and_assistant_reply_format',turns[0].content==='history-1'&&turns[1].content===JSON.stringify({reply:'answer-1'})&&turns[4].content==='history-3');
check('current_query_memory_task_and_earlier_context_preserved',turns.at(-1).role==='user'&&['current-question','相关记忆：合成偏好','合成待核对事项','older-original'].every(s=>turns.at(-1).content.includes(s)));
check('failed_cross_scope_and_forgotten_history_excluded',['failed-user','failed-answer','other-project','other-answer','forgotten-answer'].every(s=>!body.includes(s)));
check('schema_class_url_policy_preserved',JSON.stringify(wire.schema)===JSON.stringify(schema)&&wire.class==='strong'&&wire.allow_urls===true);
check('clock_and_task_preserved',wire.task.startsWith(original.task)&&wire.task.includes('2026-10-11T00:00:00Z'));
check('caller_arguments_not_mutated',JSON.stringify(original)===before);
check('input_below_official_byte_limit',Buffer.byteLength(JSON.stringify(wire.input??null))<=32768);
requests[0].cb(clone(response));check('usage_metadata_preserved',traces[0].known_usage&&JSON.stringify(traces[0].meta)===JSON.stringify(response.data.meta));
check('captured_refs_preserved',JSON.stringify(replies[0].memory_refs)===JSON.stringify(context.hits)&&JSON.stringify(chat_requests[0].memory_refs)===JSON.stringify(context.hits));
reset();dispatch({task:'Extract calendar candidate',__CHAT_INPUT__,schema:{type:'object',properties:{title:{type:'string'}}},class:'fast'});flush();
const candidate=requests[0].args,ct=candidate.input?.messages||candidate.messages;
check('structured_candidate_history_preserved',ct[1].content==='answer-1'&&candidate.class==='fast'&&!Object.hasOwn(candidate,'allow_urls'));
reset();const ordinary={task:'Extract',input:{project_id:'project-A',owner_id:'owner-A',source_account:'account-A',source:'synthetic-source'},schema:clone(schema),class:'fast',allow_urls:false};dispatch(ordinary);flush();
check('ordinary_nonchat_input_unchanged',JSON.stringify(requests[0].args.input.current)===JSON.stringify(ordinary.input)&&requests[0].args.input.related_memory===context.text&&requests[0].args.allow_urls===false);
const changes={user:()=>gm_user_id='user-B',accounts:()=>gm_accounts=[],enabled:()=>gm_enabled=false,current:()=>current=false,memory:()=>core_last_memory='memory-v2',project:()=>gm_project='project-B',owner:()=>gm_owner='owner-B'};
for(const [name,change] of Object.entries(changes)){reset();dispatch();change();flush();check('before_dispatch_'+name+'_guard',requests.length===0&&replies.length===1&&!replies[0].is_ok)}
for(const name of ['user','accounts','enabled','current']){reset();dispatch();flush();changes[name]();requests[0].cb(clone(response));check('late_'+name+'_guard',!replies[0].is_ok&&replies[0].error.startsWith('cancelled:'))}
reset();dispatch();flush();refsValid=false;requests[0].cb(clone(response));check('late_memory_refs_guard',!replies[0].is_ok&&replies[0].error.startsWith('memory_conflict:'));
reset();context.requires_resolution=true;dispatch();flush();check('memory_conflict_blocks_transport',requests.length===0&&!replies[0].is_ok);
console.log(JSON.stringify({kind:'SOURCE_BOUND_NODE_PROJECTION_FIXTURE',checks,failed:Object.keys(checks).filter(k=>!checks[k]),external_calls:0}));
'''

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--sdk-contract', type=Path, required=True)
    p.add_argument('--phase', choices=['before','after'], required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    source = a.source.read_text()
    identity = json.loads((OWN/'model-input-identity.json').read_text())
    assert hashlib.sha256(source.encode()).hexdigest() == identity['source_sha256']
    sdk = a.sdk_contract.read_text()
    assert hashlib.sha256(sdk.encode()).hexdigest() == identity['sdk_contract_sha256']
    allowed = re.search(r'!\[("task"[^\]]+)\]\.contains', sdk).group(1)
    allowed = json.loads('['+allowed+']')
    if a.phase == 'after':
        source = apply(source, (OWN/'model-input.patch').read_text())
        assert hashlib.sha256(source.encode()).hexdigest() == identity['expected_source_sha256']
    program = JS.replace('__FUNCTIONS__','\n'.join(project_model(function(source,n)) for n in NAMES))
    program = program.replace('__ALLOWED__',json.dumps(allowed))
    program = program.replace('__CHAT_INPUT__','messages:[]')
    run = subprocess.run([shutil.which('node') or 'node','-'],input=program,text=True,capture_output=True)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if run.returncode:
        a.out.with_suffix('.adapter-error.txt').write_text(run.stderr)
        raise RuntimeError(run.stderr)
    result = json.loads(run.stdout)
    result.update(phase=a.phase,source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        sdk_contract_sha256=identity['sdk_contract_sha256'],projected_functions=NAMES,
        official_parser_executed=False,total=len(result['checks']),passed=sum(result['checks'].values()))
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['phase','passed','total','failed','external_calls']}))
    raise SystemExit(bool(result['failed']))

if __name__ == '__main__':
    main()
