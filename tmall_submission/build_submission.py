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
import shutil
import stat
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = '7175af663c55703959b481791a304196343df5b6'
HOST_SHA = '1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3'
PAYLOAD_SHA = 'ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da'
BUNDLE_FILES = ['assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
                'screenshots/01-main.png', 'screenshots/02-global-memory.png']
DOCS = ['README.md', 'PROJECT_INTRO.md', 'AI_PRACTICE.md', 'ARCHITECTURE.md',
        'RUN_GUIDE.md', 'KNOWN_LIMITATIONS.md', 'DEMO_SCRIPT.md', 'TMALL_DEMO_SCRIPT.md',
        'TECH_STACK.md', 'FORM_AI_PRACTICE_300.txt', 'FORM_PROJECT_INTRO_500.txt',
        'RUN_MUSE.command', 'ACCEPTANCE.md', 'VERIFICATION.json', 'build_submission.py',
        'build_overview.py', 'tests/test_entry.py', 'runtime/README.md', 'runtime/RUNTIME_LOCK.json',
        'source/SOURCE_MANIFEST.md', 'source/SOURCE_MANIFEST.json',
        'assets/cover.png', 'assets/diagrams/architecture.svg', 'assets/diagrams/architecture.png',
        'assets/screenshots/README.md', 'assets/screenshots/01-main.png',
        'assets/screenshots/07-memory-recall.png', 'assets/screenshots/MEDIA_PROVENANCE.json',
        'demo/README.md', 'demo/Muse-Tmall-Overview.zh-CN.mp4',
        'demo/Muse-Tmall-Overview.zh-CN.srt', 'demo/OVERVIEW_PROVENANCE.json',
        'demo/Muse-rc51-real-excerpt.zh-CN.mp4']


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
        assert not p.name.endswith(('.key', '.pem', '.sqlite', '.db', '.log', '.gguf'))
        if p.is_file() and p.suffix in ('.md', '.txt', '.json', '.command', '.py', '.svg', '.splash', '.srt', '.plist'):
            data = p.read_bytes()
            assert not any(re.search(pattern, data) for pattern in patterns), str(p)
            for address in emails.findall(data):
                # No human addresses permitted. XML/Apple identifiers are not email contacts.
                reviewed.add(address.decode())
    assert not reviewed, 'Unexpected email-like contact in public allowlist'
    return dict(high_confidence_secret_matches=0, email_contacts=sorted(reviewed),
                scope='allowlisted text and paths; media separately visually reviewed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-app', type=Path, required=True)
    parser.add_argument('--mirror', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    assert sha(args.host_app / 'Contents/MacOS/octosense') == HOST_SHA
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', args.host_app)
    locked = json.loads((HERE / 'runtime/RUNTIME_LOCK.json').read_text())
    assert inventory(args.host_app) == locked['host_files']
    catalog = json.loads((args.mirror / 'catalog.json').read_text())
    selected = [e for e in catalog['entries'] if e['manifest']['id'] == 'muse-goals'
                and e['manifest']['version'] == '0.3.26-rc51']
    assert len(selected) == 1
    entry = selected[0]
    artifact = 'artifacts/muse-goals-0.3.26-rc51.bundle'
    assert entry['artifact'] == artifact
    assert sha(args.mirror / artifact / 'main.splash') == PAYLOAD_SHA
    for rel in BUNDLE_FILES:
        expected = subprocess.check_output(['git', 'show', BASE + ':official_muse/app/bundle/' + rel], cwd=ROOT)
        assert (args.mirror / artifact / rel).read_bytes() == expected
    stage = args.destination.resolve()
    assert not stage.exists(), 'Preserve existing delivery; choose a new destination'
    stage.mkdir(parents=True)
    for rel in DOCS:
        out = stage / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / rel, out)
    shutil.copytree(args.host_app, stage / 'runtime/OctoSense Host.app', symlinks=True)
    paths = ['catalog.json', artifact + '.pack.json'] + [artifact + '/' + f for f in BUNDLE_FILES]
    for rel in paths:
        assert sha(args.mirror / rel) == locked['mirror_files'][rel]
        out = stage / 'runtime/mirror' / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.mirror / rel, out)
    rows = inventory(stage)
    audit = scan(stage)
    archive = stage.parent / 'Muse-Tmall-Submission.zip'
    assert not archive.exists(), 'Preserve an existing ZIP'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, item in sorted(rows.items()):
            entry = zipfile.ZipInfo(stage.name + '/' + rel)
            entry.create_system = 3
            entry.external_attr = ((stat.S_IFLNK if item['kind'] == 'link' else stat.S_IFREG) | item['mode']) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(entry, item['target'].encode() if item['kind'] == 'link' else (stage / rel).read_bytes())
    fresh = Path(tempfile.mkdtemp(prefix='tmall-clean-restore-', dir=HERE / '.local-state'))
    run('/usr/bin/ditto', '-x', '-k', archive, fresh)
    restored = fresh / stage.name
    assert inventory(restored) == rows
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', restored / 'runtime/OctoSense Host.app')
    checked = run('/bin/sh', restored / 'RUN_MUSE.command', '--check')
    result = dict(status='PASS_SCOPED_PACKAGING', product_status='PARTIAL', base_commit=BASE,
                  zip_bytes=archive.stat().st_size, zip_sha256=sha(archive), zip_path=str(archive),
                  files=len(rows), clean_restore_exact=True, signature_and_entry_check=checked.strip(),
                  GUI_opened=False, model_called=False, private_profiles_copied=False,
                  scan=audit, receiving_mac_tested=False)
    record = HERE / '.local-state/PACKAGING_RESULT.json'
    record.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    # This directory is exclusively a generated, verified restore of this ZIP.
    shutil.rmtree(fresh)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
