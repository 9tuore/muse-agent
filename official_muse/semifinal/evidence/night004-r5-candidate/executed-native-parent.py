#!/usr/bin/env python3
"""Root serial acceptance of the signed R4 candidate on fresh marked fixtures."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
L3=ROOT/'official_muse/semifinal/mail_integration/gpt02_recovery/night004/l3'
SRC=ROOT/'official_muse/app/source/main.splash'
SHA='caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
TEMPLATE=ROOT/'build/night-004/rc7-integrated-candidate-r5/kernel-config-template.json'
CASES={'full':('native_full_chain_probe.splash','native_restart_probe.splash'),
 'deny':('native_update_deny_probe.splash','native_update_deny_restart_probe.splash'),
 'cas':('native_cas_fault_probe.splash','native_cas_restart_probe.splash'),
 'delete':('native_delete_probe.splash','native_delete_restart_probe.splash')}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def execute(cmd,base,name):
 save(base/(name+'-command.json'),cmd)
 with (base/(name+'-command.stdout.log')).open('w') as o,(base/(name+'-command.stderr.log')).open('w') as e:
  p=subprocess.run(cmd,cwd=ROOT,stdout=o,stderr=e)
 assert p.returncode==0,(name,p.returncode)
for case in sys.argv[1:]:
 assert case in CASES
 base=ROOT/('build/night-004/native-caa99-'+case+'-central-r2')
 base.mkdir(exist_ok=False)
 kernel=base/'kernel-state';(kernel/'apps/.host').mkdir(parents=True)
 for p in (kernel/'FIXTURE_ONLY',kernel/'apps/.host/FIXTURE_ONLY'):p.write_text('NIGHT004 actual Kernel fixture only\n')
 cfg=json.loads(TEMPLATE.read_text());cfg['fixture_root']=str(kernel);save(base/'kernel-config.json',cfg)
 for phase,probe in zip(('initial','restart'),CASES[case]):
  prep=base/(phase+'-prepare')
  execute(['python3',str(L3/'prepare.py'),'--source',str(SRC),'--source-sha',SHA,'--probe',str(L3/probe),'--out',str(prep)],base,phase+'-prepare')
  cmd=['python3',str(L3/'run.py'),'--prepared',str(prep/'executed.splash'),'--runner',str(ROOT/'build/night-004/native-l3-central-r4/initial/vm-bin'),'--mail-binary',str(ROOT/'build/night-004/native-l3-central-r4/initial/mail-bin'),'--out',str(base/phase),'--kernel-bridge',str(ROOT/'official_muse/semifinal/calendar_integration/GPT01_NIGHT004/kernel_bridge/bridge.py'),'--kernel-test-binary',str(ROOT/'build/night-004/frozen-runtime-testbin-r8/shell-test-bin'),'--kernel-test-frozen','--kernel-binary',str(ROOT/'build/muse-integrated-0.4.0-rc6-standalone-r2/Muse.app/Contents/Resources/host-runtime/octos-kernel'),'--kernel-config',str(base/'kernel-config.json'),'--timeout-seconds','600']
  if phase=='restart':cmd+=['--state-root',str(base/'initial/state'),'--mail-root',str(base/'initial/mail-state')]
  if case=='deny':cmd+=['--calendar-mutation-approval','deny']
  if case=='cas':cmd+=['--calendar-owner-helper','/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-calendar-history/target/debug/gpt01-night004-external-owner','--authorize-external-owner-write']
  execute(cmd,base,phase)
  report=json.loads((base/phase/'report.json').read_text())
  checks=report.get('probe',{}).get('checks',{})
  print(case,phase,report['status'],len(checks),report.get('failed'),flush=True)
  assert report['status']=='PASS' and checks and all(checks.values())
