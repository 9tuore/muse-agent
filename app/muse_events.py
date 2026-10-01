"""Normalize external observations as bounded data, never as authority."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Set


MAX_PAYLOAD_BYTES = 4096
SENSITIVE_KEYS = {"password", "auth_code", "token", "secret", "api_key", "authorization"}


def _private_database(path: Path) -> None:
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(fd, 0o600)
    finally:
        os.close(fd)


def _bounded_payload(raw: Mapping[str, Any]) -> Dict[str, Any]:
    supplied = raw.get("payload")
    if supplied is None:
        supplied = {key: raw[key] for key in ("text", "metadata", "status", "request_id") if key in raw}
    if not isinstance(supplied, dict):
        raise ValueError("event_payload_must_be_object")
    def redact(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: redact(item) for key, item in value.items()
                    if str(key).lower() not in SENSITIVE_KEYS}
        if isinstance(value, list):
            return [redact(item) for item in value[:32]]
        return value

    payload = redact(supplied)
    encoded = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    if len(encoded) > MAX_PAYLOAD_BYTES:
        payload = {"summary": str(raw.get("text") or raw.get("subject") or "")[:1000],
                   "truncated": True}
    return payload


def normalize_event(raw: Mapping[str, Any], *, account_scope: Optional[str] = None,
                    allowed_resource_refs: Optional[Set[str]] = None) -> Dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError("event_must_be_object")
    source = raw.get("source")
    if not isinstance(source, str) or not source or len(source) > 80:
        raise ValueError("event_source_required")
    observed = raw.get("observed_at") or datetime.now(timezone.utc).isoformat()
    if not isinstance(observed, str):
        raise ValueError("event_time_invalid")
    try:
        instant = datetime.fromisoformat(observed.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("event_time_invalid") from exc
    if instant.tzinfo is None:
        raise ValueError("event_time_requires_timezone")
    payload = _bounded_payload(raw)
    event_id = raw.get("event_id") or raw.get("message_id") or raw.get("request_id")
    if not event_id:
        stable = json.dumps({"source": source, "payload": payload, "subject": raw.get("subject")},
                            sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        event_id = source + ":" + hashlib.sha256(stable).hexdigest()[:24]
    if not isinstance(event_id, str) or len(event_id) > 160:
        raise ValueError("event_id_invalid")
    metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
    subject = raw.get("subject") or metadata.get("subject") or raw.get("sender_id") or raw.get("type") or "event"
    # The caller must supply the account identity from its authenticated
    # connector. Mail text or inbox JSON cannot claim another account.
    scope = account_scope or "unspecified"
    if not isinstance(scope, str) or not scope or len(scope) > 240:
        raise ValueError("account_scope_invalid")
    sensitivity = raw.get("sensitivity") or ("personal" if source in {"qqmail", "wechat", "matrix", "workspace_watcher"} else "public")
    if sensitivity not in {"public", "personal", "sensitive"}:
        raise ValueError("sensitivity_invalid")
    if source in {"qqmail", "wechat", "matrix", "workspace_watcher"} and sensitivity == "public":
        sensitivity = "personal"
    topic = raw.get("topic") or raw.get("type") or "observation"
    if not isinstance(topic, str) or len(topic) > 120:
        raise ValueError("topic_invalid")
    result = {"event_id": event_id, "source": source, "observed_at": instant.isoformat(),
              "subject": str(subject)[:240], "account_scope": scope,
              "sensitivity": sensitivity, "topic": topic, "payload": payload}
    ref = raw.get("payload_ref")
    if (isinstance(ref, str) and len(ref) <= 160
            and re.fullmatch(r"resource:[A-Za-z0-9._:-]+", ref)
            and allowed_resource_refs is not None and ref in allowed_resource_refs):
        result["payload_ref"] = ref
    return result


class EventDeduper:
    """Persist source/account/event identity across resident worker restarts."""

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / ".muse-event-dedupe.sqlite3"
        if self.path.is_symlink():
            raise ValueError("dedupe_ledger_symlink_rejected")
        _private_database(self.path)

    def accept(self, event: Mapping[str, Any]) -> bool:
        keys = (event.get("source"), event.get("account_scope"), event.get("event_id"))
        if any(not isinstance(value, str) or not value for value in keys):
            raise ValueError("normalized_event_required")
        with sqlite3.connect(str(self.path), timeout=5) as db:
            db.execute("CREATE TABLE IF NOT EXISTS seen (source TEXT, account_scope TEXT, event_id TEXT, "
                       "PRIMARY KEY (source, account_scope, event_id))")
            cursor = db.execute("INSERT OR IGNORE INTO seen VALUES (?, ?, ?)", keys)
            return cursor.rowcount == 1


class WorkspaceWatcher:
    """Observe metadata changes in one user-selected directory, top level only.

    It never reads file contents, follows symlinks, scans hidden entries or
    descends into subdirectories. ``approved`` must be checked on every poll so
    revoking the selected directory stops observation immediately.
    """

    EXTENSIONS = frozenset({".md", ".txt", ".csv"})
    SENSITIVE_NAMES = ("password", "secret", "token", "credential", "private", "key",
                       "payment", "bank", "wallet", "otp", "2fa", "game", "验证码", "密码", "支付", "游戏")
    MAX_ENTRIES = 512
    MAX_FILES = 256
    MAX_FILE_BYTES = 1024 * 1024

    def __init__(self, workspace: Path, watched_root: Path, resource_ref: str):
        if not isinstance(resource_ref, str) or not re.fullmatch(r"resource:[A-Za-z0-9._:-]+", resource_ref):
            raise ValueError("resource_ref_invalid")
        supplied = Path(watched_root).expanduser()
        if not supplied.is_absolute():
            raise ValueError("watched_root_must_be_absolute")
        if supplied.is_symlink():
            raise ValueError("watched_root_symlink_rejected")
        self.root = supplied.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("watched_root_not_directory")
        if self.root in {Path("/"), Path.home().resolve()}:
            raise ValueError("watched_root_too_broad")
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.resource_ref = resource_ref
        identity = hashlib.sha256((str(self.root) + "\n" + resource_ref).encode("utf-8")).hexdigest()[:20]
        self.state_path = self.workspace / (".muse-watch-" + identity + ".json")
        if self.state_path.is_symlink():
            raise ValueError("watch_state_symlink_rejected")
        self.previous = self._load_state()

    def _load_state(self) -> Optional[dict]:
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        if (not isinstance(state, dict) or state.get("root") != str(self.root)
                or state.get("resource_ref") != self.resource_ref or not isinstance(state.get("files"), dict)):
            raise ValueError("watch_state_invalid")
        return state["files"]

    def _scan(self) -> dict:
        files = {}
        directory = os.open(str(self.root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            with os.scandir(directory) as entries:
                examined = 0
                for entry in entries:
                    examined += 1
                    if examined > self.MAX_ENTRIES:
                        raise ValueError("watch_entry_limit_exceeded")
                    name = entry.name
                    lowered = name.lower()
                    if (name.startswith(".") or Path(name).suffix.lower() not in self.EXTENSIONS
                            or any(word in lowered for word in self.SENSITIVE_NAMES)
                            or entry.is_symlink() or not entry.is_file(follow_symlinks=False)):
                        continue
                    details = entry.stat(follow_symlinks=False)
                    files[name] = {"size": details.st_size, "mtime_ns": details.st_mtime_ns,
                                   "inode": details.st_ino}
                    if len(files) > self.MAX_FILES:
                        raise ValueError("watch_file_limit_exceeded")
        finally:
            os.close(directory)
        return files

    def _save_state(self, files: dict) -> None:
        value = {"version": 1, "root": str(self.root), "resource_ref": self.resource_ref, "files": files}
        fd, temporary = tempfile.mkstemp(prefix=".muse-watch-", dir=str(self.workspace))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.state_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def poll(self, *, approved: bool) -> list[dict]:
        if approved is not True:
            return []
        current = self._scan()
        if self.previous is None:
            self._save_state(current)
            self.previous = current
            return []
        if current == self.previous:
            return []
        observed = datetime.now(timezone.utc).isoformat()
        events = []
        for name in sorted(set(current) | set(self.previous)):
            before, after = self.previous.get(name), current.get(name)
            if before == after:
                continue
            before_in_scope = before is not None and before["size"] <= self.MAX_FILE_BYTES
            after_in_scope = after is not None and after["size"] <= self.MAX_FILE_BYTES
            if not before_in_scope and not after_in_scope:
                continue
            if before_in_scope and not after_in_scope and after is not None:
                continue  # Grew beyond the approved observation size, not deleted.
            change = ("created" if before is None else "entered_scope" if not before_in_scope
                      else "deleted" if after is None else "modified")
            identity = json.dumps([str(self.root), self.resource_ref, name, before, after], sort_keys=True)
            event_id = "file:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
            events.append(normalize_event(
                {"source": "workspace_watcher", "event_id": event_id, "observed_at": observed,
                 "subject": name, "topic": "file.changed", "sensitivity": "personal",
                 "payload_ref": self.resource_ref,
                 "payload": {"relative_path": name, "change": change, "size": after["size"] if after else None}},
                account_scope="local-workspace", allowed_resource_refs={self.resource_ref}))
        self._save_state(current)
        self.previous = current
        return events


class WatchRegistry:
    """Persist up to eight explicitly approved directory selections.

    Call ``set`` only from the UI or protected stdin approval route. Inbox
    JSON, model output and observed file contents are never approval sources.
    """

    MAX_ROOTS = 8

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / ".muse-watch-registry.sqlite3"
        if self.path.is_symlink():
            raise ValueError("watch_registry_symlink_rejected")
        _private_database(self.path)
        self._lock = threading.RLock()
        self.last_errors = {}  # type: Dict[str, str]
        with sqlite3.connect(str(self.path), timeout=5) as db:
            db.execute("CREATE TABLE IF NOT EXISTS watched (resource_ref TEXT PRIMARY KEY, "
                       "root TEXT NOT NULL UNIQUE, approved_at TEXT NOT NULL)")

    def set(self, root: Path, *, approved: bool) -> dict:
        if approved is not True:
            raise PermissionError("directory_selection_requires_approval")
        selected = Path(root).expanduser()
        if not selected.is_absolute():
            raise ValueError("watched_root_must_be_absolute")
        if selected.is_symlink():
            raise ValueError("watched_root_symlink_rejected")
        selected = selected.resolve(strict=True)
        if selected in {Path("/"), Path.home().resolve()} or not selected.is_dir():
            raise ValueError("watched_root_too_broad_or_unavailable")
        with self._lock, sqlite3.connect(str(self.path), timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT resource_ref,approved_at FROM watched WHERE root=?",
                                  (str(selected),)).fetchone()
            if existing:
                ref, approved_at = existing
            else:
                count = db.execute("SELECT COUNT(*) FROM watched").fetchone()[0]
                if count >= self.MAX_ROOTS:
                    raise ValueError("watch_root_limit_exceeded")
                # A fresh approval receives a fresh identity. Revoking and
                # reselecting the same path cannot revive an old Goal trigger.
                ref = "resource:folder-" + secrets.token_hex(10)
                approved_at = datetime.now(timezone.utc).isoformat()
                db.execute("INSERT INTO watched VALUES (?, ?, ?)", (ref, str(selected), approved_at))
            WorkspaceWatcher(self.workspace, selected, ref)
            return {"resource_ref": ref, "root": str(selected), "approved_at": approved_at}

    def list(self) -> list[dict]:
        with self._lock, sqlite3.connect(str(self.path), timeout=5) as db:
            rows = db.execute("SELECT resource_ref, root, approved_at FROM watched ORDER BY approved_at").fetchall()
        return [{"resource_ref": ref, "root": root, "approved_at": when} for ref, root, when in rows]

    def is_active(self, resource_ref: str) -> bool:
        with self._lock, sqlite3.connect(str(self.path), timeout=5) as db:
            return db.execute("SELECT 1 FROM watched WHERE resource_ref=?", (resource_ref,)).fetchone() is not None

    def revoke(self, resource_ref: str) -> bool:
        with self._lock, sqlite3.connect(str(self.path), timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT root FROM watched WHERE resource_ref=?", (resource_ref,)).fetchone()
            if row is None:
                return False
            db.execute("DELETE FROM watched WHERE resource_ref=?", (resource_ref,))
            identity = hashlib.sha256((row[0] + "\n" + resource_ref).encode("utf-8")).hexdigest()[:20]
            (self.workspace / (".muse-watch-" + identity + ".json")).unlink(missing_ok=True)
            self.last_errors.pop(resource_ref, None)
            return True

    def poll(self) -> list[dict]:
        with self._lock:
            events = []
            self.last_errors = {}
            for item in self.list():
                try:
                    watcher = WorkspaceWatcher(self.workspace, Path(item["root"]), item["resource_ref"])
                    events.extend(watcher.poll(approved=True))
                except (OSError, ValueError) as exc:
                    self.last_errors[item["resource_ref"]] = str(exc)[:160]
            return events
