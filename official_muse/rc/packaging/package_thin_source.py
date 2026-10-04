#!/usr/bin/env python3
"""Export signed application material and frozen public source without a Host copy."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ANCHOR = '3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'
PUBLISHER = 'muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5'
RESERVE = 64 * 1024**2
FILES = ['assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
         'screenshots/01-main.png', 'screenshots/02-global-memory.png']


def git(commit, path):
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare(args):
    for commit in [args.commit, args.application_commit]:
        assert len(commit) == 40 and int(commit, 16) >= 0
    manifest = json.loads(git(args.application_commit, 'official_muse/app/bundle/manifest.json'))
    version = manifest['version']
    assert manifest['id'] == 'muse-goals' and isinstance(version, str) and version
    assert '/' not in version and '\\' not in version
    artifact = f'artifacts/muse-goals-{version}.bundle'
    mirror = args.mirror.resolve()
    catalog = json.loads((mirror / 'catalog.json').read_text())
    entries = [e for e in catalog['entries'] if e['manifest']['id'] == 'muse-goals'
               and e['manifest']['version'] == version]
    assert len(entries) == 1
    entry = entries[0]
    assert entry['source']['commit'] == args.application_commit
    assert entry['artifact'] == artifact and entry['manifest'] == manifest
    pack = json.loads((mirror / (artifact + '.pack.json')).read_text())
    assert sorted(pack['files']) == sorted(FILES)
    for rel in FILES:
        data = git(args.application_commit, 'official_muse/app/bundle/' + rel)
        assert (mirror / artifact / rel).read_bytes() == data
        assert git(args.commit, 'official_muse/app/bundle/' + rel) == data
        assert base64.b64decode(pack['files'][rel], validate=True) == data
    hub = HERE / '.local-state/tools/hub'
    subprocess.run([str(hub), 'verify', str(mirror / 'catalog.json'), '--anchor', ANCHOR], check=True)
    subprocess.run([str(hub), 'check', str(mirror / artifact), '--publisher-key', PUBLISHER], check=True)
    rows = {}
    tree = subprocess.check_output(['git', 'ls-tree', '-r', '-l', '-z', args.commit], cwd=ROOT)
    for line in tree.split(b'\0'):
        if not line:
            continue
        meta, name = line.split(b'\t', 1)
        mode, kind, blob, length = meta.decode().split()
        path = name.decode('utf8')
        assert mode in ['100644', '100755'] and kind == 'blob'
        assert not Path(path).is_absolute() and '..' not in Path(path).parts
        assert not set(Path(path).parts) & {'private', 'profiles', 'vendor', 'target', 'cargo-home', '.local-state'}
        assert not path.endswith('.gguf')
        rows[path] = {'git_blob': blob, 'bytes': int(length), 'mode': int(mode, 8)}
    source_manifest = json.loads(git(args.commit, 'SOURCE_MANIFEST.json'))
    assert source_manifest['version'] == version, 'SOURCE_MANIFEST version is stale'
    assert source_manifest['product_source_head'] == args.application_commit
    assert set(source_manifest['files']) == set(rows) - {'SOURCE_MANIFEST.json'}, 'SOURCE_MANIFEST inventory is stale'
    source_tar = subprocess.check_output(['git', 'archive', '--format=tar', args.commit], cwd=ROOT)
    validated = set()
    with tarfile.open(fileobj=io.BytesIO(source_tar)) as source:
        for item in source:
            if item.isdir():
                continue
            assert item.isfile() and item.name in rows and item.name not in validated
            data = source.extractfile(item).read(); row = rows[item.name]
            assert len(data) == row['bytes']
            assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob']
            if item.name != 'SOURCE_MANIFEST.json':
                assert digest(data) == source_manifest['files'][item.name], 'SOURCE_MANIFEST SHA mismatch: ' + item.name
            validated.add(item.name)
    assert validated == set(rows)
    tutorial = (HERE / 'thin_source_tutorial.html').read_text()
    for token, value in [('__VERSION__', version), ('__SOURCE_COMMIT__', args.commit),
                         ('__APPLICATION_COMMIT__', args.application_commit)]:
        tutorial = tutorial.replace(token, value)
    assert '__VERSION__' not in tutorial and '__SOURCE_COMMIT__' not in tutorial
    mirror_paths = ['catalog.json', artifact + '.pack.json'] + [artifact + '/' + x for x in FILES]
    name = f'Muse-{version}-签名材料与源码-{args.commit[:8]}-2026-10-05'
    budget = sum(row['bytes'] for row in rows.values()) + sum((mirror / p).stat().st_size for p in mirror_paths)
    return version, artifact, mirror, mirror_paths, rows, tutorial, name, budget, source_tar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True, help='Coordinator-declared frozen source export commit')
    parser.add_argument('--application-commit', required=True, help='Signed application source commit')
    parser.add_argument('--mirror', required=True, type=Path)
    parser.add_argument('--check-only', action='store_true', help='Validate public inputs without creating a ZIP')
    args = parser.parse_args()
    version, artifact, mirror, mirror_paths, rows, tutorial, name, budget, source_tar = prepare(args)
    if args.check_only:
        print(json.dumps({'status': 'STATIC_INPUTS_PASS_NO_EXPORT', 'version': version,
                          'source_commit': args.commit, 'application_commit': args.application_commit,
                          'source_files': len(rows), 'payload_bytes': budget}, ensure_ascii=False))
        return
    assert shutil.disk_usage(ROOT).free > budget + RESERVE + 4 * 1024**2, 'Thin export capacity guard failed'
    output = HERE / ('.local-state/thin-source-' + args.commit[:8])
    output.mkdir(parents=True, exist_ok=True)
    archive = output / (name + '.zip')
    pending = output / (name + '.incomplete.zip')
    assert not archive.exists() and not pending.exists(), 'Preserve earlier outputs'
    metadata = {'version': version, 'status': 'PARTIAL_MATERIALS_ONLY_NOT_STANDALONE',
                'source_export_commit': args.commit, 'application_commit': args.application_commit,
                'source_sdk_lock_sha256': digest(git(args.commit, 'dependencies.lock.json')),
                'bundle_manifest_sha256': digest(git(args.application_commit, 'official_muse/app/bundle/manifest.json')),
                'host_included': False, 'launcher_included': False, 'models_included': False,
                'old_087_zip_sha256': '127a3ffe0a5343165f659978ec450cecaeeea201467687724e56ec66e521cf17',
                'required_old_intel_host_sha256': '938ba58a204de0421b2935c974a22645de14a6b7682f1004bc72c701c3793b3d',
                'old_host_runtime_sdk_commit': 'b48618acef0ff291ad3dc23b09946b0b15fa4f2f',
                'old_host_sdk_lock_sha256': '3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e',
                'calendar_bridge_fix_in_old_host': False,
                'rc6_bound_receiver_launcher': 'NOT_INCLUDED_NOT_VERIFIED',
                'root_rc6_startup': 'COLD2_FAIL_PREPARATION_124MS',
                'receiver_two_mac_validation': 'NOT_RUN', 'clean_build': 'BLOCKED_CAPACITY',
                'formal_publication': 'NOT_PUBLISHED', 'a4_gui_or_model_calls': 'NOT_RUN'}
    expected = {}
    with zipfile.ZipFile(pending, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        def add(rel, data, mode=0o644):
            assert rel not in expected and '..' not in Path(rel).parts
            assert shutil.disk_usage(ROOT).free > RESERVE + len(data), 'Live thin export capacity guard failed'
            info = zipfile.ZipInfo(name + '/' + rel)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
            expected[rel] = {'bytes': len(data), 'sha256': digest(data), 'mode': mode}
        add('00-先看这里.html', tutorial.encode())
        add('版本与交付边界.json', json.dumps(metadata, ensure_ascii=False, indent=2).encode())
        for rel in mirror_paths:
            add('01-AppHub镜像/' + rel, (mirror / rel).read_bytes())
        copied = set()
        with tarfile.open(fileobj=io.BytesIO(source_tar)) as source:
            for item in source:
                if item.isdir():
                    continue
                assert item.isfile() and item.name in rows
                row = rows[item.name]
                data = source.extractfile(item).read()
                assert len(data) == row['bytes']
                assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob']
                # git archive applies tar.umask; the ZIP uses the frozen Git mode instead.
                add('02-最新源码/' + item.name, data, row['mode'] & 0o777)
                copied.add(item.name)
        assert copied == set(rows)
        add('文件校验清单.json', json.dumps({'self_excluded_from_own_hash': True, 'files': expected},
                                         ensure_ascii=False, indent=2).encode())
    with zipfile.ZipFile(pending) as z:
        found = set()
        for info in z.infolist():
            prefix = name + '/'
            assert info.filename.startswith(prefix)
            rel = info.filename[len(prefix):]
            assert rel in expected and rel not in found
            data = z.read(info); row = expected[rel]
            assert len(data) == row['bytes'] and digest(data) == row['sha256']
            assert ((info.external_attr >> 16) & 0o777) == row['mode']
            found.add(rel)
        assert found == set(expected)
    pending.rename(archive)
    archive_hash = hashlib.sha256()
    with archive.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            archive_hash.update(data)
    sha = archive_hash.hexdigest()
    report = {'metadata': metadata, 'archive': str(archive), 'archive_bytes': archive.stat().st_size,
              'archive_sha256': sha, 'zip_members_verified': len(expected), 'source_files': len(rows),
              'source_allowlist_rule': 'Exact frozen tracked public regular Git files; no working-tree import',
              'no_uncompressed_stage_created': True, 'full_package_600mib_guard_changed': False,
              'thin_export_reserve_bytes': RESERVE, 'free_bytes_after': shutil.disk_usage(ROOT).free}
    (HERE / ('THIN_SOURCE_RESULT_' + args.commit[:8] + '.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
