#!/usr/bin/env python3
"""One existing real card-host fixture runner; no new runtime or actual services."""
import argparse,hashlib,json,os,shutil,sys,threading,time
from urllib.request import urlopen
from pathlib import Path
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[2]
p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--out',required=True);p.add_argument('--probes',nargs='+',required=True);p.add_argument('--data',nargs='*',default=[]);p.add_argument('--native-digest-links',action='store_true');p.add_argument('--corrupt-preserve-write-blocker',action='store_true');p.add_argument('--host',required=True);a=p.parse_args()
os.environ['MUSE_CARD_HOST']=str(Path(a.host).resolve(strict=True));sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'));sys.dont_write_bytecode=True
import regression_run as r
out=OWN/a.out;out.mkdir(exist_ok=False);base=out/'source-bundle';shutil.copytree(ROOT/a.bundle,base);source=(base/'main.splash').read_text()
data_files=[]
for relative in a.data:
 snapshot=out/Path(relative).name;shutil.copy2(OWN/relative,snapshot);data_files.append(snapshot)
original=r.subprocess.Popen
observers=[]
def visible_popen(command,*args,**kwargs):
 state=Path(command[command.index('--app-data')+1])/'muse-goals'
 state.mkdir(parents=True,exist_ok=True)
 for f in data_files:shutil.copy2(f,state/f.name)
 if a.native_digest_links:
  if not (state/'native-utf8.bin').is_file():raise RuntimeError('Synthetic native-utf8 fixture missing')
  (state/'native-digest-symlink.bin').symlink_to('native-utf8.bin')
  (state/'native-digest-symlink-dir').symlink_to('.',target_is_directory=True)
 if a.corrupt_preserve_write_blocker:
  case=json.loads((state/'preserve-case.json').read_text())
  name=case['preserved_name']
  if not case['write_blocker_entry_cap'] or '/' in name or '\\' in name or name in ('.','..'):raise RuntimeError('Invalid synthetic preserve blocker')
  count=len(list(state.iterdir()))
  if count>=256:raise RuntimeError('Unexpected fixture entry count')
  for index in range(256-count):(state/('a3-preserve-cap-fill-'+str(index).zfill(3))).write_bytes(b'')
 kwargs['env'].pop('MAKEPAD_HIDE_WINDOWS',None);kwargs['env'].pop('MAKEPAD_FOCUS',None)
 proc=original(command,*args,**kwargs)
 def observe():
  time.sleep(2)
  for route in ['s','g']:
   try:
    response=urlopen('http://127.0.0.1:8510/'+route,timeout=2).read()
    (state.parents[1]/('remote-'+route+'.json')).write_bytes(response)
   except Exception as error:(state.parents[1]/('remote-'+route+'.error.txt')).write_text(str(error))
 thread=threading.Thread(target=observe);thread.start();observers.append(thread)
 return proc
report={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'host_sha256':hashlib.sha256(r.existing.HOST.read_bytes()).hexdigest(),'data_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in data_files},'native_digest_links':a.native_digest_links,'results':{},'boundary':'Pre-final source snapshot; actual production functions in existing card-host fixture runner, synthetic data, original services replaced. No real model or OS actions.'}
for name in a.probes:
 r.subprocess.Popen=visible_popen
 try:result=r.run_suite(name,source,base,out/name,8510,OWN/(name+'.splash'))
 except Exception as error:result={'status':'ERROR','error':str(error)}
 finally:r.subprocess.Popen=original
 for observer in observers:observer.join()
 observers.clear()
 report['results'][name]=result;(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(name,json.dumps(result,ensure_ascii=False),flush=True)
