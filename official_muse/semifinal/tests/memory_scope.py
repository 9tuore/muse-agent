#!/usr/bin/env python3
"""Existing Memory DSL suite on a fixed candidate and isolated jailed storage.

Fixture transport must receive no requests. This does not test model semantics,
real account consent, mail, calendar or native UI.
"""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8509)
    args = parser.parse_args()
    bundle = args.bundle.resolve(strict=True)
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    runner_path = ROOT / 'official_muse/ui_memory/tests/regression_run.py'
    spec = importlib.util.spec_from_file_location('memory_regression_runner', runner_path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    suite = (ROOT / 'official_muse/ui_memory/tests/memory_suite.splash').read_text()
    marker = 'fs.write("memory-report.json",mr.to_json())'
    if suite.count(marker) != 1:
        raise RuntimeError('Expected one existing Memory report marker')
    transport = ('let metadata_calls=[]\n'
                 'fn chain_fixture_request(method,args,cb){ metadata_calls.push(method) '
                 'cb({is_ok:false error:"Memory-only synthetic fixture"}) }\n')
    probe = output / 'memory-probe.splash'
    probe.write_text(transport + suite.replace(marker,
                     'mr.no_tool_requests = metadata_calls.len() == 0\n'
                     '    fs.write("probe.json",mr.to_json())'))
    result = runner.run_suite('mail_calendar_chain', (bundle / 'main.splash').read_text(),
                              bundle, output / 'run', args.port, probe)
    result['boundary'] = 'FIXTURE; actual production Memory functions and jailed fs; zero external requests'
    (output / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
