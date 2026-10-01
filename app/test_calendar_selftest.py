import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import calendar_selftest
from test_muse_calendar import FakeCalendar


class WritableFakeCalendar(FakeCalendar):
    """FakeCalendar whose single calendar is writable, as the real store is."""

    def calendars(self):
        return {"status": "COMPLETED",
                "calendars": [{"id": "synthetic-calendar", "title": "Muse Test", "writable": True}]}


class CalendarSelftestTests(unittest.TestCase):
    def test_pick_calendar_prefers_named_test_calendar_then_first_writable(self):
        calendars = [
            {"id": "a", "title": "家庭", "writable": True},
            {"id": "b", "title": "Muse Test", "writable": True},
            {"id": "c", "title": "只读", "writable": False},
        ]
        self.assertEqual(calendar_selftest.pick_calendar(calendars)["id"], "b")
        self.assertEqual(calendar_selftest.pick_calendar(
            [{"id": "a", "title": "家庭", "writable": True}, {"id": "b", "title": "Archive", "writable": True}])["id"], "b")
        self.assertIsNone(calendar_selftest.pick_calendar([{"id": "c", "title": "ro", "writable": False}]))

    def test_free_window_returns_a_future_slot(self):
        backend = WritableFakeCalendar()
        service = calendar_selftest.TestCalendarService(backend, allowed_calendar_ids={"synthetic-calendar"})
        zone = ZoneInfo("Asia/Shanghai")
        start, end = calendar_selftest.free_window(service, "synthetic-calendar", "Asia/Shanghai", zone)
        self.assertIsNotNone(start)
        self.assertLess(datetime.now(zone), start)
        self.assertEqual((end - start).total_seconds(), 1800)

    def test_create_then_delete_loop_reports_every_readback(self):
        backend = WritableFakeCalendar()
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            zone = ZoneInfo("Asia/Shanghai")

            out = io.StringIO()
            with redirect_stdout(out):
                calendar_selftest.run_create(backend, workspace, "Asia/Shanghai", zone)
            created = json.loads(out.getvalue().strip().splitlines()[-1])
            self.assertTrue(created["ok"])
            self.assertEqual(created["stage"], "create")
            self.assertTrue(created["steps"]["create"]["readback_matches"])
            self.assertTrue(created["steps"]["update"]["readback_matches"])
            self.assertTrue(created["title"].startswith("[Muse Test] MUSE-CALENDAR-TEST-"))
            self.assertTrue((workspace / calendar_selftest.STATE_NAME).is_file())

            out = io.StringIO()
            with redirect_stdout(out):
                calendar_selftest.run_delete(backend, workspace, "Asia/Shanghai", zone)
            deleted = json.loads(out.getvalue().strip().splitlines()[-1])
            self.assertTrue(deleted["ok"])
            self.assertTrue(deleted["readback_absent"])
            self.assertEqual(deleted["delete_status"], "COMPLETED")
            self.assertFalse((workspace / calendar_selftest.STATE_NAME).exists())
            self.assertEqual(backend.rows, {})

    def test_create_stops_when_full_access_is_not_granted(self):
        class DenyingCalendar(WritableFakeCalendar):
            def __init__(self):
                super().__init__()
                self.authorization = "NOT_DETERMINED"

            def request_permission(self):
                self.calls.append("request_permission")
                return {"status": "NOT_DETERMINED", "granted_full_access": False}

        backend = DenyingCalendar()
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with redirect_stdout(out):
                calendar_selftest.run_create(backend, Path(tmp), "Asia/Shanghai", ZoneInfo("Asia/Shanghai"))
            result = json.loads(out.getvalue().strip().splitlines()[-1])
            self.assertFalse(result["ok"])
            self.assertEqual(result["stage"], "permission")
            self.assertEqual(backend.calls, ["request_permission"])


if __name__ == "__main__":
    unittest.main()
