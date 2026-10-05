#!/usr/bin/env python3
"""Prepare explicit public rc18 runtime inputs; never start the Host or sign."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
F = '019dc303da964424e042402893008a387a675467'
A = 'b8545265e50b846493c436999b9b0066d10ed7af'
RUN = Path('/private/tmp/muse-morning-clean-019dc303-20261005')
INPUT = RUN / 'checkout/build/clean-delivery'
STAGE = HERE / 'Muse-0.3.26-rc18-Intel开发验收草稿'
RUNTIME = STAGE / '04-运行文件'
BUNDLE = 'artifacts/muse-goals-0.3.26-rc18.bundle'
PUBLISHER = 'muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5'
ANCHOR = '3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    assert not STAGE.exists(), 'Preserve existing draft'
    assert shutil.disk_usage(HERE).free > 900 * 1024**2, '600MiB reserve plus copy budget'
    RUNTIME.mkdir(parents=True)
    checks = []
    for name, binary, expected in (
        ('Muse Host.app', 'octosense', '7eebe8331982d327646da25d1154d878a153fa56b7030143b34f07c149dcbbec'),
        ('Muse Card Host.app', 'card-host', '30ed0c9355f047e298415c983bf5846ca798633f5875c6492ef724632fdacb15')):
        assert sha(INPUT / name / 'Contents/MacOS' / binary) == expected
        subprocess.run(['/bin/cp', '-cR', str(INPUT / name), str(RUNTIME / name)], check=True)
        assert sha(RUNTIME / name / 'Contents/MacOS' / binary) == expected
        command = ['codesign', '--verify', '--deep', '--strict', str(RUNTIME / name)]
        value = subprocess.run(command, capture_output=True, text=True)
        checks.append({'command': command, 'exit_code': value.returncode, 'output': value.stdout + value.stderr})
        assert value.returncode == 0
    shutil.copy2(INPUT / 'hub', RUNTIME / 'hub')
    assert sha(RUNTIME / 'hub') == '24db5e559582c44936e3023b2bd6e276f9390531d94f77682d45760db9a6b64d'
    destination = RUNTIME / 'mirror' / BUNDLE
    paths = ['assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
             'screenshots/01-main.png', 'screenshots/02-global-memory.png']
    bundle_hashes = {}
    for relative in paths:
        data = subprocess.check_output(['git', 'show', A + ':official_muse/app/bundle/' + relative], cwd=REPO)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o644)
        bundle_hashes[relative] = sha(target)
    manifest = json.loads((destination / 'manifest.json').read_text())
    assert manifest['id'] == 'muse-goals' and manifest['version'] == '0.3.26-rc18'
    command = [str(RUNTIME / 'hub'), 'check', str(destination), '--publisher-key', PUBLISHER]
    value = subprocess.run(command, capture_output=True, text=True)
    checks.append({'command': command, 'exit_code': value.returncode, 'output': value.stdout + value.stderr})
    assert value.returncode == 0
    lock = RUN / 'checkout/dependencies.lock.json'
    metadata = {'status': 'DEVELOPMENT_PARTIAL_DRAFT_PUBLIC_CATALOG_PENDING',
                'application_A': A, 'application_version': manifest['version'],
                'runtime_host_F': F, 'runtime_sdk_lock_sha256': sha(lock),
                'Host_sha256': sha(RUNTIME / 'Muse Host.app/Contents/MacOS/octosense'),
                'Card_sha256': sha(RUNTIME / 'Muse Card Host.app/Contents/MacOS/card-host'),
                'Hub_sha256': sha(RUNTIME / 'hub'), 'canonical_bundle_files': bundle_hashes,
                'public_publisher_key': PUBLISHER, 'public_catalog_anchor': ANCHOR,
                'catalog_and_pack_pending': True, 'models_profiles_accounts_database_weights_included': False,
                'runtime_recovery_build': 'Original clean runner network FAIL preserved; same new-run inputs recovered via Git CLI',
                'A4_GUI_models_external_actions_run': False, 'receiving_Intel_Macs': 'NOT_TESTED',
                'ARM': 'NOT_TESTED', 'final_business_chain': 'PARTIAL_ROOT_REPORT_SEPARATE',
                'new_signing_or_private_key_read': False}
    (STAGE / '05-版本与校验.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    (HERE / 'PREPARE_RESULT.json').write_text(json.dumps({'metadata': metadata, 'checks': checks, 'stage': str(STAGE)}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'stage': str(STAGE), 'metadata': metadata, 'checks_passed': len(checks)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
