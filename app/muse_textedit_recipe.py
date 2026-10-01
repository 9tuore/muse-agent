"""Goal-bound TextEdit recipe execution for existing synthetic workspace files."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import stat
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from muse_app_learning import RecipeStore
from muse_ax_adapter import AXUnavailable, NativeAXAdapter
from muse_capabilities import BUILTIN_SCOPE, _safe_parts, builtin_capability_documents
from muse_goal_store import plan_digest


TEXTEDIT_BUNDLE = "com.apple.TextEdit"
MAX_TEXT_BYTES = 8192
_SYNTHETIC_NAME = re.compile(r"Muse-Test-[A-Za-z0-9-]{1,40}\.txt\Z")
_SAVE_NAMES = {"save", "存储", "保存"}


class TextEditRecipeHost:
    """A prepared recipe may run only within its separately approved Goal."""

    def __init__(self, workspace: Path, helper_path: Path):
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.helper_path = Path(helper_path)
        if not self.helper_path.is_file():
            raise ValueError("ax_helper_missing")
        self.binding_path = self.workspace / ".muse-textedit-recipe-bindings.sqlite3"
        if self.binding_path.is_symlink():
            raise ValueError("recipe_bindings_symlink_rejected")
        with self._connect_bindings() as db:
            db.execute("CREATE TABLE IF NOT EXISTS bindings ("
                       "goal_id TEXT NOT NULL, revision INTEGER NOT NULL, plan_digest TEXT NOT NULL, "
                       "approval_id TEXT NOT NULL, recipe_id TEXT NOT NULL, recipe_revision INTEGER NOT NULL, "
                       "recipe_digest TEXT NOT NULL, before_sha256 TEXT NOT NULL, created_at TEXT NOT NULL, "
                       "PRIMARY KEY(goal_id,revision,recipe_id))")
        os.chmod(self.binding_path, 0o600)

    def _connect_bindings(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.binding_path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _read_file(self, relative_path: str) -> tuple[bytes, Path]:
        parts = _safe_parts(relative_path)
        if len(parts) != 2 or parts[0] != "notes" or not _SYNTHETIC_NAME.fullmatch(parts[1]):
            raise ValueError("synthetic_textedit_file_required")
        directory = os.open(str(self.workspace), os.O_RDONLY | os.O_DIRECTORY)
        try:
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                os.close(directory)
                directory = child
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise ValueError("textedit_target_not_regular")
                data = os.read(fd, MAX_TEXT_BYTES + 1)
                if len(data) > MAX_TEXT_BYTES:
                    raise ValueError("textedit_target_too_large")
            finally:
                os.close(fd)
        finally:
            os.close(directory)
        return data, self.workspace.joinpath(*parts)

    def _adapter(self, window_title: str) -> NativeAXAdapter:
        return NativeAXAdapter(self.helper_path, window_title=window_title)

    @staticmethod
    def _document_matches(adapter: NativeAXAdapter, window_title: str, path: Path,
                          record: dict | None = None) -> bool:
        record = record if record is not None else adapter.document_url(TEXTEDIT_BUNDLE, window_title)
        url = record.get("document_url", "")
        parsed = urlsplit(url)
        if (record.get("status") != "COMPLETED" or parsed.scheme != "file" or
                parsed.netloc not in {"", "localhost"} or parsed.query or parsed.fragment):
            return False
        return Path(unquote(parsed.path)).resolve(strict=True) == path.resolve(strict=True)

    @staticmethod
    def _current_text(snapshot: dict, window_title: str) -> str:
        matches = [node for node in snapshot.get("elements", [])
                   if node.get("role") == "AXTextArea" and node.get("window_title") == window_title and
                   "set_value" in node.get("actions", [])]
        if len(matches) != 1 or not isinstance(matches[0].get("value"), str):
            raise ValueError("textedit_editor_ambiguous")
        return matches[0]["value"]

    def prepare(self, *, relative_path: str, content: str) -> dict:
        """Observe and propose; this never enables or executes the recipe."""
        try:
            existing, path = self._read_file(relative_path)
            if not isinstance(content, str) or not 1 <= len(content.encode("utf-8")) <= MAX_TEXT_BYTES:
                raise ValueError("synthetic_content_invalid")
            before_text = existing.decode("utf-8", errors="strict")
            adapter = self._adapter(path.name)
            document = adapter.document_url(TEXTEDIT_BUNDLE, path.name)
            if adapter.status().get("trusted") is not True or not self._document_matches(
                    adapter, path.name, path, document):
                raise ValueError("textedit_helper_permission_or_document_mismatch")
            focused = adapter.focus_document(TEXTEDIT_BUNDLE, path.name, document["document_url"])
            if focused.get("status") != "COMPLETED" or not self._document_matches(adapter, path.name, path):
                raise ValueError("textedit_document_focus_failed")
            store = RecipeStore(self.workspace, adapter)
            snapshot = store.observe(TEXTEDIT_BUNDLE)
            if self._current_text(snapshot, path.name) != before_text:
                raise ValueError("unsaved_changes_or_wrong_document")
            editor = next(node for node in snapshot["elements"] if node.get("role") == "AXTextArea" and
                          node.get("window_title") == path.name and "set_value" in node.get("actions", []))
            saves = [node for node in snapshot["elements"] if node.get("role") == "AXMenuItem" and
                     node.get("window_title") == path.name and node.get("name", "").lower() in _SAVE_NAMES and
                     "press" in node.get("actions", [])]
            if len(saves) != 1:
                raise ValueError("textedit_save_control_ambiguous")
            recipe_id = "textedit.synthetic_save." + hashlib.sha256(relative_path.encode()).hexdigest()[:16]
            steps = [{"role": editor["role"], "name": editor["name"], "path": editor.get("path"),
                      "window_title": path.name, "action": "set_value", "input": "content"},
                     {"role": saves[0]["role"], "name": saves[0]["name"],
                      "window_title": path.name, "action": "press", "input": None}]
            proposal = store.propose(recipe_id, TEXTEDIT_BUNDLE, steps)
            dry_run = store.dry_run(recipe_id, {"content": content, "window_title": path.name})
            if dry_run.get("status") != "READY_FOR_APPROVAL":
                raise ValueError("textedit_recipe_dry_run_failed")
            return {"status": "PROPOSED", "recipe_id": recipe_id,
                    "revision": proposal["recipe"]["revision"], "digest": proposal["digest"],
                    "target_bundle_id": TEXTEDIT_BUNDLE, "window_title": path.name,
                    "relative_path": relative_path, "content": content,
                    "before_sha256": hashlib.sha256(existing).hexdigest(),
                    "observed_steps": [{"role": step["selector"]["role"],
                                        "name": step["selector"]["name"], "action": step["action"]}
                                       for step in proposal["recipe"]["steps"]]}
        except (AXUnavailable, OSError, UnicodeError, ValueError) as exc:
            return {"status": "BLOCKED", "error": str(exc)[:160]}

    def _goal_record(self, goal_id: str) -> dict | None:
        path = self.workspace / "memory.sqlite3"
        if not path.is_file() or path.is_symlink():
            return None
        try:
            with sqlite3.connect(str(path), timeout=5) as db:
                db.row_factory = sqlite3.Row
                row = db.execute(
                    "SELECT g.status,g.revision,g.run_id,g.approval_id,g.approval_digest,g.approval_expires_at,"
                    "r.status AS run_status,r.approval_id AS run_approval_id,a.digest AS approved_digest,"
                    "a.expires_at AS approved_until,p.digest AS revision_digest,p.spec_json "
                    "FROM muse_goals g JOIN muse_goal_approvals a ON a.approval_id=g.approval_id "
                    "JOIN muse_goal_revisions p ON p.goal_id=g.goal_id AND p.revision=g.revision "
                    "LEFT JOIN muse_goal_runs r ON r.run_id=g.run_id WHERE g.goal_id=?", (goal_id,)).fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def _catalog_enabled(self) -> bool:
        try:
            from muse_capability_catalog import CapabilityCatalog

            catalog = CapabilityCatalog(self.workspace)
            entry = catalog.get("app.recipe", BUILTIN_SCOPE)
            expected = next(item for item in builtin_capability_documents(BUILTIN_SCOPE)
                            if item["id"] == "app.recipe")
            encoded = json.dumps(entry["document"], ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":")).encode("utf-8") if entry else b""
            return bool(entry and entry["enabled"] and entry["document"] == expected and
                        hashlib.sha256(encoded).hexdigest() == entry["digest"])
        except (ImportError, ValueError, KeyError, TypeError, StopIteration, sqlite3.Error):
            return False

    @staticmethod
    def _planned_args(record: dict, recipe_id: str, recipe_revision: int, digest: str) -> dict | None:
        try:
            spec = json.loads(record["spec_json"])
            steps = [step for step in spec["steps"] if step.get("capability") == "app.recipe" and
                     step.get("args", {}).get("recipe_id") == recipe_id and
                     step.get("args", {}).get("revision") == recipe_revision and
                     step.get("args", {}).get("digest") == digest]
            if (len(steps) != 1 or record["revision_digest"] != plan_digest(spec) or
                    record["approval_digest"] != record["revision_digest"] or
                    record["approved_digest"] != record["revision_digest"]):
                return None
            args = steps[0]["args"]
            refs = spec["permissions"]["resource_refs"]
            if ("app.recipe" not in spec["permissions"]["capabilities"] or
                    not {"app:com.apple.TextEdit", "resource:workspace/" + args["relative_path"],
                         "window:com.apple.TextEdit:" + args["window_title"]} <= set(refs)):
                return None
            return args
        except (KeyError, TypeError, ValueError):
            return None

    def enable_for_goal(self, *, goal_id: str, goal_revision: int, recipe_id: str,
                        recipe_revision: int, digest: str) -> dict:
        """Bind a disabled recipe to an already approved Goal revision and scope."""
        record = self._goal_record(goal_id)
        if (record is None or record["status"] != "active" or record["revision"] != goal_revision or
                record["approval_id"] is None or
                datetime.fromisoformat(record["approval_expires_at"]) <= datetime.now(timezone.utc)):
            return {"status": "BLOCKED", "error": "goal_approval_missing_or_changed"}
        args = self._planned_args(record, recipe_id, recipe_revision, digest)
        if args is None:
            return {"status": "BLOCKED", "error": "recipe_not_in_approved_goal"}
        try:
            before, _ = self._read_file(args["relative_path"])
        except (OSError, ValueError):
            return {"status": "BLOCKED", "error": "synthetic_textedit_file_required"}
        store = RecipeStore(self.workspace, self._adapter(args["window_title"]))
        with self._connect_bindings() as db:
            prior = db.execute("SELECT * FROM bindings WHERE goal_id=? AND revision=? AND recipe_id=?",
                               (goal_id, goal_revision, recipe_id)).fetchone()
        if prior is not None:
            with store._connect() as db:
                recipe = db.execute("SELECT enabled,approval_id FROM recipes WHERE id=? AND revision=?",
                                    (recipe_id, recipe_revision)).fetchone()
            if (prior["approval_id"] != record["approval_id"] or prior["recipe_digest"] != digest or
                    recipe is None or recipe["enabled"] != 1 or not recipe["approval_id"]):
                return {"status": "BLOCKED", "error": "recipe_revoked_or_approval_changed"}
            return {"status": "ENABLED", "recipe_id": recipe_id, "revision": recipe_revision,
                    "digest": digest, "approval_id": record["approval_id"], "replayed": True}
        decision = store.decide(recipe_id, recipe_revision, digest, approved=True)
        if decision.get("status") != "ENABLED":
            return decision
        with self._connect_bindings() as db:
            db.execute("INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(goal_id,revision,recipe_id) "
                       "DO UPDATE SET plan_digest=excluded.plan_digest,approval_id=excluded.approval_id,"
                       "recipe_revision=excluded.recipe_revision,recipe_digest=excluded.recipe_digest,"
                       "before_sha256=excluded.before_sha256,"
                       "created_at=excluded.created_at",
                       (goal_id, goal_revision, record["revision_digest"], record["approval_id"],
                        recipe_id, recipe_revision, digest, hashlib.sha256(before).hexdigest(),
                        datetime.now(timezone.utc).isoformat()))
        return {"status": "ENABLED", "recipe_id": recipe_id, "revision": recipe_revision,
                "digest": digest, "approval_id": record["approval_id"]}

    def revoke(self, *, recipe_id: str, recipe_revision: int, digest: str) -> dict:
        """Host user action disables this recipe and prevents same-Goal re-enablement."""
        return RecipeStore(self.workspace, self._adapter("revoked")).decide(
            recipe_id, recipe_revision, digest, approved=False)

    def execute(self, call: dict, *, approved: bool, context: dict | None = None) -> dict:
        base = {"ok": False, "status": "BLOCKED", "action_id": call.get("action_id") if isinstance(call, dict) else None,
                "capability": "app.recipe", "output": {}, "verification": {}, "evidence": {}}
        if (not isinstance(call, dict) or not isinstance(context, dict) or approved is not True or
                call.get("capability") != "app.recipe"):
            return dict(base, error="host_goal_approval_required")
        args = call.get("args")
        required = {"recipe_id", "revision", "digest", "target_bundle_id", "window_title", "relative_path", "content"}
        if not isinstance(args, dict) or set(args) != required or args.get("target_bundle_id") != TEXTEDIT_BUNDLE:
            return dict(base, error="textedit_recipe_args_invalid")
        try:
            existing, path = self._read_file(args["relative_path"])
            if (args["window_title"] != path.name or type(args["revision"]) is not int or
                    not isinstance(args["digest"], str) or len(args["digest"]) != 64 or
                    not isinstance(args["content"], str) or
                    not 1 <= len(args["content"].encode("utf-8")) <= MAX_TEXT_BYTES):
                raise ValueError("textedit_recipe_args_invalid")
            record = self._goal_record(call["goal_id"])
            if (record is None or record["status"] != "running" or record["run_status"] != "running" or
                    record["revision"] != call["revision"] or record["run_id"] != context.get("run_id") or
                    record["approval_id"] != context.get("approval_id") or
                    record["run_approval_id"] != record["approval_id"] or
                    record["revision_digest"] != context.get("plan_digest") or
                    datetime.fromisoformat(record["approval_expires_at"]) <= datetime.now(timezone.utc) or
                    datetime.fromisoformat(record["approved_until"]) <= datetime.now(timezone.utc)):
                raise ValueError("goal_run_approval_missing_or_changed")
            planned = self._planned_args(record, args["recipe_id"], args["revision"], args["digest"])
            matching_steps = [step for step in json.loads(record["spec_json"])["steps"]
                              if step.get("capability") == "app.recipe" and step.get("args") == args]
            if (planned != args or len(matching_steps) != 1 or
                    call["action_id"] != context["run_id"] + ":" + matching_steps[0]["id"]):
                raise ValueError("textedit_action_outside_approved_plan")
            with self._connect_bindings() as db:
                binding = db.execute("SELECT * FROM bindings WHERE goal_id=? AND revision=? AND recipe_id=?",
                                     (call["goal_id"], call["revision"], args["recipe_id"])).fetchone()
            if (binding is None or binding["approval_id"] != record["approval_id"] or
                    binding["plan_digest"] != record["revision_digest"] or
                    binding["recipe_digest"] != args["digest"] or
                    binding["recipe_revision"] != args["revision"] or
                    binding["before_sha256"] != hashlib.sha256(existing).hexdigest()):
                raise ValueError("recipe_goal_binding_missing_or_changed")
            if context.get("gui_control_granted") is not True:
                raise ValueError("gui_control_not_granted")
            if not self._catalog_enabled():
                raise ValueError("app_recipe_catalog_not_enabled_or_changed")
            adapter = self._adapter(path.name)
            if adapter.status().get("trusted") is not True or not self._document_matches(adapter, path.name, path):
                raise ValueError("textedit_helper_permission_or_document_mismatch")
            before_text = existing.decode("utf-8", errors="strict")
            document = adapter.document_url(TEXTEDIT_BUNDLE, path.name)
            if document.get("status") != "COMPLETED":
                raise ValueError("textedit_document_changed_before_focus")
            focused = adapter.focus_document(TEXTEDIT_BUNDLE, path.name, document["document_url"])
            if focused.get("status") != "COMPLETED":
                raise ValueError("textedit_document_focus_failed")
            # Observe the editor text only after the document is focused, matching
            # prepare(). Observing first could raise textedit_editor_ambiguous when
            # the document window is not frontmost and its AXTextArea is unexposed.
            if (not self._document_matches(adapter, path.name, path) or
                    self._current_text(adapter.snapshot(TEXTEDIT_BUNDLE), path.name) != before_text):
                raise ValueError("unsaved_changes_or_wrong_document")
            store = RecipeStore(self.workspace, adapter)
            with store._connect() as db:
                latest = db.execute("SELECT revision,digest,enabled FROM recipes WHERE id=? "
                                    "ORDER BY revision DESC LIMIT 1", (args["recipe_id"],)).fetchone()
            if (latest is None or latest["revision"] != args["revision"] or
                    latest["digest"] != args["digest"] or latest["enabled"] != 1):
                raise ValueError("recipe_version_or_approval_changed")
            current, _ = self._read_file(args["relative_path"])
            if (current != existing or not self._document_matches(adapter, path.name, path) or
                    self._current_text(adapter.snapshot(TEXTEDIT_BUNDLE), path.name) != before_text):
                raise ValueError("textedit_document_changed_after_focus")
            result = store.run(
                args["recipe_id"], {"window_title": path.name, "content": args["content"]},
                approved=True, allowed_bundle_ids=[TEXTEDIT_BUNDLE], allowed_window_titles=[path.name])
            if result.get("status") != "COMPLETED":
                return dict(base, error="recipe_run_blocked:" + str(result.get("error", result["status"])))
            expected = args["content"].encode("utf-8")
            deadline = time.monotonic() + 3
            observed = b""
            while time.monotonic() < deadline:
                observed, _ = self._read_file(args["relative_path"])
                if observed == expected:
                    break
                time.sleep(0.1)
            ax_matches = self._current_text(adapter.snapshot(TEXTEDIT_BUNDLE), path.name) == args["content"]
            if observed != expected or not ax_matches or not self._document_matches(adapter, path.name, path):
                return dict(base, status="RESULT_UNCERTAIN", error="textedit_readback_mismatch")
            digest = hashlib.sha256(observed).hexdigest()
            return dict(base, ok=True, status="COMPLETED",
                        output={"recipe_id": args["recipe_id"], "revision": args["revision"],
                                "relative_path": args["relative_path"], "window_title": path.name,
                                "bytes": len(observed), "sha256": digest},
                        verification={"ax_value_matches": True, "disk_readback_matches": True,
                                      "helper_trusted": True, "focused_document_matches": True},
                        evidence={"saved_at": datetime.now(timezone.utc).isoformat(),
                                  "approval_id": record["approval_id"]})
        except (AXUnavailable, OSError, UnicodeError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
            return dict(base, error=str(exc)[:160])


class TextEditAwareExecutor:
    """Pass all other capabilities to the existing reviewed executor."""

    def __init__(self, executor: Any, recipe_host: TextEditRecipeHost):
        self.executor = executor
        self.recipe_host = recipe_host

    def execute(self, call: dict, *, approved: bool, context: dict | None = None) -> dict:
        if isinstance(call, dict) and call.get("capability") == "app.recipe":
            return self.recipe_host.execute(call, approved=approved, context=context)
        return self.executor.execute(call, approved=approved, context=context)
