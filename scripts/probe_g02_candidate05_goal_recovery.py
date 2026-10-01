"""Isolated multi-process Goal lifecycle probe using the selected package's Python modules."""

import argparse
import hashlib
import json
import sqlite3
import sys
sys.dont_write_bytecode = True
from datetime import datetime, timezone
from pathlib import Path

import muse_action_bus
import muse_goals
from muse_action_bus import ApprovedActionBus
from muse_capabilities import CapabilityExecutor, register_builtin_catalog
from muse_capability_catalog import CapabilityCatalog
from muse_goals import GoalService


REQUEST_ID = "g02-candidate05-recovery"
REJECTED_ID = "g02-candidate05-rejected"
FOLDER_REF = "resource:folder-g02-synthetic"


class FixtureModel:
    """Local deterministic substitute; this probe does not call a model service."""

    def __init__(self):
        self.calls = []

    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        self.calls.append(purpose)
        if purpose == "goal_plan":
            spec = {
                "schema_version": "muse.goal/0.1", "goal_id": "model-id", "revision": 1,
                "title": "合成目录恢复测试", "objective": "记录获授权合成目录的变动",
                "priority": "normal", "deadline": None, "timezone": "Asia/Shanghai",
                "triggers": [{"kind": "interval", "every_seconds": 60},
                             {"kind": "event", "topic": "file.changed", "source_ref": FOLDER_REF}],
                "context_refs": [{"ref": FOLDER_REF, "purpose": "隔离测试目录"}],
                "steps": [{"id": "compose", "capability": "model.compose",
                           "args": {"instruction": "仅按已批准的合成事件写中文提纲"}},
                          {"id": "save", "capability": "workspace.write_artifact",
                           "args": {"relative_path": "notes/Muse-Recovery-Probe.md",
                                    "content_from_step": "compose", "versioned_max": 3},
                           "input_refs": ["step:compose"]}],
                "permissions": {"capabilities": ["model.compose", "workspace.write_artifact"],
                                "resource_refs": [FOLDER_REF] + [
                                    f"resource:workspace/notes/Muse-Recovery-Probe-v{number}.md"
                                    for number in (1, 2, 3)],
                                "send_message": "deny", "send_rule_ref": None, "cloud_context": "none"},
                "budget": {"period": "goal", "money": {"mode": "capped", "currency": "CNY", "amount": 0},
                           "max_model_tokens": 2000, "max_searches": 0, "max_run_seconds": 60},
                "verification": [{"type": "file_content", "target_ref": "step:save",
                                  "expected": {"nonempty": True, "sections": ["提纲"]}}],
                "notify": {"on_major_update": True, "on_need_decision": True, "on_complete": True},
                "failure_policy": {"max_retries": 0, "escalate": True},
            }
            text = json.dumps(spec, ensure_ascii=False)
        elif purpose == "goal_step":
            text = "提纲\n1. 记录本次获授权的合成目录变化。\n2. 保留运行收据供用户核对。\n"
        else:
            raise AssertionError("unexpected_model_purpose:" + purpose)
        return {"ok": True, "status": "COMPLETED", "text": text,
                "provider": "fixture", "model": "deterministic", "route": "local",
                "usage": {"total_tokens": 12}}


def open_service(workspace):
    model = FixtureModel()
    catalog = CapabilityCatalog(workspace)
    register_builtin_catalog(catalog)
    bus = ApprovedActionBus(workspace, CapabilityExecutor(workspace, catalog=catalog))
    return GoalService(workspace, model, bus), model


