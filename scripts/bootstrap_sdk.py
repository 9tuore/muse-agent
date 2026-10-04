#!/usr/bin/env python3
"""Restore pinned official SDKs and verified local overlays; never touch user data."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def tree_digest(root):
    rows = []
    for folder, dirs, files in os.walk(root, followlinks=False):
        for name in dirs[:]:
            path = Path(folder) / name
            if path.is_symlink():
                dirs.remove(name)
                files.append(name)
        for name in files:
            path = Path(folder) / name
            mode = '120000' if path.is_symlink() else '100755' if path.stat().st_mode & 0o111 else '100644'
            value = hashlib.sha256(os.readlink(path).encode()).hexdigest() if path.is_symlink() else digest(path)
            rows.append([path.relative_to(root).as_posix(), mode, value])
    payload = json.dumps(sorted(rows), separators=(',', ':'), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest(), len(rows)


def safe_path(root, name):
    parts = PurePosixPath(name)
    if parts.is_absolute() or not parts.parts or any(p in ('.', '..', '.git') for p in parts.parts) or '\\' in name:
        raise ValueError('Unsafe SDK path: ' + name)
    path = root / name
    if any(p.is_symlink() for p in path.parents if p != root and root in p.parents):
        raise ValueError('Symlink parent: ' + name)
    return path


def extract(archive, destination, prefix):
    """Write ordinary files first; links only after their targets are validated."""
    links, seen = [], set()
    with tarfile.open(archive, 'r:*') as source:
        for member in source:
            parts = PurePosixPath(member.name).parts
            if prefix:
                parts = parts[1:]
            if not parts:
                continue
            name = '/'.join(parts)
            if name in seen:
                raise ValueError('Duplicate SDK entry: ' + name)
            seen.add(name)
            path = safe_path(destination, name)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                path.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as stream, path.open('wb') as output:
                    shutil.copyfileobj(stream, output)
                path.chmod(0o755 if member.mode & 0o111 else 0o644)
            elif member.issym():
                links.append((path, member.linkname))
            else:
                raise ValueError('Unsupported SDK archive entry: ' + name)
    for path, target in links:
        if PurePosixPath(target).is_absolute() or '\\' in target:
            raise ValueError('Unsafe SDK link')
        resolved = (path.parent / target).resolve()
        if destination.parent != resolved and destination.parent not in resolved.parents:
            raise ValueError('SDK link escapes vendor')
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            path.unlink()
        path.symlink_to(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-dir', type=Path, help='Optional cache of exact pinned upstream tar/tar.gz archives')
    parser.add_argument('--verify', action='store_true', help='Verify an already restored vendor tree without downloading')
    args = parser.parse_args()
    lock = json.loads((ROOT / 'dependencies.lock.json').read_text())
    vendor = ROOT / 'vendor'
    if vendor.exists():
        for entry in lock['dependencies']:
            actual, count = tree_digest(vendor / entry['name'])
            if actual != entry['tree_sha256'] or count != entry['files']:
                raise ValueError('Existing SDK differs; preserve local changes before restoring: ' + entry['name'])
        print(json.dumps({'status': 'SDK_VERIFIED', 'files': sum(e['files'] for e in lock['dependencies'])}))
        return
    if args.verify:
        raise FileNotFoundError('SDK absent; run bootstrap without --verify first')
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    cache = args.archive_dir.resolve() if args.archive_dir else build / 'sdk-archives'
    cache.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='sdk-stage-', dir=build))
    try:
        for entry in lock['dependencies']:
            name = entry['name']
            archive = next((p for p in (cache / (name + '.tar'), cache / (name + '.tar.gz')) if p.is_file()), None)
            if archive is None:
                archive = cache / (name + '.tar.gz')
                partial = archive.with_suffix('.partial')
                print('Downloading ' + name + ' @ ' + entry['commit'], flush=True)
                with urllib.request.urlopen(entry['archive_url'], timeout=60) as response, partial.open('wb') as output:
                    shutil.copyfileobj(response, output)
                partial.rename(archive)
            destination = stage / name
            destination.mkdir()
            extract(archive, destination, prefix=True)
            for name_to_delete in entry['delete']:
                path = safe_path(destination, name_to_delete)
                if path.is_file() or path.is_symlink():
                    path.unlink()
            for relative, change in entry['overlay_files'].items():
                path = safe_path(destination, relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                if change['mode'] == '120000':
                    target = change['target']
                    resolved = (path.parent / target).resolve()
                    if stage != resolved and stage not in resolved.parents:
                        raise ValueError('Overlay link escapes vendor')
                    if path.is_symlink():
                        path.unlink()
                    path.symlink_to(target)
                else:
                    source = safe_path(ROOT / 'sdk-overlays' / name, relative)
                    if digest(source) != change['sha256']:
                        raise ValueError('Overlay hash mismatch: ' + name + '/' + relative)
                    shutil.copyfile(source, path)
                    path.chmod(0o755 if change['mode'] == '100755' else 0o644)
            actual, count = tree_digest(destination)
            if actual != entry['tree_sha256'] or count != entry['files']:
                raise ValueError('Restored SDK differs from approved tree: ' + name)
            print(json.dumps({'sdk': name, 'status': 'EXACT_TREE_PASS', 'files': count}), flush=True)
        stage.rename(vendor)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print('SDK restored. Local extensions remain separate from official upstream acceptance.')


if __name__ == '__main__':
    main()
