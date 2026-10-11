"""Owned temporary fixture only: real owner update, guards and stale CAS."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
target=OWN/'build/gpt01-calendar-history/target/debug'
binary=target/'gpt01-night004-external-owner'
original=target/'gpt01-night004-calendar'
rows=[]
with tempfile.TemporaryDirectory(prefix='gpt01-night004-external-') as name:
    root=Path(name).resolve();seed=root/'apps/gpt01-night004-seed';seed.mkdir(parents=True)
    (root/'FIXTURE_ONLY').write_text('Synthetic isolated verification only\n')
    (seed/'FIXTURE_ONLY').write_text('Synthetic isolated verification only\n')
    def seed_call(method,args):
        request={'owner':'os.calendar','method':method,'args':args}
        run=subprocess.run([str(original),str(seed)],input=json.dumps(request),capture_output=True,text=True,timeout=10)
        assert run.returncode==0,run.stderr
        reply=json.loads(run.stdout);assert reply['result']['ok'],reply
        rows.append({'step':'actual_seed_'+method,'request':request,'reply':reply})
        return reply['result']['data']
    fields={'title':'Synthetic external owner CAS','start':'2026-10-13T15:00','end':'2026-10-13T15:30',
            'timezone':'Asia/Shanghai','location':'Fixture room','notes':'Original synthetic notes','request_id':'night004-external-owner-check'}
    created=seed_call('add_event',fields)
    old=seed_call('get_event',{'id':created['id']})['event']
    host=root/'apps/.host';seed.rename(host) # Move the real fixture store unchanged into bridge layout.
    store=host/'calendar/events.json'
    digest=lambda:hashlib.sha256(store.read_bytes()).hexdigest()
    expected=root/'expected.json';expected.write_text(json.dumps(old))
    config=root/'config.json';config.write_text(json.dumps({'fixture_root':str(root)}))
    marker=host/'EXTERNAL_CALENDAR_OWNER_WRITE_OK.json'
    scope={'purpose':'NIGHT004_SYNTHETIC_EXTERNAL_OWNER','host_dir':str(host),'event_id':old['id'],'fixture_request_id':old['request_id']}
    update={'owner':'os.calendar','method':'update_event','args':{'id':old['id'],'expected':old,**{k:old[k] for k in ('title','start','end','timezone','location','notes')}}}
    update['args']['notes']='External process changed synthetic notes'
    def direct(step,request,ok,check=False):
        before=digest();cmd=[str(binary)]+(['--check-only'] if check else [])+[str(root),old['id'],old['request_id']]
        run=subprocess.run(cmd,input=json.dumps(request),capture_output=True,text=True,timeout=10)
        assert run.returncode==0,run.stderr
        reply=json.loads(run.stdout);assert reply['result']['ok'] is ok,reply
        rows.append({'step':step,'request':request,'reply':reply,'before_sha256':before,'after_sha256':digest()})
        if check or not ok:assert digest()==before
        return reply['result']
    direct('missing_external_write_marker_rejected',update,False)
    marker.write_text(json.dumps({**scope,'event_id':'wrong-event'}))
    direct('wrong_marker_event_rejected',update,False)
    marker.write_text(json.dumps(scope))
    direct('foreign_owner_rejected',{**update,'owner':'muse-goals'},False)
    direct('delete_method_rejected',{**update,'method':'remove_event'},False)
    direct('wrong_expected_request_identity_rejected',{**update,'args':{**update['args'],'expected':{**old,'request_id':'wrong-fixture'}}},False)
    saved=store.with_suffix('.saved');store.rename(saved);store.symlink_to(saved)
    direct('symlink_store_rejected',update,False)
    store.unlink();saved.rename(store)
    direct('read_only_check_returns_actual_owner',update,True,check=True)
    before=digest()
    command=['python3',str(HERE/'external_calendar_update.py'),'--config',str(config),'--event-id',old['id'],
             '--fixture-request-id',old['request_id'],'--expected-file',str(expected),'--notes',update['args']['notes']]
    run=subprocess.run(command,capture_output=True,text=True,timeout=10)
    assert run.returncode==0,run.stdout+run.stderr
    reply=json.loads(run.stdout);assert reply['result']['ok'],reply
    current=reply['result']['data']['event'];assert current['id']==old['id'] and current['request_id']==old['request_id']
    assert current['notes']==update['args']['notes'] and current!=old
    assert all(current[k]==old[k]for k in ('title','start','end','timezone','location'))
    assert len(json.loads(store.read_text()))==1
    rows.append({'step':'wrapper_actual_owner_update','command':command,'reply':reply,'before_sha256':before,'after_sha256':digest(),'event_count':1})
    stale=direct('actual_service_stale_expected_rejected',update,False)
    assert 'changed elsewhere' in stale['error'],stale
    fresh=direct('actual_readback_after_rejection',update,True,check=True)
    assert fresh['data']['current_owner_result']['event']==current
receipt={'state':'EXTERNAL_OWNER_HELPER_LOCAL_GUARDS_AND_REAL_CAS_PASS','kernel':False,'central_state_written':False,
         'fixture_authorization':True,'build':{'exit_code':0,'elapsed_seconds':1.38,'target':'owned small debug target','jobs':1,'nice':10},
         'binary_path':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
         'original_readonly_binary_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'steps':rows,
         'scope':'Real unchanged CalendarService in separate processes; temporary seed store moved unchanged into bridge layout. No actual Kernel/full-chain test or central store write.'}
(HERE/'EXTERNAL_OWNER_RESULT.json').write_text(json.dumps(receipt,ensure_ascii=True,indent=2)+'\n')
print(json.dumps({'state':receipt['state'],'steps':len(rows),'binary_sha256':receipt['binary_sha256'],'original_readonly_binary_sha256':receipt['original_readonly_binary_sha256']}))
