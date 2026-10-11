#!/usr/bin/env python3
"""Extracted Splash functions in Node fixture; no real VM, Host, GUI or network."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from test_recovery import function, apply, projection

OWN = Path(__file__).resolve().parent
NAMES = ['mail_add_account', 'mail_accounts_load', 'mail_watch_schedule', 'mail_watch_poll']
JS = r'''
Object.defineProperty(Object.prototype,'is_array',{value:function(){return Array.isArray(this)}});
Object.defineProperty(Object.prototype,'is_object',{value:function(){return this!==null && typeof this==='object' && !Array.isArray(this)}});
Object.defineProperty(String.prototype,'is_string',{value:function(){return true}});
Object.defineProperty(String.prototype,'parse_json',{value:function(){return JSON.parse(this)}});
function scenario(enabled,writable=true){
 let mail_watch={enabled},mail_watch_writable=writable,mail_pending=false,mail_notice='',mail_error='';
 let mail_accounts=[],mail_account={id:'selected-A'},authorized=[],mail_watch_timer=false,mail_watch_busy=false;
 let mail_watch_failed=false,mail_watch_completeness_unknown=false,mail_watch_history_pending=false,mail_watch_epoch=0,mail_watch_poll_accounts=[];
 let mail_watch_notice='',requests=[],timers=[],toggles=0,syncs=0,capability=true;
 const host={request:(method,args,callback)=>requests.push({method,args,callback})};
 const mail_enabled=()=>capability,mail_redraw=()=>{},mail_watch_refresh=()=>{},mail_analysis_pump=()=>{};
 const mail_host_error=error=>{mail_error=error};
 const gm_set_accounts=ids=>{authorized=ids};
 const mail_watch_toggle=()=>{toggles++;mail_watch.enabled=!mail_watch.enabled};
 const mail_watch_sync_account=()=>{syncs++};
 const start_timeout=(seconds,callback)=>timers.push({seconds,callback});
 __FUNCTIONS__
 return {login:mail_add_account,poll:mail_watch_poll,schedule:mail_watch_schedule,
  answer:(index,response)=>requests[index].callback(response),
  pause:()=>{mail_watch.enabled=false;mail_watch_epoch++;mail_watch_busy=false},
  select:()=>{mail_account={id:'selected-B'}},
  fire:()=>{const timer=timers.shift();if(timer.seconds!==30)throw Error('timer drift');timer.callback()},
  disable:()=>{capability=false},
  state:()=>({enabled:mail_watch.enabled,pending:mail_pending,toggles,requests:requests.map(r=>r.method),selected:mail_account.id,authorized,syncs,poll_accounts:mail_watch_poll_accounts,notice:mail_notice,error:mail_error})};
}
const checks={};const check=(name,ok)=>checks[name]=!!ok;
let c=scenario(false);c.login();c.answer(0,{is_ok:true});
check('persisted_pause_survives_success',!c.state().enabled && c.state().toggles===0);
check('success_still_refreshes_accounts',c.state().requests.join(',')==='mail.add_account,mail.accounts');
c.answer(1,{is_ok:true,data:[{id:'fresh-account'}]});
check('paused_account_refresh_completes',!c.state().pending && c.state().authorized[0]==='fresh-account');
c.schedule();c.fire();check('paused_timer_does_not_poll',c.state().requests.length===2 && !c.state().enabled);
c=scenario(true);c.login();c.pause();c.select();c.answer(0,{is_ok:true});
check('pause_while_login_pending_survives_late_success',!c.state().enabled && c.state().toggles===0);
check('account_selection_survives_late_login',c.state().selected==='selected-B');
c.answer(1,{is_ok:true,data:[{id:'fresh-account'}]});
check('late_account_refresh_does_not_resume',!c.state().enabled && c.state().selected==='selected-B');
c=scenario(true);c.login();c.answer(0,{is_ok:true});
check('first_connection_keeps_default_enabled',c.state().enabled && c.state().toggles===0);
check('no_eager_poll_while_account_refresh_pending',c.state().requests.length===2 && c.state().pending);
c.answer(1,{is_ok:true,data:[{id:'fresh-account'}]});c.schedule();c.fire();
check('existing_timer_polls_enabled_connection',c.state().requests[2]==='mail.accounts');
c.answer(2,{is_ok:true,data:[{id:'fresh-account'}]});
check('poll_uses_fresh_granted_accounts',c.state().syncs===1 && c.state().poll_accounts[0].id==='fresh-account');
c=scenario(true);c.schedule();c.fire();c.pause();c.answer(0,{is_ok:true,data:[{id:'stale-account'}]});
check('late_poll_response_after_pause_is_discarded',!c.state().enabled && c.state().syncs===0 && c.state().authorized.length===0);
for(const enabled of [false,true])for(const error of ['Sign-in cancelled.','fixture login failed']){
 c=scenario(enabled);c.login();c.answer(0,{is_ok:false,error});
 check((enabled?'enabled':'paused')+'_'+error,c.state().enabled===enabled && !c.state().pending && c.state().toggles===0 && c.state().requests.length===1 && c.state().error===error);
}
c=scenario(false,false);c.login();c.answer(0,{is_ok:true});
check('read_only_pause_not_toggled',!c.state().enabled && c.state().toggles===0);
c=scenario(true);c.login();c.login();check('pending_login_not_duplicated',c.state().requests.length===1);
c=scenario(true);c.disable();c.login();check('missing_capability_still_blocks_login',c.state().requests.length===0);
console.log(JSON.stringify({checks,failed:Object.keys(checks).filter(k=>!checks[k]),external_calls:0,
 boundary:'Four actual Splash functions projected to Node. Host, UI, pause, persistence and analysis are fixture adapters. Not actual Splash VM/Host proof.'}));
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--phase', choices=['before','after'], required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    identity = json.loads((OWN/'watch-pause-identity.json').read_text())
    source = a.source.read_text()
    sha = lambda text: hashlib.sha256(text.encode()).hexdigest()
    assert sha(source) == identity['source_sha256'], 'Source SHA differs from proposal base'
    if a.phase == 'after':
        patched = apply(source, (OWN/'watch-pause.patch').read_text())
        assert sha(patched) == identity['expected_source_sha256']
        assert function(source,'mail_add_account').replace('            // A completed connection starts reminders; opening the mailbox alone preserves an explicit pause.\n            if mail_watch_writable && !mail_watch.enabled { mail_watch_toggle() }\n','') == function(patched,'mail_add_account')
        for name in NAMES[1:]: assert function(source,name) == function(patched,name)
        source = patched
    funcs = []
    for name in NAMES:
        code = projection(function(source,name)).replace('fn(r)', 'function(r)')
        # Additional exact closed-subset statement boundaries, not a general compiler.
        code = re.sub(r'("(?:[^"\\]|\\.)*") (mail_\w+\()',r'\1; \2',code)
        code = code.replace('mail_accounts = [] mail_watch_poll_accounts', 'mail_accounts = []; mail_watch_poll_accounts')
        code = code.replace('gm_set_accounts([]) mail_notice', 'gm_set_accounts([]); mail_notice')
        code = code.replace('mail_host_error(r.error) mail_redraw()', 'mail_host_error(r.error); mail_redraw()')
        funcs.append(code)
    program = JS.replace('__FUNCTIONS__','\n'.join(funcs))
    node = shutil.which('node')
    assert node, 'Node fixture runtime unavailable'
    executed = subprocess.run([node],input=program,text=True,capture_output=True)
    assert executed.returncode == 0, executed.stderr
    report = json.loads(executed.stdout)
    report.update(phase=a.phase,source_sha256=sha(source),patch_sha256=identity['patch_sha256'],
                  projected_functions=NAMES,total=len(report['checks']),passed=sum(report['checks'].values()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['phase','passed','total','failed','external_calls']},ensure_ascii=False))
    raise SystemExit(bool(report['failed']))


if __name__ == '__main__':
    main()
