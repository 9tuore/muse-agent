#!/usr/bin/env python3
"""Prepare the rc18 research bundle with the exact official Host API requirements.

Leaves the active root bundle and installed app untouched. No stamping, signing,
admission, account copying or publication is implied by this file operation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    if not output.is_relative_to(ROOT / 'build'):
        raise RuntimeError('Research candidates must stay in this worktree build directory')
    source = ROOT / 'official_muse/app/source/main.splash'
    base = ROOT / 'bundle'
    manifest = json.loads((base / 'manifest.json').read_text())
    if manifest['id'] != 'muse-goals' or manifest.get('agent') is not None:
        raise RuntimeError('Unexpected active identity or Agent declaration; do not change scope silently')
    output.mkdir(parents=True, exist_ok=False)
    bundle = output / 'bundle'
    shutil.copytree(base, bundle)
    shutil.copyfile(source, bundle / 'main.splash')
    manifest['version'] = '0.3.27-rc18'
    manifest['integrity'] = {}
    manifest['capabilities'] = [c for c in manifest['capabilities'] if c != 'calendar']
    if 'runtime' not in manifest['capabilities']:
        manifest['capabilities'].append('runtime')
    requirements = manifest.setdefault('requires', [])
    if 'host-api-v1' not in requirements:
        requirements.append('host-api-v1')
    api = manifest.setdefault('host_api', {})
    required = api.setdefault('required', {})
    for method in ('runtime.list', 'mail.compose', 'mail.compose_status', 'mail.review_send'):
        required[method] = 1
    (bundle / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    record = {'id': manifest['id'], 'version': manifest['version'],
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'required': required, 'capabilities': manifest['capabilities'],
              'status': 'PREPARED_NOT_ADMITTED',
              'boundary': 'Root rc17 unchanged; new official Host/native consent/full chain remain unverified'}
    (output / 'identity.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
