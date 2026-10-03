"""LOCAL visible card-host probe of new-mail actions; no external mail is sent."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from remote import Remote


def run_size(args, size, port):
    work = args.output / size
    shutil.copytree(args.bundle, work / "bundle")
    jail = work / "state" / "muse-goals"
    jail.mkdir(parents=True)
    draft = {"account": "fixture", "to": "recipient@example.com", "subject": "中文草稿布局检查",
             "body": "合成正文，仅核对发送入口与滚动，不进行任何真实发送。", "status": "DRAFT",
             "preview": "", "attempt": "", "request_id": "", "accepted_at": 0,
             "verified_at": 0, "verified_id": "", "link_goal_id": "", "link_event_id": "", "link_run_id": ""}
    path = jail / "mail-draft.json"
    path.write_text(json.dumps(draft, ensure_ascii=False))
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    remote = Remote(port)
    with (work / "card-host.log").open("w") as log:
        process = subprocess.Popen([str(args.card_host), "--bundle", str(work / "bundle"),
                                    "--app-data", str(work / "state"), "--allow-unsigned",
                                    "--stamp", "--size", size],
                                   env=dict(os.environ, MAKEPAD_REMOTE=str(port)), stdout=log, stderr=log)
        try:
            for _ in range(100):
                try:
                    remote.find("page_title")
                    break
                except (OSError, AssertionError):
                    if process.poll() is not None:
                        raise RuntimeError("card-host exited; inspect the isolated log")
                    time.sleep(0.2)
            remote.click("邮箱")
            remote.click("继续编辑草稿")
            button = remote.wait_for("发送邮件")
            window = json.loads(remote.request("/s"))["w"][0]["sz"]
            x, y, width, height = button["r"]
            assert width > 40 and height >= 24 and x >= 0 and y >= 0
            assert x + width <= window[0] and y + height <= window[1], (button, window)
            remote.shot(work / "compose-top.png")
            assert any(w.get("t") == "请先选择发送账号。" for w in remote.widgets())
            remote.click("发送邮件")  # disabled without an authorized account
            assert hashlib.sha256(path.read_bytes()).hexdigest() == before
            scroll = remote.find("mail_form_scroll")["r"]
            assert scroll[2] > 100 and scroll[3] > 100, scroll
            for _ in range(4):
                remote.scroll(int(scroll[0] + scroll[2] / 2), int(scroll[1] + scroll[3] / 2), 160)
            assert remote.find("发送邮件")["r"] == button["r"], "send action scrolled away"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == before
            remote.shot(work / "compose-scrolled.png")
            return {"requested": size, "actual_window": window, "send_button": button["r"],
                    "scroll_area": scroll, "fixed_send_action": True, "disabled_without_account": True,
                    "draft_bytes_unchanged": True, "external_send_executed": False}
        finally:
            if process.poll() is None:
                try:
                    remote.request("/quit")
                finally:
                    process.wait(timeout=15)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--card-host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8441)
    args = parser.parse_args()
    args.bundle = args.bundle.resolve()
    args.card_host = args.card_host.resolve()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    results = [run_size(args, size, args.port + i) for i, size in enumerate(("990x539", "412x892"))]
    report = {"evidence": "LOCAL visible card-host; synthetic draft, no mailbox credentials", "sizes": results}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
