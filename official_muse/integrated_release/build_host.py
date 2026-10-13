#!/usr/bin/env python3
"""Build the paired SDK with its official packaged-resource configuration."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

FEATURES = 'app-hub,octos-core'


def packaging(sdk):
    spec = importlib.util.spec_from_file_location('sdk_packaging', sdk / 'desktop/scripts/package.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--online', action='store_true', help='Allow Cargo to download the locked public dependencies')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    sdk, target, output = (p.resolve() for p in (args.sdk, args.target, args.out))
    output.mkdir(parents=True, exist_ok=True)
    package = packaging(sdk)
    env = package.build_env(package.package_env('macos', sdk, os.environ), os.environ)
    env['CARGO_TARGET_DIR'] = str(target)
    env['CARGO_BUILD_JOBS'] = str(args.jobs)
    command = ['cargo', 'build', '--locked', '--release', '-p', 'octosense',
        '--bin', 'octosense', '--no-default-features', '--features', FEATURES]
    if not args.online:
        command.append('--offline')
    lock = sdk / 'Cargo.lock'
    lock_sha = hashlib.sha256(lock.read_bytes()).hexdigest()
    start = time.monotonic()
    with (output / 'host-build.log').open('w') as log:
        result = subprocess.run(command, cwd=sdk, env=env, stdout=log, stderr=subprocess.STDOUT)
    receipt = {'command': command, 'elapsed_seconds': round(time.monotonic() - start, 3),
        'exit_code': result.returncode, 'lock_sha256': lock_sha,
        'packaged_resources': True, 'path_remapping': True, 'status': 'BUILD_FAILED'}
    assert hashlib.sha256(lock.read_bytes()).hexdigest() == lock_sha, 'Build changed Cargo.lock'
    if result.returncode == 0:
        binary = output / 'octosense'
        shutil.copy2(target / 'release/octosense', binary)
        receipt.update(status='BUILT_NOT_RUNTIME_VERIFIED',
            host_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), host_bytes=binary.stat().st_size)
    (output / 'host-build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
