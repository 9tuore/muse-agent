"""Reviewed declarative plugin examples. No plugin-supplied code is executed."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from muse_plugins import _schema_matches


HOST_VERSION = "0.2.0"
MAX_MANIFEST_BYTES = 8192
REVIEWED = {
    ("example.hello-capability", "1.0.0"): (
        "hello-capability.json", "76577ec6c290eb06a8cd018fc58cfba6c1e4f1984e7fcb4592bd214536e1e70d"),
    ("example.browser-helper", "1.0.0"): (
        "browser-helper-1.0.json", "523f5211a9f578860fdd3fc501a7351f947cb0bd15c2ef849cb0500300e58106"),
    ("example.browser-helper", "1.1.0"): (
        "browser-helper-1.1.json", "bf7ec11571ebed94d846ba1951c0fa6ed3be0812bb6dcee72e93daf3b30303f0"),
}


def _version(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    if len(parts) != 3 or any(not part.isdecimal() for part in parts):
        raise ValueError("plugin_version_invalid")
    return tuple(int(part) for part in parts)


class DeclarativePluginSDK:
    """Install and run only three audited manifests bundled with the host."""

    def __init__(self, workspace: Path, *, manifest_dir: Path | None = None):
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / ".muse-declarative-plugins.sqlite3"
        if self.path.is_symlink():
            raise ValueError("plugin_registry_symlink_rejected")
        self.manifest_dir = manifest_dir or Path(__file__).with_name("plugin_examples")
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS installed ("
                       "plugin_id TEXT PRIMARY KEY, version TEXT NOT NULL, digest TEXT NOT NULL, "
                       "enabled INTEGER NOT NULL, revoked INTEGER NOT NULL, approval_id TEXT, updated_at TEXT NOT NULL)")
        os.chmod(self.path, 0o600)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _manifest(self, plugin_id: str, version: str) -> tuple[dict, str]:
        entry = REVIEWED.get((plugin_id, version))
        if entry is None:
            raise ValueError("unreviewed_plugin_version")
        filename, digest = entry
        path = self.manifest_dir / filename
        if path.is_symlink() or not path.is_file():
            raise ValueError("plugin_manifest_missing_or_symlink")
        raw = path.read_bytes()
        if len(raw) > MAX_MANIFEST_BYTES or hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("plugin_manifest_changed")
        manifest = json.loads(raw)
        if (not isinstance(manifest, dict) or manifest.get("manifest_version") != 1 or
                manifest.get("id") != plugin_id or manifest.get("version") != version or
                manifest.get("source") != "reviewed-builtin" or
                _version(manifest.get("minimum_host_version", "")) > _version(HOST_VERSION) or
                not isinstance(manifest.get("input_schema"), dict) or
                not isinstance(manifest.get("output_schema"), dict)):
            raise ValueError("plugin_manifest_invalid")
        expected = ({"kind": "host_hello"} if plugin_id == "example.hello-capability" else
                    {"kind": "delegate_capability", "capability_id": "browser.research"})
        if manifest.get("action") != expected:
            raise ValueError("plugin_action_invalid")
        return manifest, digest

    def catalog(self) -> list[dict]:
        output = []
        for plugin_id, version in REVIEWED:
            try:
                manifest, digest = self._manifest(plugin_id, version)
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                output.append({"id": plugin_id, "version": version, "status": "BLOCKED_INVALID_MANIFEST"})
                continue
            output.append({"id": plugin_id, "version": version, "digest": digest,
                           "source": manifest["source"], "minimum_host_version": manifest["minimum_host_version"],
                           "capabilities": manifest["capabilities"], "permissions": manifest["permissions"]})
        return output

    def list_installed(self) -> list[dict]:
        with self._connect() as db:
            rows = [dict(row) for row in db.execute("SELECT * FROM installed ORDER BY plugin_id")]
        for row in rows:
            try:
                self._manifest(row["plugin_id"], row["version"])
                valid = row["digest"] == REVIEWED[(row["plugin_id"], row["version"])][1]
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                valid = False
            row["status"] = ("BLOCKED_INVALID_MANIFEST" if not valid else "REVOKED" if row["revoked"] else
                             "ENABLED" if row["enabled"] else "DISABLED")
        return rows

    def _installed(self, plugin_id: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM installed WHERE plugin_id=?", (plugin_id,)).fetchone()
        return dict(row) if row else None

    def install(self, plugin_id: str, version: str, *, approved: bool = False) -> dict:
        if approved is not True:
            return {"status": "NEEDS_APPROVAL", "error": "explicit_user_approval_required"}
        if not isinstance(plugin_id, str) or not isinstance(version, str):
            return {"status": "BLOCKED", "error": "unreviewed_plugin_version"}
        try:
            manifest, digest = self._manifest(plugin_id, version)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        current = self._installed(plugin_id)
        if current and _version(version) <= _version(current["version"]):
            return {"status": "BLOCKED", "error": "plugin_version_not_newer"}
        with self._connect() as db:
            db.execute("INSERT INTO installed VALUES (?,?,?,?,?,?,?) ON CONFLICT(plugin_id) DO UPDATE SET "
                       "version=excluded.version,digest=excluded.digest,enabled=0,revoked=0,"
                       "approval_id=NULL,updated_at=excluded.updated_at",
                       (plugin_id, version, digest, 0, 0, None, datetime.now(timezone.utc).isoformat()))
        return {"status": "INSTALLED_DISABLED" if not current else "UPGRADED_DISABLED",
                "plugin_id": plugin_id, "version": version, "manifest_digest": digest,
                "capabilities": manifest["capabilities"], "permissions": manifest["permissions"]}

    def decide(self, plugin_id: str, decision: str, *, approved: bool = False) -> dict:
        row = self._installed(plugin_id)
        if not row:
            return {"status": "BLOCKED", "error": "plugin_not_installed"}
        if decision not in {"enable", "disable", "revoke", "uninstall"}:
            return {"status": "REJECTED", "error": "invalid_plugin_decision"}
        if decision in {"enable", "uninstall"} and approved is not True:
            return {"status": "NEEDS_APPROVAL", "error": "explicit_user_approval_required"}
        if decision == "enable":
            if row["revoked"]:
                return {"status": "BLOCKED", "error": "plugin_revoked_reinstall_required"}
            try:
                _, digest = self._manifest(plugin_id, row["version"])
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                return {"status": "BLOCKED", "error": str(exc)}
            if row["digest"] != digest:
                return {"status": "BLOCKED", "error": "plugin_manifest_changed"}
            approval_id = "plugin-approval:" + uuid.uuid4().hex
            with self._connect() as db:
                db.execute("UPDATE installed SET enabled=1,approval_id=?,updated_at=? WHERE plugin_id=?",
                           (approval_id, datetime.now(timezone.utc).isoformat(), plugin_id))
            return {"status": "ENABLED", "plugin_id": plugin_id, "approval_id": approval_id}
        if decision == "uninstall":
            with self._connect() as db:
                db.execute("DELETE FROM installed WHERE plugin_id=?", (plugin_id,))
            return {"status": "UNINSTALLED", "plugin_id": plugin_id}
        with self._connect() as db:
            db.execute("UPDATE installed SET enabled=0,revoked=?,approval_id=NULL,updated_at=? WHERE plugin_id=?",
                       (int(decision == "revoke" or row["revoked"]), datetime.now(timezone.utc).isoformat(), plugin_id))
        return {"status": "REVOKED" if decision == "revoke" else "DISABLED", "plugin_id": plugin_id}

    def _ready(self, plugin_id: str) -> tuple[dict, dict] | None:
        row = self._installed(plugin_id)
        if not row or row["enabled"] != 1 or row["revoked"]:
            return None
        try:
            manifest, digest = self._manifest(plugin_id, row["version"])
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None
        return (row, manifest) if row["digest"] == digest else None

    def run(self, plugin_id: str, payload: dict) -> dict:
        ready = self._ready(plugin_id)
        if not ready:
            return {"status": "BLOCKED", "error": "plugin_not_enabled_or_changed"}
        row, manifest = ready
        if manifest["action"]["kind"] != "host_hello":
            return {"status": "BLOCKED", "error": "goal_capability_host_required"}
        if not _schema_matches(payload, manifest["input_schema"]):
            return {"status": "REJECTED", "error": "invalid_plugin_input"}
        output = {"message": "Hello, " + payload["name"] + "!"}
        if not _schema_matches(output, manifest["output_schema"]):
            return {"status": "FAILED", "error": "invalid_plugin_output"}
        return {"status": "COMPLETED", "plugin_id": plugin_id, "version": row["version"], "output": output}

    def run_goal(self, plugin_id: str, *, goal_call: dict, approved: bool,
                 executor: Any, context: dict) -> dict:
        """A trusted host supplies the approved Goal call and executor, never the plugin."""
        ready = self._ready(plugin_id)
        if not ready:
            return {"status": "BLOCKED", "error": "plugin_not_enabled_or_changed"}
        row, manifest = ready
        if manifest["action"]["kind"] != "delegate_capability":
            return {"status": "BLOCKED", "error": "plugin_not_goal_adapter"}
        if approved is not True or not isinstance(goal_call, dict) or not isinstance(context, dict):
            return {"status": "BLOCKED", "error": "host_goal_approval_required"}
        if goal_call.get("capability") != manifest["action"]["capability_id"] or not _schema_matches(
                goal_call.get("args"), manifest["input_schema"]):
            return {"status": "BLOCKED", "error": "goal_call_outside_plugin_manifest"}
        if goal_call["args"].get("engine") != "python.org":
            return {"status": "BLOCKED", "error": "browser_engine_outside_manifest"}
        if context.get("allowed_domains") != ["python.org"]:
            return {"status": "BLOCKED", "error": "plugin_domain_scope_changed"}
        result = executor.execute(goal_call, approved=approved, context=context)
        if result.get("status") != "COMPLETED":
            return result
        if not _schema_matches(result.get("output"), manifest["output_schema"]):
            return {"status": "RESULT_UNCERTAIN", "error": "plugin_output_schema_mismatch"}
        return dict(result, plugin={"id": plugin_id, "version": row["version"],
                                    "manifest_digest": row["digest"], "approval_id": row["approval_id"]})


class PluginAwareExecutor:
    """Optional host adapter for an approved browser Goal; disabled plugins are inert."""

    def __init__(self, executor: Any, sdk: DeclarativePluginSDK):
        self.executor = executor
        self.sdk = sdk

    def execute(self, call: dict, *, approved: bool, context: dict | None = None) -> dict:
        if (isinstance(call, dict) and call.get("capability") == "browser.research" and
                self.sdk._ready("example.browser-helper")):
            return self.sdk.run_goal("example.browser-helper", goal_call=call, approved=approved,
                                     executor=self.executor, context=context or {})
        return self.executor.execute(call, approved=approved, context=context)
