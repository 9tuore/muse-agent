import tempfile
import stat
import gzip
import unittest
import zlib
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from muse_capabilities import CapabilityExecutor, MAX_WEB_DECODED_BYTES, _decode_web_body, builtin_capability_documents


def call(action_id, capability, args):
    return {"action_id": action_id, "capability": capability, "args": args,
            "goal_id": "synthetic-goal", "revision": 1}


class MuseCapabilityTests(unittest.TestCase):
    def test_gzip_web_page_is_decoded_before_text_and_hash(self):
        html = '<html><title>GOSIM</title><body><h1>压缩网页</h1><p>真实正文</p></body></html>'.encode()
        compressed = gzip.compress(html)

        class Response:
            status = 200

            def getheader(self, name, default=""):
                return {"Content-Type": "text/html; charset=utf-8", "Content-Encoding": "gzip"}.get(name, default)

            def read(self, size):
                return compressed

        class Connection:
            def __init__(self, host, address):
                pass

            def request(self, *args, **kwargs):
                pass

            def getresponse(self):
                return Response()

            def close(self):
                pass

        with tempfile.TemporaryDirectory() as tmp, \
             patch("muse_capabilities._PinnedHTTPS", Connection), \
             patch("muse_capabilities._public_address", return_value="151.101.0.223"):
            receipt = CapabilityExecutor(Path(tmp)).execute(
                call("gzip-page", "web.read", {"url": "https://www.python.org/"}), approved=True)
        self.assertEqual(receipt["status"], "COMPLETED")
        self.assertIn("真实正文", receipt["output"]["text"])
        self.assertEqual(receipt["verification"]["decoded_bytes"], len(html))
        self.assertEqual(receipt["output"]["content_sha256"], __import__("hashlib").sha256(html).hexdigest())

    def test_compression_bomb_unknown_encoding_and_invalid_text_fail_closed(self):
        self.assertEqual(_decode_web_body(zlib.compress(b"valid"), "deflate"), b"valid")
        compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        raw_deflate = compressor.compress(b"raw") + compressor.flush()
        self.assertEqual(_decode_web_body(raw_deflate, "deflate"), b"raw")
        for raw, encoding, error in (
            (gzip.compress(b"x" * (MAX_WEB_DECODED_BYTES + 1)), "gzip", "decoded_page_too_large"),
            (gzip.compress(b"ok"), "br", "unsupported_content_encoding"),
            (gzip.compress(b"ok")[:-3], "gzip", "compressed_page_incomplete_or_trailing_data"),
            (gzip.compress(b"ok"), "identity", "compressed_body_without_content_encoding"),
        ):
            with self.subTest(encoding=encoding, error=error):
                with self.assertRaisesRegex(ValueError, error):
                    _decode_web_body(raw, encoding)

        class BadResponse:
            status = 200

            def getheader(self, name, default=""):
                return {"Content-Type": "text/plain; charset=utf-8", "Content-Encoding": "identity"}.get(name, default)

            def read(self, size):
                return b"\xff\xfe\x00"

        class BadConnection:
            def __init__(self, host, address):
                pass

            def request(self, *args, **kwargs):
                pass

            def getresponse(self):
                return BadResponse()

            def close(self):
                pass

        with tempfile.TemporaryDirectory() as tmp, \
             patch("muse_capabilities._PinnedHTTPS", BadConnection), \
             patch("muse_capabilities._public_address", return_value="151.101.0.223"):
            receipt = CapabilityExecutor(Path(tmp)).execute(
                call("bad-text", "web.read", {"url": "https://www.python.org/"}), approved=True)
        self.assertEqual(receipt["status"], "BLOCKED")

    def test_approval_and_unknown_capability_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            request = call("file-1", "workspace.write_artifact",
                           {"relative_path": "notes/a.txt", "content": "hello"})
            self.assertEqual(executor.execute(request, approved=False)["status"], "WAITING_APPROVAL")
            self.assertFalse((Path(tmp) / "notes/a.txt").exists())
            self.assertEqual(executor.execute(call("x", "shell.exec", {}), approved=True)["status"], "BLOCKED")
            self.assertEqual(executor.execute(call("s", "web.search", {"query": "Muse"}), approved=False)["status"],
                             "WAITING_APPROVAL")

    def test_search_receipt_and_catalog_revocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            document = next(item for item in builtin_capability_documents() if item["id"] == "web.search")
            import hashlib
            import json
            digest = hashlib.sha256(json.dumps(document, ensure_ascii=False, sort_keys=True,
                                               separators=(",", ":")).encode()).hexdigest()

            class Catalog:
                entry = {"document": document, "digest": digest, "enabled": True}

                def get(self, capability_id, scope):
                    return self.entry if capability_id == "web.search" else None

            catalog = Catalog()
            executor = CapabilityExecutor(Path(tmp), catalog=catalog)
            request = call("search-1", "web.search", {"query": "Python packaging", "max_results": 3})
            output = {"query": "Python packaging", "candidate_count": 1, "results": [{"url": "https://www.python.org/"}],
                      "search_page": "https://cn.bing.com/search?q=Python", "retrieved_at": "2026-09-28T00:00:00Z",
                      "content_sha256": "abc"}
            with patch("muse_web_search.search_public", return_value=output) as search:
                receipt = executor.execute(request, approved=True, context={"permissions": {"capabilities": ["web.search"]}})
            self.assertTrue(receipt["ok"])
            self.assertEqual(receipt["verification"]["public_results"], 1)
            search.assert_called_once()
            catalog.entry = dict(catalog.entry, enabled=False)
            self.assertEqual(executor.execute(request, approved=True)["error"],
                             "capability_catalog_not_enabled_or_changed")

    def test_browser_requires_exact_scope_and_gui_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            request = call("browser-1", "browser.research",
                           {"query": "Python packaging", "engine": "python.org", "max_pages": 1})
            context = {"permissions": {"capabilities": ["browser.research"],
                                       "resource_refs": ["app:com.microsoft.edgemac", "site:python.org"]},
                       "allowed_domains": ["python.org"]}
            self.assertEqual(executor.execute(request, approved=False, context=context)["status"], "WAITING_APPROVAL")
            self.assertEqual(executor.execute(request, approved=True, context=context)["error"],
                             "gui_control_not_granted")
            context["gui_control_granted"] = True
            context["permissions"]["resource_refs"] = ["app:com.microsoft.edgemac"]
            self.assertEqual(executor.execute(request, approved=True, context=context)["error"],
                             "browser_scope_not_approved")
            context["permissions"]["resource_refs"] = ["app:com.microsoft.edgemac", "site:python.org"]
            context["allowed_domains"] = ["www.example.org"]
            self.assertEqual(executor.execute(request, approved=True, context=context)["error"],
                             "domain_not_approved")

    def test_browser_skips_historical_candidates_and_checks_clicked_page(self):
        class Browser:
            browser_version = "fixture"
            clicked = []

            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def search(self, query, *, engine):
                return {"search_page": "https://www.python.org/search/?q=packaging", "results": [
                    {"title": "Built-in Package Support in Python 1.5", "url": "https://www.python.org/doc/essays/packages",
                     "snippet": "packaging", "result_index": 0},
                    {"title": "Catalog Requirements", "url": "https://www.python.org/community/sigs/retired/catalog-sig",
                     "snippet": "packaging", "result_index": 1},
                    {"title": "Packaging guide", "url": "https://www.python.org/doc/packaging",
                     "snippet": "packaging", "result_index": 2},
                ]}

            def navigate(self, url):
                return {}

            def click_result(self, index, url):
                self.clicked.append(index)
                return {"title": "Packaging guide", "text": "Current packaging guidance " * 10,
                        "source_url": url, "retrieved_at": "2026-09-28T00:00:00Z",
                        "content_sha256": "a" * 64, "click_transport": "cdp_mouse"}

        with tempfile.TemporaryDirectory() as tmp, patch("muse_browser.IsolatedEdgeSession", Browser):
            executor = CapabilityExecutor(Path(tmp))
            request = call("browser-filter", "browser.research",
                           {"query": "packaging", "engine": "python.org", "max_pages": 1})
            context = {"gui_control_granted": True, "allowed_domains": ["python.org"],
                       "permissions": {"capabilities": ["browser.research"],
                                       "resource_refs": ["app:com.microsoft.edgemac", "site:python.org"]}}
            receipt = executor.execute(request, approved=True, context=context)
        self.assertEqual(receipt["status"], "COMPLETED")
        self.assertEqual(Browser.clicked, [2])
        self.assertEqual(receipt["output"]["sources"][0]["rank"], 3)

    def test_artifact_readback_replay_and_changed_action_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            request = call("file-1", "workspace.write_artifact",
                           {"relative_path": "notes/a.txt", "content": "hello",
                            "sources": [{"url": "https://www.python.org/", "retrieved_at": "2026-09-27T12:00:00Z"}]})
            result = executor.execute(request, approved=True)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertTrue(result["verification"]["readback_matches"])
            self.assertEqual((Path(tmp) / "notes/a.txt").read_text(), "hello")
            self.assertEqual(stat.S_IMODE((Path(tmp) / ".muse-capability-actions.sqlite3").stat().st_mode), 0o600)
            replay = CapabilityExecutor(Path(tmp)).execute(request, approved=True)
            self.assertTrue(replay["evidence"]["replayed"])
            changed = call("file-1", "workspace.write_artifact",
                           {"relative_path": "notes/b.txt", "content": "changed"})
            self.assertEqual(executor.execute(changed, approved=True)["error"], "action_id_changed")
            self.assertFalse((Path(tmp) / "notes/b.txt").exists())

    def test_path_boundary_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            executor = CapabilityExecutor(Path(tmp))
            for index, path in enumerate(("../escape.txt", "/tmp/escape.txt", "a/../escape.txt")):
                result = executor.execute(call(str(index), "workspace.write_artifact",
                                               {"relative_path": path, "content": "x"}), approved=True)
                self.assertEqual(result["status"], "BLOCKED")
            (Path(tmp) / "link").symlink_to(outside, target_is_directory=True)
            result = executor.execute(call("link", "workspace.write_artifact",
                                           {"relative_path": "link/escape.txt", "content": "x"}), approved=True)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse((Path(outside) / "escape.txt").exists())

    def test_artifact_cannot_create_bridge_control_or_code_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            for index, path in enumerate(("outbox/qqmail-replies/send.json", "inbox/events.jsonl",
                                          "notes/run.py", "runtime/task.sh")):
                result = executor.execute(call("reserved-" + str(index), "workspace.write_artifact",
                                               {"relative_path": path, "content": "x"}), approved=True)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertFalse((Path(tmp) / path).exists())

    def test_web_read_rejects_private_and_unapproved_domains(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            private = executor.execute(call("private", "web.read", {"url": "https://127.0.0.1/"}), approved=True)
            self.assertEqual(private["error"], "ip_literal_rejected")
            scoped = executor.execute(call("scoped", "web.read", {"url": "https://www.python.org/"}),
                                      approved=True, context={"allowed_domains": ["www.gov.cn"]})
            self.assertEqual(scoped["error"], "domain_not_approved")

    def test_plan_permissions_restrict_capability_and_artifact_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            request = call("file-scope", "workspace.write_artifact",
                           {"relative_path": "notes/allowed.md", "content": "x"})
            context = {"permissions": {"capabilities": ["workspace.write_artifact"],
                                       "resource_refs": ["resource:workspace/notes/other.md"]}}
            self.assertEqual(executor.execute(request, approved=True, context=context)["error"],
                             "resource_outside_approved_plan")
            self.assertFalse((Path(tmp) / "notes/allowed.md").exists())
            context["permissions"]["resource_refs"] = ["resource:workspace/notes/allowed.md"]
            self.assertTrue(executor.execute(request, approved=True, context=context)["ok"])
            context["permissions"]["capabilities"] = []
            self.assertEqual(executor.execute(request, approved=True, context=context)["error"],
                             "capability_outside_approved_plan")

    def test_frontmost_app_requires_exact_approved_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            request = call("app-status", "system.frontmost_app", {})
            returned = CompletedProcess([], 0, '{"name":"TextEdit","bundle_id":"com.apple.TextEdit","pid":12,"category":""}', "")
            with patch("muse_capabilities.subprocess.run", return_value=returned):
                self.assertEqual(executor.execute(request, approved=True)["error"],
                                 "frontmost_app_outside_approved_scope")
                allowed = executor.execute(request, approved=True,
                                           context={"allowed_bundle_ids": ["com.apple.TextEdit"]})
                self.assertEqual(allowed["status"], "COMPLETED")
                self.assertEqual(allowed["output"]["bundle_id"], "com.apple.TextEdit")
                missing_refs = executor.execute(request, approved=True,
                                                context={"permissions": {"capabilities": ["system.frontmost_app"],
                                                                         "resource_refs": None}})
                self.assertEqual(missing_refs["error"], "frontmost_app_outside_approved_scope")
            with patch("muse_capabilities.subprocess.run", return_value=CompletedProcess([], 0, "[]", "")):
                self.assertEqual(executor.execute(request, approved=True)["error"],
                                 "frontmost_invalid_response")

    def test_app_health_is_parameterized_and_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = CapabilityExecutor(Path(tmp))
            request = call("app-health", "system.app_health", {"bundle_id": "com.apple.TextEdit"})
            context = {"permissions": {"capabilities": ["system.app_health"],
                                       "resource_refs": ["app:com.apple.TextEdit"]}}
            returned = CompletedProcess([], 0, '{"bundle_id":"com.apple.TextEdit","pids":[74531]}', "")
            with patch("muse_capabilities.subprocess.run", return_value=returned) as run:
                receipt = executor.execute(request, approved=True, context=context)
            self.assertEqual(receipt["status"], "COMPLETED")
            self.assertTrue(receipt["output"]["running"])
            self.assertFalse(receipt["verification"]["shell_used"])
            self.assertEqual(run.call_args.args[0][-1], "com.apple.TextEdit")
            context["permissions"]["resource_refs"] = ["app:com.apple.Finder"]
            self.assertEqual(executor.execute(request, approved=True, context=context)["error"],
                             "app_outside_approved_scope")
            injection = call("app-health-inject", "system.app_health",
                             {"bundle_id": "com.apple.TextEdit;touch /tmp/x"})
            self.assertEqual(executor.execute(injection, approved=True, context=context)["error"],
                             "sensitive_or_invalid_bundle")


if __name__ == "__main__":
    unittest.main()
