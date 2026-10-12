"""Synthetic filesystem fixtures only; no GUI, service, model or live test."""
import copy
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import read_calendar_store as reader


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".reader-test-", dir=Path(__file__).parent)
        self.base = Path(self.temp.name)
        self.root = self.base / "zc05-round1/state"
        self.host = self.root / "apps/.host"
        self.store = self.host / "calendar/events.json"
        self.store.parent.mkdir(parents=True)
        for directory in (self.root, self.host):
            (directory / "FIXTURE_ONLY").write_text("SYNTHETIC TEST ONLY\n")
        self.spec = {"schema": 1, "fixture_kind": "SPRINT005_ZC05_CALENDAR_READBACK",
                     "case_name": "zc05-round1", "nonce": "UNIT-R1", "stable_ids": ["evt-unit-1"]}
        self.write_spec()
        self.event = {"id": "evt-unit-1", "title": "SPRINT005-ZC05-UNIT-R1-create", "start": "2026-10-12T16:00",
                      "end": "2026-10-12T16:30", "location": "SYNTHETIC", "notes": "UNIT FIXTURE", "timezone": "Asia/Shanghai"}
        self.store.write_text(json.dumps([self.event]))
        self.base_patch = patch.object(reader, "FIXTURE_BASE", self.base)
        self.base_patch.start()

    def tearDown(self):
        self.base_patch.stop()
        self.temp.cleanup()

    def write_spec(self):
        (self.root / reader.SPEC).write_text(json.dumps(self.spec))

    def read(self, method="get_event", args=None, root=None):
        if args is None:
            args = {"id": "evt-unit-1"} if method == "get_event" else {}
        return reader.readback(root or self.root, {"owner": "os.calendar", "method": method, "args": args})

    def refused(self, **kwargs):
        with self.assertRaises(reader.Refused):
            self.read(**kwargs)

    def test_create_edit_delete_and_reopen_exact_id(self):
        self.assertEqual(self.read()["result"]["event"], self.event)
        edited = {**self.event, "title": "SPRINT005-ZC05-UNIT-R1-edited", "start": "2026-10-12T17:00"}
        self.store.write_text(json.dumps([edited]))
        self.assertEqual(self.read()["result"]["event"], edited)
        self.store.write_text("[]")
        self.assertEqual(self.read()["result"], {"found": False, "event": None})
        # A new read opens the persisted owner store; this is not a Host restart.
        self.assertEqual(self.read()["evidence"]["event_count"], 0)

    def test_discover_before_binding_id(self):
        self.spec["stable_ids"] = []
        self.write_spec()
        events = self.read("events")["result"]["events"]
        self.assertEqual([e["id"] for e in events], ["evt-unit-1"])
        self.refused()
        self.spec["stable_ids"] = [events[0]["id"]]
        self.write_spec()
        self.assertTrue(self.read()["result"]["found"])

    def test_read_preserves_every_fixture_file_and_store_metadata(self):
        paths = [p for p in self.root.rglob("*") if p.is_file()]
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_ino) for p in paths}
        answer = self.read()
        self.assertEqual(answer["evidence"]["store_sha256"], hashlib.sha256(self.store.read_bytes()).hexdigest())
        self.assertFalse(answer["evidence"]["service_api_called"])
        self.assertEqual(answer["evidence"]["writes"], 0)
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_ino) for p in paths})

    def test_production_roots_refused_before_open(self):
        forbidden = [Path("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/live-acceptance-003/home"),
                     self.base / "formal-r3/state", self.root / "..", self.base / "zc05-round1/state/apps/.host"]
        with patch.object(reader.os, "open", side_effect=AssertionError("must not open rejected root")):
            for path in forbidden:
                with self.subTest(path=path):
                    self.refused(root=path)

    def test_marker_and_spec_are_required(self):
        for file in [self.root / "FIXTURE_ONLY", self.host / "FIXTURE_ONLY", self.root / reader.SPEC]:
            saved = file.read_bytes()
            file.unlink()
            self.refused()
            file.write_bytes(saved)

    def test_spec_identity_and_id_allowlist(self):
        for key, value in [("case_name", "zc05-another"), ("fixture_kind", "PRODUCTION"), ("nonce", "private text"),
                           ("schema", True), ("stable_ids", ["evt-unit-1", "evt-unit-1"]), ("stable_ids", ["../event"])]:
            original = copy.deepcopy(self.spec)
            self.spec[key] = value
            self.write_spec()
            with self.subTest(key=key):
                self.refused()
            self.spec = original
        self.write_spec()
        self.refused(args={"id": "unbound-id"})

    def test_symlink_files_refused(self):
        for file in [self.root / "FIXTURE_ONLY", self.host / "FIXTURE_ONLY", self.root / reader.SPEC, self.store]:
            backup = file.with_name(file.name + ".saved")
            file.rename(backup)
            file.symlink_to(backup)
            self.refused()
            file.unlink()
            backup.rename(file)

    def test_symlink_state_and_host_directories_refused(self):
        for directory in [self.host, self.root]:
            backup = directory.with_name(directory.name + ".saved")
            directory.rename(backup)
            directory.symlink_to(backup, target_is_directory=True)
            self.refused()
            directory.unlink()
            backup.rename(directory)

    def test_missing_and_corrupt_store_are_not_deletion(self):
        self.store.unlink()
        self.refused()
        self.store.write_text("{unfinished")
        self.refused()
        self.store.write_text('[{"id":"first","id":"evt-unit-1"}]')
        self.refused()

    def test_non_synthetic_and_duplicate_identity_refused(self):
        self.store.write_text(json.dumps([self.event, {**self.event, "id": "evt-unit-2", "title": "unrelated"}]))
        self.refused(method="events")
        self.store.write_text(json.dumps([self.event, self.event]))
        self.refused()

    def test_owner_write_methods_and_filters_refused(self):
        with self.assertRaises(reader.Refused):
            reader.readback(self.root, {"owner": "muse-goals", "method": "events", "args": {}})
        for method in ["add_event", "update_event", "remove_event", "notify", "turn/start"]:
            self.refused(method=method)
        self.refused(method="events", args={"from": "2026-10-12"})
        self.refused(args={"request_id": "unit"})

    def test_oversized_and_fifo_store_refused(self):
        self.store.write_bytes(b" " * (reader.MAX_BYTES + 1))
        self.refused()
        self.store.unlink()
        os.mkfifo(self.store)
        self.refused()

    def test_cli_rejects_oversized_request_before_reading_store(self):
        output = io.StringIO()
        with patch.object(reader.sys, "argv", ["reader", "--state-root", str(self.root)]), \
                patch.object(reader.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(b" " * 16385))), \
                patch.object(reader.sys, "stdout", output):
            self.assertEqual(reader.main(), 2)
        self.assertEqual(json.loads(output.getvalue())["error"], "request_too_large")


if __name__ == "__main__":
    unittest.main()
