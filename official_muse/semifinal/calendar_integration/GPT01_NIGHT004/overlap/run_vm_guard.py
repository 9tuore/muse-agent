#!/usr/bin/env python3
"""Pure/replay checks in an existing VM, without Kernel, Mail, GUI or build.

An unchanged real {} query is the receipt parser's positive replay. Main's
required {limit:200} digest rejects it. No passing receipt is manufactured.
Scope/gesture states are explicit unit fixtures, not Host approvals.
"""
import argparse,copy,hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[4]
CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
REAL=CENTRAL/'build/night-004/gpt01-overlap-same-r2'
VM_SHA='f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351'
sha=lambda b:hashlib.sha256(b).hexdigest()
literal=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
def splash(v): return literal(literal(v))+'.parse_json()'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--vm',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); out=a.out.resolve(); out.relative_to(OWN/'build'); out.mkdir(parents=True,exist_ok=False)
    assert sha(a.vm.read_bytes())==VM_SHA,'Frozen VM differs'
    sys.path.insert(0,str(CENTRAL/'official_muse/prelim/tests/calendar_sync'))
    from run import functions_in
    source=a.source.read_text(); funcs=functions_in(source)
    common=['gm_object','gm_array','gm_text','gm_number','gm_string','gm_get','gm_has','gm_account_allowed',
        'calendar_agent_receipt_status','calendar_agent_tool_name']
    dates=['calendar_iso_epoch','gm_time_valid','page_event_epoch','page_parse_date','page_two_number',
        'page_two','page_day_number','page_month_days']
    scopes=['calendar_agent_binding_valid','calendar_agent_event_matches','calendar_agent_binding_current',
        'calendar_agent_binding_at_revision','ac_goal_allowed','ac_current_goal','ac_field','chat_session_index',
        'chat_card_scope_current','chat_reply_context_valid','chat_payload_error','calendar_agent_same_candidate']
    proposal=[n for n in funcs if n.startswith('calendar_agent_preflight_')]+['calendar_agent_candidate_submit_label','calendar_agent_submit_candidate']
    names=list(dict.fromkeys(common+dates+scopes+proposal))
    defs='\n'.join(funcs[n] for n in names)
    # The full production memory-reference code is preserved. The actual recorded
    # candidate has zero memory refs; its unused branch makes no backend call.
    report=json.loads((REAL/'run/report.json').read_text())
    history=report['trace'][46]['reply']['data']
    assert report['trace'][46]['request']['method']=='octos.session.history'
    rows=[r for r in history['messages'] if r.get('role')=='tool']; assert len(rows)==1
    turn=rows[0]['thread_id']; receipt=rows[0]['host_calendar_receipt']
    assert receipt['args_digest']=='sha256:'+sha(b'{}')
    binding=json.loads((REAL/'state/calendar-agent-state.json').read_text())['binding']
    chats=json.loads((REAL/'state/chat-sessions.json').read_text())['sessions']
    goals=json.loads((REAL/'state/goals.json').read_text())['goals']
    card=next(c for s in chats for c in s.get('proposals',[]) if c['id']==binding['candidate_id'])
    assert card.get('memory_refs',[])==[]
    owner=json.loads((REAL/'kernel-state/apps/.host/calendar/events.json').read_text())
    event=next(e for e in owner if e['id']=='ev-1791775730787')
    prefix='use mod.math.*\nuse mod.std.*\nlet fs={sha256:|text|mod.fixture.sha256(text)}\n'
    prefix+='let gm_time_cache={}\nlet gm_error=""\n'
    prefix+='let calendar_agent_state='+splash({'turn_id':turn})+'\n'+defs+'\n'
    results=[]
    def execute(name,program):
        path=out/(name+'.splash'); path.write_text(prefix+program)
        proc=subprocess.Popen([str(a.vm),str(path),'--rpc'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try: stdout,stderr=proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill(); stdout,stderr=proc.communicate()
            (out/(name+'-stdout.log')).write_text(stdout); (out/(name+'-stderr.log')).write_text(stderr)
            raise AssertionError(name+' timed out')
        (out/(name+'-stdout.log')).write_text(stdout); (out/(name+'-stderr.log')).write_text(stderr)
        rpc=sum(line.startswith('MUSE_VM_RPC ') for line in stdout.splitlines())
        lines=[line[15:] for line in stdout.splitlines() if line.startswith('MUSE_VM_RESULT ')]
        values=json.loads(lines[-1]) if len(lines)==1 else None
        passed=proc.returncode==0 and stderr=='' and rpc==0 and isinstance(values,dict) and all(v is True for v in values.values())
        result={'case':name,'status':'PASS' if passed else 'FAIL','exit_code':proc.returncode,'rpc_requests':rpc,
            'checks':values,'stdout_sha256':sha(stdout.encode()),'stderr_sha256':sha(stderr.encode()),'program_sha256':sha(path.read_bytes())}
        results.append(result)
        print(json.dumps(result),flush=True)
        assert passed,name+' failed; preserved stdout/stderr'
    # Positive data stays byte-for-byte equal as a Python object. All negative
    # histories are explicitly altered copies; they are never dispatched.
    bad=[]
    def reject(name,change):
        h=copy.deepcopy(history); change(h); bad.append((name,h))
    tool_index=next(i for i,r in enumerate(history['messages']) if r.get('role')=='tool')
    row=lambda h:h['messages'][tool_index]
    reject('duplicate_occurrence',lambda h:h['messages'].append(copy.deepcopy(row(h))))
    reject('wrong_lane',lambda h:row(h).__setitem__('lane','app'))
    reject('unknown_tool',lambda h:row(h).__setitem__('tool_name','unrelated_tool'))
    reject('missing_receipt',lambda h:row(h).pop('host_calendar_receipt'))
    reject('missing_tool_call_id',lambda h:row(h).__setitem__('tool_call_id',''))
    reject('wrong_receipt_tool_call',lambda h:row(h)['host_calendar_receipt'].__setitem__('tool_call_id','other'))
    reject('wrong_turn',lambda h:row(h)['host_calendar_receipt'].__setitem__('turn_id','other'))
    reject('wrong_session',lambda h:row(h)['host_calendar_receipt'].__setitem__('session_id','other'))
    reject('context_session_mismatch',lambda h:h['context_state'].__setitem__('session_id','other'))
    reject('missing_top_session',lambda h:h.pop('session_id'))
    reject('missing_persisted_at',lambda h:row(h).pop('persisted_at'))
    reject('result_call_mismatch',lambda h:row(h)['host_calendar_receipt']['result'].__setitem__('call_id','other'))
    reject('not_kernel_persisted',lambda h:row(h)['host_calendar_receipt'].__setitem__('kernel_persisted',False))
    reject('invalid_thread',lambda h:row(h).__setitem__('thread_id','other'))
    reject('missing_turn_identifiers',lambda h:row(h).pop('thread_id'))
    def extra(h):
        r=copy.deepcopy(row(h)); r['tool_name']='calendar_add_event';r['tool_call_id']='extra';h['messages'].append(r)
    reject('extra_mutation_occurrence',extra)
    def repeated(h):
        r=copy.deepcopy(row(h));r['thread_id']='older-other-turn';h['messages'].append(r)
    reject('reused_id_in_other_turn',repeated)
    program='let real_history='+splash(history)+'\nlet checks={}\n'
    program+='let parsed=calendar_agent_preflight_query(real_history,"{}")\n'
    program+='checks.real_original_query_receipt = parsed != nil && parsed.call_id == '+literal(receipt['call_id'])+'\n'
    program+='checks.required_limit_200_rejects_original_empty_args = calendar_agent_preflight_query(real_history,"{\\"limit\\":200}") == nil\n'
    for name,h in bad:
        program+='checks.'+name+' = calendar_agent_preflight_query('+splash(h)+',"{}") == nil\n'
    program+='checks.history_unchanged = real_history.to_json() == '+literal(literal(history))+'\nchecks.to_json()\n'
    execute('receipt-replay',program)
    # Pure interval fixtures use the original actual owner event. No receipt or
    # tool result is invented to make a production query pass.
    cases=[('same','2026-10-13T16:00','2026-10-13T16:30',1),('contained','2026-10-13T16:10','2026-10-13T16:20',1),
        ('spanning','2026-10-13T15:50','2026-10-13T16:40',1),('cross_start','2026-10-13T15:50','2026-10-13T16:10',1),
        ('cross_end','2026-10-13T16:20','2026-10-13T16:40',1),('adjacent_after','2026-10-13T16:30','2026-10-13T17:00',0),
        ('adjacent_before','2026-10-13T15:30','2026-10-13T16:00',0)]
    program='let checks={}\nlet actual_event='+splash(event)+'\n'
    candidate={'timezone':'Asia/Shanghai','start':event['start'],'end':event['end']}
    for name,start,end,n in cases:
        c=candidate|{'start':start,'end':end}
        program+='let compared=calendar_agent_preflight_compare('+splash(c)+',[actual_event])\n'
        program+='checks.'+name+'=compared.status=="ready" && compared.conflicts.len()=='+str(n)+'\n'
    for name,change in [('timezone',{'timezone':'UTC'}),('no_end',{'end':''}),('bad_date',{'start':'2026-02-30T16:00'}),('zero_duration',{'end':event['start']})]:
        program+='checks.'+name+'=calendar_agent_preflight_compare('+splash(candidate)+',['+splash(event|change)+']).status=="unknown"\n'
    program+='let capped=[]\nfor i in 200 {capped.push(actual_event)}\n'
    program+='checks.cap_200_unknown=calendar_agent_preflight_compare('+splash(candidate)+',capped).status=="unknown"\n'
    program+='checks.empty_snapshot_ready=calendar_agent_preflight_compare('+splash(candidate)+',[]).status=="ready"\nchecks.to_json()\n'
    execute('intervals',program)
    # Exact existing scope gate, not a stub. Only view/dispatch adapters are
    # counted locally; they perform no action and return no fabricated receipt.
    b=copy.deepcopy(binding); b['receipt_status']='unknown'; b.pop('verification',None);b['payload']['request_id']=''
    init='let original_binding='+splash(b)+'\nlet original_chats='+splash(chats)+'\nlet original_goals='+splash(goals)+'\n'
    init+='let calendar_agent_candidate=nil\nlet calendar_agent_preflight={}\nlet calendar_agent_update_state={records:[]}\n'
    init+='let chat_sessions=[]\nlet goals=[]\nlet gm_accounts=[]\nlet gm_user_id=""\nlet gm_project=""\nlet gm_owner=""\nlet chat_selected_id=""\nlet ac_selected_chat=""\nlet ac_selected_id=""\n'
    init+='let core_storage_ready=true\nlet gm_ready=true\nlet page=""\nlet task=nil\nlet calendar_agent_busy=false\nlet calendar_agent_writable=true\nlet calendar_agent_notice=""\nlet test_queries=0\nlet test_creates=0\nlet test_query_text=""\n'
    init+='fn redraw(){}\nfn time_now(){return 1791741568}\nfn calendar_agent_submit(text){test_queries=test_queries+1 test_query_text=text}\nfn calendar_agent_submit_bound(text,binding){test_creates=test_creates+1}\n'
    init+='fn reset(){calendar_agent_candidate=original_binding.to_json().parse_json() chat_sessions=original_chats.to_json().parse_json() goals=original_goals.to_json().parse_json()'
    init+=' gm_accounts=original_binding.accounts.parse_json() gm_user_id=original_binding.user_id gm_project=original_binding.project_id gm_owner=original_binding.owner_id chat_selected_id=original_binding.session_id ac_selected_chat=chat_selected_id ac_selected_id=original_binding.goal_id'
    init+=' calendar_agent_state={request_id:"unit-query" turn_id:"unit-turn" status:"idle" binding:nil previous_requests:[]} calendar_agent_preflight={status:"empty"} test_queries=0 test_creates=0}\n'
    init+='fn snapshot(){calendar_agent_state.status="turn_completed" calendar_agent_preflight={status:"ready" candidate_json:calendar_agent_candidate.to_json() request_id:"unit-query" turn_id:"unit-turn" conflicts:[] reason:""}}\n'
    init+='fn archive(){calendar_agent_state={request_id:"" turn_id:"" status:"idle" previous_requests:[{request_id:"unit-query" turn_id:"unit-turn" status:"turn_completed" binding:nil user_id:gm_user_id accounts:gm_accounts.to_json()}]}}\n'
    program=init+'let checks={}\nreset()\nchecks.exact_production_binding_current=calendar_agent_binding_current(calendar_agent_candidate)\n'
    program+='calendar_agent_submit_candidate()\nchecks.first_gesture_query_only=test_queries==1 && test_creates==0 && test_query_text.search("{\\"limit\\":200}")>=0\n'
    program+='reset() snapshot()\nchecks.current_snapshot_ready=calendar_agent_preflight_current()\ncalendar_agent_submit_candidate()\nchecks.unsettled_query_no_create=test_creates==0\narchive()\nchecks.archived_snapshot_ready=calendar_agent_preflight_current()\ncalendar_agent_submit_candidate()\nchecks.second_gesture_create_path=test_creates==1 && calendar_agent_preflight.status=="consumed"\n'
    program+='reset() snapshot() archive() calendar_agent_preflight.status="unknown" calendar_agent_submit_candidate()\nchecks.unknown_blocks_second_native_create=test_creates==0 && test_queries==0\n'
    for name,mutation in [('account_change','gm_accounts=["local"]'),('user_change','gm_user_id="other"'),('goal_change','ac_selected_id="other"'),('plan_revision_change','goals[goals.len()-1].version=2'),('candidate_revision_change','calendar_agent_candidate.candidate_revision=2'),('candidate_time_change','calendar_agent_candidate.payload.start="2026-10-13T16:30"'),('later_query','calendar_agent_state.previous_requests.push({request_id:"other"})'),('restart','calendar_agent_preflight={status:"empty"}')]:
        program+='reset() snapshot() archive() '+mutation+'\nchecks.'+name+' = !calendar_agent_preflight_current()\n'
    program+='reset() snapshot() archive() calendar_agent_preflight.conflicts=[{title:"synthetic overlap" start:"2026-10-13T16:00" end:"2026-10-13T16:30"}]\n'
    program+='checks.separate_overlap_choice_label=calendar_agent_candidate_submit_label()=="已核对重叠，仍创建此候选"\nchecks.to_json()\n'
    execute('scope-gestures',program)
    identity={'status':'PASS_PURE_VM_REPLAY_ONLY','source_sha256':sha(source.encode()),'vm_sha256':VM_SHA,
        'actual_report':str(REAL/'run/report.json'),'actual_report_sha256':sha((REAL/'run/report.json').read_bytes()),
        'actual_history_trace_index':46,'actual_history_sha256':sha(literal(history).encode()),
        'functions_sha256':{n:sha(funcs[n].encode()) for n in names},'results':results,
        'boundary':'No Kernel/GUI/Mail/Cargo/RPC. Unchanged real {} receipt positive parser replay; Main exact limit200 rejects it. Negative histories are altered unit copies. Interval/scope/gesture states are explicit unit fixtures, no passing Host receipt fabricated. Actual post-patch full chain remains Root work.'}
    (out/'result.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n')
    (HERE/'VM_GUARD_RESULT.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
