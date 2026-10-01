import tempfile
import unittest
from pathlib import Path

from agent_app import LocalAgent


class ActivityHostTests(unittest.TestCase):
    def test_default_off_and_unselected_or_sensitive_scope_never_starts_observer(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            state = agent.handle({"type": "activity_status"})
            self.assertFalse(state["enabled"])
            self.assertEqual(state["recent"], [])
            for bundles in ([], ["com.apple.keychainaccess"], ["com.apple.TextEdit", "com.apple.Safari"]):
                result = agent.handle({"type": "activity_set", "enabled": True,
                                       "bundle_ids": bundles})
                self.assertEqual(result["status"], "REJECTED")
            self.assertEqual(agent.handle({"type": "activity_status"})["bundle_ids"], [])
            self.assertEqual(agent.handle({"type": "activity_poll"})["status"], "DISABLED")
            self.assertEqual(agent.handle({"type": "activity_set", "enabled": False})["status"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
