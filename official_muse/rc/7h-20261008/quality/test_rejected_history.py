#!/usr/bin/env python3
"""Bad final entry cannot become writable history; bytes retained, no actions."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'official_muse/phase2/tests'));from remote import Remote
sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'));from visual_capture import navigate
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();c=a.candidate.resolve();assert c.is_relative_to(Q/'runtime');a.out=a.out.resolve();assert a.out.is_relative_to(Q);a.out.mkdir(parents=True,exist_ok=False)
m=json.loads((c/'candidate.json').read_text());assert m['test_case']=='bad-tail';jail=c/'private/apps/muse-goals';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
protected={f.name:sha(f) for f in jail.glob('*.json')};r=Remote(8494);report={'source_sha256':m['source_sha256'],'host_sha256':m['host_sha256'],'kind':'SYNTHETIC_REJECT_BAD_LAST_ENTRY_VISIBLE_SHELL','pass':False,'protected_before':protected};began=time.monotonic()
try:
 proc=subprocess.run([sys.executable,str(Q/'launch_quality.py'),'--candidate',str(c),'--port','8494'],text=True,capture_output=True,timeout=40);(a.out/'launch.txt').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
 r.click('打开');deadline=time.monotonic()+25
 while True:
  labels=[w.get('t','') for w in r.widgets() if w.get('ty')=='Label']
  if any('对话记录不可读，原文件已保留' in x for x in labels):break
  if time.monotonic()>deadline:raise AssertionError('Missing fail-closed notice')
  time.sleep(.2)
 report['reject_notice']=True
 assert not any('合成历史 15/15' in x for x in labels),'Invalid history was exposed'
 r.click('＋ 新对话');time.sleep(.2)
 assert not any('合成历史 15/15' in w.get('t','') for w in r.widgets()),'Rejected history exposed'
 report['new_dialog_did_not_overwrite']=all(sha(jail/n)==h for n,h in protected.items())
 assert report['new_dialog_did_not_overwrite']
 navigate(r,'记忆');r.wait_for('汇报先给结论，再列三项重点',15);report['unaffected_memory_rendered']=True
 log=r.log(300);(a.out/'log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n');assert not any('[E]' in x or 'budget exceeded' in x for x in log['l'])
 report['model_ledger_absent']=not (c/'private/apps/.host/model/ledger.json').exists();assert report['model_ledger_absent']
 report['protected_after']={n:sha(jail/n) for n in protected};assert report['protected_after']==protected
 r.shot(a.out/'visible.png');(a.out/'snap.json').write_bytes(r.request('/snap'));report['pid']=json.loads(r.request('/s'))['pid'];report['pass']=True
except Exception as e:report['error']=str(e);raise
finally:
 report['seconds']=time.monotonic()-began;(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
