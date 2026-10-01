#!/usr/bin/env python3
"""Drive observed Edge recipe through native review, Goal approval, and live readback."""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from test_muse_desktop_package import ax, goal_row, wait_for, window_ready


QUERY = "Python 3.13"


def goal_plan(database, goal_id):
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT spec_json,digest FROM muse_goal_revisions WHERE goal_id=? ORDER BY revision DESC LIMIT 1",
                         (goal_id,)).fetchone()
    return (json.loads(row[0]), row[1]) if row else None


def completed_run(database, goal_id):
    if not database.exists():
        return None
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT result_json FROM muse_goal_runs WHERE goal_id=? AND status='completed' "
                         "ORDER BY started_at DESC LIMIT 1", (goal_id,)).fetchone()
    return json.loads(row[0]) if row and row[0] else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cancel-at-preview", action="store_true")
    args = parser.parse_args()
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    app = root / "GOSIM-Local-Agent.app"
    shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
    workspace = root / "workspace"
    workspace.mkdir()
    database = workspace / "memory.sqlite3"
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1", GOSIM_LOCAL_INBOX="0")
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
            ax(proc.pid, 'click button "Edge 搜索目标" of group 2 of window "Muse · GOSIM"')
            wait_for("Edge query dialog", lambda: "观察搜索控件" in ax(proc.pid, "get name of buttons of window 1"))
            ax(proc.pid, 'set value of text field "Edge 公开搜索词" of window 1 to ' + json.dumps(QUERY))
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_held = False
            ax(proc.pid, 'click button "观察搜索控件" of window 1')
            wait_for("native recipe preview", lambda: "生成待批准计划" in ax(
                proc.pid, "get name of buttons of window 1"), seconds=35)
            preview = None
            for target in ('text area "Edge 搜索配方预览" of window 1',
                           'text area 1 of scroll area 1 of window 1'):
                try:
                    preview = ax(proc.pid, "get value of " + target)
                    break
                except AssertionError:
                    continue
            assert preview and QUERY in preview and "python.org" in preview and "Search" in preview, preview
            assert "配方摘要 SHA-256" in preview, preview
            assert not list(workspace.glob("notes/browser-recipe*.md"))
            if args.cancel_at_preview:
                ax(proc.pid, 'click button "取消" of window 1')
                time.sleep(1)
                with sqlite3.connect(str(database), timeout=3) as db:
                    assert db.execute("SELECT COUNT(*) FROM muse_goals").fetchone()[0] == 0
                assert not list(workspace.glob("notes/browser-recipe*.md"))
                output = {"status": "PASS_LOCAL", "native_preview_seen": True,
                          "cancelled_before_goal": True, "goal_count": 0,
                          "artifact_count": 0, "paid_provider_used": False}
                (root / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
                print(json.dumps(output, ensure_ascii=False), flush=True)
                return
            ax(proc.pid, 'click button "生成待批准计划" of window 1')
            draft = wait_for("native browser Goal draft", lambda: row if (row := goal_row(database)) and
                             row["status"] == "draft" else None, seconds=90)
            plan, digest = goal_plan(database, draft["goal_id"])
            browser = next(step for step in plan["steps"] if step["capability"] == "browser.research")
            recipe = browser["args"]
            assert recipe["query"] == QUERY and recipe["engine"] == "python.org"
            card = ax(proc.pid, 'get value of text area 1 of scroll area 1 of group 3 of window "Muse · GOSIM"')
            assert all(value in card for value in (QUERY, "python.org", recipe["window_title"],
                                                    recipe["recipe_digest"], digest, "已观察控件")), card
            assert not list(workspace.glob("notes/browser-recipe*.md"))
            ax(proc.pid, 'click button "批准计划" of group 3 of window "Muse · GOSIM"')
            result = wait_for("native approved Edge Goal run", lambda: completed_run(database, draft["goal_id"]),
                              seconds=160)
            browser_receipt = next(item for item in result["receipts"] if item["capability"] == "browser.research")
            write_receipt = next(item for item in result["receipts"] if item["capability"] == "workspace.write_artifact")
            verification = browser_receipt["verification"]
            assert verification["learned_search_recipe"] is True
            assert verification["clicked_pages"] == 3 and verification["readback_pages"] == 3
            assert write_receipt["verification"]["readback_matches"] is True
            artifact = workspace / write_receipt["output"]["relative_path"]
            assert artifact.is_file()
            sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
            assert sha == write_receipt["verification"]["sha256"]
            output = {"status": "PASS_LIVE", "goal_id": draft["goal_id"], "run_id": result["run_id"],
                      "plan_digest": digest, "recipe_digest": recipe["recipe_digest"],
                      "native_card_reviewed": True, "native_approval_clicked": True,
                      "learned_search_recipe": True, "clicked_pages": 3, "readback_pages": 3,
                      "artifact_relative_path": write_receipt["output"]["relative_path"],
                      "artifact_sha256": sha, "paid_provider_used": False}
            (root / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
            print(json.dumps(output, ensure_ascii=False), flush=True)
        finally:
            if lock_held:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=5)
            time.sleep(1)
            subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)


if __name__ == "__main__":
    main()
