#!/usr/bin/env python3
"""Keep identical idle fixture images at their paths using APFS COW clones."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'official_muse/rc/7h-20261008/quality/runtime'
PRIVATE = ROOT / 'official_muse/rc/7h-20261008/packaging/.local-state/image-clones.json'
SUMMARY = ROOT / 'official_muse/rc/7h-20261008/packaging/image-clones-summary.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def attrs(path):
    return subprocess.check_output(['/usr/bin/xattr', '-lx', str(path)])

def main():
    assert not PRIVATE.exists() and not SUMMARY.exists()
    opened = subprocess.run(['lsof', '+D', str(BASE)], capture_output=True)
    assert opened.returncode == 1 and not opened.stdout
    before = shutil.disk_usage(BASE).free
    unique = {}
    rows = []
    for path in BASE.rglob('*'):
        if path.suffix not in {'.png', '.jpg', '.svg'} or path.is_symlink() or not path.is_file():
            continue
        original = path.stat()
        if original.st_nlink != 1 or original.st_flags != 0:
            continue
        checksum = digest(path)
        key = (checksum, stat.S_IMODE(original.st_mode), original.st_uid, original.st_gid)
        if key not in unique:
            unique[key] = path
            continue
        source = unique[key]
        if attrs(source) != attrs(path):
            continue
        pending = path.with_name(path.name + '.clone-pending')
        assert not pending.exists()
        try:
            subprocess.run(['/bin/cp', '-c', '-p', str(source), str(pending)], check=True, capture_output=True)
            os.utime(pending, ns=(original.st_atime_ns, original.st_mtime_ns))
            copied = pending.stat()
            assert digest(pending) == checksum and digest(path) == checksum
            assert copied.st_size == original.st_size and copied.st_mode == original.st_mode
            assert (copied.st_uid, copied.st_gid, copied.st_mtime_ns) == (original.st_uid, original.st_gid, original.st_mtime_ns)
            assert attrs(pending) == attrs(path)
            current = path.stat()
            assert (current.st_ino, current.st_mtime_ns) == (original.st_ino, original.st_mtime_ns)
            os.replace(pending, path)
            rows.append({'path':str(path.relative_to(ROOT)), 'source':str(source.relative_to(ROOT)),
                         'sha256':checksum, 'bytes':original.st_size})
        finally:
            if pending.exists():
                pending.unlink()
    result = {'kind':'APFS_COW_IDENTICAL_FIXTURE_IMAGES', 'replaced_files':len(rows),
              'initial_probe_failure':'Local Python lacked os.listxattr; first duplicate preflight stopped before replacement; switched to verified macOS xattr -lx',
              'raw_bytes_mode_owner_mtime_xattrs_verified':True, 'paths_preserved':True,
              'free_before':before, 'free_after':shutil.disk_usage(BASE).free,
              'free_change_includes_other_process_activity':True, 'tests_rerun':False}
    PRIVATE.parent.mkdir(parents=True, exist_ok=True)
    PRIVATE.write_text(json.dumps({'summary':result, 'files':rows}, ensure_ascii=False, indent=2) + '\n')
    SUMMARY.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)

if __name__ == '__main__':
    main()
