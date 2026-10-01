import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from muse_models import ModelGateway


class _FallbackFixture(BaseHTTPRequestHandler):
    calls = []
    primary_code = 503
    backup_code = 200

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).calls.append((self.path, request["model"], self.headers.get("Authorization")))
        code = self.primary_code if self.path == "/primary" else self.backup_code
        if code != 200:
            self.send_response(code)
            self.end_headers()
            return
        body = {"model": request["model"], "choices": [{"message": {"content": "verified"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
        encoded = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        pass


class ModelFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _FallbackFixture)
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
        settings.update(mode="high", cloud_data_allowed=True, daily_remote_call_limit=3)
        origin = f"http://127.0.0.1:{self.server.server_port}"
        settings["profiles"]["high-default"].update(
            endpoint=origin + "/primary", model="primary-model",
            keychain_service="org.gosim.local-agent.model.high-default",
            keychain_account="high-default")
        settings["profiles"]["high-backup"] = {
            "protocol": "openai_compatible", "endpoint": origin + "/backup",
            "model": "backup-model",
            "keychain_service": "org.gosim.local-agent.model.high-backup",
            "keychain_account": "high-backup"}
        settings["backup_high"] = "high-backup"
        self.gateway.update_settings(settings)
        self.origin = self.gateway._origin(origin + "/primary")
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False):
            for profile_id, model in (("high-default", "primary-model"),
                                      ("high-backup", "backup-model")):
                self.gateway.configure_pricing(
                    profile_id=profile_id, model=model, origin=self.origin,
                    input_cny_per_million="1", output_cny_per_million="1",
                    source="synthetic fixture", confirmed=True)
        self.gateway.key_bindings_path.write_text(json.dumps({
            "high-default": self.origin, "high-backup": self.origin}), encoding="utf-8")
        _FallbackFixture.calls.clear()
        _FallbackFixture.primary_code = 503
        _FallbackFixture.backup_code = 200

    def tearDown(self):
        self.temp.cleanup()

    def generate(self, **kwargs):
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False), \
                mock.patch.object(self.gateway, "_keychain_password",
                                  side_effect=lambda profile: "fixture-" + profile["keychain_account"]):
            return self.gateway.generate("small approved prompt", purpose="chat", max_tokens=16,
                                         **kwargs)

    def test_preview_covers_primary_and_backup_bodies(self):
        with mock.patch.object(self.gateway, "_is_loopback", return_value=False):
            preview = self.gateway.preview_cloud_request("small approved prompt", purpose="chat",
                                                         max_tokens=16)
        self.assertTrue(preview["ok"], preview)
        self.assertEqual(preview["request_body"]["model"], "primary-model")
        self.assertEqual(preview["backup_request_body"]["model"], "backup-model")
        result = self.generate(cloud_preview_sha256=preview["sha256"])
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["provider"], "high-backup")
        self.assertEqual(len(_FallbackFixture.calls), 2)

        settings = self.gateway.get_settings()
        settings["profiles"]["high-backup"]["model"] = "changed-backup"
        self.gateway.update_settings(settings)
        _FallbackFixture.calls.clear()
        changed = self.generate(cloud_preview_sha256=preview["sha256"])
        self.assertEqual(changed["error"], "cloud_preview_changed")
        self.assertEqual(_FallbackFixture.calls, [])

    def test_service_failure_uses_separate_backup_key_and_reservations(self):
        result = self.generate()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["provider"], "high-backup")
        self.assertEqual(result["fallback"], {"attempted": True,
                                               "from_profile_id": "high-default",
                                               "primary_error": "provider_overloaded"})
        self.assertEqual(_FallbackFixture.calls, [
            ("/primary", "primary-model", "Bearer fixture-high-default"),
            ("/backup", "backup-model", "Bearer fixture-high-backup")])
        status = self.gateway.cost_status()
        self.assertEqual(status["uncertain_count"], 1)
        self.assertGreater(status["reserved_micros"]["integration"], 0)
        self.assertEqual(status["spent_micros"]["integration"], 15)

    def test_remote_call_limit_and_missing_backup_price_stop_second_request(self):
        self.gateway.update_settings({"daily_remote_call_limit": 1})
        limited = self.generate()
        self.assertFalse(limited["ok"])
        self.assertEqual(limited["fallback"]["error"], "model_budget_exhausted")
        self.assertEqual(len(_FallbackFixture.calls), 1)
        self.gateway.update_settings({"daily_remote_call_limit": 3})
        prices = self.gateway.costs.prices()
        prices.pop("high-backup")
        self.gateway.costs.prices_path.write_text(
            json.dumps({"version": 1, "prices": prices}), encoding="utf-8")
        self.gateway.usage_path.unlink()
        _FallbackFixture.calls.clear()
        missing = self.generate()
        self.assertEqual(missing["fallback"]["error"], "cost_unknown")
        self.assertEqual(len(_FallbackFixture.calls), 1)

    def test_cross_origin_and_parameter_error_do_not_forward(self):
        settings = self.gateway.get_settings()
        settings["profiles"]["high-backup"]["endpoint"] = (
            f"http://localhost:{self.server.server_port}/backup")
        self.gateway.update_settings(settings)
        blocked = self.generate()
        self.assertEqual(blocked["fallback"]["error"], "backup_scope_mismatch")
        self.assertEqual(len(_FallbackFixture.calls), 1)
        settings["profiles"]["high-backup"]["endpoint"] = (
            f"http://127.0.0.1:{self.server.server_port}/backup")
        self.gateway.update_settings(settings)
        _FallbackFixture.calls.clear()
        _FallbackFixture.primary_code = 400
        invalid = self.generate()
        self.assertEqual(invalid["error"], "provider_invalid_request")
        self.assertNotIn("fallback", invalid)
        self.assertEqual(len(_FallbackFixture.calls), 1)

    def test_both_unavailable_hold_both_uncertain_reservations(self):
        _FallbackFixture.backup_code = 503
        failed = self.generate()
        self.assertEqual(failed["provider"], "high-backup")
        self.assertEqual(failed["fallback"]["primary_error"], "provider_overloaded")
        self.assertEqual(len(_FallbackFixture.calls), 2)
        self.assertEqual(self.gateway.cost_status()["uncertain_count"], 2)

    def test_backup_selection_validation_and_cloud_off_block_all_calls(self):
        with self.assertRaisesRegex(ValueError, "backup_model_slot_invalid"):
            self.gateway.update_settings({"backup_high": "high-default"})
        with self.assertRaisesRegex(ValueError, "backup_model_slot_invalid"):
            self.gateway.update_settings({"backup_high": "unknown"})
        self.gateway.update_settings({"cloud_data_allowed": False})
        blocked = self.generate()
        self.assertEqual(blocked["error"], "cloud_data_not_allowed")
        self.assertEqual(_FallbackFixture.calls, [])


if __name__ == "__main__":
    unittest.main()
