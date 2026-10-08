#!/usr/bin/env python3
"""Existing App Hub local rehearsal, quality-owned runtime and synthetic data."""
import argparse,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
OLD=Path('/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松')
BASE=OLD/'official_muse/app/build/ui-memory-20261003/final-contest-0327-rc10-r1'
SEED=OLD/'official_muse/app/build/ui-memory-20261003/rc51-cold-experiment-r3/private/apps/muse-goals'
def main():
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--sha',required=True);p.add_argument('--name',required=True);p.add_argument('--version',required=True);p.add_argument('--case',choices=['long','maxrefs','bad-tail','backup-tail','bad-goal-shape','bad-goal-tail'],default='long');a=p.parse_args()
 assert hashlib.sha256((a.bundle/'main.splash').read_bytes()).hexdigest()==a.sha
 out=Q/'runtime'/a.name;assert not out.exists()
 b=Q/'runtime'/(a.name+'-bundle');shutil.copytree(a.bundle,b);m=json.loads((b/'manifest.json').read_text());m['version']=a.version;(b/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 spec=importlib.util.spec_from_file_location('prep',ROOT/'official_muse/ui_memory/prepare_candidate.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 mod.HUB=OLD/'official_muse/rc/packaging/.local-state/tools/hub';mod.BASE_MIRROR=BASE/'mirror';mod.HOST_APP=Path('/Users/mima0000/Desktop/Muse-最新交付/01-正式参赛版/Muse-最终参赛交付-0.3.27-rc10/Muse.app/Contents/Resources/OctoSense Host.app')
 sys.argv=['prepare','--out',str(out),'--source-bundle',str(b),'--host-app',str(mod.HOST_APP),'--base-mirror',str(mod.BASE_MIRROR),'--local-model-only','--model-port','65534'];mod.main()
 jail=out/'private/apps/muse-goals'
 for n in ['memory.json','memory.backup.json','global-memory-settings.json','chat-sessions.json','chat-sessions.backup.json','calendar-state.json','goals.json','mail-watch.json']:shutil.copyfile(SEED/n,jail/n)
 chat=json.loads((jail/'chat-sessions.json').read_text())
 if a.case=='maxrefs':
  refs=[{'id':f'memory:boundary:{i}','revision':1,'account':'local','source_ids':[f'source:boundary:{j:02d}' for j in range(16)]} for i in range(6)]
  for session in chat['sessions']:
   for e in session['messages']:e['text']=e['text'][:512];e['memory_refs']=refs
 if a.case in ['bad-tail','backup-tail']:chat['sessions'][-1]['messages'][-1]['role']='not-a-role'
 raw=json.dumps(chat,ensure_ascii=False,separators=(',',':'));assert len(raw.encode())<=1048576
 (jail/'chat-sessions.json').write_text(raw)
 if a.case!='backup-tail':(jail/'chat-sessions.backup.json').write_text(raw)
 if a.case in ['bad-goal-shape','bad-goal-tail']:
  broken={'schema':2,'goals':'not-an-array' if a.case=='bad-goal-shape' else [{'id':'broken-goal'}],'runs':[],'actions':[],'selected_id':'broken-goal'}
  (jail/'goals.json').write_text(json.dumps(broken,separators=(',',':')))
 record=json.loads((out/'candidate.json').read_text());record.update(test_case=a.case,business_artifact_sha256=a.sha,seed_kind='SYNTHETIC_ONLY',seed_provenance=str(SEED),chat_bytes=len(raw.encode()))
 (out/'candidate.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
