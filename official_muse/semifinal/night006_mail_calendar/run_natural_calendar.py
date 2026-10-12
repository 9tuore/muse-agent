#!/usr/bin/env python3
"""Focused real-VM checks for direct natural-language Calendar result binding."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--vm', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = args.source.read_bytes()
    extract = module('extract', ROOT / 'official_muse/prelim/tests/calendar_sync/run.py')
    runner = module('linkage', HERE / 'run_linkage.py')
    functions = extract.functions_in(raw.decode())
    names = list(dict.fromkeys(runner.FUNCTIONS + runner.OPTIONAL + [
        'calendar_agent_history', 'calendar_agent_settle_if_resolved',
        'calendar_agent_creation_proof', 'calendar_agent_request_context_current',
        'calendar_agent_capture_request_source', 'calendar_agent_adopt_request_matter']))
    names = [name for name in names if name in functions]
    prefix = (HERE / 'linkage.splash').read_text().split('// PRODUCT_FUNCTIONS')[0]
    prefix = prefix.replace('fn calendar_agent_history(){}', '')
    prefix = prefix.replace('if method=="octos.session.open"',
        'if method=="octos.session.history"{cb({is_ok:true data:{messages:history_rows}})}\n if method=="octos.session.open"')
    prefix += '\nfn calendar_agent_preflight_history(value){}\nfn calendar_agent_preflight_current(){return false}\n'
    prefix += (HERE / 'history.splash').read_text().split('seed()')[0]
    production = '\n'.join(functions[name].replace('host.request(', 'fixture_transport(') for name in names)
    code = prefix + '\n' + production + '\n' + (HERE / 'natural_calendar.splash').read_text()
    (args.out / 'executed.splash').write_text(code)
    sha = lambda value: hashlib.sha256(value).hexdigest()
    identity = {'source_sha256': sha(raw), 'vm_sha256': sha(args.vm.read_bytes()),
                'executed_sha256': sha(code.encode()),
                'function_sha256': {name: sha(functions[name].encode()) for name in names}}
    command = [str(args.vm), str((args.out / 'executed.splash').resolve()), '--rpc']
    (args.out / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    (args.out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    (args.out / 'stdout.txt').write_text(result.stdout)
    (args.out / 'stderr.txt').write_text(result.stderr)
    report = {'status': 'ERROR', 'returncode': result.returncode,
              'boundary': 'Actual Splash VM and extracted production functions; isolated storage/helpers and synthetic exact Host receipts. Not GUI, live Calendar or SMTP.'}
    if result.returncode == 0 and not result.stderr:
        checks = json.loads(result.stdout.removeprefix('MUSE_VM_RESULT ').strip())
        failed = [row['name'] for row in checks if not row['passed']]
        report.update(status='FAIL' if failed else 'FIXTURE_PASS', count=len(checks), checks=checks, failed=failed)
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, ensure_ascii=False))
    return 0 if report['status'] == 'FIXTURE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
