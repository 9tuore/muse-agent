#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package only named Tmall materials and an existing verified Host/mirror.

No core edit, download, account export, installation or public submission.
The fresh extraction validates bytes, modes, internal links and codesign.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = '0b764f852301c2f5e4deadd6d63fde0eee3d2660'
HOST_SHA = '1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3'
PAYLOAD_SHA = '0caaee7374e2446abafffeda33fe24bdcf8f9125757f881d664efabb83c36686'
BUNDLE_FILES = ['assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
                'screenshots/01-main.png', 'screenshots/02-global-memory.png']
DOCS = ['REAL_FLOW_PROOF.json', 'FINAL_REPORT.md', 'README.md', 'PROJECT_INTRO.md', 'AI_PRACTICE.md', 'ARCHITECTURE.md',
        '使用教程.md', '使用教程.html',
        'RUN_GUIDE.md', 'KNOWN_LIMITATIONS.md', 'DEMO_SCRIPT.md', 'TMALL_DEMO_SCRIPT.md',
        'TECH_STACK.md', 'FORM_AI_PRACTICE_300.txt', 'FORM_PROJECT_INTRO_500.txt',
        'RUN_MUSE.command', 'ACCEPTANCE.md', 'VERIFICATION.json', 'build_submission.py',
        'build_overview.py', 'tests/test_entry.py', 'runtime/README.md', 'runtime/RUNTIME_LOCK.json',
        'runtime/MODEL_LOCK.json', 'runtime/muse_launcher.m', 'tests/test_offline_live.py',
        'tests/test_profile_preservation.py',
        'source/SOURCE_MANIFEST.md', 'source/SOURCE_MANIFEST.json',
        'assets/cover.png', 'assets/diagrams/architecture.svg', 'assets/diagrams/architecture.png',
        'assets/screenshots/README.md', 'assets/screenshots/01-main.png',
        'assets/screenshots/07-memory-recall.png', 'assets/screenshots/MEDIA_PROVENANCE.json',
        'demo/README.md', 'demo/Muse-Mail-Calendar-rc10.zh-CN.mp4',
        'demo/Muse-Mail-Calendar-rc10.zh-CN.srt', 'demo/RC9_PROVENANCE.json']


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(*args):
    return subprocess.check_output(list(map(str, args)), stderr=subprocess.STDOUT).decode('utf8')


def inventory(root):
    rows = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            p = Path(base) / name
            mode = stat.S_IMODE(p.lstat().st_mode)
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                target = os.readlink(p)
                p.resolve(strict=True).relative_to(root.resolve())
                assert not Path(target).is_absolute()
                rows[rel] = dict(kind='link', mode=mode, target=target)
            elif p.is_file():
                rows[rel] = dict(kind='file', mode=mode, bytes=p.stat().st_size, sha256=sha(p))
    return rows


