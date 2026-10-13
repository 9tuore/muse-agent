#!/usr/bin/env python3
"""Run real Splash mail lifecycle functions with isolated synthetic Host replies."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FUNCTIONS = (
    'gm_object gm_array gm_text gm_number gm_get gm_has gm_string '
    'mail_draft_valid mail_save mail_watch_archive_current mail_edit mail_new_draft '
    'mail_select_account mail_use_sender mail_preview mail_submit mail_send_confirmed '
    'mail_abort_before_host mail_send_step mail_review_current mail_compose_before_review '
    'mail_review_host mail_send_receipt_step mail_host_error mail_host_receipt_status mail_check_host_status core_action_index core_begin_action core_finish_action'
).split()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT / 'official_muse/app/source/main.splash')
    parser.add_argument('--vm', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--suite', choices=['mail', 'calendar'], default='mail')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = args.source.read_text()
    spec = importlib.util.spec_from_file_location('splash_parser', ROOT / 'official_muse/prelim/tests/calendar_sync/run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    functions = module.functions_in(source)
    # Baseline has the same two user actions, but no convenience wrapper yet.
    functions.setdefault('mail_submit', 'fn mail_submit(){ mail_preview() if mail_draft.status == "waiting_user" && mail_error == "" { mail_send_confirmed() } }')
    names = FUNCTIONS + (['mail_payload_pending'] if 'mail_payload_pending' in functions else [])
    if args.suite == 'calendar':
        names = 'gm_object gm_array gm_text gm_string gm_get gm_has calendar_agent_save calendar_agent_settle calendar_agent_submit_bound calendar_agent_submit_candidate calendar_agent_same_candidate mail_prepare_calendar'.split()
    production = '\n'.join(functions[name].replace('host.request(', 'fixture_transport(') for name in names)
    code = (HERE / (args.suite + '_continuation.splash')).read_text().replace('// PRODUCT_FUNCTIONS', production)
    executed = args.out / 'executed.splash'
    executed.write_text(code)
    sha = lambda data: hashlib.sha256(data).hexdigest()
    identity = dict(source_sha256=sha(source.encode()), vm_sha256=sha(args.vm.read_bytes()),
                    executed_sha256=sha(code.encode()),
                    functions={name: sha(functions[name].encode()) for name in names})
    command = [str(args.vm.resolve()), str(executed.resolve()), '--rpc']
    (args.out / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    (args.out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    (args.out / 'stdout.log').write_text(result.stdout)
    (args.out / 'stderr.log').write_text(result.stderr)
    report = dict(status='ERROR', returncode=result.returncode,
                  boundary='Actual Splash VM and extracted product functions; fixture storage/Host replies, no GUI or real email.')
    if result.returncode == 0 and not result.stderr:
        checks = json.loads(result.stdout.removeprefix('MUSE_VM_RESULT ').strip())
        failed = [row['name'] for row in checks if not row['passed']]
        report.update(status='FIXTURE_PASS' if not failed else 'FAIL', checks=checks, failed=failed, count=len(checks))
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, ensure_ascii=False))
    return 0 if report['status'] == 'FIXTURE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
