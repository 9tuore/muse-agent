"""Bind an observed Edge search form to one approved browser Goal."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from muse_app_learning import RecipeStore
from muse_browser import EDGE_BUNDLE_ID, IsolatedEdgeSession
from muse_browser_learning import BrowserSearchLearningAdapter, SEARCH_PAGE
from muse_goal_store import GoalStore, plan_digest
from muse_search_policy import topic_terms


RECIPE_ID = "edge.public_search"
RECIPE_FIELDS = {"query", "engine", "max_pages", "recipe_id", "recipe_revision",
                 "recipe_digest", "target_bundle_id", "window_title"}
GUI_LOCK = Path("/tmp/gosim-muse-5agent-20260928/gui.lock")


def _valid_query(query: Any) -> bool:
    return (isinstance(query, str) and query == query.strip() and 2 <= len(query) <= 160 and
            not any(char in query for char in "\r\n\x00@\\") and
            not re.search(r"/(?:Users|home|private)/", query, re.I) and bool(topic_terms(query)))


class BrowserRecipeHost:
    """Preparation observes only; an approved Goal enables its exact recipe."""

    def __init__(self, workspace: Path, *, session_factory: Any = IsolatedEdgeSession,
                 gui_lock_path: Path = GUI_LOCK):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.session_factory = session_factory
        self.gui_lock_path = Path(gui_lock_path)
        self.binding_path = self.workspace / ".muse-browser-recipe-bindings.sqlite3"
        if self.binding_path.is_symlink():
            raise ValueError("browser_recipe_bindings_symlink_rejected")
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS bindings ("
                       "goal_id TEXT NOT NULL, goal_revision INTEGER NOT NULL, "
                       "plan_digest TEXT NOT NULL, approval_id TEXT NOT NULL, "
                       "recipe_id TEXT NOT NULL, recipe_revision INTEGER NOT NULL, "
                       "recipe_digest TEXT NOT NULL, query TEXT NOT NULL, "
                       "window_title TEXT NOT NULL, PRIMARY KEY(goal_id,goal_revision,recipe_id))")
        os.chmod(self.binding_path, 0o600)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.binding_path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _goal(self, goal_id: str) -> dict | None:
        if not isinstance(goal_id, str):
            return None
        try:
            return GoalStore(self.workspace).get(goal_id)
        except (OSError, sqlite3.Error, ValueError):
            return None

    @staticmethod
    def _planned_args(goal: dict, args: dict) -> bool:
        spec = goal["spec"]
        steps = [step for step in spec["steps"] if step.get("capability") == "browser.research" and
                 step.get("args") == args]
        refs = set(spec["permissions"]["resource_refs"])
        required = {"app:com.microsoft.edgemac", "site:python.org",
                    "window:com.microsoft.edgemac:" + args["window_title"],
                    "resource:public-search-" + hashlib.sha256(args["query"].encode()).hexdigest()[:16]}
        return (len(steps) == 1 and goal["digest"] == plan_digest(spec) and
                goal["approval_digest"] == goal["digest"] and
                "browser.research" in spec["permissions"]["capabilities"] and required <= refs)

    @staticmethod
    def _valid_args(args: Any) -> bool:
        return (isinstance(args, dict) and set(args) == RECIPE_FIELDS and
                args.get("recipe_id") == RECIPE_ID and
                type(args.get("recipe_revision")) is int and args["recipe_revision"] >= 1 and
                isinstance(args.get("recipe_digest"), str) and
                re.fullmatch(r"[0-9a-f]{64}", args["recipe_digest"]) is not None and
                args.get("target_bundle_id") == EDGE_BUNDLE_ID and
                isinstance(args.get("window_title"), str) and
                1 <= len(args["window_title"]) <= 160 - len("window:com.microsoft.edgemac:") and
                args.get("engine") == "python.org" and args.get("max_pages") == 3 and
                _valid_query(args.get("query")))

    def prepare(self, query: str) -> dict:
        if not _valid_query(query):
            return {"status": "BLOCKED", "error": "browser_query_invalid"}
        self.gui_lock_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(str(self.gui_lock_path), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        locked = False
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except BlockingIOError:
                return {"status": "BLOCKED", "error": "gui_resource_busy"}
            os.ftruncate(fd, 0)
            os.write(fd, json.dumps({"resource": "gui", "owner": "Muse worker",
                                     "purpose": "observe Edge search recipe", "pid": os.getpid()}).encode())
            with self.session_factory(self.workspace / ".muse-browser-sessions",
                                      allowed_domains=["python.org"]) as browser:
                browser.navigate(SEARCH_PAGE)
                store = RecipeStore(self.workspace, BrowserSearchLearningAdapter(browser))
                observed = store.observe(EDGE_BUNDLE_ID)
                fields = [item for item in observed["elements"] if item.get("role") == "AXSearchField"]
                buttons = [item for item in observed["elements"] if item.get("role") == "AXButton" and
                           item.get("name") == "Search"]
                if len(fields) != 1 or len(buttons) != 1:
                    raise ValueError("browser_search_controls_ambiguous")
                title = fields[0]["window_title"]
                if (title != buttons[0]["window_title"] or
                        not 1 <= len(title) <= 160 - len("window:com.microsoft.edgemac:")):
                    raise ValueError("browser_window_title_invalid")
                steps = [{"role": fields[0]["role"], "name": fields[0]["name"],
                          "window_title": title, "action": "set_value", "input": "query"},
                         {"role": buttons[0]["role"], "name": buttons[0]["name"],
                          "window_title": title, "action": "press", "input": None}]
                proposal = store.propose(RECIPE_ID, EDGE_BUNDLE_ID, steps)
                dry_run = store.dry_run(RECIPE_ID, {"window_title": title, "query": query})
                if dry_run.get("status") != "READY_FOR_APPROVAL":
                    raise ValueError("browser_recipe_dry_run_failed")
                recipe = {"query": query, "engine": "python.org", "max_pages": 3,
                          "recipe_id": RECIPE_ID, "recipe_revision": proposal["recipe"]["revision"],
                          "recipe_digest": proposal["digest"], "target_bundle_id": EDGE_BUNDLE_ID,
                          "window_title": title}
                return {"status": "PROPOSED", "browser_recipe": recipe,
                        "observed_controls": [{"role": step["selector"]["role"],
                                               "name": step["selector"]["name"],
                                               "action": step["action"]}
                                              for step in proposal["recipe"]["steps"]],
                        "side_effects": False}
        except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
            return {"status": "BLOCKED", "error": str(exc)[:160]}
        finally:
            if locked:
                os.ftruncate(fd, 0)
            os.close(fd)

    def enable_for_goal(self, *, goal_id: str, goal_revision: int, args: dict) -> dict:
        if not self._valid_args(args):
            return {"status": "BLOCKED", "error": "browser_recipe_args_invalid"}
        goal = self._goal(goal_id)
        if (goal is None or goal["status"] != "active" or goal["revision"] != goal_revision or
                not goal.get("approval_id") or
                datetime.fromisoformat(goal["approval_expires_at"]) <= datetime.now(timezone.utc) or
                not self._planned_args(goal, args)):
            return {"status": "BLOCKED", "error": "browser_recipe_goal_approval_missing_or_changed"}
        store = RecipeStore(self.workspace, None)
        with store._connect() as db:
            row = db.execute("SELECT revision,digest,enabled,approval_id FROM recipes WHERE id=? "
                             "ORDER BY revision DESC LIMIT 1", (RECIPE_ID,)).fetchone()
        if row is None or row["revision"] != args["recipe_revision"] or row["digest"] != args["recipe_digest"]:
            return {"status": "BLOCKED", "error": "browser_recipe_version_or_digest_changed"}
        with self._connect() as db:
            prior = db.execute("SELECT * FROM bindings WHERE goal_id=? AND goal_revision=? AND recipe_id=?",
                               (goal_id, goal_revision, RECIPE_ID)).fetchone()
        if prior is not None:
            if (prior["approval_id"] != goal["approval_id"] or
                    prior["plan_digest"] != goal["digest"] or
                    prior["recipe_digest"] != args["recipe_digest"] or
                    prior["recipe_revision"] != args["recipe_revision"] or
                    row["enabled"] != 1 or not row["approval_id"]):
                return {"status": "BLOCKED", "error": "browser_recipe_revoked_or_approval_changed"}
            return {"status": "ENABLED", "recipe_digest": args["recipe_digest"],
                    "approval_id": goal["approval_id"], "replayed": True}
        decision = store.decide(RECIPE_ID, args["recipe_revision"], args["recipe_digest"], approved=True)
        if decision.get("status") != "ENABLED":
            return decision
        with self._connect() as db:
            db.execute("INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?,?)",
                       (goal_id, goal_revision, goal["digest"], goal["approval_id"], RECIPE_ID,
                        args["recipe_revision"], args["recipe_digest"], args["query"], args["window_title"]))
        return {"status": "ENABLED", "recipe_digest": args["recipe_digest"],
                "approval_id": goal["approval_id"]}

    def validate_for_run(self, call: dict, context: dict) -> dict:
        args = call.get("args")
        if not self._valid_args(args) or context.get("gui_control_granted") is not True:
            raise ValueError("browser_recipe_scope_or_gui_missing")
        goal = self._goal(call.get("goal_id"))
        if (goal is None or goal["status"] != "running" or goal["revision"] != call.get("revision") or
                goal["run_id"] != context.get("run_id") or
                goal["approval_id"] != context.get("approval_id") or
                goal["digest"] != context.get("plan_digest") or
                datetime.fromisoformat(goal["approval_expires_at"]) <= datetime.now(timezone.utc) or
                not self._planned_args(goal, args)):
            raise ValueError("browser_recipe_goal_run_changed")
        steps = [step for step in goal["spec"]["steps"] if step.get("capability") == "browser.research" and
                 step.get("args") == args]
        if call.get("action_id") != context["run_id"] + ":" + steps[0]["id"]:
            raise ValueError("browser_recipe_action_outside_plan")
        with self._connect() as db:
            binding = db.execute("SELECT * FROM bindings WHERE goal_id=? AND goal_revision=? AND recipe_id=?",
                                 (call["goal_id"], call["revision"], RECIPE_ID)).fetchone()
        if (binding is None or binding["plan_digest"] != goal["digest"] or
                binding["approval_id"] != goal["approval_id"] or
                binding["recipe_revision"] != args["recipe_revision"] or
                binding["recipe_digest"] != args["recipe_digest"] or
                binding["query"] != args["query"] or binding["window_title"] != args["window_title"]):
            raise ValueError("browser_recipe_goal_binding_missing_or_changed")
        store = RecipeStore(self.workspace, None)
        with store._connect() as db:
            latest = db.execute("SELECT revision,digest,enabled FROM recipes WHERE id=? "
                                "ORDER BY revision DESC LIMIT 1", (RECIPE_ID,)).fetchone()
        if (latest is None or latest["revision"] != args["recipe_revision"] or
                latest["digest"] != args["recipe_digest"] or latest["enabled"] != 1):
            raise ValueError("browser_recipe_version_or_approval_changed")
        return args

    def search_with_recipe(self, browser: IsolatedEdgeSession, call: dict, context: dict) -> dict:
        args = self.validate_for_run(call, context)
        browser.navigate(SEARCH_PAGE)
        store = RecipeStore(self.workspace, BrowserSearchLearningAdapter(browser))
        result = store.run(RECIPE_ID, {"window_title": args["window_title"], "query": args["query"]},
                           approved=True, allowed_bundle_ids=[EDGE_BUNDLE_ID],
                           allowed_window_titles=[args["window_title"]],
                           expected_revision=args["recipe_revision"], expected_digest=args["recipe_digest"])
        if result.get("status") != "COMPLETED":
            raise ValueError("browser_recipe_run_blocked:" + str(result.get("error", result["status"])))
        search = browser.read_search_results(args["query"], engine="python.org")
        search["recipe_id"] = RECIPE_ID
        search["recipe_revision"] = args["recipe_revision"]
        search["recipe_digest"] = args["recipe_digest"]
        search["recipe_steps"] = result["steps"]
        return search

    def revoke(self, *, recipe_revision: int, recipe_digest: str) -> dict:
        if (type(recipe_revision) is not int or recipe_revision < 1 or
                not isinstance(recipe_digest, str) or
                re.fullmatch(r"[0-9a-f]{64}", recipe_digest) is None):
            return {"status": "BLOCKED", "error": "browser_recipe_version_or_digest_invalid"}
        return RecipeStore(self.workspace, None).decide(RECIPE_ID, recipe_revision,
                                                        recipe_digest, approved=False)
