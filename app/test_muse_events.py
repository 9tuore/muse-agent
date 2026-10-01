import tempfile
import stat
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from muse_events import EventDeduper, WatchRegistry, WorkspaceWatcher, normalize_event


class MuseEventTests(unittest.TestCase):
    def test_normalize_legacy_mail_as_bounded_data(self):
        event = normalize_event({"type": "message_event", "source": "qqmail", "message_id": "qqmail:42",
                                 "sender_id": "sender@example.com", "text": "untrusted mail text",
                                 "metadata": {"subject": "Update"}}, account_scope="me@qq.com")
        self.assertEqual(event["event_id"], "qqmail:42")
        self.assertEqual(event["subject"], "Update")
        self.assertEqual(event["account_scope"], "me@qq.com")
        self.assertEqual(event["sensitivity"], "personal")
        self.assertEqual(event["payload"]["text"], "untrusted mail text")
        self.assertIn("+00:00", event["observed_at"])
        declassified = normalize_event({"source": "qqmail", "event_id": "other", "sensitivity": "public"})
        self.assertEqual(declassified["sensitivity"], "personal")

    def test_payload_secret_keys_filtered_and_duplicate_survives_restart(self):
        event = normalize_event({"source": "test", "event_id": "same", "payload": {"text": "data", "token": "secret"}})
        self.assertNotIn("token", event["payload"])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(EventDeduper(Path(tmp)).accept(event))
            self.assertFalse(EventDeduper(Path(tmp)).accept(event))
            self.assertEqual(stat.S_IMODE((Path(tmp) / ".muse-event-dedupe.sqlite3").stat().st_mode), 0o600)

    def test_naive_timestamp_rejected(self):
        with self.assertRaisesRegex(ValueError, "requires_timezone"):
            normalize_event({"source": "test", "observed_at": "2026-09-27T12:00:00"})

    def test_file_change_ref_requires_host_registration(self):
        raw = {"source": "workspace_watcher", "event_id": "change-1", "topic": "file.changed",
               "payload_ref": "resource:test-notes", "account_scope": "spoofed-account",
               "payload": {"relative_path": "notes/example.txt"}}
        self.assertNotIn("payload_ref", normalize_event(raw))
        event = normalize_event(raw, account_scope="local-workspace",
                                allowed_resource_refs={"resource:test-notes"})
        self.assertEqual(event["payload_ref"], "resource:test-notes")
        self.assertEqual(event["account_scope"], "local-workspace")
        self.assertNotEqual(event["account_scope"], raw["account_scope"])
        self.assertNotIn("payload_ref", normalize_event(raw, allowed_resource_refs={"resource:other"}))

    def test_selected_directory_change_and_restart_are_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "state"
            selected = Path(tmp) / "selected"
            selected.mkdir()
            watcher = WorkspaceWatcher(workspace, selected, "resource:test-notes")
            self.assertEqual(watcher.poll(approved=True), [])
            (selected / "draft.md").write_text("first", encoding="utf-8")
            self.assertEqual(watcher.poll(approved=False), [])
            changed = WorkspaceWatcher(workspace, selected, "resource:test-notes").poll(approved=True)
            self.assertEqual(len(changed), 1)
            self.assertEqual(changed[0]["topic"], "file.changed")
            self.assertEqual(changed[0]["payload_ref"], "resource:test-notes")
            self.assertEqual(changed[0]["payload"]["change"], "created")
            self.assertNotIn("first", str(changed[0]))
            self.assertEqual(WorkspaceWatcher(workspace, selected, "resource:test-notes").poll(approved=True), [])

    def test_watcher_skips_hidden_sensitive_and_symlink_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "state"
            selected = Path(tmp) / "selected"
            selected.mkdir()
            watcher = WorkspaceWatcher(workspace, selected, "resource:test-notes")
            watcher.poll(approved=True)
            (selected / ".hidden.md").write_text("hidden", encoding="utf-8")
            (selected / "passwords.txt").write_text("secret", encoding="utf-8")
            (selected / "link.md").symlink_to(selected / "passwords.txt")
            self.assertEqual(watcher.poll(approved=True), [])

    def test_registry_defaults_empty_and_revocation_stops_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "state"
            selected = Path(tmp) / "selected"
            selected.mkdir()
            registry = WatchRegistry(workspace)
            self.assertEqual(registry.list(), [])
            self.assertEqual(registry.poll(), [])
            with self.assertRaises(PermissionError):
                registry.set(selected, approved=False)
            with self.assertRaisesRegex(ValueError, "must_be_absolute"):
                registry.set(Path("."), approved=True)
            record = registry.set(selected, approved=True)
            self.assertEqual(registry.set(selected, approved=True)["resource_ref"], record["resource_ref"])
            self.assertEqual(len(WatchRegistry(workspace).list()), 1)
            self.assertEqual(registry.poll(), [])
            (selected / "draft.md").write_text("draft", encoding="utf-8")
            changed = WatchRegistry(workspace).poll()
            self.assertEqual(len(changed), 1)
            self.assertEqual(changed[0]["payload_ref"], record["resource_ref"])
            self.assertTrue(registry.revoke(record["resource_ref"]))
            self.assertFalse(registry.is_active(record["resource_ref"]))
            (selected / "draft.md").write_text("changed", encoding="utf-8")
            self.assertEqual(WatchRegistry(workspace).poll(), [])
            self.assertEqual(WatchRegistry(workspace).list(), [])
            second = registry.set(selected, approved=True)
            self.assertNotEqual(second["resource_ref"], record["resource_ref"])
            self.assertEqual(stat.S_IMODE((workspace / ".muse-watch-registry.sqlite3").stat().st_mode), 0o600)

    def test_revoke_waits_for_in_progress_registry_poll(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "state"
            selected = Path(tmp) / "selected"
            selected.mkdir()
            registry = WatchRegistry(workspace)
            ref = registry.set(selected, approved=True)["resource_ref"]
            registry.poll()
            (selected / "draft.md").write_text("changed", encoding="utf-8")
            entered = threading.Event()
            release = threading.Event()
            revoked = threading.Event()
            original = WorkspaceWatcher.poll

            def pause_poll(watcher, *, approved):
                entered.set()
                self.assertTrue(release.wait(2))
                return original(watcher, approved=approved)

            with patch.object(WorkspaceWatcher, "poll", pause_poll):
                observed = []
                polling = threading.Thread(target=lambda: observed.extend(registry.poll()))
                polling.start()
                self.assertTrue(entered.wait(2))
                revoking = threading.Thread(target=lambda: (registry.revoke(ref), revoked.set()))
                revoking.start()
                self.assertFalse(revoked.wait(0.1))
                release.set()
                polling.join(2)
                revoking.join(2)
            self.assertTrue(revoked.is_set())
            self.assertEqual(len(observed), 1)
            self.assertFalse(registry.is_active(ref))

    def test_watcher_bounds_all_directory_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "state"
            selected = Path(tmp) / "selected"
            selected.mkdir()
            for index in range(WorkspaceWatcher.MAX_ENTRIES + 1):
                (selected / ("ignored-" + str(index) + ".bin")).touch()
            watcher = WorkspaceWatcher(workspace, selected, "resource:test-notes")
            with self.assertRaisesRegex(ValueError, "watch_entry_limit_exceeded"):
                watcher.poll(approved=True)

    def test_oversize_file_is_not_reported_as_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "state"
            selected = Path(tmp) / "selected"
            selected.mkdir()
            target = selected / "draft.md"
            target.write_text("small", encoding="utf-8")
            watcher = WorkspaceWatcher(workspace, selected, "resource:test-notes")
            watcher.poll(approved=True)
            target.write_bytes(b"x" * (WorkspaceWatcher.MAX_FILE_BYTES + 1))
            self.assertEqual(watcher.poll(approved=True), [])
            target.write_text("small again", encoding="utf-8")
            events = watcher.poll(approved=True)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["payload"]["change"], "entered_scope")


if __name__ == "__main__":
    unittest.main()
