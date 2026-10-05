#!/usr/bin/env python3
"""One new full-capacity correction/recovery variant, no real external service."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=ROOT/'official_muse/rc/improvement-20261005-r1/readable-rc27-r1'
HOST=ROOT/'official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path);parser.add_argument('--out',default='capacity-r1');parser.add_argument('--probe',type=Path,default=HERE/'capacity.splash');args=parser.parse_args()
    if not args.source:assert sha(SOURCE/'main.splash')=='96ebb52f70a6cbf2050b14468e2eef2d8334e4cd5c4db18539e43c5bd67b4c05'
    assert sha(HOST)=='52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837'
    out=HERE/args.out;assert out.parent==HERE and not out.exists();out.mkdir()
    readable=out/'readable';shutil.copytree(SOURCE,readable)
    if args.source:shutil.copyfile(args.source,readable/'main.splash')
    compact=out/'compact'
    result=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/compact_bundle.py'),'--source',str(readable),'--out',str(compact)],capture_output=True,text=True,check=True)
    (out/'compact-binding.json').write_text(result.stdout)
    if not args.source:assert sha(compact/'main.splash')=='e5461fd7ecc1b32ee0e82019ac478b1f691d5137f18d2ac41a1d7e4f6ecd18af'
    os.environ['MUSE_CARD_HOST']=str(HOST)
    sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'));sys.path.insert(0,str(ROOT/'official_muse/rc/core_chain'))
    import regression_run
    from run_calendar_clarification import restart
    observed={'time':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'uptime':subprocess.run(['uptime'],capture_output=True,text=True,check=True).stdout.strip()}
    ps=subprocess.run(['ps','-A','-o','pid,pcpu,comm'],capture_output=True,text=True,check=True).stdout.splitlines()
    observed['top_cpu_comm']=sorted(ps[1:],key=lambda s:float(s.split()[1]),reverse=True)[:10]
    report={'source_sha256':sha(readable/'main.splash'),'compact_sha256':sha(compact/'main.splash'),'host_sha256':sha(HOST),'real_model':False,'real_external_actions':False,'default_budget_unchanged':True,'runtime_note':'Older locked fixture Card5276, not current Root native Host1d7d. Render/set_page/calendar_enabled/mail_redraw/widgets/transport instrumented by existing harness.','start_environment':observed}
    try:
        first=regression_run.run_suite('mail_calendar_chain',(compact/'main.splash').read_text(),compact,out/'first',8509,args.probe)
        report['initial']=first
        if not first['failed']:report['restart']=restart(out/'first',out)
        report['status']='FIXTURE_PASS' if not first['failed'] and not report.get('restart',{}).get('failed') else 'FAIL'
    except Exception as exc:
        report['status']='ERROR';report['error']=str(exc)
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return int(report['status']!='FIXTURE_PASS')

if __name__=='__main__':raise SystemExit(main())
