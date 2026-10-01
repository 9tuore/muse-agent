#!/usr/bin/env python3
"""Exercise the packaged native contact picker without contacting QQ Mail."""

import json
import os
import plistlib
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


SOURCE = Path(os.environ.get("MUSE_DIST_DIR", "dist")) / "GOSIM-Local-Agent.app"
AX = SOURCE / "Contents/Resources/muse_ax_helper"
BUNDLE = "org.gosim.local-agent.r17-contact-fixture"


def ax(command, title, selector=None, action=None):
    args = [str(AX), command, BUNDLE]
    if command == "snapshot":
        args.append(title)
    else:
        args.extend([json.dumps({"role": "AXButton", "name": selector,
                                 "window_title": title}), action, ""])
    result = subprocess.run(args, capture_output=True, text=True, timeout=10, check=True)
    return json.loads(result.stdout)


def wait_for(label, probe, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = probe()
        if value:
            return value
        time.sleep(0.25)
    raise AssertionError("timed out waiting for " + label)


def main():
    root = Path(tempfile.mkdtemp(prefix="muse-r17-contacts-ui-"))
    app = root / "Muse-Contacts-Test.app"
    workspace = root / "workspace"
    workspace.mkdir()
    shutil.copytree(SOURCE, app, symlinks=True)
    info = app / "Contents/Info.plist"
    with info.open("rb") as stream:
        plist = plistlib.load(stream)
    plist["CFBundleIdentifier"] = BUNDLE
    with info.open("wb") as stream:
        plistlib.dump(plist, stream)
    subprocess.run(["/usr/bin/codesign", "--force", "--deep", "--sign", "-", str(app)],
                   capture_output=True, check=True)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)],
                   capture_output=True, check=True)
    (workspace / ".qqmail_bridge_health.json").write_text(json.dumps({"status": "CONNECTED"}))
    (workspace / ".qqmail_contacts.json").write_text(json.dumps({
        "version": 1, "source": "qqmail_imap_recent_inbox_headers", "contacts": [
            {"contact_id": "fixture-alice", "name": "Alice", "address": "alice@example.com",
             "subject": "周末", "message_id_header": "<fixture@example.com>",
             "source_message_id": "qqmail:42"},
        ],
    }))
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_LOCAL_INBOX="0",
               GOSIM_SKIP_ONBOARDING="1")
    process = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")], env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_for("main window", lambda: any(item.get("name") == "邮箱往来联系人"
            for item in ax("snapshot", "Muse · GOSIM").get("elements", [])))
        opened = ax("act", "Muse · GOSIM", "邮箱往来联系人", "press")
        assert opened["status"] == "COMPLETED", opened
        wait_for("contact row", lambda: any(item.get("name") == "回复给 alice@example.com"
            for item in ax("snapshot", "QQ 邮箱 · 最近来信联系人").get("elements", [])))
        selected = ax("act", "QQ 邮箱 · 最近来信联系人", "回复给 alice@example.com", "press")
        assert selected["status"] == "COMPLETED", selected
        state = wait_for("reply session", lambda: (
            json.loads((workspace / ".agent_mail_reply_state.json").read_text())
            if (workspace / ".agent_mail_reply_state.json").exists() else None))
        assert state["active"]["origin"] == "contact"
        assert state["active"]["sender"] == "alice@example.com"
        assert state["active"]["state"] == "CHOICE"
        assert not (workspace / "outbox").exists()
        subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)],
                       capture_output=True, check=True)
        print(json.dumps({"status": "PASS_FIXTURE", "native_contact_clicked": True,
                          "reply_session_opened": True, "mail_sent": False,
                          "real_qq_contacts": "NOT_TESTED"}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        shutil.rmtree(root)


if __name__ == "__main__":
    main()
