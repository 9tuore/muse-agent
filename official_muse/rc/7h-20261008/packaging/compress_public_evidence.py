#!/usr/bin/env python3
"""Transparent compression of idle tracked legacy quality evidence, bytes intact."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import subprocess
import argparse

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'official_muse/rc/7h-20261008/quality'
OUT = ROOT / 'official_muse/rc/7h-20261008/packaging/evidence-compression.json'

def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', action='store_true', help='Idle synthetic legacy quality carriers; private receipt')
    runtime = parser.parse_args().runtime
    destination = OUT
    if runtime:
        destination = ROOT / 'official_muse/rc/7h-20261008/packaging/.local-state/runtime-evidence-compression.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists(), 'Preserve the prior receipt'
    opened = subprocess.run(['lsof', '+D', str(BASE)], capture_output=True)
    assert opened.returncode == 1 and not opened.stdout, 'Evidence has open handles or lsof failed'
    if runtime:
        excluded = {'home', '.host', '.git', 'profiles', 'keys', 'official-cli'}
        files = [os.fsencode(p.relative_to(ROOT)) for p in (BASE / 'runtime').rglob('*')
                 if p.is_file() and not excluded.intersection(p.relative_to(BASE / 'runtime').parts)]
    else:
        files = subprocess.check_output(['git', 'ls-files', '-z', '--', str(BASE)], cwd=ROOT).split(b'\0')
    before_free = shutil.disk_usage(BASE).free
    rows = []
    for raw in files:
        if not raw:
            continue
        path = ROOT / os.fsdecode(raw)
        if path.suffix not in {'.json', '.splash', '.log', '.txt', '.ndjson'} or path.is_symlink():
            continue
        original = path.stat()
        if not stat.S_ISREG(original.st_mode) or original.st_nlink != 1 or original.st_size < 65536:
            continue
        if shutil.disk_usage(BASE).free < original.st_size * 2 + 64 * 1024 * 1024:
            continue
        temporary = path.with_name(path.name + '.compression-pending')
        assert not temporary.exists(), 'Unexpected temporary file; do not overwrite'
        expected = digest(path)
        try:
            subprocess.run(['/usr/bin/ditto', '--hfsCompression', str(path), str(temporary)], check=True, capture_output=True)
            copied = temporary.stat()
            current = path.stat()
            assert digest(temporary) == expected and digest(path) == expected
            assert copied.st_size == original.st_size and stat.S_IMODE(copied.st_mode) == stat.S_IMODE(original.st_mode)
            assert current.st_ino == original.st_ino and current.st_mtime_ns == original.st_mtime_ns
            if copied.st_blocks < original.st_blocks:
                os.replace(temporary, path)
                rows.append({'path':str(path.relative_to(ROOT)), 'sha256':expected,
                             'bytes':original.st_size, 'mode':stat.S_IMODE(original.st_mode),
                             'blocks_before_bytes':original.st_blocks * 512,
                             'blocks_after_bytes':copied.st_blocks * 512})
        finally:
            if temporary.exists():
                temporary.unlink()
        if len(rows) and len(rows) % 100 == 0:
            print(json.dumps({'compressed':len(rows), 'saved_bytes':sum(x['blocks_before_bytes']-x['blocks_after_bytes'] for x in rows)}), flush=True)
    receipt = {'kind':'TRANSPARENT_FILESYSTEM_COMPRESSION', 'tracked_public_files_only':not runtime,
               'all_replaced_files_sha_mode_size_verified':True, 'tests_rerun':False,
               'free_before':before_free, 'free_after':shutil.disk_usage(BASE).free, 'files':rows,
               'saved_allocated_bytes':sum(x['blocks_before_bytes']-x['blocks_after_bytes'] for x in rows)}
    destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'files'}), flush=True)

if __name__ == '__main__':
    main()
