#!/usr/bin/env python3
"""Two isolated jails for the one corrupt-primary recovery concern."""
import argparse
import hashlib
import json
from pathlib import Path
import memory_integration_runtime as harness


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    transport = harness.TRANSPORT
    reports = {}
    for mode in ['good-backup', 'bad-backup']:
        harness.TRANSPORT = transport + '\nlet integration_corrupt_mode = ' + json.dumps(mode) + '\n'
        try:
            output = args.output / mode
            report = harness.run(args.source, output, 'memory_integration_corrupt')
            jail = output.resolve() / 'state/muse-goals'
            wanted_hash = report['observations']['primary_bad_sha256']
            # Inspect actual app storage, excluding test code/reports. No expected-raw copy is seeded.
            files = [path for path in jail.rglob('*') if path.is_file() and path.name != 'probe.json']
            retained = [str(path.relative_to(jail)) for path in files
                        if hashlib.sha256(path.read_bytes()).hexdigest() == wanted_hash]
            report['bad_primary_recoverable_after_save'] = bool(retained)
            report['storage_file_hashes'] = {str(path.relative_to(jail)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
            report['retained_original_bad_paths'] = retained
            checks = {key: value for key, value in report.items() if isinstance(value, bool)}
            report.update(passed=sum(checks.values()), failed=[key for key, value in checks.items() if not value])
            (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            reports[mode] = report
        finally:
            harness.TRANSPORT = transport
    summary = {'main_source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
               'scope': 'single memory corruption recovery audit; two synthetic app-jails; no services',
               'reports': reports}
    (args.output / 'result.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({mode: {'passed': result['passed'], 'failed': result['failed'],
                            'retained_original_bad_paths': result['retained_original_bad_paths']}
                      for mode, result in reports.items()}, indent=2), flush=True)
    return 1 if any(report['failed'] for report in reports.values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
