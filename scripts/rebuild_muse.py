#!/usr/bin/env python3
"""Build a portable native Muse candidate from pinned source and public inputs.

Fresh local catalog keys belong only to the build directory. No user profile or
developer signing key is needed. Existing accounts are never copied into the app.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / 'official_muse/integrated_release'
sys.path.insert(0, str(INTEGRATION))
from build_host import packaging, FEATURES


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True, help='New build directory inside this repository')
    p.add_argument('--model-source', type=Path, required=True, help='Public Qwen weights, llama.cpp runtime and their licenses')
    p.add_argument('--offline', action='store_true')
    p.add_argument('--jobs', type=int, default=2)
    p.add_argument('--kernel', type=Path, help='Optional prebuilt kernel; upstream verifies its exact pinned revision')
    p.add_argument('--host', type=Path, help='Optional explicitly built Host from this SDK')
    p.add_argument('--hub', type=Path, help='Optional Hub CLI from the pinned SDK')
    p.add_argument('--publisher', type=Path, help='Optional compiled muse_local_catalog helper')
    p.add_argument('--licenses', type=Path, help='Collected licenses for the pinned dependency set')
    a = p.parse_args()
    work = a.work.resolve()
    work.relative_to(ROOT / 'build')
    work.mkdir(parents=True, exist_ok=False)
    sdk = ROOT / '.local/sdk'
    commands = []

    def run(argv, cwd=ROOT, env=None, capture=False):
        argv = [str(x) for x in argv]
        # No key contents are arguments: only private file paths and public keys.
        commands.append(argv)
        (work / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        if capture:
            return subprocess.check_output(argv, cwd=cwd, env=env)
        with (work / 'build.log').open('ab') as log:
            subprocess.run(argv, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)

    run([sys.executable, ROOT / 'scripts/bootstrap_sdk.py', '--use-cargo-cache'])
    package = packaging(sdk)
    env = package.build_env(package.package_env('macos', sdk, os.environ), os.environ)
    env.update(CARGO_TARGET_DIR=str(ROOT / '.local/host-target'), CARGO_BUILD_JOBS=str(a.jobs))
    offline = ['--offline'] if a.offline else []
    host = a.host.resolve() if a.host else work / 'host/octosense'
    if not a.host:
        run([sys.executable, INTEGRATION / 'build_host.py', '--sdk', sdk,
             '--target', ROOT / '.local/host-target', '--out', work / 'host', '--jobs', a.jobs,
             *([] if a.offline else ['--online'])])
    hub = a.hub.resolve() if a.hub else ROOT / '.local/host-target/release/hub'
    if not a.hub:
        run(['cargo', 'build', '--locked', '--release', '-p', 'octosense-app-hub', '--bin', 'hub', *offline], sdk, env)
    kernel_cmd = [sys.executable, sdk / 'tools/kernel-artifact.py', '--host', '--work', work / 'kernel-build',
                  '--stage', work / 'kernel', *offline]
    if a.kernel:
        kernel_cmd += ['--kernel', a.kernel.resolve()]
    run(kernel_cmd, sdk)
    publisher = a.publisher.resolve() if a.publisher else work / 'muse_local_catalog'
    if not a.publisher:
        deps = ROOT / '.local/host-target/release/deps'
        argv = ['rustc', '--edition=2021', '-O', INTEGRATION / 'muse_local_catalog.rs', '-L', 'dependency=' + str(deps)]
        for crate in ['octosense_app_hub', 'octosense_app_policy', 'serde_json', 'hex']:
            libs = list(deps.glob('lib' + crate + '-*.rlib'))
            if len(libs) != 1:
                raise RuntimeError(f'{crate}: select an unambiguous matching build in a fresh target directory')
            argv += ['--extern', crate + '=' + str(libs[0])]
        run([*argv, '-o', publisher])
    run([sys.executable, INTEGRATION / 'prepare_bundle.py', '--out', work / 'source'])
    bundle = work / 'source/bundle'
    private = work / 'private'
    private.mkdir(mode=0o700)
    public = {}
    for name in ['anchor', 'working', 'publisher']:
        public[name] = run([hub, 'keygen', private / (name + '.key')], capture=True).decode().strip()
    certificate = run([hub, 'certify', '--anchor', private / 'anchor.key', '--working', private / 'working.key'], capture=True)
    (private / 'working.cert').write_bytes(certificate)
    (private / 'anchor.pub').write_text(public['anchor'] + '\n')
    run([hub, 'stamp', bundle])
    run([hub, 'sign-manifest', bundle, '--key', private / 'publisher.key', '--key-id', 'muse-integrated-local'])
    commit = run(['git', 'rev-parse', 'HEAD'], capture=True).decode().strip()
    run([publisher, bundle, work / 'mirror', private / 'working.key', private / 'working.cert',
         private / 'anchor.pub', commit, public['publisher'], '1'])
    licenses = a.licenses.resolve() if a.licenses else work / 'licenses'
    if not a.licenses:
        metadata = run(['cargo', 'metadata', '--locked', '--format-version', '1',
                        '--no-default-features', '--features', FEATURES, *offline], sdk, env, True)
        (work / 'metadata.json').write_bytes(metadata)
        if a.kernel:
            raise RuntimeError('A prebuilt kernel needs --licenses for its matching dependency set')
        kernel_sources = [p for p in (work / 'kernel-build').iterdir() if (p / 'Cargo.toml').is_file()]
        if len(kernel_sources) != 1:
            raise RuntimeError('Cannot identify the pinned kernel source for license collection')
        run([sys.executable, INTEGRATION / 'collect_licenses.py', '--metadata', work / 'metadata.json',
             '--sdk', sdk, '--kernel-source', kernel_sources[0], '--out', licenses])
    run([sys.executable, INTEGRATION / 'package_app.py', '--sdk', sdk, '--host', host,
         '--kernel', work / 'kernel/octos-kernel', '--kernel-receipt', work / 'kernel/octos-kernel.json',
         '--mirror', work / 'mirror', '--out', work / 'package', '--model-source', a.model_source.resolve(),
         '--licenses', licenses, '--hub-anchor', public['anchor'], '--apfs-clone'])
    print(work / 'package/Muse.app')


if __name__ == '__main__':
    main()
