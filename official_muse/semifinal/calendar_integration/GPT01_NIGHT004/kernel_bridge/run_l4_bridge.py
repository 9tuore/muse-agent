#!/usr/bin/env python3
"""Root-only execution: actual signed candidate/Broker/Kernel bridge L4.

No VM result injection, service imitation, automatic write retry or secret lookup.
"""
import argparse,hashlib,json,queue,subprocess,threading,time,uuid
from pathlib import Path

MAIN_SHA='643009fed5065fd0cb43c2b2210c175cd162f31a9eb6bf5f67004f8f504223dc'
SOURCE_SHA='0426f4db13d86b577166b334c4686668c81cf8c7fa62d0f05e44e43c54eee1b9'
KERNEL_SHA='56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270'
CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
TOOLS=('calendar.events','calendar.get_event','calendar.add_event','calendar.update_event','calendar.remove_event','calendar.notify')
CANON={t.replace('.','_'):t for t in TOOLS}
FIELDS=('title','start','end','timezone','location','notes')
REQUIRED=('stable_retry_restart','destructive_update_deny','destructive_remove_deny','interrupt_reconcile','signed_caller_withdrawal')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def lines(path):return [json.loads(s) for s in path.read_text().splitlines()] if path.is_file() else []
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=True,indent=2)+'\n')
def require(value,message):
    if not value:raise AssertionError(message)

class Bridge:
    def __init__(self,args,out,launch):
        self.out=out;self.seq=0;self.waiting={};self.q=queue.Queue()
        self.err=(out/f'wrapper-{launch}-stderr.log').open('w')
        command=['python3',str(args.bridge),'--test-binary',str(args.test_binary),'--kernel',str(args.kernel),'--config',str(args.config)]
        self.p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True,bufsize=1)
        save(out/f'launch-{launch}.json',{'command':command,'wrapper_pid':self.p.pid})
        def read():
            try:
                with (out/f'wrapper-{launch}-stdout.jsonl').open('w') as raw:
                    for line in self.p.stdout:
                        raw.write(line);raw.flush();self.q.put(json.loads(line))
            except Exception as error:self.q.put(error)
            finally:self.q.put(None)
        threading.Thread(target=read,daemon=True).start()
        ready=self.receive(None,30)
        require(ready.get('method')=='fixture.ready' and ready.get('is_ok') is True,'No actual fixture.ready/admission')
        require(ready['data']['source_main_sha256']==MAIN_SHA and ready['data']['kernel_sha256']==KERNEL_SHA,'Actual ready identity drift')
    def send(self,method,payload=None):
        self.seq+=1;rid=f'l4-{self.p.pid}-{self.seq}'
        request={'request_id':rid,'method':method,'payload':payload or {}}
        with (self.out/'parent-requests.jsonl').open('a') as f:f.write(json.dumps(request)+'\n')
        self.p.stdin.write(json.dumps(request)+'\n');self.p.stdin.flush();return rid
    def receive(self,rid,timeout=200):
        if rid in self.waiting:return self.waiting.pop(rid)
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            item=self.q.get(timeout=max(.01,deadline-time.monotonic()))
            if isinstance(item,Exception):raise item
            if item is None:raise RuntimeError('Actual bridge exited before reply')
            if item.get('request_id')==rid:return item
            self.waiting[item.get('request_id')]=item
        raise TimeoutError('Actual bridge reply unknown; never automatically retry a write')
    def call(self,method,payload=None):return self.receive(self.send(method,payload))
    def data(self,method,payload=None):
        reply=self.call(method,payload);require(reply.get('is_ok') is True,f'{method}: {reply}');return reply['data']
    def open(self):
        data=self.data('octos.session.open')
        require(data.get('conversation') is True and data.get('shared_history') is True,'Actual public conversation contract not enabled')
    def quit(self):
        self.data('fixture/quit');self.p.stdin.close()
        code=self.p.wait(timeout=20);self.err.close();require(code==0,f'Actual wrapper/test exit {code}')

