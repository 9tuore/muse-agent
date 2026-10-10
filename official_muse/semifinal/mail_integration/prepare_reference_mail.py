#!/usr/bin/env python3
"""Prepare isolated official SMTP review reference host; does not build/run/send."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tomllib

ROOT = Path(__file__).resolve().parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--base', type=Path, default=ROOT/'build/pivot-builtin-calendar-original-r5')
    parser.add_argument('--sdk', type=Path, default=ROOT/'.local-state/official-rc2-source')
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT/'build') and not out.exists(), 'Fresh ignored build directory required'
    base = args.base.resolve(strict=True)
    sdk = args.sdk.resolve(strict=True)
    native_manifest = tomllib.loads((base/'native/Cargo.toml').read_text())
    widgets = native_manifest['dependencies']['makepad-widgets']['path']
    connected = sdk/'crates/shell/src/connected_review.rs'
    production = connected.read_text().split('#[cfg(test)]', 1)[0]
    assert 'crate::' not in production and 'super::' not in production
    host = (base/'native/src/host.rs').read_text()
    assert 'services::pump(cx,' in host and 'services::is_sheet_input_event(event)' in host
    assert 'self.host_sheet.handle_event(cx, event' in host
    assert 'trusted_user_input()' in production
    main_text = (base/'native/src/main.rs').read_text()
    assert main_text.count('fn main() {') == 1
    assert 'octosense_mail_service' not in main_text
    root_text = (base/'Cargo.toml').read_text()
    root_manifest = tomllib.loads(root_text)
    workspace = root_manifest['workspace']['dependencies']
    sdk_dependencies = tomllib.loads((sdk/'Cargo.toml').read_text())['workspace']['dependencies']
    wanted = ['uuid', 'url', 'oauth2', 'reqwest']
    # Preserve the exact verified official version/options rather than invent versions.
    def dependency_line(name):
        spec = sdk_dependencies[name]
        if isinstance(spec, str): return name+' = '+json.dumps(spec)
        assert 'path' not in spec and 'git' not in spec
        def value(v):
            return str(v).lower() if isinstance(v, bool) else json.dumps(v)
        return name+' = {'+', '.join(k+' = '+value(v) for k,v in spec.items())+'}'
    additions = '\n'.join(dependency_line(name) for name in wanted if name not in workspace)
    additions += '\nmakepad-widgets = {path = '+json.dumps(widgets)+'}'
    additions += '\noctosense-mail-service = {path = "mail"}\n'
    root_text = re.sub(r'^members = .*$', 'members = ["calendar", "native", "mail", "oauth"]', root_text, count=1, flags=re.M)
    root_text = root_text.replace('[workspace.dependencies]\n', '[workspace.dependencies]\n'+additions, 1)
    out.mkdir(parents=True)
    for name in ['calendar', 'native']:
        shutil.copytree(base/name, out/name)
    shutil.copytree(sdk/'apps/mail/host-service', out/'mail')
    shutil.copytree(sdk/'crates/oauth-service', out/'oauth')
    shutil.copyfile(connected, out/'native/src/connected_review.rs')
    native_text = (out/'native/Cargo.toml').read_text().replace('muse-calendar-reference-host', 'muse-mail-reference-host')
    native_text = native_text.replace('[dependencies]\n', '[dependencies]\noctosense-mail-service = {path = "../mail"}\noctosense-oauth-service = {path = "../oauth", features = ["host"]}\nuuid = {workspace = true}\n', 1)
    (out/'native/Cargo.toml').write_text(native_text)
    # Register before any isolate is allocated, including the separate host sheet.
    assert main_text.count('mod args;') == 1
    main_text = main_text.replace('mod args;', 'mod connected_review;\nmod args;', 1)
    main_text = main_text.replace('fn main() {', '''fn main() {
    octosense_mail_service::register();
    octosense_mail_service::public_review::on_review(Some(std::sync::Arc::new(connected_review::smtp_sheet)));
    connected_review::register();
    octosense_mail_service::drafts::on_change(Some(std::sync::Arc::new(makepad_widgets::makepad_platform::SignalToUI::set_ui_signal)));''', 1)
    (out/'native/src/main.rs').write_text(main_text)
    (out/'Cargo.toml').write_text(root_text)
    seed_lock = base/'Cargo.lock'
    assert seed_lock.is_file(), 'Verified seed lock required'
    shutil.copyfile(seed_lock, out/'Cargo.lock')
    sources = {str(p.relative_to(out)):sha(p) for name in ['calendar','native','mail','oauth'] for p in sorted((out/name).rglob('*')) if p.is_file()}
    sources.update({name:sha(out/name) for name in ['Cargo.toml', 'Cargo.lock']})
    assert sha(connected) == sources['native/src/connected_review.rs']
    report = {'status':'PREPARED_NOT_BUILT', 'official_review_byte_identical':True,
        'connected_review_sha256':sha(connected), 'source_files':sources,
        'generator_sha256':sha(Path(__file__)),
        'seed_lock':{'path':str(seed_lock), 'sha256':sha(seed_lock), 'copied_byte_identical':sha(seed_lock)==sha(out/'Cargo.lock'), 'status':'SEED_NOT_RESOLVED_FOR_MAIL_OAUTH'},
        'registration_order':['mail real transport', 'official SMTP review hook', 'official isolate review widget', 'official draft UI wake signal', 'existing Calendar service', 'parse args / host run'],
        'boundary':'Reference component, not installed/full Shell. No demo, fake approval, OAuth service registration, accounts inspection, GUI or send.',
        'central_build_command':['cargo','build','--offline','--release','--manifest-path',str(out/'Cargo.toml'),'--target-dir',str(ROOT/'build/official-hub-rc2-target'),'-p','muse-mail-reference-host'],
        'lock_boundary':'Existing lock copied as seed; added Mail/OAuth resolution not yet locked or built.'}
    (out/'prepare_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'source_files'},indent=2))

if __name__ == '__main__': main()
