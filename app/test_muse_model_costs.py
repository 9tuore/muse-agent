import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from muse_model_costs import CostLedger
from muse_models import ModelGateway


class _RemoteFixture(BaseHTTPRequestHandler):
    calls = 0
    last_body = None
    auth_headers = []

    def do_POST(self):
        type(self).calls += 1
        type(self).auth_headers.append(self.headers.get("Authorization"))
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "https://other.invalid/v1/chat/completions")
            self.end_headers()
            return
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).last_body = data
        body = {"model": data["model"], "choices": [{"message": {"content": "ready"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
        encoded = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        pass


class CostLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = CostLedger(Path(self.temp.name))
        self.price = self.ledger.configure_price(
            profile_id="high-default", model="fixture", protocol="openai_compatible",
            origin="https://example.invalid:443", input_cny_per_million="100000",
            output_cny_per_million="100000", source="fixture confirmed", confirmed=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_concurrent_reservations_cannot_exceed_bucket(self):
        outcomes = []
        barrier = threading.Barrier(3)

        def reserve():
            barrier.wait()
            try:
                outcomes.append(self.ledger.reserve(self.price, 80, 20, "repair"))
            except ValueError as exc:
                outcomes.append(str(exc))

        threads = [threading.Thread(target=reserve) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join()
        self.assertEqual(sum(isinstance(item, tuple) for item in outcomes), 1)
        self.assertIn("model_money_budget_exhausted", outcomes)
        self.assertEqual(self.ledger.status()["reserved_micros"]["repair"], 10_000_000)

    def test_uncertain_charge_remains_reserved_across_restart(self):
        reservation, _ = self.ledger.reserve(self.price, 10, 5, "integration")
        self.ledger.uncertain(reservation)
        recovered = CostLedger(Path(self.temp.name)).status()
        self.assertEqual(recovered["uncertain_count"], 1)
        self.assertEqual(recovered["reserved_micros"]["integration"], 1_500_000)
        self.assertEqual(self.ledger.settle(reservation, self.price, 10, 5), 1_500_000)
        self.assertEqual(self.ledger.status()["uncertain_count"], 0)


class GatewayPaidBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _RemoteFixture)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.gateway = ModelGateway(Path(self.temp.name))
        settings = self.gateway.get_settings()
        settings["mode"] = "high"
        settings["cloud_data_allowed"] = True
        settings["allow_unknown_cost"] = True
        settings["daily_remote_call_limit"] = 3
        settings["profiles"]["high-default"]["endpoint"] = (
            f"http://127.0.0.1:{self.server.server_port}/v1/chat/completions")
        settings["profiles"]["high-default"]["model"] = "fixture"
        settings["profiles"]["high-default"]["keychain_service"] = "org.gosim.local-agent.model.high-default"
        settings["profiles"]["high-default"]["keychain_account"] = "high-default"
        self.gateway.update_settings(settings)
        _RemoteFixture.calls = 0
        _RemoteFixture.last_body = None
        _RemoteFixture.auth_headers.clear()

    def tearDown(self):
        self.temp.cleanup()

    def test_unknown_price_stops_before_network_even_with_legacy_toggle(self):
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False):
            result = self.gateway.generate("hello", purpose="chat")
        self.assertEqual(result["error"], "cost_unknown")
        self.assertEqual(_RemoteFixture.calls, 0)

    def test_paid_request_settles_reported_usage_and_redirect_stops(self):
        endpoint = self.gateway.get_settings()["profiles"]["high-default"]["endpoint"]
        origin = self.gateway._origin(endpoint)
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False):
            self.gateway.configure_pricing(
                profile_id="high-default", model="fixture", origin=origin,
                input_cny_per_million="10", output_cny_per_million="20",
                source="synthetic fixture price", confirmed=True)
        self.gateway.key_bindings_path.write_text(json.dumps({"high-default": origin}))
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False), \
                mock.patch.object(self.gateway, "_keychain_password", return_value="fixture-secret"):
            result = self.gateway.generate("hello", purpose="chat", max_tokens=16)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["usage"]["cost"]["micros"], 200)
        self.assertEqual(self.gateway.cost_status()["spent_micros"]["integration"], 200)
        settings = self.gateway.get_settings()
        settings["profiles"]["high-default"]["endpoint"] = endpoint.replace("/v1/chat/completions", "/redirect")
        self.gateway.update_settings(settings)
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False), \
                mock.patch.object(self.gateway, "_keychain_password", return_value="fixture-secret"):
            redirected = self.gateway.generate("hello", purpose="chat", max_tokens=16)
        self.assertFalse(redirected["ok"])
        self.assertEqual(self.gateway.cost_status()["uncertain_count"], 1)

    def test_preview_matches_sent_body_and_changed_prompt_stops_before_network(self):
        endpoint = self.gateway.get_settings()["profiles"]["high-default"]["endpoint"]
        origin = self.gateway._origin(endpoint)
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False):
            self.gateway.configure_pricing(
                profile_id="high-default", model="fixture", origin=origin,
                input_cny_per_million="10", output_cny_per_million="20",
                source="synthetic fixture price", confirmed=True)
            preview = self.gateway.preview_cloud_request("safe current request", purpose="chat", max_tokens=16)
        self.assertTrue(preview["ok"], preview)
        self.assertEqual(preview["destination"]["endpoint"], endpoint)
        self.assertEqual(preview["request_body"]["messages"][-1]["content"], "safe current request")
        self.gateway.key_bindings_path.write_text(json.dumps({"high-default": origin}))
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False), \
                mock.patch.object(self.gateway, "_keychain_password", return_value="fixture-secret"):
            changed = self.gateway.generate("different request", purpose="chat", max_tokens=16,
                                            cloud_preview_sha256=preview["sha256"])
            self.assertEqual(changed["error"], "cloud_preview_changed")
            self.assertEqual(_RemoteFixture.calls, 0)
            actual = self.gateway.generate("safe current request", purpose="chat", max_tokens=16,
                                           cloud_preview_sha256=preview["sha256"])
        self.assertTrue(actual["ok"], actual)
        self.assertEqual(_RemoteFixture.last_body, preview["request_body"])

    def test_sensitive_content_is_blocked_before_network_and_reservations(self):
        secrets = ("api_key=fixtureSecret123456", "Authorization: Bearer fixtureToken123456789",
                   "验证码：123456", "-----BEGIN PRIVATE KEY----- fixture")
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False):
            for secret in secrets:
                preview = self.gateway.preview_cloud_request(secret, purpose="chat")
                self.assertEqual(preview["error"], "cloud_sensitive_content")
                result = self.gateway.generate(secret, purpose="chat")
                self.assertEqual(result["error"], "cloud_sensitive_content")
                self.assertNotIn(secret, json.dumps(result, ensure_ascii=False))
        self.assertEqual(_RemoteFixture.calls, 0)
        self.assertFalse(self.gateway.usage_path.exists())
        self.assertEqual(self.gateway.cost_status()["uncertain_count"], 0)

    def test_remote_key_is_not_loaded_or_sent_after_profile_moves_to_loopback(self):
        # A high profile can retain its Keychain reference when its endpoint is
        # changed to a local service. The old remote key belongs to its origin.
        self.gateway.key_bindings_path.write_text(
            json.dumps({"high-default": "https://former-provider.example:443"}),
            encoding="utf-8")
        with mock.patch.object(self.gateway, "_keychain_password",
                               return_value="remote-key-must-stay-private") as lookup:
            result = self.gateway.generate("local request", purpose="chat", max_tokens=16)
        self.assertTrue(result["ok"], result)
        lookup.assert_not_called()
        self.assertEqual(_RemoteFixture.auth_headers, [None])


if __name__ == "__main__":
    unittest.main()
