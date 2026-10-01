"""Bind one official Octos MCP call to a reviewed Muse Goal and native decision.

The stdio MCP child can only queue a request and wait. It cannot approve a Goal
or reach ApprovedActionBus. The native host must supply a separate, verified
click witness to ``decide_from_native``; the default guard denies everything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from muse_goal_store import GoalStore, iso, plan_digest, utc_now


TOOL_NAME = "muse_goal_step"
WAIT_SECONDS = 45
META_KEYS = ("muse_host_session_id", "muse_host_turn_id",
             "muse_host_tool_call_id", "muse_host_call_nonce")


def _result(status: str, *, error: str | None = None, **fields: Any) -> dict:
    body = {"status": status, **fields}
    if error:
        body["error"] = error
    return {"content": [{"type": "text", "text": json.dumps(body, ensure_ascii=False,
                                                             sort_keys=True)}],
            "isError": status != "COMPLETED"}


def _readback(workspace: Path, relative_path: str, limit: int = 64 * 1024) -> bytes:
    """Read an approved artifact without following a symlink in any component."""
    parts = relative_path.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("readback_path_invalid")
    directory = os.open(str(workspace), os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            return os.read(fd, limit + 1)
        finally:
            os.close(fd)
    finally:
        os.close(directory)


class OfficialGoalBridge:
    """Shared SQLite handoff between the official MCP child and Muse native host."""

    def __init__(self, workspace: Path, action_bus: Any = None,
                 *, native_click_guard: Callable[[Any, dict], bool] | None = None):
        self.workspace = Path(workspace).resolve()
        self.store = GoalStore(self.workspace)
        self.action_bus = action_bus
        self.native_click_guard = native_click_guard
        with self.store._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS muse_official_pending ("
                       "pending_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, turn_id TEXT NOT NULL, "
                       "tool_call_id TEXT NOT NULL, call_nonce TEXT UNIQUE NOT NULL, "
                       "goal_id TEXT NOT NULL, revision INTEGER NOT NULL, plan_digest TEXT NOT NULL, "
                       "step_id TEXT NOT NULL, status TEXT NOT NULL, expires_at TEXT NOT NULL, "
                       "result_json TEXT, created_at TEXT NOT NULL, decided_at TEXT, "
                       "UNIQUE(session_id,turn_id,tool_call_id))")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS muse_official_one_pending_goal "
                       "ON muse_official_pending(goal_id,revision) "
                       "WHERE status IN ('WAITING_HUMAN','EXECUTING')")

    def _valid_goal(self, args: dict, *, status: str) -> tuple[dict, dict]:
        if set(args) != {"goal_id", "revision", "plan_digest", "step_id"}:
            raise ValueError("model_arguments_invalid")
        goal_id, revision = args["goal_id"], args["revision"]
        digest, step_id = args["plan_digest"], args["step_id"]
        if (not isinstance(goal_id, str) or not goal_id.startswith("goal:") or
                type(revision) is not int or revision < 1 or
                not isinstance(digest, str) or len(digest) != 64 or
                not isinstance(step_id, str) or not step_id):
            raise ValueError("model_arguments_invalid")
        goal = self.store.get(goal_id)
        if (goal is None or goal["status"] != status or goal["revision"] != revision or
                goal["digest"] != digest or plan_digest(goal["spec"]) != digest):
            raise ValueError("goal_revision_or_digest_changed")
        spec = goal["spec"]
        steps = spec.get("steps")
        if (not isinstance(steps, list) or len(steps) != 1 or
                steps[0].get("id") != step_id or
                steps[0].get("capability") != "workspace.write_artifact" or
                not isinstance(steps[0].get("args"), dict) or
                set(steps[0]["args"]) != {"relative_path", "content"} or
                not isinstance(steps[0]["args"]["relative_path"], str) or
                not isinstance(steps[0]["args"]["content"], str)):
            raise ValueError("official_step_must_be_static_single_write")
        path = steps[0]["args"]["relative_path"]
        permissions = spec.get("permissions", {})
        if (permissions.get("capabilities") != ["workspace.write_artifact"] or
                "resource:workspace/" + path not in permissions.get("resource_refs", []) or
                spec.get("budget", {}).get("money", {}).get("amount") != 0 or
                spec.get("budget", {}).get("money", {}).get("mode") != "capped" or
                not any(trigger.get("kind") == "interval" for trigger in spec.get("triggers", []))):
            raise ValueError("official_step_scope_rejected")
        return goal, steps[0]

    def prepare(self, params: dict) -> dict:
        """Called only by the stdio MCP side; it grants no action authority."""
        if not isinstance(params, dict) or params.get("name") != TOOL_NAME:
            return {"ok": False, "error": "official_tool_rejected"}
        meta, args = params.get("_meta"), params.get("arguments")
        if not isinstance(meta, dict) or not isinstance(args, dict):
            return {"ok": False, "error": "host_context_required"}
        if any(not isinstance(meta.get(key), str) or not meta[key] or len(meta[key]) > 200
               for key in META_KEYS):
            return {"ok": False, "error": "host_context_required"}
        try:
            uuid.UUID(meta["muse_host_turn_id"])
            nonce = uuid.UUID(meta["muse_host_call_nonce"])
            if nonce.version != 4:
                raise ValueError("host_nonce_invalid")
            self._valid_goal(args, status="draft")
        except (ValueError, TypeError, KeyError) as exc:
            return {"ok": False, "error": str(exc)[:120]}
        pending_id = "official:" + uuid.uuid4().hex
        now = utc_now()
        expires_at = iso(now + timedelta(seconds=WAIT_SECONDS))
        try:
            with self.store._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("UPDATE muse_official_pending SET status='EXPIRED' "
                           "WHERE status='WAITING_HUMAN' AND expires_at<=?", (iso(now),))
                db.execute("INSERT INTO muse_official_pending VALUES (?,?,?,?,?,?,?,?,?,"
                           "'WAITING_HUMAN',?,NULL,?,NULL)",
                           (pending_id, meta["muse_host_session_id"], meta["muse_host_turn_id"],
                            meta["muse_host_tool_call_id"], meta["muse_host_call_nonce"],
                            args["goal_id"], args["revision"], args["plan_digest"],
                            args["step_id"], expires_at, iso(now)))
        except sqlite3.IntegrityError:
            return {"ok": False, "error": "official_call_replayed_or_goal_pending"}
        return {"ok": True, "pending_id": pending_id, "expires_at": expires_at,
                "goal_id": args["goal_id"], "revision": args["revision"],
                "plan_digest": args["plan_digest"], "step_id": args["step_id"],
                "official_session_id": meta["muse_host_session_id"],
                "official_turn_id": meta["muse_host_turn_id"]}

    def pending_for_ui(self, pending_id: str) -> dict:
        """Return the stored Goal plan for display; never use model supplied text."""
        with self.store._connect() as db:
            row = db.execute("SELECT * FROM muse_official_pending WHERE pending_id=?",
                             (pending_id,)).fetchone()
        if row is None:
            return {"ok": False, "error": "pending_not_found"}
        item = dict(row)
        goal = self.store.get(item["goal_id"])
        if not goal or goal["revision"] != item["revision"] or goal["digest"] != item["plan_digest"]:
            return {"ok": False, "error": "goal_revision_or_digest_changed"}
        return {"ok": True, "pending_id": pending_id, "status": item["status"],
                "expires_at": item["expires_at"], "official_session_id": item["session_id"],
                "official_turn_id": item["turn_id"],
                "official_tool_call_id": item["tool_call_id"],
                "official_call_nonce": item["call_nonce"], "goal_id": item["goal_id"],
                "revision": item["revision"], "plan_digest": item["plan_digest"],
                "step_id": item["step_id"], "plan": goal["spec"]}

    def list_pending_for_ui(self) -> list[dict]:
        """Give the native review pane only live pending requests."""
        with self.store._connect() as db:
            ids = [row["pending_id"] for row in db.execute(
                "SELECT pending_id FROM muse_official_pending WHERE status='WAITING_HUMAN' "
                "AND expires_at>? ORDER BY created_at LIMIT 10", (iso(utc_now()),))]
        return [item for pending_id in ids if (item := self.pending_for_ui(pending_id)).get("ok")]

    def decide_from_native(self, pending_id: str, decision: str, reviewed_digest: str,
                           click_witness: Any) -> dict:
        """Only the trusted native click route may call this method."""
        if self.action_bus is None or self.native_click_guard is None:
            return {"ok": False, "error": "native_click_guard_unavailable"}
        if decision not in {"approve", "deny"} or not isinstance(reviewed_digest, str):
            return {"ok": False, "error": "native_decision_invalid"}
        pending = self.pending_for_ui(pending_id)
        if not pending.get("ok") or pending["status"] != "WAITING_HUMAN":
            return {"ok": False, "error": pending.get("error", "pending_not_waiting")}
        if pending["expires_at"] <= iso(utc_now()) or reviewed_digest != pending["plan_digest"]:
            return {"ok": False, "error": "pending_expired_or_digest_changed"}
        try:
            witnessed = self.native_click_guard(click_witness, pending) is True
        except Exception:
            witnessed = False
        if not witnessed:
            return {"ok": False, "error": "native_click_not_verified"}
        with self.store._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            changed = db.execute("UPDATE muse_official_pending SET status='EXECUTING',decided_at=? "
                                 "WHERE pending_id=? AND status='WAITING_HUMAN' AND expires_at>?",
                                 (iso(utc_now()), pending_id, iso(utc_now()))).rowcount
            if changed != 1:
                return {"ok": False, "error": "pending_not_waiting"}
        if decision == "deny":
            body = {"ok": False, "status": "DENIED", "pending_id": pending_id,
                    "goal_id": pending["goal_id"]}
        else:
            body = self._execute_approved(pending)
        with self.store._connect() as db:
            db.execute("UPDATE muse_official_pending SET status=?,result_json=? "
                       "WHERE pending_id=? AND status='EXECUTING'",
                       (body["status"], json.dumps(body, ensure_ascii=False, sort_keys=True), pending_id))
        return body

    def _execute_approved(self, pending: dict) -> dict:
        args = {key: pending[key] for key in ("goal_id", "revision", "plan_digest", "step_id")}
        try:
            goal, step = self._valid_goal(args, status="draft")
            spec = goal["spec"]
            now = utc_now()
            expiry = now + timedelta(days=30)
            if spec["deadline"]:
                expiry = min(expiry, datetime.fromisoformat(
                    spec["deadline"].replace("Z", "+00:00")).astimezone(timezone.utc))
            if expiry <= now:
                raise ValueError("goal_deadline_reached")
            approval_id, run_id = "approval:" + uuid.uuid4().hex, "run:" + uuid.uuid4().hex
            scope = {key: spec[key] for key in ("permissions", "budget", "deadline", "verification")}
            with self.store._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT status,revision FROM muse_goals WHERE goal_id=?",
                                 (args["goal_id"],)).fetchone()
                plan = db.execute("SELECT digest,spec_json FROM muse_goal_revisions "
                                  "WHERE goal_id=? AND revision=?",
                                  (args["goal_id"], args["revision"])).fetchone()
                if (row is None or row["status"] != "draft" or row["revision"] != args["revision"] or
                        plan is None or plan["digest"] != args["plan_digest"] or
                        plan_digest(json.loads(plan["spec_json"])) != args["plan_digest"]):
                    raise ValueError("goal_revision_or_digest_changed")
                db.execute("INSERT INTO muse_goal_approvals VALUES (?,?,?,?,?,?,?)",
                           (approval_id, args["goal_id"], args["revision"], args["plan_digest"],
                            json.dumps(scope, ensure_ascii=False, sort_keys=True), iso(expiry), iso(now)))
                db.execute("UPDATE muse_goals SET status='running',approval_id=?,approval_digest=?,"
                           "approval_expires_at=?,run_id=?,run_count=run_count+1,next_due=NULL,"
                           "pending_event_id=NULL,last_error=NULL,updated_at=? WHERE goal_id=?",
                           (approval_id, args["plan_digest"], iso(expiry), run_id, iso(now),
                            args["goal_id"]))
                db.execute("INSERT INTO muse_goal_runs(run_id,goal_id,revision,approval_id,"
                           "trigger_kind,event_id,status,started_at) VALUES (?,?,?,?,?,?,'running',?)",
                           (run_id, args["goal_id"], args["revision"], approval_id,
                            "official_mcp", pending["pending_id"], iso(now)))
        except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
            return {"ok": False, "status": "BLOCKED", "pending_id": pending["pending_id"],
                    "error": str(exc)[:160]}
        try:
            call = {"action_id": run_id + ":" + args["step_id"], "capability": step["capability"],
                    "args": dict(step["args"]), "goal_id": args["goal_id"],
                    "revision": args["revision"]}
            receipt = self.action_bus.execute(call, approved=True, context={
                "approval_id": approval_id, "plan_digest": args["plan_digest"], "run_id": run_id,
                "permissions": spec["permissions"], "budget": spec["budget"]})
            if (not isinstance(receipt, dict) or receipt.get("ok") is not True or
                    receipt.get("capability") != "workspace.write_artifact" or
                    receipt.get("verification", {}).get("readback_matches") is not True):
                raise ValueError("approved_action_or_readback_failed")
            content = step["args"]["content"].encode("utf-8")
            digest = hashlib.sha256(content).hexdigest()
            if (_readback(self.workspace, step["args"]["relative_path"]) != content or
                    receipt.get("output", {}).get("sha256") != digest or
                    receipt.get("verification", {}).get("sha256") != digest):
                raise ValueError("independent_readback_mismatch")
            result = {"ok": True, "status": "COMPLETED", "goal_id": args["goal_id"],
                      "revision": args["revision"], "run_id": run_id, "approval_id": approval_id,
                      "receipts": [receipt], "verification": "CHECKS_PASSED",
                      "official_session_id": pending["official_session_id"],
                      "official_turn_id": pending["official_turn_id"],
                      "official_tool_call_id": pending["official_tool_call_id"],
                      "official_call_nonce": pending["official_call_nonce"]}
            public_receipt = {"action_id": receipt.get("action_id"),
                              "capability": receipt["capability"],
                              "relative_path": receipt["output"]["relative_path"],
                              "bytes": receipt["output"]["bytes"],
                              "sha256": digest, "readback_matches": True}
            self.store.finish(args["goal_id"], run_id, "completed", result, None)
            return {"ok": True, "status": "COMPLETED", "pending_id": pending["pending_id"],
                    "goal_id": args["goal_id"], "revision": args["revision"],
                    "plan_digest": args["plan_digest"], "approval_id": approval_id,
                    "run_id": run_id, "official_session_id": pending["official_session_id"],
                    "official_turn_id": pending["official_turn_id"],
                    "official_tool_call_id": pending["official_tool_call_id"],
                    "official_call_nonce": pending["official_call_nonce"],
                    "receipt": public_receipt, "readback_sha256": digest}
        except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
            failure = {"ok": False, "status": "WAITING_USER", "goal_id": args["goal_id"],
                       "revision": args["revision"], "run_id": run_id,
                       "approval_id": approval_id, "receipts": [],
                       "verification": "FAILED", "error": str(exc)[:160]}
            try:
                self.store.finish(args["goal_id"], run_id, "failed", failure, None)
            except (OSError, ValueError, sqlite3.Error):
                pass
            return {"ok": False, "status": "BLOCKED", "pending_id": pending["pending_id"],
                    "error": str(exc)[:160]}

    def wait_for_result(self, pending_id: str) -> dict:
        deadline = time.monotonic() + WAIT_SECONDS + 2
        while time.monotonic() < deadline:
            with self.store._connect() as db:
                row = db.execute("SELECT status,result_json,expires_at FROM muse_official_pending "
                                 "WHERE pending_id=?", (pending_id,)).fetchone()
            if row is None:
                return _result("BLOCKED", error="pending_disappeared")
            if row["result_json"]:
                body = json.loads(row["result_json"])
                return _result(body["status"], **{key: value for key, value in body.items()
                                                  if key != "status"})
            if row["status"] == "EXPIRED":
                return _result("WAITING_HUMAN", error="approval_time_expired")
            if row["status"] == "WAITING_HUMAN" and row["expires_at"] <= iso(utc_now()):
                with self.store._connect() as db:
                    db.execute("UPDATE muse_official_pending SET status='EXPIRED' "
                               "WHERE pending_id=? AND status='WAITING_HUMAN'", (pending_id,))
                return _result("WAITING_HUMAN", error="approval_time_expired")
            time.sleep(0.1)
        with self.store._connect() as db:
            db.execute("UPDATE muse_official_pending SET status='EXPIRED' "
                       "WHERE pending_id=? AND status='WAITING_HUMAN'", (pending_id,))
            row = db.execute("SELECT status,result_json FROM muse_official_pending "
                             "WHERE pending_id=?", (pending_id,)).fetchone()
        if row and row["result_json"]:
            body = json.loads(row["result_json"])
            return _result(body["status"], **{key: value for key, value in body.items()
                                              if key != "status"})
        if row and row["status"] == "EXECUTING":
            return _result("IN_PROGRESS", error="action_still_running",
                           pending_id=pending_id)
        return _result("WAITING_HUMAN", error="approval_time_expired")


def serve_stdio(workspace: Path) -> None:
    bridge = OfficialGoalBridge(workspace)
    for line in sys.stdin:
        frame = None
        try:
            frame = json.loads(line)
            if not isinstance(frame, dict) or "id" not in frame:
                continue
            method = frame.get("method")
            if method == "initialize":
                result = {"protocolVersion": frame.get("params", {}).get("protocolVersion", "2025-06-18"),
                          "capabilities": {"tools": {}},
                          "serverInfo": {"name": "muse-official-goal-bridge", "version": "0.1"}}
            elif method == "tools/list":
                result = {"tools": [{"name": TOOL_NAME,
                    "description": "Request one reviewed Muse Goal step. Requires a separate native click.",
                    "inputSchema": {"type": "object", "additionalProperties": False,
                        "properties": {"goal_id": {"type": "string"},
                                       "revision": {"type": "integer"},
                                       "plan_digest": {"type": "string"},
                                       "step_id": {"type": "string"}},
                        "required": ["goal_id", "revision", "plan_digest", "step_id"]}}]}
            elif method == "tools/call":
                prepared = bridge.prepare(frame.get("params"))
                result = (bridge.wait_for_result(prepared["pending_id"])
                          if prepared.get("ok") else
                          _result("BLOCKED", error=prepared["error"]))
            else:
                result = {}
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": frame["id"],
                                         "result": result}, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
            if isinstance(frame, dict) and "id" in frame:
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": frame["id"],
                    "result": _result("BLOCKED", error="bridge_unavailable:" +
                                      type(exc).__name__)}) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-stdio", action="store_true", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    options = parser.parse_args()
    serve_stdio(options.workspace)
