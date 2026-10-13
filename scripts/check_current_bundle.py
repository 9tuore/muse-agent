#!/usr/bin/env python3
"""Ensure the root publishing bundle matches the current readable product source."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
(ROOT / 'build').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='current-bundle-', dir=ROOT / 'build') as temp:
    candidate = Path(temp) / 'candidate'
    subprocess.run([sys.executable, str(ROOT / 'official_muse/integrated_release/prepare_bundle.py'),
                    '--out', str(candidate)], check=True, capture_output=True, text=True)
    expected = candidate / 'bundle'
    for name in ('main.splash', 'manifest.json', 'listing.json', 'AGENT.md'):
        if (ROOT / 'bundle' / name).read_bytes() != (expected / name).read_bytes():
            raise SystemExit('Root bundle is stale: ' + name + '; refresh it from prepare_bundle.py output.')
    identity = json.loads((candidate / 'bundle-identity.json').read_text())
    print(json.dumps({'status': 'CURRENT_SOURCE_MATCH', 'version': identity['version'],
                      'source_sha256': identity['upstream_source_sha256'],
                      'bundle_sha256': identity['transform']['artifact_sha256']}, indent=2))
