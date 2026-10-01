"""The observed Edge form stays bound to the reviewed Goal revision."""

import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_app import LocalAgent
from muse_browser_learning import SEARCH_PAGE
from muse_browser_recipe import BrowserRecipeHost
from muse_capabilities import CapabilityExecutor
from muse_goals import GoalService


class NoModel:
    def generate(self, *_args, **_kwargs):
        raise AssertionError("host_prepared_goal_must_not_call_model")


class ObservedSearchSession:
    navigations = 0

    def __init__(self, _workspace, allowed_domains):
        assert allowed_domains == ["python.org"]
        self.url = "about:blank"

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass

    def navigate(self, url):
        type(self).navigations += 1
        self.url = url

    def _evaluate(self, expression):
        if expression == "location.href":
            return self.url
        if expression == "document.title":
            return "Welcome to Python.org"
        if "document.querySelectorAll('input,button')" in expression:
            return json.dumps([
                {"index": 0, "role": "AXSearchField", "name": "Search", "value": "",
                 "enabled": True, "x": 10, "y": 10, "width": 20, "height": 20},
                {"index": 1, "role": "AXButton", "name": "Search", "value": "",
                 "enabled": True, "x": 40, "y": 10, "width": 20, "height": 20},
            ])
        raise AssertionError(expression)


class ChangedSearchSession(ObservedSearchSession):
    def _evaluate(self, expression):
        value = super()._evaluate(expression)
        if "document.querySelectorAll('input,button')" in expression:
            controls = json.loads(value)
            controls[0]["name"] = "Changed Search"
            return json.dumps(controls)
        return value


class BrowserRecipeHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.host = BrowserRecipeHost(self.root, session_factory=ObservedSearchSession,
                                      gui_lock_path=self.root / "gui.lock")
        self.service = GoalService(self.root, NoModel(), CapabilityExecutor(self.root))

    def _prepared_draft(self):
        prepared = self.host.prepare("Python 3.13")
        self.assertEqual(prepared["status"], "PROPOSED", prepared)
        with sqlite3.connect(str(self.root / ".muse-app-recipes.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT enabled FROM recipes ORDER BY revision DESC LIMIT 1")
                             .fetchone()[0], 0)
        draft = self.service.handle({
            "type": "goal_propose", "request_id": "learned-edge", "browser_recipe": prepared["browser_recipe"],
            "text": "用 Edge 浏览器在 Python.org 搜索 Python 3.13，读取三篇公开资料并写提纲"})
        self.assertEqual(draft["status"], "DRAFT", draft)
        return prepared, draft

    def _approved_run(self):
        prepared, draft = self._prepared_draft()
        args = prepared["browser_recipe"]
        self.assertEqual(self.host.enable_for_goal(goal_id=draft["goal_id"], goal_revision=1,
                                                    args=args)["status"], "BLOCKED")
        wrong = self.service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                     "revision": 1, "decision": "approve", "plan_digest": "0" * 64})
        self.assertEqual(wrong["status"], "REJECTED")
        approved = self.service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                        "revision": 1, "decision": "approve",
                                        "plan_digest": draft["plan_digest"]})
        self.assertEqual(approved["status"], "ACTIVE")
        self.assertEqual(self.host.enable_for_goal(goal_id=draft["goal_id"], goal_revision=1,
                                                    args=args)["status"], "ENABLED")
        claimed = self.service.store.claim(draft["goal_id"], datetime.now(timezone.utc) +
                                           timedelta(minutes=1), "interval", None)
        self.assertEqual(claimed["status"], "running")
        run_id = claimed["run_id"]
        context = {"gui_control_granted": True, "run_id": run_id,
                   "approval_id": approved["approval_id"], "plan_digest": draft["plan_digest"]}
        call = {"goal_id": draft["goal_id"], "revision": 1, "action_id": run_id + ":browser",
                "capability": "browser.research", "args": args}
        self.assertEqual(self.host.validate_for_run(call, context), args)
        return prepared, draft, call, context

    def test_preparation_approval_and_refresh_fail_closed_before_search(self):
        prepared, _draft, call, context = self._approved_run()
        navigations = ObservedSearchSession.navigations
        refreshed = self.host.prepare("Python 3.13")
        self.assertEqual(refreshed["status"], "PROPOSED")
        self.assertEqual(refreshed["browser_recipe"]["recipe_revision"], 2)
        browser = ObservedSearchSession(self.root, ["python.org"])
        with self.assertRaisesRegex(ValueError, "browser_recipe_version_or_approval_changed"):
            self.host.search_with_recipe(browser, call, context)
        self.assertEqual(ObservedSearchSession.navigations, navigations + 1)
        self.assertEqual(browser.url, "about:blank")
        self.assertNotEqual(prepared["browser_recipe"]["recipe_digest"],
                            refreshed["browser_recipe"]["recipe_digest"])

    def test_revocation_and_changed_query_block_existing_binding(self):
        prepared, _draft, call, context = self._approved_run()
        changed = dict(call, args=dict(call["args"], query="Python 3.14"))
        with self.assertRaisesRegex(ValueError, "browser_recipe_goal_run_changed"):
            self.host.validate_for_run(changed, context)
        self.assertEqual(self.host.revoke(recipe_revision=prepared["browser_recipe"]["recipe_revision"],
                                          recipe_digest=prepared["browser_recipe"]["recipe_digest"])["status"],
                         "DISABLED")
        with self.assertRaisesRegex(ValueError, "browser_recipe_version_or_approval_changed"):
            self.host.validate_for_run(call, context)

    def test_changed_live_control_blocks_without_press_or_fixed_search(self):
        _prepared, _draft, call, context = self._approved_run()
        browser = ChangedSearchSession(self.root, ["python.org"])
        with self.assertRaisesRegex(ValueError, "browser_recipe_run_blocked:control_missing_changed_or_disabled"):
            self.host.search_with_recipe(browser, call, context)
        self.assertEqual(browser.url, SEARCH_PAGE)

    def test_worker_event_pauses_old_digest_after_refresh(self):
        agent = LocalAgent(self.root / "agent-refresh")
        agent.muse_capabilities.gui_lock_path = self.root / "agent-refresh-gui.lock"
        agent._muse_browser_recipe_host.gui_lock_path = self.root / "agent-refresh-gui.lock"
        agent._muse_browser_recipe_host.session_factory = ObservedSearchSession
        first = agent.handle({"type": "browser_recipe_prepare", "query": "Python 3.13"})
        self.assertEqual(first["status"], "PROPOSED")
        draft = agent.handle({"type": "goal_propose", "request_id": "old-digest", "text":
                              "用 Edge 浏览器在 Python.org 搜索 Python 3.13，读取三篇公开资料并写提纲",
                              "browser_recipe": first["browser_recipe"]})
        self.assertEqual(draft["status"], "DRAFT")
        second = agent.handle({"type": "browser_recipe_prepare", "query": "Python 3.13"})
        self.assertEqual(second["browser_recipe"]["recipe_revision"], 2)
        result = agent.handle({"type": "goal_decide", "goal_id": draft["goal_id"], "revision": 1,
                               "decision": "approve", "plan_digest": draft["plan_digest"]})
        self.assertEqual(result["status"], "PAUSED")
        self.assertEqual(result["error"], "browser_recipe_version_or_digest_changed")
        self.assertEqual(list((self.root / "agent-refresh").rglob("*.md")), [])

    def test_worker_event_revocation_blocks_before_browser_launch(self):
        agent = LocalAgent(self.root / "agent-revoke")
        agent.muse_capabilities.gui_lock_path = self.root / "agent-revoke-gui.lock"
        agent._muse_browser_recipe_host.gui_lock_path = self.root / "agent-revoke-gui.lock"
        agent._muse_browser_recipe_host.session_factory = ObservedSearchSession
        prepared = agent.handle({"type": "browser_recipe_prepare", "query": "Python 3.13"})
        draft = agent.handle({"type": "goal_propose", "request_id": "revoke-before-tick", "text":
                              "用 Edge 浏览器在 Python.org 搜索 Python 3.13，读取三篇公开资料并写提纲",
                              "browser_recipe": prepared["browser_recipe"]})
        approved = agent.handle({"type": "goal_decide", "goal_id": draft["goal_id"], "revision": 1,
                                 "decision": "approve", "plan_digest": draft["plan_digest"]})
        self.assertEqual(approved["status"], "ACTIVE")
        revoked = agent.handle({"type": "browser_recipe_revoke", "recipe_revision": 1,
                                "recipe_digest": prepared["browser_recipe"]["recipe_digest"]})
        self.assertEqual(revoked["status"], "DISABLED")
        tick = agent.handle({"type": "goal_tick"})
        run = next(item for item in tick["results"] if item["goal_id"] == draft["goal_id"])
        self.assertEqual(run["status"], "WAITING_USER")
        self.assertIn("browser_recipe_version_or_approval_changed", run["error"])


if __name__ == "__main__":
    unittest.main()
