"""SQLite registry for reviewed Capability DSL declarations.

The registry describes callable adapters. Runtime approval and execution remain
with the host and CapabilityExecutor; a staged document cannot grant itself use.
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from muse_dsl import DslValidationError, decode_document, encode_document


class CapabilityCatalog:
    def __init__(self, workspace: Path):
        self.path = Path(workspace) / "memory.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _migrate(self) -> None:
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS muse_capability_documents ("
                       "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                       "capability_id TEXT NOT NULL, revision INTEGER NOT NULL, digest TEXT NOT NULL, "
                       "document_json TEXT NOT NULL, status TEXT NOT NULL, reviewed_at TEXT, "
                       "PRIMARY KEY(project,account,visibility,capability_id))")

    @staticmethod
    def _scope(scope: Dict[str, str]) -> tuple[str, str, str]:
        if not isinstance(scope, dict) or set(scope) != {"project", "account", "visibility"}:
            raise DslValidationError("scope_invalid")
        values = (scope["project"], scope["account"], scope["visibility"])
        if any(not isinstance(value, str) or not 1 <= len(value) <= 160 for value in values):
            raise DslValidationError("scope_invalid")
        if values[2] not in {"personal", "project", "shared"}:
            raise DslValidationError("scope_visibility_invalid")
        return values

    def stage(self, document: Dict[str, Any]) -> Dict[str, Any]:
        encoded = encode_document(document)
        if document["kind"] != "capability":
            raise DslValidationError("capability_document_required")
        scope = self._scope(document["scope"])
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT revision,digest FROM muse_capability_documents WHERE project=? "
                                 "AND account=? AND visibility=? AND capability_id=?",
                                 (*scope, document["id"])).fetchone()
            if current and current["digest"] == digest:
                return self.get(document["id"], document["scope"])
            if (current and document["revision"] != current["revision"] + 1) or (
                not current and document["revision"] != 1
            ):
                raise DslValidationError("capability_revision_invalid")
            db.execute("INSERT INTO muse_capability_documents VALUES (?,?,?,?,?,?,?,'staged',NULL) "
                       "ON CONFLICT(project,account,visibility,capability_id) DO UPDATE SET "
                       "revision=excluded.revision,digest=excluded.digest,document_json=excluded.document_json,"
                       "status='staged',reviewed_at=NULL",
                       (*scope, document["id"], document["revision"], digest, encoded))
        return self.get(document["id"], document["scope"])

    def approve(self, capability_id: str, revision: int, digest: str, scope: Dict[str, str],
                *, trusted_adapters: frozenset[str]) -> bool:
        """Host call after reviewing the exact document and installed adapter."""
        if not isinstance(trusted_adapters, frozenset):
            raise DslValidationError("trusted_adapter_set_required")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision,digest,document_json FROM muse_capability_documents "
                             "WHERE project=? AND account=? AND visibility=? AND capability_id=?",
                             (*self._scope(scope), capability_id)).fetchone()
            if not row or row["revision"] != revision or row["digest"] != digest:
                return False
            document = decode_document(row["document_json"])
            if document["payload"]["adapter"] not in trusted_adapters:
                return False
            db.execute("UPDATE muse_capability_documents SET status='enabled',reviewed_at=? WHERE project=? "
                       "AND account=? AND visibility=? AND capability_id=?",
                       (datetime.now(timezone.utc).isoformat(), *self._scope(scope), capability_id))
        return True

    def revoke(self, capability_id: str, scope: Dict[str, str]) -> bool:
        with self._connect() as db:
            cursor = db.execute("UPDATE muse_capability_documents SET status='revoked' WHERE project=? "
                                "AND account=? AND visibility=? AND capability_id=? AND status='enabled'",
                                (*self._scope(scope), capability_id))
        return cursor.rowcount == 1

    def get(self, capability_id: str, scope: Dict[str, str]) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            row = db.execute("SELECT revision,digest,document_json,status,reviewed_at "
                             "FROM muse_capability_documents WHERE project=? AND account=? AND visibility=? "
                             "AND capability_id=?", (*self._scope(scope), capability_id)).fetchone()
        if not row:
            return None
        return {"document": decode_document(row["document_json"]), "digest": row["digest"],
                "status": row["status"], "enabled": row["status"] == "enabled",
                "reviewed_at": row["reviewed_at"]}

    def list(self, scope: Dict[str, str]) -> List[Dict[str, Any]]:
        with self._connect() as db:
            ids = [row["capability_id"] for row in db.execute(
                "SELECT capability_id FROM muse_capability_documents WHERE project=? AND account=? "
                "AND visibility=? ORDER BY capability_id", self._scope(scope))]
        return [self.get(capability_id, scope) for capability_id in ids]
