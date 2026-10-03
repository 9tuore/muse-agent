#!/usr/bin/env python3
"""Package the trusted-theme build in a new local app; never launch/install it."""
from pathlib import Path
import hashlib, json, plistlib, shutil, subprocess

r = Path(__file__).resolve().parents[3]
e = r / 'official_muse/prelim/evidence/startup-host'
i = json.loads((e / 'source-index.json').read_text())
build = json.loads((e / 'build-result.json').read_text())
assert build['status'] == 'BUILD_PASS' and build['symlink_restored']
link = Path(i['lexical_link'])
assert str(link.readlink()) == i['original_symlink_target']
matched = link.parents[1]
snapshot = Path(i['snapshot_sdk'])
base = snapshot.parent
binary = base / 'target/release/octosense'
original = base / 'OctoSense mail-sync Host candidate.app'
app = base / 'OctoSense trusted-theme Host candidate.app'
staging = base / '.packaging-trusted-theme.app'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def protect():
    assert sha(original / 'Contents/MacOS/octosense') == 'e9ac1e477665a93476fa10454adff5d16e482d21a075c19b34ce9a6d486d824d'
    assert sha(Path(i['raw_backup'])) == i['raw_backup_sha256']
    assert sha(Path(i['source_sdk']) / 'widgets/src/splash.rs') == i['baseline_splash_sha256']
    assert sha(r / 'official_muse/app/bundle/main.splash') == i['root_main_sha256']
    assert sha(r / 'official_muse/incoming_mail.splash') == i['mail_module_sha256']

protect()
raw_sha = sha(binary)
assert raw_sha != i['raw_backup_sha256']
if app.exists() or staging.exists():
    raise RuntimeError('A fresh unique package output is required')
shutil.copytree(original, staging, symlinks=True, ignore=shutil.ignore_patterns('_CodeSignature'))
shutil.copy2(binary, staging / 'Contents/MacOS/octosense')
resources = {
    'octosense_shell': matched / 'crates/shell/resources',
    'makepad_widgets': snapshot / 'widgets/resources',
    'octosense_app_hub_app': matched / '.sources/app-hub/crates/app-hub-app/resources',
}
for name, source in resources.items():
    dest = staging / 'Contents/Resources' / name / 'resources'
    assert source.is_dir() and dest.is_dir()
    shutil.rmtree(dest)
    shutil.copytree(source, dest, symlinks=True)
info = staging / 'Contents/Info.plist'
data = plistlib.loads(info.read_bytes())
data['CFBundleName'] = 'OctoSense trusted-theme Host candidate'
data['CFBundleDisplayName'] = data['CFBundleName']
info.write_bytes(plistlib.dumps(data))
links = []
for path in staging.rglob('*'):
    if path.is_symlink():
        assert path.resolve().exists(), path
        links.append({'path': str(path.relative_to(staging)), 'target': str(path.readlink())})
subprocess.run(['codesign', '--force', '--sign', '-', str(staging)], check=True)
subprocess.run(['codesign', '--verify', '--strict', '--deep', str(staging)], check=True)
staging.rename(app)

def tree_hash(path):
    h = hashlib.sha256()
    for p in sorted(path.rglob('*')):
        h.update(str(p.relative_to(path)).encode())
        if p.is_symlink():
            h.update(str(p.readlink()).encode())
        elif p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()

trees = {name: {'source': str(source), 'source_sha256': tree_hash(source),
    'package_sha256': tree_hash(app / 'Contents/Resources' / name / 'resources')}
    for name, source in resources.items()}
assert all(v['source_sha256'] == v['package_sha256'] for v in trees.values())
protect()
result = {
    'kind': 'BUILT_SIGNED_HOST_NOT_LIVE_VERIFIED', 'app_path': str(app),
    'raw_binary_path': str(binary), 'raw_binary_sha256': raw_sha,
    'packaged_binary_sha256': sha(app / 'Contents/MacOS/octosense'),
    'resource_trees': trees, 'package_links': links, 'codesign_strict_verify': True,
    'sdk_snapshot': str(snapshot), 'patch_sha256': i['patch_sha256'],
    'lexical_symlink_restored_to': str(link.readlink()),
    'protected_originals_unchanged': True, 'root_main_sha256': i['root_main_sha256'],
    'mail_module_sha256': i['mail_module_sha256'],
    'launched': False, 'installed': False, 'runtime_startup_pass': False,
}
(e / 'candidate-artifact.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'app': str(app), 'raw_sha256': raw_sha,
    'packaged_binary_sha256': result['packaged_binary_sha256'],
    'codesign_strict_verify': True, 'runtime_startup_pass': False}, ensure_ascii=False))
