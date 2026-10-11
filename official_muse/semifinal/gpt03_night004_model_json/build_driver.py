#!/usr/bin/env python3
"""Link a tiny test gateway to existing SDK rlibs; never invoke Cargo or mutate the SDK."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda data: hashlib.sha256(data).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--target', type=Path, required=True)
parser.add_argument('--sdk', type=Path, required=True)
parser.add_argument('--sdk-library', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
out = args.out.resolve(); out.relative_to(ROOT / 'build'); out.mkdir(parents=True, exist_ok=False)
target = args.target.resolve(); deps = target / 'release/deps'; fingerprints = target / 'release/.fingerprint'
library = args.sdk_library.resolve(strict=True); library.relative_to(deps)
suffix = library.stem.removeprefix('liboctosense_llm_service-')
fingerprint = fingerprints / ('octosense-llm-service-' + suffix) / 'lib-octosense_llm_service.json'
sdk_meta = json.loads(fingerprint.read_text()); wanted = {row[1]: row[3] for row in sdk_meta['deps']}
extern = {'octosense_llm_service': library}
dependency_proof = {}
for package, name in [('serde_json', 'serde_json'), ('octosense-llm-config', 'octosense_llm_config'),
                      ('octosense-appstore', 'octosense_appstore')]:
    matches = []
    for directory in fingerprints.glob(package + '-*'):
        marker = directory / ('lib-' + name)
        if marker.is_file() and int.from_bytes(bytes.fromhex(marker.read_text().strip()), 'little') == wanted[name]:
            matches.append(directory)
    assert len(matches) == 1, 'Exact compiled SDK dependency fingerprint required: ' + name
    directory = matches[0]
    extern[name] = deps / ('lib' + name + '-' + directory.name[len(package)+1:] + '.rlib')
    dependency_proof[name] = dict(fingerprint=marker.name, expected_dependency_fingerprint=wanted[name],
        matched_directory=str(directory), rlib_sha256=sha(extern[name].read_bytes()))
sdk = args.sdk.resolve(strict=True)
source_files = ['apps/ai-providers/host-service/src/complete/mod.rs', 'apps/ai-providers/host-service/src/complete/wire.rs',
    'apps/ai-providers/host-service/src/complete/schema.rs', 'apps/ai-providers/host-service/src/complete/ledger.rs',
    'apps/ai-providers/host-service/src/complete/media/mod.rs']
source_identity = {}
for name in source_files:
    path = sdk / name
    assert path.stat().st_mtime <= library.stat().st_mtime, 'SDK source newer than compiled library: ' + name
    source_identity[name] = sha(path.read_bytes())
    saved = out / 'sdk-source' / name; saved.parent.mkdir(parents=True, exist_ok=True); saved.write_bytes(path.read_bytes())
binary = out / 'sdk-model-json-driver'
command = ['rustc', '--edition=2021', str(HERE / 'sdk_driver.rs'), '-o', str(binary), '-L', 'dependency=' + str(deps)]
for name, path in extern.items(): command += ['--extern', name + '=' + str(path)]
for path in sorted((target / 'release/build').glob('*/out')): command += ['-L', 'native=' + str(path)]
result = subprocess.run(command, capture_output=True, text=True)
(out / 'rustc-stdout.log').write_text(result.stdout); (out / 'rustc-stderr.log').write_text(result.stderr)
report = dict(status='LINKED_NOT_RUNTIME_TESTED' if result.returncode == 0 else 'LINK_FAILED', command=command,
    exit_code=result.returncode, rustc_version=subprocess.run(['rustc', '--version'], capture_output=True, text=True, check=True).stdout.strip(),
    library=str(library), library_sha256=sha(library.read_bytes()), sdk_source_sha256=source_identity,
    sdk_fingerprint= sdk_meta, dependency_proof=dependency_proof, driver_source_sha256=sha((HERE/'sdk_driver.rs').read_bytes()),
    driver_binary_sha256=sha(binary.read_bytes()) if binary.is_file() else None,
    boundary='Test-only wrapper links existing actual SDK rlibs. No Cargo, SDK edits, Kernel or GUI. Source snapshots remain read-only inputs.')
(out / 'build-identity.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key:report[key] for key in ['status','exit_code','library_sha256','driver_binary_sha256']}))
raise SystemExit(result.returncode)
