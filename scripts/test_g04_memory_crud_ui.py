#!/usr/bin/env python3
"""Exercise native correction, pin, and forgetting on one synthetic memory."""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


BEFORE = "Muse synthetic fact before correction."
AFTER = "Muse synthetic fact after correction."
SEED = r'''
import sys
from pathlib import Path
from memory_store import MemoryStore
MemoryStore(Path(sys.argv[1])).remember("synthetic", "g04-native-test", sys.argv[2],
                                        external_id="g04-memory-ui-fixture")
'''


def record(database):
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT id,content,confirmed,pinned,deleted_at FROM memories "
                         "WHERE external_id='g04-memory-ui-fixture'").fetchone()
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    app = root / "GOSIM-Local-Agent.app"
    shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
    workspace = root / "workspace"
    workspace.mkdir()
    resources = app / "Contents/Resources"
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
               GOSIM_LOCAL_INBOX="0", PYTHONPATH=str(resources), PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([str(resources / "python/bin/python3"), "-B", "-c", SEED,
                    str(workspace), BEFORE], env=env, capture_output=True, text=True, check=True)
    database = workspace / "memory.sqlite3"
    assert record(database)[1] == BEFORE
    with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
        proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                env=env, stdout=stdout, stderr=stderr)
        try:
            wait_for("Muse window", lambda: window_ready(proc.pid))
            ax(proc.pid, 'click menu item "管理本机记忆" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
            wait_for("memory editor", lambda: "保存更正" in ax(proc.pid, "get name of buttons of window 1"))
            for target in ('text area 1 of scroll area 1 of window 1',
                           'text area 1 of scroll area 1 of group 1 of window 1'):
                try:
                    ax(proc.pid, "set value of " + target + " to " + json.dumps(AFTER))
                    break
                except AssertionError:
                    continue
            else:
                raise AssertionError("native memory editor inaccessible")
            ax(proc.pid, 'click button "保存更正" of window 1')
            wait_for("corrected memory", lambda: row if (row := record(database)) and
                     row[1] == AFTER and row[2] == 1 else None)
            wait_for("memory editor reopens", lambda: "固定/取消固定" in ax(
                proc.pid, "get name of buttons of window 1"))
            ax(proc.pid, 'click button "固定/取消固定" of window 1')
            wait_for("pinned memory", lambda: record(database)[3] == 1)
            wait_for("memory editor reopens after pin", lambda: "遗忘" in ax(
                proc.pid, "get name of buttons of window 1"))
            ax(proc.pid, 'click button "遗忘" of window 1')
            wait_for("forget confirmation", lambda: "遗忘" in ax(proc.pid, "get name of buttons of window 1"))
            ax(proc.pid, 'click button "遗忘" of window 1')
            wait_for("forgotten memory", lambda: record(database)[4] is not None)
            output = {"status": "PASS_LOCAL", "native_viewed": True,
                      "corrected_and_confirmed": True, "pinned": True,
                      "forgotten_with_tombstone": True, "production_data_used": False}
            (root / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
            print(json.dumps(output, ensure_ascii=False), flush=True)
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=5)
            time.sleep(1)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)


if __name__ == "__main__":
    main()
