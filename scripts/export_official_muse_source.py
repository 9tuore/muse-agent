"""Export the competition's official Muse source, without local state or keys."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="a new directory; existing paths are refused")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output.exists():
        raise FileExistsError(args.output)
    core = (root / "official_muse/phase2/core_logic.splash").read_text()
    main = (root / "official_muse/app/bundle/main.splash").read_text()
    core_body = core[core.index("fn core_goal_index"):].strip()
    inline_body = main[main.index("fn core_goal_index"):main.index("fn state_label")].strip()
    if core_body != inline_body:
        raise ValueError("standalone and inlined Core functions differ; resolve before exporting")
    files = list((root / "official_muse/app/bundle").rglob("*"))
    files += list((root / "official_muse/phase2").rglob("*"))
    files += [root / name for name in (
        "official_muse/README.md", "PHASE2_LIVE_ACCEPTANCE.md",
        "PHASE2_LIVE_TEST_REPORT.md", "PHASE2_LIVE_EVIDENCE_INDEX.md")]
    files += [Path(__file__).resolve()]
    excluded = {"__pycache__", ".local-state", "build", ".git", "keys"}
    files = sorted({p for p in files if p.is_file()
                    and not excluded.intersection(p.relative_to(root).parts)
                    and p.suffix in {".py", ".splash", ".json", ".md", ".patch", ".svg", ".png"}})
    for file in files:
        if file.is_symlink():
            raise ValueError(f"source export refuses symlinks: {file.relative_to(root)}")
    args.output.mkdir(parents=True)
    hashes = {}
    for file in files:
        target = args.output / file.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        hashes[str(file.relative_to(root))] = hashlib.sha256(file.read_bytes()).hexdigest()
    shutil.copy2(root / "official_muse/README.md", args.output / "README.md")
    (args.output / ".gitignore").write_text(
        "build/\n.local-state/\n__pycache__/\n*.pyc\n*.key\n*.pem\n.DS_Store\n")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    manifest = json.loads((root / "official_muse/app/bundle/manifest.json").read_text())
    inventory = {"version": manifest["version"], "source_commit": commit,
                 "bundle_blake3": manifest["integrity"]["bundle_blake3"], "files": hashes,
                 "note": "Local source export only; no GitHub push or issue submission."}
    (args.output / "SOURCE_INVENTORY.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2))
    print(json.dumps({"version": manifest["version"], "files": len(hashes),
                      "output": str(args.output.resolve())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
