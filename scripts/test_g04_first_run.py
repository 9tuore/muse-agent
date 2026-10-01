#!/usr/bin/env python3
"""Check the real native first-run choices in an isolated copied app."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from test_muse_desktop_package import ax

MODEL_FILE = "Qwen3-0.6B-Q8_0.gguf"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--choice", choices=("later", "existing", "high", "reuse", "failure"), default="later")
    parser.add_argument("--model-source", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="gosim-g04-first-run-") as temp:
        root = Path(temp)
        app = root / "GOSIM-Local-Agent.app"
        shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
        subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
        workspace = root / "workspace"
        workspace.mkdir()
        if args.choice == "reuse":
            assert args.model_source and args.model_source.is_file()
            models = root / "models"
            models.mkdir()
            os.link(args.model_source, models / MODEL_FILE)
        if args.choice == "failure":
            (root / "models").write_text("synthetic blocked model directory\n")
        home = root / "home"
        home.mkdir()
        env = dict(os.environ, HOME=str(home), AGENT_WORKSPACE=str(workspace), GOSIM_LOCAL_INBOX="0")
        env.pop("GOSIM_SKIP_ONBOARDING", None)
        env.pop("GOSIM_BACKGROUND_TEST", None)
        listener_before = subprocess.run(["/usr/sbin/lsof", "-tiTCP:8080", "-sTCP:LISTEN"],
                                         capture_output=True, text=True, check=False).stdout.strip()
        with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
            proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                    env=env, stdout=stdout, stderr=stderr)
            try:
                names = ""
                for _ in range(30):
                    time.sleep(0.5)
                    try:
                        names = ax(proc.pid, "get name of buttons of window 1")
                    except AssertionError:
                        continue
                    if "下载默认模型" in names:
                        break
                expected = ("下载默认模型", "使用已有本地服务", "仅高阶模型", "稍后设置")
                assert all(label in names for label in expected), names
                intro = ax(proc.pid, "get value of static texts of window 1")
                assert "huggingface.co/Qwen/Qwen3-0.6B-GGUF" in intro and "Apache-2.0" in intro, intro
                choice_label = {"later": "稍后设置", "existing": "使用已有本地服务",
                                "high": "仅高阶模型", "reuse": "下载默认模型",
                                "failure": "下载默认模型"}[args.choice]
                ax(proc.pid, f'click button "{choice_label}" of window 1')
                guide_buttons = None
                if args.choice == "later":
                    ax(proc.pid, 'click menu item "系统权限自检" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
                    for _ in range(20):
                        time.sleep(0.25)
                        guide_buttons = ax(proc.pid, "get name of buttons of window 1")
                        if "打开系统设置" in guide_buttons:
                            break
                    assert "打开系统设置" in guide_buttons and "稍后" in guide_buttons, guide_buttons
                    ax(proc.pid, 'click button "稍后" of window 1')
                if args.choice == "reuse":
                    for _ in range(40):
                        time.sleep(0.25)
                        if proc.poll() is not None:
                            print("reuse_exit_code", proc.returncode, flush=True)
                            print("reuse_stderr", (root / "app.stderr").read_text(errors="replace")[-4000:], flush=True)
                            raise AssertionError("app exited during verified model reuse")
                        try:
                            result_text = ax(proc.pid, "get value of static texts of window 1")
                            buttons = ax(proc.pid, "get name of buttons of window 1")
                        except AssertionError:
                            continue
                        if "本地模型已就绪" in result_text and "知道了" in buttons:
                            break
                    else:
                        print("reuse_windows", ax(proc.pid, "get name of windows"), flush=True)
                        print("reuse_last_text", result_text, flush=True)
                        print("reuse_last_buttons", buttons, flush=True)
                        print("reuse_stderr", (root / "app.stderr").read_text(errors="replace")[-1000:], flush=True)
                        raise AssertionError("verified local model result not shown")
                    assert "默认模型已验证" in result_text, result_text
                    ax(proc.pid, 'click button "知道了" of window 1')
                if args.choice == "failure":
                    for _ in range(20):
                        time.sleep(0.25)
                        result_text = ax(proc.pid, "get value of static texts of window 1")
                        buttons = ax(proc.pid, "get name of buttons of window 1")
                        if "模型尚未就绪" in result_text and "重试下载" in buttons and "稍后" in buttons:
                            break
                    else:
                        raise AssertionError("retry/later failure dialog missing")
                    assert "无法创建模型目录" in result_text, result_text
                    ax(proc.pid, 'click button "稍后" of window 1')
                saved = root / "setup.json"
                if args.choice not in {"later", "failure"}:
                    for _ in range(20):
                        if saved.exists():
                            break
                        time.sleep(0.25)
                mode = json.loads(saved.read_text())["mode"] if saved.exists() else None
                assert mode == {"later": None, "existing": "local-external", "high": "high-only",
                                "reuse": "local-managed", "failure": None}[args.choice], mode
                if args.choice == "high":
                    model_settings = workspace / ".muse_model_settings.json"
                    for _ in range(20):
                        if model_settings.exists():
                            break
                        time.sleep(0.25)
                    assert json.loads(model_settings.read_text())["mode"] == "high"
                model_path = root / "models" / MODEL_FILE
                if args.choice == "reuse":
                    assert model_path.stat().st_ino == args.model_source.stat().st_ino
                elif args.choice != "failure":
                    assert not model_path.exists()
                listener_after = subprocess.run(["/usr/sbin/lsof", "-tiTCP:8080", "-sTCP:LISTEN"],
                                                capture_output=True, text=True, check=False).stdout.strip()
                assert listener_after == listener_before, (listener_before, listener_after)
                if args.choice == "reuse":
                    time.sleep(3)
                    assert proc.poll() is None, "app exited after hash reuse"
                print(json.dumps({"result": "PASS_LOCAL", "first_run_buttons": names,
                                  "choice": args.choice, "saved_mode": mode,
                                  "permission_guide_buttons": guide_buttons,
                                  "official_source_and_license_visible": True,
                                  "model_sha_reuse": args.choice == "reuse",
                                  "failure_retry_and_later_visible": args.choice == "failure",
                                  "app_alive_after_hash_reuse": args.choice == "reuse" and proc.poll() is None,
                                  "no_new_port_8080_listener": True}, ensure_ascii=False))
            finally:
                if proc.poll() is None:
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
