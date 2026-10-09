#!/usr/bin/env python3
"""Read-only bundle layout/byte checks, not Hub admission or app execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def files(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("Bundle must contain ordinary files: " + str(path))
        if path.is_file():
            name = path.relative_to(folder).as_posix()
            if path.suffix.lower() not in {".json", ".splash", ".svg", ".png"}:
                raise ValueError("Unexpected file in this Muse bundle: " + name)
            result[name] = {"bytes": path.stat().st_size,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    return result


def check(root, reference=None):
    bundle = root / "bundle"
    if not bundle.is_dir() or bundle.is_symlink():
        raise ValueError("bundle/ must be the real canonical directory")
    alias = root / "official_muse/app/bundle"
    if not alias.is_symlink() or alias.readlink() != Path("../../bundle") or alias.resolve() != bundle.resolve():
        raise ValueError("Legacy bundle must be the relative ../../bundle alias")
    inventory = files(bundle)
    for name in ("manifest.json", "listing.json", "main.splash"):
        if name not in inventory:
            raise ValueError("Missing bundle entry: " + name)
    manifest = json.loads((bundle / "manifest.json").read_text())
    listing = json.loads((bundle / "listing.json").read_text())
    screenshots = listing.get("screenshots", [])
    if not isinstance(screenshots, list) or not screenshots:
        raise ValueError("Listing needs actual screenshot references")
    for name in [listing.get("icon", "")] + screenshots:
        if not isinstance(name, str) or name not in inventory:
            raise ValueError("Missing/invalid listing resource: " + str(name))
    if reference is not None and inventory != files(reference):
        raise ValueError("Bundle file set, lengths or hashes differ from reference")
    names = ["bundle/" + name for name in inventory]
    output = subprocess.check_output(["git", "check-attr", "text", "--", *names], cwd=root, text=True)
    if len(output.splitlines()) != len(names) or any(not line.endswith(": text: unset") for line in output.splitlines()):
        raise ValueError("Every bundle file needs .gitattributes -text")
    blockers = []
    integrity = manifest.get("integrity") or {}
    if integrity.get("signature") is not None:
        blockers.append("Legacy signed bytes preserved; GitHub publisher-prepare requires a separately reviewed editable release, not this sealed local rehearsal.")
    if "github" in integrity or "publisher-github-v1" in (manifest.get("requires") or []):
        blockers.append("Already sealed GitHub release: verify its downloaded pack; do not prepare or restamp it.")
    return {"layout": "PASS", "app_id": manifest["id"], "version": manifest["version"],
            "files": inventory, "reference_byte_equal": reference is not None,
            "alias": "official_muse/app/bundle -> ../../bundle",
            "git_text_attributes": "unset", "github_prepare_blockers": blockers,
            "boundary": "Layout only. No Hub gate, signature verification, GUI, provider call or publication."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reference", type=Path, help="Optional immutable source bundle for exact migration comparison")
    parser.add_argument("--for-github-release", action="store_true", help="Also refuse sealed source bytes; does not grant release approval")
    parser.add_argument("--out", type=Path, help="Optional report outside bundle/")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        report = check(root, args.reference)
        if args.out:
            output = args.out.resolve()
            if output == root / "bundle" or (root / "bundle") in output.parents:
                raise ValueError("Reports belong outside bundle/")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if args.for_github_release and report["github_prepare_blockers"] else 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print("release-layout: REFUSED: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
