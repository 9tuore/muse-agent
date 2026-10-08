#!/usr/bin/env python3
"""Local rc16 reproduction app; no accounts, production state or publication."""
from pathlib import Path
import hashlib,json,plistlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'build/7h-delivery-r1'
APP=OUT/'Muse.app'
VERSION='0.3.27-rc16'
SOURCE='dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4'
HOST='276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638'
ANCHOR='3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'
def run(args):
 return subprocess.run([str(x) for x in args],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True).stdout
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(),'Previous package/evidence is immutable'
 candidate=ROOT/'official_muse/app/build/ui-memory-20261003/7h-live-candidate-r9'
 assert sha(candidate/'bundle/main.splash')==SOURCE
 OUT.mkdir()
 run(['/bin/cp','-cR',ROOT/'build/7h-final-host-r1/Muse Candidate.app',APP])
 resources=APP/'Contents/Resources';mirror=resources/'mirror'
 # Only this new copy's old distribution catalog is replaced. Original evidence stays.
 if mirror.exists():shutil.rmtree(mirror)
 mirror.mkdir()
 hub=ROOT/'official_muse/rc/7h-20261008/quality/tools/hub'
 keys=Path('/Users/mima0000/.codex/worktrees/muse-official-migration/Agent APP黑客松/official_muse/app/build/keys')
 original=json.loads((candidate/'mirror/catalog.json').read_text())
 identity=(ROOT/'official_muse/rc/7h-20261008/source-component-r1/local-publisher-public.txt').read_text().strip()
 args=[hub,'publish',candidate/'bundle','--catalog',mirror/'catalog.json','--anchor',ANCHOR,'--key',keys/'working.key','--anchor-cert',original['key']['anchor_certificate'],'--publisher','muse-local-rehearsal','--publisher-key',identity,'--repo','local-rehearsal','--commit',run(['git','rev-parse','HEAD']).strip(),'--out',mirror]
 (OUT/'publish.txt').write_text(run(args));(OUT/'verify.txt').write_text(run([hub,'verify',mirror/'catalog.json','--anchor',ANCHOR]))
 catalog=json.loads((mirror/'catalog.json').read_text());assert len(catalog['entries'])==1
 assert catalog['entries'][0]['manifest']['version']==VERSION
 src=(ROOT/'tmall_submission/runtime/muse_launcher.m').read_text()
 src=src.replace('0.3.27-rc10',VERSION).replace('MUSE_TMALL_STATE','MUSE_7H_STATE').replace('MUSE_TMALL_REMOTE','MUSE_7H_REMOTE').replace('Muse Tmall Experience rc10','Muse Seven Hour 20261008')
 launcher=OUT/'muse_launcher.m';launcher.write_text(src)
 run(['/usr/bin/clang','-fobjc-arc','-mmacosx-version-min=14.0','-framework','AppKit','-framework','Foundation',launcher,'-o',APP/'Contents/MacOS/muse-launcher'])
 info_path=APP/'Contents/Info.plist';info=plistlib.loads(info_path.read_bytes());info.update(CFBundleIdentifier='org.xinghai.muse.7h.rc16',CFBundleName='Muse',CFBundleDisplayName='Muse',CFBundleShortVersionString='0.3.27',CFBundleVersion='16');info_path.write_bytes(plistlib.dumps(info))
 run(['/usr/bin/codesign','--force','--sign','-',APP]);run(['/usr/bin/codesign','--verify','--deep','--strict',APP])
 (OUT/'launcher-check.txt').write_text(run([APP/'Contents/MacOS/muse-launcher','--check']))
 assert sha(resources/'OctoSense Host.app/Contents/MacOS/octosense')==HOST
 record={'version':VERSION,'source_sha256':SOURCE,'host_sha256':HOST,'catalog_entry_count':1,'signature':'AD_HOC_DEVELOPMENT_ONLY','launcher_resource_check':'PASS','system_grant':'NOT_GRANTED','mail_profile':'Fresh canonical profile needs native login; no credentials transferred','full_chain':'PARTIAL','upstream_calendar_acceptance':False,'production_data_included':False}
 (OUT/'DELIVERY.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':main()
