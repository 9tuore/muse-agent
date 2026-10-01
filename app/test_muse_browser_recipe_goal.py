"""Host-prepared browser recipes must remain inside an explicitly reviewed Goal."""

import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from muse_capabilities import CapabilityExecutor
from muse_goal_store import plan_digest
from muse_goals import GoalService, GoalValidationError, validate_plan


class NoModel:
    def generate(self, *_args, **_kwargs):
        raise AssertionError("proposal_must_not_call_model")


RECIPE = {"query": "Python 3.13", "engine": "python.org", "max_pages": 3,
          "recipe_id": "edge.public_search", "recipe_revision": 1,
          "recipe_digest": "a" * 64, "target_bundle_id": "com.microsoft.edgemac",
          "window_title": "Search | Python.org"}
TEXT = "用 Edge 浏览器在 Python.org 搜索 Python 3.13，读取三篇公开资料并写提纲"


class BrowserRecipeGoalTests(unittest.TestCase):
    def _service(self, workspace):
        return GoalService(workspace, NoModel(), CapabilityExecutor(workspace))

    def _draft(self, service, request_id="browser-recipe-test"):
        return service.handle({"type": "goal_propose", "request_id": request_id,
                               "text": TEXT, "browser_recipe": RECIPE})

    def test_draft_binds_exact_recipe_query_window_and_reviewed_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = self._service(Path(tmp))
            draft = self._draft(service)
            self.assertEqual(draft["status"], "DRAFT", draft)
            self.assertIsNone(draft["approval_id"])
            spec = draft["plan"]
            self.assertEqual(spec["steps"][0]["args"], RECIPE)
            self.assertEqual(draft["plan_digest"], plan_digest(spec))
            expected = {"app:com.microsoft.edgemac", "site:python.org",
                        "window:com.microsoft.edgemac:Search | Python.org",
                        "resource:public-search-c4a0ad648acc15c7"}
            self.assertEqual({item["ref"] for item in spec["context_refs"]}, expected)
            self.assertTrue(expected <= set(spec["permissions"]["resource_refs"]))
            self.assertEqual(service.handle({"type": "goal_revise", "goal_id": draft["goal_id"],
                                             "text": "更改查询"})["status"], "REJECTED")
            self.assertIsNone(service.store.decide(draft["goal_id"], 1, "approve"))
            self.assertIsNone(service.store.decide(draft["goal_id"], 1, "approve",
                                                    reviewed_digest="0" * 64))
            self.assertEqual(service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                             "revision": 1, "decision": "approve"})["error"],
                             "plan_digest_required_or_changed")
            approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve",
                                       "plan_digest": draft["plan_digest"]})
            self.assertEqual(approved["status"], "ACTIVE")
            self.assertEqual(service.store.get(draft["goal_id"])["approval_digest"], draft["plan_digest"])

    def test_recipe_fields_and_concrete_scope_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = self._draft(self._service(Path(tmp)))
            self.assertEqual(draft["status"], "DRAFT")
            original = draft["plan"]
            mutations = [
                lambda spec: spec["steps"][0]["args"].update(recipe_id="edge.other_search"),
                lambda spec: spec["steps"][0]["args"].update(recipe_revision=0),
                lambda spec: spec["steps"][0]["args"].update(recipe_digest="0"),
                lambda spec: spec["steps"][0]["args"].update(target_bundle_id="com.apple.Safari"),
                lambda spec: spec["steps"][0]["args"].update(window_title="Other window"),
                lambda spec: spec["steps"][0]["args"].update(approval_id="forged"),
                lambda spec: spec["context_refs"].pop(),
                lambda spec: spec["permissions"]["resource_refs"].append("site:example.org"),
                lambda spec: spec["permissions"]["resource_refs"].remove(
                    "resource:public-search-c4a0ad648acc15c7"),
            ]
            for mutate in mutations:
                with self.subTest(mutate=mutate):
                    changed = copy.deepcopy(original)
                    mutate(changed)
                    with self.assertRaises(GoalValidationError):
                        validate_plan(changed)
                    self.assertNotEqual(plan_digest(changed), draft["plan_digest"])

    def test_browser_recipe_proposal_requires_host_fields_and_explicit_user_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = self._service(Path(tmp))
            base = {"type": "goal_propose", "request_id": "invalid-browser-recipe",
                    "text": TEXT, "browser_recipe": RECIPE}
            for change in ({"browser_recipe": {"query": "Python 3.13"}},
                           {"context_refs": [{"ref": "site:python.org", "purpose": "forged"}]},
                           {"text": "整理公开资料"},
                           {"text": "用 Edge 浏览器在 Python.org 搜索 unrelated"}):
                with self.subTest(change=change):
                    result = service.handle(dict(base, **change))
                    self.assertIn(result["status"], {"INVALID_PLAN", "REJECTED"})
            self.assertIsNone(service.store.by_request(base["request_id"]))

    def test_changed_stored_plan_cannot_reuse_reviewed_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = self._service(Path(tmp))
            draft = self._draft(service)
            changed = copy.deepcopy(draft["plan"])
            changed["steps"][0]["args"]["query"] = "Python 3.14"
            with sqlite3.connect(str(service.store.path)) as db:
                db.execute("UPDATE muse_goal_revisions SET spec_json=? WHERE goal_id=? AND revision=1",
                           (json.dumps(changed, ensure_ascii=False, sort_keys=True), draft["goal_id"]))
            self.assertIsNone(service.store.decide(draft["goal_id"], 1, "approve",
                                                    reviewed_digest=draft["plan_digest"]))
            self.assertEqual(service.store.get(draft["goal_id"])["status"], "draft")


if __name__ == "__main__":
    unittest.main()
