#!/usr/bin/env python3
"""Package a fresh build using only paths inside the clean checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, default=Path('vendor'))
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--kind', choices=('host', 'card'), default='host')
    args = parser.parse_args()
    root = Path.cwd().resolve()
    for p in [args.sdk, args.target, args.output]:
        assert root in p.resolve().parents, 'All inputs and output must be inside this checkout'
    executable_name = 'octosense' if args.kind == 'host' else 'card-host'
    binary = args.target / 'release' / executable_name
    unsigned_sha = hashlib.sha256(binary.read_bytes()).hexdigest()
    info = plistlib.loads((args.target / 'release/Info.plist').read_bytes())
    assert not args.output.exists()
    macos = args.output / 'Contents/MacOS'; macos.mkdir(parents=True)
    executable = macos / executable_name; shutil.copy2(binary, executable)
    resources = args.output / 'Contents/Resources'
    roots = [('makepad_widgets', args.sdk / 'makepad/widgets/resources')]
    if args.kind == 'host':
        roots.extend([('octosense_shell', args.sdk / 'octosense/crates/shell/resources'), ('octosense_app_hub_app', args.sdk / 'app-hub/crates/app-hub-app/resources')])
    for crate, source in roots:
        shutil.copytree(source, resources / crate / 'resources')
        (macos / crate).symlink_to(Path('../Resources') / crate, target_is_directory=True)
    for dependency in args.sdk.iterdir():
        if dependency.is_dir():
            for f in dependency.iterdir():
                if f.is_file() and f.name.startswith(('LICENSE', 'COPYING')):
                    destination = resources / 'licenses' / dependency.name
                    destination.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, destination / f.name)
    info.update({'CFBundleIdentifier': 'dev.makepad.octosense.musecleanroom.local' if args.kind == 'host' else 'dev.makepad.octosense.musecardcleanroom.local', 'CFBundleExecutable': executable_name, 'CFBundleName': args.output.stem, 'CFBundleDisplayName': args.output.stem, 'CFBundlePackageType': 'APPL', 'CFBundleVersion': '1', 'CFBundleShortVersionString': args.version.split('-')[0], 'CFBundleDevelopmentRegion': 'zh_CN', 'CFBundleLocalizations': ['zh_CN'], 'NSLocationUsageDescription': '在你授权后，用于在地图上显示你的位置。', 'NSLocationWhenInUseUsageDescription': '在你授权后，用于在地图上显示你的位置。'})
    if args.kind == 'host':
        info['NSCalendarsFullAccessUsageDescription'] = 'Muse 在你确认后读取、创建或修改系统日历事件，并读回结果。'
    (args.output / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
    subprocess.run(['codesign', '--force', '--sign', '-', str(args.output)], check=True)
    subprocess.run(['codesign', '--verify', '--deep', '--strict', '--verbose=2', str(args.output)], check=True)
    report = {'app': str(args.output), 'kind': args.kind, 'unsigned_binary_sha256': unsigned_sha, 'signed_binary_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(), 'architecture': subprocess.check_output(['lipo', '-archs', str(executable)], text=True).strip(), 'resource_roots': [crate for crate, _ in roots], 'signature': 'ad hoc, strict verify passed; no publisher signing key used', 'version': args.version, 'ui_or_external_actions_run': False}
    (args.output.parent / f'clean-{args.kind}.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
