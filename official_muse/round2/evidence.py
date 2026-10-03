#!/usr/bin/env python3
"""Validate evidence against an immutable product candidate, not a docs HEAD."""
import argparse
import json
import hashlib
from pathlib import Path

KINDS = {'UNIT', 'FIXTURE', 'CARD_HOST', 'SHELL_LIVE', 'REAL_EXTERNAL_SERVICE', 'USER_CONFIRMED'}
FIELDS = {'id', 'feature', 'muse_commit', 'bundle_version', 'octosense_commit',
          'apphub_commit', 'host_extension_commit', 'test_time', 'environment',
          'test_kind', 'result', 'evidence_files'}
IDENTITY = ('muse_commit', 'bundle_version', 'octosense_commit', 'apphub_commit', 'host_extension_commit')


def evaluate(entry, candidate, root):
    missing = FIELDS - entry.keys()
    if missing or entry.get('test_kind') not in KINDS:
        return 'INVALID_EVIDENCE'
    if any(entry.get(k) != candidate.get(k) for k in IDENTITY):
        return 'STALE_EVIDENCE'
    # Archive exports have no Git HEAD: bind their independently measured snapshot instead.
    if candidate.get('octosense_commit') is None:
        if not candidate.get('octosense_source_sha256') or entry.get('octosense_source_sha256') != candidate['octosense_source_sha256']:
            return 'STALE_EVIDENCE'
    if candidate.get('host_executable_sha256') and entry.get('host_executable_sha256') != candidate['host_executable_sha256']:
        return 'STALE_EVIDENCE'
    if entry.get('bundle_blake3') != candidate.get('bundle_blake3'):
        return 'STALE_EVIDENCE'
    if not entry['evidence_files'] or any(not (root / p).is_file() for p in entry['evidence_files']):
        return 'MISSING_EVIDENCE'
    return entry['result']


def candidate_matches_files(candidate, root):
    bundle = root / 'official_muse/app/bundle'
    try:
        manifest = json.loads((bundle / 'manifest.json').read_text())
    except (OSError, ValueError):
        return False
    if not isinstance(manifest, dict) or not isinstance(manifest.get('integrity'), dict):
        return False
    if manifest.get('version') != candidate['bundle_version'] or manifest['integrity'].get('bundle_blake3') != candidate['bundle_blake3']:
        return False
    manifest.get('integrity', {}).pop('signature', None)
    manifest_digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if manifest_digest != candidate.get('manifest_semantic_sha256'):
        return False
    actual_names = {str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    if actual_names != set(candidate.get('bundle_files_sha256', {})):
        return False
    for name, digest in candidate.get('bundle_files_sha256', {}).items():
        file = bundle / name
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
            return False
    return bool(candidate.get('bundle_files_sha256'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('index', type=Path)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text())
    index = json.loads(args.index.read_text())
    product_current = candidate_matches_files(candidate, args.root)
    results = []
    for entry in index['entries']:
        effective = evaluate(entry, candidate, args.root)
        if not product_current and effective != 'INVALID_EVIDENCE':
            effective = 'STALE_EVIDENCE'
        results.append({'id': entry.get('id'), 'declared': entry.get('result'), 'effective': effective})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(any(r['effective'] in {'INVALID_EVIDENCE', 'MISSING_EVIDENCE'} for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
