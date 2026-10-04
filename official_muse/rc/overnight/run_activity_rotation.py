#!/usr/bin/env python3
"""Native jailed-fs activity rotation; no model or external transport calls."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
import regression_run

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
result = regression_run.run_suite('activity_rotation', args.source.read_text(),
    ROOT / 'official_muse/app/bundle', args.out.resolve(), 8488,
    Path(__file__).with_name('activity_rotation.splash'))
print(json.dumps(result, ensure_ascii=False))
assert not result['failed']
