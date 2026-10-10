#!/usr/bin/env python3
"""Compile the actual dependency-path function against filesystem variants."""
import argparse
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    tests = Path(__file__).with_name('dependency_path_tests.rs').read_text()
    rows = []
    for variant, source in [('before', args.before), ('after', args.after)]:
        text = source.read_text()
        start = text.index('pub fn extract_dependency_paths(')
        end = text.index('\npub fn get_crate_dir(', start)
        function = text[start:end].strip()
        fixture = args.out.resolve() / variant / 'fixtures'
        fixture.mkdir(parents=True)
        rust = args.out / (variant + '.rs')
        rust.write_text(tests + '\n' + function + '\n')
        executable = args.out / (variant + '-tests')
        compile_result = subprocess.run(['rustc', '--edition=2021', '--test', str(rust),
                                         '-o', str(executable)], capture_output=True, text=True)
        (args.out / (variant + '-compile.txt')).write_text(
            compile_result.stdout + compile_result.stderr)
        assert compile_result.returncode == 0
        env = dict(os.environ, MUSE_PATH_TEST_ROOT=str(fixture))
        run = subprocess.run([str(executable.resolve())], env=env, capture_output=True, text=True)
        (args.out / (variant + '-run.txt')).write_text(run.stdout + run.stderr)
        rows.append({'variant': variant, 'exit': run.returncode,
                     'summary': next(line for line in run.stdout.splitlines()
                                     if line.startswith('test result:'))})
    report = {'kind': 'ACTUAL_RUST_FUNCTION_REGRESSION', 'cases': 6, 'results': rows,
              'scope': 'Actual source function, not whole APK/runtime acceptance'}
    (args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    assert rows[0]['exit'] != 0 and rows[1]['exit'] == 0


if __name__ == '__main__':
    main()
