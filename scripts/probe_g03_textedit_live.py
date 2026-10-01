#!/usr/bin/env python3
"""Open only a fresh synthetic TextEdit document and inspect its AX controls."""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_ax_adapter import AXUnavailable, NativeAXAdapter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--helper", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--name", default="Muse-G03-Synthetic.txt")
    args = parser.parse_args()
    if not re.fullmatch(r"Muse-G03-[A-Za-z0-9-]{1,40}\.txt", args.name):
        raise ValueError("synthetic_filename_required")
    args.root.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="muse-g03-textedit-", dir=args.root))
    document = directory / args.name
    document.write_text("Muse G-03 synthetic document.\n", encoding="utf-8")
    opened = subprocess.run(["/usr/bin/open", "-a", "/System/Applications/TextEdit.app", str(document)],
                            capture_output=True, text=True, timeout=10, check=False)
    if opened.returncode:
        print(json.dumps({"status": "OPEN_FAILED", "returncode": opened.returncode}))
        return 1
    adapter = NativeAXAdapter(args.helper)
    for _ in range(10):
        time.sleep(0.5)
        try:
            snapshot = adapter.snapshot("com.apple.TextEdit")
        except AXUnavailable as exc:
            print(json.dumps({"status": exc.result.get("status"), "ax_error": exc.result.get("ax_error"),
                              "document": str(document)}))
            return 0
        nodes = [node for node in snapshot["elements"]
                 if args.name == node.get("window_title", "") and
                 (node.get("path", "").startswith("w") or node.get("name") in {"Save", "存储"})]
        if nodes:
            print(json.dumps({"status": "OBSERVED", "document": str(document),
                              "observed_at": snapshot["observed_at"], "controls": [
                                  {key: node.get(key) for key in ("role", "name", "path", "actions", "window_title")}
                                  for node in nodes]}, ensure_ascii=False))
            return 0
    print(json.dumps({"status": "NO_SYNTHETIC_WINDOW", "document": str(document),
                      "observed_elements": len(snapshot["elements"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
