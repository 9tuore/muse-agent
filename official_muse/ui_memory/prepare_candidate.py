#!/usr/bin/env python3
"""Local-only App Hub gate and isolated candidate. No remote publication or account data export."""
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HOST_ROOT=Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host')
LEGACY_BUILD=Path('/Users/mima0000/.codex/worktrees/muse-official-migration/Agent APP黑客松/official_muse/app/build')
BASE_MIRROR=Path('/Users/mima0000/.codex/worktrees/muse-round2-improvements/Agent APP黑客松/official_muse/app/build/round2/mirror')
BASE_APPS=LEGACY_BUILD/'phase2-final-029-r2-apps'
HUB=Path(os.environ.get('MUSE_HUB_CLI', str(HOST_ROOT/'OctoSense-App-Hub/target/release/hub')))
ANCHOR='3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'
HOST_APP=HOST_ROOT/'OctoSense/target/muse-calendar-test/OctoSense Muse 中文版 0.2.10-r2.app'
def copy_authorized_model_profile(authorized,private):
 # Copy only the official model profile, never Mail/Calendar account stores.
 # Credentials remain opaque private file bytes and are never returned/logged.
 source=authorized/'home/octos-home/.octos/profiles/_main.json'
 if not source.is_file():raise RuntimeError('Authorized model profile is missing')
 data=json.loads(source.read_text())
 llm=data.get('config',{}).get('llm',{})
 primary=llm.get('primary',{})
 route=primary.get('route',{})
 metadata={'family_id':primary.get('family_id'),'model_id':primary.get('model_id'),
           'base_url':route.get('base_url'),'api_type':route.get('api_type')}
 if metadata != {'family_id':'minimax-cn','model_id':'MiniMax-M3',
                 'base_url':'https://api.minimax.cn/v1','api_type':'openai'}:
  raise RuntimeError('Authorized model must be the verified official MiniMax China/M3 route')
 if llm.get('fallbacks') != []:raise RuntimeError('Remote acceptance requires no fallback providers')
 destination=private/'home/octos-home/.octos/profiles/_main.json'
 destination.parent.mkdir(parents=True)
 shutil.copyfile(source,destination)
 destination.chmod(0o600)
 private.chmod(0o700)
 return metadata
