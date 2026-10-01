"""Data-only recipes learned from an observed accessibility tree.

The host owns approval.  The adapter owns actual observation and UI actions;
neither a page nor a model can grant itself permission to run a recipe.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


MAX_RECIPE_BYTES = 16_384
SAFE_ACTIONS = {"press", "set_value"}
SAFE_ROLES = {"AXButton", "AXTextField", "AXTextArea", "AXSearchField", "AXMenuItem"}
SAFE_PRESS_NAMES = {"save", "存储", "保存", "open", "打开", "new", "新建",
                    "find", "查找", "search", "搜索", "next", "下一页"}
BLOCKED_NAMES = re.compile(r"password|passcode|验证码|密码|支付|购买|删除|发送|publish|post|checkout|buy|delete|remove|erase", re.I)


class AccessibilityAdapter(Protocol):
    def snapshot(self, bundle_id: str) -> dict: ...

    def act(self, bundle_id: str, selector: dict, action: str, value: str | None) -> dict: ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canon(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _selector(node: dict, nodes: list[dict]) -> dict:
    role, name, path, title = (node.get("role"), node.get("name"), node.get("path"),
                               node.get("window_title"))
    if (role not in SAFE_ROLES or not isinstance(name, str) or len(name) > 120
            or BLOCKED_NAMES.search(name)):
        raise ValueError("unsafe_or_unnamed_control")
    if not name and (not isinstance(path, str) or not re.fullmatch(r"w[0-9]+(/[0-9]+){1,10}", path)):
        raise ValueError("unnamed_control_requires_observed_path")
    if title is not None and (not isinstance(title, str) or not 1 <= len(title) <= 240):
        raise ValueError("invalid_observed_window_title")
    if sum(item.get("role") == role and item.get("name") == name and
           (bool(name) or item.get("path") == path) and
           (title is None or item.get("window_title") == title) for item in nodes) != 1:
        raise ValueError("ambiguous_control")
    return {"role": role, "name": name, **({"path": path} if not name else {})}


def _match(snapshot: dict, selector: dict, *, require_enabled: bool = True) -> dict:
    matches = [node for node in snapshot.get("elements", [])
               if node.get("role") == selector["role"] and node.get("name") == selector["name"] and
               ("path" not in selector or node.get("path") == selector["path"]) and
               ("window_title" not in selector or node.get("window_title") == selector["window_title"])]
    if len(matches) != 1 or (require_enabled and matches[0].get("enabled") is not True):
        raise ValueError("control_missing_changed_or_disabled")
    return matches[0]


class RecipeStore:
    """One generic observe/propose/approve/replay path for multiple apps."""

    def __init__(self, workspace: Path, adapter: AccessibilityAdapter):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / ".muse-app-recipes.sqlite3"
        if self.path.is_symlink():
            raise ValueError("recipe_store_symlink_rejected")
        self.adapter = adapter
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS recipes (id TEXT NOT NULL, revision INTEGER NOT NULL, "
                       "digest TEXT NOT NULL, body TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 0, "
                       "approval_id TEXT, created_at TEXT NOT NULL, PRIMARY KEY(id,revision))")
        self.path.chmod(0o600)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def observe(self, bundle_id: str) -> dict:
        if not isinstance(bundle_id, str) or not re.fullmatch(r"[A-Za-z0-9.-]{3,160}", bundle_id):
            raise ValueError("invalid_bundle_id")
        snapshot = self.adapter.snapshot(bundle_id)
        if snapshot.get("bundle_id") != bundle_id or not isinstance(snapshot.get("elements"), list):
            raise ValueError("invalid_observation")
        if len(snapshot["elements"]) > 500:
            raise ValueError("observation_too_large")
        return snapshot

    def propose(self, recipe_id: str, bundle_id: str, steps: list[dict], *, scope: str = "test") -> dict:
        """Resolve semantic control names against a fresh observation.

        Each proposed step names a control and an action; selectors are generated
        only when that control is unique in the observed tree.
        """
        if not isinstance(recipe_id, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]{2,79}", recipe_id):
            raise ValueError("invalid_recipe_id")
        if scope != "test" or not isinstance(steps, list) or not 1 <= len(steps) <= 12:
            raise ValueError("invalid_recipe_scope_or_steps")
        observed = self.observe(bundle_id)
        nodes = observed["elements"]
        compiled = []
        for index, step in enumerate(steps):
            if (not isinstance(step, dict) or not {"role", "name", "action", "input"} <= set(step)
                    or set(step) - {"role", "name", "path", "window_title", "action", "input"}):
                raise ValueError("invalid_step")
            selector = _selector(step, nodes)
            node = _match(observed, dict(selector, **({"window_title": step["window_title"]}
                                                if "window_title" in step else {})),
                          require_enabled=index == 0)
            action, input_name = step["action"], step["input"]
            if action not in SAFE_ACTIONS or action not in node.get("actions", []):
                raise ValueError("action_not_observed")
            if action == "press" and selector["name"].lower() not in SAFE_PRESS_NAMES:
                raise ValueError("press_action_not_reviewed")
            if action == "set_value":
                if (selector["role"] not in {"AXTextField", "AXTextArea", "AXSearchField"}
                        or not isinstance(input_name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", input_name)):
                    raise ValueError("invalid_input_binding")
            elif input_name is not None:
                raise ValueError("press_has_no_input")
            compiled.append({"selector": selector, "action": action, "input": input_name})
        recipe = {"id": recipe_id, "revision": 0, "scope": scope, "target_bundle_id": bundle_id,
                  "observed_at": observed.get("observed_at", _now()), "steps": compiled,
                  "verification": "fresh_adapter_snapshot_after_each_step"}
        with self._connect() as db:
            row = db.execute("SELECT MAX(revision) FROM recipes WHERE id=?", (recipe_id,)).fetchone()
            recipe["revision"] = (row[0] or 0) + 1
            encoded = _canon(recipe)
            if len(encoded) > MAX_RECIPE_BYTES:
                raise ValueError("recipe_too_large")
            digest = hashlib.sha256(encoded).hexdigest()
            db.execute("UPDATE recipes SET enabled=0 WHERE id=?", (recipe_id,))
            db.execute("INSERT INTO recipes(id,revision,digest,body,created_at) VALUES(?,?,?,?,?)",
                       (recipe_id, recipe["revision"], digest, encoded.decode("utf-8"), _now()))
        return {"status": "PROPOSED", "recipe": recipe, "digest": digest}

    def decide(self, recipe_id: str, revision: int, digest: str, *, approved: bool) -> dict:
        with self._connect() as db:
            row = db.execute("SELECT * FROM recipes WHERE id=? AND revision=?", (recipe_id, revision)).fetchone()
            if row is None or row["digest"] != digest:
                return {"status": "BLOCKED", "error": "recipe_version_or_digest_changed"}
            if not approved:
                db.execute("UPDATE recipes SET enabled=0,approval_id=NULL WHERE id=?", (recipe_id,))
                return {"status": "DISABLED"}
            latest = db.execute("SELECT MAX(revision) FROM recipes WHERE id=?", (recipe_id,)).fetchone()[0]
            if revision != latest:
                return {"status": "BLOCKED", "error": "stale_recipe_revision"}
            approval_id = "recipe:" + digest[:24]
            db.execute("UPDATE recipes SET enabled=1,approval_id=? WHERE id=? AND revision=?",
                       (approval_id, recipe_id, revision))
            return {"status": "ENABLED", "approval_id": approval_id}

    def dry_run(self, recipe_id: str, inputs: dict) -> dict:
        if not isinstance(inputs, dict) or len(_canon(inputs)) > 16_384:
            return {"status": "BLOCKED", "error": "invalid_inputs"}
        with self._connect() as db:
            row = db.execute("SELECT body,digest FROM recipes WHERE id=? ORDER BY revision DESC LIMIT 1",
                             (recipe_id,)).fetchone()
        if row is None:
            return {"status": "BLOCKED", "error": "recipe_missing"}
        recipe = json.loads(row["body"])
        try:
            title = inputs.get("window_title")
            if not isinstance(title, str) or not 1 <= len(title) <= 240:
                raise ValueError("window_title_required")
            snapshot = self.observe(recipe["target_bundle_id"])
            for index, step in enumerate(recipe["steps"]):
                _match(snapshot, dict(step["selector"], window_title=title), require_enabled=index == 0)
                if step["input"]:
                    value = inputs.get(step["input"])
                    if not isinstance(value, str) or len(value) > 8_192:
                        raise ValueError("invalid_bound_value")
        except (ValueError, OSError) as exc:
            return {"status": "BLOCKED", "error": str(exc)}
        return {"status": "READY_FOR_APPROVAL", "digest": row["digest"],
                "revision": recipe["revision"], "target_bundle_id": recipe["target_bundle_id"],
                "steps": len(recipe["steps"]), "side_effects": False}

    def run(self, recipe_id: str, inputs: dict, *, approved: bool,
            allowed_bundle_ids: list[str], allowed_window_titles: list[str],
            expected_revision: int | None = None, expected_digest: str | None = None) -> dict:
        if not approved:
            return {"status": "WAITING_APPROVAL"}
        if not isinstance(inputs, dict) or len(_canon(inputs)) > 16_384:
            return {"status": "BLOCKED", "error": "invalid_inputs"}
        with self._connect() as db:
            row = db.execute("SELECT * FROM recipes WHERE id=? ORDER BY revision DESC LIMIT 1", (recipe_id,)).fetchone()
        if row is None or not row["enabled"] or not row["approval_id"]:
            return {"status": "BLOCKED", "error": "recipe_not_enabled"}
        if ((expected_revision is not None and row["revision"] != expected_revision) or
                (expected_digest is not None and row["digest"] != expected_digest)):
            return {"status": "BLOCKED", "error": "recipe_version_or_digest_changed"}
        recipe = json.loads(row["body"])
        bundle_id = recipe["target_bundle_id"]
        if bundle_id not in allowed_bundle_ids or hashlib.sha256(_canon(recipe)).hexdigest() != row["digest"]:
            return {"status": "BLOCKED", "error": "target_or_recipe_changed"}
        window_title = inputs.get("window_title")
        if (not isinstance(window_title, str) or not 1 <= len(window_title) <= 240
                or window_title not in allowed_window_titles):
            return {"status": "BLOCKED", "error": "window_outside_approved_scope"}
        receipts = []
        try:
            for step in recipe["steps"]:
                with self._connect() as db:
                    current = db.execute("SELECT enabled,digest FROM recipes WHERE id=? AND revision=?",
                                         (recipe_id, recipe["revision"])).fetchone()
                if not current or not current["enabled"] or current["digest"] != row["digest"]:
                    raise ValueError("recipe_revoked")
                before = self.observe(bundle_id)
                selector = dict(step["selector"], window_title=window_title)
                _match(before, selector)
                value = inputs.get(step["input"]) if step["input"] else None
                if step["action"] == "set_value" and (not isinstance(value, str) or len(value) > 8_192):
                    raise ValueError("invalid_bound_value")
                receipt = self.adapter.act(bundle_id, selector, step["action"], value)
                if receipt.get("status") != "COMPLETED":
                    raise ValueError("action_failed_or_uncertain")
                after = self.observe(bundle_id)
                if step["action"] == "set_value" and _match(after, selector).get("value") != value:
                    raise ValueError("value_readback_mismatch")
                receipts.append({"selector": step["selector"], "action": step["action"],
                                 "verification": "VALUE_MATCHES" if step["action"] == "set_value" else "ADAPTER_ACTION_COMPLETED"})
        except (ValueError, OSError) as exc:
            return {"status": "BLOCKED", "error": str(exc), "completed_steps": receipts}
        return {"status": "COMPLETED", "recipe_id": recipe_id, "revision": recipe["revision"],
                "approval_id": row["approval_id"], "steps": receipts}
