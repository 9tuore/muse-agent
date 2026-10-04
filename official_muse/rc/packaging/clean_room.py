#!/usr/bin/env python3
"""Fetch an exact committed tree into a new directory, then build without old caches."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.parse import urlparse


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='Public HTTPS Git URL or relative committed local Git repository')
    parser.add_argument('--commit', required=True, help='Coordinator-approved final full commit SHA')
    parser.add_argument('--directory', type=Path, required=True, help='New directory; never reuse an existing checkout')
    parser.add_argument('--publisher-key', action='append', default=[], help='Repeatable public id=64-hex Ed25519 verification key; no key files are read')
    args = parser.parse_args()
    for pair in args.publisher_key:
        identity, separator, public = pair.partition('=')
        assert separator and identity and re.fullmatch(r'[0-9a-fA-F]{64}', public), 'Expected public publisher id=64-hex key'
    assert re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', args.commit), 'Use the exact final commit, not HEAD or a branch'
    source = urlparse(args.source)
    if source.scheme:
        assert source.scheme == 'https' and not source.username and not source.password and not source.query and not source.fragment
        git_source = args.source
    else:
        assert not Path(args.source).is_absolute(), 'Pass the seed Git repository as a relative location'
        git_source = str(Path(args.source).resolve())
    assert not args.directory.exists(), 'Do not reuse or reset any existing directory'
    args.directory.mkdir(parents=True)
    root = args.directory.resolve(); checkout = root / 'checkout'; checkout.mkdir()
    logs = root / 'evidence'; logs.mkdir()
    # Cargo searches parent directories as well as CARGO_HOME. Refuse external
    # configuration rather than silently inheriting a machine-specific setup.
    for parent in checkout.parents:
        for name in ('config', 'config.toml'):
            assert not (parent / '.cargo' / name).exists(), 'External parent Cargo configuration is not allowed'
    # HOME stays unchanged solely for the installed rustup/toolchain and system tools.
    # Cargo/git configuration and dependency caches are isolated; no credentials are copied.
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'RUSTUP_HOME') if k in os.environ}
    env.update({'CARGO_HOME': str(root / 'cargo-home'), 'CARGO_TARGET_DIR': str(checkout / 'build/clean-target'), 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_TERMINAL_PROMPT': '0', 'LC_ALL': 'C', 'TZ': 'UTC'})
    records = []

    def run(name, command, cwd=checkout):
        started = time.monotonic()
        free_before = shutil.disk_usage(root).free
        with (logs / f'{name}.log').open('x') as log:
            result = subprocess.run(command, cwd=cwd, env=env, stdout=log, stderr=log)
        records.append({'name': name, 'command': command, 'cwd_relative_to_checkout': str(cwd.relative_to(checkout)), 'exit_code': result.returncode, 'seconds': time.monotonic() - started, 'disk_free_before_bytes': free_before, 'disk_free_after_bytes': shutil.disk_usage(root).free, 'log_sha256': sha(logs / f'{name}.log')})
        (logs / 'progress.json').write_text(json.dumps(records, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError(f'{name} failed; original log is preserved')

    status = 'FAIL'
    try:
        run('git-init', ['git', 'init'])
        run('git-fetch-final', ['git', 'fetch', '--depth=1', git_source, args.commit])
        run('git-checkout-final', ['git', 'checkout', '--detach', 'FETCH_HEAD'])
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, env=env, text=True).strip()
        assert actual == args.commit
        run('tool-versions', ['python3', '-c', 'import subprocess; [subprocess.run(c,check=True) for c in [["rustc","--version"],["cargo","--version"],["python3","--version"],["xcrun","--show-sdk-version"],["clang","--version"]]]'])
        run('sdk-bootstrap', ['python3', 'scripts/bootstrap_sdk.py'])
        run('sdk-verify-before', ['python3', 'scripts/bootstrap_sdk.py', '--verify'])
        source_lock_sha = sha(checkout / 'dependencies.lock.json')
        cargo_locks = {name: sha(checkout / 'vendor' / name / 'Cargo.lock') for name in ('octosense', 'app-hub')}
        for name in ('octosense', 'app-hub'):
            run(f'cargo-fetch-{name}', ['cargo', 'fetch', '--locked'], checkout / 'vendor' / name)
        run('host-build', ['cargo', 'build', '--release', '--locked', '--offline', '-j', '2', '-p', 'octosense', '--bin', 'octosense', '--no-default-features', '--features', 'app-hub'], checkout / 'vendor/octosense')
        manifest = json.loads((checkout / 'official_muse/app/bundle/manifest.json').read_text())
        delivery = checkout / 'build/clean-delivery'; delivery.mkdir()
        shutil.copytree(checkout / 'official_muse/app/bundle', delivery / 'bundle', symlinks=True)
        run('package-host', ['python3', 'official_muse/rc/packaging/package_clean_host.py', '--target', 'build/clean-target', '--output', 'build/clean-delivery/Muse Host.app', '--version', manifest['version']])
        run('card-host-build', ['cargo', 'build', '--release', '--locked', '--offline', '-j', '2', '-p', 'octosense-card-host', '--bin', 'card-host'], checkout / 'vendor/app-hub')
        run('package-card-host', ['python3', 'official_muse/rc/packaging/package_clean_host.py', '--kind', 'card', '--target', 'build/clean-target', '--output', 'build/clean-delivery/Muse Card Host.app', '--version', manifest['version']])
        run('hub-build', ['cargo', 'build', '--locked', '--offline', '-j', '2', '-p', 'octosense-app-hub', '--bin', 'hub'], checkout / 'vendor/app-hub')
        run('sdk-verify-after', ['python3', 'scripts/bootstrap_sdk.py', '--verify'])
        assert sha(checkout / 'dependencies.lock.json') == source_lock_sha
        assert all(sha(checkout / 'vendor' / name / 'Cargo.lock') == value for name, value in cargo_locks.items())
        hub = checkout / 'build/clean-target/debug/hub'; shutil.copy2(hub, delivery / 'hub')
        # Reproducibility check preserves the final committed bytes. No stamp or signing of a changed manifest.
        command = [str(hub), 'check', 'build/clean-delivery/bundle', '--allow-unsigned']
        for pair in args.publisher_key:
            command.extend(['--publisher-key', pair])
        run('hub-check-final', command)
        dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=checkout, env=env, text=True)
        assert not dirty, 'No tracked source or lock changes are allowed'
        status = 'CLEAN_BUILD_PASS_LOCAL_EXTENDED_HUB'
    finally:
        check = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=checkout, env=env, capture_output=True, text=True)
        result = {'status': status, 'requested_commit': args.commit, 'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'steps': records, 'fresh_cargo_home': True, 'fresh_target': True, 'old_vendor_or_targets_used': False, 'publisher_public_keys_arguments': args.publisher_key, 'publisher_identity_scope': 'explicit local-development verification only; no formal publisher continuity claim', 'private_key_or_real_account_used': False, 'tracked_source_changes': check.stdout if check.returncode == 0 else 'UNVERIFIED', 'evidence_path': str(logs), 'disk_free_final_bytes': shutil.disk_usage(root).free}
        (logs / 'CLEAN_REPRODUCIBILITY_REPORT.json').write_text(json.dumps(result, indent=2) + '\n')
        (logs / 'CLEAN_REPRODUCIBILITY_REPORT.md').write_text('# Clean reproducibility\n\nStatus: '+status+'\n\nCommit: `'+args.commit+'`\n\nFresh SDK/download/cache/target. No UI or external actions. Local extended Hub only. Individual original logs are preserved beside this report.\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
