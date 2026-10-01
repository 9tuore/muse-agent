#!/usr/bin/env python3
"""Bounded live Calendar self-test driven from the packaged Muse app.

This runs through the existing :class:`TestCalendarService`, so every write is
followed by an independent readback and only ``[Muse Test]`` events carrying a
unique marker are ever created, modified or removed. It never touches a user's
existing events.

Usage::

    calendar_selftest.py create <workspace> <helper> <timezone-name>
    calendar_selftest.py delete <workspace> <helper> <timezone-name>

The ``create`` mode asks for full access if needed, then creates + reads back +
modifies + reads back one test event, and stores its identity in
``<workspace>/calendar-selftest.json``. The ``delete`` mode removes only that
exact event and confirms it is gone (the native app asks the user first).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from muse_calendar import (TEST_TITLE_PREFIX, NativeEventKitBackend,
                           TestCalendarService)

STATE_NAME = "calendar-selftest.json"
EVIDENCE_NAME = "calendar-selftest-evidence.jsonl"
_EVIDENCE: "Path | None" = None


def emit(value: dict) -> None:
    if _EVIDENCE is not None:
        try:
            with _EVIDENCE.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"at": datetime.now().isoformat(), **value},
                                        ensure_ascii=False) + "\n")
        except OSError:
            pass
    sys.stdout.write(json.dumps(value, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def pick_calendar(calendars: list) -> dict | None:
    writable = [c for c in calendars if isinstance(c, dict) and c.get("writable")]
    if not writable:
        return None
    for calendar in writable:
        title = str(calendar.get("title") or "").lower()
        if "muse" in title or "test" in title:
            return calendar
    return sorted(writable, key=lambda c: str(c.get("title") or ""))[0]


def free_window(service: TestCalendarService, calendar_id: str, tz_name: str, zone: ZoneInfo):
    now = datetime.now(zone)
    for day in range(3, 33):
        start = (now + timedelta(days=day)).replace(hour=3, minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=30)
        read = service.read_window(calendar_id, start.isoformat(), end.isoformat(), tz_name)
        if read.get("status") == "COMPLETED" and not read.get("events"):
            return start, end
    return None, None


def run_delete(backend, workspace: Path, tz_name: str, zone: ZoneInfo) -> None:
    state_path = workspace / STATE_NAME
    if not state_path.is_file():
        emit({"ok": False, "stage": "delete", "error": "no_pending_selftest_state"})
        return
    state = json.loads(state_path.read_text(encoding="utf-8"))
    service = TestCalendarService(backend, allowed_calendar_ids={state["calendar_id"]})
    result = service.delete_test_event(
        calendar_id=state["calendar_id"], event_id=state["event_id"], marker=state["marker"],
        start=state["start"], end=state["end"], timezone_name=tz_name,
        approved=True, confirm_delete=True)
    read = service.read_window(state["calendar_id"], state["start"], state["end"], tz_name)
    absent = read.get("status") == "COMPLETED" and not any(
        item.get("event_id") == state["event_id"] for item in read.get("events", []))
    if result.get("status") == "COMPLETED" and absent:
        state_path.unlink(missing_ok=True)
    emit({"ok": result.get("status") == "COMPLETED" and absent, "stage": "delete",
          "event_id": state["event_id"], "title": state.get("title", ""),
          "delete_status": result.get("status"), "readback_absent": absent,
          "detail": result})


def run_create(backend, workspace: Path, tz_name: str, zone: ZoneInfo) -> None:
    status = backend.status()
    requested = False
    if status.get("status") != "FULL_ACCESS":
        requested = True
        backend.request_permission()
        status = backend.status()
    if status.get("status") != "FULL_ACCESS":
        emit({"ok": False, "stage": "permission", "prompt_requested": requested,
              "authorization": status})
        return
    calendars = backend.calendars().get("calendars", [])
    target = pick_calendar(calendars)
    if target is None:
        emit({"ok": False, "stage": "calendar", "error": "no_writable_calendar"})
        return
    service = TestCalendarService(backend, allowed_calendar_ids={target["id"]})
    start, end = free_window(service, target["id"], tz_name, zone)
    if start is None:
        emit({"ok": False, "stage": "window", "error": "no_free_window_found"})
        return
    stamp = datetime.now(zone).strftime("%Y%m%d-%H%M%S")
    marker = "muse-calendar-selftest-" + stamp
    title = TEST_TITLE_PREFIX + "MUSE-CALENDAR-TEST-" + stamp
    created = service.create_test_event(
        action_id=marker, calendar_id=target["id"], title=title,
        start=start.isoformat(), end=end.isoformat(), timezone_name=tz_name, approved=True)
    steps = {"permission": {"status": status.get("status"), "prompt_requested": requested},
             "calendar": {"id": target["id"], "title": target.get("title", "")},
             "window": {"start": start.isoformat(), "end": end.isoformat()},
             "create": {"status": created.get("status"),
                        "readback_matches": created.get("readback_matches", False),
                        "event_id": (created.get("event") or {}).get("event_id", "")}}
    if created.get("status") != "COMPLETED":
        emit({"ok": False, "stage": "create", "title": title, "steps": steps, "detail": created})
        return
    event_id = created["event"]["event_id"]
    new_end = end + timedelta(minutes=15)
    updated_title = title + " (updated)"
    updated = service.update_test_event(
        calendar_id=target["id"], event_id=event_id, marker=marker, title=updated_title,
        start=start.isoformat(), end=new_end.isoformat(), timezone_name=tz_name, approved=True)
    steps["update"] = {"status": updated.get("status"),
                       "readback_matches": updated.get("readback_matches", False),
                       "title": updated_title}
    state = {"calendar_id": target["id"], "event_id": event_id, "marker": marker,
             "title": updated_title, "start": start.isoformat(), "end": new_end.isoformat()}
    (workspace / STATE_NAME).write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    ok = created.get("readback_matches") is True and updated.get("status") == "COMPLETED"
    emit({"ok": ok, "stage": "create", "title": updated_title,
          "calendar_title": target.get("title", ""), "event_id": event_id,
          "window": {"start": start.isoformat(), "end": new_end.isoformat()},
          "steps": steps, "delete_pending_confirmation": True})


def main(argv: list) -> int:
    global _EVIDENCE
    if len(argv) != 5 or argv[1] not in {"create", "delete"}:
        emit({"ok": False, "error": "usage: calendar_selftest.py create|delete <workspace> <helper> <tz>"})
        return 2
    mode, workspace, helper, tz_name = argv[1], Path(argv[2]), Path(argv[3]), argv[4]
    try:
        zone = ZoneInfo(tz_name)
    except Exception:
        emit({"ok": False, "error": "invalid_timezone"})
        return 2
    _EVIDENCE = workspace / EVIDENCE_NAME
    backend = NativeEventKitBackend(helper)
    if mode == "delete":
        run_delete(backend, workspace, tz_name, zone)
    else:
        run_create(backend, workspace, tz_name, zone)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
