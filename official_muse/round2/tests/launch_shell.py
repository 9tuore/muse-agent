#!/usr/bin/env python3
"""Launch the existing approved packaged host into one explicit local profile."""
import argparse
from pathlib import Path
import subprocess,time,sys
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase2/tests'))
from remote import Remote
p=argparse.ArgumentParser();p.add_argument('port',type=int);p.add_argument('--home',type=Path,required=True);p.add_argument('--apps',type=Path,required=True);p.add_argument('--mirror',type=Path,required=True);p.add_argument('--demo',action='store_true');p.add_argument('--restart',action='store_true');a=p.parse_args()
r=Remote(a.port)
if a.restart:
    r.request('/quit')
    for i in range(100):
        try:urlopen(r.base+'/s',timeout=.3).read();time.sleep(.1)
        except OSError:break
    else:raise RuntimeError('old Shell still running')
app=Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/muse-calendar-test/OctoSense Muse 中文版 0.2.10-r2.app')
cmd=['open','-n']
for k,v in {'OCTOSENSE_HOME':a.home.resolve(),'OCTOSENSE_APP_DATA':a.apps.resolve(),'OCTOSENSE_HUB':a.mirror.resolve(),'OCTOSENSE_HUB_ANCHOR':'3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840','MAKEPAD_REMOTE':a.port,'MAKEPAD_APP_CONFIG':'{"mail_demo":true}' if a.demo else '{}'}.items():cmd+=['--env',f'{k}={v}']
cmd +=[str(app),'--args','--test-action','launch-apphub'];subprocess.run(cmd,check=True)
for i in range(120):
    try:r.find('已安装');break
    except (AssertionError,OSError):time.sleep(.25)
else:raise RuntimeError('App Hub missing')
print('Shell ready',a.port,flush=True)
