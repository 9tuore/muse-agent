#!/usr/bin/env python3
"""Prepare the two recovery comparisons without editing production main."""
import argparse
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASELINE = 'e7d665dd7f466e454aeca071895273e81549af169f8613c3490671a3cf8cca20'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    args = parser.parse_args()
    source = args.baseline.read_text()
    sha = lambda value: hashlib.sha256(value.encode()).hexdigest()
    assert sha(source) == BASELINE
    replacements = {
        'authority.update.to_json() != record.to_json().parse_json().to_json()':
            'authority.update != record.to_json().parse_json()',
        'current.to_json() == authority.to_json()':
            'current.to_json().parse_json() == authority.to_json().parse_json()',
    }
    candidate = source
    for old, new in replacements.items():
        assert candidate.count(old) == 1
        candidate = candidate.replace(old, new)
    helper = HERE.parents[2] / 'official_muse/semifinal/tests/run_official_api.py'
    spec = importlib.util.spec_from_file_location('verified_helpers', helper)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    before, after = h.functions_in(source), h.functions_in(candidate)
    changed = sorted(name for name in before if before[name] != after[name])
    assert before.keys() == after.keys()
    assert changed == ['calendar_agent_authority_current', 'mail_native_completion_matches']
    patch = ''.join(difflib.unified_diff(source.splitlines(True), candidate.splitlines(True),
        fromfile='a/official_muse/app/source/main.splash', tofile='b/official_muse/app/source/main.splash'))
    args.candidate.write_text(candidate)
    (HERE / 'completion-order.patch').write_text(patch)
    identity = {'baseline_sha256': BASELINE, 'candidate_sha256': sha(candidate),
                'patch_sha256': sha(patch), 'changed_functions': changed,
                'all_other_functions_byte_equal': True,
                'change': 'Compare complete parsed JSON structures. Preserve all fields, array order, string bytes and existing guards.'}
    (HERE / 'patch-identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    print(json.dumps(identity))


if __name__ == '__main__':
    main()
