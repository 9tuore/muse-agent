#!/usr/bin/env python3
"""Verify saved actual VM samples and bad-input outcomes; no runtime rerun."""
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence/memory-abba-r1'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    report = json.loads((EVIDENCE / 'report.json').read_text())
    assert report['status'] == 'PASS' and all(report['checks'].values())
    assert SHA(EVIDENCE / 'executed-parent.py') == report['runner_sha256']
    identities = {}
    for name in ['baseline', 'candidate']:
        identities[name] = json.loads((EVIDENCE / (name + '-identity.json')).read_text())
        assert SHA(EVIDENCE / (name + '-executed.splash')) == identities[name]['executed_sha256']
    records = []
    for i, name in enumerate(report['order']):
        r = json.loads((EVIDENCE / f'{i+1}-{name}.json').read_text())
        assert r['source_identity'] == identities[name]
        assert r['memory_sha256'] == report['dataset_sha256'] and all(r['checks'].values())
        assert len(r['samples']) == 96 and len(r['outcomes']) == 22
        assert r['outcomes'] == report['outcomes']
        outcomes = {p['name']: p['accepted'] for p in r['outcomes']}
        for kind, phase in [('source', 'sources'), ('claim', 'claims')]:
            assert outcomes[kind + ':all:0'] is False
            assert outcomes[kind + ':' + phase + ':0'] is False
            assert outcomes[kind + ':' + phase + ':2'] is True
        assert outcomes['source:claims:0'] is True and outcomes['claim:sources:0'] is True
        for sample in r['samples']:
            assert sample['elapsed_ns'] == sample['end_ns'] - sample['start_ns'] > 0
        records.append((name, r))
    for name in ['baseline', 'candidate']:
        for phase, expected in report['measurements'][name].items():
            values = [s['elapsed_ns'] for n, r in records if n == name for s in r['samples'] if s['phase'] == phase]
            ordered = sorted(values)
            assert len(values) == expected['samples']
            assert statistics.median(values)/1e6 == expected['median_ms']
            assert ordered[(95*len(values)+99)//100-1]/1e6 == expected['p95_ms']
    print(json.dumps(dict(status='PASS', actual_passes=4, actual_slice_intervals=384,
                         preserved_bad_input_outcomes=22, extra_runtime_runs=0)))


if __name__ == '__main__':
    main()
