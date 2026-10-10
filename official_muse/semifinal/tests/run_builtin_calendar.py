#!/usr/bin/env python3
"""Compile byte-identical official Calendar with the real prepared App Hub.

This tests the built-in service and its durable store, not Muse admission,
the Shell approval router, or a running Calendar UI. No EventKit/network calls.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument('--hub', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--protocol', action='store_true', help='Run independent-process real service CRUD and restart checks')
    p.add_argument('--native', action='store_true', help='Also build the original Calendar reference UI host; never admits Muse as system')
    p.add_argument('--patch-calendar', action='store_true', help='Test the isolated review patch; not the original official release')
    a = p.parse_args()
    sdk, hub = a.sdk.resolve(strict=True), a.hub.resolve(strict=True)
    out = a.out.resolve()
    assert out.is_relative_to(ROOT / 'build') and not out.exists()
    out.mkdir(parents=True)
    original = sdk / 'apps/calendar/host-service'
    shutil.copytree(original, out / 'calendar')
    source_files = sorted(original.rglob('*'))
    identity = {str(f.relative_to(original)): sha(f) for f in source_files if f.is_file()}
    assert all(sha(out / 'calendar' / n) == digest for n, digest in identity.items())
    hub_config = tomllib.loads((hub / 'Cargo.toml').read_text())
    members = ['calendar']
    if a.protocol:
        client = out / 'client'
        (client / 'src').mkdir(parents=True)
        shutil.copyfile(Path(__file__).with_name('builtin_calendar_client.rs'), client / 'src/main.rs')
        (client / 'Cargo.toml').write_text('[package]\nname="muse-calendar-probe"\nversion="0.1.0"\nedition="2021"\n[dependencies]\noctosense-calendar-service={path="../calendar"}\nserde_json={workspace=true}\noctosense-app-policy={path='+json.dumps(str(hub/'crates/app-policy'))+'}\n')
        members.append('client')
    if a.native:
        import re
        native = out / 'native'
        shutil.copytree(hub / 'crates/card-host/src', native / 'src')
        cargo = (hub / 'crates/card-host/Cargo.toml').read_text()
        cargo = cargo.replace('name = "octosense-card-host"', 'name = "muse-calendar-reference-host"').replace('name = "card-host"', 'name = "muse-calendar-reference-host"')
        cargo = re.sub(r'path = "(\.\./[^\"]+)"', lambda m: 'path = ' + json.dumps(str((hub / 'crates/card-host' / m[1]).resolve(strict=True))), cargo)
        # Resolve newly introduced Git dependencies to the same verified
        # prepared checkouts without an unavailable offline Git metadata lookup.
        dependencies = tomllib.loads(cargo)['dependencies']
        for name, spec in dependencies.items():
            if 'git' not in spec: continue
            prepared = hub_config['patch'][spec['git']][name]
            path = (hub / prepared['path']).resolve(strict=True)
            options = ', features = ' + json.dumps(spec['features']) if 'features' in spec else ''
            replacement = name + ' = {path = ' + json.dumps(str(path)) + options + '}'
            cargo = re.sub(r'^' + re.escape(name) + r' = .*$', lambda _: replacement, cargo, flags=re.M)
        cargo = cargo.replace('[dependencies]', '[dependencies]\noctosense-calendar-service = {path = "../calendar"}')
        (native / 'Cargo.toml').write_text(cargo)
        main_path = native / 'src/main.rs'
        main_path.write_text(main_path.read_text().replace('fn main() {', 'fn main() {\n    octosense_calendar_service::register();'))
        members.append('native')
    shutil.copytree(sdk / 'apps/calendar/bundle', out / 'bundle')
    patch_sha = None
    if a.patch_calendar:
        from prepare_builtin_calendar_patch import prepare
        patch_sha = prepare(sdk, out)
    workspace = ['[workspace]', 'resolver = "2"', 'members = ' + json.dumps(members),
                 '[workspace.dependencies]',
                 f'octosense-appstore = {{path = {json.dumps(str(hub / "crates/appstore"))}, default-features = false}}',
                 'serde = {version = "1", features = ["derive"]}', 'serde_json = "1"',
                 'chrono = {version = "0.4", features = ["serde"]}', 'chrono-tz = "0.10.4"']
    for origin, items in hub_config['patch'].items():
        workspace.append(f'[patch.{json.dumps(origin)}]')
        for name, spec in items.items():
            path = (hub / spec['path']).resolve(strict=True)
            workspace.append(f'{name} = {{path = {json.dumps(str(path))}}}')
    (out / 'Cargo.toml').write_text('\n'.join(workspace) + '\n')
    # Preserve the prepared framework's resolution; a fresh offline graph
    # otherwise asks Git for replaced source metadata that is not cached.
    shutil.copyfile(hub / 'Cargo.lock', out / 'Cargo.lock')
    report = {'kind': 'OFFICIAL_BUILTIN_CALENDAR_SERVICE_WITH_REAL_APPSTORE', 'status': 'ERROR',
              'source_files': identity, 'source_byte_identical': not a.patch_calendar, 'patch_sha256':patch_sha,
              'sdk_head': subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip(),
              # The prepared Hub has no .git; git -C would silently return the enclosing Muse HEAD.
              'hub_head': json.loads((hub.parent / 'identity.json').read_text())['app_hub'],
              'boundary': 'Official service unit tests with actual App Hub library. Not a running Shell UI, Muse tool grant, native approval, or full business chain.'}
    cmd = ['cargo', 'test', '--offline', '--manifest-path', str(out / 'Cargo.toml'),
           '--target-dir', str(a.target.resolve()), '-p', 'octosense-calendar-service',
           '--', '--test-threads=1']
    report['command'] = cmd
    try:
        with (out / 'test.log').open('w') as log:
            done = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=600)
        report['exit_code'] = done.returncode
        report['status'] = 'PASS_OFFICIAL_SERVICE_UNIT' if done.returncode == 0 else 'BUILD_OR_TEST_FAILED'
        if done.returncode == 0 and (a.protocol or a.native):
            build = cmd[:cmd.index('-p')]
            build[1] = 'build'
            for name, enabled in [('muse-calendar-probe', a.protocol), ('muse-calendar-reference-host', a.native)]:
                if enabled:
                    with (out / (name + '.log')).open('w') as log:
                        result = subprocess.run(build + ['-p', name], stdout=log, stderr=subprocess.STDOUT, timeout=600)
                    report[name + '_build_exit'] = result.returncode
                    if result.returncode == 0:
                        (out/'bin').mkdir(exist_ok=True)
                        shutil.copyfile(a.target.resolve()/'debug'/name,out/'bin'/name)
                        (out/'bin'/name).chmod(0o755)
                        report[name + '_sha256'] = sha(out/'bin'/name)
                    if result.returncode: report['status'] = 'BUILD_OR_TEST_FAILED'
            if a.protocol and report.get('muse-calendar-probe_build_exit') == 0:
                from builtin_calendar_protocol import run
                report['protocol'] = run(out/'bin/muse-calendar-probe', out, patched=a.patch_calendar)
                if not all(report['protocol']['checks'].values()): report['status'] = 'FAIL_PROTOCOL'
                if a.patch_calendar and not all(report['protocol']['known_gaps'].values()): report['status']='FAIL_PATCH_GAPS'
    except Exception as error:
        report['error'] = str(error)
    report['log_sha256'] = sha(out / 'test.log')
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report.get(k) for k in ('status', 'exit_code', 'error')}))
    return 0 if report['status'] == 'PASS_OFFICIAL_SERVICE_UNIT' else 1


if __name__ == '__main__':
    raise SystemExit(main())
