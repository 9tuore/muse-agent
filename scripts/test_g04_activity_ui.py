#!/usr/bin/env python3
"""Exercise opt-in native Activity against a copied, integrated package."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    args = parser.parse_args()
    previous_app = subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", "-e",
        'ObjC.import("AppKit"); ObjC.unwrap($.NSWorkspace.sharedWorkspace.frontmostApplication.bundleIdentifier)'],
        capture_output=True, text=True, timeout=5, check=False).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="gosim-g04-activity-") as temp:
        root = Path(temp)
        app = root / "GOSIM-Local-Agent.app"
        shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
        subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
        workspace = root / "workspace"
        workspace.mkdir()
        env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
                   GOSIM_LOCAL_INBOX="0", GOSIM_DEV_UI="0")
        with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
            proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                    env=env, stdout=stdout, stderr=stderr)
            try:
                wait_for("Muse main window", lambda: window_ready(proc.pid))
                ax(proc.pid, 'click button "活动" of group 1 of window "Muse · GOSIM"')
                wait_for("Activity window", lambda: ax(proc.pid, 'get name of window "Muse · 活动"') == "Muse · 活动")
                buttons = ax(proc.pid, 'get name of buttons of window "Muse · 活动"')
                assert "开启观察" in buttons and "刷新" in buttons, buttons
                wait_for("Activity status", lambda: ax(proc.pid,
                    'get enabled of button "开启观察" of window "Muse · 活动"') == "true")
                time.sleep(1)
                ax(proc.pid, 'click checkbox "TextEdit" of window "Muse · 活动"')
                ax(proc.pid, 'click button "开启观察" of window "Muse · 活动"')
                try:
                    wait_for("Activity running", lambda: "正在观察所选应用的前台切换" in ax(
                        proc.pid, 'get value of static texts of window "Muse · 活动"'))
                except AssertionError:
                    for query in ('get name of buttons of window "Muse · 活动"',
                                  'get value of static texts of window "Muse · 活动"',
                                  'get value of checkbox "TextEdit" of window "Muse · 活动"'):
                        try:
                            print(query, ax(proc.pid, query))
                        except AssertionError as exc:
                            print(query, str(exc))
                    print("app.stderr", (root / "app.stderr").read_text(errors="replace")[-1200:])
                    raise
                subprocess.run(["/usr/bin/open", "-a", "TextEdit"], check=True, timeout=10)
                def observed():
                    try:
                        value = ax(proc.pid, 'get value of text area 1 of scroll area 1 of window "Muse · 活动"')
                        return value if "TextEdit" in value and "NSWorkspace" in value else None
                    except AssertionError:
                        return None
                event = wait_for("TextEdit frontmost activity", observed, seconds=12)
                names = ax(proc.pid, 'get name of buttons of window "Muse · 活动"')
                stop_name = "停止观察" if "停止观察" in names else "开启观察"
                ax(proc.pid, f'click button "{stop_name}" of window "Muse · 活动"')
                wait_for("Activity disabled", lambda: "已关闭" in ax(
                    proc.pid, 'get value of static texts of window "Muse · 活动"'))
                print(json.dumps({"status": "PASS_LOCAL", "source": "NSWorkspace",
                                  "observed_textedit": True, "opt_in_and_stop": True,
                                  "event_excerpt": event[:160]}, ensure_ascii=False))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
                time.sleep(1)
                if previous_app:
                    subprocess.run(["/usr/bin/open", "-b", previous_app], timeout=5, check=False)
        subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)


if __name__ == "__main__":
    main()
