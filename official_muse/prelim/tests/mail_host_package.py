#!/usr/bin/env python3
"""Package the built candidate with matched resources; no launch or installation."""
from pathlib import Path
import hashlib,json,plistlib,shutil,subprocess
r=Path(__file__).resolve().parents[3]
base=r/'official_muse/app/build/ui-memory-20261003/mail-host-033'
matched=base/'OctoSense';candidate=base.parent/'prelim-host'
ev=r/'official_muse/prelim/evidence/mail-host'
binary=candidate/'target/release/octosense'
build=(ev/'candidate-build-r2.log').read_text()
if 'Finished `release` profile' not in build: raise RuntimeError('Candidate build not confirmed')
protected=json.loads((ev/'build-inputs.json').read_text())['protected_original_binaries']
for entry in protected.values():
    if hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest()!=entry['sha256']: raise RuntimeError('Protected original changed')
if hashlib.sha256(binary.read_bytes()).hexdigest()==protected['octosense']['sha256']: raise RuntimeError('Candidate is still the cloned old binary')
app=candidate/'OctoSense mail-sync Host candidate.app'
staging=candidate/'.packaging-mail-sync.app'
if app.exists() or staging.exists(): raise RuntimeError('New package output required')
original=next(base.glob('*.app'))
shutil.copytree(original,staging,symlinks=True,ignore=shutil.ignore_patterns('_CodeSignature'))
shutil.copy2(binary,staging/'Contents/MacOS/octosense')
resource_paths={'octosense_shell':matched/'crates/shell/resources','makepad_widgets':matched/'.sources/makepad/widgets/resources','octosense_app_hub_app':matched/'.sources/app-hub/crates/app-hub-app/resources'}
for name,source in resource_paths.items():
    dest=staging/'Contents/Resources'/name/'resources'
    if not source.is_dir() or not dest.is_dir(): raise RuntimeError(f'Missing matched resources: {name}')
    shutil.rmtree(dest);shutil.copytree(source,dest,symlinks=True)
info=staging/'Contents/Info.plist'
with info.open('rb') as f: data=plistlib.load(f)
data['CFBundleName']='OctoSense mail-sync Host candidate';data['CFBundleDisplayName']=data['CFBundleName']
with info.open('wb') as f: plistlib.dump(data,f)
links=[]
for p in staging.rglob('*'):
    if p.is_symlink():
        if not p.resolve().exists(): raise RuntimeError(f'Dangling package link: {p}')
        links.append({'path':str(p.relative_to(staging)),'target':str(p.readlink())})
subprocess.run(['codesign','--force','--sign','-',str(staging)],check=True)
subprocess.run(['codesign','--verify','--strict','--deep',str(staging)],check=True)
staging.rename(app)
def tree_hash(path):
    h=hashlib.sha256()
    for p in sorted(path.rglob('*')):
        h.update(str(p.relative_to(path)).encode())
        if p.is_symlink(): h.update(str(p.readlink()).encode())
        elif p.is_file(): h.update(p.read_bytes())
    return h.hexdigest()
source_links={p.name:{'symlink':p.is_symlink(),'resolved':str(p.resolve()),'exists':p.resolve().exists()} for p in (matched/'.sources').iterdir()}
result={'kind':'BUILT_HOST_PACKAGE_NOT_LIVE_VERIFIED','app_path':str(app),'raw_binary_path':str(binary),'raw_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'packaged_binary_sha256':hashlib.sha256((app/'Contents/MacOS/octosense').read_bytes()).hexdigest(),'package_links':links,'matched_sources':source_links,'resource_trees':{name:{'source':str(source),'source_sha256':tree_hash(source),'package_sha256':tree_hash(app/'Contents/Resources'/name/'resources')} for name,source in resource_paths.items()},'codesign_strict_verify':True,'launched':False,'installed':False,'real_mail':False,'protected_originals_unchanged':True}
assert all(item['source_sha256']==item['package_sha256'] for item in result['resource_trees'].values())
(ev/'candidate-artifact.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'app':str(app),'raw_sha256':result['raw_binary_sha256'],'package_sha256':result['packaged_binary_sha256'],'matched_resources':True,'launched':False},ensure_ascii=False))
