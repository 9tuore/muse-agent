"""Authorize a planned capability against the current Goal run before execution."""

from __future__ import annotations

import json
import fcntl
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from muse_goal_store import GoalStore, plan_digest
from muse_search_policy import select_results


class ApprovedActionBus:
    def __init__(self, workspace: Path, executor: Any, *, gui_lock_path: Path | None = None):
        self.store = GoalStore(workspace)
        self.executor = executor
        self.gui_lock_path = gui_lock_path or Path("/tmp/gosim-muse-5agent-20260928/gui.lock")
        with self.store._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS muse_action_receipts ("
                       "action_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, "
                       "capability TEXT NOT NULL, receipt_json TEXT NOT NULL)")

    def execute(self, call: dict, *, approved: bool, context: dict | None = None) -> dict:
        call = call if isinstance(call, dict) else {}
        context = context if isinstance(context, dict) else {}
        base = {"ok": False, "status": "BLOCKED_AUTHORIZATION",
                "action_id": call.get("action_id"), "capability": call.get("capability"),
                "output": {}, "verification": {}, "evidence": {}}

        def reject(reason: str) -> dict:
            return dict(base, error=reason)

        if approved is not True:
            return reject("host_approval_required")
        goal_id, revision = call.get("goal_id"), call.get("revision")
        action_id, capability, args = call.get("action_id"), call.get("capability"), call.get("args")
        if (not isinstance(goal_id, str) or not goal_id or type(revision) is not int or revision < 1
                or not isinstance(action_id, str) or not isinstance(capability, str)
                or not isinstance(args, dict)):
            return reject("invalid_action_call")
        try:
            with sqlite3.connect(str(self.store.path), timeout=30) as db:
                db.row_factory = sqlite3.Row
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT g.status AS goal_status,g.revision,g.run_id,g.approval_id,"
                    "g.approval_digest,g.approval_expires_at,r.status AS run_status,"
                    "r.revision AS run_revision,r.approval_id AS run_approval_id,"
                    "a.digest AS approved_digest,a.scope_json,a.expires_at AS approved_until,"
                    "p.digest AS revision_digest,p.spec_json "
                    "FROM muse_goals g JOIN muse_goal_runs r ON r.run_id=g.run_id "
                    "JOIN muse_goal_approvals a ON a.approval_id=g.approval_id "
                    "JOIN muse_goal_revisions p ON p.goal_id=g.goal_id AND p.revision=g.revision "
                    "WHERE g.goal_id=?", (goal_id,)).fetchone()
                if row is None or row["goal_status"] != "running" or row["run_status"] != "running":
                    return reject("run_not_active")
                run_id = row["run_id"]
                if (row["revision"] != revision or row["run_revision"] != revision
                        or context.get("run_id", run_id) != run_id):
                    return reject("run_revision_changed")
                if (context.get("approval_id") != row["approval_id"]
                        or row["run_approval_id"] != row["approval_id"]):
                    return reject("approval_mismatch")
                spec = json.loads(row["spec_json"])
                digest = plan_digest(spec)
                if (context.get("plan_digest") != digest or row["approval_digest"] != digest
                        or row["approved_digest"] != digest or row["revision_digest"] != digest):
                    return reject("plan_changed")
                now = datetime.now(timezone.utc)
                if any(datetime.fromisoformat(row[field]) <= now for field in
                       ("approval_expires_at", "approved_until")):
                    return reject("approval_expired")
                deadline = spec.get("deadline")
                if deadline and datetime.fromisoformat(deadline.replace("Z", "+00:00")) <= now:
                    return reject("goal_deadline_reached")
                scope = json.loads(row["scope_json"])
                expected_scope = {key: spec[key] for key in ("permissions", "budget", "deadline", "verification")}
                if (scope != expected_scope or context.get("permissions") != spec["permissions"]
                        or context.get("budget") != spec["budget"]):
                    return reject("approval_scope_changed")
                prefix = run_id + ":"
                if not action_id.startswith(prefix):
                    return reject("action_outside_run")
                step_id = action_id[len(prefix):]
                steps = [step for step in spec["steps"] if step.get("id") == step_id]
                if len(steps) != 1 or steps[0].get("capability") != capability:
                    return reject("action_outside_plan")
                planned = steps[0].get("args")
                if not isinstance(planned, dict):
                    return reject("action_args_changed")
                if "url_from_step" in planned:
                    search_id, rank = planned["url_from_step"], planned["selected_rank"]
                    search_steps = [step for step in spec["steps"]
                                    if step.get("id") == search_id and step.get("capability") == "web.search"]
                    if capability != "web.read" or len(search_steps) != 1:
                        return reject("search_binding_invalid")
                    prior = db.execute("SELECT receipt_json FROM muse_action_receipts "
                                       "WHERE action_id=? AND run_id=? AND capability='web.search'",
                                       (prefix + search_id, run_id)).fetchone()
                    if prior is None:
                        return reject("search_receipt_missing")
                    search_receipt = json.loads(prior["receipt_json"])
                    selected = select_results(search_steps[0]["args"]["query"],
                                              search_receipt["output"].get("results"), limit=5)
                    if (type(rank) is not int or not 0 <= rank < 5 or len(selected) <= rank or
                            args != {"url": selected[rank]["url"]}):
                        return reject("action_args_changed")
                elif not self._args_match(planned, args):
                    return reject("action_args_changed")
                if capability == "web.search":
                    prior = db.execute("SELECT receipt_json FROM muse_action_receipts "
                                       "WHERE action_id=? AND run_id=? AND capability='web.search'",
                                       (action_id, run_id)).fetchone()
                    if prior is not None:
                        return json.loads(prior["receipt_json"])
                trusted_context = dict(context, permissions=spec["permissions"], budget=spec["budget"],
                                       approval_id=row["approval_id"], plan_digest=digest, run_id=run_id)
                trusted_context.pop("step_outputs", None)
                trusted_context.pop("gui_control_granted", None)
                trusted_context.pop("allowed_domains", None)
                if capability in {"browser.research", "app.recipe"}:
                    refs = spec["permissions"].get("resource_refs", [])
                    if capability == "browser.research":
                        if (capability not in spec["permissions"].get("capabilities", []) or
                                not {"app:com.microsoft.edgemac", "site:python.org"} <= set(refs)):
                            return reject("browser_scope_not_approved")
                        trusted_context["allowed_domains"] = ["python.org"]
                    else:
                        relative_path, window_title = args.get("relative_path"), args.get("window_title")
                        if (capability not in spec["permissions"].get("capabilities", []) or
                                args.get("target_bundle_id") != "com.apple.TextEdit" or
                                not isinstance(relative_path, str) or not isinstance(window_title, str) or
                                not {"app:com.apple.TextEdit", "resource:workspace/" + relative_path,
                                     "window:com.apple.TextEdit:" + window_title} <= set(refs)):
                            return reject("textedit_scope_not_approved")
                    lock_dir = self.gui_lock_path.parent
                    lock_dir.mkdir(mode=0o700, exist_ok=True)
                    fd = os.open(str(self.gui_lock_path), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
                    locked = False
                    try:
                        try:
                            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            locked = True
                        except BlockingIOError:
                            return reject("gui_resource_busy")
                        os.ftruncate(fd, 0)
                        os.write(fd, json.dumps({"resource": "gui", "owner": "Muse worker",
                                                 "purpose": "approved " + capability, "pid": os.getpid()}).encode())
                        trusted_context["gui_control_granted"] = True
                        receipt = self.executor.execute(call, approved=True, context=trusted_context)
                    finally:
                        if locked:
                            os.ftruncate(fd, 0)
                        os.close(fd)
                else:
                    receipt = self.executor.execute(call, approved=True, context=trusted_context)
                if capability == "web.search" and isinstance(receipt, dict) and receipt.get("ok"):
                    encoded = json.dumps(receipt, ensure_ascii=False, sort_keys=True)
                    if len(encoded.encode("utf-8")) > 128 * 1024:
                        return reject("search_receipt_too_large")
                    db.execute("INSERT INTO muse_action_receipts VALUES (?,?,?,?)",
                               (action_id, run_id, capability, encoded))
                return receipt
        except (sqlite3.Error, OSError, ValueError, TypeError, KeyError) as exc:
            return reject("authority_unavailable:" + type(exc).__name__)

    @staticmethod
    def _args_match(planned: dict, actual: dict) -> bool:
        dynamic = {"content_from_step": "content", "sources_from_step": "sources",
                   "sources_from_steps": "sources",
                   "versioned_max": "relative_path"}
        allowed = set(planned) - set(dynamic)
        allowed.update(dynamic[key] for key in dynamic if key in planned)
        if set(actual) != allowed:
            return False
        for key, value in planned.items():
            if key in dynamic or (key == "relative_path" and "versioned_max" in planned):
                continue
            if actual.get(key) != value:
                return False
        return True