def scan(stage):
    import re
    prohibited = {'.git', 'target', 'node_modules', 'cache', '.local-state', 'profiles', 'private'}
    patterns = [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}',
                rb'(?i)["\x27](?:api_key|password|auth_code)["\x27]\s*:\s*["\x27][^"\x27]{8,}["\x27]']
    emails = re.compile(rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
    reviewed = set()
    for p in stage.rglob('*'):
        assert not set(p.relative_to(stage).parts) & prohibited
        assert not p.name.endswith(('.key', '.pem', '.sqlite', '.db', '.log'))
        if p.suffix == '.gguf':
            assert p.relative_to(stage).as_posix() == 'Muse.app/Contents/Resources/local-model/qwen2.5-0.5b-instruct-q4_0.gguf'
            assert sha(p) == '7671c0c304e6ce5a7fc577bcb12aba01e2c155cc2efd29b2213c95b18edaf6ed'
        if p.is_file() and p.suffix in ('.md', '.html', '.txt', '.json', '.command', '.py', '.m', '.svg', '.splash', '.srt', '.plist'):
            data = p.read_bytes()
            # Exact static test fixture from the shipped host-login unit test.
            scanned = data
            if p.relative_to(stage).as_posix() == 'source/current/official_muse/ui_memory/host-login/patch_host.py':
                scanned = scanned.replace(b'" fixture-only-value "', b'"fixture"').replace(b'"fixture-only-value"', b'"fixture"')
            assert not any(re.search(pattern, scanned) for pattern in patterns), str(p)
            for address in emails.findall(data):
                # No human addresses permitted. XML/Apple identifiers are not email contacts.
                decoded = address.decode()
                if 'source/current/' in p.relative_to(stage).as_posix():
                    assert not re.search(rb'(?:[0-9]{5,}@qq\.com|yyao52706@gmail\.com)', address), 'private test contact in source'
                    continue
                if decoded.endswith(('@example.com', '@example.invalid', '@users.noreply.github.com')) or decoded in {'user@qq.com','test@qq.com','a@qq.com','b@qq.com','u@qq.com'}: continue
                reviewed.add(decoded)
    assert not reviewed, 'Unexpected email-like contact in public allowlist'
    return dict(high_confidence_secret_matches=0, email_contacts=sorted(reviewed),
                scope='allowlisted text and paths; media separately visually reviewed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-app', type=Path, required=True)
    parser.add_argument('--mirror', type=Path, required=True)
    parser.add_argument('--model-root', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--source-list', type=Path, required=True)
    args = parser.parse_args()
    assert sha(args.host_app / 'Contents/MacOS/octosense') == HOST_SHA
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', args.host_app)
    locked = json.loads((HERE / 'runtime/RUNTIME_LOCK.json').read_text())
    assert inventory(args.host_app) == locked['host_files']
    model = json.loads((HERE / 'runtime/MODEL_LOCK.json').read_text())
    assert inventory(args.model_root) == model['files'], 'Model/runner/license identity mismatch'
    assert run('/usr/bin/lipo', '-archs', args.model_root / 'llama/llama-server').strip() == 'x86_64'
    catalog = json.loads((args.mirror / 'catalog.json').read_text())
    selected = [e for e in catalog['entries'] if e['manifest']['id'] == 'muse-goals'
                and e['manifest']['version'] == '0.3.27-rc10']
    assert len(selected) == 1
    entry = selected[0]
    artifact = 'artifacts/muse-goals-0.3.27-rc10.bundle'
    assert entry['artifact'] == artifact
    assert sha(args.mirror / artifact / 'main.splash') == PAYLOAD_SHA
    for rel in BUNDLE_FILES:
        expected = subprocess.check_output(['git', 'show', BASE + ':official_muse/app/bundle/' + rel], cwd=ROOT)
        actual = (args.mirror / artifact / rel).read_bytes()
        if rel == 'manifest.json':
            declared = json.loads(expected); delivered = json.loads(actual)
            declared.pop('integrity', None); delivered.pop('integrity', None)
            declared.pop('signature', None); delivered.pop('signature', None)
            assert declared == delivered, 'Runtime manifest policy differs from frozen source'
        else:
            assert actual == expected
    stage = args.destination.resolve()
    assert not stage.exists(), 'Preserve existing delivery; choose a new destination'
    stage.mkdir(parents=True)
    for rel in DOCS:
        out = stage / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / rel, out)
    source_rows = {}
    for rel in json.loads(args.source_list.read_text()):
        assert not set(Path(rel).parts) & {'.git', 'private', '.local-state', 'target', 'build'}
        data = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
        out = stage / 'source/current' / rel
        out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
        source_rows[rel] = hashlib.sha256(data).hexdigest()
    (stage / 'source/CURRENT_FILES.json').write_text(json.dumps({'commit':BASE,'sha256':source_rows},indent=2)+'\n')
    app = stage / 'Muse.app'
    contents = app / 'Contents'
    resources = contents / 'Resources'
    (contents / 'MacOS').mkdir(parents=True)
    resources.mkdir()
    shutil.copytree(args.host_app, resources / 'OctoSense Host.app', symlinks=True)
    shutil.copytree(args.model_root, resources / 'local-model', symlinks=True)
    paths = ['catalog.json', artifact + '.pack.json'] + [artifact + '/' + f for f in BUNDLE_FILES]
    for rel in paths:
        assert sha(args.mirror / rel) == locked['mirror_files'][rel]
        out = resources / 'mirror' / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.mirror / rel, out)
    run('/usr/bin/clang', '-fobjc-arc', '-mmacosx-version-min=14.0', '-framework', 'AppKit',
        HERE / 'runtime/muse_launcher.m', '-o', contents / 'MacOS/muse-launcher')
    info = dict(CFBundleIdentifier='org.xinghai.muse.tmall.rc10', CFBundleExecutable='muse-launcher',
                CFBundleName='Muse', CFBundleDisplayName='Muse', CFBundlePackageType='APPL',
                CFBundleShortVersionString='0.3.27', CFBundleVersion='10',
                CFBundleDevelopmentRegion='zh_CN', LSMinimumSystemVersion='14.0', LSUIElement=True,
                NSCalendarsUsageDescription='Muse 在你授权后读取系统日历，在确认后安排或修改事件并读回核对。',
                NSCalendarsFullAccessUsageDescription='Muse 在你授权后读取系统日历，在确认后安排或修改事件并读回核对。')
    (contents / 'Info.plist').write_bytes(plistlib.dumps(info))
    run('/usr/bin/codesign', '--force', '--sign', '-', app)
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', app)
    assert inventory(resources / 'OctoSense Host.app') == locked['host_files']
    assert inventory(resources / 'local-model') == model['files']
    rows = inventory(stage)
    audit = scan(stage)
    archive = stage.parent / (stage.name + '.zip')
    assert not archive.exists(), 'Preserve an existing ZIP'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, item in sorted(rows.items()):
            entry = zipfile.ZipInfo(stage.name + '/' + rel)
            entry.create_system = 3
            entry.external_attr = ((stat.S_IFLNK if item['kind'] == 'link' else stat.S_IFREG) | item['mode']) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(entry, item['target'].encode() if item['kind'] == 'link' else (stage / rel).read_bytes())
    assert archive.stat().st_size < 500_000_000, 'Delivery ZIP must stay below 500 MB (decimal)'
    fresh = Path(tempfile.mkdtemp(prefix='tmall-clean-restore-', dir=HERE / '.local-state'))
    run('/usr/bin/ditto', '-x', '-k', archive, fresh)
    restored = fresh / stage.name
    assert inventory(restored) == rows
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', restored / 'Muse.app')
    checked = run('/bin/sh', restored / 'RUN_MUSE.command', '--check')
    result = dict(status='PASS_SCOPED_PACKAGING', product_status='PARTIAL', base_commit=BASE,
                  zip_bytes=archive.stat().st_size, zip_sha256=sha(archive), zip_path=str(archive),
                  files=len(rows), clean_restore_exact=True, signature_and_entry_check=checked.strip(),
                  model_bundled=True, model=model['model_id'], below_500_MB=True,
                  model_files_exact=True, host_files_exact=True,
                  GUI_opened=False, model_called=False, private_profiles_copied=False,
                  scan=audit, receiving_mac_tested=False)
    record = HERE / '.local-state/PACKAGING_RESULT.json'
    record.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    # This directory is exclusively a generated, verified restore of this ZIP.
    shutil.rmtree(fresh)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
