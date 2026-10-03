#!/usr/bin/env python3
"""Package only the isolated rebuilt Host, never the installed application."""
import hashlib
import json
import plistlib
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROVENANCE = json.loads((HERE / 'source_provenance.json').read_text())
SOURCE = Path(PROVENANCE['isolated_source'])
WORK = SOURCE.parent
TARGET = WORK / 'target/release'
BUNDLE = WORK / 'OctoSense Muse 0.3.3 UI-candidate.app'


def main():
    assert not BUNDLE.exists(), 'refuse to overwrite a candidate'
    binary = TARGET / 'octosense'
    assert binary.is_file()
    sources = {
        'makepad_widgets': SOURCE / '.sources/makepad/widgets/resources',
        'octosense_shell': SOURCE / 'crates/shell/resources',
        'octosense_app_hub_app': SOURCE / '.sources/app-hub/crates/app-hub-app/resources',
    }
    assert all(path.is_dir() for path in sources.values())
    macos = BUNDLE / 'Contents/MacOS'
    macos.mkdir(parents=True)
    executable = macos / 'octosense'
    shutil.copy2(binary, executable)
    for crate, source in sources.items():
        shutil.copytree(source, BUNDLE / 'Contents/Resources' / crate / 'resources')
        (macos / crate).symlink_to(Path('../Resources') / crate, target_is_directory=True)
    with (TARGET / 'Info.plist').open('rb') as stream:
        info = plistlib.load(stream)
    info.update({
        'CFBundleIdentifier': 'dev.makepad.octosense.muse.mail033.local',
        'CFBundleName': 'OctoSense Muse 0.3.3 UI-candidate',
        'CFBundleDisplayName': 'OctoSense Muse 0.3.3 UI-candidate',
        'CFBundleExecutable': 'octosense', 'CFBundlePackageType': 'APPL',
        'CFBundleVersion': '3', 'CFBundleShortVersionString': '0.3.3',
        'CFBundleDevelopmentRegion': 'zh_CN', 'CFBundleLocalizations': ['zh_CN'],
        'NSCalendarsFullAccessUsageDescription': 'Muse 在你确认后读取、创建或修改系统日历事件，并读回结果。',
    })
    with (BUNDLE / 'Contents/Info.plist').open('wb') as stream:
        plistlib.dump(info, stream)
    subprocess.run(['codesign', '--force', '--sign', '-', str(BUNDLE)], check=True)
    subprocess.run(['codesign', '--verify', '--strict', '--verbose=1', str(BUNDLE)], check=True)
    report = {
        'candidate': str(BUNDLE),
        'unsigned_binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'signed_executable_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(),
        'signature': 'local ad hoc, strict verification passed',
        'mail_source_sha256': hashlib.sha256((SOURCE / 'apps/mail/host-service/src/lib.rs').read_bytes()).hexdigest(),
    }
    (HERE / 'package_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
