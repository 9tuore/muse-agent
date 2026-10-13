#!/usr/bin/env python3
"""Stage one signed local Muse .app from explicit, frozen public inputs."""
import argparse
import hashlib
import json
import os
import plistlib
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from build_host import FEATURES, packaging

HERE = Path(__file__).resolve().parent


def run(command, **kwargs):
    return subprocess.run([str(item) for item in command], check=True, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_tree(source, destination, apfs_clone=False):
    if not apfs_clone:
        shutil.copytree(source, destination, symlinks=True)
        return {'mode': 'shutil.copytree'}
    if sys.platform != 'darwin':
        raise ValueError('Explicit APFS clone requires macOS')
    source, destination = Path(source).resolve(), Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('APFS clone destination must not exist')
    if os.stat(source).st_dev != os.stat(destination.parent).st_dev:
        raise ValueError('APFS clone source and destination must be on the same volume')
    volume = subprocess.run(['/bin/df', '-P', str(source)], check=True,
                            capture_output=True, text=True).stdout
    device = volume.splitlines()[-1].split()[0]
    info = plistlib.loads(subprocess.run(['/usr/sbin/diskutil', 'info', '-plist', device],
                                       check=True, capture_output=True).stdout)
    if info.get('FilesystemType') != 'apfs':
        raise ValueError('Explicit APFS clone requires an APFS volume')
    command = ['/bin/cp', '-c', '-R', '-p', '-P', str(source), str(destination)]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return {'mode': 'apfs_clone_requested', 'command': command,
            'filesystem': info['FilesystemType'], 'device': device,
            'returncode': result.returncode, 'stderr': result.stderr,
            'boundary': 'cp -c requests clonefile and may fall back to copyfile; physical shared blocks are not measured. Existing source symlinks are preserved; source links are not created.'}


def main():
    parser = argparse.ArgumentParser()
    for name in ('sdk', 'host', 'kernel', 'kernel-receipt', 'mirror', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--model-mode', choices=('offline', 'gpt', 'hybrid'), default='hybrid')
    parser.add_argument('--model-source', type=Path)
    parser.add_argument('--licenses', type=Path,
        help='Copy collected dependency license documents into the signed app')
    parser.add_argument('--apfs-clone', action='store_true',
        help='Request independent APFS CoW directory copies via cp -c; requires macOS and the same APFS volume')
    parser.add_argument('--paired-host-app', type=Path,
        help='Copy matching verified app resources/Kernel; sign the staged Host as standalone; no Cargo')
    parser.add_argument('--state-root', type=Path,
        help='Reference an existing absolute state root in launcher.json; never copy its contents')
    parser.add_argument('--hub-anchor', help='Public trust anchor for a newly built private local catalog; never a signing key')
    args = parser.parse_args()
    if args.model_mode != 'gpt' and args.model_source is None:
        parser.error('--model-source is required for offline/hybrid mode')
    if args.state_root is not None and not args.state_root.is_absolute():
        parser.error('--state-root must be absolute')
    if args.hub_anchor is not None and re.fullmatch('[0-9a-f]{64}', args.hub_anchor) is None:
        parser.error('--hub-anchor must be a 32-byte lowercase public key')
    directory_copies = []
    source_host_sha256 = sha(args.host)
    source_kernel_sha256 = sha(args.kernel)
    source_release = None
    release_identity = args.host.with_name(args.host.name + '.release-identity.json')
    if release_identity.is_file():
        identity = json.loads(release_identity.read_text())
        assert identity.get('sha256') == source_host_sha256, 'Host release receipt mismatch'
        assert isinstance(identity.get('release_tag'), str) and identity['release_tag'], 'Host release tag missing'
        source_release = {'release_tag': identity['release_tag'], 'sha256': source_host_sha256}
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
        directory_copies.append(copy_tree(source.parent, inner.parent, args.apfs_clone))
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
    # Foundation treats this directory as the bare executable's resource root.
    runtime = resources / 'host-runtime'
    directory_copies.append(copy_tree(inner / 'Resources', runtime, args.apfs_clone))
    shutil.copy2(inner / 'MacOS/octosense', runtime / 'muse-host')
    shutil.copy2(inner / 'MacOS/octos-kernel', runtime / 'octos-kernel')
    shutil.rmtree(inner.parent)
    if args.model_mode != 'gpt':
        directory_copies.append(copy_tree(args.model_source, resources / 'local-model', args.apfs_clone))
    directory_copies.append(copy_tree(args.mirror, resources / 'mirror', args.apfs_clone))
    if args.licenses:
        directory_copies.append(copy_tree(args.licenses, resources / 'Licenses', args.apfs_clone))
    # Local signing keys and account data are not inputs to this packager.
    assert not list(resources.rglob('*.key')), 'A private key entered the package'
    # Preserve the original working LaunchServices identity and shell executable.
    shutil.copy2(HERE / 'workbuddy_info.plist', app / 'Contents/Info.plist')
    (resources / 'launcher.json').write_text(json.dumps({'version': '0.4.0-rc23',
        'model_mode': args.model_mode, 'state_root': str(args.state_root) if args.state_root else None,
        'hub_anchor': args.hub_anchor}, indent=2) + '\n')
    shutil.copy2(HERE / 'workbuddy_launcher.sh', executable / 'Launcher')
    (executable / 'Launcher').chmod(0o755)
    run(['clang', '-fobjc-arc', '-O2', '-framework', 'AppKit', HERE / 'muse_launcher.m',
        '-o', executable / 'muse-launcher'])
    run(['codesign', '--force', '--sign', '-', executable / 'muse-launcher'])
    # Sign only our staged copy, then ask the official staging helper to
    # re-attest the same pinned revision and the resulting binary bytes.
    if not args.paired_host_app:
        run(['codesign', '--force', '--sign', '-', runtime / 'octos-kernel'])
        kernel_tool = package.kernel_tool()
        signed_receipt = kernel_tool.stage(runtime / 'octos-kernel', output / 'signed-kernel',
            kernel_tool.octos_revision(), 'prebuilt')
        shutil.copy2(output / 'signed-kernel/octos-kernel.json', runtime / 'octos-kernel.json')
    else:
        signed_receipt = receipt
    # Sign outside every .app so the original Info/resource special slots are removed.
    with tempfile.TemporaryDirectory(prefix='standalone-host-', dir=output) as staging:
        standalone = Path(staging) / 'octosense'
        shutil.copy2(runtime / 'muse-host', standalone)
        run(['codesign', '--force', '--sign', '-', '--identifier',
            'org.xinghai.muse.paired-host', standalone])
        run(['codesign', '--verify', '--strict', standalone])
        shutil.copy2(standalone, runtime / 'muse-host')
    run(['codesign', '--force', '--sign', '-', app])
    run(['codesign', '--verify', '--deep', '--strict', app])
    assert sha(runtime / 'octos-kernel') == signed_receipt['sha256'], 'Packaging changed the pinned kernel'
    if args.paired_host_app:
        assert sha(runtime / 'octos-kernel') == source_kernel_sha256, 'Packaging changed the working Kernel'
    run([executable / 'muse-launcher', '--check'])
    shutil.copy2(HERE / 'launch_muse.sh', output / 'launch_muse.sh')
    (output / 'launch_muse.sh').chmod(0o755)
    inventory = {p.relative_to(runtime).as_posix(): sha(p)
        for p in sorted(runtime.rglob('*')) if p.is_file() and p not in (runtime / 'muse-host', runtime / 'octos-kernel')}
    (output / 'HOST_RESOURCES.json').write_text(json.dumps(inventory, indent=2) + '\n')
    assert sha(executable / 'Launcher') == sha(HERE / 'workbuddy_launcher.sh'), 'Packaged entry differs from source script'
    assert (app / 'Contents/Info.plist').read_bytes() == (HERE / 'workbuddy_info.plist').read_bytes(), 'Working App Info changed'
    record = {'version': '0.4.0-rc23', 'status': 'PACKAGED_NOT_RUNTIME_VERIFIED',
        'signature': 'AD_HOC_LOCAL_ONLY', 'source_host_sha256': source_host_sha256,
        'source_host_release': source_release,
        'source_kernel_sha256': source_kernel_sha256,
        'reused_signed_pair': False, 'reused_signed_kernel': bool(args.paired_host_app),
        'standalone_host': True,
        'host_launch_method': 'outer CFBundleExecutable shell -> exec Resources/host-runtime/muse-host',
        'outer_info_plist_sha256': sha(app / 'Contents/Info.plist'),
        'source_launcher_sha256': sha(HERE / 'workbuddy_launcher.sh'),
        'packaged_launcher_sha256': sha(executable / 'Launcher'),
        'existing_profile_preserved': True, 'fresh_local_profile_bootstrap': True,
        'qwen_supervision': 'background guardian watches original shell/Host parent PID; runtime not verified',
        'host_resources_files': len(inventory),
        'state_root_reference': str(args.state_root) if args.state_root is not None else None,
        'catalog_sha256': sha(resources / 'mirror/catalog.json'),
        'muse_main_sha256': sha(resources / 'mirror/artifacts/muse-goals-0.4.0-rc23.bundle/main.splash'),
        'host_sha256': sha(runtime / 'muse-host'),
        'host_hash_boundary': 'source_host_sha256 is the input; host_sha256 is the packaged executable after signing',
        'kernel_sha256': sha(runtime / 'octos-kernel'),
        'production_data_included': False, 'calendar_shared_tools_granted': False,
        'model': {'gpt': 'native OpenAI GPT; user setup required; no bundled model',
            'offline': 'Qwen2.5-0.5B basic offline fallback',
            'hybrid': 'existing Native cloud provider (including MiniMax) plus bundled Qwen service; local selection and collaboration not verified'}[args.model_mode],
        'model_mode': args.model_mode, 'model_runtime_verified': False,
        'upstream_host': ('source-built ' + source_release['release_tag']
            if source_release else 'explicit Host input without release receipt')}
    if args.apfs_clone:
        record.update(directory_copy_mode='apfs_clone_requested', directory_copies=directory_copies)
    (output / 'PACKAGE.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
