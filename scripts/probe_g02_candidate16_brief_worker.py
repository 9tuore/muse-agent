"""Audit candidate16 Brief delivery with its bundled worker and synthetic Goal source."""

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from muse_capabilities import CapabilityExecutor
from muse_goals import GoalService


SOURCE_URL = "https://example.test/brief"


class FixtureModel:
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            content = json.dumps({
                "title": "合成公开页变化", "objective": "持续整理获授权网址的变化",
                "kind": "research", "artifact": "notes/research.md",
                "content": "初稿", "interval_seconds": 60,
            }, ensure_ascii=False)
        else:
            content = "提纲：根据隔离来源记录已验证的页面变化。"
        return {"ok": True, "status": "COMPLETED", "text": content,
                "provider": "fixture", "model": "fixture", "usage": {"total_tokens": 20}}


class FixtureExecutor:
    def __init__(self, workspace):
        self.real = CapabilityExecutor(workspace)
        self.body = "版本一：合成资料"
        self.reads = 0

    def execute(self, call, *, approved, context=None):
        if call["capability"] == "web.read":
            self.reads += 1
            return {"ok": True, "status": "COMPLETED", "capability": "web.read",
                    "output": {"title": "合成公开页", "text": self.body,
                               "source_url": SOURCE_URL,
                               "retrieved_at": datetime.now(timezone.utc).isoformat(),
                               "content_sha256": hashlib.sha256(self.body.encode()).hexdigest()}}
        return self.real.execute(call, approved=approved, context=context)


def worker(resources, workspace, home, events, *, dwell=2.6):
    env = dict(os.environ, HOME=str(home), PYTHONPATH=str(resources),
               PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
               LOCAL_MODEL_URL="http://127.0.0.1:9/v1/chat/completions",
               GOSIM_LOCAL_INBOX="0")
    command = [str(resources / "python/bin/python3"), "-B",
               str(resources / "desktop_worker.py"), str(workspace)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, env=env)
    for event in events:
        process.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
    process.stdin.flush()
    time.sleep(dwell)
    process.stdin.close()
    process.stdin = None
    out, err = process.communicate(timeout=20)
    if process.returncode != 0 or err:
        raise AssertionError({"exit_code": process.returncode, "stderr": err[-600:]})
    return [json.loads(line) for line in out.splitlines() if line.startswith("{")]


