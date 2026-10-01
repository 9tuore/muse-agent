"""Scoped synthetic Calendar actions with conflict checks and readback.

The native backend never asks TCC for permission. This service accepts only
explicitly selected test calendars and events with its own marker; it cannot
invite attendees or change existing personal meetings.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


TEST_TITLE_PREFIX = "[Muse Test] "
ACTION_ID = re.compile(r"[A-Za-z0-9._:-]{1,100}\Z")


class CalendarBackend(Protocol):
    def status(self) -> dict: ...
    def request_permission(self) -> dict: ...
    def calendars(self) -> dict: ...
    def events(self, calendar_id: str, start: str, end: str) -> dict: ...
    def create(self, payload: dict) -> dict: ...
    def create_event(self, payload: dict) -> dict: ...
    def update(self, payload: dict) -> dict: ...
    def delete(self, payload: dict) -> dict: ...


class NativeEventKitBackend:
    def __init__(self, helper: Path):
        self.helper = Path(helper)
        if not self.helper.is_file():
            raise ValueError("calendar_helper_missing")

    def _call(self, operation: str, payload: dict | None = None, *, timeout: float = 10) -> dict:
        encoded = json.dumps(payload or {}, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode()) > 16_384:
            return {"status": "BLOCKED", "error": "calendar_request_too_large"}
        try:
            completed = subprocess.run([str(self.helper), operation], input=encoded + "\n",
                                       capture_output=True, text=True, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return {"status": "BLOCKED", "error": "calendar_helper_unavailable"}
        if completed.returncode not in (0, 2) or len(completed.stdout) > 131_072:
            return {"status": "BLOCKED", "error": "calendar_helper_failed"}
        try:
            result = json.loads(completed.stdout)
        except (ValueError, TypeError):
            return {"status": "BLOCKED", "error": "calendar_helper_invalid_response"}
        return result if isinstance(result, dict) else {"status": "BLOCKED", "error": "calendar_helper_invalid_response"}

    def status(self) -> dict:
        return self._call("status")

    def request_permission(self) -> dict:
        # The operating-system prompt waits for the user's own decision, so this
        # call must outlive the default helper timeout.
        return self._call("request-full-access", timeout=130)

    def calendars(self) -> dict:
        return self._call("calendars")

    def events(self, calendar_id: str, start: str, end: str) -> dict:
        return self._call("events", {"calendar_id": calendar_id, "start": start, "end": end})

    def create(self, payload: dict) -> dict:
        return self._call("create", payload)

    def create_event(self, payload: dict) -> dict:
        return self._call("create-event", payload)

    def update(self, payload: dict) -> dict:
        return self._call("update", payload)

    def delete(self, payload: dict) -> dict:
        return self._call("delete", payload)


class TestCalendarService:
    def __init__(self, backend: CalendarBackend, *, allowed_calendar_ids: set[str]):
        self.backend = backend
        self.allowed_calendar_ids = set(allowed_calendar_ids)

    def permission_status(self) -> dict:
        return self.backend.status()

    def request_permission(self) -> dict:
        """Ask the operating system for Calendar access.

        This is the only path that may raise the macOS prompt; it never grants
        access itself and the caller must re-read :meth:`permission_status`
        afterwards. Read/write operations remain gated on FULL_ACCESS.
        """
        return self.backend.request_permission()

    def list_calendars(self) -> dict:
        status = self.backend.status()
        if status.get("status") != "FULL_ACCESS":
            return {"status": "WAITING_USER_PERMISSION", "authorization": status}
        return self.backend.calendars()

    def _authorized(self, calendar_id: str) -> dict | None:
        if not isinstance(calendar_id, str) or calendar_id not in self.allowed_calendar_ids:
            return {"status": "BLOCKED", "error": "calendar_outside_approved_scope"}
        status = self.backend.status()
        if status.get("status") != "FULL_ACCESS":
            return {"status": "WAITING_USER_PERMISSION", "authorization": status}
        return None

    @staticmethod
    def _time_window(start: str, end: str, timezone_name: str) -> tuple[datetime, datetime]:
        try:
            first = datetime.fromisoformat(start.replace("Z", "+00:00"))
            last = datetime.fromisoformat(end.replace("Z", "+00:00"))
            zone = ZoneInfo(timezone_name)
        except (ValueError, TypeError, ZoneInfoNotFoundError):
            raise ValueError("calendar_time_or_zone_invalid") from None
        if (first.tzinfo is None or last.tzinfo is None or first >= last or
                last - first > timedelta(days=31) or
                first.utcoffset() != first.astimezone(zone).utcoffset() or
                last.utcoffset() != last.astimezone(zone).utcoffset()):
            raise ValueError("calendar_time_or_zone_invalid")
        return first, last

    def read_window(self, calendar_id: str, start: str, end: str, timezone_name: str) -> dict:
        blocked = self._authorized(calendar_id)
        if blocked:
            return blocked
        try:
            first, last = self._time_window(start, end, timezone_name)
        except ValueError as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        result = self.backend.events(calendar_id, start, end)
        if result.get("status") != "COMPLETED":
            return result
        events = result.get("events", [])
        if not isinstance(events, list) or len(events) > 100:
            return {"status": "BLOCKED", "error": "calendar_result_invalid"}
        intervals = []
        for event in events:
            try:
                event_start = datetime.fromisoformat(event["start"].replace("Z", "+00:00"))
                event_end = datetime.fromisoformat(event["end"].replace("Z", "+00:00"))
            except (KeyError, TypeError, ValueError):
                return {"status": "BLOCKED", "error": "calendar_result_invalid"}
            if event_start.tzinfo is None or event_end.tzinfo is None or event_start >= event_end:
                return {"status": "BLOCKED", "error": "calendar_result_invalid"}
            event_start = event_start.astimezone(first.tzinfo)
            event_end = event_end.astimezone(first.tzinfo)
            if event_start < last and event_end > first:
                intervals.append((max(event_start, first), min(event_end, last)))
        intervals.sort()
        free = []
        cursor = first
        for busy_start, busy_end in intervals:
            if busy_start > cursor:
                free.append({"start": cursor.isoformat(), "end": busy_start.isoformat()})
            cursor = max(cursor, busy_end)
        if cursor < last:
            free.append({"start": cursor.isoformat(), "end": last.isoformat()})
        return {"status": "COMPLETED", "calendar_id": calendar_id, "scope": "selected_calendar_only",
                "events": events, "free_slots": free, "timezone": timezone_name}

    def create_test_event(self, *, action_id: str, calendar_id: str, title: str,
                          start: str, end: str, timezone_name: str, approved: bool) -> dict:
        if not approved:
            return {"status": "WAITING_APPROVAL"}
        blocked = self._authorized(calendar_id)
        if blocked:
            return blocked
        if (not isinstance(action_id, str) or not ACTION_ID.fullmatch(action_id) or
                not isinstance(title, str) or not title.startswith(TEST_TITLE_PREFIX) or len(title) > 160):
            return {"status": "BLOCKED", "error": "synthetic_event_required"}
        try:
            self._time_window(start, end, timezone_name)
        except ValueError as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        before = self.read_window(calendar_id, start, end, timezone_name)
        if before["status"] != "COMPLETED":
            return before
        previous = [item for item in before["events"] if item.get("marker") == action_id]
        if previous:
            item = previous[0]
            if not self._matches_event(item, title, start, end):
                return {"status": "BLOCKED", "error": "action_id_changed"}
            return {"status": "COMPLETED", "event": item, "replayed": True}
        if before["events"]:
            return {"status": "CONFLICT", "conflicts": [item["event_id"] for item in before["events"]]}
        created = self.backend.create({"calendar_id": calendar_id, "title": title, "start": start,
                                       "end": end, "timezone": timezone_name, "marker": action_id})
        if created.get("status") not in ("COMPLETED", "RESULT_UNCERTAIN"):
            return created
        after = self.read_window(calendar_id, start, end, timezone_name)
        matches = [item for item in after.get("events", []) if item.get("marker") == action_id]
        if len(matches) != 1:
            return {"status": "RESULT_UNCERTAIN", "backend_status": created.get("status"),
                    "error": "create_readback_missing"}
        item = matches[0]
        if not self._matches_event(item, title, start, end):
            return {"status": "RESULT_UNCERTAIN", "error": "create_readback_changed"}
        return {"status": "COMPLETED", "event": item, "readback_matches": True, "replayed": False}

    @staticmethod
    def _matches_event(item: dict, title: str, start: str, end: str) -> bool:
        try:
            return (item["title"] == title and
                    datetime.fromisoformat(item["start"].replace("Z", "+00:00")) ==
                    datetime.fromisoformat(start.replace("Z", "+00:00")) and
                    datetime.fromisoformat(item["end"].replace("Z", "+00:00")) ==
                    datetime.fromisoformat(end.replace("Z", "+00:00")))
        except (KeyError, TypeError, ValueError):
            return False

    def update_test_event(self, *, calendar_id: str, event_id: str, marker: str, title: str,
                          start: str, end: str, timezone_name: str, approved: bool) -> dict:
        if not approved:
            return {"status": "WAITING_APPROVAL"}
        blocked = self._authorized(calendar_id)
        if blocked:
            return blocked
        if (not isinstance(event_id, str) or not event_id or not isinstance(marker, str) or
                not ACTION_ID.fullmatch(marker) or not isinstance(title, str) or
                not title.startswith(TEST_TITLE_PREFIX) or len(title) > 160):
            return {"status": "BLOCKED", "error": "synthetic_event_required"}
        try:
            self._time_window(start, end, timezone_name)
        except ValueError as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        before = self.read_window(calendar_id, start, end, timezone_name)
        if before["status"] != "COMPLETED":
            return before
        conflicts = [item["event_id"] for item in before["events"] if item.get("event_id") != event_id]
        if conflicts:
            return {"status": "CONFLICT", "conflicts": conflicts}
        result = self.backend.update({"calendar_id": calendar_id, "event_id": event_id, "marker": marker,
                                      "title": title, "start": start, "end": end, "timezone": timezone_name})
        if result.get("status") not in ("COMPLETED", "RESULT_UNCERTAIN"):
            return result
        after = self.read_window(calendar_id, start, end, timezone_name)
        matches = [item for item in after.get("events", []) if item.get("marker") == marker]
        if len(matches) != 1:
            return {"status": "RESULT_UNCERTAIN", "backend_status": result.get("status")}
        item = matches[0]
        if not self._matches_event(item, title, start, end):
            return {"status": "RESULT_UNCERTAIN", "error": "update_readback_changed"}
        return {"status": "COMPLETED", "event": item, "readback_matches": True}

    def delete_test_event(self, *, calendar_id: str, event_id: str, marker: str,
                          start: str, end: str, timezone_name: str, approved: bool,
                          confirm_delete: bool) -> dict:
        if not approved or not confirm_delete:
            return {"status": "WAITING_APPROVAL"}
        blocked = self._authorized(calendar_id)
        if blocked:
            return blocked
        if not isinstance(event_id, str) or not event_id or not isinstance(marker, str) or not ACTION_ID.fullmatch(marker):
            return {"status": "BLOCKED", "error": "synthetic_event_required"}
        try:
            self._time_window(start, end, timezone_name)
        except ValueError as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        before = self.read_window(calendar_id, start, end, timezone_name)
        if before["status"] != "COMPLETED":
            return before
        if not any(item.get("event_id") == event_id and item.get("marker") == marker
                   for item in before["events"]):
            return {"status": "BLOCKED", "error": "test_event_not_found"}
        result = self.backend.delete({"calendar_id": calendar_id, "event_id": event_id, "marker": marker})
        if result.get("status") not in ("COMPLETED", "RESULT_UNCERTAIN"):
            return result
        after = self.read_window(calendar_id, start, end, timezone_name)
        if after["status"] != "COMPLETED" or any(item.get("event_id") == event_id for item in after["events"]):
            return {"status": "RESULT_UNCERTAIN", "backend_status": result.get("status")}
        return {"status": "COMPLETED", "event_id": event_id, "readback_absent": True}


class UserCalendarService:
    """User-approved real calendar events.

    Unlike :class:`TestCalendarService` (synthetic ``[Muse Test]`` events only),
    this writes events the user actually asked for. The host still owns approval:
    every write requires ``approved=True`` and is followed by an independent
    readback; nothing is created or modified before that confirmation.
    """

    def __init__(self, backend: CalendarBackend):
        self.backend = backend

    def permission_status(self) -> dict:
        return self.backend.status()

    def request_permission(self) -> dict:
        return self.backend.request_permission()

    def writable_calendars(self) -> dict:
        result = self.backend.calendars()
        if result.get("status") != "COMPLETED":
            return result
        rows = [item for item in result.get("calendars", [])
                if isinstance(item, dict) and item.get("writable")]
        default_id = next((item["id"] for item in rows if item.get("default")), "")
        return {"status": "COMPLETED", "calendars": rows, "default_id": default_id}

    def create_event(self, *, title: Any, start: Any, end: Any, timezone_name: Any,
                     calendar_id: Optional[str] = None, notes: Optional[str] = None,
                     approved: bool = False) -> dict:
        if not approved:
            return {"status": "WAITING_APPROVAL"}
        status = self.backend.status()
        if status.get("status") != "FULL_ACCESS":
            return {"status": "WAITING_USER_PERMISSION", "authorization": status}
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 160:
            return {"status": "BLOCKED", "error": "event_title_invalid"}
        try:
            first, last = TestCalendarService._time_window(start, end, timezone_name)
        except ValueError as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        if notes is not None and (not isinstance(notes, str) or len(notes) > 400):
            return {"status": "BLOCKED", "error": "event_notes_invalid"}
        if calendar_id is None:
            listing = self.writable_calendars()
            if listing.get("status") != "COMPLETED" or not listing["calendars"]:
                return {"status": "BLOCKED", "error": "no_writable_calendar"}
            calendar_id = listing.get("default_id") or listing["calendars"][0]["id"]
        if not isinstance(calendar_id, str) or not calendar_id:
            return {"status": "BLOCKED", "error": "calendar_id_invalid"}
        payload = {"calendar_id": calendar_id, "title": title.strip(),
                   "start": start, "end": end, "timezone": timezone_name}
        if notes:
            payload["notes"] = notes
        created = self.backend.create_event(payload)
        if created.get("status") != "COMPLETED":
            return created
        event = created.get("event") or {}
        try:
            readback_ok = (event.get("title") == title.strip() and
                           datetime.fromisoformat(event["start"].replace("Z", "+00:00")) == first and
                           datetime.fromisoformat(event["end"].replace("Z", "+00:00")) == last)
        except (KeyError, TypeError, ValueError):
            readback_ok = False
        if not readback_ok:
            return {"status": "RESULT_UNCERTAIN", "error": "create_readback_changed"}
        return {"status": "COMPLETED", "event": event, "readback_matches": True,
                "calendar_id": calendar_id}
