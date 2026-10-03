#!/usr/bin/env python3
"""Bind the unchanged 60 adapter fixtures to a verified frozen main snapshot.
Does not execute system Calendar services or test the full application UI.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import page_calendar_probe as probe


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(main_path, expected_main_sha, output, port):
    main_path = main_path.resolve()
    main_bytes = main_path.read_bytes()
    adapter_path = probe.SOURCE
    adapter_bytes = adapter_path.read_bytes()
    assert digest(main_bytes) == expected_main_sha, 'main differs from the requested frozen source'
    assert main_bytes.count(adapter_bytes) == 1, 'final main must contain one exact adapter block'
    index = main_bytes.index(adapter_bytes)
    extracted = main_bytes[index:index+len(adapter_bytes)]
    manifest_path = main_path.parent / 'manifest.json'
    manifest_bytes = manifest_path.read_bytes()
    product_version = json.loads(manifest_bytes)['version']
    output.mkdir(parents=True, exist_ok=False)
    (output / 'main-frozen.splash').write_bytes(main_bytes)
    extracted_path = output / 'adapter-from-main.splash'
    extracted_path.write_bytes(extracted)
    # Original fixtures/oracle and card-host execution are unchanged.
    probe.SOURCE = extracted_path
    report = probe.run(output / 'runtime', port)
    assert len(report['checks']) == 60 and all(report['checks'].values()), 'original 60 checks must pass'
    assert digest(main_path.read_bytes()) == expected_main_sha, 'frozen main changed during execution'
    assert digest(adapter_path.read_bytes()) == digest(adapter_bytes), 'adapter changed during execution'
    report.pop('results')
    report.update(passed=60, total=60, product_version=product_version,
                  original_probe_sha256=digest(Path(probe.__file__).read_bytes()),
                  binding_probe_sha256=digest(Path(__file__).read_bytes()),
                  main_binding=dict(path=str(main_path), sha256=expected_main_sha,
                                    snapshot=str(output / 'main-frozen.splash'),
                                    exact_adapter_occurrences=1, extracted_adapter_sha256=digest(extracted),
                                    adapter_byte_offset=index, unchanged_after_run=True,
                                    manifest_sha256=digest(manifest_bytes),
                                    git_head_at_probe=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=probe.ROOT).decode().strip()),
                  scope='same 60 synthetic fixtures executing exact adapter bytes extracted from final main; no real system Calendar/notification/full-UI PASS')
    text = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    (output / 'bound-report.json').write_text(text)
    Path(__file__).with_name('page_final_probe_report.json').write_text(text)
    print(json.dumps(dict(status=report['status'], passed=60, total=60, product_version=product_version,
                          main_sha256=expected_main_sha, adapter_sha256=digest(extracted), evidence=str(output)), ensure_ascii=False))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--main', type=Path, default=probe.ROOT/'official_muse/app/bundle/main.splash')
    parser.add_argument('--expected-main-sha', required=True)
    parser.add_argument('--port', type=int, default=8483)
    parser.add_argument('--output', type=Path, default=probe.ROOT/'official_muse/app/build/ui-memory-20261003'/('page-final-'+datetime.now(probe.ZONE).strftime('%Y%m%d-%H%M%S')))
    args = parser.parse_args()
    run(args.main, args.expected_main_sha, args.output.resolve(), args.port)
