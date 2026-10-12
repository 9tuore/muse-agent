#!/usr/bin/env python3
"""Execute extracted production Splash functions in the real VM, with isolated I/O."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FUNCTIONS = '''gm_object gm_array gm_text gm_number gm_get gm_has gm_string
calendar_agent_save calendar_agent_settle calendar_agent_submit_bound
calendar_agent_binding_valid calendar_agent_binding_current calendar_agent_binding_at_revision
calendar_agent_event_matches calendar_agent_authority calendar_agent_delete_expected
calendar_agent_update_index calendar_agent_delete_index calendar_agent_delete_blocks
calendar_agent_delete_target calendar_agent_update_target calendar_agent_tool_name
calendar_agent_receipt_status calendar_agent_link_result calendar_agent_project
mail_prepare_calendar calendar_agent_boot calendar_agent_same_candidate
mail_calendar_link_valid mail_calendar_verified mail_calendar_current
calendar_agent_authority_valid calendar_agent_authority_current calendar_agent_submit
calendar_agent_prepare_candidate calendar_agent_candidate_error calendar_agent_wall
chat_payload_error gm_time_valid calendar_iso_epoch calendar_display_time
page_event_epoch page_parse_date page_two_number page_day_number page_month_days page_two
page_time_floor page_date_parts'''.split()
OPTIONAL = '''calendar_agent_request_for_matter calendar_agent_request_matches_matter
calendar_agent_adopt_mail_result calendar_agent_mail_context_current
calendar_agent_input_changed calendar_agent_short_text calendar_agent_prepare_edit'''.split()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--vm', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--suite', choices=['linkage', 'history'], default='linkage')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = args.source.read_bytes()
    spec = importlib.util.spec_from_file_location('extract', ROOT / 'official_muse/prelim/tests/calendar_sync/run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    functions = module.functions_in(raw.decode())
    names = FUNCTIONS + [name for name in OPTIONAL if name in functions]
    if args.suite == 'history':
        names += ['calendar_agent_history', 'calendar_agent_settle_if_resolved']
    extracted = '\n'.join(functions[name].replace('host.request(', 'fixture_transport(') for name in names)
    if 'calendar_agent_input_changed' not in functions:
        extracted += '\nfn calendar_agent_input_changed(text){calendar_agent_input_text=text}\n'
    if 'calendar_agent_adopt_mail_result' not in functions:
        extracted += '\nfn calendar_agent_adopt_mail_result(rows){return false}\n'
    template = (HERE / 'linkage.splash').read_text()
    if args.suite == 'history':
        template = template.split('// PRODUCT_FUNCTIONS')[0].replace('fn calendar_agent_history(){}', '')
        template += '\nfn calendar_agent_preflight_history(value){}\nfn calendar_agent_preflight_current(){return false}\n'
        template += '// PRODUCT_FUNCTIONS\n' + (HERE / 'history.splash').read_text()
        template = template.replace('if method=="octos.session.open"', 'if method=="octos.session.history"{cb({is_ok:true data:{messages:history_rows}})}\n if method=="octos.session.open"')
    code = template.replace('// PRODUCT_FUNCTIONS', extracted)
    (args.out / 'executed.splash').write_text(code)
    sha = lambda x: hashlib.sha256(x).hexdigest()
    identity = dict(source_sha256=sha(raw), runner_sha256=sha(Path(__file__).read_bytes()),
                    harness_sha256=sha((HERE / 'linkage.splash').read_bytes()),
                    executed_sha256=sha(code.encode()), vm_sha256=sha(args.vm.read_bytes()),
                    functions={name: sha(functions[name].encode()) for name in names})
    command = [str(args.vm.resolve()), str((args.out / 'executed.splash').resolve()), '--rpc']
    (args.out / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    (args.out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    (args.out / 'stdout.txt').write_text(result.stdout)
    (args.out / 'stderr.txt').write_text(result.stderr)
    report = dict(status='ERROR', returncode=result.returncode,
                  boundary='Real Splash VM and production functions; synthetic Host receipts, isolated storage and GUI/goal helpers. Not GUI, SMTP or real Calendar owner validation.')
    if result.returncode == 0 and not result.stderr:
        rows = json.loads(result.stdout.removeprefix('MUSE_VM_RESULT ').strip())
        failed = [row['name'] for row in rows if not row['passed']]
        report.update(status='FAIL' if failed else 'FIXTURE_PASS', checks=rows, failed=failed, count=len(rows))
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, ensure_ascii=False))
    return 0 if report['status'] == 'FIXTURE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
