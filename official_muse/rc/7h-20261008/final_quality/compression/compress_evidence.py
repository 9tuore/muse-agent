#!/usr/bin/env python3
"""Lossless filesystem compression for closed, single-link text evidence only."""
import argparse,datetime,hashlib,json,os,stat,subprocess,tempfile
from pathlib import Path
Q=Path(__file__).resolve().parent.parent
RECEIPT=Q/'compression/receipt.json'
TMP=Q/'runtime/compression-temp'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def closed(p):
 try:r=subprocess.run(['/usr/sbin/lsof','-t','--',str(p)],capture_output=True,text=True,timeout=8)
 except subprocess.TimeoutExpired:return False,'lsof_timeout'
 if r.returncode==1 and not r.stdout.strip() and not r.stderr.strip():return True,'lsof_no_open_handles'
 return False,'opened_or_lsof_uncertain'
def inventory(p):
 s=p.lstat();return dict(sha256=digest(p),mode=stat.S_IMODE(s.st_mode),size=s.st_size,blocks=s.st_blocks,allocated_bytes=s.st_blocks*512,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,mtime_ns=s.st_mtime_ns,inode=s.st_ino,flags=s.st_flags)
def eligible(p):
 if p.suffix.lower() not in ['.json','.log','.txt']:return False
 if any(x in p.relative_to(Q).parts for x in ['runtime','__pycache__','compression','bundle']):return False
 if not p.resolve().is_relative_to(Q.resolve()):return False
 s=p.lstat();return stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not p.is_symlink()
def compress(p):
 entry={'path':p.relative_to(Q).as_posix(),'replaced':False}
 if not eligible(p):entry['reason']='ineligible';return entry
 ok,why=closed(p)
 if not ok:entry['reason']=why;return entry
 before=inventory(p);entry['before']=before
 free=os.statvfs(Q).f_bavail*os.statvfs(Q).f_frsize
 if free<max(before['size']*2+16*1024*1024,32*1024*1024):entry['reason']='TEMP_SPACE_INSUFFICIENT';return entry
 fd,name=tempfile.mkstemp(prefix='ditto-',dir=TMP);os.close(fd);tmp=Path(name);tmp.unlink() # only empty, newly-created task scratch placeholder
 try:
  r=subprocess.run(['/usr/bin/ditto','--hfsCompression','--noclone',str(p),str(tmp)],capture_output=True,text=True,timeout=60)
  entry['ditto_exit']=r.returncode
  if r.returncode:entry['reason']='ditto_failed';entry['error']=r.stderr[:400];return entry
  after=inventory(tmp);entry['temporary']=after
  required=['sha256','mode','size','uid','gid','mtime_ns']
  if any(before[k]!=after[k] for k in required) or after['nlink']!=1:entry['reason']='METADATA_OR_HASH_MISMATCH';return entry
  if after['blocks']>=before['blocks']:entry['reason']='NO_BLOCKS_SAVING';return entry
  ok,why=closed(p)
  current=inventory(p)
  if not ok or current!=before:entry['reason']='SOURCE_OPENED_OR_CHANGED';return entry
  os.replace(tmp,p)
  final=inventory(p);entry['after']=final
  assert all(final[k]==before[k] for k in required) and final['blocks']<before['blocks']
  entry.update(replaced=True,reason='VERIFIED_ATOMIC_REPLACEMENT',saved_bytes=before['allocated_bytes']-final['allocated_bytes'])
  return entry
 finally:
  if tmp.exists():tmp.unlink() # only a redundant new scratch copy; original evidence never deleted

def main():
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args();assert not RECEIPT.exists(),'Use one immutable receipt per execution'
 TMP.mkdir(parents=True,exist_ok=True)
 files=sorted((p for p in Q.rglob('*') if p.is_file() and eligible(p)),key=lambda p:p.stat().st_size)
 probes=[p for p in files if 8192<=p.stat().st_size<=65536 and p.stat().st_blocks*512>=8192];assert probes,'No safe small probe available'
 run={'started_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),'scope':'Owned closed JSON/log/txt evidence only; excludes runtime, candidate/bundle copies, screenshots and source; no new tests or PASS claims.','method':'ditto --hfsCompression --noclone; verified same SHA/mode/size/owner/mtime and lower st_blocks before atomic replacement','eligible_count':len(files),'eligible_before_allocated_bytes':sum(p.stat().st_blocks*512 for p in files),'entries':[],'status':'PROBE_RUNNING'}
 def save():
  t=RECEIPT.with_suffix('.pending');t.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n');t.replace(RECEIPT)
 save();probe=compress(probes[0]);run['probe']=probe;run['entries'].append(probe);save()
 if not probe['replaced']:run['status']='STOPPED_PROBE_NO_SAFE_GAIN';save();print(json.dumps({'status':run['status'],'probe':probe},ensure_ascii=False));return
 if not a.apply:run['status']='PROBE_VERIFIED_ONLY';save();print(json.dumps({'status':run['status'],'saved_bytes':probe['saved_bytes']}));return
 run['status']='APPLYING';save()
 for source in files:
  if source==probes[0]:continue
  result=compress(source);run['entries'].append(result)
  if result.get('reason')=='TEMP_SPACE_INSUFFICIENT':run['status']='STOPPED_TEMP_SPACE';save();break
  save()
 else:run['status']='COMPLETE_LOSSLESS_COMPRESSION'
 run['replaced_count']=sum(e['replaced'] for e in run['entries']);run['saved_bytes']=sum(e.get('saved_bytes',0) for e in run['entries']);run['finished_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds');save();print(json.dumps({k:run[k] for k in ['status','eligible_count','replaced_count','saved_bytes']},ensure_ascii=False))
if __name__=='__main__':main()
