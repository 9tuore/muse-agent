#!/usr/bin/env python3
"""Own idle runtime only: lossless compression and identical-image COW copies."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,stat,subprocess
Q=Path(__file__).resolve().parent.parent;BASE=Q/'runtime';PRIVATE=BASE/'storage-maintenance';OUT=PRIVATE/'receipt.json'
EXCLUDED={'home','.host','profiles','keys','.git','official-cli','storage-maintenance','compression-temp','__pycache__'}
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def attrs(p):return subprocess.check_output(['/usr/bin/xattr','-lx',str(p)])
def meta(p):
 s=p.lstat();return {'sha256':digest(p),'mode':stat.S_IMODE(s.st_mode),'size':s.st_size,'uid':s.st_uid,'gid':s.st_gid,'mtime_ns':s.st_mtime_ns,'blocks':s.st_blocks,'inode':s.st_ino,'flags':s.st_flags,'nlink':s.st_nlink,'xattrs_sha256':hashlib.sha256(attrs(p)).hexdigest()}
def idle(paths):
 r=subprocess.run(['/usr/sbin/lsof','-nP','-t','--',*map(str,paths)],capture_output=True,timeout=15)
 return r.returncode==1 and not r.stdout and not r.stderr
def eligible(p):
 if EXCLUDED.intersection(p.relative_to(BASE).parts) or p.is_symlink():return False
 s=p.lstat();return stat.S_ISREG(s.st_mode) and s.st_nlink==1 and p.resolve().is_relative_to(BASE.resolve())
def main():
 assert not OUT.exists(),'Preserve previous private receipt'
 check=subprocess.run(['/usr/sbin/lsof','-nP','+D',str(BASE)],capture_output=True,timeout=30)
 assert check.returncode==1 and not check.stdout and not check.stderr,'Runtime open or lsof uncertain'
 files=[p for p in BASE.rglob('*') if p.is_file() and eligible(p)];PRIVATE.mkdir()
 run={'status':'RUNNING','started_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),'base':str(BASE),'excluded_components':sorted(EXCLUDED),'no_open_handles_initially':True,'eligible_allocated_bytes_before':sum(p.stat().st_blocks*512 for p in files),'free_before':shutil.disk_usage(BASE).free,'tests_rerun':False,'compression':[],'cow':[],'skipped':[]}
 def save():
  t=OUT.with_suffix('.pending');t.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n');t.replace(OUT)
 save()
 for p in files:
  if p.suffix not in {'.json','.splash','.log','.txt','.ndjson'} or p.stat().st_size<65536 or p.stat().st_flags&32:continue
  before=meta(p)
  if shutil.disk_usage(BASE).free<before['size']*2+64*1024*1024:run['status']='STOPPED_TEMP_SPACE';save();return
  if not idle([p]):run['skipped'].append({'path':str(p.relative_to(BASE)),'reason':'OPEN_OR_UNCERTAIN'});continue
  t=PRIVATE/'compression-pending';assert not t.exists()
  try:
   subprocess.run(['/usr/bin/ditto','--hfsCompression','--noclone',str(p),str(t)],check=True,capture_output=True,timeout=60);copy=meta(t);current=meta(p)
   same=['sha256','mode','size','uid','gid','mtime_ns'];assert all(copy[k]==before[k] for k in same) and current==before and copy['nlink']==1
   if copy['blocks']>=before['blocks']:run['skipped'].append({'path':str(p.relative_to(BASE)),'reason':'NO_BLOCKS_GAIN'});continue
   if not idle([p]):run['skipped'].append({'path':str(p.relative_to(BASE)),'reason':'OPEN_BEFORE_REPLACE'});continue
   os.replace(t,p);after=meta(p);assert all(after[k]==before[k] for k in same)
   run['compression'].append({'path':str(p.relative_to(BASE)),'before':before,'after':after,'saved_allocated_bytes':(before['blocks']-after['blocks'])*512,'compression_xattrs_may_change':'native decmpfs/resource metadata; logical bytes and identity fields above unchanged'})
  finally:
   if t.exists():t.unlink() # only redundant scratch copy; never unique evidence
  save()
 unique={}
 for p in files:
  if p.suffix.lower() not in {'.png','.jpg','.jpeg','.svg'} or p.stat().st_flags!=0:continue
  before=meta(p);key=tuple(before[k] for k in ['sha256','mode','size','uid','gid','xattrs_sha256'])
  if key not in unique:unique[key]=p;continue
  source=unique[key]
  if not idle([source,p]):run['skipped'].append({'path':str(p.relative_to(BASE)),'reason':'IMAGE_OPEN_OR_UNCERTAIN'});continue
  if shutil.disk_usage(BASE).free<before['size']*2+64*1024*1024:run['status']='STOPPED_TEMP_SPACE';save();return
  t=PRIVATE/'clone-pending';assert not t.exists();source_before=meta(source)
  try:
   assert attrs(source)==attrs(p) and source.stat().st_dev==p.stat().st_dev
   subprocess.run(['/bin/cp','-c','-p',str(source),str(t)],check=True,capture_output=True,timeout=60);s=p.stat();os.utime(t,ns=(s.st_atime_ns,s.st_mtime_ns));copy=meta(t)
   fields=['sha256','mode','size','uid','gid','mtime_ns','flags','xattrs_sha256'];assert all(copy[k]==before[k] for k in fields) and copy['nlink']==1 and meta(p)==before and meta(source)==source_before
   if not idle([source,p]):run['skipped'].append({'path':str(p.relative_to(BASE)),'reason':'IMAGE_OPEN_BEFORE_REPLACE'});continue
   os.replace(t,p);after=meta(p);assert all(after[k]==before[k] for k in fields)
   run['cow'].append({'path':str(p.relative_to(BASE)),'source':str(source.relative_to(BASE)),'before':before,'after':after,'method':'cp -c -p same APFS volume; stat_blocks alone does not measure shared extents'})
  finally:
   if t.exists():t.unlink() # redundant temporary only
  save()
 # Independent final reread of each replaced private carrier.
 for row in run['compression']+run['cow']:
  now=meta(BASE/row['path']);assert all(now[k]==row['after'][k] for k in ['sha256','mode','size','uid','gid','mtime_ns','xattrs_sha256'])
 run.update(status='COMPLETE_LOSSLESS_RUNTIME_OPTIMIZATION',finished_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),compressed_count=len(run['compression']),compression_saved_allocated_bytes=sum(x['saved_allocated_bytes'] for x in run['compression']),cow_replaced_count=len(run['cow']),cow_duplicate_logical_bytes=sum(x['before']['size'] for x in run['cow']),free_after=shutil.disk_usage(BASE).free,global_free_change_not_task_attributable=True,all_replaced_final_hash_metadata_verified=True)
 save();print(json.dumps({k:run[k] for k in ['status','compressed_count','compression_saved_allocated_bytes','cow_replaced_count','cow_duplicate_logical_bytes','free_before','free_after']},ensure_ascii=False))
if __name__=='__main__':main()
