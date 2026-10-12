#!/usr/bin/env python3
"""OFFLINE_GUARD_ONLY: synthetic path/hash/rect counterexamples, no GUI/network."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
from ua_gui import GUIEvidence, GuardBlocked, candidate_key, check_data_dir, check_frozen_identity, check_visible_widget


class GuardCounterexamples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="muse-zc05-offline-guards-")
        self.root = Path(self.temp.name)
        self.data = self.root / "fixture"
        (self.data / "apps/.host").mkdir(parents=True)
        for marker in (self.data / "FIXTURE_ONLY", self.data / "apps/.host/FIXTURE_ONLY"):
            marker.write_text("OFFLINE SYNTHETIC FIXTURE_ONLY\n")
        self.identity = {"data_dir": str(self.data), "production_scope_inventory_complete": True,
                         "production_data_dirs": [str(self.root / "synthetic-production")],
                         "git_commit": "a" * 40, "version": "offline-test", "candidate_id": "OFFLINE_ONLY",
                         "bundle_fingerprint": {"algorithm": "blake3", "value": "b" * 64},
                         "frozen_files": {}, "plugin_hashes": []}
        for name in ("main", "manifest", "host", "kernel", "launcher", "launcher_config", "catalog_summary"):
            path = self.root / name
            path.write_text(json.dumps({"version": "offline-test", "integrity": {"bundle_blake3": "b" * 64}})
                            if name == "manifest" else f"OFFLINE SYNTHETIC {name}")
            self.identity["frozen_files"][name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.pane = {"i": "AppHubView", "w": 1, "r": [0, 0, 1024, 660]}
        self.button = {"ty": "Button", "t": "Install", "w": 1, "r": [155, 527, 848, 46]}

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_fixture_markers_and_identity(self):
        check_data_dir(self.identity)
        check_frozen_identity(self.identity)

    def test_both_markers_required(self):
        for marker in (self.data / "FIXTURE_ONLY", self.data / "apps/.host/FIXTURE_ONLY"):
            saved = marker.read_bytes()
            marker.unlink()
            with self.assertRaises(GuardBlocked):
                check_data_dir(self.identity)
            marker.write_bytes(saved)

    def test_equal_ancestor_descendant_production_overlap(self):
        for forbidden in (self.data, self.root, self.data / "private-production"):
            identity = copy.deepcopy(self.identity)
            identity["production_data_dirs"] = [str(forbidden)]
            with self.assertRaises(GuardBlocked):
                check_data_dir(identity)

    def test_production_inventory_required(self):
        self.identity["production_data_dirs"] = []
        with self.assertRaises(GuardBlocked):
            check_data_dir(self.identity)

    def test_symlink_marker_rejected(self):
        marker = self.data / "apps/.host/FIXTURE_ONLY"
        marker.unlink()
        external = self.root / "external-marker"
        external.write_text("FIXTURE_ONLY")
        marker.symlink_to(external)
        with self.assertRaises(GuardBlocked):
            check_data_dir(self.identity)

    def test_every_required_frozen_component_required(self):
        for name in self.identity["frozen_files"]:
            identity = copy.deepcopy(self.identity)
            del identity["frozen_files"][name]
            with self.assertRaises(GuardBlocked):
                check_frozen_identity(identity)

    def test_kernel_launcher_and_config_mutation_rejected(self):
        for name in ("kernel", "launcher", "launcher_config", "catalog_summary"):
            identity = copy.deepcopy(self.identity)
            identity["frozen_files"][name]["sha256"] = "0" * 64
            with self.assertRaises(GuardBlocked):
                check_frozen_identity(identity)

    def test_plugin_hash_validated(self):
        self.identity["plugin_hashes"] = [dict(self.identity["frozen_files"]["main"], sha256="0" * 64)]
        with self.assertRaises(GuardBlocked):
            check_frozen_identity(self.identity)

    def test_version_and_bundle_fingerprint_bound_to_manifest(self):
        for field, value in (("version", "wrong-version"), ("bundle_fingerprint", {"algorithm": "blake3", "value": "c" * 64})):
            identity = copy.deepcopy(self.identity)
            identity[field] = value
            with self.assertRaises(GuardBlocked):
                check_frozen_identity(identity)

    def test_disabled_button_rejected(self):
        with self.assertRaises(GuardBlocked):
            check_visible_widget(dict(self.button, enabled=False), self.pane, [0, 0, 1024, 768])

    def test_root_observed_clipped_install_rejected(self):
        with self.assertRaises(GuardBlocked):
            check_visible_widget(dict(self.button, r=[155, 647, 848, 26]), self.pane, [0, 0, 1024, 768])

    def test_fully_contained_geometry_only_does_not_imply_gui_pass(self):
        check_visible_widget(self.button, self.pane, [0, 0, 1024, 768])
        # _unique separately requires the inspected native-image proof before input.
        helper = GUIEvidence.__new__(GUIEvidence)
        helper.identity = {"remote_window_rect": [0, 0, 1024, 768]}
        helper.snapshot = lambda: [self.button, self.pane]
        with self.assertRaises(GuardBlocked):
            helper._unique("Install", "Button", "AppHubView", None)

    def test_window_edge_and_foreign_window_rejected(self):
        for button in (dict(self.button, r=[900, 500, 848, 46]), dict(self.button, w=2)):
            with self.assertRaises(GuardBlocked):
                check_visible_widget(button, self.pane, [0, 0, 1024, 768])

    def test_same_candidate_key_ignores_restart_pid_but_not_changed_hash(self):
        other = copy.deepcopy(self.identity)
        other.update(owner_pid=123, native_window_id=456)
        self.assertEqual(candidate_key(self.identity), candidate_key(other))
        other["frozen_files"]["kernel"]["sha256"] = "0" * 64
        self.assertNotEqual(candidate_key(self.identity), candidate_key(other))


if __name__ == "__main__":
    print("OFFLINE_GUARD_ONLY: not a GUI test, not product PASS; no network or native window calls", flush=True)
    unittest.main()
