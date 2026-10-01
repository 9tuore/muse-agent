#!/usr/bin/env python3
"""Drive the packaged TextEdit synthetic-file Goal through native controls."""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
import uuid
from pathlib import Path

from test_muse_desktop_package import ax, goal_row, wait_for, window_ready


BEFORE = "Muse synthetic starting text.\n"
AFTER = "Muse G04 approved synthetic save.\n"


def run():
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
    notes = workspace / "notes"
    notes.mkdir(parents=True)
    document = notes / f"Muse-Test-G04-{uuid.uuid4().hex[:8]}.txt"
    document.write_text(BEFORE, encoding="utf-8")
    helper = app / "Contents/Resources/muse_ax_helper"
    status = json.loads(subprocess.check_output([str(helper), "status"], text=True))
    assert status["prompt_requested"] is False, status
    opened = subprocess.run(["/usr/bin/open", "-a", "TextEdit", str(document)],
                            capture_output=True, text=True, timeout=10)
    assert opened.returncode == 0, opened.stderr
    def document_ready():
        result = json.loads(subprocess.check_output(
            [str(helper), "document", "com.apple.TextEdit", document.name], text=True))
        return result if result.get("status") == "COMPLETED" and str(document) in result.get("document_url", "") else None
    doc_state = wait_for("TextEdit document", document_ready, seconds=20)
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
               GOSIM_LOCAL_INBOX="0")
    lock_path = Path("/tmp/gosim-muse-5agent-20260928/gui.lock")
    lock_path.parent.mkdir(mode=0o700, exist_ok=True)
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    lock_held = True
    with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
        proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                env=env, stdout=stdout, stderr=stderr)
        try:
            wait_for("Muse window", lambda: window_ready(proc.pid))
            ax(proc.pid, 'click menu item "TextEdit 合成文件配方" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
            wait_for("TextEdit recipe dialog", lambda: "生成待批准计划" in ax(
                proc.pid, "get name of buttons of window 1"))
            selectors = (
                'text area "TextEdit 合成文件新内容" of window 1',
                'text area 1 of scroll area 1 of window 1',
                'text area 1 of scroll area 1 of group 1 of window 1',
            )
            for selector in selectors:
                try:
                    ax(proc.pid, 'set value of ' + selector + ' to ' + json.dumps(AFTER))
                    break
                except AssertionError:
                    continue
            else:
                print("recipe_dialog_tree", ax(proc.pid, "get entire contents of window 1")[:3000], flush=True)
                raise AssertionError("recipe content editor not accessible")
            ax(proc.pid, 'click button "生成待批准计划" of window 1')
            database = workspace / "memory.sqlite3"
            draft = wait_for("TextEdit draft", lambda: row if (row := goal_row(database)) and row["status"] == "draft" else None,
                             seconds=35)
            assert document.read_text(encoding="utf-8") == BEFORE
            card = ax(proc.pid, 'get value of text area 1 of scroll area 1 of group 3 of window "Muse · GOSIM"')
            assert document.name in card and AFTER.strip() in card, card
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_held = False
            ax(proc.pid, 'click button "批准计划" of group 3 of window "Muse · GOSIM"')
            def completed():
                with sqlite3.connect(str(database), timeout=3) as db:
                    row = db.execute("SELECT result_json FROM muse_goal_runs WHERE status='completed' ORDER BY started_at DESC LIMIT 1").fetchone()
                return json.loads(row[0]) if row and row[0] else None
            result = wait_for("TextEdit saved Goal", completed, seconds=35)
            assert document.read_text(encoding="utf-8") == AFTER
            receipt = next(item for item in result["receipts"] if item["capability"] == "app.recipe")
            assert receipt["verification"]["focused_document_matches"] is True, receipt
            assert receipt["verification"]["ax_value_matches"] is True, receipt
            assert receipt["verification"]["disk_readback_matches"] is True, receipt
            output = {"status": "PASS_LOCAL", "helper_status": status,
                      "textedit_document": doc_state, "goal_id": draft["goal_id"],
                      "run_id": result["run_id"], "focused_document_matches": True,
                      "readback_matches": True,
                      "file_sha256": hashlib.sha256(document.read_bytes()).hexdigest()}
            (root / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
            print(json.dumps(output, ensure_ascii=False), flush=True)
        finally:
            if lock_held:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == "__main__":
    run()
