#!/usr/bin/env python3
"""Stage one signed local Muse .app from explicit, frozen public inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess

from build_host import FEATURES, packaging

HERE = Path(__file__).resolve().parent


def run(command, **kwargs):
    return subprocess.run([str(item) for item in command], check=True, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    for name in ('sdk', 'host', 'kernel', 'kernel-receipt', 'mirror', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--model-mode', choices=('offline', 'gpt', 'hybrid'), default='hybrid')
    parser.add_argument('--model-source', type=Path)
    parser.add_argument('--paired-host-app', type=Path,
        help='Copy an already signed matching Host/Kernel app and resources; no Cargo or re-signing of the pair')
    parser.add_argument('--state-root', type=Path,
        help='Reference an existing absolute state root in Info.plist; never copy its contents')
    args = parser.parse_args()
    if args.model_mode != 'gpt' and args.model_source is None:
        parser.error('--model-source is required for offline/hybrid mode')
    if args.state_root is not None and not args.state_root.is_absolute():
        parser.error('--state-root must be absolute')
    source_host_sha256 = sha(args.host)
    source_kernel_sha256 = sha(args.kernel)
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    app = output / 'Muse.app'
    resources = app / 'Contents/Resources'
    executable = app / 'Contents/MacOS'
    executable.mkdir(parents=True)
    resources.mkdir()
    sdk = args.sdk.resolve()
    receipt = json.loads(args.kernel_receipt.read_text())
    assert receipt['sha256'] == source_kernel_sha256, 'Kernel receipt mismatch'
    inner = resources / 'OctoSense Host.app/Contents'
    package = packaging(sdk)
    if args.paired_host_app:
        source = args.paired_host_app.resolve() / 'Contents'
        assert sha(source / 'MacOS/octosense') == source_host_sha256, 'Paired app Host mismatch'
        assert sha(source / 'MacOS/octos-kernel') == source_kernel_sha256, 'Paired app Kernel mismatch'
        assert (source / 'Resources/octos-kernel.json').read_bytes() == args.kernel_receipt.read_bytes(), 'Paired app receipt mismatch'
        assert receipt['revision'] == package.kernel_tool().octos_revision(), 'Kernel revision is not the SDK pin'
        run(['codesign', '--verify', '--deep', '--strict', source.parent])
        shutil.copytree(source.parent, inner.parent, symlinks=True)
    else:
        (inner / 'MacOS').mkdir(parents=True)
        env = dict(os.environ, CARGO_NET_OFFLINE='true')
        tree = subprocess.check_output(['cargo', 'tree', '--offline', '--locked', '-p', 'octosense',
            '-e', 'normal', '--prefix', 'none', '--format', '{p}', '--no-default-features',
            '--features', FEATURES], cwd=sdk, env=env, text=True)
        linked = set()
        for line in tree.splitlines():
            match = re.match(r'(\S+) v(\S+)', line.strip())
            if match:
                linked.add(match.groups())
        metadata = json.loads(subprocess.check_output(['cargo', 'metadata', '--offline', '--locked',
            '--format-version', '1', '--no-default-features', '--features', FEATURES],
            cwd=sdk, env=env, text=True))
        package.stage_resources(package.resource_crates(metadata, linked), inner / 'Resources')
        shutil.copy2(args.host, inner / 'MacOS/octosense')
        shutil.copy2(args.kernel, inner / 'MacOS/octos-kernel')
        shutil.copy2(args.kernel_receipt, inner / 'Resources/octos-kernel.json')
    assert sha(inner / 'MacOS/octosense') == source_host_sha256, 'Host input changed while staging'
    if args.model_mode != 'gpt':
        shutil.copytree(args.model_source, resources / 'local-model', symlinks=True)
    shutil.copytree(args.mirror, resources / 'mirror', symlinks=True)
    # Local signing keys and account data are not inputs to this packager.
    assert not list(resources.rglob('*.key')), 'A private key entered the package'
    plist = dict(CFBundleName='Muse', CFBundleDisplayName='Muse', CFBundleExecutable='muse-launcher',
        CFBundleIdentifier='org.xinghai.muse.integrated', CFBundlePackageType='APPL',
        CFBundleShortVersionString='0.4.0', CFBundleVersion='4', LSMinimumSystemVersion='14.0',
        NSHighResolutionCapable=True, MuseModelMode=args.model_mode)
    if args.paired_host_app:
        plist['MuseHostLaunchMethod'] = 'workbuddy'
    if args.state_root is not None:
        plist['MuseStateRoot'] = str(args.state_root)
    with (app / 'Contents/Info.plist').open('wb') as stream:
        plistlib.dump(plist, stream)
    host_plist = dict(plist, CFBundleName='OctoSense', CFBundleDisplayName='OctoSense',
        CFBundleExecutable='octosense', CFBundleIdentifier='org.xinghai.muse.paired-host')
    if not args.paired_host_app:
        with (inner / 'Info.plist').open('wb') as stream:
            plistlib.dump(host_plist, stream)
    else:
        wrapper = resources / 'WorkBuddy Launcher.app/Contents'
        (wrapper / 'MacOS').mkdir(parents=True)
        wrapper_plist = dict(host_plist, CFBundleExecutable='Launcher',
            CFBundleIdentifier='org.xinghai.muse.workbuddy-launcher')
        with (wrapper / 'Info.plist').open('wb') as stream:
            plistlib.dump(wrapper_plist, stream)
        shutil.copy2(HERE / 'workbuddy_launcher.sh', wrapper / 'MacOS/Launcher')
        (wrapper / 'MacOS/Launcher').chmod(0o755)
        run(['codesign', '--force', '--sign', '-', wrapper.parent])
    run(['clang', '-fobjc-arc', '-O2', '-framework', 'AppKit', HERE / 'muse_launcher.m',
        '-o', executable / 'muse-launcher'])
    # Sign only our staged copy, then ask the official staging helper to
    # re-attest the same pinned revision and the resulting binary bytes.
    if not args.paired_host_app:
        run(['codesign', '--force', '--sign', '-', inner / 'MacOS/octos-kernel'])
        kernel_tool = package.kernel_tool()
        signed_receipt = kernel_tool.stage(inner / 'MacOS/octos-kernel', output / 'signed-kernel',
            kernel_tool.octos_revision(), 'prebuilt')
        shutil.copy2(output / 'signed-kernel/octos-kernel.json', inner / 'Resources/octos-kernel.json')
        run(['codesign', '--force', '--sign', '-', inner.parent])
    else:
        signed_receipt = receipt
    run(['codesign', '--force', '--sign', '-', app])
    run(['codesign', '--verify', '--deep', '--strict', app])
    assert sha(inner / 'MacOS/octos-kernel') == signed_receipt['sha256'], 'Packaging changed the pinned kernel'
    if args.paired_host_app:
        assert sha(inner / 'MacOS/octosense') == source_host_sha256, 'Packaging changed the working Host'
        assert sha(inner / 'MacOS/octos-kernel') == source_kernel_sha256, 'Packaging changed the working Kernel'
    run([executable / 'muse-launcher', '--check'])
    shutil.copy2(HERE / 'launch_muse.sh', output / 'launch_muse.sh')
    (output / 'launch_muse.sh').chmod(0o755)
    inventory = {p.relative_to(inner / 'Resources').as_posix(): sha(p)
        for p in sorted((inner / 'Resources').rglob('*')) if p.is_file()}
    (output / 'HOST_RESOURCES.json').write_text(json.dumps(inventory, indent=2) + '\n')
    record = {'version': '0.4.0-rc4', 'status': 'PACKAGED_NOT_RUNTIME_VERIFIED',
        'signature': 'AD_HOC_LOCAL_ONLY', 'source_host_sha256': source_host_sha256,
        'source_kernel_sha256': source_kernel_sha256,
        'reused_signed_pair': bool(args.paired_host_app),
        'host_launch_method': 'LaunchServices WorkBuddy shell wrapper' if args.paired_host_app else 'NSTask',
        'host_resources_files': len(inventory),
        'state_root_reference': str(args.state_root) if args.state_root is not None else None,
        'catalog_sha256': sha(resources / 'mirror/catalog.json'),
        'muse_main_sha256': sha(resources / 'mirror/artifacts/muse-goals-0.4.0-rc4.bundle/main.splash'),
        'host_sha256': sha(inner / 'MacOS/octosense'),
        'host_hash_boundary': 'source_host_sha256 is the input; host_sha256 is the packaged executable after signing',
        'kernel_sha256': sha(inner / 'MacOS/octos-kernel'),
        'production_data_included': False, 'calendar_shared_tools_granted': False,
        'model': {'gpt': 'native OpenAI GPT; user setup required; no bundled model',
            'offline': 'Qwen2.5-0.5B basic offline fallback',
            'hybrid': 'existing Native cloud provider (including MiniMax) plus bundled Qwen service; local selection and collaboration not verified'}[args.model_mode],
        'model_mode': args.model_mode, 'model_runtime_verified': False,
        'upstream_host': 'paired pending-review build'}
    (output / 'PACKAGE.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
