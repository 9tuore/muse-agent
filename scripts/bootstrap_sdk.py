#!/usr/bin/env python3
"""Restore or verify the exact SDK used by the independent Muse candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args])


def seed_cargo_cache(repo, entry):
    """Reuse public Git objects, then dissociate before delivering the checkout."""
    prefix = {'sdk': 'octosense', 'app-hub': 'octosense-app-hub'}.get(entry['name'], entry['name'])
    candidates = sorted((Path.home() / '.cargo/git/db').glob(prefix + '-*'))
    candidates = [p for p in candidates if len(p.name) == len(prefix) + 17]
    if not candidates:
        return False
    info = repo / '.git/objects/info'
    info.mkdir(exist_ok=True)
    (info / 'alternates').write_text(''.join(str(p / 'objects') + '\n' for p in candidates))
    for i, cache in enumerate(candidates):
        refs = subprocess.check_output(['git', '--git-dir', str(cache), 'for-each-ref', '--format=%(objectname)']).decode().splitlines()
        for j, revision in enumerate(refs):
            git(repo, 'update-ref', f'refs/cache/{i}-{j}', revision)
    return subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', entry['commit'] + '^{commit}'], capture_output=True).returncode == 0


def verify(destination, entries):
    for entry in entries:
        repo = destination if entry['name'] == 'sdk' else destination / '.sources' / entry['name']
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == entry['commit'], entry['name'] + ': revision differs'
        patch = ROOT / entry['patch']
        assert hashlib.sha256(patch.read_bytes()).hexdigest() == entry['patch_sha256'], entry['name'] + ': patch differs'
        assert git(repo, 'diff', 'HEAD', '--binary') == patch.read_bytes(), entry['name'] + ': source changes differ; preserve them before restoring'
    print(json.dumps({'status': 'EXACT_CURRENT_SDK_VERIFIED', 'repositories': len(entries)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=ROOT / '.local/sdk')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--use-cargo-cache', action='store_true', help='Reuse public Cargo Git objects; checkout is made independent afterwards')
    args = parser.parse_args()
    destination = args.destination.resolve()
    destination.relative_to(ROOT)
    entries = json.loads((ROOT / 'dependencies.lock.json').read_text())['dependencies']
    if destination.exists():
        verify(destination, entries)
        return
    if args.verify:
        raise SystemExit('SDK absent; restore it first.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='sdk-restore-', dir=destination.parent) as temporary:
        stage = Path(temporary) / 'sdk'
        for entry in entries:
            repo = stage if entry['name'] == 'sdk' else stage / '.sources' / entry['name']
            repo.mkdir(parents=True)
            git(repo, 'init', '--quiet')
            git(repo, 'remote', 'add', 'origin', entry['repository'])
            cached = args.use_cargo_cache and seed_cargo_cache(repo, entry)
            if not cached:
                git(repo, 'fetch', '--depth', '1', 'origin', entry['commit'])
            git(repo, 'checkout', '--detach', '--quiet', entry['commit'])
            alternates = repo / '.git/objects/info/alternates'
            if alternates.exists():
                for ref in git(repo, 'for-each-ref', '--format=%(refname)', 'refs/cache').decode().splitlines():
                    git(repo, 'update-ref', '-d', ref)
                git(repo, 'repack', '-a', '-d', '--quiet')
                alternates.unlink()
            patch = ROOT / entry['patch']
            assert hashlib.sha256(patch.read_bytes()).hexdigest() == entry['patch_sha256']
            if patch.stat().st_size:
                git(repo, 'apply', '--index', '--binary', str(patch))
        verify(stage, entries)
        stage.rename(destination)


if __name__ == '__main__':
    main()
