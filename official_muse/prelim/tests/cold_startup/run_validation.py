#!/usr/bin/env python3
"""Exercise the shipped history validator in card-host; no external services."""
import argparse,hashlib,json,os,subprocess,time,shutil,re
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[4]
def main():
 p=argparse.ArgumentParser();p.add_argument('--host',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--host-cwd',type=Path,required=True);p.add_argument('--source',type=Path,default=ROOT/'official_muse/app/bundle');p.add_argument('--probe',type=Path,default=Path(__file__).parent/'chat_validation.splash');p.add_argument('--port',type=int,default=8477);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'bundle';shutil.copytree(a.source,bundle)
 source=(bundle/'main.splash').read_text();markers=list(re.finditer(r'^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)',source,re.M))
 if len(markers)!=1:raise RuntimeError('Expected exactly one verified startup marker')
 prefix=source[:markers[0].start()]
 (bundle/'main.splash').write_text(prefix+a.probe.read_text())
 manifest=json.loads((bundle/'manifest.json').read_text());manifest['integrity']['signature']=None;(bundle/'manifest.json').write_text(json.dumps(manifest))
 env=dict(os.environ,MAKEPAD_REMOTE=str(a.port));env.pop('MAKEPAD_HIDE_WINDOWS',None)
 with (a.out/'runtime.log').open('w') as log:
  proc=subprocess.Popen([str(a.host.resolve()),'--bundle',str(bundle.resolve()),'--app-data',str((a.out/'state').resolve()),'--allow-unsigned','--stamp','--size','640x420'],env=env,cwd=a.host_cwd,stdout=log,stderr=log)
  try:
   report=a.out/'state/muse-goals/cold-validation.json';until=time.monotonic()+20
   while not report.exists():
    if proc.poll() is not None or time.monotonic()>until:raise RuntimeError('Validator did not finish; preserve runtime.log')
    time.sleep(.1)
   data=json.loads(report.read_text());data['source_sha256']=hashlib.sha256(source.encode()).hexdigest();data['host_sha256']=hashlib.sha256(a.host.read_bytes()).hexdigest();(a.out/'report.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':sum(c['pass'] for c in data['cases']),'total':len(data['cases']),'source_sha256':data['source_sha256'],'calls':data['calls']}))
   assert all(c['pass'] for c in data['cases']),data
  finally:
   try:urlopen(f'http://127.0.0.1:{a.port}/quit',timeout=2).read()
   except Exception:proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
if __name__=='__main__':main()