def one(items, status, *, reason=None):
    matches = [item for item in items if item.get("status") == status and
               (reason is None or item.get("reason") == reason)]
    if not matches:
        raise AssertionError({"missing_status": status, "reason": reason, "observed": items})
    return matches[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_app", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    resources = args.package_app.resolve(strict=True) / "Contents/Resources"
    assert Path(sys.executable).resolve() == (resources / "python/bin/python3").resolve()
    assert Path(sys.modules["muse_goals"].__file__).resolve() == resources / "muse_goals.py"
    workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-c16-brief-workspace-"))
    home = Path(tempfile.mkdtemp(prefix="gosim-g02-c16-brief-home-"))

    executor = FixtureExecutor(workspace)
    goal = GoalService(workspace, FixtureModel(), executor)
    draft = goal.handle({"type": "goal_propose", "request_id": "g02-c16-brief-source",
                         "text": "持续整理 " + SOURCE_URL})
    assert draft["status"] == "DRAFT", draft
    approved = goal.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": draft["revision"], "decision": "approve",
                            "plan_digest": draft["plan_digest"]})
    assert approved["status"] == "ACTIVE", approved
    base = datetime.now(timezone.utc) + timedelta(seconds=1)
    first_run = goal.tick(base)[0]
    assert first_run["status"] == "COMPLETED" and first_run["verification"] == "CHECKS_PASSED", first_run

    initial = worker(resources, workspace, home, [
        {"type": "brief_settings_get"}, {"type": "brief_tick"},
        {"type": "brief_settings_set", "settings": {"brief_mode": "custom", "brief_local_time": "00:00"}},
        {"type": "brief_tick"},
    ])
    off = one(initial, "NO_CHANGE", reason="brief_off")
    settings = one(initial, "SAVED")
    initial_no_change = one(initial, "NO_CHANGE", reason="no_verified_updates")
    default = one(initial, "READY")["brief_settings"]

    same_run = goal.tick(base + timedelta(seconds=61))[0]
    assert same_run["status"] == "NO_CHANGE" and same_run["notify"] is False, same_run
    no_change = worker(resources, workspace, home, [{"type": "brief_tick"}])
    silent = one(no_change, "NO_CHANGE", reason="no_verified_updates")

    executor.body = "版本二：合成资料有真实内容变化"
    changed_run = goal.tick(base + timedelta(seconds=122))[0]
    assert changed_run["status"] == "COMPLETED" and changed_run["verification"] == "CHECKS_PASSED", changed_run
    ready_events = worker(resources, workspace, home, [])
    ready = one(ready_events, "BRIEF_READY", reason=None)
    replay_events = worker(resources, workspace, home, [])
    replay = next(item for item in replay_events if item.get("status") == "BRIEF_READY"
                  and item.get("replayed") is True)
    brief_id = ready["brief"]["brief_id"]
    ack_events = worker(resources, workspace, home, [
        {"type": "brief_ack", "brief_id": brief_id}, {"type": "brief_tick"},
    ])
    acknowledged = one(ack_events, "ACKNOWLEDGED")
    ack_no_change = one(ack_events, "NO_CHANGE", reason="already_delivered")
    post_ack_auto = worker(resources, workspace, home, [])
    after_ack = worker(resources, workspace, home, [{"type": "brief_tick"}])
    delivered = one(after_ack, "NO_CHANGE", reason="already_delivered")

    db_path = workspace / "memory.sqlite3"
    with sqlite3.connect("file:" + str(db_path) + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        runs = [dict(row) for row in db.execute(
            "SELECT run_id,status,finished_at,result_json FROM muse_goal_runs ORDER BY finished_at")]
        deliveries = [dict(row) for row in db.execute(
            "SELECT local_day,brief_id,status,payload_json FROM muse_brief_deliveries")]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    artifact_readbacks = []
    for run in (first_run, changed_run):
        receipt = next(item for item in run["receipts"]
                       if item["capability"] == "workspace.write_artifact")
        relative_path = receipt["output"]["relative_path"]
        actual_sha = hashlib.sha256((workspace / relative_path).read_bytes()).hexdigest()
        artifact_readbacks.append({"relative_path": relative_path,
                                   "receipt_sha256": receipt["output"]["sha256"],
                                   "disk_sha256": actual_sha})
    brief = ready["brief"]
    checks = {
        "default_off_and_user_enabled": default["brief_mode"] == "off" and
            off["reason"] == "brief_off" and settings["brief_settings"]["brief_mode"] == "custom" and
            initial_no_change["reason"] == "no_verified_updates",
        "no_change_not_reported": same_run["status"] == "NO_CHANGE" and not same_run["notify"] and
            silent["reason"] == "no_verified_updates" and
            not any(item.get("status") == "BRIEF_READY" for item in initial + no_change),
        "verified_change_only": changed_run["status"] == "COMPLETED" and
            changed_run["verification"] == "CHECKS_PASSED" and
            len(brief["verified_updates"]) == 1 and
            brief["verified_updates"][0]["run_id"] == changed_run["run_id"] and
            brief["verified_updates"][0]["source_urls"] == [SOURCE_URL] and
            all(item["run_id"] != same_run["run_id"] for item in brief["verified_updates"]),
        "restart_replays_exact_id": replay["brief"]["brief_id"] == brief_id and
            replay["brief"] == brief and replay["replayed"] is True,
        "ack_stops_repeats": acknowledged["ok"] and ack_no_change["reason"] == "already_delivered" and
            delivered["reason"] == "already_delivered" and
            not any(item.get("status") == "BRIEF_READY" for item in post_ack_auto) and
            not any(item.get("status") == "BRIEF_READY" for item in after_ack),
        "persisted_verification": [json.loads(row["result_json"])["status"] for row in runs] ==
            ["COMPLETED", "NO_CHANGE", "COMPLETED"] and len(deliveries) == 1 and
            deliveries[0]["brief_id"] == brief_id and deliveries[0]["status"] == "delivered" and
            integrity == "ok" and executor.reads == 3 and
            all(item["receipt_sha256"] == item["disk_sha256"] for item in artifact_readbacks) and
            artifact_readbacks[0]["disk_sha256"] != artifact_readbacks[1]["disk_sha256"],
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL", "classification": "PASS_LOCAL_FIXTURE",
        "package_app": str(args.package_app), "workspace": str(workspace), "home": str(home),
        "checks": checks,
        "goal": {"goal_id": draft["goal_id"], "approval_id": approved["approval_id"],
                 "plan_digest": draft["plan_digest"],
                 "run_statuses": [first_run["status"], same_run["status"], changed_run["status"]],
                 "run_ids": [first_run["run_id"], same_run["run_id"], changed_run["run_id"]],
                 "source_url": SOURCE_URL, "source_reads": executor.reads,
                 "source_changes": [first_run["source_changes"], same_run["source_changes"],
                                    changed_run["source_changes"]],
                 "artifact_readbacks": artifact_readbacks},
        "brief": {"default_mode": default["brief_mode"],
                  "enabled_mode": settings["brief_settings"]["brief_mode"],
                  "pre_change_reasons": [initial_no_change["reason"], silent["reason"]],
                  "brief_id": brief_id, "verified_run_id": brief["verified_updates"][0]["run_id"],
                  "ready_replayed": ready["replayed"], "restart_replayed": replay["replayed"],
                  "ack_status": acknowledged["status"], "after_ack_reason": delivered["reason"],
                  "delivery_rows": len(deliveries)},
        "external_services": {"web_fetch": "NOT_USED", "paid_model": "NOT_USED",
                              "gui": "NOT_USED"},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
