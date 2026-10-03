#!/usr/bin/env python3
"""Run existing real Shell layout assertions; retry read-only transient frame capture."""
import sys,time,json,hashlib
from pathlib import Path
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase2/tests'))
import live_shell_layout
from remote import Remote
ROOT=Path(__file__).resolve().parents[3]
c=json.loads((ROOT/'official_muse/round2/candidate.json').read_text())
assert hashlib.sha256((ROOT/'official_muse/app/build/round2/isolated-apps/muse-goals/bundle/main.splash').read_bytes()).hexdigest()==c['bundle_files_sha256']['main.splash']
shot=Remote.shot

def capture(self,path):
    for attempt in range(4):
        try:return shot(self,path)
        except HTTPError as e:
            if e.code!=404 or attempt==3:raise
            time.sleep(.5)
Remote.shot=capture
sys.argv=[sys.argv[0],'8490',str(ROOT/'official_muse/app/build/round2/live-layout'), '--version',c['bundle_version']]
live_shell_layout.main()
p=ROOT/'official_muse/app/build/round2/live-layout/report.json';r=json.loads(p.read_text());r['candidate']=c['muse_commit'];r['test_kind']='SHELL_LIVE';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
