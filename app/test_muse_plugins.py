"""The plugin registry never executes unreviewed or unapproved entries."""

import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

from muse_plugins import BUILTIN_ID, PluginRegistry, REVIEWED_MANIFEST_SHA256


class PluginRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)

    def test_builtin_requires_explicit_approval(self):
        registry = PluginRegistry(self.workspace)
        self.assertEqual(registry.list()[0]["status"], "DISABLED")
        self.assertEqual(registry.run(BUILTIN_ID, {"text": "你好"})["status"], "BLOCKED")
        self.assertEqual(registry.decide(BUILTIN_ID, "enable")["status"], "NEEDS_APPROVAL")
        self.assertEqual(registry.list()[0]["status"], "DISABLED")

    def test_approved_builtin_validates_input_and_output_across_restart(self):
        registry = PluginRegistry(self.workspace)
        approval = registry.decide(BUILTIN_ID, "enable", approved=True)
        self.assertEqual(approval["status"], "ENABLED")
        self.assertEqual(approval["manifest_digest"], REVIEWED_MANIFEST_SHA256)
        self.assertEqual(stat.S_IMODE(os.stat(registry.path).st_mode), 0o600)
        result = registry.run(BUILTIN_ID, {"text": "你好\n世界"})
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["output"], {"characters": 5, "lines": 2})
        self.assertEqual(result["verification"], "OUTPUT_SCHEMA_VALIDATED")
        restarted = PluginRegistry(self.workspace)
        self.assertEqual(restarted.list()[0]["status"], "ENABLED")
        self.assertEqual(restarted._approval()["approval_id"], approval["approval_id"])
        self.assertEqual(restarted._approval()["version"], approval["version"])
        self.assertEqual(restarted._approval()["digest"], REVIEWED_MANIFEST_SHA256)

    def test_disable_revokes_persistently(self):
        registry = PluginRegistry(self.workspace)
        first = registry.decide(BUILTIN_ID, "enable", approved=True)
        self.assertEqual(registry.decide(BUILTIN_ID, "disable")["status"], "DISABLED")
        restarted = PluginRegistry(self.workspace)
        self.assertEqual(restarted.list()[0]["status"], "DISABLED")
        self.assertEqual(restarted.run(BUILTIN_ID, {"text": "abc"})["status"], "BLOCKED")
        second = restarted.decide(BUILTIN_ID, "enable", approved=True)
        self.assertNotEqual(first["approval_id"], second["approval_id"])

    def test_changed_manifest_blocks_same_process_and_restart(self):
        copied_manifest = self.workspace / "reviewed.json"
        shutil.copyfile(Path(__file__).with_name("muse_plugin_manifest.json"), copied_manifest)
        registry = PluginRegistry(self.workspace, copied_manifest)
        registry.decide(BUILTIN_ID, "enable", approved=True)
        manifest = json.loads(copied_manifest.read_text(encoding="utf-8"))
        manifest["version"] = "2.0.0"
        copied_manifest.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(registry.list()[0]["status"], "BLOCKED_INVALID_MANIFEST")
        self.assertEqual(registry.run(BUILTIN_ID, {"text": "abc"})["status"], "BLOCKED")
        self.assertEqual(registry.decide(BUILTIN_ID, "enable", approved=True)["status"], "BLOCKED")
        self.assertEqual(PluginRegistry(self.workspace, copied_manifest).list()[0]["status"],
                         "BLOCKED_INVALID_MANIFEST")

    def test_unknown_plugin_is_metadata_only_even_with_approval(self):
        registry = PluginRegistry(self.workspace)
        marker = self.workspace / "executed"
        proposal = {"id": "thirdparty.evil", "version": "1.0.0",
                    "description": f"touch {marker}", "requested_capabilities": ["process.run"]}
        self.assertEqual(registry.stage(proposal)["status"], "STAGED_BLOCKED")
        self.assertEqual(PluginRegistry(self.workspace).list()[1]["status"], "STAGED_BLOCKED")
        self.assertEqual(registry.decide("thirdparty.evil", "enable", approved=True)["status"],
                         "BLOCKED")
        self.assertEqual(registry.run("thirdparty.evil", {"text": "abc"})["status"], "BLOCKED")
        self.assertFalse(marker.exists())
        self.assertEqual(registry.stage(dict(proposal, source_code="touch file"))["status"],
                         "REJECTED")

    def test_input_schema_rejects_extra_field_type_and_length(self):
        registry = PluginRegistry(self.workspace)
        registry.decide(BUILTIN_ID, "enable", approved=True)
        for payload in ({"text": "x", "path": "/etc/passwd"}, {"text": 1},
                        {"text": "x" * 2001}):
            with self.subTest(payload_type=str(type(payload["text"]))):
                self.assertEqual(registry.run(BUILTIN_ID, payload)["status"], "REJECTED")

    def test_unknown_decision_and_symlink_registry_are_rejected(self):
        registry = PluginRegistry(self.workspace)
        self.assertEqual(registry.decide(BUILTIN_ID, "approve", approved=True)["status"],
                         "REJECTED")
        other = self.workspace / "other"
        other.mkdir()
        (other / ".muse-plugin-registry.sqlite3").symlink_to(registry.path)
        with self.assertRaisesRegex(ValueError, "plugin_registry_symlink_rejected"):
            PluginRegistry(other)


if __name__ == "__main__":
    unittest.main()
