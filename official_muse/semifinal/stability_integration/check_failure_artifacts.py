"""Explicit offline check of preserved failure artifacts, never a new live run."""
import argparse
import json
from pathlib import Path

from check_host_log import analyze


def check(artifact_dir, expected):
    source = artifact_dir / 'bundle/main.splash'
    log = artifact_dir / 'runtime-0.log'
    missing = [str(p) for p in (source, log) if not p.is_file()]
    if missing:
        return {'status': 'NOT_TESTED', 'missing_evidence': missing}, 2
    try:
        result = analyze(source.read_bytes(), [(str(log), log.read_text())])
    except (OSError, UnicodeError) as error:
        return {'status': 'NOT_TESTED', 'unreadable_evidence': str(error)}, 2
    classes = result['cases'][0]['classifications']
    if expected == 'refusal':
        matches = ('PAYLOAD_NOT_OBSERVED' in classes
                   and 'SCRIPT_TIME_BUDGET_EXCEEDED' not in classes
                   and any(e['bytes'] == 717 for e in result['cases'][0]['evaluations']))
    else:
        matches = ('SCRIPT_TIME_BUDGET_EXCEEDED' in classes
                   and 'PAYLOAD_EVALUATED_WITHOUT_VIEW' in classes)
    result.update(status='PASS_PRESERVED_FAILURE_CHECK' if matches else 'FAIL_EXPECTED_FAILURE_NOT_FOUND',
                  expected=expected, artifact_dir=str(artifact_dir),
                  evidence_limit='Caller supplies artifact provenance. Offline preserved-log check only; no new live run or compatibility-reason proof.')
    return result, 0 if matches else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir', required=True, type=Path)
    parser.add_argument('--expected', required=True, choices=('refusal', 'timeout'))
    args = parser.parse_args()
    result, code = check(args.artifact_dir, args.expected)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
