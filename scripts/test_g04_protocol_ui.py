#!/usr/bin/env python3
"""Check native GPT Responses and DeepSeek protocol save/readback."""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


def protocol(workspace):
    path = workspace / ".muse_model_settings.json"
    if not path.exists():
        return None
    settings = json.loads(path.read_text())
    return settings["profiles"][settings["active_high"]]["protocol"]


def open_settings(pid):
    wait_for("model settings loaded", lambda: "模式：" in ax(pid,
        'get value of static texts of group 3 of window "Muse · GOSIM"'), seconds=15)
    ax(pid, 'click menu item "模型与预算设置" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
    wait_for("model settings dialog", lambda: "保存" in ax(pid, "get name of buttons of window 1"))


def select_protocol(pid, title):
    ax(pid, 'click pop up button 2 of window 1')
    choices = ax(pid, 'get name of menu items of menu 1 of pop up button 2 of window 1')
    assert title in choices, choices
    ax(pid, 'click menu item ' + json.dumps(title, ensure_ascii=False) + ' of menu 1 of pop up button 2 of window 1')
    ax(pid, 'click button "保存" of window 1')


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
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
               GOSIM_LOCAL_INBOX="0")
    with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
        proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                env=env, stdout=stdout, stderr=stderr)
        try:
            wait_for("Muse window", lambda: window_ready(proc.pid))
            open_settings(proc.pid)
            select_protocol(proc.pid, "OpenAI Responses (GPT)")
            try:
                wait_for("GPT protocol saved", lambda: protocol(workspace) == "openai_responses", seconds=5)
            except AssertionError:
                print("task_card", ax(proc.pid,
                    'get value of text area 1 of scroll area 1 of group 3 of window "Muse · GOSIM"'))
                print("settings_file", (workspace / ".muse_model_settings.json").exists())
                ax(proc.pid, 'click menu item "技术详情" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
                for group in range(1, 4):
                    query = f'get value of text area 1 of scroll area 1 of group {group} of window "Muse · 技术详情"'
                    try:
                        print("technical_log", ax(proc.pid, query)[-1600:])
                    except AssertionError:
                        continue
                raise
            open_settings(proc.pid)
            assert "OpenAI Responses (GPT)" in ax(proc.pid, 'get value of pop up button 2 of window 1')
            select_protocol(proc.pid, "DeepSeek Chat")
            wait_for("DeepSeek protocol saved", lambda: protocol(workspace) == "deepseek_chat")
            open_settings(proc.pid)
            assert "DeepSeek Chat" in ax(proc.pid, 'get value of pop up button 2 of window 1')
            ax(proc.pid, 'click button "取消" of window 1')
            proc.terminate()
            proc.wait(timeout=5)
            proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                    env=env, stdout=stdout, stderr=stderr)
            wait_for("restarted Muse window", lambda: window_ready(proc.pid))
            open_settings(proc.pid)
            assert "DeepSeek Chat" in ax(proc.pid, 'get value of pop up button 2 of window 1')
            ax(proc.pid, 'click button "取消" of window 1')
            output = {"status": "PASS_LOCAL", "gpt_responses_roundtrip": True,
                      "deepseek_chat_roundtrip": True, "restart_roundtrip": True,
                      "remote_call_made": False}
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
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)


if __name__ == "__main__":
    main()
