#!/usr/bin/env python3
"""Compress only the inventoried owned, closed source/cache files; retain bytes."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import os
import shutil
import stat
import subprocess

p = Path(__file__).resolve().parent
e = p / "evidence"
state = p / ".local-state"
inventory = json.loads((e / "source-cache-compression-inventory.json").read_text())
pending = sorted(inventory["candidates"], key=lambda r: r["bytes"], reverse=True)
floor = 2_000_000_000
reserve = 64 * 1024**2


def digest(f):
    h = hashlib.sha256()
    with f.open("rb") as stream:
        for part in iter(lambda: stream.read(1024**2), b""):
            h.update(part)
    return h.hexdigest()


def closed(files):
    result = subprocess.run(["lsof", "-Fn", *map(str, files)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 1 and not result.stdout


def signature(s):
    return (s.st_ino, s.st_size, s.st_mode, s.st_uid, s.st_gid, s.st_mtime_ns,
            s.st_nlink)


def xattrs(f):
    names = subprocess.check_output(["/usr/bin/xattr", str(f)]).decode().splitlines()
    return {key: subprocess.check_output(["/usr/bin/xattr", "-p", "-x", key, str(f)])
            for key in names}


started = datetime.now().astimezone().isoformat()
free_before = shutil.disk_usage(state).free
replaced = skipped = saved = 0
audit = e / "source-cache-compression-items.jsonl"
assert not audit.exists(), "Do not overwrite an earlier audit"
with audit.open("w") as output:
    while pending:
        free = shutil.disk_usage(state).free
        budget = free - floor - reserve
        if budget <= 0:
            break
        group = []
        for item in pending[:]:
            if len(group) == 16:
                break
            if item["bytes"] <= budget:
                group.append(item)
                pending.remove(item)
                budget -= item["bytes"]
        if not group:
            break
        files = [p / item["path"] for item in group]
        assert closed(files), "Batch has an open file or lsof could not verify it"
        copies = []
        for item, f in zip(group, files):
            s = f.stat()
            assert not f.is_symlink() and s.st_nlink == 1
            assert not any(q.is_symlink() for q in f.parents if q != p and p in q.parents)
            assert s.st_ino == item["inode"] and not s.st_flags & stat.UF_COMPRESSED
            tmp = f.with_name(f.name + ".source-hfs-tmp")
            assert not tmp.exists()
            sha = digest(f)
            attrs = xattrs(f)
            result = subprocess.run(["/usr/bin/ditto", "--hfsCompression", "--noclone",
                                     str(f), str(tmp)], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            assert result.returncode == 0, result.stderr
            new = tmp.stat()
            assert digest(tmp) == sha and new.st_size == s.st_size
            assert (new.st_mode, new.st_uid, new.st_gid, new.st_mtime_ns) == (
                s.st_mode, s.st_uid, s.st_gid, s.st_mtime_ns)
            assert signature(f.stat()) == signature(s)
            new_attrs = xattrs(tmp)
            assert all(new_attrs.get(key) == value for key, value in attrs.items())
            assert shutil.disk_usage(state).free >= floor + reserve
            copies.append((f, tmp, s, new, sha))
        assert closed(files), "Open file before replacement; originals retained"
        for f, tmp, s, new, sha in copies:
            assert signature(f.stat()) == signature(s)
            row = {"path": str(f.relative_to(p)), "sha256": sha, "bytes": s.st_size,
                   "mode": stat.S_IMODE(s.st_mode), "uid": s.st_uid, "gid": s.st_gid,
                   "mtime_ns": s.st_mtime_ns, "original_xattrs_equal": True,
                   "blocks_before": s.st_blocks * 512, "blocks_after": new.st_blocks * 512,
                   "batch_closed_before_and_after_copy": True, "replaced": False}
            if new.st_blocks < s.st_blocks:
                os.replace(tmp, f)
                assert digest(f) == sha and f.stat().st_size == s.st_size
                row["replaced"] = True
                replaced += 1
                saved += (s.st_blocks - new.st_blocks) * 512
            else:
                tmp.unlink()
                skipped += 1
            row["free_after"] = shutil.disk_usage(state).free
            output.write(json.dumps(row) + "\n")
            output.flush()
        print("compressed", replaced, "no saving", skipped, "saved blocks", saved,
              "free", shutil.disk_usage(state).free, "remaining", len(pending), flush=True)
summary = {"started": started, "ended": datetime.now().astimezone().isoformat(),
           "compressed_files": replaced, "no_saving_files": skipped,
           "remaining": len(pending), "saved_blocks_bytes": saved,
           "data_free_before": free_before, "data_free_after": shutil.disk_usage(state).free,
           "resource_floor": floor, "reserve": reserve,
           "dependencies_sources_original_bytes_retained": True, "build_started": False}
(e / "source-cache-compression-summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2), flush=True)
