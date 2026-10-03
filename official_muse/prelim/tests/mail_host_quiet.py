#!/usr/bin/env python3
"""Observe actual watch-file metadata across two quiet modern Host polls."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--module',type=Path);a=p.parse_args()
r=Path(__file__).resolve().parents[3];a.out=a.out.resolve()
module=(a.module or r/'official_muse/incoming_mail.splash').resolve(); runner=r/'official_muse/prelim/tests/mail_run.py'
proc=subprocess.Popen([sys.executable,str(runner),'--module',str(module),'--suite',str(Path(__file__).with_suffix('.splash')),'--out',str(a.out)],cwd=r)
jail=a.out/'state/muse-goals';checkpoint=jail/'quiet-checkpoint.json';watch=jail/'mail-watch.json'
deadline=time.monotonic()+45
while not checkpoint.exists():
    if proc.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Quiet checkpoint missing; original logs retained')
    time.sleep(.01)
if (jail/'probe.json').exists(): raise RuntimeError('Observer missed polling window; no unchanged-write claim')
before=watch.stat().st_mtime_ns;content=watch.read_bytes();code=proc.wait(timeout=50)
after=watch.stat().st_mtime_ns
result={'kind':'FIXTURE_REAL_WATCH_FILE_METADATA','mtime_before_ns':before,'mtime_after_ns':after,'unchanged_mtime':before==after,'unchanged_bytes':content==watch.read_bytes(),'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'runner_exit_code':code,'real_mail':False}
result['passed']=int(result['unchanged_mtime'])+int(result['unchanged_bytes']);result['failed']=[k for k in ['unchanged_mtime','unchanged_bytes'] if not result[k]]
(a.out/'quiet-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
raise SystemExit(int(code!=0 or bool(result['failed'])))
