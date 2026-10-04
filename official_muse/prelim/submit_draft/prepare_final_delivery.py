#!/usr/bin/env python3
"""Plan or stream an approved source inventory plus explicit Root changes.

Required: --source-root, --bundle, --host-app, --out. Use --plan-only until
Root freezes the candidate. No build, signing, Git mutation or full extraction.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import stat
import tarfile

from export_public_source import checked_path, git, sha256_file

PROTECTED = {"private", "keys", "db", "profiles", "profile", "state", "app-data",
             ".host", ".git", "target", "node_modules", "__pycache__", ".venv"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".key", ".pem", ".p12",
                      ".gguf", ".safetensors", ".pt", ".pth", ".onnx", ".ckpt"}
BUNDLE_SUFFIXES = {".card", ".json", ".l0", ".octoscript", ".splash", ".svg",
                   ".png", ".jpg", ".jpeg", ".webp", ".ttf", ".otf", ".txt", ".md"}
# Inspected, previously approved Android policy source; never an overlay exception.
BASELINE_POLICY = "vendor/octosense/rom/vendor/octosense/sepolicy/private/octosense_update.te"
BASELINE_SOURCE_EXCEPTIONS = {
    BASELINE_POLICY,
    "vendor/makepad/tools/open_harmony/deveco/entry/src/main/resources/base/profile/backup_config.json",
    "vendor/makepad/tools/open_harmony/deveco/entry/src/main/resources/base/profile/main_pages.json",
}
BUNDLE_PREFIX = "official_muse/app/bundle/"


def safe_name(name, baseline=False):
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or str(path) != name or "\\" in name:
        raise ValueError("Unsafe/non-canonical path: " + name)
    if any(p in {".", ".."} for p in path.parts):
        raise ValueError("Path traversal: " + name)
    parts = {p.lower() for p in path.parts}
    if PROTECTED & parts and not (baseline and name in BASELINE_SOURCE_EXCEPTIONS):
        raise ValueError("Protected runtime/cache path: " + name)
    if (path.suffix.lower() in FORBIDDEN_SUFFIXES
            or re.search(r"\.(?:db|sqlite3?)(?:-(?:wal|shm|journal))?$", path.name.lower())
            or path.name.lower() in {"secrets.json", "credentials.json"}):
        raise ValueError("Database/key/weight path: " + name)
    if any(p.lower() == ".env" or p.lower().startswith(".env.") for p in path.parts):
        raise ValueError("Environment secret path: " + name)
    return name


def ordinary(root, name, baseline=False):
    safe_name(name, baseline)
    path = checked_path(root, name)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("Not an ordinary file: " + name)
    return path


def digest_value(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Expected an approved SHA256 digest")
    return value


def directory(path):
    absolute = path.absolute()
    if PROTECTED & {p.lower() for p in absolute.parts}:
        raise ValueError("Input directory points into protected data: " + str(path))
    if not absolute.is_dir() or absolute.resolve() != absolute:
        raise ValueError("Input directory missing or uses a symlink: " + str(path))
    return absolute


def validate_links(root, files, links):
    for name, target in links.items():
        safe_name(name)
        path = checked_path(root, name)
        if not path.is_symlink() or os.readlink(path) != target or PurePosixPath(target).is_absolute():
            raise ValueError("Invalid dependency link: " + name)
        resolved = path.resolve(strict=True)
        if root not in resolved.parents or not resolved.is_dir():
            raise ValueError("Dependency link leaves approved source: " + name)
        prefix = resolved.relative_to(root).as_posix() + "/"
        if not any(n.startswith(prefix) for n in files):
            raise ValueError("Dependency target missing from inventory: " + name)


def write_archive(path, files, links, generated):
    """Stream source files, then read back exact members/hashes; never unpack SDK."""
    expected = {name: digest for name, (_, digest) in files.items()}
    expected.update({name: hashlib.sha256(data).hexdigest() for name, data in generated.items()})
    partial = path.with_name(path.name + ".partial")
    with partial.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=1, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT) as package:
                for name, (source, _) in sorted(files.items()):
                    info = source.stat()
                    member = tarfile.TarInfo(name)
                    member.size = info.st_size
                    member.mode = 0o755 if info.st_mode & 0o111 else 0o644
                    with source.open("rb") as stream:
                        package.addfile(member, stream)
                for name, data in sorted(generated.items()):
                    import io
                    member = tarfile.TarInfo(name)
                    member.size, member.mode = len(data), 0o644
                    package.addfile(member, io.BytesIO(data))
                for name, target in sorted(links.items()):
                    member = tarfile.TarInfo(name)
                    member.type, member.linkname, member.mode = tarfile.SYMTYPE, target, 0o777
                    package.addfile(member)
    seen = set()
    with tarfile.open(partial, "r|gz") as package:
        for member in package:
            name = member.name
            if name in seen:
                raise ValueError("Duplicate archive member: " + name)
            seen.add(name)
            if name in links:
                if not member.issym() or member.linkname != links[name]:
                    raise ValueError("Archive dependency link mismatch: " + name)
            elif name in expected and member.isfile():
                digest = hashlib.sha256()
                stream = package.extractfile(member)
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                if digest.hexdigest() != expected[name]:
                    raise ValueError("Archive SHA mismatch: " + name)
            else:
                raise ValueError("Unapproved archive member: " + name)
    if seen != expected.keys() | links.keys():
        raise ValueError("Archive inventory mismatch")
    partial.rename(path)
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path),
            "files": len(expected), "links": len(links), "readback": "PASS"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("source-root", "bundle", "host-app", "out"):
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--change-root", type=Path)
    parser.add_argument("--root-changes", type=Path,
                        help="Root-approved JSON: source_head, files {archive_path: {source, sha256}}, optional review_files")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    os.environ["GIT_OPTIONAL_LOCKS"] = "0"
    root, bundle, host = map(directory, (args.source_root, args.bundle, args.host_app))
    out = args.out.absolute()
    if out.exists() or out.resolve() != out or any(out == p or p in out.parents for p in (root, bundle, host)):
        raise ValueError("Output must be new, without symlinks, outside source/bundle/Host")
    if PROTECTED & {p.lower() for p in out.parts}:
        raise ValueError("Output points into protected data")
    baseline_path = ordinary(root, "SOURCE_MANIFEST.json")
    baseline_bytes = baseline_path.read_bytes()
    baseline = json.loads(baseline_bytes)
    head = git(root, "rev-parse", "HEAD")
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Approved public source has tracked changes")
    files = {name: (ordinary(root, name, baseline=True), digest_value(digest))
             for name, digest in baseline["files"].items()}
    files.pop("SOURCE_MANIFEST.json", None)
    files.pop("BASELINE_SOURCE_MANIFEST.json", None)
    files.pop("DELIVERY_BINDING.json", None)
    links = dict(baseline["relative_dependency_links"])
    validate_links(root, files, links)
    changes, change_root, change_head = {}, None, None
    if bool(args.change_root) != bool(args.root_changes):
        raise ValueError("--change-root and --root-changes must be supplied together")
    if args.root_changes:
        change_root = directory(args.change_root)
        changes = json.loads(ordinary(change_root, args.root_changes.absolute().relative_to(change_root).as_posix()).read_bytes())
        change_head = git(change_root, "rev-parse", "HEAD")
        if changes["source_head"] != change_head:
            raise ValueError("Root changes HEAD differs from approved plan")
        for name, entry in changes["files"].items():
            safe_name(name)
            if name in links or name in {"SOURCE_MANIFEST.json", "BASELINE_SOURCE_MANIFEST.json", "DELIVERY_BINDING.json"}:
                raise ValueError("Overlay conflicts with dependency/metadata path: " + name)
            source = ordinary(change_root, entry["source"])
            expected = digest_value(entry["sha256"])
            if sha256_file(source) != expected:
                raise ValueError("Root change differs from approved SHA256: " + name)
            files[name] = (source, expected)
    bundle_files = {}
    for folder, dirs, names in os.walk(bundle, followlinks=False):
        for name in dirs:
            rel = (Path(folder) / name).relative_to(bundle).as_posix()
            safe_name(rel)
            if (bundle / rel).is_symlink():
                raise ValueError("Bundle directory symlink: " + rel)
        for name in names:
            rel = (Path(folder) / name).relative_to(bundle).as_posix()
            if Path(rel).suffix.lower() not in BUNDLE_SUFFIXES:
                raise ValueError("Non-bundle file: " + rel)
            path = ordinary(bundle, rel)
            bundle_files[BUNDLE_PREFIX + rel] = (path, sha256_file(path))
    for required in ("main.splash", "manifest.json", "listing.json"):
        if BUNDLE_PREFIX + required not in bundle_files:
            raise ValueError("Missing required bundle file: " + required)
    if sum(p.stat().st_size for p, _ in bundle_files.values()) > 8_000_000:
        raise ValueError("Bundle exceeds conservative 8 MB packaging ceiling")
    for name, entry in changes.get("files", {}).items():
        if name in bundle_files and entry["sha256"] != bundle_files[name][1]:
            raise ValueError("Root overlay differs from actual payload: " + name)
    files = {n: entry for n, entry in files.items() if not n.startswith(BUNDLE_PREFIX)}
    files.update(bundle_files)
    manifest = json.loads(ordinary(bundle, "manifest.json").read_bytes())
    listing = json.loads(ordinary(bundle, "listing.json").read_bytes())
    resources = [listing["icon"]] + listing["screenshots"]
    for resource in resources:
        if BUNDLE_PREFIX + safe_name(resource) not in bundle_files:
            raise ValueError("Declared bundle resource absent: " + resource)
    info = plistlib.loads(ordinary(host, "Contents/Info.plist").read_bytes())
    executable = info["CFBundleExecutable"]
    if len(PurePosixPath(executable).parts) != 1:
        raise ValueError("Host executable name traverses paths")
    host_binary = ordinary(host, "Contents/MacOS/" + executable)
    binding = {"status": "PARTIAL", "mode": "PLAN_ONLY" if args.plan_only else "SOURCE_ARCHIVE_NOT_RELEASE",
               "created_at_utc": datetime.now(timezone.utc).isoformat(), "repository_url": baseline["repository_url"],
               "source_head": head, "root_changes_head": change_head, "baseline_version": baseline["version"],
               "root_override_paths": sorted(changes.get("files", {})), "version": manifest["version"], "app_id": manifest["id"],
               "payload_sha256": bundle_files[BUNDLE_PREFIX + "main.splash"][1], "host_sha256": sha256_file(host_binary),
               "host_executable": "Contents/MacOS/" + executable,
               "baseline_manifest_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
               "bundle_manifest_claimed_blake3": manifest.get("integrity", {}).get("bundle_blake3"),
               "gate_build_cold_start": "NOT_EXECUTED", "final_media": "ROOT_MUST_VERIFY", "formal_submission": "NOT_EXECUTED"}
    encoded = lambda value: (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    generated = {"BASELINE_SOURCE_MANIFEST.json": baseline_bytes, "DELIVERY_BINDING.json": encoded(binding)}
    if generated.keys() & files.keys() or files.keys() & links.keys():
        raise ValueError("Generated/source/link member collision")
    inventory = {n: digest for n, (_, digest) in files.items()}
    inventory.update({n: hashlib.sha256(data).hexdigest() for n, data in generated.items()})
    final_manifest = dict(binding, files=inventory, relative_dependency_links=links,
                          note="Actual selected payload; baseline provenance preserved separately. Self hash excluded. PARTIAL is not release acceptance.")
    generated["SOURCE_MANIFEST.json"] = encoded(final_manifest)
    review_names = {n for n in ("README.md", "SOURCE_DELIVERY.md", "THIRD_PARTY_NOTICES.md", "ROUND_ACCEPTANCE.md", "BUILD_EVIDENCE.json") if n in files}
    review_names.update(bundle_files)
    for name in changes.get("review_files", []):
        if safe_name(name) not in files:
            raise ValueError("Review file not in approved source export: " + name)
        review_names.add(name)
    review_files = {n: files[n] for n in sorted(review_names)}
    review_inventory = {"status": "PARTIAL_REVIEW_DRAFT", "binding": binding,
                        "files": {n: {"sha256": d, "bytes": p.stat().st_size} for n, (p, d) in review_files.items()},
                        "native_sdk_included": False, "complete_source_archive": "muse-source.tar.gz"}
    out.mkdir(parents=True)
    (out / "SOURCE_PACKAGE_INVENTORY.json").write_bytes(encoded(final_manifest))
    (out / "DELIVERY_PLAN.json").write_bytes(encoded(dict(binding, files=len(files), links=len(links),
                                                        logical_source_bytes=sum(p.stat().st_size for p, _ in files.values()))))
    (out / "REVIEW_PACKAGE_INVENTORY.json").write_bytes(encoded(review_inventory))
    if not args.plan_only:
        source_result = write_archive(out / "muse-source.tar.gz", files, links, generated)
        review_result = write_archive(out / "muse-review.tar.gz", review_files, {}, {
            "DELIVERY_BINDING.json": encoded(binding), "REVIEW_PACKAGE_INVENTORY.json": encoded(review_inventory)})
        if git(root, "rev-parse", "HEAD") != head or (change_root and git(change_root, "rev-parse", "HEAD") != change_head):
            raise ValueError("Source HEAD changed during export; archives are not final")
        if sha256_file(host_binary) != binding["host_sha256"] or sha256_file(bundle / "main.splash") != binding["payload_sha256"]:
            raise ValueError("Actual payload/Host changed during export; archives are not final")
        (out / "ARCHIVE_VERIFICATION.json").write_bytes(encoded(dict(binding, source=source_result, review=review_result)))
    print(json.dumps(dict(binding, output=str(out), selected_files=len(files), selected_links=len(links)), ensure_ascii=True))


if __name__ == "__main__":
    main()
