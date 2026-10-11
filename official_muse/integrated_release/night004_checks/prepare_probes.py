#!/usr/bin/env python3
"""Compile only the two local macOS C probes; retain commands and exit codes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    evidence = HERE / 'local-evidence/probes'
    evidence.mkdir(parents=True, exist_ok=True)
    report = {'status': 'PREPARING', 'at_utc': datetime.now(timezone.utc).isoformat(),
              'commands': [], 'cargo_builds': 0, 'host_startups': 0,
              'gui_actions': 0, 'keychain_accesses': 0}
    definitions = (
        ('signature_probe.c', 'signature_probe', ('Security', 'CoreFoundation')),
        ('owned_main_window_id.c', 'owned-main-window-id', ('ApplicationServices',)),
    )
    for source_name, binary_name, frameworks in definitions:
        source, binary = HERE / source_name, HERE / binary_name
        command = ['/usr/bin/clang', '-Wall', '-Wextra', '-Werror', str(source)]
        for framework in frameworks:
            command.extend(('-framework', framework))
        command.extend(('-o', str(binary)))
        row = {'argv': command, 'source_sha256': sha(source), 'exit_code': None}
        report['commands'].append(row)
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=60)
            row['exit_code'] = completed.returncode
            row['stdout'], row['stderr'] = completed.stdout, completed.stderr
            if completed.returncode == 0:
                row['binary_sha256'] = sha(binary)
        except (OSError, subprocess.TimeoutExpired) as error:
            row['error_type'] = type(error).__name__
        (evidence / (binary_name + '.json')).write_text(json.dumps(row, indent=2) + '\n')
        if row['exit_code'] != 0:
            report['status'] = 'FAILED'
            break
    if report['status'] != 'FAILED':
        report['status'] = 'TWO_C_PROBES_PREPARED'
    target = evidence / 'result.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'evidence': str(target)}))
    return 0 if report['status'] == 'TWO_C_PROBES_PREPARED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
