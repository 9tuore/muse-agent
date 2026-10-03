#!/usr/bin/env python3
"""Exclusive lexical SDK link swap; restore it on success, failure or interruption."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,time
r=Path(__file__).resolve().parents[3];e=r/'official_muse/prelim/evidence/startup-host';i=json.loads((e/'source-index.json').read_text());link=Path(i['lexical_link']);snap=Path(i['snapshot_sdk']);matched=link.parents[1];target=snap.parent/'target';lock=e/'sdk-build-exclusive.lock'
def active_compilers():
 text=subprocess.check_output(['ps','-axo','pid=,comm='],text=True)
 return [line.strip() for line in text.splitlines() if line.strip().split(None,1)[-1].endswith(('/cargo','/rustc'))]
if active_compilers():raise RuntimeError('Other compilation active; SDK link left untouched')
assert str(link.readlink())==i['original_symlink_target']
assert hashlib.sha256((link/'widgets/src/splash.rs').read_bytes()).hexdigest()==i['baseline_splash_sha256']
fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,str(os.getpid()).encode());os.close(fd)
cmd=['cargo','build','-j','2','--locked','--offline','--release','--manifest-path',str(matched/'Cargo.toml'),'--target-dir',str(target),'-p','octosense','--bin','octosense','--no-default-features','--features','app-hub']
logpath=e/'build.log';proc=None;result={'command':cmd,'cwd':str(matched),'source_snapshot':str(snap),'symlink_restored':False}
def swap(value):
 temp=link.with_name('makepad.startup-theme-swap');os.symlink(value,temp);os.replace(temp,link)
def interrupted(signum,frame):raise KeyboardInterrupt
signal.signal(signal.SIGTERM,interrupted)
try:
 if active_compilers():raise RuntimeError('Compilation started before SDK swap; aborted')
 swap(str(snap));result['snapshot_link_active']=str(link.readlink())
 with logpath.open('w') as log:
  proc=subprocess.Popen(cmd,cwd=matched,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  unexpected=[]
  while proc.poll() is None:
   time.sleep(.5)
   text=logpath.read_text()
   # These unchanged foundational crates should remain cached. Stop before
   # a whole SDK rebuild if relocation invalidates their identity.
   unexpected=[line for line in text.splitlines() if 'Compiling ' in line and any(' '+x+' ' in line for x in ['makepad-platform','makepad-script','makepad-draw'])]
   if unexpected:
    result['status']='FULL_REBUILD_REQUIRES_REPORT';result['unexpected_rebuild']=unexpected
    print(json.dumps({'status':result['status'],'unexpected':unexpected}),flush=True)
    break
  if not unexpected:
   result['exit_code']=proc.wait();result['status']='BUILD_PASS' if proc.returncode==0 else 'BUILD_FAILED'
finally:
 if proc is not None and proc.poll() is None:
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 if link.is_symlink() and str(link.readlink())==str(snap):swap(i['original_symlink_target'])
 result['symlink_restored']=str(link.readlink())==i['original_symlink_target']
 lock.unlink()
 (e/'build-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False),flush=True)
assert result['symlink_restored']
raise SystemExit(0 if result.get('status')=='BUILD_PASS' else 2)
