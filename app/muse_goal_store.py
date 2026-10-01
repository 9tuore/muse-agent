"""SQLite state for Muse goals. Plans and approvals are separate records."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from muse_dsl import goal_document


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def plan_digest(spec: Dict[str, Any]) -> str:
    data = json.dumps(spec, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class GoalStore:
    """Own only muse_* tables inside the existing memory database."""

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / "memory.sqlite3"
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _migrate(self) -> None:
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS muse_schema_migrations "
                       "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
            if not db.execute("SELECT 1 FROM muse_schema_migrations WHERE version=1").fetchone():
                db.execute("CREATE TABLE IF NOT EXISTS muse_goals ("
                       "goal_id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, "
                       "revision INTEGER NOT NULL, status TEXT NOT NULL, next_due TEXT, "
                       "approval_id TEXT, approval_digest TEXT, approval_expires_at TEXT, "
                       "run_id TEXT, run_count INTEGER NOT NULL DEFAULT 0, "
                       "last_error TEXT, model_json TEXT NOT NULL, updated_at TEXT NOT NULL)")
                db.execute("CREATE TABLE IF NOT EXISTS muse_goal_revisions ("
                       "goal_id TEXT NOT NULL, revision INTEGER NOT NULL, spec_json TEXT NOT NULL, "
                       "digest TEXT NOT NULL, created_at TEXT NOT NULL, "
                       "PRIMARY KEY(goal_id, revision), "
                       "FOREIGN KEY(goal_id) REFERENCES muse_goals(goal_id))")
                db.execute("CREATE TABLE IF NOT EXISTS muse_goal_approvals ("
                       "approval_id TEXT PRIMARY KEY, goal_id TEXT NOT NULL, revision INTEGER NOT NULL, "
                       "digest TEXT NOT NULL, scope_json TEXT NOT NULL, expires_at TEXT NOT NULL, "
                       "created_at TEXT NOT NULL)")
                db.execute("CREATE TABLE IF NOT EXISTS muse_goal_runs ("
                       "run_id TEXT PRIMARY KEY, goal_id TEXT NOT NULL, revision INTEGER NOT NULL, "
                       "approval_id TEXT NOT NULL, trigger_kind TEXT NOT NULL, event_id TEXT, "
                       "status TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, "
                       "result_json TEXT)")
                db.execute("CREATE TABLE IF NOT EXISTS muse_goal_events ("
                       "goal_id TEXT NOT NULL, event_id TEXT NOT NULL, observed_at TEXT NOT NULL, "
                       "PRIMARY KEY(goal_id, event_id))")
                db.execute("INSERT INTO muse_schema_migrations VALUES (1, ?)", (iso(utc_now()),))
            if not db.execute("SELECT 1 FROM muse_schema_migrations WHERE version=2").fetchone():
                if "pending_event_id" not in {row[1] for row in db.execute("PRAGMA table_info(muse_goals)")}:
                    db.execute("ALTER TABLE muse_goals ADD COLUMN pending_event_id TEXT")
                if "event_json" not in {row[1] for row in db.execute("PRAGMA table_info(muse_goal_events)")}:
                    db.execute("ALTER TABLE muse_goal_events ADD COLUMN event_json TEXT")
                db.execute("INSERT INTO muse_schema_migrations VALUES (2, ?)", (iso(utc_now()),))
        os.chmod(self.path, 0o600)

    def by_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            row = db.execute("SELECT goal_id FROM muse_goals WHERE request_id=?", (request_id,)).fetchone()
        return self.get(row["goal_id"]) if row else None

    def save_draft(self, spec: Dict[str, Any], request_id: str, model: Dict[str, Any]) -> Dict[str, Any]:
        goal_id = spec["goal_id"]
        timestamp = iso(utc_now())
        goal_document(spec, created_at=timestamp, updated_at=timestamp)
        encoded = json.dumps(spec, ensure_ascii=False, sort_keys=True)
        digest = plan_digest(spec)
        with self._connect() as db:
            db.execute("INSERT INTO muse_goals(goal_id,request_id,revision,status,model_json,updated_at) "
                       "VALUES (?,?,1,'draft',?,?)",
                       (goal_id, request_id, json.dumps(model, ensure_ascii=False), timestamp))
            db.execute("INSERT INTO muse_goal_revisions VALUES (?,?,?,?,?)",
                       (goal_id, 1, encoded, digest, timestamp))
        return self.get(goal_id)

    def save_revision(self, spec: Dict[str, Any], model: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        goal_id = spec["goal_id"]
        timestamp = iso(utc_now())
        goal_document(spec, created_at=timestamp, updated_at=timestamp)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision,status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row or row["status"] in {"running", "cancelled", "rejected", "completed"} or (
                spec["revision"] != row["revision"] + 1
            ):
                return None
            db.execute("INSERT INTO muse_goal_revisions VALUES (?,?,?,?,?)",
                       (goal_id, spec["revision"], json.dumps(spec, ensure_ascii=False, sort_keys=True),
                        plan_digest(spec), timestamp))
            db.execute("UPDATE muse_goals SET revision=?,status='draft',next_due=NULL,approval_id=NULL,"
                       "approval_digest=NULL,approval_expires_at=NULL,run_id=NULL,pending_event_id=NULL,last_error=NULL,"
                       "model_json=?,updated_at=? WHERE goal_id=?",
                       (spec["revision"], json.dumps(model, ensure_ascii=False), timestamp, goal_id))
        return self.get(goal_id)

    def get(self, goal_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row:
                return None
            plan = db.execute("SELECT spec_json,digest,created_at FROM muse_goal_revisions "
                              "WHERE goal_id=? AND revision=?", (goal_id, row["revision"])).fetchone()
        value = dict(row)
        value["spec"] = json.loads(plan["spec_json"])
        value["digest"] = plan["digest"]
        value["model"] = json.loads(value.pop("model_json"))
        value["dsl"] = goal_document(value["spec"], created_at=plan["created_at"],
                                     updated_at=value["updated_at"])
        return value

    def list(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._connect() as db:
            ids = [row["goal_id"] for row in db.execute(
                "SELECT goal_id FROM muse_goals ORDER BY updated_at DESC LIMIT ?", (limit,))]
        return [self.get(goal_id) for goal_id in ids]

    def decide(self, goal_id: str, revision: int, decision: str,
               *, reviewed_digest: Optional[str] = None) -> Optional[Dict[str, Any]]:
        now = utc_now()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision,status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row or row["revision"] != revision or row["status"] != "draft":
                return None
            plan = db.execute("SELECT spec_json,digest FROM muse_goal_revisions "
                              "WHERE goal_id=? AND revision=?", (goal_id, revision)).fetchone()
            spec = json.loads(plan["spec_json"])
            if decision == "approve" and (
                plan_digest(spec) != plan["digest"] or reviewed_digest != plan["digest"]
            ):
                return None
            if decision == "reject":
                db.execute("UPDATE muse_goals SET status='rejected',updated_at=? WHERE goal_id=?",
                           (iso(now), goal_id))
            else:
                deadline = spec["deadline"]
                expiry = now + timedelta(days=30)
                if deadline:
                    expiry = min(expiry, datetime.fromisoformat(deadline.replace("Z", "+00:00")).astimezone(timezone.utc))
                if expiry <= now:
                    return None
                approval_id = "approval:" + uuid.uuid4().hex
                scope = {key: spec[key] for key in ("permissions", "budget", "deadline", "verification")}
                first_due = iso(now) if any(item["kind"] == "interval" for item in spec["triggers"]) else None
                db.execute("INSERT INTO muse_goal_approvals VALUES (?,?,?,?,?,?,?)",
                           (approval_id, goal_id, revision, plan["digest"],
                            json.dumps(scope, ensure_ascii=False, sort_keys=True), iso(expiry), iso(now)))
                db.execute("UPDATE muse_goals SET status='active',approval_id=?,approval_digest=?,"
                           "approval_expires_at=?,next_due=?,updated_at=? WHERE goal_id=?",
                           (approval_id, plan["digest"], iso(expiry), first_due, iso(now), goal_id))
        return self.get(goal_id)

    def control(self, goal_id: str, action: str) -> Optional[Dict[str, Any]]:
        allowed = {"pause": ("active", "paused"), "resume": ("paused", "active"),
                   "cancel": ("active", "cancelled"), "retry": ("waiting_user", "active")}
        current, target = allowed[action]
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row or (action != "cancel" and row["status"] != current) or (
                action == "cancel" and row["status"] not in {"active", "paused", "waiting_user"}
            ):
                return None
            if action == "retry":
                plan = db.execute("SELECT spec_json,digest FROM muse_goal_revisions WHERE goal_id=? AND revision=?",
                                  (goal_id, row["revision"])).fetchone()
                now = iso(utc_now())
                if not row["approval_id"] or row["approval_digest"] != plan["digest"] or (
                    row["approval_expires_at"] <= now
                ):
                    return None
                runs = db.execute("SELECT status,event_id,result_json FROM muse_goal_runs WHERE goal_id=? "
                                  "AND revision=? ORDER BY started_at DESC,run_id DESC",
                                  (goal_id, row["revision"])).fetchall()
                if not runs or runs[0]["status"] != "failed" or not runs[0]["result_json"]:
                    return None
                spec = json.loads(plan["spec_json"])
                failed_count = next((index for index, run in enumerate(runs) if run["status"] != "failed"), len(runs))
                if failed_count > spec["failure_policy"]["max_retries"]:
                    return None
                result = json.loads(runs[0]["result_json"])
                safe = {"web.read", "web.search", "model.compose", "system.frontmost_app"}
                if result.get("failed_capability") not in safe or any(
                    receipt.get("capability") not in safe for receipt in result.get("receipts", [])
                ):
                    return None
                db.execute("UPDATE muse_goals SET status='active',next_due=?,pending_event_id=?,"
                           "last_error=NULL,updated_at=? WHERE goal_id=?",
                           (now, runs[0]["event_id"], now, goal_id))
            else:
                if action == "cancel":
                    db.execute("UPDATE muse_goals SET status=?,next_due=NULL,pending_event_id=NULL,"
                               "updated_at=? WHERE goal_id=?", (target, iso(utc_now()), goal_id))
                else:
                    db.execute("UPDATE muse_goals SET status=?,updated_at=? WHERE goal_id=?",
                               (target, iso(utc_now()), goal_id))
        return self.get(goal_id)

    def due_ids(self, now: datetime) -> List[str]:
        with self._connect() as db:
            return [row["goal_id"] for row in db.execute(
                "SELECT goal_id FROM muse_goals WHERE status='active' AND next_due<=? "
                "ORDER BY next_due LIMIT 10", (iso(now),))]

    def expire_due(self, now: datetime) -> int:
        expired = 0
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT g.goal_id,p.spec_json FROM muse_goals g "
                              "JOIN muse_goal_revisions p ON p.goal_id=g.goal_id AND p.revision=g.revision "
                              "WHERE g.status IN ('active','paused','waiting_user')").fetchall()
            for row in rows:
                deadline = json.loads(row["spec_json"])["deadline"]
                if deadline and datetime.fromisoformat(deadline.replace("Z", "+00:00")) <= now:
                    db.execute("UPDATE muse_goals SET status='expired',next_due=NULL,pending_event_id=NULL,"
                               "last_error='deadline_reached',updated_at=? WHERE goal_id=?",
                               (iso(now), row["goal_id"]))
                    expired += 1
        return expired

    def schedule_event(self, goal_id: str, event: Dict[str, Any], now: datetime) -> bool:
        event_id, observed_at = event["event_id"], event["observed_at"]
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row or row["status"] != "active":
                return False
            # A late folder snapshot must not replace a newer run for the same watched directory.
            if event.get("source") == "workspace_watcher" and event.get("topic") == "file.changed":
                observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
                for previous in db.execute("SELECT observed_at,event_json FROM muse_goal_events "
                                           "WHERE goal_id=?", (goal_id,)):
                    if not previous["event_json"]:
                        continue
                    recorded = json.loads(previous["event_json"])
                    if (recorded.get("source") == "workspace_watcher" and
                            recorded.get("topic") == "file.changed" and
                            recorded.get("payload_ref") == event.get("payload_ref") and
                            datetime.fromisoformat(previous["observed_at"].replace("Z", "+00:00")) > observed):
                        return False
            try:
                db.execute("INSERT INTO muse_goal_events(goal_id,event_id,observed_at,event_json) "
                           "VALUES (?,?,?,?)", (goal_id, event_id, observed_at,
                                               json.dumps(event, ensure_ascii=False, sort_keys=True)))
            except sqlite3.IntegrityError:
                return False
            db.execute("UPDATE muse_goals SET next_due=?,pending_event_id=?,updated_at=? WHERE goal_id=?",
                       (iso(now), event_id, iso(now), goal_id))
        return True

    def pending_event(self, goal_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            row = db.execute("SELECT e.event_json FROM muse_goals g JOIN muse_goal_events e "
                             "ON e.goal_id=g.goal_id AND e.event_id=g.pending_event_id "
                             "WHERE g.goal_id=?", (goal_id,)).fetchone()
        return json.loads(row["event_json"]) if row and row["event_json"] else None

    def approval_started_at(self, approval_id: Optional[str]) -> Optional[datetime]:
        if not approval_id:
            return None
        with self._connect() as db:
            row = db.execute("SELECT created_at FROM muse_goal_approvals WHERE approval_id=?",
                             (approval_id,)).fetchone()
        return datetime.fromisoformat(row["created_at"]) if row else None

    def completed_receipts(self, goal_id: str) -> List[Dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT result_json FROM muse_goal_runs WHERE goal_id=? AND status='completed' "
                              "ORDER BY finished_at", (goal_id,)).fetchall()
        receipts: List[Dict[str, Any]] = []
        for row in rows:
            result = json.loads(row["result_json"])
            receipts.extend(result.get("receipts", []))
        return receipts

    def budget_usage(self, goal_id: str, since: Optional[datetime] = None) -> Dict[str, int]:
        query = "SELECT result_json FROM muse_goal_runs WHERE goal_id=? AND result_json IS NOT NULL"
        params: tuple = (goal_id,)
        if since is not None:
            query += " AND started_at>=?"
            params += (iso(since),)
        with self._connect() as db:
            rows = db.execute(query, params).fetchall()
        totals = {"model_tokens": 0, "web_reads": 0}
        for row in rows:
            result = json.loads(row["result_json"])
            for key in totals:
                amount = result.get(key)
                if type(amount) is int and amount > 0:
                    totals[key] += amount
        return totals

    def claim(self, goal_id: str, now: datetime, trigger_kind: str, event_id: Optional[str]) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row or row["status"] != "active" or not row["next_due"] or row["next_due"] > iso(now):
                return None
            plan = db.execute("SELECT spec_json,digest FROM muse_goal_revisions "
                              "WHERE goal_id=? AND revision=?", (goal_id, row["revision"])).fetchone()
            deadline = json.loads(plan["spec_json"])["deadline"]
            if deadline and datetime.fromisoformat(deadline.replace("Z", "+00:00")) <= now:
                db.execute("UPDATE muse_goals SET status='expired',next_due=NULL,pending_event_id=NULL,"
                           "last_error='deadline_reached',updated_at=? WHERE goal_id=?", (iso(now), goal_id))
                return None
            if not row["approval_id"] or row["approval_digest"] != plan["digest"] or (
                row["approval_expires_at"] <= iso(now)
            ):
                db.execute("UPDATE muse_goals SET status='waiting_user',last_error='approval_expired_or_changed',"
                           "updated_at=? WHERE goal_id=?", (iso(now), goal_id))
                return None
            run_id = "run:" + uuid.uuid4().hex
            db.execute("UPDATE muse_goals SET status='running',run_id=?,next_due=NULL,"
                       "run_count=run_count+1,updated_at=? WHERE goal_id=?",
                       (run_id, iso(now), goal_id))
            db.execute("INSERT INTO muse_goal_runs(run_id,goal_id,revision,approval_id,trigger_kind,"
                       "event_id,status,started_at) VALUES (?,?,?,?,?,?,'running',?)",
                       (run_id, goal_id, row["revision"], row["approval_id"], trigger_kind, event_id, iso(now)))
        return self.get(goal_id)

    def finish(self, goal_id: str, run_id: str, status: str, result: Dict[str, Any],
               next_due: Optional[datetime], keep_active: bool = False) -> Dict[str, Any]:
        now = utc_now()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT run_id,status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
            if not row or row["run_id"] != run_id or row["status"] != "running":
                raise ValueError("run_state_changed")
            db.execute("UPDATE muse_goal_runs SET status=?,finished_at=?,result_json=? WHERE run_id=?",
                       (status, iso(now), json.dumps(result, ensure_ascii=False), run_id))
            goal_status = "active" if status == "completed" and (next_due or keep_active) else (
                "completed" if status == "completed" else "waiting_user")
            db.execute("UPDATE muse_goals SET status=?,run_id=NULL,next_due=?,pending_event_id=NULL,last_error=?,"
                       "updated_at=? WHERE goal_id=?",
                       (goal_status, iso(next_due) if next_due else None,
                        result.get("error"), iso(now), goal_id))
        return self.get(goal_id)

    def recover_interrupted(self, now: Optional[datetime] = None) -> int:
        """Review stale runs without interrupting another process's active run."""
        now = now or utc_now()
        recovered = 0
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT g.goal_id,g.run_id,r.started_at,p.spec_json FROM muse_goals g "
                              "JOIN muse_goal_runs r ON r.run_id=g.run_id "
                              "JOIN muse_goal_revisions p ON p.goal_id=g.goal_id AND p.revision=g.revision "
                              "WHERE g.status='running'").fetchall()
            for row in rows:
                limit = json.loads(row["spec_json"])["budget"]["max_run_seconds"]
                if datetime.fromisoformat(row["started_at"]) + timedelta(seconds=limit + 60) > now:
                    continue
                db.execute("UPDATE muse_goals SET status='waiting_user',run_id=NULL,"
                           "last_error='interrupted_run_requires_review',updated_at=? WHERE goal_id=?",
                           (iso(now), row["goal_id"]))
                db.execute("UPDATE muse_goal_runs SET status='interrupted',finished_at=? WHERE run_id=?",
                           (iso(now), row["run_id"]))
                recovered += 1
        return recovered
