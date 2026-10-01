#!/usr/bin/env python3
"""Check the reviewed plugin boundary through a copied app's private worker."""

import argparse
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path


PLUGIN_ID = "builtin.text_stats"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    source = args.app.resolve(strict=True)
    resources = source / "Contents/Resources"
    for name in ("desktop_worker.py", "muse_plugins.py", "muse_plugin_manifest.json"):
        if not (resources / name).is_file():
            raise SystemExit("missing_packaged_resource:" + name)
    root = args.output_dir.resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="muse-plugin-package-"))
    root.mkdir(parents=True, exist_ok=True)
    copied = root / "Muse-Plugin-Test.app"
    if copied.exists():
        raise SystemExit("output_app_already_exists")
    shutil.copytree(source, copied, symlinks=True)
    workspace = root / "workspace"
    workspace.mkdir()
    worker_path = copied / "Contents/Resources/desktop_worker.py"
    python_path = copied / "Contents/Resources/python/bin/python3"
    environment = dict(os.environ, GOSIM_LOCAL_INBOX="0", PYTHONUNBUFFERED="1",
                       PYTHONDONTWRITEBYTECODE="1")

    def verify_signature():
        checked = subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(copied)],
                                 capture_output=True, text=True, check=False)
        if checked.returncode:
            raise AssertionError("copied_app_signature_invalid:" + checked.stderr[:180])

    verify_signature()

    def session():
        process = subprocess.Popen([str(python_path), "-B", str(worker_path), str(workspace)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1,
                                   cwd=str(root), env=environment)
        frames = queue.Queue()

        def reader():
            for line in process.stdout:
                try:
                    frames.put(json.loads(line))
                except ValueError:
                    frames.put({"status": "NON_JSON_FRAME"})

        threading.Thread(target=reader, daemon=True).start()

        def call(event):
            process.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
            process.stdin.flush()
            end = time.monotonic() + 12
            while time.monotonic() < end:
                try:
                    result = frames.get(timeout=0.5)
                except queue.Empty:
                    if process.poll() is not None:
                        raise AssertionError("worker_exited:" + str(process.poll()))
                    continue
                if result.get("status") in {"NON_JSON_FRAME", "GOAL_TICK_FAILED"}:
                    raise AssertionError(result)
                return result
            raise AssertionError("worker_response_timeout")

        return process, call

    first, call = session()
    try:
        assert call({"type": "plugin_list"})["plugins"][0]["status"] == "DISABLED"
        assert call({"type": "plugin_run", "plugin_id": PLUGIN_ID,
                     "input": {"text": "你好\n世界"}})["status"] == "BLOCKED"
        assert call({"type": "plugin_decide", "plugin_id": PLUGIN_ID,
                     "decision": "enable"})["status"] == "NEEDS_APPROVAL"
        approval = call({"type": "plugin_decide", "plugin_id": PLUGIN_ID,
                         "decision": "enable", "approved": True})
        assert approval["status"] == "ENABLED" and approval["approval_id"].startswith("plugin-approval:")
        result = call({"type": "plugin_run", "plugin_id": PLUGIN_ID,
                       "input": {"text": "你好\n世界"}})
        assert result["output"] == {"characters": 5, "lines": 2}, result
        assert call({"type": "plugin_run", "plugin_id": "thirdparty.unreviewed",
                     "input": {"text": "x"}})["status"] == "BLOCKED"
    finally:
        first.terminate()
        first.wait(timeout=5)

    second, call = session()
    try:
        assert call({"type": "plugin_list"})["plugins"][0]["status"] == "ENABLED"
        assert call({"type": "plugin_run", "plugin_id": PLUGIN_ID,
                     "input": {"text": "再见"}})["output"] == {"characters": 2, "lines": 1}
        assert call({"type": "plugin_decide", "plugin_id": PLUGIN_ID,
                     "decision": "disable"})["status"] == "DISABLED"
        assert call({"type": "plugin_run", "plugin_id": PLUGIN_ID,
                     "input": {"text": "再见"}})["status"] == "BLOCKED"
        verify_signature()
        print(json.dumps({"status": "PASS", "copied_app": str(copied),
                          "workspace": str(workspace), "approval_id": approval["approval_id"],
                          "manifest_digest": approval["manifest_digest"],
                          "restart_persistence": True, "revocation": True,
                          "unknown_code_blocked": True,
                          "signature_before_after": True}, ensure_ascii=False))
    finally:
        second.terminate()
        second.wait(timeout=5)


if __name__ == "__main__":
    main()
