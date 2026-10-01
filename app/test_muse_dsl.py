import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from muse_dsl import DslValidationError, decode_document, encode_document, goal_document
from muse_goal_store import GoalStore
from test_muse_goals import spec_for


NOW = datetime(2026, 9, 28, 5, 0, tzinfo=timezone.utc).isoformat()
SCOPE = {"project": "gosim-muse", "account": "local", "visibility": "personal"}
ORIGIN = {"type": "user", "ref": "request:1"}


def memory_document():
    return {
        "schema_version": "muse.dsl/1", "kind": "memory", "id": "memory:1", "revision": 1,
        "scope": SCOPE, "created_at": NOW, "updated_at": NOW, "origin": ORIGIN,
        "payload": {
            "subject_id": "entity:gosim", "predicate": "release_date", "value": "2026-09-28",
            "epistemic_type": "external_claim", "source_ids": ["source:official:1"],
            "observed_at": NOW, "valid_from": None, "valid_until": None,
            "relations": [], "deleted": False,
        },
    }


def capability_document():
    return {
        "schema_version": "muse.dsl/1", "kind": "capability", "id": "web.read", "revision": 1,
        "scope": SCOPE, "created_at": NOW, "updated_at": NOW,
        "origin": {"type": "local_runtime", "ref": "builtin-catalog"},
        "payload": {
            "capability_id": "web.read", "version": "1.0.0", "input_schema": {"type": "object"},
            "output_schema": {"type": "object"}, "target_app": None,
            "required_permissions": ["network.public_https"], "risk": "read",
            "preconditions": ["public_url"], "adapter": "web.read",
            "verification": {"http_status": 200}, "timeout_seconds": 8,
            "idempotent": True, "compensation": None,
        },
    }


class DslTests(unittest.TestCase):
    def test_all_three_roundtrip(self):
        goal = goal_document(spec_for("准备公开资料提纲"), created_at=NOW, updated_at=NOW)
        for document in (goal, memory_document(), capability_document()):
            self.assertEqual(decode_document(encode_document(document)), document)

    def test_existing_goal_store_exposes_same_spec_through_dsl(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = GoalStore(Path(tmp))
            spec = spec_for("准备公开资料提纲")
            spec["goal_id"] = "goal:test"
            goal = store.save_draft(spec, "request:1", {"provider": "fixture"})
            self.assertEqual(goal["dsl"]["payload"], goal["spec"])
            self.assertEqual(decode_document(encode_document(goal["dsl"])), goal["dsl"])
            self.assertEqual(GoalStore(Path(tmp)).get("goal:test")["dsl"]["payload"], spec)

    def test_rejects_invalid_version_identity_source_adapter_and_large_input(self):
        bad = []
        for field, value in (("schema_version", "muse.dsl/99"), ("id", "../escape")):
            item = memory_document()
            item[field] = value
            bad.append(item)
        item = memory_document()
        item["payload"]["source_ids"] = []
        bad.append(item)
        item = capability_document()
        item["payload"]["adapter"] = "eval"
        bad.append(item)
        item = capability_document()
        item["payload"]["capability_id"] = "wrong.name"
        bad.append(item)
        item = memory_document()
        item["payload"]["value"] = "x" * 70000
        bad.append(item)
        for item in bad:
            with self.subTest(item=item["kind"], field=item.get("id")):
                with self.assertRaises(DslValidationError):
                    encode_document(item)

    def test_rejects_duplicate_keys_and_ambiguous_time(self):
        raw = encode_document(memory_document())
        with self.assertRaises(DslValidationError):
            decode_document(raw.replace('"kind":"memory"', '"kind":"memory","kind":"goal"'))
        item = memory_document()
        item["payload"]["observed_at"] = "2026-09-28T13:00:00"
        with self.assertRaises(DslValidationError):
            encode_document(item)

    def test_redacted_memory_tombstone_roundtrip(self):
        item = memory_document()
        item["revision"] = 2
        item["payload"].update(value="", source_ids=[], relations=[], deleted=True)
        self.assertEqual(decode_document(encode_document(item)), item)
        item["payload"]["value"] = "leaked content"
        with self.assertRaises(DslValidationError):
            encode_document(item)


if __name__ == "__main__":
    unittest.main()
