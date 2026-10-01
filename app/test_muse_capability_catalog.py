import copy
import tempfile
import unittest
from pathlib import Path

from muse_capability_catalog import CapabilityCatalog
from muse_dsl import DslValidationError
from test_muse_dsl import capability_document


class CapabilityCatalogTests(unittest.TestCase):
    def test_staged_disabled_until_exact_revision_and_trusted_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = CapabilityCatalog(Path(tmp))
            document = capability_document()
            scope = document["scope"]
            staged = catalog.stage(document)
            self.assertEqual(staged["status"], "staged")
            self.assertFalse(staged["enabled"])
            self.assertFalse(catalog.approve("web.read", 2, staged["digest"], scope,
                                             trusted_adapters=frozenset({"web.read"})))
            self.assertFalse(catalog.approve("web.read", 1, staged["digest"], scope,
                                             trusted_adapters=frozenset()))
            self.assertTrue(catalog.approve("web.read", 1, staged["digest"], scope,
                                            trusted_adapters=frozenset({"web.read"})))
            self.assertTrue(CapabilityCatalog(Path(tmp)).get("web.read", scope)["enabled"])
            self.assertEqual(len(catalog.list(scope)), 1)
            other = {"project": "teacher-project", "account": "teacher", "visibility": "personal"}
            self.assertIsNone(catalog.get("web.read", other))
            self.assertEqual(catalog.list(other), [])

            changed = copy.deepcopy(document)
            changed["revision"] = 2
            changed["payload"]["version"] = "2.0.0"
            changed["payload"]["risk"] = "external_write"
            revised = catalog.stage(changed)
            self.assertFalse(revised["enabled"])
            self.assertFalse(catalog.approve("web.read", 2, staged["digest"], scope,
                                             trusted_adapters=frozenset({"web.read"})))
            self.assertTrue(catalog.approve("web.read", 2, revised["digest"], scope,
                                            trusted_adapters=frozenset({"web.read"})))
            self.assertTrue(catalog.revoke("web.read", scope))
            self.assertFalse(CapabilityCatalog(Path(tmp)).get("web.read", scope)["enabled"])

    def test_stage_refuses_skipped_revision_and_arbitrary_code_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = CapabilityCatalog(Path(tmp))
            document = capability_document()
            document["revision"] = 3
            with self.assertRaisesRegex(DslValidationError, "capability_revision_invalid"):
                catalog.stage(document)
            document["revision"] = 1
            document["payload"]["adapter"] = "eval"
            with self.assertRaisesRegex(DslValidationError, "untrusted_adapter"):
                catalog.stage(document)


if __name__ == "__main__":
    unittest.main()
