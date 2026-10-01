"""Scheduled, source-linked briefs from verified local Goal runs only."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULTS = {"brief_mode": "off", "brief_local_time": "08:00",
            "quiet_start": None, "quiet_end": None}
SLOTS = {"morning": "08:00", "evening": "20:00"}


class BriefService:
    def __init__(self, workspace: Path):
        self.path = Path(workspace) / "memory.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS muse_brief_settings ("
                       "singleton INTEGER PRIMARY KEY CHECK(singleton=1), settings_json TEXT NOT NULL, "
                       "enabled_at TEXT, updated_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS muse_brief_deliveries ("
                       "local_day TEXT PRIMARY KEY, brief_id TEXT NOT NULL UNIQUE, "
                       "status TEXT NOT NULL, prepared_at TEXT NOT NULL, delivered_at TEXT, "
                       "payload_json TEXT NOT NULL)")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def _clock(value: Any) -> int:
        if not isinstance(value, str) or len(value) != 5 or value[2] != ":" or (
            not value[:2].isdigit() or not value[3:].isdigit()
        ):
            raise ValueError("brief_time_invalid")
        hour, minute = int(value[:2]), int(value[3:])
        if hour > 23 or minute > 59:
            raise ValueError("brief_time_invalid")
        return hour * 60 + minute

    @classmethod
    def _validate_settings(cls, settings: Dict[str, Any]) -> None:
        if not isinstance(settings, dict) or set(settings) != set(DEFAULTS) or (
            settings["brief_mode"] not in {"off", "morning", "evening", "custom"}
        ):
            raise ValueError("brief_settings_invalid")
        cls._clock(settings["brief_local_time"])
        start, end = settings["quiet_start"], settings["quiet_end"]
        if (start is None) != (end is None):
            raise ValueError("quiet_hours_pair_required")
        if start is not None and cls._clock(start) == cls._clock(end):
            raise ValueError("quiet_hours_equal")

    @staticmethod
    def _in_quiet_hours(settings: Dict[str, Any], minutes: int) -> bool:
        start, end = settings["quiet_start"], settings["quiet_end"]
        if start is None:
            return False
        begin = BriefService._clock(start)
        finish = BriefService._clock(end)
        return begin <= minutes < finish if begin < finish else minutes >= begin or minutes < finish

    def get_settings(self) -> Dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT settings_json,enabled_at FROM muse_brief_settings WHERE singleton=1").fetchone()
        return {"settings": json.loads(row["settings_json"]) if row else DEFAULTS.copy(),
                "enabled_at": row["enabled_at"] if row else None}

    def set_settings(self, changes: Dict[str, Any], *, now: Optional[datetime] = None) -> Dict[str, Any]:
        if not isinstance(changes, dict) or set(changes) - set(DEFAULTS):
            raise ValueError("brief_settings_invalid")
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("timezone_aware_now_required")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT settings_json,enabled_at FROM muse_brief_settings WHERE singleton=1").fetchone()
            before = json.loads(row["settings_json"]) if row else DEFAULTS.copy()
            settings = {**before, **changes}
            self._validate_settings(settings)
            enabled_at = row["enabled_at"] if row else None
            if before["brief_mode"] == "off" and settings["brief_mode"] != "off":
                enabled_at = now.astimezone(timezone.utc).isoformat()
            if settings["brief_mode"] == "off":
                enabled_at = None
                db.execute("DELETE FROM muse_brief_deliveries WHERE status='prepared'")
            db.execute("INSERT INTO muse_brief_settings VALUES (1,?,?,?) ON CONFLICT(singleton) "
                       "DO UPDATE SET settings_json=excluded.settings_json,enabled_at=excluded.enabled_at,"
                       "updated_at=excluded.updated_at",
                       (json.dumps(settings, ensure_ascii=False, sort_keys=True), enabled_at,
                        now.astimezone(timezone.utc).isoformat()))
        return {"ok": True, "status": "SAVED", "brief_settings": settings,
                "enabled_at": enabled_at}

    def tick(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("timezone_aware_now_required")
        local = now.astimezone()
        today = local.date().isoformat()
        current_minutes = local.hour * 60 + local.minute
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            setting_row = db.execute("SELECT settings_json,enabled_at FROM muse_brief_settings WHERE singleton=1").fetchone()
            if not setting_row:
                return {"ok": True, "status": "NO_CHANGE", "reason": "brief_off"}
            settings = json.loads(setting_row["settings_json"])
            if settings["brief_mode"] == "off":
                return {"ok": True, "status": "NO_CHANGE", "reason": "brief_off"}
            due = self._clock(SLOTS.get(settings["brief_mode"], settings["brief_local_time"]))
            if current_minutes < due:
                return {"ok": True, "status": "NO_CHANGE", "reason": "before_brief_time"}
            if self._in_quiet_hours(settings, current_minutes):
                return {"ok": True, "status": "QUIET_HOURS"}
            existing = db.execute("SELECT status,payload_json FROM muse_brief_deliveries WHERE local_day=?",
                                  (today,)).fetchone()
            if existing:
                if existing["status"] == "delivered":
                    return {"ok": True, "status": "NO_CHANGE", "reason": "already_delivered"}
                return {"ok": True, "status": "BRIEF_READY", "brief": json.loads(existing["payload_json"]),
                        "replayed": True}
            if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='muse_goal_runs'").fetchone():
                return {"ok": True, "status": "NO_CHANGE", "reason": "no_goal_runs"}
            delivered = db.execute("SELECT MAX(delivered_at) AS at FROM muse_brief_deliveries "
                                   "WHERE status='delivered'").fetchone()["at"]
            since = max(value for value in (setting_row["enabled_at"], delivered,
                                             (now - timedelta(hours=36)).astimezone(timezone.utc).isoformat())
                        if value is not None)
            rows = db.execute("SELECT goal_id,run_id,status,finished_at,result_json FROM muse_goal_runs "
                              "WHERE finished_at>? AND finished_at<=? AND status IN "
                              "('completed','failed','interrupted') ORDER BY finished_at DESC LIMIT 100",
                              (since, now.astimezone(timezone.utc).isoformat())).fetchall()
            updates = []
            decisions = []
            for row in rows:
                result = json.loads(row["result_json"]) if row["result_json"] else {}
                if (row["status"] == "completed" and result.get("status") == "COMPLETED" and
                    result.get("verification") == "CHECKS_PASSED"):
                    receipts = result.get("receipts", [])
                    artifacts = [item.get("output", {}).get("relative_path") for item in receipts
                                 if item.get("capability") == "workspace.write_artifact"]
                    sources = [item.get("output", {}).get("source_url") for item in receipts
                               if item.get("capability") == "web.read"]
                    updates.append({"goal_id": row["goal_id"], "run_id": row["run_id"],
                                    "verified_at": row["finished_at"],
                                    "artifact_paths": [item for item in artifacts if item],
                                    "source_urls": [item for item in sources if item]})
                elif row["status"] in {"failed", "interrupted"}:
                    decisions.append({"goal_id": row["goal_id"], "run_id": row["run_id"],
                                      "observed_at": row["finished_at"],
                                      "reason": result.get("error") or row["status"]})
            if not updates and not decisions:
                return {"ok": True, "status": "NO_CHANGE", "reason": "no_verified_updates"}
            brief = {"brief_id": "brief:" + today, "local_day": today,
                     "period_start": since, "period_end": now.astimezone(timezone.utc).isoformat(),
                     "summary": f"已验证更新 {len(updates)} 项，待决定 {len(decisions)} 项",
                     "verified_updates": list(reversed(updates[:20])),
                     "needs_decision": list(reversed(decisions[:20]))}
            db.execute("INSERT INTO muse_brief_deliveries VALUES (?,?, 'prepared', ?, NULL, ?)",
                       (today, brief["brief_id"], now.astimezone(timezone.utc).isoformat(),
                        json.dumps(brief, ensure_ascii=False, sort_keys=True)))
        return {"ok": True, "status": "BRIEF_READY", "brief": brief, "replayed": False}

    def acknowledge(self, brief_id: str, *, now: Optional[datetime] = None) -> Dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("timezone_aware_now_required")
        with self._connect() as db:
            cursor = db.execute("UPDATE muse_brief_deliveries SET status='delivered',delivered_at=? "
                                "WHERE brief_id=? AND status='prepared'",
                                (now.astimezone(timezone.utc).isoformat(), brief_id))
        return {"ok": cursor.rowcount == 1, "status": "ACKNOWLEDGED" if cursor.rowcount else "NOT_FOUND"}

    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        kind = event.get("type") if isinstance(event, dict) else None
        try:
            if kind == "brief_settings_get":
                return {"ok": True, "status": "READY", "brief_settings": self.get_settings()["settings"]}
            if kind == "brief_settings_set":
                return self.set_settings(event.get("settings"))
            if kind == "brief_tick":
                return self.tick()
            if kind == "brief_ack":
                return self.acknowledge(event.get("brief_id"))
        except (TypeError, ValueError, sqlite3.Error) as exc:
            return {"ok": False, "status": "REJECTED", "error": str(exc)[:160]}
        return {"ok": False, "status": "REJECTED", "error": "unsupported_brief_event"}