def turn_payload(text,steps,approval='once'):
    return {'text':text,'trigger':'app','fixture_approval':approval,'fixture_tool_plan':steps}
def step(tool,args):return {'tool':tool,'args':args}
def turn(bridge,text,steps,approval='once'):
    return bridge.call('octos.turn.start',turn_payload(text,steps,approval))
def snapshot(bridge,root):
    owner=bridge.data('fixture/logsideeffects');store=root/'apps/.host/calendar/events.json'
    return {'actual_owner_result':owner,'event_count':len(owner['events']),'store_sha256':sha(store) if store.is_file() else None}
def event(bridge,identity):
    value=bridge.data('fixture/read-owner',{'method':'get_event','args':identity})
    require(value.get('found') is True,'Selected actual owner event absent');return value['event']
def bound_receipt(history,reply,tool,terminal):
    tid=reply.get('data',{}).get('turn_id');require(bool(tid),'Actual turn ID missing')
    matches=[row for row in history.get('messages',[]) if row.get('role')=='tool'
             and CANON.get(row.get('tool_name',row.get('name')))==tool
             and row.get('host_calendar_receipt',{}).get('turn_id')==tid]
    require(len(matches)==1,f'Expected one exact actual History row for {tool}/{tid}')
    row=matches[0];receipt=row['host_calendar_receipt']
    require(row.get('lane') in ('person','system_agent'),'Actual merged History lane missing')
    require(receipt.get('kernel_persisted') is True and receipt.get('source')=='broker_tool_result','Actual bound persisted receipt missing')
    require(receipt.get('owner')=='os.calendar' and receipt.get('caller') in ('muse-goals','card.muse-goals'),'Actual receipt owner/caller mismatch')
    require(receipt.get('terminal')==terminal,'Actual receipt terminal mismatch')
    require(row.get('tool_call_id')==receipt.get('tool_call_id') and (row.get('turn_id') or row.get('thread_id'))==tid,'Actual occurrence IDs mismatch')
    require(all(receipt.get(k) for k in ('call_id','session_id','tool_call_id','args_digest')),'Actual receipt identifiers missing')
    return receipt

