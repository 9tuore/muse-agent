#!/usr/bin/env python3
"""Export an already approved public SOURCE_MANIFEST inventory, without deletion.

The output is a source snapshot, not a release or an App Hub bundle. Only listed
regular files, SOURCE_MANIFEST.json itself, and listed internal links are read.
No directory walk, Git history export, dependency changes, or runtime calls occur.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tarfile
from datetime import datetime, timezone


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def checked_path(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(p in {"", ".", ".."} for p in path.parts):
        raise ValueError("Unsafe inventory path: " + name)
    if "\\" in name or str(path) != name:
        raise ValueError("Non-canonical inventory path: " + name)
    for parent in path.parents:
        if parent != PurePosixPath(".") and (root / parent).is_symlink():
            raise ValueError("Symlink parent: " + name)
    return root / path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source.resolve(strict=True)
    output = args.output.resolve()
    if output == root or root in output.parents:
        raise ValueError("Output must be outside the read-only source checkout")
    if output.exists():
        raise FileExistsError(output)
    if git(root, "rev-parse", "HEAD") != args.source_head:
        raise ValueError("Public source HEAD differs from requested snapshot")
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Public checkout has tracked changes")
    manifest_path = root / "SOURCE_MANIFEST.json"
    manifest_hash = sha256_file(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = dict(manifest["files"])
    if "SOURCE_MANIFEST.json" in expected:
        raise ValueError("Manifest must not contain its own hash")
    expected["SOURCE_MANIFEST.json"] = manifest_hash
    links = manifest["relative_dependency_links"]
    if expected.keys() & links.keys():
        raise ValueError("A path is declared as both a regular file and a link")
    excluded_parts = {".git", "target", "node_modules", "__pycache__", ".venv"}
    weight_extensions = {".gguf", ".safetensors", ".pt", ".pth", ".onnx", ".ckpt"}
    logical = 0
    modes = {}
    for name, digest in expected.items():
        path = checked_path(root, name)
        if excluded_parts.intersection(PurePosixPath(name).parts) or path.suffix.lower() in weight_extensions:
            raise ValueError("Inventory includes excluded runtime/cache/weight path: " + name)
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Not an ordinary file: " + name)
        if sha256_file(path) != digest:
            raise ValueError("Approved file hash differs: " + name)
        logical += info.st_size
        modes[name] = 0o755 if info.st_mode & 0o111 else 0o644
    for name, target in links.items():
        path = checked_path(root, name)
        if not path.is_symlink() or os.readlink(path) != target:
            raise ValueError("Dependency link differs: " + name)
        resolved = path.resolve(strict=True)
        if root not in resolved.parents or not resolved.is_dir():
            raise ValueError("Dependency link leaves the export: " + name)
        relative = resolved.relative_to(root).as_posix() + "/"
        if not any(p.startswith(relative) for p in expected):
            raise ValueError("Dependency link target has no exported source: " + name)
    output.mkdir(parents=True)
    prefix = "muse-source-" + manifest["version"] + "-" + args.source_head[:7]
    archive = output / (prefix + ".tar.gz")
    partial = output / (prefix + ".tar.gz.partial")
    print(json.dumps({"stage": "inventory_verified", "regular_files": len(expected),
                      "internal_links": len(links), "logical_bytes": logical}), flush=True)
    with partial.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=1, mtime=0) as compressed:
            with tarfile.open(mode="w|", fileobj=compressed, format=tarfile.PAX_FORMAT) as package:
                for name in sorted(expected):
                    path = root / name
                    member = tarfile.TarInfo(prefix + "/" + name)
                    member.size = path.stat().st_size
                    member.mode = modes[name]
                    with path.open("rb") as stream:
                        package.addfile(member, stream)
                for name, target in sorted(links.items()):
                    member = tarfile.TarInfo(prefix + "/" + name)
                    member.type = tarfile.SYMTYPE
                    member.linkname = target
                    member.mode = 0o777
                    package.addfile(member)
    print(json.dumps({"stage": "archive_created", "bytes": partial.stat().st_size}), flush=True)
    seen = set()
    with tarfile.open(partial, "r|gz") as package:
        for member in package:
            if not member.name.startswith(prefix + "/"):
                raise ValueError("Unexpected archive root")
            name = member.name[len(prefix) + 1:]
            if name in seen:
                raise ValueError("Duplicate archive member: " + name)
            seen.add(name)
            if name in links:
                if not member.issym() or member.linkname != links[name]:
                    raise ValueError("Archive link mismatch: " + name)
            elif name in expected and member.isfile():
                digest = hashlib.sha256()
                stream = package.extractfile(member)
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                if digest.hexdigest() != expected[name] or member.mode != modes[name]:
                    raise ValueError("Archive file/mode mismatch: " + name)
            else:
                raise ValueError("Unapproved archive member: " + name)
    if seen != expected.keys() | links.keys():
        raise ValueError("Archive inventory mismatch")
    if git(root, "rev-parse", "HEAD") != args.source_head or sha256_file(manifest_path) != manifest_hash:
        raise ValueError("Source snapshot changed during export")
    partial.rename(archive)
    result = {
        "status": "SOURCE_SNAPSHOT_VERIFIED_NOT_RELEASE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_repository": manifest["repository_url"], "source_head": args.source_head,
        "version": manifest["version"], "source_manifest_sha256": manifest_hash,
        "regular_file_count": len(expected), "internal_link_count": len(links),
        "input_regular_file_logical_bytes": logical, "archive_bytes": archive.stat().st_size,
        "compression_saved_bytes_same_inventory": logical - archive.stat().st_size,
        "archive_sha256": sha256_file(archive), "archive_name": archive.name,
        "readback_hashes_and_executable_modes": "PASS", "exact_archive_members": "PASS",
        "internal_dependency_links": "PASS", "source_deletions": 0,
        "workspace_bytes_freed": 0, "git_history_rewritten": False,
        "build_gate_cold_start": "NOT_EXECUTED", "publisher_review": "NOT_EXECUTED",
        "product_acceptance": manifest["delivery"]["product_acceptance_counts"],
        "note": "Every approved file retained, including public historical failures, licenses, locks and SDK resources. No public checkout writes. Compression comparison uses identical regular-file inventory; it is not disk cleanup."
    }
    (output / "EXPORT_VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
