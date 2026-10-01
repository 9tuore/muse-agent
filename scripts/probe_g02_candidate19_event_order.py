"""Reproduce and verify the signed package's out-of-order folder event boundary."""

import argparse
import json
import sqlite3
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import muse_goal_store
from muse_goals import GoalService
from probe_g02_candidate05_goal_recovery import FOLDER_REF, open_service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--expect", choices=("old_package", "fixed_source"), required=True)
    args = parser.parse_args()
    workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-c19-event-order-"))
    service, model = open_service(workspace)
    draft = service.handle({"type": "goal_propose", "request_id": "g02-c19-event-order",
                            "text": "监控获授权合成目录变化并写提纲",
                            "context_refs": [{"ref": FOLDER_REF, "purpose": "隔离测试目录"}]})
    approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                               "revision": 1, "decision": "approve",
                               "plan_digest": draft["plan_digest"]})
    assert approved["status"] == "ACTIVE"
    base = datetime.now(timezone.utc)
    time.sleep(0.02)  # Both observations are after approval and before delivery.

    def event(event_id, instant, subject):
        return {"event_id": event_id, "source": "workspace_watcher",
                "observed_at": instant.isoformat(), "topic": "file.changed",
                "payload_ref": FOLDER_REF, "subject": subject,
                "account_scope": "local-workspace"}

    newer_time = base + timedelta(milliseconds=2)
    older_time = base + timedelta(milliseconds=1)
    newer = event("newer", newer_time, "newer.txt")
    older = event("older", older_time, "older.txt")
    first = service.on_event(newer)
    duplicate = service.on_event(newer)
    out_of_order = service.on_event(older)
    restarted = GoalService(workspace, model, service.capabilities)
    replay_after_restart = restarted.on_event(older)
    same_poll = (restarted.on_event(event("same-poll", newer_time, "peer.txt"))
                 if args.expect == "fixed_source" else [])
    with sqlite3.connect("file:" + str(workspace / "memory.sqlite3") + "?mode=ro",
                         uri=True) as db:
        run_rows = db.execute("SELECT event_id,status FROM muse_goal_runs WHERE goal_id=? "
                              "ORDER BY started_at", (draft["goal_id"],)).fetchall()
        event_rows = db.execute("SELECT event_id,observed_at FROM muse_goal_events WHERE goal_id=? "
                                "ORDER BY event_id", (draft["goal_id"],)).fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    statuses = {"newer": [item["status"] for item in first],
                "duplicate": [item["status"] for item in duplicate],
                "older": [item["status"] for item in out_of_order],
                "older_after_restart": [item["status"] for item in replay_after_restart],
                "same_poll": [item["status"] for item in same_poll]}
    common = statuses["newer"] == ["COMPLETED"] and statuses["duplicate"] == [] and (
        statuses["older_after_restart"] == [] and integrity == "ok")
    if args.expect == "old_package":
        passed = common and statuses["older"] == ["COMPLETED"] and len(run_rows) == 2
    else:
        passed = (common and statuses["older"] == [] and statuses["same_poll"] == ["COMPLETED"]
                  and len(run_rows) == 2 and [row[0] for row in event_rows] == ["newer", "same-poll"])
    result = {"status": "PASS" if passed else "FAIL", "expected": args.expect,
              "workspace": str(workspace), "goal_store_module": muse_goal_store.__file__,
              "goal_id": draft["goal_id"], "plan_digest": draft["plan_digest"],
              "approval_id": approved["approval_id"],
              "timestamps": {"newer": newer_time.isoformat(), "older": older_time.isoformat()},
              "statuses": statuses, "run_rows": run_rows, "event_rows": event_rows,
              "model_step_calls": model.calls.count("goal_step"), "sqlite_integrity": integrity}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": result["status"], "expected": args.expect,
                      "statuses": statuses, "run_count": len(run_rows)}, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
