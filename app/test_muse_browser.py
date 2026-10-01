import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from muse_browser import BrowserError, IsolatedEdgeSession, _CDP, discover_edge_binary


class BrowserBoundaryTests(unittest.TestCase):
    def test_missing_installed_browser_is_explicit(self):
        with patch("muse_browser.subprocess.run", return_value=CompletedProcess([], 0, "", "")):
            with self.assertRaisesRegex(BrowserError, "BLOCKED_BROWSER_UNAVAILABLE"):
                discover_edge_binary()

    def test_fresh_profile_is_removed_without_touching_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "keep.txt"
            existing.write_text("keep")
            edge = root / "edge"
            edge.write_text("fixture")
            session = IsolatedEdgeSession(root, edge_binary=edge)
            self.assertTrue(session.profile.is_dir())
            self.assertNotEqual(session.profile, root)
            session.close()
            self.assertFalse(session.profile.exists())
            self.assertEqual(existing.read_text(), "keep")

    def test_private_navigation_is_denied_before_cdp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edge = root / "edge"
            edge.write_text("fixture")
            session = IsolatedEdgeSession(root, edge_binary=edge)
            session.cdp = object()
            with self.assertRaisesRegex(ValueError, "ip_literal_rejected"):
                session.navigate("https://127.0.0.1/admin")
            session.cdp = None
            session.close()

    def test_intercepted_private_request_is_failed_not_continued(self):
        cdp = _CDP.__new__(_CDP)
        cdp.next_id = 0
        cdp.dns_checked = set()
        cdp.allowed_domains = ["python.org"]
        sent = []
        cdp._send = sent.append
        cdp._filter_request({"params": {"requestId": "one", "request": {"url": "https://127.0.0.1/private"}}})
        self.assertEqual(sent[-1]["method"], "Fetch.failRequest")
        with patch("muse_browser._public_address", return_value="151.101.0.223"):
            cdp._filter_request({"params": {"requestId": "two", "request": {"url": "https://www.python.org/"}}})
        self.assertEqual(sent[-1]["method"], "Fetch.continueRequest")

    def test_query_and_search_engine_rejected_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edge = root / "edge"
            edge.write_text("fixture")
            session = IsolatedEdgeSession(root, edge_binary=edge)
            with self.assertRaisesRegex(BrowserError, "query_invalid"):
                session.search("x")
            with self.assertRaisesRegex(BrowserError, "search_engine_not_reviewed"):
                session.search("Python", engine="arbitrary")
            session.close()


if __name__ == "__main__":
    unittest.main()
