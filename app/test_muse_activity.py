"""Opt-in Activity scope and bounded event transport."""

import json
import tempfile
import unittest
from pathlib import Path

from muse_activity import ActivityFeed


class ActivityFeedTests(unittest.TestCase):
    def test_disabled_by_default_and_sensitive_scope_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            helper = Path(tmp) / "helper"
            helper.write_text("#!/bin/sh\nexit 0\n")
            helper.chmod(0o700)
            feed = ActivityFeed(helper, allowed_bundle_ids={"com.apple.TextEdit"})
            self.assertEqual(feed.start()["status"], "DISABLED")
            self.assertEqual(feed.poll()["status"], "DISABLED")
            with self.assertRaisesRegex(ValueError, "activity_scope_invalid"):
                ActivityFeed(helper, allowed_bundle_ids={"com.example.password-manager"}, enabled=True)

    def test_real_pipe_events_are_ordered_scoped_and_cleared_on_disable(self):
        with tempfile.TemporaryDirectory() as tmp:
            helper = Path(tmp) / "helper"
            records = [
                {"status": "EVENT", "type": "frontmost_snapshot", "bundle_id": "com.apple.TextEdit",
                 "source": "NSWorkspace", "observed_at": "2026-09-28T00:00:00Z"},
                {"status": "EVENT", "type": "frontmost_changed", "bundle_id": "com.apple.TextEdit",
                 "source": "NSWorkspace", "observed_at": "2026-09-28T00:00:01Z"},
                {"status": "EVENT", "type": "frontmost_changed", "bundle_id": "com.other.App",
                 "source": "NSWorkspace", "observed_at": "2026-09-28T00:00:02Z"},
            ]
            helper.write_text("#!/usr/bin/python3\nimport time\nprint(" + repr(json.dumps(records[0])) + ", flush=True)\n"
                              "print(" + repr(json.dumps(records[1])) + ", flush=True)\n"
                              "print(" + repr(json.dumps(records[2])) + ", flush=True)\n"
                              "time.sleep(5)\n")
            helper.chmod(0o700)
            feed = ActivityFeed(helper, allowed_bundle_ids={"com.apple.TextEdit"}, enabled=True)
            try:
                self.assertEqual(feed.start()["status"], "RUNNING")
                self.assertEqual(feed.poll(2)["type"], "frontmost_snapshot")
                self.assertEqual(feed.poll(2)["type"], "frontmost_changed")
                self.assertEqual(feed.poll(2)["error"], "activity_event_outside_scope")
                self.assertEqual(len(feed.recent), 2)
                self.assertEqual(feed.set_enabled(False), {"status": "DISABLED", "recent_count": 0})
            finally:
                feed.stop()


if __name__ == "__main__":
    unittest.main()
