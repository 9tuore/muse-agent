#!/usr/bin/env python3
"""Read-only source contract audit. No GUI, account data or transport calls."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SDK = ROOT / '.local-state/official-rc2-source'

def read(relative):
    return (SDK / relative).read_text()

apps = read('crates/shell/src/apps.rs')
review = read('apps/mail/host-service/src/public_review.rs')
ui = read('crates/shell/src/connected_review.rs')
service = read('apps/mail/host-service/src/lib.rs')
native = ROOT / 'build/pivot-builtin-calendar-original-r5/native'
cargo = (native / 'Cargo.toml').read_text()
main = (native / 'src/main.rs').read_text()
host = ROOT / 'build/pivot-reference-release-r1/muse-calendar-reference-host'
expected = json.loads((host.parent / 'report.json').read_text())['host_sha256']
checks = {
    'release_binary_matches_recorded_sha': hashlib.sha256(host.read_bytes()).hexdigest() == expected,
    'reference_registers_calendar': 'octosense_calendar_service::register();' in main,
    'reference_has_no_mail_dependency': 'octosense-mail-service' not in cargo,
    'reference_has_no_mail_registration': 'octosense_mail_service' not in main,
    'official_shell_registers_mail': 'octosense_mail_service::register()' in apps,
    'official_shell_mounts_smtp_review': 'crate::connected_review::smtp_sheet' in apps,
    'official_shell_registers_review_widget': 'crate::connected_review::register();' in apps,
    'missing_review_hook_fails_closed': 'This host has no native Mail review surface' in review,
    'foreground_required': 'if !call.may_prompt || call.from_sheet' in review,
    'physical_down_and_up_required': 'if !down || !up' in review,
    'ui_uses_trusted_physical_input': 'self.trusted_down = makepad_platform::trusted_user_input();' in ui and 'request.approve(down, makepad_platform::trusted_user_input())' in ui,
    'account_grants_are_app_scoped': 'store.granted(app, account)?' in service,
}
report = {'kind': 'READ_ONLY_MAIL_REGISTRATION_SOURCE_AUDIT', 'checks': checks,
          'status': 'PASS_SOURCE_AUDIT' if all(checks.values()) else 'FAIL_SOURCE_AUDIT',
          'host_sha256': expected,
          'reference_source_identity_boundary': 'r5 native source inspected; release report has no frozen source manifest, so binary/source correspondence is not proven',
          'boundary': 'Source assertions only; no runtime dispatch, login, native review, delivery or receipt verification.'}
print(json.dumps(report, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
