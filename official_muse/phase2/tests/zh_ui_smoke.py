"""Check Chinese labels in the real visible Muse and host Mail sheet.

Run before asking the person to enter credentials. This test never supplies a
password, signs into an account, sends mail, or changes system calendars.
"""
import argparse
import json
from pathlib import Path

from remote import Remote
from visible_nav import PAGES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    remote = Remote(args.port)
    report = {"evidence": "LIVE visible packaged OctoSense Shell", "pages": []}
    for label, expected, slug in PAGES:
        remote.click(label)
        assert remote.find("page_title")["t"] == expected
        if slug == "settings":
            remote.find("Muse 官方应用 · 0.2.10（中文修订候选）")
        remote.shot(args.output / f"{slug}.png")
        report["pages"].append({"page": label, "title": expected, "passed": True})

    remote.click("邮箱")
    remote.click("连接账号")
    for label in ("取消", "登录", "OctoSense · 添加邮箱账号", "邮箱地址",
                  "登录用户名（与邮箱地址不同时填写）", "密码或邮箱应用专用密码",
                  "IMAP：所有文件夹", "POP3：仅收件箱"):
        remote.wait_for(label)
    # Only this newly opened, untouched sheet is captured. No real account
    # details or secret fields are included in the saved JSON.
    remote.shot(args.output / "mail-signin.png")
    remote.click("登录")  # Empty form: validation rejects before any network call.
    remote.wait_for("请填写有效的邮箱地址。")
    remote.shot(args.output / "mail-signin-validation.png")
    x, y, width, height = remote.find("password")["r"]
    remote.scroll(int(x + width - 8), int(y + height / 2), 180)
    remote.click("POP3：仅收件箱")
    remote.wait_for("收件服务器（POP3，TLS）")
    remote.shot(args.output / "mail-signin-servers.png")
    remote.click("IMAP：所有文件夹")
    remote.wait_for("收件服务器（IMAP，TLS）")
    x, y, width, height = remote.find("incoming")["r"]
    remote.scroll(int(x + width - 8), int(y + height / 2), -10000)
    remote.click("取消")
    remote.wait_for("page_title")
    report["mail_host"] = {"labels_chinese": True, "empty_validation_chinese": True,
                           "protocol_switches": ["pop3", "imap"],
                           "real_signin_or_send": False}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
