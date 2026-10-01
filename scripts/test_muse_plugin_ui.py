#!/usr/bin/env python3
"""Exercise built-in plugin consent, sample run, and revocation through Muse UI."""

import argparse
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

from test_muse_desktop_package import ax, capture_screen, wait_for, window_ready


MENU = 'click menu item "插件与权限" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1'


def approvals(workspace):
    path = workspace / ".muse-plugin-registry.sqlite3"
    if not path.exists():
        return []
    with sqlite3.connect(str(path)) as db:
        return db.execute("SELECT plugin_id,version,digest,enabled FROM approvals").fetchall()


def alert_buttons(pid):
    try:
        return ax(pid, "get name of buttons of window 1")
    except AssertionError:
        return ""


def chat(pid):
    return ax(pid, 'get value of text area 1 of group 5 of window "Muse · GOSIM"')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.app.resolve(strict=True)
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    copied = root / "Muse-Plugin-UI.app"
    workspace = root / "workspace"
    shutil.copytree(source, copied)
    workspace.mkdir()
    process = None
    try:
        with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
            process = subprocess.Popen([str(copied / "Contents/MacOS/GOSIM-Local-Agent")],
                                       env=dict(os.environ, AGENT_WORKSPACE=str(workspace),
                                                GOSIM_DEV_UI="0", GOSIM_LOCAL_INBOX="0"),
                                       stdout=stdout, stderr=stderr)
            wait_for("Muse window", lambda: window_ready(process.pid))
            ax(process.pid, MENU)
            wait_for("disabled plugin dialog", lambda: "启用并授权" in alert_buttons(process.pid))
            details = ax(process.pid, "get value of static texts of window 1")
            for expected in ("文本字符与行数", "1.0.0", "未启用", "text.stats", "文件权限：无", "网络：无"):
                assert expected in details, (expected, details)
            assert approvals(workspace) == [], "plugin enabled before native approval"
            capture_screen(root / "plugin-before-approval.png")
            ax(process.pid, 'click button "启用并授权" of window 1')
            approved = wait_for("native plugin approval", lambda: rows if (rows := approvals(workspace)) else None)
            assert len(approved) == 1 and approved[0][0] == "builtin.text_stats" and approved[0][3] == 1
            ax(process.pid, MENU)
            wait_for("enabled plugin dialog", lambda: "运行合成示例" in alert_buttons(process.pid))
            assert "已启用" in ax(process.pid, "get value of static texts of window 1")
            capture_screen(root / "plugin-enabled.png")
            ax(process.pid, 'click button "运行合成示例" of window 1')
            wait_for("synthetic plugin result in native chat", lambda: "5 个字符，2 行" in chat(process.pid))
            capture_screen(root / "plugin-example-result.png")
            ax(process.pid, MENU)
            wait_for("revoke plugin dialog", lambda: "禁用" in alert_buttons(process.pid))
            ax(process.pid, 'click button "禁用" of window 1')
            wait_for("native plugin revocation", lambda: not approvals(workspace))
            ax(process.pid, MENU)
            wait_for("disabled after revocation", lambda: "启用并授权" in alert_buttons(process.pid))
            assert "未启用" in ax(process.pid, "get value of static texts of window 1")
            capture_screen(root / "plugin-disabled-again.png")
            ax(process.pid, 'click button "关闭" of window 1')
            print({"status": "PASS", "workspace": str(workspace), "plugin_id": "builtin.text_stats",
                   "native_approval": True, "synthetic_run_visible": True, "native_revocation": True,
                   "output_dir": str(root)})
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
