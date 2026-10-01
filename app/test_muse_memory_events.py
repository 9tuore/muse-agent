import tempfile
import unittest
from pathlib import Path

from agent_app import LocalAgent
from memory_store import MemoryStore
from test_muse_dsl import memory_document
from test_muse_memory_graph import source


class MemoryEventTests(unittest.TestCase):
    def test_user_can_explain_correct_pin_and_forget_scoped_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            memory = MemoryStore(workspace)
            claim = memory_document()
            memory.put_source(source(), claim["scope"])
            memory.put_claim(claim)
            agent = LocalAgent(workspace)
            listed = agent.handle({"type": "memory_claim_list"})
            self.assertEqual([item["id"] for item in listed["claims"]], ["memory:1"])
            explained = agent.handle({"type": "memory_claim_get", "claim_id": "memory:1"})
            self.assertEqual(explained["claim"]["sources"][0]["source_id"], "source:official:1")
            self.assertTrue(agent.handle({"type": "memory_claim_correct", "claim_id": "memory:1",
                                          "content": "2026-10-02"})["ok"])
            self.assertTrue(agent.handle({"type": "memory_claim_pin", "claim_id": "memory:1",
                                          "pinned": True})["ok"])
            self.assertEqual(agent.handle({"type": "memory_claim_get", "claim_id": "memory:1"})
                             ["claim"]["document"]["payload"]["epistemic_type"], "user_statement")
            self.assertEqual(agent.handle({"type": "memory_claim_revision", "claim_id": "memory:1",
                                           "revision": 1})["claim"]["payload"]["value"], "2026-09-28")
            self.assertFalse(agent.handle({"type": "memory_claim_list", "scope": {
                "project": "teacher-project", "account": "teacher", "visibility": "personal"}})["ok"])
            self.assertTrue(agent.handle({"type": "memory_claim_delete", "claim_id": "memory:1"})["ok"])
            restarted = LocalAgent(workspace)
            self.assertEqual(restarted.handle({"type": "memory_claim_list"})["claims"], [])
            self.assertFalse(restarted.handle({"type": "memory_claim_revision", "claim_id": "memory:1",
                                               "revision": 1})["ok"])


if __name__ == "__main__":
    unittest.main()
