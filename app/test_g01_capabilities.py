import tempfile
import time
import unittest
from pathlib import Path

from g01_capabilities import CapabilityError, CapabilityHost


class G01CapabilityHostTests(unittest.TestCase):
    def test_status_is_bounded_and_reports_worker_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = CapabilityHost(Path(tmp)).execute("system.status")
            self.assertTrue(result["ok"])
            self.assertEqual(result["source"], "g01-capability-host")
            self.assertEqual(result["worker"]["state"], "absent")
            self.assertNotIn("processes", result)

    def test_write_readback_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = CapabilityHost(Path(tmp))
            result = host.execute(
                "workspace.write_readback",
                {"relative_path": "notes/shift.txt", "content": "worker is ready"},
            )
            self.assertTrue(result["readback"])
            self.assertEqual((Path(tmp) / "notes/shift.txt").read_text(), "worker is ready")
            with self.assertRaisesRegex(CapabilityError, "overwrite_protection"):
                host.execute(
                    "workspace.write_readback",
                    {"relative_path": "notes/shift.txt", "content": "changed"},
                )
            host.execute(
                "workspace.write_readback",
                {"relative_path": "notes/shift.txt", "content": "changed", "overwrite": True},
            )
            self.assertEqual((Path(tmp) / "notes/shift.txt").read_text(), "changed")

    def test_path_escape_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            host = CapabilityHost(Path(tmp))
            for relative in ("../escape.txt", "/tmp/escape.txt", "a/../escape.txt"):
                with self.assertRaisesRegex(CapabilityError, "path_rejected"):
                    host.execute(
                        "workspace.write_readback",
                        {"relative_path": relative, "content": "blocked"},
                    )
            with self.assertRaisesRegex(CapabilityError, "reserved_path"):
                host.execute(
                    "workspace.write_readback",
                    {"relative_path": ".g01-test-worker.json", "content": "blocked"},
                )
            link = Path(tmp) / "link"
            link.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(CapabilityError, "symlink_path_rejected"):
                host.execute(
                    "workspace.write_readback",
                    {"relative_path": "link/escape.txt", "content": "blocked"},
                )
            self.assertFalse((Path(outside) / "escape.txt").exists())

    def test_owned_worker_start_health_stop_and_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = CapabilityHost(Path(tmp))
            started = host.execute("test_worker.start")
            self.assertEqual(started["state"], "running")
            healthy = host.execute("test_worker.health")
            self.assertTrue(healthy["healthy"])
            self.assertTrue(healthy["owned"])
            self.assertEqual(host.execute("test_worker.start")["state"], "already_running")
            stopped = host.execute("test_worker.stop")
            self.assertEqual(stopped["state"], "stopped")
            self.assertFalse(stopped["health"]["pid_alive"])
            self.assertEqual(host.execute("test_worker.health")["state"], "stopped")

    def test_lease_expiry_and_call_budget_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = CapabilityHost(Path(tmp))
            host.lease.expires_at = time.time() - 1
            with self.assertRaisesRegex(CapabilityError, "capability_lease_expired"):
                host.execute("system.status")
            host = CapabilityHost(Path(tmp))
            host.lease.max_calls["system.status"] = 1
            host.execute("system.status")
            with self.assertRaisesRegex(CapabilityError, "capability_call_limit_exceeded"):
                host.execute("system.status")


if __name__ == "__main__":
    unittest.main()
