"""Exercise a packaged worker's Memory commands in an isolated synthetic workspace."""

import argparse
import copy
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

import memory_store
from muse_dsl import DslValidationError
from memory_store import MemoryStore


LOCAL = {"project": "gosim-muse", "account": "local", "visibility": "personal"}
OTHER = {"project": "gosim-muse", "account": "other-fixture", "visibility": "personal"}
MARKER = "G02-CANDIDATE07-DELETE-MARKER"
CORRECTED = "G02-CANDIDATE07-USER-CORRECTED"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(source_id, value, now):
    return {"source_id": source_id, "kind": "url",
            "locator": "https://example.invalid/g02/synthetic/" + source_id,
            "content_sha256": sha(value.encode()), "observed_at": now, "updated_at": now}


def claim(claim_id, source_id, value, scope, predicate, now, relations=None):
    return {"schema_version": "muse.dsl/1", "kind": "memory", "id": claim_id,
            "revision": 1, "scope": scope, "created_at": now, "updated_at": now,
            "origin": {"type": "user", "ref": "request:g02-fixture"},
            "payload": {"subject_id": "entity:g02-fixture", "predicate": predicate,
                        "value": value, "epistemic_type": "external_claim",
                        "source_ids": [source_id], "observed_at": now,
                        "valid_from": None, "valid_until": None,
                        "relations": relations or [], "deleted": False}}


