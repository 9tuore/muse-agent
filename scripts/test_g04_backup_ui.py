#!/usr/bin/env python3
"""Save a same-origin backup profile through the packaged native UI."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready


FIXTURE = r'''
import sys
from pathlib import Path
from muse_models import ModelGateway
gateway = ModelGateway(Path(sys.argv[1]))
settings = gateway.get_settings()
settings["profiles"]["high-default"].update({
    "endpoint": "https://api.example.test/v1/chat/completions", "model": "primary-test"})
settings["profiles"]["high-backup"] = {
    "protocol": "openai_compatible", "endpoint": "https://api.example.test/v1/backup",
    "model": "backup-test", "keychain_service": "", "keychain_account": ""}
settings["profiles"]["high-cross-origin"] = {
    "protocol": "openai_compatible", "endpoint": "https://other.example.test/v1/backup",
    "model": "cross-origin-test", "keychain_service": "", "keychain_account": ""}
gateway.update_settings(settings)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="gosim-g04-backup-") as temp:
        root = Path(temp)
        app = root / "GOSIM-Local-Agent.app"
        shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
        workspace = root / "workspace"
        workspace.mkdir()
        resources = app / "Contents/Resources"
        env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
                   GOSIM_LOCAL_INBOX="0", PYTHONPATH=str(resources))
        subprocess.run([str(resources / "python/bin/python3"), "-B", "-c", FIXTURE, str(workspace)],
                       env=env, check=True, capture_output=True, text=True, timeout=10)
        with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
            proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                    env=env, stdout=stdout, stderr=stderr)
            try:
                wait_for("Muse main window", lambda: window_ready(proc.pid))
                time.sleep(1)
                ax(proc.pid, 'click menu item "备用高阶模型" of menu 1 of menu bar item "Muse · GOSIM" of menu bar 1')
                ax(proc.pid, 'click pop up button 1 of window 1')
                options = ax(proc.pid, 'get name of menu items of menu 1 of pop up button 1 of window 1')
                assert "无备用模型" in options and "high-backup" in options, options
                assert "high-cross-origin" not in options, options
                ax(proc.pid, 'click menu item "high-backup · backup-test" of menu 1 of pop up button 1 of window 1')
                ax(proc.pid, 'click button "保存" of window 1')
                path = workspace / ".muse_model_settings.json"
                wait_for("backup profile saved", lambda: json.loads(path.read_text())["backup_high"] == "high-backup")
                print(json.dumps({"status": "PASS_LOCAL", "backup_high": "high-backup",
                                  "same_origin_only": True, "no_remote_call": True}, ensure_ascii=False))
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
