#!/usr/bin/env python3
"""Continue only after the recorded single-file compression probe proved safe."""
import datetime,json,stat,os
from compress_evidence import Q,TMP,eligible,compress,inventory
receipt=Q/'compression/batch-receipt.json';assert not receipt.exists()
probe=json.loads((Q/'compression/probe-large.json').read_text());assert probe['replaced'] and probe['after']['blocks']<probe['before']['blocks']
proof=Q/probe['path'];now=inventory(proof);assert all(now[k]==probe['after'][k] for k in ['sha256','mode','size','blocks','uid','gid','mtime_ns'])
files=sorted([p for p in Q.rglob('*') if p.is_file() and eligible(p)],key=lambda p:p.stat().st_blocks,reverse=True)
run={'status':'RUNNING','started_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),'verified_probe':'probe-large.json','scope':'Only owned closed single-link JSON/log/txt evidence. No test runs, verdict edits, unique evidence removal, source/candidate/PNG/runtime changes.','entries':[],'eligible_files':len(files)}
def save():
 tmp=receipt.with_suffix('.pending');tmp.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n');tmp.replace(receipt)
save()
for i,p in enumerate(files):
 if p.stat().st_flags & 32:
  result={'path':p.relative_to(Q).as_posix(),'replaced':False,'reason':'ALREADY_FILESYSTEM_COMPRESSED'}
 else:result=compress(p)
 run['entries'].append(result);save()
 if result.get('reason')=='TEMP_SPACE_INSUFFICIENT':run['status']='STOPPED_TEMP_SPACE';break
 if (i+1)%25==0:print(json.dumps({'processed':i+1,'saved_bytes':sum(e.get('saved_bytes',0) for e in run['entries'])}),flush=True)
else:run['status']='COMPLETE'
run['replaced_count']=sum(e['replaced'] for e in run['entries']);run['batch_saved_bytes']=sum(e.get('saved_bytes',0) for e in run['entries']);run['total_saved_bytes_with_probe']=run['batch_saved_bytes']+probe['saved_bytes'];run['finished_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds');save();print(json.dumps({k:run[k] for k in ['status','replaced_count','batch_saved_bytes','total_saved_bytes_with_probe']}),flush=True)