def rows(workspace, goal_id):
    with sqlite3.connect(str(workspace / "memory.sqlite3")) as db:
        db.row_factory = sqlite3.Row
        goal = dict(db.execute("SELECT goal_id,revision,status,approval_id,run_count,next_due,pending_event_id "
                               "FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone())
        runs = [dict(row) for row in db.execute(
            "SELECT run_id,status,trigger_kind,event_id,approval_id FROM muse_goal_runs "
            "WHERE goal_id=? ORDER BY started_at,run_id", (goal_id,))]
        events = [dict(row) for row in db.execute(
            "SELECT event_id,observed_at FROM muse_goal_events WHERE goal_id=? ORDER BY event_id", (goal_id,))]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    return {"goal": goal, "runs": runs, "events": events, "integrity": integrity}


def artifact(workspace, version):
    path = workspace / f"notes/Muse-Recovery-Probe-v{version}.md"
    data = path.read_bytes()
    return {"relative_path": str(path.relative_to(workspace)), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "contains_outline": "提纲" in data.decode("utf-8")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "resume", "dedupe_cancel", "verify_cancel_restart"))
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    service, model = open_service(workspace)
    if args.phase == "prepare":
        event = {"type": "goal_propose", "request_id": REQUEST_ID,
                 "text": "监控获授权合成目录变化并写提纲",
                 "context_refs": [{"ref": FOLDER_REF, "purpose": "隔离测试目录"}]}
        draft = service.handle(event)
        stale = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                "revision": 2, "decision": "approve",
                                "plan_digest": draft["plan_digest"]})
        approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                   "revision": 1, "decision": "approve",
                                   "plan_digest": draft["plan_digest"]})
        paused = service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                 "action": "pause"})
        rejected_draft = service.handle(dict(event, request_id=REJECTED_ID))
        rejected = service.handle({"type": "goal_decide", "goal_id": rejected_draft["goal_id"],
                                   "revision": 1, "decision": "reject"})
        result = {"phase": args.phase, "draft": draft["status"], "stale_approval": stale["status"],
                  "approved": approved["status"], "paused": paused["status"],
                  "rejected_plan": rejected["status"], "tick_while_paused": service.tick(),
                  "artifact_before_resume": (workspace / "notes/Muse-Recovery-Probe-v1.md").exists(),
                  "rows": rows(workspace, draft["goal_id"]), "model_calls": model.calls}
    else:
        goal = service.store.by_request(REQUEST_ID)
        if goal is None:
            raise RuntimeError("prepared_goal_missing")
        goal_id = goal["goal_id"]
        if args.phase == "resume":
            before = service.handle({"type": "goal_get", "goal_id": goal_id})
            rejected = service.store.by_request(REJECTED_ID)
            resumed = service.handle({"type": "goal_control", "goal_id": goal_id,
                                      "action": "resume"})
            scheduled = service.tick()
            after_tick = rows(workspace, goal_id)
            old_event = {"event_id": "g02-event-before-approval", "source": "fixture",
                         "observed_at": "2020-01-01T00:00:00+00:00", "topic": "file.changed",
                         "payload_ref": FOLDER_REF, "subject": "old.txt"}
            stale_event = service.on_event(old_event)
            event = {"event_id": "g02-event-1", "source": "fixture",
                     "observed_at": datetime.now(timezone.utc).isoformat(), "topic": "file.changed",
                     "payload_ref": FOLDER_REF, "subject": "synthetic.txt"}
            triggered = service.on_event(event)
            result = {"phase": args.phase, "status_before_restart": before["status"],
                      "rejected_plan_after_restart": rejected["status"], "resumed": resumed["status"],
                      "scheduled_status": [item["status"] for item in scheduled],
                      "stale_event_results": stale_event,
                      "event_status": [item["status"] for item in triggered],
                      "first_artifact": artifact(workspace, 1),
                      "second_artifact": artifact(workspace, 2),
                      "rows_after_tick": after_tick, "rows": rows(workspace, goal_id),
                      "model_calls": model.calls}
        elif args.phase == "dedupe_cancel":
            event = {"event_id": "g02-event-1", "source": "fixture",
                     "observed_at": datetime.now(timezone.utc).isoformat(), "topic": "file.changed",
                     "payload_ref": FOLDER_REF, "subject": "synthetic.txt"}
            duplicate = service.on_event(event)
            cancelled = service.handle({"type": "goal_control", "goal_id": goal_id,
                                        "action": "cancel"})
            after_cancel = service.tick()
            result = {"phase": args.phase, "duplicate_event_results": duplicate,
                      "cancelled": cancelled["status"], "tick_after_cancel": after_cancel,
                      "third_artifact_exists": (workspace / "notes/Muse-Recovery-Probe-v3.md").exists(),
                      "first_artifact": artifact(workspace, 1),
                      "second_artifact": artifact(workspace, 2),
                      "rows": rows(workspace, goal_id), "model_calls": model.calls}
        else:
            before = rows(workspace, goal_id)
            late_event = {"event_id": "g02-event-after-cancel", "source": "fixture",
                          "observed_at": datetime.now(timezone.utc).isoformat(), "topic": "file.changed",
                          "payload_ref": FOLDER_REF, "subject": "late.txt"}
            result = {"phase": args.phase,
                      "status_after_restart": service.handle({"type": "goal_get", "goal_id": goal_id})["status"],
                      "tick_after_restart": service.tick(),
                      "event_after_cancel": service.on_event(late_event),
                      "third_artifact_exists": (workspace / "notes/Muse-Recovery-Probe-v3.md").exists(),
                      "first_artifact": artifact(workspace, 1),
                      "second_artifact": artifact(workspace, 2),
                      "rows_before": before, "rows_after": rows(workspace, goal_id),
                      "model_calls": model.calls}
    result["runtime"] = {"python": sys.executable, "goal_module": muse_goals.__file__,
                         "action_bus_module": muse_action_bus.__file__,
                         "model": "deterministic_fixture", "event_source": "fixture"}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
