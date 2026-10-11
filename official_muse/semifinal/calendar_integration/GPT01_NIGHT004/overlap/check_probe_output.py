#!/usr/bin/env python3
"""Check compact final JSON formatting in the frozen VM, with saved data only."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[4]
CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
REAL=CENTRAL/'build/night-004/gpt01-overlap-same-r2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lit=lambda v:json.dumps(json.dumps(v,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+'.parse_json()'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vm',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); out=a.out.resolve();out.relative_to(OWN/'build');out.mkdir(parents=True,exist_ok=False)
    assert sha(a.vm)=='f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351'
    sys.path.insert(0,str(CENTRAL/'official_muse/prelim/tests/calendar_sync'))
    from run import functions_in
    probe=(HERE/'native_overlap_probe.splash').read_text(); func=functions_in(probe)['native_overlap_probe']
    # Exact changed final assignment; discarded raw dictionaries never enter it.
    final=func[func.index('    overlap_observations = {'):].rsplit('}',1)[0]
    root=json.loads((REAL/'run/report.json').read_text()); trace=root['trace']
    replies=lambda method:[x['reply']['data'] for x in trace if x['request']['method']==method and x['reply'].get('is_ok')]
    history=replies('octos.session.history'); events=[r['host_calendar_receipt']['result']['data']['events'] for r in history[0]['messages'] if r.get('role')=='tool']
    bounded=[r['host_calendar_receipt']['result']['data']['events'] for r in history[3]['messages'] if r.get('tool_name')=='calendar_events'][-1]
    owner=replies('fixture/logsideeffects'); state=json.loads((REAL/'state/calendar-agent-state.json').read_text())
    goals=json.loads((REAL/'state/goals.json').read_text())
    expected=json.loads((REAL/'state/l3-native-checkpoint.json').read_text())['event']
    data={'overlap_case':'same','overlap_expected_block':True,'expected':expected,'owner_before':owner[0],
        'owner_after':owner[-1],'sha_before':'103a5a86b630f772b0c560541a48a856cd1f9b300183baf4088d651b9017668a',
        'sha_after':'aa86c92ee37c7765026b08feb47370ab1723fb0c17119238814ba252792a5792',
        'full':{'events':events[0]},'bounded':{'events':bounded},'first_count':2,
        'first_sha':'aa86c92ee37c7765026b08feb47370ab1723fb0c17119238814ba252792a5792',
        'first_status':state['status'],'goals':goals['goals'],'runs':goals['runs'],
        'calendar_agent_state':state,'calendar_agent_notice':'FORMAT ONLY: saved prepatch fixture fields, no live action.',
        'receiver':replies('fixture.receiver')[-1]}
    main_funcs=functions_in((CENTRAL/'official_muse/app/source/main.splash').read_text())
    program='use mod.math.*\nuse mod.std.*\nlet overlap_observations={}\n'
    program+='\n'.join('let '+k+'='+lit(v) for k,v in data.items())+'\n'
    program+=main_funcs['calendar_agent_event_json']+'\n'+functions_in(probe)['overlap_matching']+'\n'
    program+='fn emit_saved_fields(){\n'+final+'}\nemit_saved_fields()\n'
    program+='let overlap_checks={format_only:true}\n'
    program+=functions_in(probe)['native_overlap_result']+'\nnative_overlap_result()\n'
    path=out/'saved-fields.splash';path.write_text(program)
    r=subprocess.run([str(a.vm),str(path),'--rpc'],input='',capture_output=True,text=True,timeout=20)
    (out/'stdout.log').write_text(r.stdout);(out/'stderr.log').write_text(r.stderr)
    lines=[s[len('MUSE_VM_RESULT '):] for s in r.stdout.splitlines() if s.startswith('MUSE_VM_RESULT ')]
    parsed=json.loads(lines[-1]) if len(lines)==1 else None
    assert r.returncode==0 and r.stderr=='' and parsed and parsed['kind']=='NIGHT004_NATIVE_OVERLAP_PROBE'
    assert not any(s.startswith('MUSE_VM_RPC ') for s in r.stdout.splitlines())
    obs=parsed['observations'];assert obs['after_owner_count']==2 and all(isinstance(v,(str,int,bool)) for v in obs.values())
    record={'status':'PASS_COMPACT_FORMAT_ONLY','exit_code':r.returncode,'rpc_requests':0,'program':str(path),
        'program_sha256':sha(path),'stdout_sha256':sha(out/'stdout.log'),'output_bytes':len(r.stdout.encode()),
        'observation_fields':len(obs),'probe_sha256':sha(HERE/'native_overlap_probe.splash'),
        'boundary':'Exact final assignment and exact local-string result function with saved actual fixture fields. No VM probe journey/Kernel/services/RPC; format-only checks, no fabricated passing receipt. Root full-path compact output remains pending.'}
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    (HERE/'COMPACT_OUTPUT_VM_RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

if __name__=='__main__':main()
