import unittest

from muse_calendar import TestCalendarService


class FakeCalendar:
    def __init__(self):
        self.authorization = "FULL_ACCESS"
        self.rows = {}
        self.next_id = 1
        self.calls = []

    def status(self):
        return {"status": self.authorization}

    def request_permission(self):
        self.calls.append("request_permission")
        self.authorization = "FULL_ACCESS"
        return {"status": "FULL_ACCESS", "granted_full_access": True}

    def calendars(self):
        return {"status": "COMPLETED", "calendars": [{"id": "synthetic-calendar", "title": "Muse Test"}]}

    def events(self, calendar_id, start, end):
        return {"status": "COMPLETED", "events": [dict(row) for row in self.rows.values()
                                                  if row["calendar_id"] == calendar_id and
                                                  row["start"] < end and row["end"] > start]}

    def create(self, payload):
        self.calls.append("create")
        event_id = "event-" + str(self.next_id)
        self.next_id += 1
        self.rows[event_id] = dict(payload, event_id=event_id)
        return {"status": "COMPLETED", "event_id": event_id}

    def update(self, payload):
        self.calls.append("update")
        row = self.rows.get(payload["event_id"])
        if not row or row["marker"] != payload["marker"] or row["calendar_id"] != payload["calendar_id"]:
            return {"status": "BLOCKED"}
        row.update(payload)
        return {"status": "COMPLETED"}

    def delete(self, payload):
        self.calls.append("delete")
        row = self.rows.get(payload["event_id"])
        if not row or row["marker"] != payload["marker"] or row["calendar_id"] != payload["calendar_id"]:
            return {"status": "BLOCKED"}
        del self.rows[payload["event_id"]]
        return {"status": "COMPLETED"}


class CalendarTests(unittest.TestCase):
    START = "2026-10-01T14:00:00+08:00"
    END = "2026-10-01T15:00:00+08:00"

    def setUp(self):
        self.backend = FakeCalendar()
        self.service = TestCalendarService(self.backend, allowed_calendar_ids={"synthetic-calendar"})

    def create(self, **changes):
        args = dict(action_id="synthetic-1", calendar_id="synthetic-calendar", title="[Muse Test] rehearsal",
                    start=self.START, end=self.END, timezone_name="Asia/Shanghai", approved=True)
        args.update(changes)
        return self.service.create_test_event(**args)

    def test_synthetic_create_conflict_replay_update_delete_readback(self):
        first = self.create()
        self.assertEqual(first["status"], "COMPLETED")
        self.assertTrue(first["readback_matches"])
        self.assertEqual(self.create()["replayed"], True)
        self.assertEqual(self.backend.calls, ["create"])
        self.assertEqual(self.create(action_id="synthetic-2")["status"], "CONFLICT")
        event_id = first["event"]["event_id"]
        updated = self.service.update_test_event(calendar_id="synthetic-calendar", event_id=event_id,
                                                 marker="synthetic-1", title="[Muse Test] revised",
                                                 start=self.START, end=self.END,
                                                 timezone_name="Asia/Shanghai", approved=True)
        self.assertEqual(updated["status"], "COMPLETED")
        self.assertTrue(updated["readback_matches"])
        self.assertEqual(self.service.delete_test_event(calendar_id="synthetic-calendar", event_id=event_id,
                                                       marker="synthetic-1", start=self.START, end=self.END,
                                                       timezone_name="Asia/Shanghai", approved=True,
                                                       confirm_delete=False)["status"], "WAITING_APPROVAL")
        self.assertEqual(self.service.delete_test_event(calendar_id="synthetic-calendar", event_id=event_id,
                                                       marker="synthetic-1", start=self.START, end=self.END,
                                                       timezone_name="Asia/Shanghai", approved=True,
                                                       confirm_delete=True)["status"], "COMPLETED")
        self.assertEqual(self.backend.rows, {})

    def test_scope_permission_and_time_zone_fail_closed(self):
        self.assertEqual(self.create(calendar_id="personal-calendar")["error"], "calendar_outside_approved_scope")
        self.assertEqual(self.create(approved=False)["status"], "WAITING_APPROVAL")
        self.assertEqual(self.create(title="Real meeting")["error"], "synthetic_event_required")
        self.assertEqual(self.create(start="2026-10-01T14:00:00+00:00")["error"],
                         "calendar_time_or_zone_invalid")
        self.backend.authorization = "DENIED"
        self.assertEqual(self.create()["status"], "WAITING_USER_PERMISSION")
        self.assertEqual(self.backend.calls, [])

    def test_native_utc_readback_matches_explicit_local_offset(self):
        item = {"title": "[Muse Test] rehearsal", "start": "2026-10-01T06:00:00Z",
                "end": "2026-10-01T07:00:00Z"}
        self.assertTrue(TestCalendarService._matches_event(
            item, "[Muse Test] rehearsal", self.START, self.END))

    def test_request_permission_is_the_only_prompt_path_and_regates_readback(self):
        self.backend.authorization = "NOT_DETERMINED"
        self.assertEqual(self.service.permission_status()["status"], "NOT_DETERMINED")
        # Read/write stays blocked until full access exists.
        self.assertEqual(self.create()["status"], "WAITING_USER_PERMISSION")
        self.assertEqual(self.backend.calls, [])
        granted = self.service.request_permission()
        self.assertEqual(granted["status"], "FULL_ACCESS")
        self.assertTrue(granted["granted_full_access"])
        # After the OS grant the same call reaches the backend.
        self.assertEqual(self.create()["status"], "COMPLETED")

    def test_read_window_reports_only_selected_calendar_free_gaps(self):
        self.create()
        read = self.service.read_window("synthetic-calendar", "2026-10-01T13:00:00+08:00",
                                        "2026-10-01T16:00:00+08:00", "Asia/Shanghai")
        self.assertEqual(read["status"], "COMPLETED")
        self.assertEqual(len(read["events"]), 1)
        self.assertEqual(len(read["free_slots"]), 2)
        self.assertEqual(read["scope"], "selected_calendar_only")

    def test_update_refuses_conflicting_selected_calendar_event(self):
        created = self.create()
        self.backend.rows["other"] = {
            "event_id": "other", "calendar_id": "synthetic-calendar", "title": "Other event",
            "start": self.START, "end": self.END, "marker": ""}
        result = self.service.update_test_event(
            calendar_id="synthetic-calendar", event_id=created["event"]["event_id"],
            marker="synthetic-1", title="[Muse Test] revised", start=self.START, end=self.END,
            timezone_name="Asia/Shanghai", approved=True)
        self.assertEqual(result, {"status": "CONFLICT", "conflicts": ["other"]})
        self.assertEqual(self.backend.calls, ["create"])


if __name__ == "__main__":
    unittest.main()
