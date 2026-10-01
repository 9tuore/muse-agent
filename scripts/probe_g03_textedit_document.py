#!/usr/bin/env python3
"""Check synthetic TextEdit AXDocument URL before product recipe integration."""

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_ax_adapter import AXUnavailable, NativeAXAdapter


def main():
    root = Path("/tmp/gosim-g03-textedit-goal/notes")
    root.mkdir(parents=True, exist_ok=True)
    path = root / "Muse-Test-Alpha.txt"
    if not path.exists():
        path.write_text("Muse synthetic starting text.\n", encoding="utf-8")
    opened = subprocess.run(["/usr/bin/open", "-a", "/System/Applications/TextEdit.app", str(path)],
                            capture_output=True, text=True, timeout=10, check=False)
    adapter = NativeAXAdapter(Path("/tmp/gosim-g03-build/muse_ax_helper"), window_title=path.name)
    result = {"open_returncode": opened.returncode, "path": str(path)}
    for _ in range(10):
        time.sleep(0.4)
        try:
            result["document"] = adapter.document_url("com.apple.TextEdit", path.name)
            result["snapshot"] = {"element_count": len(adapter.snapshot("com.apple.TextEdit")["elements"])}
        except AXUnavailable as exc:
            result["error"] = exc.result
            continue
        if result["document"].get("status") == "COMPLETED":
            break
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
