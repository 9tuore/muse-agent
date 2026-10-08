#!/usr/bin/env python3
"""Summarize actual one-round rc16 matrix without recategorizing failures."""
from pathlib import Path
import json,hashlib,re,statistics,datetime
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
v=json.loads((Q/'final-rc16-cold10-reopen5-r1/report.json').read_text())
assert len(v['cold'])==10 and len(v['reopen'])==5, 'Matrix incomplete'
expected_source='dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4';expected_host='276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638'
assert v['source_sha256']==expected_source and v['host_sha256']==expected_host
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
j=Q/'runtime/final-rc16-r1/private/apps/muse-goals';seed=Q/'runtime/seed/private/apps/muse-goals';rootbundle=ROOT/'official_muse/app/build/ui-memory-20261003/7h-live-candidate-r9/bundle'
core_diff={p.name:{'seed':sha(p),'final':sha(j/p.name)} for p in seed.iterdir() if p.is_file() and p.name not in ['activity.json','activity.backup.json'] and sha(p)!=sha(j/p.name)}
bundle_diff={p.relative_to(rootbundle).as_posix():{'root':sha(p),'loaded':sha(j/'bundle'/p.relative_to(rootbundle))} for p in rootbundle.rglob('*') if p.is_file() and sha(p)!=sha(j/'bundle'/p.relative_to(rootbundle))}
records=[];errors=[];chunk=[]
for mode in ['cold','reopen']:
 for run in v[mode]:
  d=Q/'final-rc16-cold10-reopen5-r1'/(mode+'-'+f"{run['index']:02d}");log=json.loads((d/'log.json').read_text())['l'];bad=[x for x in log if '[E]' in x or 'budget exceeded' in x or 'source preparation failed' in x or 'no root view' in x];errors.extend(bad)
  images=[d/'visible.png',d/'memory-visible.png'];image_valid=all(p.is_file() and p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' for p in images)
  chunk += [float(m.group(1)) for line in log if (m:=re.search(r'max_chunk_ms=([0-9.]+)',line))]
  records.append({'mode':mode,'index':run['index'],'pass':run['pass'],'pid':run.get('pid'),'interactive_seconds':run.get('first_interactive_seconds'),'input_editable':run.get('input_editable'),'core_state_equal':run.get('core_state_equal'),'model_ledger_equal':run.get('model_ledger_equal'),'activity_increment_valid':run.get('activity_increment_valid'),'activity_backup_valid':run.get('activity_backup_valid'),'error':run.get('error'),'evidence':d.relative_to(Q).as_posix(),'png_valid':image_valid,'png_sha256':{p.name:sha(p) for p in images}})
all_pass=all(x['pass'] and x['png_valid'] for x in records) and not errors and not core_diff and not bundle_diff
coldpids=[x.get('pid') for x in v['cold']];reopenpids=[x.get('pid') for x in v['reopen']]
all_pass=all_pass and len(set(coldpids))==10 and None not in coldpids and len(set(reopenpids))==1 and reopenpids[0]==coldpids[-1]
times=[x['first_interactive_seconds'] for x in v['cold'] if 'first_interactive_seconds' in x]
s={'status':'PASS_SINGLE_ROUND_10_COLD_5_REOPEN' if all_pass else 'FAIL','completed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),'version':'0.3.27-rc16','source_sha256':expected_source,'host_sha256':expected_host,'requested_counts':{'cold':10,'reopen':5},'pass_counts':{mode:sum(x['pass'] for x in v[mode]) for mode in ['cold','reopen']},'single_uninterrupted_15_of_15':all_pass,'cold_distinct_pids':len(set(coldpids)),'reopen_same_pid':len(set(reopenpids))==1,'core_seed_file_differences':core_diff,'loaded_vs_root_signed_bundle_differences':bundle_diff,'runtime_errors':errors,'max_observed_source_prep_chunk_ms':max(chunk) if chunk else None,'cold_interactive_seconds':{'min':min(times),'max':max(times),'median':statistics.median(times)} if times else None,'strict_all_files_equal':False,'activity':'Authorized calendar permission log increments only; original Activity prefix and backup relation checked on every run.','official_signed_gate':'official-signed-rc16-r1/report.json','storage_reuse':'storage-reuse-rc16.json: unchanged restore closure, old8cases remain oldHost evidence','root_owned_behavior':'Specific newChat project inheritance and local-project model recall acceptance handled by Root; no model called here.','prior_rc15':'FINAL_SUMMARY.json retains rc15 identity; no rc15 run counted here.','device':'DEVICE_NOT_TESTED','runs':records,'scope':'Synthetic visible desktop cold/reopen acceptance; not model backend, external Mail/Calendar writes, user system grants or upstream extension acceptance.'}
(Q/'FINAL_SUMMARY_RC16.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:s[k] for k in ['status','pass_counts','single_uninterrupted_15_of_15','cold_interactive_seconds','core_seed_file_differences','loaded_vs_root_signed_bundle_differences','max_observed_source_prep_chunk_ms']},ensure_ascii=False))
