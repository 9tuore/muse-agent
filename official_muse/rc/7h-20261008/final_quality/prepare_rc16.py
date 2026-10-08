#!/usr/bin/env python3
"""Prepare local-only final candidate after Root supplies verified Host freeze."""
import argparse, hashlib, importlib.util, json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
Q=Path(__file__).resolve().parent
SHA='dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4'
OLD=Path('/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--host-app',type=Path,required=True);p.add_argument('--host-sha',required=True);p.add_argument('--name',default='final-r1');a=p.parse_args()
 assert sha(a.host_app/'Contents/MacOS/octosense')==a.host_sha
 source=ROOT/'build/7h-focus-r2/compact/main.splash';assert sha(source)==SHA
 out=Q/'runtime'/a.name;bundle=Q/'runtime'/(a.name+'-bundle');assert not out.exists() and not bundle.exists()
 # Only known synthetic bundle assets and exact frozen source are copied.
 shutil.copytree(ROOT/'official_muse/app/build/ui-memory-20261003/7h-live-candidate-r9/bundle',bundle)
 shutil.copyfile(source,bundle/'main.splash')
 m=json.loads((bundle/'manifest.json').read_text());assert m['version']=='0.3.27-rc16';(bundle/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 spec=importlib.util.spec_from_file_location('prep_final',ROOT/'official_muse/ui_memory/prepare_candidate.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 mod.HUB=OLD/'official_muse/rc/packaging/.local-state/tools/hub'
 mod.BASE_MIRROR=OLD/'official_muse/app/build/ui-memory-20261003/final-contest-0327-rc10-r1/mirror'
 sys.argv=['prepare','--out',str(out),'--source-bundle',str(bundle),'--host-app',str(a.host_app),'--base-mirror',str(mod.BASE_MIRROR),'--local-model-only','--model-port','65534'];mod.main()
 jail=out/'private/apps/muse-goals'
 for f in (Q/'runtime/seed/private/apps/muse-goals').iterdir():
  if f.is_file():shutil.copyfile(f,jail/f.name)
 record=json.loads((out/'candidate.json').read_text());record.update(expected_goal_title='质量验收：恢复非空中文目标',expected_goal_card=True,seed_kind='SYNTHETIC_ONLY',seed_description='16 sessions/256 messages/64 claims/65 sources; planned Goal and failed Run/Action; disabled mail watcher with ready seen baseline',freeze_source_sha256=SHA)
 (out/'candidate.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'candidate':str(out),'source_sha256':SHA,'host_sha256':a.host_sha},ensure_ascii=False))
if __name__=='__main__':main()
