#!/usr/bin/env python3
"""Copy the observed Host source, preserving original code/data and dependency trees."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ORIGIN = Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense')
WORK = ROOT / 'official_muse/app/build/ui-memory-20261003/mail-host-033'

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    copy = WORK / 'OctoSense'
    if copy.exists():
        raise SystemExit('Refusing to overwrite an existing isolated source')
    shutil.copytree(ORIGIN, copy, symlinks=True,
                    ignore=shutil.ignore_patterns('target', '.sources', '.git', '.local-state'))
    (copy / '.sources').mkdir()
    links = {}
    for path in (ORIGIN / '.sources').iterdir():
        resolved = path.resolve()
        (copy / '.sources' / path.name).symlink_to(resolved, target_is_directory=True)
        links[path.name] = str(resolved)
    names = ['apps/mail/host-service/src/lib.rs', 'apps/mail/host-service/src/network.rs',
             'apps/calendar/host-service/src/lib.rs', 'apps/calendar/host-service/src/eventkit.m',
             'Cargo.toml', 'Cargo.lock', 'native-runtime.lock.json', 'runtime-patches.lock.json']
    record = dict(source=str(ORIGIN), isolated_source=str(copy),
                  git_provenance='source snapshot without Git metadata; no claimed upstream commit',
                  dependency_links_read_only=links,
                  baseline_sha256={name: hashlib.sha256((ORIGIN/name).read_bytes()).hexdigest() for name in names},
                  original_host_binary_sha256=hashlib.sha256((ORIGIN/'target/release/octosense').read_bytes()).hexdigest(),
                  git_author_email_checked=subprocess.check_output(['git', 'config', 'user.email'], cwd=ROOT).decode().strip())
    Path(__file__).with_name('source_provenance.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(isolated_source=str(copy), baseline_mail_lib_sha256=record['baseline_sha256'][names[0]])))

if __name__ == '__main__':
    main()
