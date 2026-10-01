"""Local, searchable memory for chats, message summaries, and selected files."""

from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union

from muse_memory_graph import MemoryGraph


TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".rst", ".csv", ".json"}
MAX_FILE_BYTES = 128 * 1024
MAX_INDEX_FILES = 200


class MemoryStore:
    def __init__(self, workspace: Path):
        self.path = workspace / "memory.sqlite3"
        workspace.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS memories ("
                "id INTEGER PRIMARY KEY, kind TEXT NOT NULL, source TEXT NOT NULL, "
                "external_id TEXT UNIQUE, content TEXT NOT NULL, created_at TEXT NOT NULL)"
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(memories)")}
            additions = {
                "scope": "TEXT NOT NULL DEFAULT 'personal'",
                "account_scope": "TEXT NOT NULL DEFAULT 'local'",
                "record_type": "TEXT NOT NULL DEFAULT 'raw'",
                "confidence": "REAL NOT NULL DEFAULT 1.0",
                "confirmed": "INTEGER NOT NULL DEFAULT 0",
                "pinned": "INTEGER NOT NULL DEFAULT 0",
                "deleted_at": "TEXT",
            }
            for name, definition in additions.items():
                if name not in columns:
                    db.execute(f"ALTER TABLE memories ADD COLUMN {name} {definition}")
            db.execute(
                "CREATE TABLE IF NOT EXISTS muse_memory_settings ("
                "scope TEXT NOT NULL, account_scope TEXT NOT NULL, recording INTEGER NOT NULL, "
                "PRIMARY KEY(scope, account_scope))"
            )
        os.chmod(self.path, 0o600)
        self.graph = MemoryGraph(self.path)

    def put_source(self, source: Dict[str, str], scope: Dict[str, str]) -> None:
        self.graph.put_source(source, scope)

    def put_claim(self, document: Dict[str, object]) -> None:
        self.graph.put_claim(document)

    def get_claim(self, claim_id: str, scope: Dict[str, str]) -> Optional[Dict[str, object]]:
        return self.graph.get_claim(claim_id, scope)

    def get_claim_revision(self, claim_id: str, revision: int,
                           scope: Dict[str, str]) -> Optional[Dict[str, object]]:
        return self.graph.get_claim_revision(claim_id, revision, scope)

    def correct_claim(self, claim_id: str, content: str, scope: Dict[str, str], *, user_ref: str) -> bool:
        return self.graph.correct_claim(claim_id, content, scope, user_ref=user_ref)

    def pin_claim(self, claim_id: str, pinned: bool, scope: Dict[str, str]) -> bool:
        return self.graph.pin_claim(claim_id, pinned, scope)

    def find_claims(self, scope: Dict[str, str], *, subject_id: Optional[str] = None,
                    predicate: Optional[str] = None, limit: int = 30) -> List[Dict[str, object]]:
        return self.graph.find_claims(scope, subject_id=subject_id, predicate=predicate, limit=limit)

    def explain_claim(self, claim_id: str, scope: Dict[str, str]) -> Optional[Dict[str, object]]:
        return self.graph.explain_claim(claim_id, scope)

    def delete_claim(self, claim_id: str, scope: Dict[str, str]) -> bool:
        return self.graph.delete_claim(claim_id, scope)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.path), timeout=5)

    def remember(self, kind: str, source: str, content: str, external_id: Optional[str] = None,
                 *, scope: str = "personal", account_scope: str = "local",
                 record_type: str = "raw", confidence: float = 1.0,
                 confirmed: bool = False) -> None:
        self._validate_scope(scope, account_scope)
        if record_type not in {"raw", "index", "fact", "inference"} or not 0 <= confidence <= 1 or type(confirmed) is not bool:
            raise ValueError("invalid_memory_metadata")
        value = content.strip()[:2000]
        if not value or not self.recording_enabled(scope, account_scope):
            return
        scoped_id = (f"{scope}:{account_scope}:{external_id}" if external_id and
                     (scope, account_scope) != ("personal", "local") else external_id)
        with self._connect() as db:
            db.execute(
                "INSERT INTO memories(kind, source, external_id, content, created_at, scope, "
                "account_scope, record_type, confidence, confirmed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(external_id) DO UPDATE SET content=excluded.content, "
                "created_at=excluded.created_at, record_type=excluded.record_type, "
                "confidence=excluded.confidence, confirmed=excluded.confirmed WHERE memories.deleted_at IS NULL",
                (kind, source, scoped_id, value, datetime.now(timezone.utc).isoformat(),
                 scope, account_scope, record_type, confidence, int(confirmed)),
            )

    @staticmethod
    def _validate_scope(scope: str, account_scope: str) -> None:
        if not all(isinstance(item, str) and 1 <= len(item) <= 160 and "\x00" not in item
                   for item in (scope, account_scope)):
            raise ValueError("invalid_memory_scope")

    def recording_enabled(self, scope: str = "personal", account_scope: str = "local") -> bool:
        self._validate_scope(scope, account_scope)
        with self._connect() as db:
            row = db.execute("SELECT recording FROM muse_memory_settings WHERE scope=? AND account_scope=?",
                             (scope, account_scope)).fetchone()
        return row is None or bool(row[0])

    def set_recording(self, enabled: bool, *, scope: str = "personal", account_scope: str = "local") -> None:
        self._validate_scope(scope, account_scope)
        if type(enabled) is not bool:
            raise ValueError("recording_must_be_boolean")
        with self._connect() as db:
            db.execute("INSERT INTO muse_memory_settings VALUES (?,?,?) ON CONFLICT(scope,account_scope) "
                       "DO UPDATE SET recording=excluded.recording", (scope, account_scope, int(enabled)))

    @staticmethod
    def _query_terms(query: str) -> List[str]:
        words = [word for word in query.strip()[:120].split() if word][:5]
        for span in re.findall(r"[\u4e00-\u9fff]{2,}", query[:120]):
            for width in (4, 3, 2):
                for index in range(len(span) - width + 1):
                    words.append(span[index:index + width])
                    if len(words) >= 24:
                        break
                if len(words) >= 24:
                    break
            if len(words) >= 24:
                break
        return list(dict.fromkeys(words))[:24]

    def search(self, query: str, limit: int = 6, *, scope: str = "personal",
               account_scope: str = "local") -> List[Dict[str, str]]:
        self._validate_scope(scope, account_scope)
        words = self._query_terms(query)
        if not words:
            return []
        clauses = " OR ".join("content LIKE ? ESCAPE '\\'" for _ in words)
        patterns = ["%" + word.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%" for word in words]
        with self._connect() as db:
            rows = db.execute(
                f"SELECT kind, source, content, created_at FROM memories WHERE deleted_at IS NULL "
                f"AND scope=? AND account_scope=? AND ({clauses}) "
                "ORDER BY pinned DESC, confirmed DESC, created_at DESC LIMIT ?",
                (scope, account_scope, *patterns, max(1, min(limit, 20))),
            ).fetchall()
        return [dict(zip(("kind", "source", "content", "created_at"), row)) for row in rows]

    def search_goal_results(self, query: str, account_scopes: List[str],
                            limit: int = 6) -> List[Dict[str, object]]:
        """Search only bounded goal summaries in scopes explicitly supplied by the caller."""
        if not isinstance(account_scopes, list) or not 1 <= len(account_scopes) <= 8:
            raise ValueError("explicit_account_scopes_required")
        for account_scope in account_scopes:
            self._validate_scope("personal", account_scope)
        scopes = [item for item in dict.fromkeys(account_scopes)
                  if self.recording_enabled("personal", item)]
        words = self._query_terms(query)
        if not scopes or not words:
            return []
        scope_slots = ",".join("?" for _ in scopes)
        clauses = " OR ".join("content LIKE ? ESCAPE '\\'" for _ in words)
        patterns = ["%" + word.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
                    for word in words]
        with self._connect() as db:
            rows = db.execute(
                "SELECT kind,source,content,created_at,scope,account_scope,record_type,confirmed "
                "FROM memories WHERE deleted_at IS NULL AND kind='goal_result' AND scope='personal' "
                f"AND account_scope IN ({scope_slots}) AND ({clauses}) "
                "ORDER BY confirmed DESC,created_at DESC LIMIT ?",
                (*scopes, *patterns, max(1, min(limit, 20))),
            ).fetchall()
        keys = ("kind", "source", "content", "created_at", "scope", "account_scope", "record_type", "confirmed")
        return [dict(zip(keys, row)) for row in rows]

    def list_goal_result_scopes(self) -> List[str]:
        """Discover scopes with retained goal summaries; the caller still authorizes retrieval."""
        with self._connect() as db:
            rows = db.execute("SELECT DISTINCT account_scope FROM memories WHERE scope='personal' "
                              "AND kind='goal_result' AND deleted_at IS NULL ORDER BY account_scope").fetchall()
        return [row[0] for row in rows if self.recording_enabled("personal", row[0])]

    def recent(self, limit: int = 8, *, scope: str = "personal", account_scope: str = "local") -> List[Dict[str, str]]:
        self._validate_scope(scope, account_scope)
        with self._connect() as db:
            rows = db.execute(
                "SELECT kind, source, content, created_at FROM memories "
                "WHERE deleted_at IS NULL AND scope=? AND account_scope=? AND "
                "kind IN ('chat_user', 'chat_assistant') ORDER BY id DESC LIMIT ?",
                (scope, account_scope, max(1, min(limit, 20))),
            ).fetchall()
        return [dict(zip(("kind", "source", "content", "created_at"), row)) for row in reversed(rows)]

    def recent_any(self, limit: int = 4, *, scope: str = "personal", account_scope: str = "local") -> List[Dict[str, str]]:
        self._validate_scope(scope, account_scope)
        with self._connect() as db:
            rows = db.execute(
                "SELECT kind, source, content, created_at FROM memories "
                "WHERE deleted_at IS NULL AND scope=? AND account_scope=? "
                "ORDER BY id DESC LIMIT ?", (scope, account_scope, max(1, min(limit, 20)))
            ).fetchall()
        return [dict(zip(("kind", "source", "content", "created_at"), row)) for row in rows]

    def count(self, *, scope: str = "personal", account_scope: str = "local") -> int:
        self._validate_scope(scope, account_scope)
        with self._connect() as db:
            return db.execute("SELECT COUNT(*) FROM memories WHERE deleted_at IS NULL AND "
                              "scope=? AND account_scope=?", (scope, account_scope)).fetchone()[0]

    def list_records(self, limit: int = 30, *, scope: str = "personal",
                     account_scope: str = "local") -> List[Dict[str, object]]:
        self._validate_scope(scope, account_scope)
        with self._connect() as db:
            rows = db.execute("SELECT id,kind,source,content,created_at,record_type,confidence,"
                              "confirmed,pinned FROM memories WHERE deleted_at IS NULL AND "
                              "scope=? AND account_scope=? ORDER BY pinned DESC,id DESC LIMIT ?",
                              (scope, account_scope, max(1, min(limit, 100)))).fetchall()
        keys = ("id", "kind", "source", "content", "created_at", "record_type", "confidence", "confirmed", "pinned")
        return [dict(zip(keys, row)) for row in rows]

    def correct(self, record_id: int, content: str, *, scope: str = "personal",
                account_scope: str = "local") -> bool:
        self._validate_scope(scope, account_scope)
        if type(record_id) is not int or not isinstance(content, str) or not content.strip():
            raise ValueError("invalid_memory_correction")
        with self._connect() as db:
            cursor = db.execute("UPDATE memories SET content=?,record_type='fact',confidence=1.0,"
                                "confirmed=1,created_at=? WHERE id=? AND scope=? AND account_scope=? "
                                "AND deleted_at IS NULL",
                                (content.strip()[:2000], datetime.now(timezone.utc).isoformat(),
                                 record_id, scope, account_scope))
        return cursor.rowcount == 1

    def pin(self, record_id: int, pinned: bool, *, scope: str = "personal",
            account_scope: str = "local") -> bool:
        self._validate_scope(scope, account_scope)
        if type(record_id) is not int or type(pinned) is not bool:
            raise ValueError("invalid_memory_pin")
        with self._connect() as db:
            cursor = db.execute("UPDATE memories SET pinned=? WHERE id=? AND scope=? AND account_scope=? "
                                "AND deleted_at IS NULL", (int(pinned), record_id, scope, account_scope))
        return cursor.rowcount == 1

    def delete(self, record_id: int, *, scope: str = "personal", account_scope: str = "local") -> bool:
        """Keep only a tombstone so a selected folder cannot re-add this item."""
        self._validate_scope(scope, account_scope)
        if type(record_id) is not int:
            raise ValueError("invalid_memory_id")
        graph_deleted = False
        with self._connect() as db:
            row = db.execute("SELECT kind,external_id FROM memories WHERE id=? AND scope=? AND "
                             "account_scope=? AND deleted_at IS NULL",
                             (record_id, scope, account_scope)).fetchone()
        if row and row[0] == "goal_result" and row[1] and "muse:run:" in row[1]:
            run_id = "run:" + row[1].rsplit("muse:run:", 1)[1]
            graph_deleted = self.graph.delete_claim(
                "memory:" + run_id,
                {"project": "gosim-muse", "account": account_scope, "visibility": "personal"})
        with self._connect() as db:
            cursor = db.execute("UPDATE memories SET content='',deleted_at=? WHERE id=? AND "
                                "scope=? AND account_scope=? AND deleted_at IS NULL",
                                (datetime.now(timezone.utc).isoformat(), record_id, scope, account_scope))
        return graph_deleted or cursor.rowcount == 1

    def index_folder(self, folder: Path) -> Dict[str, Union[int, str]]:
        """Read bounded text files under a user-selected folder; never follow symlinks."""
        root = folder.expanduser().resolve()
        if not root.is_dir():
            return {"status": "REJECTED", "reason": "folder_not_found", "indexed": 0, "skipped": 0}
        indexed = skipped = inspected = 0
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if not name.startswith(".") and not (Path(directory) / name).is_symlink()]
            for name in files:
                inspected += 1
                if indexed >= MAX_INDEX_FILES or inspected > 5000:
                    break
                path = Path(directory) / name
                if name.startswith(".") or path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    if path.stat().st_size > MAX_FILE_BYTES:
                        skipped += 1
                        continue
                    content = path.read_text(encoding="utf-8")[:2000]
                    self.remember("file", str(path), content, f"file:{path}")
                    indexed += 1
                except (OSError, UnicodeError):
                    skipped += 1
            if indexed >= MAX_INDEX_FILES or inspected > 5000:
                break
        return {"status": "COMPLETED", "root": str(root), "indexed": indexed, "skipped": skipped}
