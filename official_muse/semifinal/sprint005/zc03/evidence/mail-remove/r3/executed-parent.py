#!/usr/bin/env python3
"""Existing real ScriptVM; frozen mailbox UI functions, synthetic deferred transport."""
import argparse,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--vm',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 raw=a.source.read_bytes();source=raw.decode();(out/'frozen-main.splash').write_bytes(raw)
 s=importlib.util.spec_from_file_location('parser',H.parents[3]/'official_muse/prelim/tests/calendar_sync/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);f=m.functions_in(source)
 cancel=re.search(r'Secondary\{text: "取消" on_click: \|\| \{ (mail_remove_confirm = "" mail_redraw\(\)) \}\}',source).group(1)
 rows=[]
 def add(name,mode='remove',expect='remove',**kw):rows.append(dict(name=name,mode=mode,expect=expect,**kw))
 add('remove-selected-A-clears-only-view')
 add('remove-A-preserves-selected-B',selected='B')
 add('async-switch-to-B-preserved',switch='B')
 add('async-switch-to-nil-preserved',switch='nil')
 add('cancel-prevents-dispatch',mode='cancel',expect='blocked')
 add('no-confirmation',expect='blocked',confirm='')
 add('wrong-confirmation',expect='blocked',confirm='B')
 add('unknown-account',expect='blocked',target='missing')
 for flag in ['pending','sending','model_pending','calendar_link_pending']:add('guard-'+flag,expect='blocked',flag=flag)
 add('no-mail-capability',expect='blocked',cap=False)
 for status in ['sending','accepted','unknown']:add('same-draft-'+status,expect='blocked',draft_status=status)
 add('other-account-accepted-not-blocking',draft_account='B',draft_status='accepted')
 add('failed-remove-keeps-current-view',expect='failure',reply=dict(is_ok=False,error='cancelled by fixture'))
 add('failed-remove-after-switch-B',expect='failure',switch='B',reply=dict(is_ok=False,error='timeout fixture'))
 add('accounts-reload-fails-after-remove',expect='reload-fail',reload_ok=False)
 add('add-second-account',mode='add',expect='add')
 add('add-cancelled-login',mode='add',expect='add-failure',reply=dict(is_ok=False,error='cancelled login'))
 add('add-pending-blocked',mode='add',expect='blocked',flag='pending')
 add('add-capability-blocked',mode='add',expect='blocked',cap=False)
 defs=['mail_enabled','mail_host_error','mail_accounts_load','mail_remove_account','mail_add_account']
 code='''use mod.math.*
use mod.std.*
let fixture_caps=["mail"] let fixture_trace=[] let fixture_pending=[] let fixture_grants=[]
let host={capabilities:||fixture_caps}
let mail_pending=false let mail_sending=false let mail_model_pending=false let mail_calendar_link_pending=false
let mail_accounts=[] let mail_account=nil let mail_remove_confirm="" let mail_draft={}
let mail_selected=nil let mail_messages=[] let mail_folders_data=[] let mail_folder="INBOX"
let mail_total=0 let mail_offset=0 let mail_connection_verified=false let mail_compose_open=false
let mail_error="" let mail_notice="" let mail_error_detail_open=false let mail_error_detail="" let mail_error_detail_user=""
fn mail_redraw(){}
fn gm_set_accounts(ids){fixture_grants=ids}
fn fixture_transport(method,args,cb){fixture_trace.push({method:method args:args}) fixture_pending.push({method:method callback:cb})}
'''
 code+='\n'.join(f[n].replace('host.request(','fixture_transport(') for n in defs)+'\nfn fixture_cancel(){'+cancel+'}\n'
 probe='''
let rows=__ROWS__.parse_json() let results=[]
for row in rows {
 fixture_caps=["mail"] if row["cap"]==false {fixture_caps=[]}
 fixture_trace=[] fixture_pending=[] fixture_grants=["A","B"]
 mail_pending=false mail_sending=false mail_model_pending=false mail_calendar_link_pending=false
 if row["flag"]=="pending" {mail_pending=true}
 if row["flag"]=="sending" {mail_sending=true}
 if row["flag"]=="model_pending" {mail_model_pending=true}
 if row["flag"]=="calendar_link_pending" {mail_calendar_link_pending=true}
 mail_accounts=[{id:"A" address:"a@fixture.invalid"},{id:"B" address:"b@fixture.invalid"}]
 if row.mode=="add" {mail_accounts=[{id:"A" address:"a@fixture.invalid"}]}
 mail_account=mail_accounts[0] if row["selected"]=="B" {mail_account=mail_accounts[1]}
 mail_remove_confirm="A" if row["confirm"]!=nil {mail_remove_confirm=row.confirm}
 mail_draft={account:"A" status:"DRAFT" body:"historical draft keep"}
 if row["draft_account"]!=nil {mail_draft.account=row.draft_account}
 if row["draft_status"]!=nil {mail_draft.status=row.draft_status}
 mail_selected={id:"old-message"} mail_messages=[{id:"old-message"}] mail_folders_data=[{id:"old-folder"}]
 mail_folder="old-folder" mail_total=9 mail_offset=25 mail_connection_verified=true mail_compose_open=true
 mail_error="" mail_notice=""
 let draft_before=mail_draft.to_json() let target="A" if row["target"]!=nil {target=row.target}
 if row.mode=="cancel" {fixture_cancel() mail_remove_account(target)}
 else if row.mode=="add" {mail_add_account()}
 else {mail_remove_account(target)}
 let queued=fixture_pending.len()
 let pending_before_reply=mail_pending
 if row["switch"]=="B" {mail_account=mail_accounts[1] mail_selected={id:"B-message"} mail_messages=[{id:"B-message"}] mail_folders_data=[{id:"B-folder"}] mail_folder="B-folder"}
 if row["switch"]=="nil" {mail_account=nil}
 let choice_before_reply=mail_account.to_json() let list_before_reply=mail_messages.to_json()
 let index=0
 while index<fixture_pending.len() && index<3 {
  let item=fixture_pending[index] index=index+1
  let reply={is_ok:true data:nil}
  if item.method=="mail.accounts" {
   if row.mode=="add" {reply={is_ok:true data:[{id:"A"},{id:"B"}]}}
   else {reply={is_ok:true data:[{id:"B"}]}}
   if row["reload_ok"]==false {reply={is_ok:false error:"fixture reload failed"}}
  } else if row["reply"]!=nil {reply=row.reply}
  item.callback(reply)
 }
 results.push({name:row.name trace:fixture_trace pending_before_reply:pending_before_reply queued:queued pending:mail_pending
  account:mail_account choice_before_reply:choice_before_reply messages:mail_messages list_before_reply:list_before_reply
  selected:mail_selected folders:mail_folders_data folder:mail_folder total:mail_total offset:mail_offset connection:mail_connection_verified compose:mail_compose_open
  accounts:mail_accounts grants:fixture_grants confirm:mail_remove_confirm error:mail_error notice:mail_notice draft_unchanged:draft_before==mail_draft.to_json()})
}
results.to_json()
'''.replace('__ROWS__',json.dumps(json.dumps(rows,ensure_ascii=False),ensure_ascii=False))
 code+=probe;(out/'executed.splash').write_text(code);(out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
 ident=dict(source_sha256=SHA(raw),vm_sha256=SHA(a.vm.read_bytes()),runner_sha256=SHA(Path(__file__).read_bytes()),executed_sha256=SHA(code.encode()),production_functions={n:SHA(f[n].encode()) for n in defs},cancel_ui_body=cancel,cancel_ui_body_sha256=SHA(cancel.encode()),transport_only_normalization=True,fixture_boundaries=['host.capabilities','deferred transport replies','mail_redraw','gm_set_accounts'])
 (out/'identity.json').write_text(json.dumps(ident,indent=2)+'\n');(out/'parent-command.json').write_text(json.dumps([sys.executable,*sys.argv],indent=2)+'\n');cmd=[str(a.vm.resolve()),str(out/'executed.splash'),'--rpc'];(out/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
 proc=subprocess.run(cmd,text=True,capture_output=True,timeout=30);(out/'stdout.log').write_text(proc.stdout);(out/'stderr.log').write_text(proc.stderr)
 report=dict(status='ERROR',returncode=proc.returncode,identity=ident,boundary='Actual pure CLI Splash VM, synthetic account A/B/C and deferred transport. No GUI, actual account creation/removal, credentials, real mailbox or business storage tested.')
 if proc.returncode==0 and not proc.stderr:
  actual=json.loads(proc.stdout.removeprefix('MUSE_VM_RESULT ').strip());failed=[];assert len(actual)==len(rows)
  for row,r in zip(rows,actual):
   mode=row['expect'];services=[t['method'] for t in r['trace']];checks=dict(name=row['name']==r['name'],draft_preserved=r['draft_unchanged'])
   if mode=='blocked':checks['zero_dispatch']=services==[];checks['accounts_retained']=[a['id'] for a in r['accounts']]==(['A'] if row['mode']=='add' else ['A','B'])
   elif mode in ['failure','add-failure']:checks['single_failed_dispatch']=services==['mail.remove_account' if mode=='failure' else 'mail.add_account'];checks['error']=bool(r['error']);checks['selection_retained']=r['account']==json.loads(r['choice_before_reply']);checks['pending_cleared']=r['pending'] is False
   elif mode in ['remove','reload-fail','add']:
    checks['exact_service_order']=services==['mail.add_account' if mode=='add' else 'mail.remove_account','mail.accounts'];checks['pending_cleared']=r['pending'] is False
    if mode!='add':checks['exact_target']=r['trace'][0]['args']==dict(account=row.get('target','A'))
    if mode=='remove':checks['other_account_retained']=[a['id'] for a in r['accounts']]==['B'] and r['grants']==['B']
    if mode=='add':checks['second_account_list']=[a['id'] for a in r['accounts']]==['A','B'] and r['grants']==['A','B']
    if mode=='reload-fail':checks['reload_error']=bool(r['error']) and r['grants']==[]
    if row.get('switch')=='B' or row.get('selected')=='B':checks['other_selection_preserved']=r['account']['id']=='B' and r['messages']!=[] and r['selected'] is not None
    elif row.get('switch')=='nil':checks['nil_choice_preserved']=r['account'] is None and r['messages']==json.loads(r['list_before_reply'])
    elif mode!='add':checks['removed_selection_cleared']=r['account'] is None and r['messages']==[] and r['selected'] is None and r['folders']==[] and r['folder']=='INBOX' and r['total']==0 and r['offset']==0 and r['connection'] is False and r['compose'] is False
   if mode!='blocked':checks['pending_during_async']=r['queued']==1 and r['pending_before_reply'] is True
   r['checks']=checks
   if not all(checks.values()):failed.append(dict(name=row['name'],checks=[k for k,v in checks.items() if not v]))
  report.update(status='FIXTURE_PASS' if not failed else 'FAIL',failed=failed,cases=len(rows),actual=actual)
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report.get(k) for k in ['status','cases','failed','returncode']},ensure_ascii=False))
 return 0 if report['status']=='FIXTURE_PASS' else 1
if __name__=='__main__':raise SystemExit(main())
