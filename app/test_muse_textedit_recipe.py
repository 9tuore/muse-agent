"""Goal and file boundaries for the synthetic TextEdit recipe host."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from muse_capabilities import BUILTIN_SCOPE, CapabilityExecutor, register_builtin_catalog
from muse_capability_catalog import CapabilityCatalog
from muse_textedit_recipe import TextEditRecipeHost


class FakeAX:
    text = "Muse synthetic starting text.\n"
    document = None
    actions = []
    focused = False
    focus_calls = []

    def __init__(self, helper_path, *, window_title=None):
        self.window_title = window_title

    def status(self):
        return {"status": "TRUSTED", "trusted": True}

    def document_url(self, bundle_id, window_title):
        return {"status": "COMPLETED", "document_url": self.document.as_uri(),
                "window_title": window_title}

    def focus_document(self, bundle_id, window_title, document_url):
        self.focus_calls.append((bundle_id, window_title, document_url))
        if document_url != self.document.as_uri():
            return {"status": "BLOCKED"}
        self.focused = True
        return {"status": "COMPLETED"}

    def snapshot(self, bundle_id):
        return {"bundle_id": bundle_id, "observed_at": "2026-09-28T00:00:00Z",
                "elements": [] if not self.focused else [{"role": "AXTextArea", "name": "First Text View", "path": "w0/0",
                              "window_title": self.window_title, "enabled": True,
                              "actions": ["set_value"], "value": self.text},
                             {"role": "AXMenuItem", "name": "Save", "path": "menu/0",
                              "window_title": self.window_title, "enabled": False,
                              "actions": ["press"]}]}

    def act(self, bundle_id, selector, action, value):
        self.actions.append(action)
        return {"status": "COMPLETED"}


class TextEditRecipeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "notes").mkdir()
        FakeAX.text = "Muse synthetic starting text.\n"
        self.path = self.root / "notes" / "Muse-Test-Alpha.txt"
        self.path.write_text(FakeAX.text, encoding="utf-8")
        self.helper = self.root / "helper"
        self.helper.write_text("fixture")
        FakeAX.document = self.path
        FakeAX.actions = []
        FakeAX.focused = False
        FakeAX.focus_calls = []
        self.patcher = patch("muse_textedit_recipe.NativeAXAdapter", FakeAX)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.host = TextEditRecipeHost(self.root, self.helper)

    def test_prepare_observes_but_cannot_enable_or_write(self):
        proposal = self.host.prepare(relative_path="notes/Muse-Test-Alpha.txt",
                                     content="Muse synthetic revised.\n")
        self.assertEqual(proposal["status"], "PROPOSED")
        self.assertEqual(FakeAX.focus_calls,
                         [("com.apple.TextEdit", self.path.name, self.path.as_uri())])
        self.assertEqual(len(proposal["observed_steps"]), 2)
        self.assertEqual(self.path.read_text(), FakeAX.text)
        self.assertEqual(FakeAX.actions, [])
        self.assertEqual(self.host.enable_for_goal(
            goal_id="goal:forged", goal_revision=1, recipe_id=proposal["recipe_id"],
            recipe_revision=proposal["revision"], digest=proposal["digest"])["status"], "BLOCKED")
        forged_call = {"goal_id": "goal:forged", "revision": 1, "action_id": "run:forged:edit",
                       "capability": "app.recipe", "args": {
                           key: proposal[key] for key in ("recipe_id", "revision", "digest", "target_bundle_id",
                                                      "window_title", "relative_path", "content")}}
        self.assertEqual(self.host.execute(forged_call, approved=True,
                                           context={"gui_control_granted": True})["status"], "BLOCKED")
        self.assertEqual(FakeAX.actions, [])

    def test_path_symlink_unsaved_value_and_document_mismatch_block(self):
        self.assertEqual(self.host.prepare(relative_path="../escape.txt", content="safe")["status"], "BLOCKED")
        outside = self.root / "outside.txt"
        outside.write_text("private")
        link = self.root / "notes" / "Muse-Test-Link.txt"
        link.symlink_to(outside)
        self.assertEqual(self.host.prepare(relative_path="notes/Muse-Test-Link.txt", content="safe")["status"],
                         "BLOCKED")
        with patch.object(FakeAX, "focus_document", return_value={"status": "BLOCKED"}):
            self.assertEqual(self.host.prepare(relative_path="notes/Muse-Test-Alpha.txt", content="safe")["error"],
                             "textedit_document_focus_failed")
        FakeAX.text = "unsaved edit"
        self.assertEqual(self.host.prepare(relative_path="notes/Muse-Test-Alpha.txt", content="safe")["error"],
                         "unsaved_changes_or_wrong_document")
        FakeAX.text = "Muse synthetic starting text.\n"
        FakeAX.document = outside
        self.assertEqual(self.host.prepare(relative_path="notes/Muse-Test-Alpha.txt", content="safe")["error"],
                         "textedit_helper_permission_or_document_mismatch")

    def test_recipe_capability_requires_host_and_enabled_catalog(self):
        catalog = CapabilityCatalog(self.root)
        register_builtin_catalog(catalog)
        self.assertTrue(self.host._catalog_enabled())
        direct = CapabilityExecutor(self.root, catalog=catalog).execute(
            {"action_id": "run:edit", "goal_id": "goal:test", "revision": 1,
             "capability": "app.recipe", "args": {}}, approved=True)
        self.assertEqual(direct["error"], "textedit_recipe_host_required")
        self.assertTrue(catalog.revoke("app.recipe", BUILTIN_SCOPE))
        self.assertFalse(self.host._catalog_enabled())


if __name__ == "__main__":
    unittest.main()
