#!/usr/bin/env python3
"""Compile the independent official tokenizer check, without executing Muse."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--makepad', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--target', type=Path, required=True)
    a = p.parse_args()
    sdk = (a.makepad / 'platform/script').resolve(strict=True)
    source, artifact = a.source.resolve(strict=True), a.artifact.resolve(strict=True)
    out, target = a.out.resolve(), a.target.resolve()
    assert out.is_relative_to(ROOT / 'build') and target.is_relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'src').mkdir()
    shutil.copyfile(Path(__file__).with_name('compact_tokens.rs'), out / 'src/main.rs')
    (out / 'Cargo.toml').write_text('[workspace]\n[package]\nname="muse-compact-token-check"\nversion="0.0.1"\nedition="2021"\n[dependencies]\nmakepad-script={path=' + json.dumps(str(sdk)) + '}\n')
    command = ['cargo', 'run', '--offline', '--manifest-path', str(out / 'Cargo.toml'),
               '--target-dir', str(target), '--', str(source), str(artifact)]
    done = subprocess.run(command, capture_output=True, text=True, timeout=180)
    (out / 'build.log').write_text(done.stderr)
    report = {'status': 'ERROR', 'exit_code': done.returncode,
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
              'checker_sha256': hashlib.sha256((out / 'src/main.rs').read_bytes()).hexdigest(),
              'boundary': 'Official tokenizer/parser only; not execution, Host admission, or external actions.'}
    if done.returncode == 0:
        report.update(json.loads(done.stdout), status='PASS_OFFICIAL_TOKEN_AND_OPCODE_EQUIVALENCE')
    else:
        report['output'] = done.stdout
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return done.returncode


if __name__ == '__main__':
    raise SystemExit(main())
