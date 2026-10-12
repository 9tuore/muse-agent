#!/usr/bin/env python3
"""Read only frozen startup evidence and explicit source/build files, never profiles."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics

SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
LABEL = re.compile(r'Muse · ([0-9][0-9A-Za-z.\-]*)')
PAIRS = [('menu-before-open.png', 'menu-after-return.png'),
         ('menu-after-return.png', 'apphub-library-before-open.png'),
         ('apphub-library-before-open.png', 'apphub-after-open.png'),
         ('apphub-after-open.png', 'native-initial.png')]


def summary(values):
    assert values and all(v >= 0 for v in values)
    return dict(samples=len(values), median=statistics.median(values), min=min(values), max=max(values))


def startup(directory):
    result = json.loads((directory / 'result.json').read_text())
    rows = result['launches']
    assert len(rows) == result['requested_repetitions'] == 20
    assert all(r.get('input_readback_and_clear') is True and not r.get('error') for r in rows)
    phases = {}
    for a, b in PAIRS:
        values = []
        for row in rows:
            trial = directory / f'{row["number"]:02d}'
            # Hashes are checked against the actual cycle record, not only file existence.
            recorded = {Path(v['path']).name: v['sha256'] for v in row.values()
                        if isinstance(v, dict) and 'path' in v and 'sha256' in v}
            for name in (a, b):
                assert SHA(trial / name) == recorded[name], 'native evidence changed: ' + name
            elapsed = ((trial / b).stat().st_mtime_ns - (trial / a).stat().st_mtime_ns) / 1e9
            assert elapsed >= 0, 'capture timestamps were reordered'
            values.append(elapsed)
        phases[a + ' -> ' + b] = summary(values)
    return dict(raw_status=result['status'], cycles=20,
                observed_seconds={k: summary([r[k] for r in rows]) for k in
                    ['host_ready_seconds', 'muse_ready_seconds', 'interactivity_seconds', 'total_seconds']},
                png_mtime_intervals_seconds=phases,
                evidence_result_sha256=SHA(directory / 'result.json'),
                boundary='Offline old actual R5 evidence. PNG mtimes include polling, input and capture work; they do not isolate a function or prove a new speedup. Raw native-review-pending status is preserved.')


def identities(source, candidate, legacy):
    readable = candidate / 'readable-bundle'
    signed = candidate / 'bundle'
    ident = json.loads((candidate / 'bundle-identity.json').read_text())
    manifest = json.loads((signed / 'manifest.json').read_text())
    text = source.read_text()
    version = manifest['version']
    source_labels = LABEL.findall(text)
    assert len(source_labels) == 1
    normalized = text.replace('Muse · ' + source_labels[0], 'Muse · ' + version)
    checks = dict(upstream_source_matches=SHA(source) == ident['upstream_source_sha256'],
                  version_matches=version == ident['version'],
                  stamped_readable_matches=hashlib.sha256(normalized.encode()).hexdigest() == SHA(readable / 'main.splash'),
                  transform_source_matches=SHA(readable / 'main.splash') == ident['transform']['source_sha256'],
                  signed_artifact_matches=SHA(signed / 'main.splash') == ident['transform']['artifact_sha256'],
                  readable_ui_version_matches=LABEL.findall((readable / 'main.splash').read_text()) == [version],
                  signed_ui_version_matches=LABEL.findall((signed / 'main.splash').read_text()) == [version])
    old_manifest = json.loads((legacy / 'manifest.json').read_text())
    return dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                source_sha256=SHA(source), source_template_version=source_labels[0],
                candidate_version=version, candidate_ui_version=version,
                candidate_manifest_sha256=SHA(signed / 'manifest.json'),
                signed_artifact_sha256=SHA(signed / 'main.splash'),
                legacy_root_bundle=dict(version=old_manifest['version'], main_sha256=SHA(legacy / 'main.splash')),
                delivery_entry_assessment='Root bundle is a distinct historical artifact; document the supported paired R5 entry instead of silently replacing it.',
                boundary='Source template, stamped readable source and signed artifact are different layers. No private profile, credentials, signing keys, installation, signing or publishing accessed.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--startup', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--legacy-bundle', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    assert not a.out.exists()
    report = dict(startup=startup(a.startup), identity=identities(a.source, a.candidate, a.legacy_bundle))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(identity=report['identity']['status'], cycles=20,
                         full_ready=report['startup']['observed_seconds']['muse_ready_seconds'],
                         after_open=report['startup']['png_mtime_intervals_seconds']['apphub-after-open.png -> native-initial.png'],
                         actual_candidate_ui_version=report['identity']['candidate_ui_version'])))
    return 0 if report['identity']['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
