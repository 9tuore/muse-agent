"""Portable layout tests; fixtures are synthetic, not Hub admission evidence."""
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

MODULE = Path(__file__).resolve().parents[1] / "check_release_layout.py"
spec = importlib.util.spec_from_file_location("release_layout", MODULE)
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)


def png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\0\0\0\0")) + chunk(b"IEND", b""))


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitattributes").write_text("bundle/** -text\n")
        self.manifest = {"id": "muse-layout-fixture", "version": "1.0.0", "integrity": {}}
        self.listing = {"icon": "icon.png", "screenshots": ["screen.png"]}
        self.save_json()
        (self.bundle / "main.splash").write_text('// Synthetic layout fixture\n')
        for name in ("icon.png", "screen.png"):
            (self.bundle / name).write_bytes(png())

    def save_json(self):
        (self.bundle / "manifest.json").write_text(json.dumps(self.manifest))
        (self.bundle / "listing.json").write_text(json.dumps(self.listing))

    def alias(self):
        path = self.root / "official_muse/app/bundle"
        path.parent.mkdir(parents=True)
        path.symlink_to("../../bundle")
        return path

    def test_publication_does_not_need_historical_source_tree(self):
        result = layout.check(self.root)
        self.assertEqual(result["mode"], "publication-layout")
        self.assertFalse(result["legacy_alias_checked"])

    def test_migration_requires_exact_alias_and_byte_identity(self):
        with self.assertRaisesRegex(ValueError, "Legacy bundle"):
            layout.check(self.root, migration=True)
        self.alias()
        reference = self.root / "frozen"
        shutil.copytree(self.bundle, reference)
        self.assertTrue(layout.check(self.root, reference, migration=True)["reference_byte_equal"])
        (self.bundle / "main.splash").write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "hashes differ"):
            layout.check(self.root, reference, migration=True)

    def test_agent_and_skill_text_allowed_by_locked_hub(self):
        (self.bundle / "AGENT.md").write_text("# Synthetic Agent\n")
        skill = self.bundle / "skills/read/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("# Synthetic skill\n")
        result = layout.check(self.root)
        self.assertIn("AGENT.md", result["files"])
        self.assertIn("skills/read/SKILL.md", result["files"])

    def test_reject_native_file(self):
        (self.bundle / "native.dylib").write_bytes(b"not permitted")
        with self.assertRaisesRegex(ValueError, "Unexpected file"):
            layout.check(self.root)

    def test_reject_internal_symlink(self):
        (self.bundle / "linked.png").symlink_to("icon.png")
        with self.assertRaisesRegex(ValueError, "ordinary files"):
            layout.check(self.root)

    def test_reject_noncanonical_bundle(self):
        self.bundle.rename(self.root / "elsewhere")
        self.bundle.symlink_to("elsewhere")
        with self.assertRaisesRegex(ValueError, "real canonical"):
            layout.check(self.root)

    def test_reject_missing_or_escaping_resources(self):
        for name in ("missing.png", "../icon.png", "/tmp/icon.png", "a\\icon.png", "a//icon.png"):
            with self.subTest(name=name):
                self.listing["icon"] = name
                self.save_json()
                with self.assertRaises(ValueError):
                    layout.check(self.root)

    def test_require_text_attributes(self):
        (self.root / ".gitattributes").write_text("bundle/** text\n")
        with self.assertRaisesRegex(ValueError, "-text"):
            layout.check(self.root)

    def test_sealed_rehearsal_is_not_editable_github_source(self):
        self.manifest["integrity"] = {"signature": "synthetic, not verified"}
        self.save_json()
        self.assertEqual(layout.check(self.root)["layout"], "PASS")
        result = subprocess.run(["python3", str(MODULE), "--root", str(self.root), "--for-github-release"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("github_prepare_blockers", result.stdout)


if __name__ == "__main__":
    unittest.main()