def command(args,out):
 r=subprocess.run([str(HUB),*map(str,args)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 out.write_text(r.stdout)
 if r.returncode:raise RuntimeError(f'Local gate failed: {out.name}')
 return r.stdout.strip()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
 profiles=p.add_mutually_exclusive_group()
 profiles.add_argument('--clone-host-profile',action='store_true')
 profiles.add_argument('--local-model-only',action='store_true')
 profiles.add_argument('--authorized-model-only',action='store_true')
 p.add_argument('--host-app',type=Path,default=HOST_APP)
 p.add_argument('--base-mirror',type=Path,default=BASE_MIRROR)
 p.add_argument('--model-port',type=int,default=8080)
 p.add_argument('--authorized-profile',type=Path,help='Existing private home/apps profile to clone read-only for real acceptance')
 p.add_argument('--source-bundle',type=Path,default=ROOT/'official_muse/app/bundle')
 a=p.parse_args();out=a.out.resolve()
 if a.authorized_profile and not (a.clone_host_profile or a.authorized_model_only):raise RuntimeError('--authorized-profile requires an authorized clone mode')
 if a.authorized_model_only and not a.authorized_profile:raise RuntimeError('--authorized-model-only requires --authorized-profile')
 host_app=a.host_app.resolve();host_binary=host_app/'Contents/MacOS/octosense'
 if not host_binary.is_file():raise RuntimeError('Selected test Host binary does not exist')
 if out.exists():raise RuntimeError('Use a fresh output directory; previous evidence is immutable.')
 out.mkdir(parents=True);bundle=out/'bundle';mirror=out/'mirror'
 shutil.copytree(a.source_bundle.resolve(),bundle)
 shutil.copytree(a.base_mirror.resolve(),mirror)
 publisher=LEGACY_BUILD/'keys/publisher.key';working=LEGACY_BUILD/'keys/working.key'
 assert HUB.is_file() and publisher.is_file() and working.is_file()
 pub=subprocess.check_output([str(HUB),'pubkey',str(publisher)],text=True).strip();identity='muse-local-rehearsal='+pub
 command(['stamp',bundle],out/'stamp.txt')
 command(['sign-manifest',bundle,'--key',publisher,'--key-id','muse-local-rehearsal'],out/'sign.txt')
 command(['check',bundle,'--publisher-key',identity],out/'check.txt')
 command(['scan',bundle,'--packet',out/'review-packet.json','--publisher-key',identity],out/'scan.txt')
 catalog=json.loads((mirror/'catalog.json').read_text());cert=catalog['key']['anchor_certificate']
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 command(['publish',bundle,'--catalog',mirror/'catalog.json','--key',working,'--anchor-cert',cert,
          '--publisher','muse-local-rehearsal','--publisher-key',identity,'--repo','local-rehearsal','--commit',head,'--out',mirror],out/'publish.txt')
 command(['verify',mirror/'catalog.json','--anchor',ANCHOR],out/'verify.txt')
 private=out/'private';private.mkdir()
 model_metadata=None
 if a.authorized_model_only:
  model_metadata=copy_authorized_model_profile(a.authorized_profile.resolve(),private)
  jail=private/'apps/muse-goals';jail.mkdir(parents=True)
  shutil.copytree(bundle,jail/'bundle')
 if a.clone_host_profile:
  authorized=a.authorized_profile.resolve() if a.authorized_profile else None
  profile_home=authorized/'home' if authorized else LEGACY_BUILD/'phase2-live-home'
  profile_host=authorized/'apps/.host' if authorized else BASE_APPS/'.host'
  if not profile_home.is_dir() or not profile_host.is_dir():raise RuntimeError('Authorized source profile is missing')
  # The 862 MiB build tree is a regenerable unpack cache, not user settings.
  shutil.copytree(profile_home,private/'home',ignore=shutil.ignore_patterns('build','run'))
  jail=private/'apps/muse-goals';jail.mkdir(parents=True)
  # Reuse the already-authorized Host account state only inside the private clone.
  # The app does not receive credentials; the Host continues owning them.
  shutil.copytree(profile_host,private/'apps/.host')
  shutil.copytree(bundle,jail/'bundle')
  # Fresh synthetic app data with real existing Host settings/grants, not production Muse data.
  (jail/'mail-watch.json').write_text(json.dumps({'schema':1,'enabled':False,'accounts':[],'alerts':[]}))
  private.chmod(0o700)
 if a.local_model_only:
  # New synthetic profile: no Host account state, production app files, or credentials.
  profile=private/'home/octos-home/.octos/profiles/_main.json'
  profile.parent.mkdir(parents=True)
  profile.write_text(json.dumps({'id':'_main','name':'Muse隔离本地验收','enabled':True,
    'config':{'llm':{'primary':{'family_id':'local','model_id':'local-default',
      'route':{'base_url':f'http://127.0.0.1:{a.model_port}/v1','api_type':'openai'}},'fallbacks':[]},'env_vars':{}}},ensure_ascii=False)+'\n')
  profile.chmod(0o600)
  jail=private/'apps/muse-goals';jail.mkdir(parents=True)
  shutil.copytree(bundle,jail/'bundle')
  private.chmod(0o700)
 record={'version':json.loads((bundle/'manifest.json').read_text())['version'],'source_sha256':hashlib.sha256((bundle/'main.splash').read_bytes()).hexdigest(),
         'manifest':json.loads((bundle/'manifest.json').read_text()),'commit':head,'gate':'LOCAL_EXTENDED_HUB_PASS',
         'review':'packet generated, no independent publisher review','upstream_calendar_acceptance':False,
         'host_app_path':str(host_app),'host_sha256':hashlib.sha256(host_binary.read_bytes()).hexdigest(),
         'hub_cli_sha256':hashlib.sha256(HUB.read_bytes()).hexdigest(),
         'profile_kind':'AUTHORIZED_MODEL_ONLY_SYNTHETIC' if a.authorized_model_only else 'LOCAL_MODEL_ONLY_SYNTHETIC' if a.local_model_only else 'PRIVATE_AUTHORIZED_CLONE' if a.clone_host_profile else 'NO_PROFILE'}
 if model_metadata:record['model_metadata']=model_metadata
 if a.clone_host_profile:record['authorized_profile_source']=str(authorized) if authorized else 'legacy phase2 authorized profile'
 record['source_bundle']=str(a.source_bundle.resolve())
 (out/'candidate.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in record.items() if k not in ('manifest','host_sha256')},ensure_ascii=False))
if __name__=='__main__':main()
