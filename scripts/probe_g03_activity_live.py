#!/usr/bin/env python3
"""Observe native activation events for two already-running, approved apps."""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_activity import ActivityFeed


HELPER = Path("/tmp/gosim-g03-build/muse_activity_helper")
TARGET = "com.apple.TextEdit"


def frontmost() -> str:
    result = subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", "-e",
                             'ObjC.import("AppKit"); ObjC.unwrap($.NSWorkspace.sharedWorkspace.frontmostApplication.bundleIdentifier)'],
                            capture_output=True, text=True, timeout=5, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def main():
    previous = frontmost()
    if previous not in {"com.openai.codex", "com.apple.TextEdit"} or previous == TARGET:
        print(json.dumps({"status": "BLOCKED", "error": "frontmost_context_not_safe_to_switch",
                          "previous_bundle": previous})); return
    if subprocess.run(["/usr/bin/pgrep", "-x", "TextEdit"], capture_output=True).returncode != 0:
        print(json.dumps({"status": "BLOCKED", "error": "textedit_not_running"})); return
    feed = ActivityFeed(HELPER, allowed_bundle_ids={previous, TARGET}, enabled=True)
    events = []
    try:
        feed.start()
        first = feed.poll(3)
        if first.get("status") == "EVENT":
            events.append(first)
        subprocess.run(["/usr/bin/open", "-b", TARGET], timeout=5, check=True)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            event = feed.poll(1)
            if event.get("status") == "EVENT":
                events.append(event)
                if event.get("type") == "frontmost_changed" and event.get("bundle_id") == TARGET:
                    break
    finally:
        subprocess.run(["/usr/bin/open", "-b", previous], timeout=5, check=False)
        feed.stop()
    print(json.dumps({"test_id": "G03-ACTIVITY-NATIVE-EVENT", "phase": "A",
                      "actual_at": datetime.now(timezone.utc).isoformat(),
                      "status": "PASS_LIVE" if any(event["type"] == "frontmost_changed" and
                                                     event["bundle_id"] == TARGET for event in events) else "BLOCKED",
                      "events": events, "previous_bundle_restored": frontmost() == previous,
                      "source": "NSWorkspace", "scope": sorted({previous, TARGET}),
                      "unsupported": ["global_notifications", "lock_screen", "screen_content", "clipboard"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
