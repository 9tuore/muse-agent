#!/usr/bin/env python3
"""Prepare synthetic damaged primary cases; never reads production user storage."""
import argparse, hashlib, json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--synthetic-seed', type=Path, required=True,
               help='Explicit synthetic64claim fixture directory, never user storage')
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
backup = (a.synthetic_seed / 'memory.backup.json').read_bytes()
settings = (a.synthetic_seed / 'global-memory-settings.json').read_bytes()
saved = json.loads(backup)
if len(saved['claims']) != 64 or len(saved['sources']) != 65:
    raise SystemExit('Expected supplied synthetic64claim/65source fixture')
raw = b'{invalid-json:' + b'x' * (90000 - len(b'{invalid-json:'))
bad_backup = b'{also-invalid:' + b'y' * (90000 - len(b'{also-invalid:'))
digest = hashlib.sha256(raw).hexdigest()
a.out.mkdir(parents=True, exist_ok=False)
for name in ['primary_bad_backup_valid', 'both_bad_stop', 'preserve_write_rejected_stop']:
    folder = a.out / name
    folder.mkdir()
    (folder / 'memory.json').write_bytes(raw)
    (folder / 'memory.backup.json').write_bytes(bad_backup if name == 'both_bad_stop' else backup)
    (folder / 'global-memory-settings.json').write_bytes(settings)
    case = {'id': name, 'raw_bytes': len(raw), 'raw_sha256': digest,
            'preserved_name': 'memory.json.corrupt-' + digest,
            'expected_loaded': name == 'primary_bad_backup_valid',
            'expected_preserved': name == 'primary_bad_backup_valid',
            'write_blocker_entry_cap': name == 'preserve_write_rejected_stop',
            'expected_claims': 64, 'expected_sources': 65,
            'before_file_sha256': {n: hashlib.sha256((folder / n).read_bytes()).hexdigest()
                                  for n in ['memory.json', 'memory.backup.json', 'global-memory-settings.json']}}
    (folder / 'preserve-case.json').write_text(json.dumps(case, indent=2) + '\n')
print(json.dumps({'cases': 3, 'raw_bytes': len(raw), 'raw_sha256': digest,
                  'status': 'PREPARED_NOT_RUN'}, indent=2))
