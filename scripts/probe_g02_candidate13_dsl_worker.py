"""Audit three packaged DSL contracts and a read-only capability source receipt."""

import argparse
import copy
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from muse_capability_catalog import CapabilityCatalog
from muse_dsl import DslValidationError, decode_document, encode_document
from muse_goal_store import GoalStore, plan_digest


def worker(resources, workspace, home, events, *, entry="desktop_worker.py"):
    env = dict(os.environ, HOME=str(home), PYTHONPATH=str(resources),
               PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
               GOSIM_LOCAL_INBOX="0",
               LOCAL_MODEL_URL="http://127.0.0.1:9/v1/chat/completions")
    result = subprocess.run(
        [str(resources / "python/bin/python3"), "-B",
         str(resources / entry), str(workspace)],
        input="".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events),
        text=True, capture_output=True, timeout=30, env=env, check=True)
    if result.stderr:
        raise AssertionError("worker_stderr:" + result.stderr[-400:])
    return [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]


def one(replies, status):
    matches = [item for item in replies if item.get("status") == status]
    if len(matches) != 1:
        raise AssertionError({"expected": status, "replies": replies})
    return matches[0]


def rejected(document):
    try:
        encode_document(document)
    except DslValidationError as exc:
        return str(exc)
    raise AssertionError("invalid_document_accepted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_app", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expect-strict", action="store_true")
    args = parser.parse_args()
    resources = args.package_app.resolve(strict=True) / "Contents/Resources"
    assert Path(sys.executable).resolve() == (resources / "python/bin/python3").resolve()
    assert Path(sys.modules["muse_goal_store"].__file__).resolve() == resources / "muse_goal_store.py"
    home = Path(tempfile.mkdtemp(prefix="gosim-g02-c13-dsl-home-"))
    stale_workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-c13-stale-plan-"))
    health_workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-c13-health-receipt-"))
    lifecycle_workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-c13-goal-lifecycle-"))

    recipe = {"query": "Python 3.13", "engine": "python.org", "max_pages": 3,
              "recipe_id": "edge.public_search", "recipe_revision": 1,
              "recipe_digest": "a" * 64, "target_bundle_id": "com.microsoft.edgemac",
              "window_title": "Welcome to Python.org"}
    draft = one(worker(resources, stale_workspace, home, [{
        "type": "goal_propose", "request_id": "g02-c13-stale-plan",
        "text": "用 Edge 浏览器在 python.org 搜索 Python 3.13 并写提纲",
        "browser_recipe": recipe}]), "DRAFT")
    stale_reply = worker(resources, stale_workspace, home, [
        {"type": "goal_decide", "goal_id": draft["goal_id"], "revision": 1,
         "decision": "approve", "plan_digest": "0" * 64},
        {"type": "goal_decide", "goal_id": draft["goal_id"], "revision": 1,
         "decision": "approve"}])
    with sqlite3.connect(stale_workspace / "memory.sqlite3") as db:
        row = db.execute("SELECT spec_json FROM muse_goal_revisions WHERE goal_id=?",
                         (draft["goal_id"],)).fetchone()
        spec = json.loads(row[0])
        spec["objective"] += " 已被外部篡改"
        db.execute("UPDATE muse_goal_revisions SET spec_json=? WHERE goal_id=?",
                   (json.dumps(spec, ensure_ascii=False, sort_keys=True), draft["goal_id"]))
    tampered = one(worker(resources, stale_workspace, home, [{
        "type": "goal_decide", "goal_id": draft["goal_id"], "revision": 1,
        "decision": "approve", "plan_digest": draft["plan_digest"]}]), "REJECTED")
    with sqlite3.connect("file:" + str(stale_workspace / "memory.sqlite3") + "?mode=ro",
                         uri=True) as db:
        stale_status = db.execute("SELECT status FROM muse_goals WHERE goal_id=?",
                                  (draft["goal_id"],)).fetchone()[0]
        approval_count = db.execute("SELECT COUNT(*) FROM muse_goal_approvals WHERE goal_id=?",
                                    (draft["goal_id"],)).fetchone()[0]

    health_draft = one(worker(resources, health_workspace, home, [{
        "type": "goal_propose", "request_id": "g02-c13-health-source",
        "text": "检查 TextEdit 进程健康"}]), "DRAFT")
    generic_negative = None
    if args.expect_strict:
        generic_negative = worker(resources, health_workspace, home, [
            {"type": "goal_decide", "goal_id": health_draft["goal_id"],
             "revision": 1, "decision": "approve"},
            {"type": "goal_decide", "goal_id": health_draft["goal_id"],
             "revision": 1, "decision": "approve", "plan_digest": "0" * 64}])
        with sqlite3.connect("file:" + str(health_workspace / "memory.sqlite3") + "?mode=ro",
                             uri=True) as db:
            generic_approval_count = db.execute(
                "SELECT COUNT(*) FROM muse_goal_approvals WHERE goal_id=?",
                (health_draft["goal_id"],)).fetchone()[0]
    approval_reply = worker(resources, health_workspace, home, [{
        "type": "goal_decide", "goal_id": health_draft["goal_id"], "revision": 1,
        "decision": "approve", "plan_digest": health_draft["plan_digest"]}])
    approved = one(approval_reply, "ACTIVE")
    with sqlite3.connect("file:" + str(health_workspace / "memory.sqlite3") + "?mode=ro",
                         uri=True) as db:
        run_count = db.execute("SELECT COUNT(*) FROM muse_goal_runs WHERE goal_id=?",
                               (health_draft["goal_id"],)).fetchone()[0]
    if run_count == 0:
        worker(resources, health_workspace, home, [{"type": "goal_tick"}])
    with sqlite3.connect("file:" + str(health_workspace / "memory.sqlite3") + "?mode=ro",
                         uri=True) as db:
        db.row_factory = sqlite3.Row
        goal_row = dict(db.execute("SELECT goal_id,revision,status,approval_id,approval_digest "
                                   "FROM muse_goals WHERE goal_id=?",
                                   (health_draft["goal_id"],)).fetchone())
        revision_row = dict(db.execute("SELECT spec_json,digest FROM muse_goal_revisions "
                                       "WHERE goal_id=? AND revision=1",
                                       (health_draft["goal_id"],)).fetchone())
        approval_row = dict(db.execute("SELECT approval_id,digest,scope_json "
                                       "FROM muse_goal_approvals WHERE goal_id=?",
                                       (health_draft["goal_id"],)).fetchone())
        run_row = dict(db.execute("SELECT run_id,approval_id,status,result_json "
                                  "FROM muse_goal_runs WHERE goal_id=?",
                                  (health_draft["goal_id"],)).fetchone())
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    goal = GoalStore(health_workspace).get(health_draft["goal_id"])
    goal_dsl = goal["dsl"]
    catalog = CapabilityCatalog(health_workspace)
    capability = catalog.get("system.app_health", goal_dsl["scope"])
    run = json.loads(run_row["result_json"])
    receipt = one(run["receipts"], "COMPLETED")
    scope = json.loads(approval_row["scope_json"])
    spec = json.loads(revision_row["spec_json"])
    capability_doc = capability["document"]
    wrong_adapter = copy.deepcopy(capability_doc)
    wrong_adapter["payload"]["adapter"] = "shell.exec"
    wrong_scope = dict(goal_dsl["scope"], account="foreign-fixture")

    now = datetime.now(timezone.utc).isoformat()
    memory = {
        "schema_version": "muse.dsl/1", "kind": "memory", "id": "memory:g02:c13",
        "revision": 1, "scope": goal_dsl["scope"],
        "created_at": now, "updated_at": now,
        "origin": {"type": "user", "ref": "request:g02-c13"},
        "payload": {"subject_id": "entity:g02-c13", "predicate": "fixture_claim",
                    "value": "synthetic", "epistemic_type": "external_claim",
                    "source_ids": ["source:g02-c13"], "observed_at": now,
                    "valid_from": None, "valid_until": None,
                    "relations": [], "deleted": False},
    }
    missing_source = copy.deepcopy(memory)
    missing_source["payload"]["source_ids"] = []
    forged_approval = copy.deepcopy(goal_dsl)
    forged_approval["approved"] = True

    first_draft = one(worker(resources, lifecycle_workspace, home, [{
        "type": "goal_propose", "request_id": "g02-c13-stream-restart",
        "text": "检查 TextEdit 进程健康"}], entry="agent_app.py"), "DRAFT")
    first_control = worker(resources, lifecycle_workspace, home, [
        {"type": "goal_decide", "goal_id": first_draft["goal_id"], "revision": 1,
         "decision": "approve", "plan_digest": first_draft["plan_digest"]},
        {"type": "goal_control", "goal_id": first_draft["goal_id"], "action": "pause"}],
        entry="agent_app.py")
    resumed = worker(resources, lifecycle_workspace, home, [
        {"type": "goal_get", "goal_id": first_draft["goal_id"]},
        {"type": "goal_tick"},
        {"type": "goal_control", "goal_id": first_draft["goal_id"], "action": "resume"},
        {"type": "goal_tick"}], entry="agent_app.py")
    cancel_draft = one(worker(resources, lifecycle_workspace, home, [{
        "type": "goal_propose", "request_id": "g02-c13-stream-cancel",
        "text": "检查 TextEdit 进程健康"}], entry="agent_app.py"), "DRAFT")
    cancelled = worker(resources, lifecycle_workspace, home, [
        {"type": "goal_decide", "goal_id": cancel_draft["goal_id"], "revision": 1,
         "decision": "approve", "plan_digest": cancel_draft["plan_digest"]},
        {"type": "goal_control", "goal_id": cancel_draft["goal_id"], "action": "cancel"}],
        entry="agent_app.py")
    after_cancel_restart = worker(resources, lifecycle_workspace, home, [
        {"type": "goal_get", "goal_id": cancel_draft["goal_id"]},
        {"type": "goal_tick"}], entry="agent_app.py")
    with sqlite3.connect("file:" + str(lifecycle_workspace / "memory.sqlite3") + "?mode=ro",
                         uri=True) as db:
        lifecycle_rows = db.execute(
            "SELECT goal_id,status,run_count,next_due,pending_event_id FROM muse_goals "
            "WHERE goal_id IN (?,?) ORDER BY goal_id",
            (first_draft["goal_id"], cancel_draft["goal_id"])).fetchall()
    lifecycle_by_id = {row[0]: row[1:] for row in lifecycle_rows}
    checks = {
        "wrong_or_missing_review_digest_rejected":
            len(stale_reply) == 2 and all(item.get("error") == "plan_digest_required_or_changed"
                                          for item in stale_reply),
        "tampered_plan_rejected": tampered.get("status") == "REJECTED" and
            stale_status == "draft" and approval_count == 0,
        "three_dsl_roundtrips": all(decode_document(encode_document(document)) == document
                                    for document in (goal_dsl, memory, capability_doc)),
        "dsl_authority_injection_rejected":
            rejected(forged_approval) == "envelope_fields_invalid" and
            rejected(missing_source) == "source_required" and
            rejected(wrong_adapter) == "untrusted_adapter",
        "goal_approval_persisted": goal_row["status"] == run_row["status"] == "completed" and
            health_draft["plan_digest"] == revision_row["digest"] ==
            goal_row["approval_digest"] == approval_row["digest"] == plan_digest(spec) and
            goal_row["approval_id"] == approved["approval_id"] ==
            approval_row["approval_id"] == run_row["approval_id"] and
            scope == {key: spec[key] for key in ("permissions", "budget", "deadline", "verification")},
        "capability_catalog_binding":
            capability["enabled"] and capability_doc["payload"]["adapter"] ==
            "builtin.system.app_health.v1" and
            hashlib.sha256(encode_document(capability_doc).encode()).hexdigest() == capability["digest"] and
            catalog.get("system.app_health", wrong_scope) is None and
            not catalog.approve("system.app_health", 2, capability["digest"], goal_dsl["scope"],
                                trusted_adapters=frozenset({"builtin.system.app_health.v1"})),
        "source_receipt_bound_to_goal":
            run["status"] == "COMPLETED" and receipt["capability"] == "system.app_health" and
            receipt["action_id"] == run_row["run_id"] + ":check_textedit" and
            receipt["output"]["bundle_id"] == "com.apple.TextEdit" and
            receipt["verification"] == {"source": "NSRunningApplication", "read_only": True,
                                        "shell_used": False} and
            receipt["evidence"]["source"] == "local_appkit" and
            spec["permissions"]["resource_refs"] == ["app:com.apple.TextEdit"],
        "pause_resume_restart_worker_stream":
            [item["status"] for item in first_control] == ["ACTIVE", "PAUSED"] and
            [item["status"] for item in resumed] == ["PAUSED", "READY", "ACTIVE", "READY"] and
            resumed[1]["results"] == [] and
            [item["status"] for item in resumed[3]["results"]] == ["COMPLETED"] and
            lifecycle_by_id[first_draft["goal_id"]][1] == 1,
        "cancel_restart_worker_stream":
            [item["status"] for item in cancelled] == ["ACTIVE", "CANCELLED"] and
            [item["status"] for item in after_cancel_restart] == ["CANCELLED", "READY"] and
            after_cancel_restart[1]["results"] == [] and
            lifecycle_by_id[cancel_draft["goal_id"]] == ("cancelled", 0, None, None),
        "sqlite_integrity": integrity == "ok",
    }
    if args.expect_strict:
        checks["generic_missing_or_wrong_digest_rejected"] = (
            len(generic_negative) == 2 and
            all(item.get("status") == "REJECTED" and
                item.get("error") == "plan_digest_required_or_changed"
                for item in generic_negative) and generic_approval_count == 0)
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "approval_type": "synthetic_host_decision_fixture",
        "runtime": {"python": sys.executable, "goal_store": sys.modules["muse_goal_store"].__file__,
                    "worker": str(resources / "desktop_worker.py"),
                    "model": "disabled_local_url", "gui_focus": "not_requested"},
        "workspaces": {"home": str(home), "stale_plan": str(stale_workspace),
                       "health": str(health_workspace), "lifecycle": str(lifecycle_workspace)},
        "checks": checks,
        "stale_plan": {"draft_digest": draft["plan_digest"],
                       "wrong_or_missing": [item.get("error") for item in stale_reply],
                       "tampered_status": tampered["status"],
                       "approval_count": approval_count},
        "generic_digest_negative": (
            {"errors": [item.get("error") for item in generic_negative],
             "approval_count_before_correct_decision": generic_approval_count}
            if args.expect_strict else None),
        "goal": {"goal_id": goal_row["goal_id"], "plan_digest": revision_row["digest"],
                 "approval_id": goal_row["approval_id"], "run_id": run_row["run_id"],
                 "status": goal_row["status"]},
        "capability": {"id": capability_doc["id"], "revision": capability_doc["revision"],
                       "digest": capability["digest"], "adapter": capability_doc["payload"]["adapter"]},
        "receipt": {"action_id": receipt["action_id"], "capability": receipt["capability"],
                    "output": receipt["output"], "verification": receipt["verification"],
                    "evidence": receipt["evidence"]},
        "lifecycle": {"paused_before_restart": first_control[-1]["status"],
                       "resumed_run": [item["status"] for item in resumed[-1]["results"]],
                       "cancelled_after_restart": after_cancel_restart[0]["status"],
                       "cancelled_run_count": lifecycle_by_id[cancel_draft["goal_id"]][1]},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
