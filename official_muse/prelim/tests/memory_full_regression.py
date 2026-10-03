"""Run the existing suites against one frozen full main, in visible card-host."""
import argparse
import hashlib
import json
from pathlib import Path

import memory_regression as original
from memory_runtime import ROOT, run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = ROOT/'official_muse/app/bundle/main.splash'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    original.OUT = out
    original.run = lambda output, port=8482, probe='memory_suite': run(
        output, port, probe.replace('memory_', 'memory_regression_', 1), main_source=source, visible=True)
    original.main()
    first = json.loads((out/'acceptance.json').read_text())
    count = first['boolean_checks_passed']
    reports = {}
    for probe, folder in [('memory_p0', 'p0'), ('memory_variants', 'variants'),
                          ('memory_restart', 'variants'), ('memory_security', 'security')]:
        report = run(out/'targeted'/folder, port=8482, probe=probe, main_source=source, visible=True)
        checks = {k:v for k,v in report.items() if type(v) is bool}
        assert checks and all(checks.values()), checks
        count += len(checks)
        reports[probe] = report
    assert all(r['main_source_sha256'] == digest for r in [*first['reports'].values(), *reports.values()])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    result = {'status': 'PASS_FIXTURE_ONLY', 'main_source_sha256': digest,
        'scope': 'FROZEN_FULL_MAIN/FIXTURE, real visible card-host; mocked rendering and forbidden external transport',
        'boolean_checks_passed': count, 'reports': reports}
    (out/'full-main-summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('FINAL', count, 'PASS_FIXTURE_ONLY', flush=True)


if __name__ == '__main__': main()
