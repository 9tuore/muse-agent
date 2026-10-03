#!/usr/bin/env python3
"""Run the existing mail suites against a new contract module, serial port 8485."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[3]
a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False)
runner=r/'official_muse/prelim/tests/mail_run.py';module=r/'official_muse/incoming_mail.splash'
suites=[('contract','prelim/tests/mail_host_contract.splash'),('stability','prelim/tests/mail_stability.splash'),('pagination','prelim/tests/mail_pagination.splash'),('callbacks','prelim/tests/mail_callbacks.splash'),('monitor','ui_memory/tests/regression_mail_monitor.splash'),('incoming','ui_memory/tests/regression_incoming.splash'),('precached','prelim/tests/mail_precached.splash'),('paused-boot','prelim/tests/mail_paused_boot.splash'),('self-loop','prelim/tests/mail_self_loop.splash'),('idle','prelim/tests/mail_idle.splash')]
results=[]
for name,suite in suites:
    cmd=[sys.executable,str(runner),'--module',str(module),'--suite',str(r/'official_muse'/suite),'--out',str(a.out/name),'--timeout','90']
    code=subprocess.run(cmd,cwd=r).returncode
    results.append({'suite':name,'exit_code':code,'report':str(a.out/name/'report.json')})
    (a.out/'suite-index.json').write_text(json.dumps(results,indent=2)+'\n')
cmd=[sys.executable,str(r/'official_muse/prelim/tests/mail_restart.py'),'--module',str(module),'--out',str(a.out/'restart')]
code=subprocess.run(cmd,cwd=r).returncode
results.append({'suite':'restart','exit_code':code,'report':str(a.out/'restart/restart-report.json')})
(a.out/'suite-index.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(int(any(e['exit_code'] for e in results)))
