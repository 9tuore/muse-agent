import tempfile
import unittest
from pathlib import Path

from muse_app_learning import RecipeStore


class FakeAX:
    def __init__(self):
        self.nodes = {
            "com.apple.TextEdit": [
                {"role": "AXTextArea", "name": "Document", "enabled": True,
                 "actions": ["set_value"], "value": "", "window_title": "Muse-Test.txt"}],
            "com.microsoft.edgemac": [
                {"role": "AXSearchField", "name": "Search", "enabled": True,
                 "actions": ["set_value"], "value": "", "window_title": "Muse-Test Browser"}],
        }
        self.actions = []

    def snapshot(self, bundle_id):
        return {"bundle_id": bundle_id, "observed_at": "2026-09-28T05:00:00+00:00",
                "elements": [dict(node) for node in self.nodes[bundle_id]]}

    def act(self, bundle_id, selector, action, value):
        self.actions.append((bundle_id, action, value))
        for node in self.nodes[bundle_id]:
            if node["role"] == selector["role"] and node["name"] == selector["name"]:
                node["value"] = value
                return {"status": "COMPLETED"}
        return {"status": "BLOCKED"}


class LearningTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.adapter = FakeAX()
        self.store = RecipeStore(Path(temp.name), self.adapter)

    def test_two_observed_apps_reuse_with_new_inputs_and_restart(self):
        for recipe_id, bundle, role, name, key, first, second, title in (
            ("textedit.write", "com.apple.TextEdit", "AXTextArea", "Document", "content", "alpha", "beta", "Muse-Test.txt"),
            ("edge.search", "com.microsoft.edgemac", "AXSearchField", "Search", "query", "Muse", "GOSIM", "Muse-Test Browser"),
        ):
            proposal = self.store.propose(recipe_id, bundle, [
                {"role": role, "name": name, "action": "set_value", "input": key}])
            self.assertEqual(self.store.dry_run(recipe_id, {key: first, "window_title": title})["status"], "READY_FOR_APPROVAL")
            self.assertEqual(self.store.run(recipe_id, {key: first, "window_title": title}, approved=True,
                                            allowed_bundle_ids=[bundle], allowed_window_titles=[title])["status"], "BLOCKED")
            self.assertEqual(self.store.decide(recipe_id, 1, proposal["digest"], approved=True)["status"], "ENABLED")
            for value in (first, second):
                result = self.store.run(recipe_id, {key: value, "window_title": title}, approved=True,
                                        allowed_bundle_ids=[bundle], allowed_window_titles=[title])
                self.assertEqual(result["status"], "COMPLETED")
                self.assertEqual(self.adapter.nodes[bundle][0]["value"], value)

    def test_unknown_or_dangerous_control_and_changed_ui_stop(self):
        with self.assertRaisesRegex(ValueError, "unsafe_or_unnamed_control"):
            self.store.propose("textedit.bad", "com.apple.TextEdit", [
                {"role": "AXButton", "name": "Delete", "action": "press", "input": None}])
        proposal = self.store.propose("textedit.write", "com.apple.TextEdit", [
            {"role": "AXTextArea", "name": "Document", "action": "set_value", "input": "content"}])
        self.store.decide("textedit.write", 1, proposal["digest"], approved=True)
        self.adapter.nodes["com.apple.TextEdit"][0]["name"] = "Different document"
        result = self.store.run("textedit.write", {"content": "safe", "window_title": "Muse-Test.txt"},
                                approved=True, allowed_bundle_ids=["com.apple.TextEdit"],
                                allowed_window_titles=["Muse-Test.txt"])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(self.adapter.actions, [])

    def test_press_allowlist_and_exact_window_scope(self):
        self.adapter.nodes["com.apple.TextEdit"].append(
            {"role": "AXButton", "name": "Publish", "enabled": True,
             "actions": ["press"], "window_title": "Muse-Test.txt"})
        with self.assertRaisesRegex(ValueError, "unsafe_or_unnamed_control"):
            self.store.propose("textedit.publish", "com.apple.TextEdit", [
                {"role": "AXButton", "name": "Publish", "window_title": "Muse-Test.txt",
                 "action": "press", "input": None}])
        self.adapter.nodes["com.apple.TextEdit"].append(
            {"role": "AXButton", "name": "Help", "enabled": True,
             "actions": ["press"], "window_title": "Muse-Test.txt"})
        with self.assertRaisesRegex(ValueError, "press_action_not_reviewed"):
            self.store.propose("textedit.help", "com.apple.TextEdit", [
                {"role": "AXButton", "name": "Help", "window_title": "Muse-Test.txt",
                 "action": "press", "input": None}])

    def test_revision_revoke_scope_and_input_are_enforced(self):
        step = {"role": "AXTextArea", "name": "Document", "action": "set_value", "input": "content"}
        first = self.store.propose("textedit.write", "com.apple.TextEdit", [step])
        self.store.decide("textedit.write", 1, first["digest"], approved=True)
        second = self.store.propose("textedit.write", "com.apple.TextEdit", [step])
        self.assertEqual(self.store.run("textedit.write", {"content": "x", "window_title": "Muse-Test.txt"},
                                        approved=True, allowed_bundle_ids=["com.apple.TextEdit"],
                                        allowed_window_titles=["Muse-Test.txt"])["status"], "BLOCKED")
        self.assertEqual(self.store.decide("textedit.write", 1, first["digest"], approved=True)["error"],
                         "stale_recipe_revision")
        self.store.decide("textedit.write", 2, second["digest"], approved=True)
        self.assertEqual(self.store.run("textedit.write", {"content": "x", "window_title": "Private.txt"},
                                        approved=True, allowed_bundle_ids=["com.apple.TextEdit"],
                                        allowed_window_titles=["Muse-Test.txt"])["error"],
                         "window_outside_approved_scope")
        self.assertEqual(self.store.run("textedit.write", {"content": "x", "window_title": "Muse-Test.txt"},
                                        approved=False, allowed_bundle_ids=["com.apple.TextEdit"],
                                        allowed_window_titles=["Muse-Test.txt"])["status"], "WAITING_APPROVAL")
        self.assertEqual(self.store.run("textedit.write", {"content": "x", "window_title": "Muse-Test.txt"},
                                        approved=True, allowed_bundle_ids=[],
                                        allowed_window_titles=["Muse-Test.txt"])["status"], "BLOCKED")
        self.store.decide("textedit.write", 2, second["digest"], approved=False)
        self.assertEqual(self.store.run("textedit.write", {"content": "x", "window_title": "Muse-Test.txt"},
                                        approved=True, allowed_bundle_ids=["com.apple.TextEdit"],
                                        allowed_window_titles=["Muse-Test.txt"])["status"], "BLOCKED")

    def test_expected_recipe_digest_blocks_before_any_ui_action(self):
        proposal = self.store.propose("edge.search", "com.microsoft.edgemac", [
            {"role": "AXSearchField", "name": "Search", "action": "set_value", "input": "query"}])
        self.store.decide("edge.search", 1, proposal["digest"], approved=True)
        result = self.store.run("edge.search", {"query": "Python 3.13", "window_title": "Muse-Test Browser"},
                                approved=True, allowed_bundle_ids=["com.microsoft.edgemac"],
                                allowed_window_titles=["Muse-Test Browser"],
                                expected_revision=1, expected_digest="0" * 64)
        self.assertEqual(result, {"status": "BLOCKED", "error": "recipe_version_or_digest_changed"})
        self.assertEqual(self.adapter.actions, [])


if __name__ == "__main__":
    unittest.main()