def worker(python, resources, workspace, events):
    env = dict(os.environ, GOSIM_LOCAL_INBOX="0", PYTHONPATH=str(resources),
               PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [str(python), "-B", str(resources / "desktop_worker.py"), str(workspace)],
        input="".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events),
        text=True, capture_output=True, env=env, timeout=30, check=True)
    replies = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    if len(replies) != len(events):
        raise AssertionError({"expected": len(events), "actual": len(replies),
                              "stdout": result.stdout[:1500], "stderr": result.stderr[:1000]})
    return dict(zip((event["type"] + ":" + str(index) for index, event in enumerate(events)), replies))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expect-fixed", action="store_true")
    args = parser.parse_args()
    resources = args.app.resolve() / "Contents/Resources"
    python = resources / "python/bin/python3"
    assert Path(sys.executable).resolve() == python.resolve(), "run with package's bundled Python"
    assert Path(memory_store.__file__).resolve() == resources / "memory_store.py"
    now = datetime.now(timezone.utc).isoformat()
    original = claim("memory:g02:source", "source:g02:original", MARKER,
                     LOCAL, "synthetic_release", now)
    related = claim("memory:g02:relation", "source:g02:related", "G02-RELATED",
                    LOCAL, "synthetic_relation", now,
                    [{"kind": "supports", "target_id": original["id"]}])
    foreign = claim("memory:g02:other", "source:g02:other", "G02-OTHER-ACCOUNT",
                    OTHER, "synthetic_release", now)
    with tempfile.TemporaryDirectory(prefix="gosim-g02-candidate07-memory-") as temporary:
        workspace = Path(temporary) / "workspace"
        selected = Path(temporary) / "selected"
        selected.mkdir()
        (selected / "synthetic.txt").write_text(MARKER + "\n", encoding="utf-8")
        memory = MemoryStore(workspace)
        for document in (original, related, foreign):
            memory.put_source(source(document["payload"]["source_ids"][0],
                                     document["payload"]["value"], now), document["scope"])
            memory.put_claim(document)
        memory.remember("note", "fixture", "G02-OTHER-ACCOUNT", "g02:other",
                        account_scope="other-fixture")
        phase1_events = [
            {"type": "memory_claim_list"},
            {"type": "memory_claim_get", "claim_id": original["id"]},
            {"type": "memory_claim_get", "claim_id": foreign["id"]},
            {"type": "memory_claim_list", "scope": OTHER},
            {"type": "memory_claim_correct", "claim_id": original["id"], "content": CORRECTED},
            {"type": "memory_claim_get", "claim_id": original["id"]},
            {"type": "memory_claim_revision", "claim_id": original["id"], "revision": 1},
            {"type": "memory_claim_pin", "claim_id": original["id"], "pinned": True},
            {"type": "memory_claim_get", "claim_id": original["id"]},
            {"type": "memory_claim_delete", "claim_id": original["id"]},
            {"type": "memory_claim_get", "claim_id": original["id"]},
            {"type": "memory_claim_revision", "claim_id": original["id"], "revision": 1},
            {"type": "memory_claim_list"},
            {"type": "memory_settings_set", "enabled": False},
            {"type": "memory_settings_get"},
        ]
        first = list(worker(python, resources, workspace, phase1_events).values())
        phase2_events = [
            {"type": "memory_claim_list"},
            {"type": "memory_claim_get", "claim_id": original["id"]},
            {"type": "memory_claim_get", "claim_id": related["id"]},
            {"type": "memory_claim_get", "claim_id": foreign["id"]},
            {"type": "memory_settings_get"},
            {"type": "memory_index_folder", "path": str(selected)},
            {"type": "memory_list"},
            {"type": "memory_search", "query": MARKER},
            {"type": "memory_list", "account_scope": "other-fixture"},
        ]
        second = list(worker(python, resources, workspace, phase2_events).values())
        restarted = MemoryStore(workspace)
        reimport = {}
        for name, source_id, value in (("original", "source:g02:original", MARKER),
                                       ("corrected", first[5]["claim"]["document"]["payload"]["source_ids"][0],
                                        CORRECTED)):
            candidate = copy.deepcopy(original)
            candidate["id"] = "memory:g02:reimport:" + name
            candidate["payload"]["source_ids"] = [source_id]
            candidate["payload"]["value"] = value
            try:
                restarted.put_claim(candidate)
            except DslValidationError as exc:
                reimport[name] = {"accepted": False, "reason": str(exc)}
            else:
                reimport[name] = {"accepted": True}
        with sqlite3.connect(str(workspace / "memory.sqlite3")) as db:
            db_state = {"integrity": db.execute("PRAGMA integrity_check").fetchone()[0],
                        "relation_rows": db.execute("SELECT COUNT(*) FROM muse_memory_relations").fetchone()[0],
                        "deleted_claim": db.execute("SELECT deleted,revision FROM muse_memory_claims "
                                                    "WHERE account='local' AND claim_id=?",
                                                    (original["id"],)).fetchone(),
                        "local_legacy_count": db.execute("SELECT COUNT(*) FROM memories WHERE "
                                                         "account_scope='local' AND deleted_at IS NULL").fetchone()[0]}
        checks = {
            "initial_claim_ids": [c["id"] for c in first[0]["claims"]],
            "initial_source_hash": first[1]["claim"]["sources"][0]["content_sha256"],
            "foreign_default_get": first[2]["status"],
            "foreign_scope_request": first[3],
            "correction_status": first[4]["status"],
            "corrected_revision": first[5]["claim"]["document"]["revision"],
            "corrected_source_kind": first[5]["claim"]["sources"][0]["kind"],
            "original_revision_before_delete": first[6]["status"],
            "pinned": first[8]["claim"]["pinned"],
            "delete_status": first[9]["status"],
            "tombstone_value": first[10]["claim"]["document"]["payload"]["value"],
            "revision_after_delete": first[11]["status"],
            "claim_ids_after_delete": [c["id"] for c in first[12]["claims"]],
            "recording_after_disable": first[14]["recording"],
            "claim_ids_after_restart": [c["id"] for c in second[0]["claims"]],
            "tombstone_after_restart": second[1]["claim"]["document"]["payload"]["deleted"],
            "relations_after_restart": second[2]["claim"]["document"]["payload"]["relations"],
            "foreign_after_restart": second[3]["status"],
            "foreign_backend_intact": restarted.get_claim(foreign["id"], OTHER) == foreign,
            "recording_after_restart": second[4]["recording"],
            "reindex_status": second[5]["memory_index"]["status"],
            "reindex_reported_files": second[5]["memory_index"]["indexed"],
            "local_legacy_records_after_reindex": len(second[6]["records"]),
            "local_search_matches_after_reindex": len(second[7]["memory_matches"]),
            "explicit_foreign_legacy_status": second[8]["status"],
            "explicit_foreign_legacy_records": len(second[8].get("records", [])),
            "reimport": reimport, "sqlite": db_state,
        }
        assert set(checks["initial_claim_ids"]) == {original["id"], related["id"]}
        assert checks["initial_source_hash"] == sha(MARKER.encode())
        assert checks["foreign_default_get"] == "NOT_FOUND"
        assert checks["foreign_scope_request"]["error"] == "memory_scope_not_authorized"
        assert checks["correction_status"] == checks["delete_status"] == "SAVED"
        assert checks["corrected_revision"] == 2 and checks["corrected_source_kind"] == "user"
        assert checks["original_revision_before_delete"] == "READY" and checks["pinned"]
        assert checks["tombstone_value"] == "" and checks["revision_after_delete"] == "NOT_FOUND"
        assert checks["claim_ids_after_delete"] == checks["claim_ids_after_restart"] == [related["id"]]
        assert checks["tombstone_after_restart"] and checks["relations_after_restart"] == []
        assert checks["foreign_after_restart"] == "NOT_FOUND" and checks["foreign_backend_intact"]
        assert checks["recording_after_disable"] is checks["recording_after_restart"] is False
        assert checks["reindex_status"] == "COMPLETED"
        assert checks["local_legacy_records_after_reindex"] == checks["local_search_matches_after_reindex"] == 0
        assert checks["sqlite"]["integrity"] == "ok" and checks["sqlite"]["relation_rows"] == 0
        if args.expect_fixed:
            assert checks["reimport"]["original"]["reason"] == "forgotten_source_cannot_reimport"
            assert checks["explicit_foreign_legacy_status"] == "REJECTED"
            assert checks["explicit_foreign_legacy_records"] == 0
        result = {"runtime": {"python": str(python), "worker": str(resources / "desktop_worker.py"),
                              "memory_store": memory_store.__file__, "workspace": "isolated temporary directory",
                              "fixture_source": "synthetic example.invalid URL; no network or model call"},
                  "checks": checks}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
