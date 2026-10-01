import copy
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from memory_store import MemoryStore
from muse_dsl import DslValidationError
from muse_memory_graph import MemoryGraph
from test_muse_dsl import NOW, memory_document


def source(source_id="source:official:1", text="official version", kind="url"):
    return {"source_id": source_id, "kind": kind, "locator": "https://example.org/release",
            "content_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "observed_at": NOW, "updated_at": NOW}


class MemoryGraphTests(unittest.TestCase):
    def test_claim_source_scope_conflict_and_delete_reimport(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            first = memory_document()
            scope = first["scope"]
            memory.put_source(source(), scope)
            memory.put_claim(first)
            explained = memory.explain_claim("memory:1", scope)
            self.assertEqual(explained["sources"][0]["content_sha256"], source()["content_sha256"])
            self.assertEqual(memory.find_claims(scope, subject_id="entity:gosim")[0], first)

            second = copy.deepcopy(first)
            second["id"] = "memory:2"
            second["payload"]["value"] = "2026-10-01"
            second["payload"]["relations"] = [{"kind": "contradicts", "target_id": "memory:1"}]
            memory.put_claim(second)
            self.assertEqual(len(memory.find_claims(scope, predicate="release_date")), 2)
            self.assertEqual(memory.get_claim("memory:2", scope)["payload"]["relations"][0]["kind"], "contradicts")

            other = {"project": "teacher-project", "account": "teacher", "visibility": "personal"}
            self.assertEqual(memory.find_claims(other), [])
            self.assertIsNone(memory.explain_claim("memory:1", other))
            self.assertTrue(memory.delete_claim("memory:1", scope))
            self.assertEqual(memory.get_claim("memory:1", scope)["payload"]["value"], "")
            retained = memory.find_claims(scope, predicate="release_date")
            self.assertEqual(len(retained), 1)
            self.assertEqual(retained[0]["id"], "memory:2")
            self.assertEqual(retained[0]["payload"]["relations"], [])
            self.assertEqual(memory.get_claim_revision("memory:2", 1, scope)["payload"]["relations"], [])
            with sqlite3.connect(str(Path(tmp) / "memory.sqlite3")) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM muse_memory_relations").fetchone()[0], 0)
            restored = copy.deepcopy(first)
            restored["id"] = "memory:3"
            with self.assertRaisesRegex(DslValidationError, "forgotten_source_cannot_reimport"):
                memory.put_claim(restored)
            restarted = MemoryStore(Path(tmp))
            self.assertEqual(restarted.get_claim("memory:1", scope)["payload"]["value"], "")
            self.assertEqual(len(restarted.find_claims(scope)), 1)

    def test_source_and_relation_must_exist_in_same_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            claim = memory_document()
            with self.assertRaisesRegex(DslValidationError, "source_not_found_in_scope"):
                memory.put_claim(claim)
            memory.put_source(source(), claim["scope"])
            claim["payload"]["relations"] = [{"kind": "supports", "target_id": "memory:missing"}]
            with self.assertRaisesRegex(DslValidationError, "relation_target_not_found_in_scope"):
                memory.put_claim(claim)

    def test_user_correction_has_revision_and_delete_purges_old_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            claim = memory_document()
            scope = claim["scope"]
            memory.put_source(source(), scope)
            memory.put_claim(claim)
            self.assertTrue(memory.correct_claim("memory:1", "2026-10-02", scope, user_ref="user:local"))
            revised = memory.get_claim("memory:1", scope)
            self.assertEqual(revised["revision"], 2)
            self.assertEqual(revised["payload"]["epistemic_type"], "user_statement")
            self.assertEqual(memory.get_claim_revision("memory:1", 1, scope)["payload"]["value"], "2026-09-28")
            self.assertTrue(memory.pin_claim("memory:1", True, scope))
            other = copy.deepcopy(claim)
            other["id"] = "memory:0"
            memory.put_claim(other)
            self.assertEqual(memory.find_claims(scope)[0]["id"], "memory:1")
            self.assertTrue(memory.explain_claim("memory:1", scope)["pinned"])
            self.assertTrue(memory.delete_claim("memory:1", scope))
            self.assertIsNone(memory.get_claim_revision("memory:1", 1, scope))
            self.assertEqual(memory.get_claim("memory:1", scope)["payload"]["value"], "")
            reimport = copy.deepcopy(claim)
            reimport["id"] = "memory:reimport-original"
            with self.assertRaisesRegex(DslValidationError, "forgotten_source_cannot_reimport"):
                memory.put_claim(reimport)
            with sqlite3.connect(str(Path(tmp) / "memory.sqlite3")) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM muse_memory_claim_revisions "
                                            "WHERE claim_id='memory:1'").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM muse_memory_pins "
                                            "WHERE claim_id='memory:1'").fetchone()[0], 0)

    def test_supersedes_cycle_is_rejected_without_partial_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            first = memory_document()
            scope = first["scope"]
            memory.put_source(source(), scope)
            memory.put_claim(first)
            second = copy.deepcopy(first)
            second["id"] = "memory:2"
            second["payload"]["relations"] = [{"kind": "supersedes", "target_id": "memory:1"}]
            memory.put_claim(second)
            first["revision"] = 2
            first["payload"]["relations"] = [{"kind": "supersedes", "target_id": "memory:2"}]
            with self.assertRaisesRegex(DslValidationError, "supersedes_cycle"):
                memory.put_claim(first)
            self.assertEqual(memory.get_claim("memory:1", scope)["revision"], 1)

    def test_deleting_goal_projection_also_redacts_structured_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            claim = memory_document()
            claim["id"] = "memory:run:test"
            claim["payload"]["source_ids"] = ["source:run:test"]
            source_record = source("source:run:test", "verified receipt", "runtime_receipt")
            source_record["locator"] = "run:test"
            memory.put_source(source_record, claim["scope"])
            memory.put_claim(claim)
            memory.remember("goal_result", "muse_goal", "verified receipt", "muse:run:test",
                            record_type="fact", confirmed=True)
            record_id = memory.list_records()[0]["id"]
            self.assertTrue(memory.delete(record_id))
            restarted = MemoryStore(Path(tmp))
            self.assertEqual(restarted.find_claims(claim["scope"]), [])
            self.assertEqual(restarted.search("verified receipt"), [])
            restarted.remember("goal_result", "muse_goal", "verified receipt", "muse:run:test")
            self.assertEqual(restarted.count(), 0)

    def test_legacy_rows_survive_graph_migration_and_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            original = workspace / "memory.sqlite3"
            with sqlite3.connect(str(original)) as db:
                db.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, source TEXT NOT NULL, "
                           "external_id TEXT UNIQUE, content TEXT NOT NULL, created_at TEXT NOT NULL)")
                db.execute("INSERT INTO memories(kind,source,external_id,content,created_at) VALUES (?,?,?,?,?)",
                           ("chat_user", "local_user", "legacy:1", "旧记忆保留", NOW))
            backup = workspace / "backup.sqlite3"
            with sqlite3.connect(str(original)) as live, sqlite3.connect(str(backup)) as target:
                live.backup(target)
            memory = MemoryStore(workspace)
            self.assertEqual(memory.search("旧记忆")[0]["content"], "旧记忆保留")
            with sqlite3.connect(str(original)) as db, sqlite3.connect(str(backup)) as old:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(old.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertIsNone(old.execute("SELECT name FROM sqlite_master WHERE name='muse_memory_claims'").fetchone())
                self.assertEqual(db.execute("SELECT COUNT(*) FROM memories").fetchone()[0], 1)

    def test_failed_graph_migration_rolls_back_without_touching_legacy_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.sqlite3"
            with sqlite3.connect(str(path)) as db:
                db.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY, content TEXT)")
                db.execute("INSERT INTO memories(content) VALUES ('legacy intact')")
                db.execute("CREATE TABLE muse_memory_claims (incompatible TEXT)")
            with self.assertRaises(sqlite3.OperationalError):
                MemoryGraph(path)
            with sqlite3.connect(str(path)) as db:
                self.assertEqual(db.execute("SELECT content FROM memories").fetchone()[0], "legacy intact")
                self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='muse_memory_sources'").fetchone())
                self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='muse_memory_graph_migrations'").fetchone())
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")


if __name__ == "__main__":
    unittest.main()
