#!/usr/bin/env python3
"""Repeat the focused scope/correction/forget fixtures on one module version."""
from datetime import datetime
import json
from memory_runtime import ROOT, run


def main():
    output = ROOT / 'official_muse/prelim/evidence/memory' / (
        'targeted-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    reports = {}
    for probe, folder in [('memory_p0', 'p0'), ('memory_variants', 'variants'),
                          ('memory_restart', 'variants'), ('memory_security', 'security')]:
        report = run(output / folder, probe=probe)
        checks = {key: value for key, value in report.items() if isinstance(value, bool)}
        assert checks and all(checks.values()), (probe, checks)
        reports[probe] = report
    first = reports['memory_p0']
    for field in ('main_source_sha256', 'core_sha256', 'module_sha256', 'host_sha256'):
        assert all(report[field] == first[field] for report in reports.values()), field
    (output / 'targeted.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
