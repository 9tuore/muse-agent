#!/usr/bin/env python3
"""Reuse verified run_official_api; independent ROOT, status-only probe, clean owned quit."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[4]
CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
RUNNER=CENTRAL/'official_muse/semifinal/tests/run_official_api.py'
sys.dont_write_bytecode=True

def main():
    args=sys.argv[1:]
    out=Path(args[args.index('--out')+1]).resolve()
    port=int(args[args.index('--port')+1]);assert port==9695
    assert out.is_relative_to(ROOT/'build') and not out.exists()
    spec=importlib.util.spec_from_file_location('gpt02_existing_runner',RUNNER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=ROOT  # Only independent fixture bundle/jail/out, never central writes.
    original=subprocess.Popen; shutdown={}
    class Owned:
        def __init__(self,*a,**kw):
            assert kw['env'].get('MAKEPAD_HIDE_WINDOWS')=='1'
            self.child=original(*a,**kw);shutdown['pid']=self.child.pid
        def __getattr__(self,key):return getattr(self.child,key)
        def terminate(self):
            shutdown['method']='remote_quit'
            try:
                with urlopen('http://127.0.0.1:'+str(port)+'/s',timeout=2) as response:
                    assert json.loads(response.read()).get('pid')==self.child.pid
                with urlopen('http://127.0.0.1:'+str(port)+'/quit',timeout=2) as response:response.read()
            except Exception as error:
                shutdown.update(method='terminate_unclean',error=str(error));self.child.terminate()
        def kill(self):shutdown['method']='kill_unclean';self.child.kill()
        def wait(self,*a,**kw):
            result=self.child.wait(*a,**kw);shutdown['exit']=result;return result
    module.subprocess.Popen=Owned
    try:
        code=module.main()
    finally:
        module.subprocess.Popen=original
    report_path=out/'report.json';report=json.loads(report_path.read_text())
    errors=[line for line in (out/'runtime.log').read_text().splitlines() if '[E]' in line or 'script time budget exceeded' in line]
    report.update(owned_shutdown=shutdown,post_exit_runtime_errors=errors,
                  wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  reused_runner_path=str(RUNNER),independent_worktree=str(ROOT))
    if errors or shutdown.get('method')!='remote_quit' or shutdown.get('exit')!=0:
        report['status']='FAIL';report.setdefault('failed',[]).append('post_exit_errors_or_unclean');code=1
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report.get(key) for key in ('status','failed','error','owned_shutdown')},ensure_ascii=False))
    return code
if __name__=='__main__':raise SystemExit(main())
