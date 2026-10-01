#!/usr/bin/env python3
"""Check native memory and proactivity switches serialize as JSON booleans."""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


def open_menu(pid, item):
    ax(pid, 'click menu item ' + json.dumps(item, ensure_ascii=False) +
       ' of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
    wait_for(item + " dialog", lambda: "保存" in ax(pid, "get name of buttons of window 1"))


def recording(database):
    if not database.exists():
        return None
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT recording FROM muse_memory_settings WHERE scope='personal' AND account_scope='local'").fetchone()
    return row[0] if row else None


def launch(app, workspace, root, name):
    stdout = (root / f"app-{name}.stdout").open("w")
    stderr = (root / f"app-{name}.stderr").open("w")
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1", GOSIM_LOCAL_INBOX="0")
    proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                            env=env, stdout=stdout, stderr=stderr)
    wait_for("Muse window", lambda: window_ready(proc.pid))
    time.sleep(1)
    return proc, stdout, stderr


def stop(proc, stdout, stderr):
    if proc.poll() is None:
        proc.terminate()
    proc.wait(timeout=5)
    stdout.close()
    stderr.close()


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
    database = workspace / "memory.sqlite3"
    processes = []
    try:
        proc, stdout, stderr = launch(app, workspace, root, "first")
        processes.append((proc, stdout, stderr))
        open_menu(proc.pid, "记忆记录设置")
        ax(proc.pid, 'click checkbox "在当前范围记录新记忆" of window 1')
        ax(proc.pid, 'click button "保存" of window 1')
        wait_for("memory recording disabled", lambda: recording(database) == 0)
        open_menu(proc.pid, "主动通知设置")
        ax(proc.pid, 'click checkbox "允许长期目标主动通知" of window 1')
        ax(proc.pid, 'click button "保存" of window 1')
        proactivity = workspace / ".muse_proactivity.json"
        wait_for("proactivity disabled", lambda: proactivity.exists() and
                 json.loads(proactivity.read_text())["enabled"] is False)
        settings = json.loads(proactivity.read_text())
        assert all(type(settings[key]) is bool for key in
                   ("enabled", "notify_on_completion", "notify_on_need_decision"))
        stop(proc, stdout, stderr)
        processes.clear()
        proc, stdout, stderr = launch(app, workspace, root, "restart")
        processes.append((proc, stdout, stderr))
        open_menu(proc.pid, "记忆记录设置")
        memory_value = ax(proc.pid, 'get value of checkbox "在当前范围记录新记忆" of window 1')
        assert memory_value in {"0", "false"}, memory_value
        ax(proc.pid, 'click button "取消" of window 1')
        open_menu(proc.pid, "主动通知设置")
        proactive_value = ax(proc.pid, 'get value of checkbox "允许长期目标主动通知" of window 1')
        assert proactive_value in {"0", "false"}, proactive_value
        ax(proc.pid, 'click button "取消" of window 1')
        result = {"status": "PASS_LOCAL", "memory_recording_disabled": True,
                  "proactivity_enabled": False, "restart_readback": True,
                  "proactivity_values_are_booleans": True}
        (root / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False))
    finally:
        for item in processes:
            stop(*item)
        subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)


if __name__ == "__main__":
    main()
