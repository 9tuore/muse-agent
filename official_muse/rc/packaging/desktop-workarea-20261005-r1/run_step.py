#!/usr/bin/env python3
import hashlib,json,os,shutil,signal,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=Path('/private/tmp/muse-morning-clean-019dc303-20261005/checkout')
SDK=CACHE/'vendor/octosense'
ENV={k:os.environ[k] for k in ['PATH','HOME','RUSTUP_HOME'] if k in os.environ}
ENV.update(CARGO_HOME=str(CACHE.parent/'cargo-home'),CARGO_TARGET_DIR=str(CACHE/'build/clean-target'),CARGO_NET_OFFLINE='true',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1',GIT_TERMINAL_PROMPT='0',LC_ALL='C',TZ='UTC')
RESERVE=600*1024**2
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(name,command,cwd=SDK):
 log=HERE/(name+'.log')
 assert not log.exists()
 assert Path(ENV['CARGO_HOME']).is_dir()
 assert shutil.disk_usage(HERE).free>RESERVE
 start=time.monotonic()
 guard=None
 with log.open('x') as out:
  process=subprocess.Popen(command,cwd=cwd,env=ENV,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  while process.poll() is None:
   if shutil.disk_usage(HERE).free<=RESERVE:
    guard='CAPACITY_RESERVE_600MiB'
    os.killpg(process.pid,signal.SIGTERM)
    try:process.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    break
   time.sleep(2)
 result=dict(name=name,command=command,cwd=str(cwd),exit_code=process.returncode,seconds=time.monotonic()-start,guard_stop=guard,log=str(log),log_sha256=sha(log),incremental_not_cold_build=True,free_bytes_after=shutil.disk_usage(HERE).free)
 (HERE/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
 return result