def run(args):
    cfg=json.loads(args.config.read_text());input_root=Path(cfg['fixture_root'])
    require(not input_root.is_symlink(),'Symlink fixture root refused')
    root=input_root.resolve(strict=True)
    central_fixture=(CENTRAL/'build/night-004').resolve()
    require(root!=central_fixture and root.is_relative_to(central_fixture) and (root/'FIXTURE_ONLY').is_file(),'Only marked central NIGHT-004 fixture root')
    for path in (root/'FIXTURE_ONLY',root/'apps',root/'apps/catalog.json',root/'apps/.host',root/'apps/.host/calendar',root/'apps/.host/calendar/events.json'):
        require(not path.is_symlink(),'Fixture marker/store ancestors cannot be symlinks')
    require(cfg['main_sha256']==MAIN_SHA and sha(Path(cfg['signed_bundle'])/'main.splash')==MAIN_SHA,'Frozen signed candidate must be 643009')
    require(sha(args.sdk_test_source)==SOURCE_SHA,'Actual R8 test source must be 0426')
    require(len(args.test_binary_sha256)==64 and sha(args.test_binary)==args.test_binary_sha256,'Explicit actual R8 test binary identity mismatch')
    require(sha(args.kernel)==KERNEL_SHA,'Pinned actual Kernel mismatch')
    out=args.out.resolve();require(out.is_relative_to(root) and out!=root,'Output must be a new child of this fixture root')
    out.mkdir(parents=True,exist_ok=False)
    result={'state':'RUNNING','scope':'Signed candidate actual bridge/Broker/Kernel L4; no production Main VM evaluation',
            'fixture_model':True,'fixture_authorization':True,'main_sha256':MAIN_SHA,'source_sha256':SOURCE_SHA,
            'test_binary_sha256':args.test_binary_sha256,'kernel_sha256':KERNEL_SHA,'cases':[]}
    save(out/'identity.json',{k:v for k,v in result.items() if k!='cases'})
    bridge=None
    try:
        bridge=Bridge(args,out,1);bridge.open()
        require(snapshot(bridge,root)['event_count']==0,'Use a fresh empty isolated owner store')
        request_id='night004-bridge-l4-'+uuid.uuid4().hex
        add={'title':'NIGHT004 synthetic bridge L4','start':'2026-10-13T15:00','end':'2026-10-13T15:30',
             'timezone':'Asia/Shanghai','location':'Synthetic fixture room','notes':'Synthetic original notes','request_id':request_id}
        plan=[step('calendar.add_event',add),step('calendar.get_event',{'request_id':request_id})]
        first=turn(bridge,'Synthetic L4: create and precisely read this selected fixture event.',plan)
        require(first.get('is_ok') is True,'Actual create turn failed')
        original=event(bridge,{'request_id':request_id});before=snapshot(bridge,root)
        require(before['event_count']==1 and all(original[k]==v for k,v in add.items()),'Actual initial fields/count mismatch')
        for label in ('same_process_retry','restart_retry'):
            if label=='restart_retry':bridge.quit();bridge=Bridge(args,out,2);bridge.open()
            retry=turn(bridge,'Synthetic L4: repeat the exact same stable fixture request, then read it.',plan)
            require(retry.get('is_ok') is True,'Actual stable retry turn failed')
            history=bridge.data('octos.session.history');receipt=bound_receipt(history,retry,'calendar.add_event','ok')
            require(receipt['result']['data'].get('reused') is True,'Actual add retry did not report reuse')
            after=snapshot(bridge,root);require(after==before and event(bridge,{'request_id':request_id})==original,'Retry changed/duplicated actual event')
            save(out/f'{label}.json',{'actual_turn_reply':retry,'actual_history':history,'before':before,'after':after})
        archived=bridge.data('fixture/history-sessions')
        require(any(CANON.get(row.get('tool_name',row.get('name')))=='calendar.add_event'
                    for h in archived['histories'] for row in h.get('raw_kernel_history',{}).get('messages',[])), 'Actual persisted archive tool rows missing')
        save(out/'restart-raw-history.json',archived)
        result['cases'].append({'case':'stable_retry_restart','status':'PASS','request_id':request_id,'event_id':original['id']})
        for tool in ('calendar.update_event','calendar.remove_event'):
            current=event(bridge,{'id':original['id']});mutation={'id':current['id'],'expected':current}
            if tool=='calendar.update_event':mutation.update({k:current[k] for k in FIELDS});mutation['notes']='Synthetic denied change'
            before=snapshot(bridge,root);audit_path=root/'approval-home/logs/approvals-audit.jsonl';audit_start=len(lines(audit_path))
            fixture_path=root/'fixture-approvals.jsonl';fixture_start=len(lines(fixture_path))
            denied=turn(bridge,'Synthetic L4: request this destructive mutation; fixture sheet decision is Deny.',[step(tool,mutation)],'deny')
            history=bridge.data('octos.session.history');receipt=bound_receipt(history,denied,tool,'error')
            require(receipt['result']['error']['kind']=='declined','Actual terminal is not Router decline')
            decisions=lines(audit_path)[audit_start:];fixtures=lines(fixture_path)[fixture_start:]
            require(any(r.get('id')=='hosttool:'+receipt['call_id'] and r.get('app')=='os.calendar' and r.get('tool')==tool
                        and r.get('result')=='denied' and r.get('by')=='person' and r.get('reason')=='denied on the sheet' for r in decisions), 'Actual confirmation sheet/audit ID did not match Kernel call')
            require(any(r.get('owner')=='os.calendar' and r.get('tool')==tool and r.get('args')==mutation
                        and r.get('approved') is False and r.get('fixture_gesture') is True for r in fixtures), 'Actual fixture answer did not match pending owner request')
            after=snapshot(bridge,root);require(after==before and event(bridge,{'id':current['id']})==current,'Deny produced an actual side effect')
            case='destructive_update_deny' if tool.endswith('update_event') else 'destructive_remove_deny'
            save(out/f'{case}.json',{'actual_turn_reply':denied,'actual_history':history,'actual_audit':decisions,'actual_fixture_answers':fixtures,'before':before,'after':after})
            result['cases'].append({'case':case,'status':'PASS','call_id':receipt['call_id']})
        current=event(bridge,{'id':original['id']});before=snapshot(bridge,root)
        update={k:current[k] for k in FIELDS};update.update(id=current['id'],expected={'$tool_result':0,'path':['event']},notes='Synthetic interrupted revision')
        resolved=root/'resolved-model-calls.jsonl';offset=len(lines(resolved))
        events=root/'actual-kernel-events.jsonl';events_offset=len(lines(events))
        pending=bridge.send('octos.turn.start',turn_payload('Synthetic L4: get this event, then request its selected update.',
                            [step('calendar.get_event',{'id':current['id']}),step('calendar.update_event',update)]))
        deadline=time.monotonic()+20
        while not any(r.get('tool')=='calendar.update_event' for r in lines(resolved)[offset:]):
            require(time.monotonic()<deadline,'Actual update was never resolved; pending outcome unknown, no write retry')
            time.sleep(.005)
        interrupt_id=bridge.send('octos.turn.interrupt');interrupted=bridge.receive(interrupt_id);terminal=bridge.receive(pending)
        starts=[v for v in lines(events)[events_offset:] if v.get('method')=='turn/started']
        started_ids={v.get('params',{}).get('turn_id') for v in starts}-{None}
        stopped_ids=set(interrupted.get('data',{}).get('interrupted',[]))
        actual_stop=interrupted.get('is_ok') is True and bool(started_ids & stopped_ids)
        after=snapshot(bridge,root);after_event=event(bridge,{'id':current['id']})
        require(after['event_count']==1 and after_event['request_id']==request_id,'Interrupted operation duplicated/lost selected identity')
        require(all(after_event[k]==current[k] for k in FIELDS if k!='notes') and after_event['notes'] in (current['notes'],update['notes']), 'Reconciliation found unexpected owner state')
        check=turn(bridge,'Synthetic L4: read only; reconcile the selected event after interruption.',[step('calendar.get_event',{'id':current['id']})])
        history=bridge.data('octos.session.history');receipt=bound_receipt(history,check,'calendar.get_event','ok')
        require(receipt['result']['data']['event']==after_event and snapshot(bridge,root)==after,'Actual read-only Kernel reconciliation mismatch')
        save(out/'interrupt_reconcile.json',{'actual_interrupt_reply':interrupted,'actual_pending_turn_terminal':terminal,
             'actual_turn_started_events':starts,
             'actual_reconcile_turn':check,'actual_history':history,'before':before,'after':after,'actual_owner_event':after_event,
             'observation':'actual Kernel interruption' if actual_stop else 'completion/interruption race; no cancellation coverage'})
        result['cases'].append({'case':'interrupt_reconcile','status':'PASS' if actual_stop else 'NOT_TESTED','side_effect_observed':after!=before})
        if args.withdrawal_catalog:
            catalog=root/'apps/catalog.json';old=json.loads(catalog.read_text());new=json.loads(args.withdrawal_catalog.read_text())
            selected=[e for e in new.get('entries',[]) if e.get('manifest',{}).get('id')=='muse-goals' and e['manifest'].get('version')=='0.4.0-rc7']
            require(len(selected)==1 and selected[0].get('status',{}).get('state')=='withdrawn','Explicit signed catalog must withdraw the exact selected public release')
            require(new.get('sequence',0)>old['sequence'] and bool(new.get('signature')),'Withdrawal needs signed higher sequence')
            offered=next(e for e in old['entries'] if e['manifest']['id']=='muse-goals' and e['manifest']['version']=='0.4.0-rc7')
            require(selected[0]['manifest']==offered['manifest'],'Withdrawal must preserve the exact public candidate manifest')
            allowed=[{**e,'status':selected[0]['status']} if e==offered else e for e in old['entries']]
            require(new['entries']==allowed,'Withdrawal must change only the selected entry status')
            before=snapshot(bridge,root);(out/'original-offered-catalog.json').write_bytes(catalog.read_bytes())
            require(not catalog.is_symlink(),'Fixture catalog cannot be a symlink')
            staging=catalog.with_name('catalog.l4-withdrawal.tmp');require(not staging.exists(),'Do not overwrite prior evidence')
            staging.write_bytes(args.withdrawal_catalog.read_bytes());staging.replace(catalog)
            mutation={k:after_event[k] for k in FIELDS};mutation.update(id=after_event['id'],expected=after_event,notes='Synthetic revoked request')
            denied=turn(bridge,'Synthetic L4: request update after genuine signed caller withdrawal.',[step('calendar.update_event',mutation)])
            require(denied.get('is_ok') is False and 'withdrawn' in denied.get('error',{}).get('message','').lower(),'Actual verified admission did not report withdrawal')
            after=snapshot(bridge,root);require(after==before,'Signed withdrawal did not prevent actual side effect')
            save(out/'signed_caller_withdrawal.json',{'withdrawal_catalog_sha256':sha(args.withdrawal_catalog),'actual_turn_reply':denied,'before':before,'after':after,
                 'phase':'real signature/catalog admission; no fabricated Kernel tool receipt','restoration':'none; original lower sequence is not restored'})
            result['cases'].append({'case':'signed_caller_withdrawal','status':'PASS'})
        else:result['cases'].append({'case':'signed_caller_withdrawal','status':'NOT_TESTED','reason':'Root must supply public same-anchor signed higher-sequence withdrawal catalog'})
        result['state']='PASS' if all(any(c['case']==name and c['status']=='PASS' for c in result['cases']) for name in REQUIRED) else 'PARTIAL'
        bridge.quit();bridge=None
    except Exception as error:
        result['state']='FAILED';result['error']=str(error)
        result['recovery']='Actual result unknown where a reply was missing. Preserve store/history; no automatic write retry.'
    finally:
        if bridge:
            try:bridge.quit()
            except Exception as error:
                result['shutdown_error']=str(error)
                # EOF asks the actual driver to settle its pending operation or
                # mark its deadline unknown; do not kill another Kernel/UI.
                try:
                    if not bridge.p.stdin.closed:bridge.p.stdin.close()
                    result['eof_exit_code']=bridge.p.wait(timeout=205)
                    bridge.err.close()
                except Exception as eof_error:result['eof_shutdown_error']=str(eof_error)
        save(out/'result.json',result)
    print(json.dumps({'state':result['state'],'result':str(out/'result.json')}))
    return 0 if result['state']=='PASS' else 2

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--test-binary',type=Path,required=True)
    parser.add_argument('--test-binary-sha256',required=True,help='Actual Root R8 binary SHA; no guessed identity')
    parser.add_argument('--kernel',type=Path,required=True)
    parser.add_argument('--bridge',type=Path,default=Path(__file__).with_name('bridge.py'))
    parser.add_argument('--sdk-test-source',type=Path,default=CENTRAL/'build/runtime-closure-full-shell-r1/sdk/crates/shell/src/host_tools/real_kernel_tests.rs')
    parser.add_argument('--withdrawal-catalog',type=Path,help='Root-provided public same-anchor signed higher-sequence withdrawn catalog; required for complete PASS')
    parser.add_argument('--out',type=Path,required=True,help='New evidence directory inside the selected marked fixture root')
    return run(parser.parse_args())
if __name__=='__main__':raise SystemExit(main())
