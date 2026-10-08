#!/usr/bin/env python3
"""Prepare hash-verified CMake CLI in this task's isolated tools."""
from pathlib import Path
import hashlib
import json
import shutil
import tarfile
import urllib.request
import subprocess
p = Path(__file__).resolve().parent
state = p / ".local-state"
assets = json.loads((p / "evidence/cmake-release-assets.json").read_text())["assets"]
item = next(a for a in assets if a["name"].endswith("macos-universal.tar.gz"))
sha_item = next(a for a in assets if a["name"].endswith("SHA-256.txt"))
with urllib.request.urlopen(sha_item["url"], timeout=30) as r:
    checksums = r.read().decode()
expected = next(line.split()[0] for line in checksums.splitlines() if line.split()[-1] == item["name"])
archive = state / "downloads" / item["name"]
with urllib.request.urlopen(item["url"], timeout=60) as remote, archive.open("wb") as out:
    shutil.copyfileobj(remote, out, 1024 * 1024)
assert archive.stat().st_size == item["bytes"]
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected
root = state / "tools/cmake-3.31.6"
assert not root.exists()
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    entry = next(m.name for m in members if m.name.endswith("/Contents/bin/cmake"))
    prefix = entry[:-len("bin/cmake")]
    for m in members:
        if not m.name.startswith(prefix):
            continue
        rel = m.name[len(prefix):]
        if rel != "bin/cmake" and not rel.startswith("share/cmake-3.31/"):
            continue
        dest = root / rel
        assert dest.resolve().is_relative_to(root.resolve())
        if m.isdir():
            dest.mkdir(parents=True, exist_ok=True)
        elif m.isfile():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(m) as src, dest.open("wb") as out:
                shutil.copyfileobj(src, out)
            dest.chmod(m.mode)
        else:
            raise RuntimeError("Unexpected selected CMake archive member type")
link = state / "tools/bin/cmake"
link.symlink_to((root / "bin/cmake").resolve())
version = subprocess.check_output([str(link), "--version"], text=True)
(p / "evidence/cmake-cli-verified.json").write_text(json.dumps({"url": item["url"],
    "sha256_url": sha_item["url"], "sha256": expected, "bytes": item["bytes"],
    "version_output": version, "scope": "own CLI plus required CMake modules, no system install"}, indent=2))
archive.unlink()
print(version, flush=True)
