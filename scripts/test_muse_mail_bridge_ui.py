#!/usr/bin/env python3
"""Check packaged QQ connection controls without contacting QQ Mail."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


FAKE_BRIDGE = '''#!/usr/bin/env python3
import argparse, json, os, sys, time
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("--workspace", required=True)
p.add_argument("--address", required=True)
p.add_argument("--auth-code-stdin", action="store_true")
a = p.parse_args()
secret = sys.stdin.buffer.readline(258)
if not a.auth_code_stdin or not secret.endswith(b"\\n") or len(secret) > 257:
    raise SystemExit(2)
Path(a.workspace, "fake_bridge_observation.json").write_text(json.dumps({
    "address": a.address, "received_code": bool(secret[:-1]),
    "code_in_argv": any("fixture-code" in part for part in sys.argv),
    "code_in_env": any("fixture-code" in value for value in os.environ.values()),
    "pid": os.getpid(),
}), encoding="utf-8")
while True:
    time.sleep(1)
'''


def main():
    source = Path(os.environ.get("MUSE_DIST_DIR", "dist")) / "GOSIM-Local-Agent.app"
    source = source.resolve()
    root = Path(tempfile.mkdtemp(prefix="muse-mail-ui-"))
    copied = root / "Muse-Mail-Test.app"
    workspace = root / "workspace"
    shutil.copytree(source, copied, symlinks=True)
    workspace.mkdir()
    (copied / "Contents/Resources/qqmail_imap_bridge.py").write_text(FAKE_BRIDGE, encoding="utf-8")
    subprocess.run(["/usr/bin/codesign", "--force", "--deep", "--sign", "-", str(copied)],
                   check=True, capture_output=True)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(copied)],
                   check=True, capture_output=True)
    app = None
    external = None
    try:
        env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_DEV_UI="0",
                   GOSIM_LOCAL_INBOX="0", GOSIM_SKIP_ONBOARDING="1")
        app = subprocess.Popen([str(copied / "Contents/MacOS/GOSIM-Local-Agent")],
                               env=env, stdout=(root / "app.stdout").open("w"),
                               stderr=(root / "app.stderr").open("w"))
        wait_for("Muse window", lambda: window_ready(app.pid))
        external = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(90)",
                                     "qqmail_imap_bridge.py", "--workspace", str(workspace)])
        ax(app.pid, 'click menu item "连接或断开 QQ 邮箱" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
        alert_text = wait_for("existing-bridge alert", lambda: text if
            "此工作区已有 QQ 邮箱连接" in (text := ax(app.pid, 'get name of every static text of window 1'))
            else None)
        assert "此工作区已有 QQ 邮箱连接" in alert_text, alert_text
        assert not (workspace / "fake_bridge_observation.json").exists()
        ax(app.pid, 'click button "知道了" of window 1')
        external.terminate()
        external.wait(timeout=5)
        external = None

        ax(app.pid, 'click menu item "连接或断开 QQ 邮箱" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
        wait_for("QQ connection form", lambda: "连接" in ax(app.pid, 'get name of buttons of window 1'))
        ax(app.pid, 'set value of text field 1 of window 1 to "fixture@qq.com"')
        ax(app.pid, 'set value of text field 2 of window 1 to "fixture-code"')
        ax(app.pid, 'click button "连接" of window 1')
        observation_path = workspace / "fake_bridge_observation.json"
        observation = wait_for("private bridge stdin receipt", lambda: (
            json.loads(observation_path.read_text(encoding="utf-8")) if observation_path.exists() else None))
        assert observation["address"] == "fixture@qq.com" and observation["received_code"]
        assert not observation["code_in_argv"] and not observation["code_in_env"]
        bridge_pid = observation["pid"]
        assert subprocess.run(["/bin/ps", "-p", str(bridge_pid)], capture_output=True).returncode == 0
        ax(app.pid, 'set frontmost to true')
        ax(app.pid, 'keystroke "q" using command down')
        wait_for("app exits through native Quit", lambda: app.poll() is not None)
        wait_for("owned bridge exits with app", lambda: subprocess.run(
            ["/bin/ps", "-p", str(bridge_pid)], capture_output=True).returncode != 0)
        print(json.dumps({"status": "PASS", "workspace": str(workspace),
                          "conflicting_bridge_blocked": True, "private_bridge_stdin": True,
                          "credential_absent_from_argv_env": True, "owned_bridge_cleanup": True,
                          "real_qq_login": "NOT_TESTED"}, ensure_ascii=False))
    finally:
        if external and external.poll() is None:
            external.terminate()
            external.wait(timeout=5)
        if app and app.poll() is None:
            app.terminate()
            app.wait(timeout=5)


if __name__ == "__main__":
    main()
