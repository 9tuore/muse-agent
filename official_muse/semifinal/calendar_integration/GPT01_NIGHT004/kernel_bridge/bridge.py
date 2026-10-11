#!/usr/bin/env python3
"""Filter actual test-driver JSON frames; retain full original harness logs."""
import argparse,json,os,subprocess,sys,threading
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--test-binary',type=Path,required=True);P.add_argument('--kernel',type=Path,required=True);P.add_argument('--config',type=Path,required=True)
a=P.parse_args();config=json.loads(a.config.read_text());root=Path(config['fixture_root']).resolve();assert root.joinpath('FIXTURE_ONLY').is_file()
env={**os.environ,'OCTOS_SHELL_TEST_KERNEL':str(a.kernel.resolve()),'NIGHT004_KERNEL_BRIDGE_CONFIG':str(a.config.resolve()),'NIGHT004_KERNEL_BRIDGE_MODEL':str(Path(__file__).with_name('plan_model.py').resolve())}
name='host_tools::real_kernel_tests::night004_kernel_jsonl_bridge_fixture_driver'
with (root/'bridge-harness-stderr.log').open('a') as err,(root/'bridge-harness-stdout.log').open('a') as raw:
 p=subprocess.Popen([str(a.test_binary.resolve()),'--exact',name,'--ignored','--nocapture','--test-threads=1'],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1)
 def forward():
  try:
   for line in sys.stdin:p.stdin.write(line);p.stdin.flush()
  except BrokenPipeError:pass
  finally:
   try:p.stdin.close()
   except BrokenPipeError:pass
 threading.Thread(target=forward,daemon=True).start()
 count=0
 for line in p.stdout:
  raw.write(line);raw.flush();marker='NIGHT004_BRIDGE_JSON '
  if marker in line:
   payload=line.split(marker,1)[1].strip();json.loads(payload);print(payload,flush=True);count+=1
 code=p.wait()
 if code or not count:raise SystemExit(code or 2)
