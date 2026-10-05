#!/usr/bin/env python3
"""Validate all bounded history, including a damaged final entry; never clear data."""
import copy, hashlib, json, subprocess, sys
from pathlib import Path
import receipt_fixture, regression_run
ROOT=Path(__file__).resolve().parents[3]
out=(ROOT/sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
source=(ROOT/'official_muse/app/source/main.splash').read_text()
source=regression_run.existing.replace_function(source,'boot_load','fn boot_load(step,error){ if step == 1 { restore_done = true restore_error = error } }')
results={};real_popen=subprocess.Popen
for broken in (False,True):
    seed=receipt_fixture.profile('linked63_dense'); history=seed['chat-sessions.json']
    for session in history['sessions']:
        session['messages']=[dict(role='user' if i%2==0 else 'assistant',text='合成恢复文本'*100,state='success',at=1,project='a2-project',owner='a2-owner',memory_refs=[dict(id=f'fixture-ref-{n}',revision=1,account='local',source_ids=[f'source-{j}' for j in range(16)]) for n in range(6)]) for i in range(16)]
    if broken:history['sessions'][-1]['messages'][-1]['memory_refs'][-1]['source_ids'][-1]=17
    expected=receipt_fixture.encoded(history);case=out/('invalid_final' if broken else 'valid_full');case.mkdir()
    probe=case/'probe.splash';probe.write_text('''let restore_done=false
let restore_error=""
let restore_wait=0
fn restore_assert(){
    if !restore_done && restore_wait < 220 { restore_wait=restore_wait+1 start_timeout(0.03,|| restore_assert()) return }
    fs.write("probe.json",{restore_completed:restore_done ready_correct:chat_ready==EXPECTED_READY history_preserved:fs.read("chat-sessions.json")==fs.read("before.json") all_restored:EXPECTED_ALL error_correct:EXPECTED_ERROR}.to_json())
}
fn restore_probe(){chat_boot_begin("") start_timeout(0.03,|| restore_assert())}
start_timeout(0.1,|| restore_probe())
'''.replace('EXPECTED_READY','false' if broken else 'true').replace('EXPECTED_ALL','chat_sessions.len()==0' if broken else 'chat_sessions.len()==16 && messages.len()==16').replace('EXPECTED_ERROR','restore_error!=""' if broken else 'restore_error==""'))
    def seeded(command,*args,**kwargs):
        state=Path(command[command.index('--app-data')+1])/'muse-goals';state.mkdir(parents=True)
        for name,value in seed.items():(state/name).write_text(receipt_fixture.encoded(value))
        (state/'before.json').write_text(expected)
        return real_popen(command,*args,**kwargs)
    regression_run.subprocess.Popen=seeded
    try:
        result=regression_run.run_suite('model_suite',source,ROOT/'official_muse/app/bundle',case/'first',8510,probe)
        results[case.name]=result;print(case.name,result,flush=True)
    finally:regression_run.subprocess.Popen=real_popen
(out/'report.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(int(any(v['failed'] for v in results.values())))
