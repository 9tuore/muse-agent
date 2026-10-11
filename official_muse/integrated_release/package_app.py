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
    args = parser.parse_args()
    if args.model_mode != 'gpt' and args.model_source is None:
        parser.error('--model-source is required for offline/hybrid mode')
    source_host_sha256 = sha(args.host)
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    app = output / 'Muse.app'
    resources = app / 'Contents/Resources'
    executable = app / 'Contents/MacOS'
    executable.mkdir(parents=True)
    resources.mkdir()
    sdk = args.sdk.resolve()
    receipt = json.loads(args.kernel_receipt.read_text())
    assert receipt['sha256'] == sha(args.kernel), 'Kernel receipt mismatch'
    inner = resources / 'OctoSense Host.app/Contents'
    (inner / 'MacOS').mkdir(parents=True)
    package = packaging(sdk)
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
    assert sha(inner / 'MacOS/octosense') == source_host_sha256, 'Host input changed while staging'
    shutil.copy2(args.kernel, inner / 'MacOS/octos-kernel')
    shutil.copy2(args.kernel_receipt, inner / 'Resources/octos-kernel.json')
    if args.model_mode != 'gpt':
        shutil.copytree(args.model_source, resources / 'local-model', symlinks=True)
    shutil.copytree(args.mirror, resources / 'mirror', symlinks=True)
    # Local signing keys and account data are not inputs to this packager.
    assert not list(resources.rglob('*.key')), 'A private key entered the package'
    plist = dict(CFBundleName='Muse', CFBundleDisplayName='Muse', CFBundleExecutable='muse-launcher',
        CFBundleIdentifier='org.xinghai.muse.integrated', CFBundlePackageType='APPL',
        CFBundleShortVersionString='0.4.0', CFBundleVersion='4', LSMinimumSystemVersion='14.0',
        NSHighResolutionCapable=True, MuseModelMode=args.model_mode)
    with (app / 'Contents/Info.plist').open('wb') as stream:
        plistlib.dump(plist, stream)
    host_plist = dict(plist, CFBundleName='OctoSense', CFBundleDisplayName='OctoSense',
        CFBundleExecutable='octosense', CFBundleIdentifier='org.xinghai.muse.paired-host')
    with (inner / 'Info.plist').open('wb') as stream:
        plistlib.dump(host_plist, stream)
    run(['clang', '-fobjc-arc', '-O2', '-framework', 'AppKit', HERE / 'muse_launcher.m',
        '-o', executable / 'muse-launcher'])
    # Sign only our staged copy, then ask the official staging helper to
    # re-attest the same pinned revision and the resulting binary bytes.
    run(['codesign', '--force', '--sign', '-', inner / 'MacOS/octos-kernel'])
    kernel_tool = package.kernel_tool()
    signed_receipt = kernel_tool.stage(inner / 'MacOS/octos-kernel', output / 'signed-kernel',
        kernel_tool.octos_revision(), 'prebuilt')
    shutil.copy2(output / 'signed-kernel/octos-kernel.json', inner / 'Resources/octos-kernel.json')
    run(['codesign', '--force', '--sign', '-', inner.parent])
    run(['codesign', '--force', '--sign', '-', app])
    run(['codesign', '--verify', '--deep', '--strict', app])
    assert sha(inner / 'MacOS/octos-kernel') == signed_receipt['sha256'], 'Packaging changed the pinned kernel'
    run([executable / 'muse-launcher', '--check'])
    shutil.copy2(HERE / 'launch_muse.sh', output / 'launch_muse.sh')
    (output / 'launch_muse.sh').chmod(0o755)
    record = {'version': '0.4.0-rc4', 'status': 'PACKAGED_NOT_RUNTIME_VERIFIED',
        'signature': 'AD_HOC_LOCAL_ONLY', 'source_host_sha256': source_host_sha256,
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
