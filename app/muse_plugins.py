"""Reviewed built-in plugin catalog. Staged metadata is never executable code."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BUILTIN_ID = "builtin.text_stats"
BUILTIN_VERSION = "1.0.0"
REVIEWED_MANIFEST_SHA256 = "be0df33294741098b8a0d463c231a5921d403dca2d5d41e46780523b696ee9da"
MAX_MANIFEST_BYTES = 8192
MAX_INPUT_BYTES = 8192


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _schema_matches(value: Any, schema: Dict[str, Any]) -> bool:
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, dict) or set(schema.get("required", [])) - set(value):
            return False
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            return False
        return all((key not in properties and schema.get("additionalProperties") is True) or
                   (key in properties and _schema_matches(item, properties[key]))
                   for key, item in value.items())
    if kind == "array":
        if not isinstance(value, list) or not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 1000000):
            return False
        item_schema = schema.get("items")
        return item_schema is None or all(_schema_matches(item, item_schema) for item in value)
    if kind == "string":
        return isinstance(value, str) and len(value) <= schema.get("maxLength", 1000000)
    if kind == "integer":
        return type(value) is int and schema.get("minimum", -1) <= value <= schema.get("maximum", 1000000)
    return False


class PluginRegistry:
    """Host-authorized enablement for one pinned, pure-function built-in."""

    def __init__(self, workspace: Path, manifest_path: Optional[Path] = None):
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / ".muse-plugin-registry.sqlite3"
        if self.path.is_symlink():
            raise ValueError("plugin_registry_symlink_rejected")
        self.manifest_path = manifest_path or Path(__file__).with_name("muse_plugin_manifest.json")
        self.manifest: Optional[Dict[str, Any]] = None
        self.manifest_error: Optional[str] = None
        self._load_reviewed_manifest()
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS approvals ("
                       "plugin_id TEXT PRIMARY KEY, version TEXT NOT NULL, digest TEXT NOT NULL, "
                       "approval_id TEXT NOT NULL, enabled INTEGER NOT NULL, decided_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS staged ("
                       "plugin_id TEXT PRIMARY KEY, version TEXT NOT NULL, digest TEXT NOT NULL, "
                       "manifest_json TEXT NOT NULL, staged_at TEXT NOT NULL)")
        os.chmod(self.path, 0o600)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _load_reviewed_manifest(self) -> None:
        self.manifest = None
        self.manifest_error = None
        try:
            if self.manifest_path.is_symlink():
                raise ValueError("manifest_symlink_rejected")
            data = self.manifest_path.read_bytes()
            if len(data) > MAX_MANIFEST_BYTES or hashlib.sha256(data).hexdigest() != REVIEWED_MANIFEST_SHA256:
                raise ValueError("unreviewed_manifest_digest")
            manifest = json.loads(data)
            if (not isinstance(manifest, dict) or manifest.get("manifest_version") != 1 or
                manifest.get("id") != BUILTIN_ID or manifest.get("version") != BUILTIN_VERSION or
                manifest.get("capabilities") != ["text.stats"] or
                manifest.get("permissions") != {"filesystem": "none", "network": False,
                                               "process": False, "secrets": False} or
                not isinstance(manifest.get("input_schema"), dict) or
                not isinstance(manifest.get("output_schema"), dict)):
                raise ValueError("invalid_reviewed_manifest")
            self.manifest = manifest
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self.manifest_error = str(exc)

    def _approval(self) -> Optional[Dict[str, Any]]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM approvals WHERE plugin_id=?", (BUILTIN_ID,)).fetchone()
        return dict(row) if row else None

    def _enabled(self) -> bool:
        self._load_reviewed_manifest()
        approval = self._approval()
        return bool(self.manifest and approval and approval["enabled"] == 1 and
                    approval["version"] == BUILTIN_VERSION and
                    approval["digest"] == REVIEWED_MANIFEST_SHA256)

    def list(self) -> List[Dict[str, Any]]:
        self._load_reviewed_manifest()
        built_in = {"id": BUILTIN_ID, "version": BUILTIN_VERSION,
                    "digest": REVIEWED_MANIFEST_SHA256,
                    "status": "BLOCKED_INVALID_MANIFEST" if self.manifest is None else
                              "ENABLED" if self._enabled() else "DISABLED",
                    "capabilities": ["text.stats"],
                    "permissions": {"filesystem": "none", "network": False,
                                    "process": False, "secrets": False}}
        with self._connect() as db:
            staged = [dict(row) for row in db.execute(
                "SELECT plugin_id,version,digest FROM staged ORDER BY plugin_id")]
        return [built_in] + [{"id": item["plugin_id"], "version": item["version"],
                              "digest": item["digest"], "status": "STAGED_BLOCKED"} for item in staged]

    def decide(self, plugin_id: str, decision: str, *, approved: bool = False) -> Dict[str, Any]:
        if plugin_id != BUILTIN_ID:
            return {"ok": False, "status": "BLOCKED", "error": "unknown_plugin_not_executable"}
        if decision not in {"enable", "disable"}:
            return {"ok": False, "status": "REJECTED", "error": "invalid_plugin_decision"}
        if decision == "disable":
            with self._connect() as db:
                db.execute("DELETE FROM approvals WHERE plugin_id=?", (BUILTIN_ID,))
            return {"ok": True, "status": "DISABLED", "plugin_id": BUILTIN_ID}
        if approved is not True:
            return {"ok": False, "status": "NEEDS_APPROVAL", "error": "explicit_user_approval_required"}
        self._load_reviewed_manifest()
        if self.manifest is None:
            return {"ok": False, "status": "BLOCKED", "error": self.manifest_error or "invalid_manifest"}
        approval_id = "plugin-approval:" + uuid.uuid4().hex
        with self._connect() as db:
            db.execute("INSERT INTO approvals VALUES (?,?,?,?,1,?) ON CONFLICT(plugin_id) DO UPDATE SET "
                       "version=excluded.version,digest=excluded.digest,approval_id=excluded.approval_id,"
                       "enabled=1,decided_at=excluded.decided_at",
                       (BUILTIN_ID, BUILTIN_VERSION, REVIEWED_MANIFEST_SHA256, approval_id, _now()))
        return {"ok": True, "status": "ENABLED", "plugin_id": BUILTIN_ID,
                "version": BUILTIN_VERSION, "manifest_digest": REVIEWED_MANIFEST_SHA256,
                "approval_id": approval_id}

    def run(self, plugin_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if plugin_id != BUILTIN_ID:
            return {"ok": False, "status": "BLOCKED", "error": "unknown_plugin_not_executable"}
        if not self._enabled():
            return {"ok": False, "status": "BLOCKED", "error": "plugin_not_approved_or_manifest_changed"}
        try:
            encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        except (TypeError, ValueError):
            return {"ok": False, "status": "REJECTED", "error": "invalid_plugin_input"}
        if len(encoded) > MAX_INPUT_BYTES or not _schema_matches(payload, self.manifest["input_schema"]):
            return {"ok": False, "status": "REJECTED", "error": "invalid_plugin_input"}
        content = payload["text"]
        output = {"characters": len(content), "lines": len(content.splitlines())}
        if not _schema_matches(output, self.manifest["output_schema"]):
            return {"ok": False, "status": "FAILED", "error": "invalid_plugin_output"}
        return {"ok": True, "status": "COMPLETED", "plugin_id": BUILTIN_ID,
                "version": BUILTIN_VERSION, "output": output,
                "verification": "OUTPUT_SCHEMA_VALIDATED"}

    def stage(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Persist bounded third-party metadata only; no code path is accepted."""
        if not isinstance(proposal, dict) or set(proposal) != {
            "id", "version", "description", "requested_capabilities"
        } or proposal.get("id") == BUILTIN_ID:
            return {"ok": False, "status": "REJECTED", "error": "invalid_staged_manifest"}
        plugin_id, version = proposal.get("id"), proposal.get("version")
        capabilities = proposal.get("requested_capabilities")
        if (not isinstance(plugin_id, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]{1,63}", plugin_id) or
            not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) or
            not isinstance(proposal.get("description"), str) or len(proposal["description"]) > 240 or
            not isinstance(capabilities, list) or len(capabilities) > 8 or any(
                not isinstance(item, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]{1,63}", item)
                for item in capabilities
            )):
            return {"ok": False, "status": "REJECTED", "error": "invalid_staged_manifest"}
        encoded = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 2048:
            return {"ok": False, "status": "REJECTED", "error": "staged_manifest_too_large"}
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        with self._connect() as db:
            db.execute("INSERT INTO staged VALUES (?,?,?,?,?) ON CONFLICT(plugin_id) DO UPDATE SET "
                       "version=excluded.version,digest=excluded.digest,manifest_json=excluded.manifest_json,"
                       "staged_at=excluded.staged_at", (plugin_id, version, digest, encoded, _now()))
        return {"ok": True, "status": "STAGED_BLOCKED", "plugin_id": plugin_id,
                "version": version, "manifest_digest": digest}
