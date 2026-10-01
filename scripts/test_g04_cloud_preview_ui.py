#!/usr/bin/env python3
"""Exercise packaged native cloud-preview Cancel/Confirm without an API call."""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


SETUP = r'''
import sys
from pathlib import Path
from muse_models import ModelGateway
gateway = ModelGateway(Path(sys.argv[1]))
settings = gateway.get_settings()
settings["mode"] = "high"
settings["profiles"]["high-default"].update({
    "endpoint": "https://api.example.test/v1/chat/completions", "model": "preview-fixture"})
settings["cloud_data_allowed"] = False
gateway.update_settings(settings)
'''
MESSAGE = "合成云端预览测试：请只回答收到。"


def count_chat(workspace):
    path = workspace / "memory.sqlite3"
    if not path.exists():
        return 0
    with sqlite3.connect(str(path), timeout=3) as db:
        return db.execute("SELECT COUNT(*) FROM memories WHERE kind='chat_user'").fetchone()[0]


def preview_visible(pid):
    try:
        names = ax(pid, "get name of buttons of window 1")
        return "确认发送" in names and "取消" in names
    except AssertionError:
        return False


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
               GOSIM_LOCAL_INBOX="0", PYTHONPATH=str(resources))
    subprocess.run([str(resources / "python/bin/python3"), "-B", "-c", SETUP, str(workspace)],
                   env=env, capture_output=True, text=True, timeout=10, check=True)
    with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
        proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                env=env, stdout=stdout, stderr=stderr)
        try:
            wait_for("Muse window", lambda: window_ready(proc.pid))
            input_ref = 'text field "即时对话输入" of group 2 of window "Muse · GOSIM"'
            send_ref = 'button "发送" of group 2 of window "Muse · GOSIM"'
            ax(proc.pid, 'set value of ' + input_ref + ' to ' + json.dumps(MESSAGE, ensure_ascii=False))
            ax(proc.pid, 'click ' + send_ref)
            wait_for("cloud preview dialog", lambda: preview_visible(proc.pid), seconds=15)
            preview = ax(proc.pid, 'get value of text area "完整云端请求预览" of scroll area 1 of window 1')
            assert "api.example.test" in preview and MESSAGE in preview, preview
            ax(proc.pid, 'click button "取消" of window 1')
            wait_for("restored input", lambda: ax(proc.pid, 'get value of ' + input_ref) == MESSAGE)
            assert count_chat(workspace) == 0, "Cancel persisted chat"
            assert not (workspace / ".muse_model_usage.json").exists(), "Cancel reserved usage"

            ax(proc.pid, 'click ' + send_ref)
            wait_for("second cloud preview", lambda: preview_visible(proc.pid), seconds=15)
            ax(proc.pid, 'click button "确认发送" of window 1')
            wait_for("confirmed chat recorded", lambda: count_chat(workspace) == 1, seconds=15)
            assert not (workspace / ".muse_model_usage.json").exists(), "fixture made a remote reservation"
            output = {"status": "PASS_FIXTURE", "preview_contains_endpoint_and_exact_message": True,
                      "cancel_did_not_send": True, "confirm_sent_bound_message_to_worker": True,
                      "remote_call_made": False, "cloud_data_allowed": False}
            (root / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
            print(json.dumps(output, ensure_ascii=False))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
            time.sleep(1)


if __name__ == "__main__":
    main()
