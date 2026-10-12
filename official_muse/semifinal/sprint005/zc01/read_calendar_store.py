#!/usr/bin/env python3
"""Independent, read-only Calendar owner-store evidence for ZC05 fixtures.

This is filesystem readback, not CalendarService RPC or an Agent receipt.
No subprocess, network, model, GUI, profile or production fallback is used.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

FIXTURE_BASE = Path("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/sprint005")
SPEC = "SPRINT005_CALENDAR_READBACK.json"
MAX_BYTES = 1024 * 1024
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class Refused(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refused("duplicate_json_key")
        result[key] = value
    return result


def parse(data):
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError):
        raise Refused("invalid_json") from None


def read_file(parent_fd, name, maximum):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise Refused("not_a_bounded_regular_file")
        chunks, size = [], 0
        while True:
            chunk = os.read(fd, min(65536, maximum + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > maximum:
                raise Refused("file_too_large")
        after = os.fstat(fd)
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise Refused("store_changed_during_read_retry")
        return b"".join(chunks), after
    finally:
        os.close(fd)


def open_absolute_dir(path):
    fd = os.open("/", DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def state_case(root):
    # Check the spelling before resolving/opening anything. Markers alone
    # must never authorize a production root or a traversal into one.
    if not root.is_absolute() or any(p in (".", "..") for p in root.parts):
        raise Refused("fixture_path_not_allowed")
    try:
        relative = root.relative_to(FIXTURE_BASE)
    except ValueError:
        raise Refused("fixture_path_not_allowed") from None
    if len(relative.parts) != 2 or relative.parts[1] != "state" or not re.fullmatch(r"zc05-[a-z0-9][a-z0-9-]{0,63}", relative.parts[0]):
        raise Refused("fixture_path_not_allowed")
    return relative.parts[0]


def readback(root, request):
    case = state_case(root)
    if not isinstance(request, dict) or set(request) - {"owner", "method", "args"} or request.get("owner") != "os.calendar":
        raise Refused("calendar_owner_required")
    method = request.get("method")
    args = request.get("args", {})
    if method not in ("events", "get_event") or not isinstance(args, dict):
        raise Refused("read_only_method_required")
    if method == "events" and args:
        raise Refused("events_readback_has_no_service_filters")
    if method == "get_event" and (set(args) != {"id"} or not isinstance(args["id"], str)):
        raise Refused("one_stable_id_required")
    fds = []
    try:
        state_fd = open_absolute_dir(root)
        fds.append(state_fd)
        read_file(state_fd, "FIXTURE_ONLY", 2048)
        spec_bytes, _ = read_file(state_fd, SPEC, 16384)
        spec = parse(spec_bytes)
        if not isinstance(spec, dict) or set(spec) != {"schema", "fixture_kind", "case_name", "nonce", "stable_ids"}:
            raise Refused("fixture_spec_required")
        if type(spec["schema"]) is not int or spec["schema"] != 1 or spec["fixture_kind"] != "SPRINT005_ZC05_CALENDAR_READBACK" or spec["case_name"] != case:
            raise Refused("fixture_spec_mismatch")
        nonce, ids = spec["nonce"], spec["stable_ids"]
        if not isinstance(nonce, str) or not re.fullmatch(r"[A-Z0-9-]{4,40}", nonce):
            raise Refused("synthetic_nonce_required")
        if not isinstance(ids, list) or len(ids) > 100 or any(not isinstance(i, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", i) for i in ids) or len(ids) != len(set(ids)):
            raise Refused("stable_id_allowlist_required")
        if method == "get_event" and args["id"] not in ids:
            raise Refused("stable_id_not_allowed")
        parent_fd = state_fd
        for part in ("apps", ".host"):
            parent_fd = os.open(part, DIR_FLAGS, dir_fd=parent_fd)
            fds.append(parent_fd)
        read_file(parent_fd, "FIXTURE_ONLY", 2048)
        calendar_fd = os.open("calendar", DIR_FLAGS, dir_fd=parent_fd)
        fds.append(calendar_fd)
        data, metadata = read_file(calendar_fd, "events.json", MAX_BYTES)
        events = parse(data)
        if not isinstance(events, list) or len(events) > 500:
            raise Refused("invalid_calendar_store")
        seen = set()
        prefix = "SPRINT005-ZC05-" + nonce + "-"
        for event in events:
            if not isinstance(event, dict) or set(event) - {"id", "title", "start", "end", "location", "notes", "request_id", "timezone"}:
                raise Refused("invalid_calendar_record")
            if any(not isinstance(event.get(k), str) for k in ("id", "title", "start")) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", event["id"]):
                raise Refused("invalid_calendar_record")
            if not event["title"].startswith(prefix):
                raise Refused("non_synthetic_record_refused")
            if event["id"] in seen:
                raise Refused("ambiguous_calendar_identity")
            seen.add(event["id"])
            if any(k in event and not isinstance(event[k], str) for k in ("location", "notes", "request_id", "timezone")) or (event.get("end") is not None and not isinstance(event["end"], str)):
                raise Refused("invalid_calendar_record")
        if method == "get_event":
            found = next((e for e in events if e["id"] == args["id"]), None)
            result = {"found": found is not None, "event": found}
        else:
            result = {"events": events}
        return {"result": result, "evidence": {
            "kind": "actual_owner_store_readback", "service_api_called": False, "fixture_only": True,
            "case_name": case, "nonce": nonce, "store_sha256": hashlib.sha256(data).hexdigest(),
            "store_bytes": len(data), "store_mtime_ns": metadata.st_mtime_ns,
            "fixture_spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
            "event_count": len(events), "writes": 0, "model_calls": 0, "gui_actions": 0,
        }}
    except OSError:
        # Missing/unreadable store is an error, never evidence of deletion.
        raise Refused("unsafe_missing_or_unreadable_fixture_file") from None
    finally:
        for fd in reversed(fds):
            os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--id")
    args = parser.parse_args()
    try:
        if args.id:
            request = {"owner": "os.calendar", "method": "get_event", "args": {"id": args.id}}
        else:
            data = sys.stdin.buffer.read(16385)
            if len(data) > 16384:
                raise Refused("request_too_large")
            request = parse(data)
        print(json.dumps(readback(args.state_root, request), ensure_ascii=False))
    except Refused as error:
        print(json.dumps({"error": str(error), "service_api_called": False, "writes": 0}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
