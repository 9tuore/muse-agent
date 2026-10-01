"""Declarative SDK lifecycle and host authority boundaries."""

import shutil
import tempfile
import unittest
from pathlib import Path

from muse_plugin_sdk import DeclarativePluginSDK, PluginAwareExecutor


HELLO = "example.hello-capability"
BROWSER = "example.browser-helper"


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, call, *, approved, context=None):
        self.calls.append((call, approved, context))
        return {"ok": True, "status": "COMPLETED",
                "output": {"query": call["args"]["query"], "sources": [
                    {"source_url": "https://www.python.org/", "title": "Python",
                     "text": "Public source", "retrieved_at": "2026-09-28T00:00:00Z",
                     "content_sha256": "a" * 64}]}}


class DeclarativePluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sdk = DeclarativePluginSDK(Path(self.temp.name))

    def test_hello_install_enable_disable_revoke_uninstall(self):
        self.assertEqual(self.sdk.install(HELLO, "1.0.0")["status"], "NEEDS_APPROVAL")
        self.assertEqual(self.sdk.install(HELLO, "1.0.0", approved=True)["status"], "INSTALLED_DISABLED")
        self.assertEqual(self.sdk.run(HELLO, {"name": "Muse"})["status"], "BLOCKED")
        self.assertEqual(self.sdk.decide(HELLO, "enable")["status"], "NEEDS_APPROVAL")
        self.assertEqual(self.sdk.decide(HELLO, "enable", approved=True)["status"], "ENABLED")
        self.assertEqual(self.sdk.run(HELLO, {"name": "Muse"})["output"], {"message": "Hello, Muse!"})
        self.assertEqual(self.sdk.run(HELLO, {"name": "Muse", "path": "/etc/passwd"})["status"], "REJECTED")
        self.assertEqual(self.sdk.decide(HELLO, "disable")["status"], "DISABLED")
        self.assertEqual(self.sdk.run(HELLO, {"name": "Muse"})["status"], "BLOCKED")
        self.assertEqual(self.sdk.decide(HELLO, "enable", approved=True)["status"], "ENABLED")
        self.assertEqual(self.sdk.decide(HELLO, "revoke")["status"], "REVOKED")
        self.sdk.decide(HELLO, "disable")
        self.assertEqual(self.sdk.decide(HELLO, "enable", approved=True)["error"],
                         "plugin_revoked_reinstall_required")
        self.assertEqual(self.sdk.decide(HELLO, "uninstall")["status"], "NEEDS_APPROVAL")
        self.assertEqual(self.sdk.decide(HELLO, "uninstall", approved=True)["status"], "UNINSTALLED")
        self.assertEqual(self.sdk.list_installed(), [])

    def test_reviewed_upgrade_resets_approval_and_downgrade_is_denied(self):
        self.sdk.install(BROWSER, "1.0.0", approved=True)
        first = self.sdk.decide(BROWSER, "enable", approved=True)
        self.assertEqual(self.sdk.install(BROWSER, "1.1.0", approved=True)["status"], "UPGRADED_DISABLED")
        self.assertEqual(self.sdk.list_installed()[0]["status"], "DISABLED")
        second = self.sdk.decide(BROWSER, "enable", approved=True)
        self.assertNotEqual(first["approval_id"], second["approval_id"])
        self.assertEqual(self.sdk.install(BROWSER, "1.0.0", approved=True)["error"],
                         "plugin_version_not_newer")
        self.assertEqual(self.sdk.install("../../evil", "1.0.0", approved=True)["status"], "BLOCKED")

    def test_changed_manifest_cannot_run_after_approval(self):
        examples = Path(__file__).with_name("plugin_examples")
        copied = Path(self.temp.name) / "manifests"
        shutil.copytree(examples, copied)
        sdk = DeclarativePluginSDK(Path(self.temp.name), manifest_dir=copied)
        sdk.install(HELLO, "1.0.0", approved=True)
        sdk.decide(HELLO, "enable", approved=True)
        with (copied / "hello-capability.json").open("ab") as stream:
            stream.write(b" ")
        self.assertEqual(sdk.run(HELLO, {"name": "Muse"})["status"], "BLOCKED")
        self.assertEqual(sdk.list_installed()[0]["status"], "BLOCKED_INVALID_MANIFEST")

    def test_browser_helper_delegates_only_trusted_goal_call(self):
        self.sdk.install(BROWSER, "1.1.0", approved=True)
        self.sdk.decide(BROWSER, "enable", approved=True)
        raw = FakeExecutor()
        adapter = PluginAwareExecutor(raw, self.sdk)
        call = {"goal_id": "approved-goal", "revision": 1, "action_id": "run-1:browser",
                "capability": "browser.research",
                "args": {"query": "Python 3.13", "engine": "python.org", "max_pages": 1}}
        context = {"allowed_domains": ["python.org"], "gui_control_granted": True}
        self.assertEqual(adapter.execute(call, approved=False, context=context)["status"], "BLOCKED")
        self.assertEqual(raw.calls, [])
        self.assertEqual(adapter.execute(call, approved=True, context=dict(context, allowed_domains=["example.org"]))["status"],
                         "BLOCKED")
        self.assertEqual(raw.calls, [])
        receipt = adapter.execute(call, approved=True, context=context)
        self.assertEqual(receipt["status"], "COMPLETED")
        self.assertEqual(receipt["plugin"]["id"], BROWSER)
        self.assertEqual(len(raw.calls), 1)
        self.sdk.decide(BROWSER, "revoke")
        # With the optional plugin disabled, the host's reviewed built-in path remains available.
        self.assertNotIn("plugin", adapter.execute(call, approved=True, context=context))


if __name__ == "__main__":
    unittest.main()
