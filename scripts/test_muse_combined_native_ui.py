#!/usr/bin/env python3
"""Check public research and a selected-folder update through a copied Muse UI."""

import argparse
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path

from test_muse_desktop_package import ax, capture_screen, goal_row, wait_for, window_ready


GOAL = ("持续关注 https://www.python.org/ 的公开资料变化，整理一份中文 Python 资料提纲并注明来源。"
        "当我选定的合成资料目录有文件变化时，更新同一个提纲。")


def watch_ref(workspace):
    path = workspace / ".muse-watch-registry.sqlite3"
    if not path.exists():
        return None
    with sqlite3.connect(str(path)) as db:
        row = db.execute("SELECT resource_ref FROM watched LIMIT 1").fetchone()
    return row[0] if row else None


def runs(database):
    if not database.exists():
        return []
    with sqlite3.connect(str(database)) as db:
        rows = db.execute("SELECT result_json FROM muse_goal_runs WHERE status='completed' ORDER BY started_at").fetchall()
    return [json.loads(row[0]) for row in rows if row[0]]


def artifact(workspace, result):
    receipt = next(item for item in result["receipts"] if item["capability"] == "workspace.write_artifact")
    path = workspace / receipt["output"]["relative_path"]
    assert path.is_file() and receipt["verification"]["readback_matches"] is True
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.app.resolve(strict=True)
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    copied = root / "Muse-Combined-UI.app"
    workspace = root / "workspace"
    selected = root / "selected"
    if not str(selected).isascii():
        selected = Path(tempfile.mkdtemp(prefix="muse-g03-selected-", dir="/tmp"))
    shutil.copytree(source, copied)
    workspace.mkdir()
    if not selected.exists():
        selected.mkdir()
    spec = importlib.util.spec_from_file_location("packaged_muse_models", copied / "Contents/Resources/muse_models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    gateway = module.ModelGateway(workspace)
    settings = gateway.get_settings()
    settings["timeout_seconds"] = 60
    gateway.update_settings(settings)
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_DEV_UI="0", GOSIM_LOCAL_INBOX="0")
    process = None
    try:
        with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
            process = subprocess.Popen([str(copied / "Contents/MacOS/GOSIM-Local-Agent")],
                                       env=env, stdout=stdout, stderr=stderr)
            wait_for("Muse window", lambda: window_ready(process.pid))
            ax(process.pid, 'click button "选目录" of group 3 of window "Muse · GOSIM"')
            time.sleep(0.7)
            ax(process.pid, 'keystroke "g" using {command down, shift down}')
            time.sleep(0.4)
            ax(process.pid, "keystroke " + json.dumps(str(selected), ensure_ascii=False))
            ax(process.pid, "key code 36")
            time.sleep(0.4)
            ax(process.pid, "key code 36")
            time.sleep(0.6)
            ax(process.pid, 'click button "授权监控此目录" of window 1')
            selected_ref = wait_for("native folder authorization", lambda: watch_ref(workspace))
            time.sleep(0.7)
            ax(process.pid, 'click pop up button 1 of group 5 of window "Muse · GOSIM"')
            assert selected.name in ax(process.pid,
                'get name of menu items of menu 1 of pop up button 1 of group 5 of window "Muse · GOSIM"')
            ax(process.pid, 'click menu item 2 of menu 1 of pop up button 1 of group 5 of window "Muse · GOSIM"')
            ax(process.pid, 'set value of text field "即时对话输入" of group 5 of window "Muse · GOSIM" to ' +
               json.dumps(GOAL, ensure_ascii=False))
            ax(process.pid, 'click button "设为长期目标" of group 5 of window "Muse · GOSIM"')
            database = workspace / "memory.sqlite3"
            draft = wait_for("research draft", lambda: row if (row := goal_row(database)) and row["status"] == "draft" else None,
                             seconds=150)
            with sqlite3.connect(str(database)) as db:
                plan = json.loads(db.execute("SELECT spec_json FROM muse_goal_revisions WHERE goal_id=?",
                                             (draft["goal_id"],)).fetchone()[0])
            assert {item["kind"] for item in plan["triggers"]} == {"interval", "event"}
            assert selected_ref in plan["permissions"]["resource_refs"]
            assert any(step["capability"] == "web.read" for step in plan["steps"])
            assert not list(workspace.rglob("*.md")), "artifact before native approval"
            capture_screen(root / "draft.png")
            ax(process.pid, 'click button "批准计划" of group 6 of window "Muse · GOSIM"')
            first = wait_for("first autonomous research run", lambda: values[0] if (values := runs(database)) else None,
                             seconds=190)
            first_path = artifact(workspace, first)
            assert "https://www.python.org/" in first_path.read_text(encoding="utf-8")
            capture_screen(root / "first-result.png")
            time.sleep(3)
            (selected / "synthetic-change.md").write_text("合成验收：新增一项资料。\n", encoding="utf-8")
            second = wait_for("same goal file event update", lambda: next((item for item in runs(database)
                if item["goal_id"] == first["goal_id"] and str(item.get("event_id") or "").startswith("file:")), None),
                seconds=190)
            assert second["goal_id"] == first["goal_id"] and second["event_id"].startswith("file:")
            second_path = artifact(workspace, second)
            assert second_path != first_path and "synthetic-change.md" in second_path.read_text(encoding="utf-8")
            wait_for("second result visible in chat", lambda: second_path.name in ax(process.pid,
                'get value of text area 1 of group 5 of window "Muse · GOSIM"'), seconds=20)
            capture_screen(root / "second-result.png")
            print(json.dumps({"status": "PASS", "goal_id": first["goal_id"], "first_run_id": first["run_id"],
                              "second_run_id": second["run_id"], "second_event_id": second["event_id"],
                              "watch_ref": selected_ref, "first_artifact": str(first_path),
                              "second_artifact": str(second_path), "selected_folder": str(selected),
                              "second_update_visible_in_chat": True,
                              "output_dir": str(root)}, ensure_ascii=False))
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
