"""Capture real visible-window Muse pages through the Makepad remote bridge.

The caller opens Muse in a visible card-host or Shell window first. This tool
only clicks navigation and saves pixels returned by that same running host.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from remote import Remote


PAGES = (
    ("对话", "对话", "chat"),
    ("长期目标", "长期目标", "goals"),
    ("记忆", "记忆", "memory"),
    ("活动记录", "活动记录", "activity"),
    ("邮箱", "邮箱", "mail"),
    ("日历", "日历", "calendar"),
    ("能力授权", "能力与授权", "capabilities"),
    ("设置", "设置", "settings"),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    remote = Remote(args.port)
    args.output.mkdir(parents=True, exist_ok=True)
    for label, expected_title, slug in PAGES:
        remote.click(label)
        title = remote.find("page_title").get("t")
        if title != expected_title:
            raise AssertionError(f"{slug}: opened {title!r}, expected {expected_title!r}")
        path = args.output / f"{slug}.png"
        remote.shot(path)
        print(f"{slug}: {path}")


if __name__ == "__main__":
    main()
