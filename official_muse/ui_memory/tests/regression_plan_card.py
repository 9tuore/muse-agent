#!/usr/bin/env python3
"""Reproduce direct card approval while preserving an unrelated unsent composer."""
import json,subprocess,sys
from pathlib import Path
import receipt_fixture,regression_run
ROOT=Path(__file__).resolve().parents[3]
out=(ROOT/sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
seed=receipt_fixture.profile('linked63_dense')
seed['goals.json']=dict(schema=2,goals=[],runs=[],actions=[],selected_id='')
real_popen=subprocess.Popen
def seeded(command,*args,**kwargs):
    state=Path(command[command.index('--app-data')+1])/'muse-goals';state.mkdir(parents=True)
    for name,value in seed.items():(state/name).write_text(receipt_fixture.encoded(value))
    return real_popen(command,*args,**kwargs)
regression_run.subprocess.Popen=seeded
try:
    result=regression_run.run_suite('model_suite',(ROOT/'official_muse/app/source/main.splash').read_text(),ROOT/'official_muse/app/bundle',out/'first',8507,Path(__file__).with_suffix('.splash'))
    print(json.dumps(result),flush=True)
finally:regression_run.subprocess.Popen=real_popen
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
raise SystemExit(int(bool(result['failed'])))
