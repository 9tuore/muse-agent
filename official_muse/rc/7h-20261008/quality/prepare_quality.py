#!/usr/bin/env python3
"""Fresh isolated quality profile from a pinned synthetic baseline; no accounts."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OLD=Path('/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松')
QUALITY=Path(__file__).resolve().parent
BASE=OLD/'official_muse/app/build/ui-memory-20261003/final-contest-0327-rc10-r1'
SEED=OLD/'official_muse/app/build/ui-memory-20261003/rc51-cold-experiment-r3/private/apps/muse-goals'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--source-bundle',type=Path,default=ROOT/'official_muse/app/bundle');a=p.parse_args()
 out=a.out.resolve();assert out.is_relative_to(QUALITY/'runtime') and not out.exists()
 m=json.loads((BASE/'candidate.json').read_text());assert sha(a.source_bundle/'main.splash')==m['source_sha256'],'Baseline helper only accepts frozen rc10'
 out.mkdir(parents=True)
 shutil.copytree(BASE/'mirror',out/'mirror')
 shutil.copytree(BASE/'bundle',out/'bundle')
 private=out/'private';jail=private/'apps/muse-goals';jail.mkdir(parents=True)
 shutil.copytree(out/'bundle',jail/'bundle')
 names=['memory.json','memory.backup.json','global-memory-settings.json','chat-sessions.json','chat-sessions.backup.json','calendar-state.json','goals.json','mail-watch.json']
 for n in names:shutil.copyfile(SEED/n,jail/n)
 # Empty unavailable local route; never use/copy a live model or account config.
 profile=private/'home/octos-home/.octos/profiles/_main.json';profile.parent.mkdir(parents=True)
 profile.write_text(json.dumps({'id':'_main','name':'MUSE-7H synthetic quality','enabled':True,'config':{'llm':{'primary':{'family_id':'local','model_id':'local-default','route':{'base_url':'http://127.0.0.1:65534/v1','api_type':'openai'}},'fallbacks':[]},'env_vars':{}}},ensure_ascii=False)+'\n');profile.chmod(0o600);private.chmod(0o700)
 m.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),runtime_private_path=str(private),profile_kind='LOCAL_MODEL_ONLY_SYNTHETIC',seed_source=str(SEED),seed_files={n:sha(jail/n) for n in names})
 (out/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:m[k] for k in ['version','source_sha256','host_sha256','commit','seed_files']},ensure_ascii=False))
if __name__=='__main__':main()
