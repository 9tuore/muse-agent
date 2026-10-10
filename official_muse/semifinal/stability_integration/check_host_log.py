"""Offline artifact/log correlation; never establishes Mail execution success."""
import argparse
import hashlib
import json
from pathlib import Path
import re

EVAL = re.compile(r'\[SPLASH\] eval: (\d+) bytes .*?view=(true|false)')
ERROR = re.compile(r'\[E\]|panicked at|script (?:time|instruction|memory) budget exceeded|script error|card-host:.*(?:refused|cannot|did not lower)', re.I)
REFUSAL = re.compile(r'this host does not implement required APIs:|card-host refused this bundle|host API.*(?:incompatible|unsupported)', re.I)


def analyze(source, logs, report=None):
    sha = hashlib.sha256(source).hexdigest()
    identity = report is not None and report.get('source_sha256') == sha
    cases = []
    for index, (name, text) in enumerate(logs):
        evaluations = [{'bytes': int(n), 'view': v == 'true'} for n, v in EVAL.findall(text)]
        matching = [e for e in evaluations if e['bytes'] == len(source)]
        errors = [line for line in text.splitlines() if ERROR.search(line)]
        refused = [line for line in text.splitlines() if REFUSAL.search(line)]
        timeout = any('script time budget exceeded' in line.lower() for line in errors)
        case = (report.get('cases', []) if report else [])
        harness = case[index] if index < len(case) else None
        classes = []
        if report is not None and not identity:
            classes.append('ARTIFACT_SHA_MISMATCH')
        if report is not None and len(report.get('cases', [])) != len(logs):
            classes.append('REPORT_LOG_COUNT_MISMATCH')
        if refused:
            classes.append('COMPATIBILITY_REFUSAL')
        if timeout:
            classes.append('SCRIPT_TIME_BUDGET_EXCEEDED')
        if any('script time budget exceeded' not in line.lower() for line in errors):
            classes.append('OTHER_RUNTIME_ERROR')
        if not matching:
            classes.append('PAYLOAD_NOT_OBSERVED')
        elif not any(e['view'] for e in matching):
            classes.append('PAYLOAD_EVALUATED_WITHOUT_VIEW')
        if harness is not None and (not harness.get('checks') or not all(v is True for v in harness['checks'].values()) or harness.get('runtime_errors')):
            classes.append('HARNESS_CASE_INCOMPLETE_OR_FAILED')
        if not classes:
            classes.append('PAYLOAD_BYTES_AND_VIEW_OBSERVED')
        cases.append({'log': name, 'classifications': classes, 'evaluations': evaluations,
                      'error_lines': errors, 'refusal_lines': refused,
                      'harness_case': harness})
    return {'source_sha256': sha, 'source_bytes': len(source),
            'report_source_sha_matches': identity if report is not None else None,
            'identity_limit': 'Log eval records bytes, not SHA. Report SHA binds harness input only; equal byte counts alone do not prove identical executed bytes.',
            'timeout_limit': 'Time-budget error does not state milliseconds. 64ms attribution requires matching Host budget configuration.',
            'boundary': 'Offline log correlation only; no Mail delivery, native approval, or full-chain claim.',
            'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--log', required=True, action='append', type=Path,
                        help='One per harness case, in report case order')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text()) if args.report else None
    result = analyze(args.source.read_bytes(), [(str(p), p.read_text()) for p in args.log], report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    bad = any(c['classifications'] != ['PAYLOAD_BYTES_AND_VIEW_OBSERVED'] for c in result['cases'])
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
