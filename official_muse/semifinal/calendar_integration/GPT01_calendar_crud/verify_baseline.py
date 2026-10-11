"""Read-only preflight: every source byte must still match before applying."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / 'BASELINE.json').read_text())
mismatches = []
count = 0
for tree, files in data['files'].items():
    root = Path(data['source_roots'][tree])
    for name, hashes in files.items():
        path = root / name
        current = hashlib.sha256(path.read_bytes() if path.exists() else b'').hexdigest()
        count += 1
        if current != hashes['before']:
            mismatches.append({'tree': tree, 'path': name, 'expected_before': hashes['before'], 'actual': current})
print(json.dumps({'files_checked': count, 'baseline_matches': not mismatches, 'mismatches': mismatches}, indent=2))
raise SystemExit(bool(mismatches))
