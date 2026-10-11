#!/usr/bin/env python3
"""Source-bound ASCII decision fixture, Node projection; NOT a Splash VM/Host test."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

OWN=Path(__file__).resolve().parent
ROOT=OWN.parents[3]

def function(source,name):
    start=source.index('fn '+name+'('); brace=source.index('{',start)
    pos=brace+1; depth=1; quoted=False; escaped=False
    while depth:
        c=source[pos]
        if quoted:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='{': depth+=1
        elif c=='}': depth-=1
        pos+=1
    return source[start:pos]

def apply(source,patch):
    lines=source.splitlines(True); out=[];pos=0
    for line in patch.splitlines(True)[2:]:
        if line.startswith('@@'):
            hunk=re.match(r'@@ -(\d+)(?:,(\d+))?',line)
            target=int(hunk.group(1))-(0 if hunk.group(2)=='0' else 1)
            out.extend(lines[pos:target]);pos=target
        elif line.startswith(' '): assert lines[pos]==line[1:];out.append(lines[pos]);pos+=1
        elif line.startswith('-'): assert lines[pos]==line[1:];pos+=1
        elif line.startswith('+'): out.append(line[1:])
    out.extend(lines[pos:]);return ''.join(out)

def projection(fn):
    # Closed subset used by these 3 functions. No general VM or syntax claim.
    fn=re.sub(r'^fn ', 'function ',fn)
    fn=fn.replace('.len()', '.length').replace('nil','null')
    fn=re.sub(r',\|\|\s*', ',()=> ',fn)
    fn=fn.replace(') return','); return')
    fn=re.sub(r'("(?:[^"\\]|\\.)*") let ',r'\1; let ',fn)
    fn=re.sub(r'(true|false|"(?:[^"\\]|\\.)*") (\w+(?:\.\w+)*\s*=|return )',r'\1; \2',fn)
    fn=re.sub(r'([\w.]+)\.to_json\(\)',r'JSON.stringify(\1)',fn).replace('.search(','.indexOf(')
    fn=re.sub(r'for (\w+) in ([\w.]+) \{',r'for (const \1 of \2) {',fn)
    fn=re.sub(r'("(?:[^"\\]|\\.)*") return ',r'\1; return ',fn)
    fn=fn.replace('document: document pinned: false source_history: document.payload.source_ids\n        memory_type: "source" conversation_id: "" history: []',
                  'document: document, pinned: false, source_history: document.payload.source_ids,\n        memory_type: "source", conversation_id: "", history: []')
    # All if expressions in this closed subset have no object literal.
    fn=re.sub(r'\bif ([^{}]+)\{',lambda m:'if ('+m.group(1).strip()+') {',fn)
    return fn

JS=r'''
const fs=require('fs'), assert=require('assert');
const checks={}; function check(name,value){checks[name]=!!value}
const gm_object=v=>v!==null && typeof v==='object' && !Array.isArray(v);
const gm_array=Array.isArray;
const gm_string=(v,cap)=>typeof v==='string' && v.length<=cap;
const gm_account_allowed=v=>v==='synthetic-account';
const gm_same_scope=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const core_hash_valid=v=>typeof v==='string' && /^[a-f0-9]{64}$/.test(v);
let core_error='',memory=[],memory_sources=[],memory_forget=[],commits=0;
let failAt=2;
const scope={project:'muse-goals',account:'synthetic-account',visibility:'personal',project_id:'fixture-project',owner_id:'fixture-owner'};
const core_source_index=(id,account)=>memory_sources.findIndex(s=>s.source_id===id && s.scope.account===account);
const core_memory_index=(id,account)=>memory.findIndex(s=>s.document.id===id && s.document.scope.account===account);
const core_is_forgotten=()=>memory_forget.length>0;
let mail_draft,mail_sending,mail_error='',mail_notice='',actionStatus,runStatus,events=[];
const mail_save=()=>{fs.writeFileSync(process.argv[2]+'.draft',JSON.stringify(mail_draft));return true};
const core_finish_action=(id,status)=>{actionStatus=status;return true};
const core_finish_run=(goal,run,status)=>{runStatus=status;return true};
const core_record_event=(kind)=>{events.push(kind);return true};
const mail_redraw=()=>{};
const time_now=()=>1791686400;
const start_timeout=(_,callback)=>callback();
function core_commit_memory(claims,sources,forget){
 commits++;
 if(commits===failAt){core_error='synthetic claim commit interruption';return false}
 const serialized=JSON.stringify({claims,sources,forget});
 fs.writeFileSync(process.argv[2],serialized);
 const readback=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 memory=readback.claims;memory_sources=readback.sources;memory_forget=readback.forget;return true;
}
__FUNCTIONS__
const source={source_id:'source:mail:synthetic-account:message-1',kind:'runtime_receipt',locator:'mail:synthetic-account:message-1',content_sha256:'a'.repeat(64),observed_at:'2026-10-11T00:00:00Z',updated_at:'2026-10-11T00:00:00Z',scope,support_excerpt:'Synthetic mail'};
const doc={schema_version:'muse.dsl/1',kind:'memory',id:'memory:mail:synthetic-account:message-1',revision:1,scope,created_at:'2026-10-11T00:00:00Z',updated_at:'2026-10-11T00:00:00Z',origin:{type:'local_runtime',ref:'mail-host'},payload:{subject_id:'mail:synthetic-account:message-1',predicate:'message_content',value:'Synthetic content',epistemic_type:'external_claim',source_ids:[source.source_id],observed_at:'2026-10-11T00:00:00Z',relations:[],deleted:false}};
check('source_first_commit',core_add_source(source));
check('claim_failure_injected',!core_add_claim(doc));
check('disk_has_only_source_after_interruption',memory_sources.length===1 && memory.length===0);
({claims:memory,sources:memory_sources,forget:memory_forget}=JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
check('restart_source_reused',core_add_source({...source,observed_at:'2026-10-11T00:01:00Z'}));
check('source_retry_no_extra_commit',commits===2);
check('claim_retry_recovers',core_add_claim(doc));
check('exactly_one_source_one_claim',memory_sources.length===1 && memory.length===1);
check('same_claim_not_duplicated',!core_add_claim(doc) && memory.length===1);
check('changed_source_refused',!core_add_source({...source,content_sha256:'b'.repeat(64)}));
check('cross_scope_source_refused',!core_add_source({...source,scope:{...scope,owner_id:'different-owner'}}));
const committed=fs.readFileSync(process.argv[2],'utf8');
check('rejection_preserves_disk',committed===JSON.stringify({claims:memory,sources:memory_sources,forget:memory_forget}));
const payload={to:'self@example.invalid',subject:'Synthetic status',body:'No live delivery'};
const draft=(status,receipt=null)=>({...payload,status,revision:1,attempts:[{status,revision:1,operation_id:'fixture-operation',payload:{...payload},receipt}]});
const decide=__DECIDE__;
check('before_delivery_reconciles_unsent',decide(draft('failed_before_delivery'))==='failed_before_delivery');
if(__AFTER__){
 check('accepted_receipt',decide(draft('accepted',{accepted:true}))==='accepted');
 check('accepted_without_receipt_stays_unknown',decide(draft('accepted'))==='unknown');
 for(const status of ['draft','cancelled','awaiting_approval','sending','outcome_unknown'])check(status+'_not_terminal',decide(draft(status))==='unknown');
 const stale=draft('failed_before_delivery');stale.attempts[0].revision=2;
 check('stale_revision_not_reconciled',decide(stale)==='unknown');
 const wrong=draft('failed_before_delivery');wrong.attempts[0].payload.body='Different';
 check('wrong_payload_not_reconciled',decide(wrong)==='unknown');
 check('contradictory_receipt_not_unsent',decide(draft('failed_before_delivery',{accepted:true}))==='unknown');
 check('missing_attempt_not_reconciled',decide({...draft('failed_before_delivery'),attempts:[]})==='unknown');
 check('nonobject_not_reconciled',decide(null)==='unknown');
}
function receiptCase(label,accepted,unsent){
 mail_draft={request_id:'fixture-request',status:'unknown',to:payload.to,subject:payload.subject,body:payload.body,host_compose_id:'compose-fixture',host_revision:1,attempt:'synthetic-bound-payload',preview:'synthetic-preview'};
 mail_sending=true;actionStatus='unknown';runStatus='running';events=[];
 mail_send_receipt_step({request_id:'fixture-request',goal_id:'fixture-goal',run_id:'fixture-run',snapshot:{account:'synthetic-account'},accepted,unsent,notice:'synthetic-unsent'},0);
 check(label+'_body_and_host_identity_preserved',mail_draft.body===payload.body && mail_draft.host_compose_id==='compose-fixture' && mail_draft.host_revision===1);
 check(label+'_action_result',actionStatus===(accepted?'accepted':unsent?'failed':'unknown'));
 check(label+'_run_not_falsely_verified',runStatus===(unsent?'failed':'running'));
 check(label+'_draft_result',mail_draft.status===(accepted?'accepted':unsent?'DRAFT':'unknown'));
 check(label+'_saved_readback',JSON.parse(fs.readFileSync(process.argv[2]+'.draft','utf8')).status===mail_draft.status);
}
receiptCase('cancel',false,true);
receiptCase('unknown',false,false);
receiptCase('accepted_not_received',true,false);
if(__AFTER__)receiptCase('authoritative_before_delivery',false,true);
console.log(JSON.stringify({checks,failed:Object.keys(checks).filter(k=>!checks[k]),memory:{sources:memory_sources.length,claims:memory.length,commit_calls:commits},external_service_calls:0,boundary:'Extracted production functions projected into Node for synthetic ASCII decisions. Validation intrinsics/persistence fault are fixture adapters; not official Splash VM or Host.'}));
'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['before','after'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    src=ROOT/'official_muse/app/source/main.splash';original=src.read_text();source=original
    identity=json.loads((OWN/'patch_identity.json').read_text())
    assert hashlib.sha256(src.read_bytes()).hexdigest()==identity['source_sha256']
    if a.phase=='after':
        source=apply(source,(OWN/'mail-terminal-recovery.patch').read_text())
        assert hashlib.sha256(source.encode()).hexdigest()==identity['expected_source_sha256']
    assert a.out.resolve().is_relative_to(OWN.resolve()) and not a.out.exists()
    a.out.mkdir(parents=True)
    names=['core_add_source','core_add_claim','mail_send_receipt_step']
    if a.phase=='after':names.append('mail_host_receipt_status')
    functions='\n'.join(projection(function(source,name)) for name in names)
    # Before behavior comes directly from the actual callback's terminal guard.
    callback=function(original,'mail_check_host_status')
    guard=re.search(r'if (r\.data\["status"\] != "accepted") \{',callback)
    assert guard
    decide='mail_host_receipt_status' if a.phase=='after' else '(data)=>('+guard.group(1).replace('r.data','data')+' ? "unknown" : "accepted")'
    js=JS.replace('__FUNCTIONS__',functions).replace('__DECIDE__',decide).replace('__AFTER__','true' if a.phase=='after' else 'false')
    node=shutil.which('node');assert node,'Node unavailable'
    with tempfile.TemporaryDirectory(prefix='muse-mail-fixture-') as tmp:
        test=Path(tmp)/'fixture.js';test.write_text(js)
        run=subprocess.run([node,str(test),str(Path(tmp)/'memory.json')],capture_output=True,text=True,timeout=15)
    (a.out/'stdout.txt').write_text(run.stdout);(a.out/'stderr.txt').write_text(run.stderr)
    if run.returncode:raise RuntimeError('Fixture execution error; stderr retained')
    report=json.loads(run.stdout);report.update(phase=a.phase,source_sha256=hashlib.sha256(source.encode()).hexdigest(),status='FAIL' if report['failed'] else 'PASS_SOURCE_DECISION_FIXTURE')
    (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False));return 1 if report['failed'] else 0
if __name__=='__main__':raise SystemExit(main())
