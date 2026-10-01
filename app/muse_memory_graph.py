"""Source-backed memory claims in the existing SQLite workspace database."""

from __future__ import annotations

import copy
import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from muse_dsl import DslValidationError, decode_document, encode_document


_HASH = re.compile(r"[0-9a-f]{64}\Z")


class MemoryGraph:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _migrate(self) -> None:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS muse_memory_graph_migrations "
                       "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
            if not db.execute("SELECT 1 FROM muse_memory_graph_migrations WHERE version=1").fetchone():
                db.execute("CREATE TABLE muse_memory_sources ("
                       "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                       "source_id TEXT NOT NULL, kind TEXT NOT NULL, locator TEXT NOT NULL, "
                       "content_sha256 TEXT NOT NULL, observed_at TEXT NOT NULL, updated_at TEXT NOT NULL, "
                       "PRIMARY KEY(project,account,visibility,source_id))")
                db.execute("CREATE TABLE muse_memory_claims ("
                       "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                       "claim_id TEXT NOT NULL, revision INTEGER NOT NULL, subject_id TEXT NOT NULL, "
                       "predicate TEXT NOT NULL, epistemic_type TEXT NOT NULL, deleted INTEGER NOT NULL, "
                       "document_json TEXT NOT NULL, PRIMARY KEY(project,account,visibility,claim_id))")
                db.execute("CREATE INDEX muse_memory_claim_lookup ON muse_memory_claims "
                       "(project,account,visibility,subject_id,predicate,deleted)")
                db.execute("CREATE TABLE muse_memory_relations ("
                       "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                       "from_id TEXT NOT NULL, to_id TEXT NOT NULL, kind TEXT NOT NULL, "
                       "PRIMARY KEY(project,account,visibility,from_id,to_id,kind))")
                db.execute("CREATE TABLE muse_memory_forget ("
                       "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                       "content_sha256 TEXT NOT NULL, subject_id TEXT NOT NULL, predicate TEXT NOT NULL, "
                       "forgot_at TEXT NOT NULL, PRIMARY KEY(project,account,visibility,content_sha256,subject_id,predicate))")
                db.execute("INSERT INTO muse_memory_graph_migrations VALUES (1,?)",
                           (datetime.now(timezone.utc).isoformat(),))
            if not db.execute("SELECT 1 FROM muse_memory_graph_migrations WHERE version=2").fetchone():
                db.execute("CREATE TABLE muse_memory_claim_revisions ("
                           "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                           "claim_id TEXT NOT NULL, revision INTEGER NOT NULL, document_json TEXT NOT NULL, "
                           "PRIMARY KEY(project,account,visibility,claim_id,revision))")
                db.execute("INSERT INTO muse_memory_claim_revisions SELECT project,account,visibility,claim_id,"
                           "revision,document_json FROM muse_memory_claims")
                db.execute("CREATE TABLE muse_memory_pins ("
                           "project TEXT NOT NULL, account TEXT NOT NULL, visibility TEXT NOT NULL, "
                           "claim_id TEXT NOT NULL, PRIMARY KEY(project,account,visibility,claim_id))")
                db.execute("INSERT INTO muse_memory_graph_migrations VALUES (2,?)",
                           (datetime.now(timezone.utc).isoformat(),))

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

    def put_source(self, source: Dict[str, str], scope: Dict[str, str]) -> None:
        keys = {"source_id", "kind", "locator", "content_sha256", "observed_at", "updated_at"}
        if not isinstance(source, dict) or set(source) != keys:
            raise DslValidationError("source_fields_invalid")
        if (not isinstance(source["source_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,159}", source["source_id"])
                or source["kind"] not in {"url", "file", "user", "runtime_receipt"}
                or not isinstance(source["locator"], str) or not 1 <= len(source["locator"]) <= 2048
                or not isinstance(source["content_sha256"], str) or not _HASH.fullmatch(source["content_sha256"])):
            raise DslValidationError("source_invalid")
        for field in ("observed_at", "updated_at"):
            try:
                if datetime.fromisoformat(source[field].replace("Z", "+00:00")).tzinfo is None:
                    raise ValueError("timezone_required")
            except (ValueError, TypeError, AttributeError) as exc:
                raise DslValidationError("source_time_invalid") from exc
        scoped = self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM muse_memory_sources WHERE project=? AND account=? AND "
                             "visibility=? AND source_id=?", (*scoped, source["source_id"])).fetchone()
            if row and (row["content_sha256"] != source["content_sha256"] or row["locator"] != source["locator"]):
                raise DslValidationError("source_id_conflict")
            if not row:
                db.execute("INSERT INTO muse_memory_sources VALUES (?,?,?,?,?,?,?,?,?)",
                           (*scoped, *[source[key] for key in ("source_id", "kind", "locator", "content_sha256",
                                                                 "observed_at", "updated_at")]))

    def put_claim(self, document: Dict[str, Any]) -> None:
        encoded = encode_document(document)
        if document["kind"] != "memory" or document["payload"]["deleted"]:
            raise DslValidationError("active_memory_document_required")
        scoped = self._scope(document["scope"])
        payload = document["payload"]
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT revision,deleted FROM muse_memory_claims WHERE project=? AND account=? "
                             "AND visibility=? AND claim_id=?", (*scoped, document["id"])).fetchone()
            if (old and (old["deleted"] or document["revision"] != old["revision"] + 1)) or (
                not old and document["revision"] != 1
            ):
                raise DslValidationError("claim_revision_invalid")
            for source_id in payload["source_ids"]:
                source = db.execute("SELECT content_sha256 FROM muse_memory_sources WHERE project=? AND "
                                    "account=? AND visibility=? AND source_id=?", (*scoped, source_id)).fetchone()
                if not source:
                    raise DslValidationError("source_not_found_in_scope")
                if db.execute("SELECT 1 FROM muse_memory_forget WHERE project=? AND account=? AND "
                              "visibility=? AND content_sha256=? AND subject_id=? AND predicate=?",
                              (*scoped, source["content_sha256"], payload["subject_id"], payload["predicate"])).fetchone():
                    raise DslValidationError("forgotten_source_cannot_reimport")
            for relation in payload["relations"]:
                target = db.execute("SELECT 1 FROM muse_memory_claims WHERE project=? AND account=? AND "
                                    "visibility=? AND claim_id=? AND deleted=0",
                                    (*scoped, relation["target_id"])).fetchone()
                if not target:
                    raise DslValidationError("relation_target_not_found_in_scope")
                if relation["kind"] == "supersedes" and db.execute(
                    "WITH RECURSIVE chain(id) AS (SELECT to_id FROM muse_memory_relations WHERE project=? "
                    "AND account=? AND visibility=? AND from_id=? AND kind='supersedes' UNION "
                    "SELECT r.to_id FROM muse_memory_relations r JOIN chain c ON r.from_id=c.id "
                    "WHERE r.project=? AND r.account=? AND r.visibility=? AND r.kind='supersedes') "
                    "SELECT 1 FROM chain WHERE id=? LIMIT 1",
                    (*scoped, relation["target_id"], *scoped, document["id"])).fetchone():
                    raise DslValidationError("supersedes_cycle")
            if old:
                db.execute("UPDATE muse_memory_claims SET revision=?,subject_id=?,predicate=?,epistemic_type=?,"
                           "document_json=? WHERE project=? AND account=? AND visibility=? AND claim_id=?",
                           (document["revision"], payload["subject_id"], payload["predicate"],
                            payload["epistemic_type"], encoded, *scoped, document["id"]))
            else:
                db.execute("INSERT INTO muse_memory_claims VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (*scoped, document["id"], document["revision"], payload["subject_id"],
                            payload["predicate"], payload["epistemic_type"], 0, encoded))
            db.execute("INSERT INTO muse_memory_claim_revisions VALUES (?,?,?,?,?,?)",
                       (*scoped, document["id"], document["revision"], encoded))
            db.execute("DELETE FROM muse_memory_relations WHERE project=? AND account=? AND visibility=? AND from_id=?",
                       (*scoped, document["id"]))
            for relation in payload["relations"]:
                db.execute("INSERT INTO muse_memory_relations VALUES (?,?,?,?,?,?)",
                           (*scoped, document["id"], relation["target_id"], relation["kind"]))

    def get_claim(self, claim_id: str, scope: Dict[str, str]) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            row = db.execute("SELECT document_json FROM muse_memory_claims WHERE project=? AND account=? AND "
                             "visibility=? AND claim_id=?", (*self._scope(scope), claim_id)).fetchone()
        return decode_document(row["document_json"]) if row else None

    def get_claim_revision(self, claim_id: str, revision: int,
                           scope: Dict[str, str]) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            active = db.execute("SELECT deleted FROM muse_memory_claims WHERE project=? AND account=? AND "
                                "visibility=? AND claim_id=?", (*self._scope(scope), claim_id)).fetchone()
            if not active or active["deleted"]:
                return None
            row = db.execute("SELECT document_json FROM muse_memory_claim_revisions WHERE project=? AND "
                             "account=? AND visibility=? AND claim_id=? AND revision=?",
                             (*self._scope(scope), claim_id, revision)).fetchone()
        return decode_document(row["document_json"]) if row else None

    def correct_claim(self, claim_id: str, content: str, scope: Dict[str, str], *, user_ref: str) -> bool:
        if not isinstance(content, str) or not 1 <= len(content.strip()) <= 4000 or (
            not isinstance(user_ref, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,159}", user_ref)
        ):
            raise DslValidationError("invalid_memory_correction")
        current = self.get_claim(claim_id, scope)
        if not current or current["payload"]["deleted"]:
            return False
        revised = copy.deepcopy(current)
        revised["revision"] += 1
        now = datetime.now(timezone.utc).isoformat()
        revised["updated_at"] = now
        source_id = "source:user:" + hashlib.sha256(
            (claim_id + str(revised["revision"]) + content).encode("utf-8")).hexdigest()[:32]
        self.put_source({"source_id": source_id, "kind": "user", "locator": "user-correction:" + user_ref,
                         "content_sha256": hashlib.sha256(content.strip().encode("utf-8")).hexdigest(),
                         "observed_at": now, "updated_at": now}, scope)
        revised["origin"] = {"type": "user", "ref": user_ref}
        revised["payload"].update(value=content.strip(), epistemic_type="user_statement",
                                  source_ids=[source_id], observed_at=now)
        self.put_claim(revised)
        return True

    def pin_claim(self, claim_id: str, pinned: bool, scope: Dict[str, str]) -> bool:
        if type(pinned) is not bool:
            raise DslValidationError("invalid_memory_pin")
        current = self.get_claim(claim_id, scope)
        if not current or current["payload"]["deleted"]:
            return False
        with self._connect() as db:
            if pinned:
                db.execute("INSERT OR IGNORE INTO muse_memory_pins VALUES (?,?,?,?)",
                           (*self._scope(scope), claim_id))
            else:
                db.execute("DELETE FROM muse_memory_pins WHERE project=? AND account=? AND visibility=? AND "
                           "claim_id=?", (*self._scope(scope), claim_id))
        return True

    def find_claims(self, scope: Dict[str, str], *, subject_id: Optional[str] = None,
                    predicate: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
        query = ("SELECT c.document_json FROM muse_memory_claims c LEFT JOIN muse_memory_pins p "
                 "ON p.project=c.project AND p.account=c.account AND p.visibility=c.visibility "
                 "AND p.claim_id=c.claim_id WHERE c.project=? AND c.account=? AND c.visibility=? AND c.deleted=0")
        params: tuple[Any, ...] = self._scope(scope)
        for name, value in (("subject_id", subject_id), ("predicate", predicate)):
            if value is not None:
                query += " AND c." + name + "=?"
                params += (value,)
        query += " ORDER BY (p.claim_id IS NOT NULL) DESC,c.claim_id LIMIT ?"
        with self._connect() as db:
            rows = db.execute(query, (*params, max(1, min(limit, 100)))).fetchall()
        return [decode_document(row["document_json"]) for row in rows]

    def explain_claim(self, claim_id: str, scope: Dict[str, str]) -> Optional[Dict[str, Any]]:
        document = self.get_claim(claim_id, scope)
        if document is None:
            return None
        ids = document["payload"]["source_ids"]
        with self._connect() as db:
            sources = [dict(row) for source_id in ids for row in db.execute(
                "SELECT source_id,kind,locator,content_sha256,observed_at,updated_at FROM muse_memory_sources "
                "WHERE project=? AND account=? AND visibility=? AND source_id=?",
                (*self._scope(scope), source_id)).fetchall()]
            pinned = db.execute("SELECT 1 FROM muse_memory_pins WHERE project=? AND account=? AND "
                                "visibility=? AND claim_id=?", (*self._scope(scope), claim_id)).fetchone()
        return {"document": document, "sources": sources, "pinned": bool(pinned)}

    def delete_claim(self, claim_id: str, scope: Dict[str, str]) -> bool:
        scoped = self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT document_json FROM muse_memory_claims WHERE project=? AND account=? AND "
                             "visibility=? AND claim_id=? AND deleted=0", (*scoped, claim_id)).fetchone()
            if not row:
                return False
            document = decode_document(row["document_json"])
            payload = document["payload"]
            now = datetime.now(timezone.utc).isoformat()
            revisions = db.execute("SELECT document_json FROM muse_memory_claim_revisions WHERE project=? AND "
                                   "account=? AND visibility=? AND claim_id=?",
                                   (*scoped, claim_id)).fetchall()
            old_payloads = [decode_document(old["document_json"])["payload"] for old in revisions]
            source_claims = {(source_id, old["subject_id"], old["predicate"])
                             for old in old_payloads for source_id in old["source_ids"]}
            source_claims.update((source_id, payload["subject_id"], payload["predicate"])
                                 for source_id in payload["source_ids"])
            for source_id, subject_id, predicate in source_claims:
                source = db.execute("SELECT content_sha256,kind,locator FROM muse_memory_sources WHERE project=? AND "
                                    "account=? AND visibility=? AND source_id=?", (*scoped, source_id)).fetchone()
                db.execute("INSERT OR IGNORE INTO muse_memory_forget VALUES (?,?,?,?,?,?,?)",
                           (*scoped, source["content_sha256"], subject_id, predicate, now))
                if source["kind"] == "runtime_receipt":
                    external_id = (f"personal:{scoped[1]}:muse:{source['locator']}" if scoped[1] != "local"
                                   else "muse:" + source["locator"])
                    db.execute("UPDATE memories SET content='',deleted_at=? WHERE external_id=? AND "
                               "scope='personal' AND account_scope=? AND deleted_at IS NULL",
                               (now, external_id, scoped[1]))
            document["revision"] += 1
            document["updated_at"] = now
            payload.update(value="", source_ids=[], relations=[], deleted=True)
            db.execute("UPDATE muse_memory_claims SET revision=?,deleted=1,document_json=? WHERE project=? "
                       "AND account=? AND visibility=? AND claim_id=?",
                       (document["revision"], encode_document(document), *scoped, claim_id))
            db.execute("DELETE FROM muse_memory_claim_revisions WHERE project=? AND account=? AND "
                       "visibility=? AND claim_id=?", (*scoped, claim_id))
            db.execute("INSERT INTO muse_memory_claim_revisions VALUES (?,?,?,?,?,?)",
                       (*scoped, claim_id, document["revision"], encode_document(document)))
            db.execute("DELETE FROM muse_memory_pins WHERE project=? AND account=? AND visibility=? AND claim_id=?",
                       (*scoped, claim_id))
            incoming = db.execute("SELECT DISTINCT from_id FROM muse_memory_relations WHERE project=? AND "
                                  "account=? AND visibility=? AND to_id=?", (*scoped, claim_id)).fetchall()
            for relation_row in incoming:
                from_id = relation_row["from_id"]
                current = db.execute("SELECT document_json FROM muse_memory_claims WHERE project=? AND "
                                     "account=? AND visibility=? AND claim_id=? AND deleted=0",
                                     (*scoped, from_id)).fetchone()
                if not current:
                    continue
                revised = decode_document(current["document_json"])
                revised["revision"] += 1
                revised["updated_at"] = now
                revised["payload"]["relations"] = [relation for relation in revised["payload"]["relations"]
                                                   if relation["target_id"] != claim_id]
                db.execute("UPDATE muse_memory_claims SET revision=?,document_json=? WHERE project=? AND "
                           "account=? AND visibility=? AND claim_id=?",
                           (revised["revision"], encode_document(revised), *scoped, from_id))
                history = db.execute("SELECT revision,document_json FROM muse_memory_claim_revisions WHERE "
                                     "project=? AND account=? AND visibility=? AND claim_id=?",
                                     (*scoped, from_id)).fetchall()
                for old in history:
                    old_doc = decode_document(old["document_json"])
                    old_doc["payload"]["relations"] = [relation for relation in old_doc["payload"]["relations"]
                                                        if relation["target_id"] != claim_id]
                    db.execute("UPDATE muse_memory_claim_revisions SET document_json=? WHERE project=? AND "
                               "account=? AND visibility=? AND claim_id=? AND revision=?",
                               (encode_document(old_doc), *scoped, from_id, old["revision"]))
                db.execute("INSERT INTO muse_memory_claim_revisions VALUES (?,?,?,?,?,?)",
                           (*scoped, from_id, revised["revision"], encode_document(revised)))
            db.execute("DELETE FROM muse_memory_relations WHERE project=? AND account=? AND visibility=? "
                       "AND (from_id=? OR to_id=?)", (*scoped, claim_id, claim_id))
        return True
