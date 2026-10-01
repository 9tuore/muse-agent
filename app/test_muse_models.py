import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from muse_models import ModelGateway


class _Handler(BaseHTTPRequestHandler):
    calls = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length))
        self.calls.append(request)
        if self.path.endswith("/v1/messages"):
            body = {
                "model": request["model"],
                "content": [{"type": "text", "text": '{"goal":"anthropic"}'}],
                "usage": {"input_tokens": 13, "output_tokens": 5},
            }
        else:
            body = {
                "model": request["model"],
                "choices": [{"message": {"content": '{"goal":"draft"}' if request["model"] == "high-test" else "local answer"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 4},
            }
        encoded = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        pass


class ModelGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
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
        self.endpoint = "http://127.0.0.1:%s/v1/chat/completions" % self.server.server_port
        settings = self.gateway.get_settings()
        settings["profiles"]["local-default"]["endpoint"] = self.endpoint
        settings["profiles"]["local-default"]["model"] = "local-test"
        settings["profiles"]["high-default"]["endpoint"] = self.endpoint
        settings["profiles"]["high-default"]["model"] = "high-test"
        self.gateway.update_settings(settings)
        _Handler.calls.clear()

    def tearDown(self):
        self.temp.cleanup()

    def test_modes_change_real_request_model(self):
        local = self.gateway.generate("hello", purpose="goal_plan")
        self.assertTrue(local["ok"])
        self.assertEqual(local["route"], "local")
        self.assertEqual(_Handler.calls[-1]["model"], "local-test")
        self.gateway.update_settings({"mode": "high"})
        high = self.gateway.generate("make JSON", purpose="goal_plan", require_json=True)
        self.assertTrue(high["ok"])
        self.assertEqual(json.loads(high["text"]), {"goal": "draft"})
        self.assertEqual(_Handler.calls[-1]["model"], "high-test")
        self.gateway.update_settings({"mode": "mixed"})
        self.assertEqual(self.gateway.generate("plan", purpose="goal_plan")["route"], "high")
        self.assertEqual(self.gateway.generate("chat", purpose="chat")["route"], "local")
        self.gateway.update_settings({"mode": "custom", "purpose_routes": {"chat": "high"}})
        self.assertEqual(self.gateway.generate("chat", purpose="chat")["route"], "high")
        self.assertEqual(self.gateway.generate("plan", purpose="goal_plan")["route"], "local")

    def test_local_chat_uses_distinct_message_roles(self):
        messages = [{"role": "system", "content": "回答最新问题"},
                    {"role": "user", "content": "第一问"},
                    {"role": "assistant", "content": "第一答"},
                    {"role": "user", "content": "第二问"}]
        result = self.gateway.generate("第二问", purpose="chat", local_messages=messages)
        self.assertTrue(result["ok"])
        self.assertEqual(_Handler.calls[-1]["messages"], messages)

    def test_missing_high_and_cloud_permission_fail_closed(self):
        self.gateway.update_settings({"mode": "high", "profiles": {
            **self.gateway.get_settings()["profiles"],
            "high-default": {**self.gateway.get_settings()["profiles"]["high-default"], "endpoint": ""},
        }})
        self.assertEqual(self.gateway.generate("x", purpose="chat")["error"], "model_slot_not_configured")
        self.assertEqual(_Handler.calls, [])
        settings = self.gateway.get_settings()
        settings["profiles"]["high-default"]["endpoint"] = "https://example.invalid/v1/chat/completions"
        self.gateway.update_settings(settings)
        self.assertEqual(self.gateway.generate("x", purpose="chat")["error"], "cloud_data_not_allowed")
        self.assertEqual(_Handler.calls, [])

    def test_remote_base_url_without_operation_is_rejected_before_request(self):
        settings = self.gateway.get_settings()
        settings["mode"] = "high"
        settings["cloud_data_allowed"] = True
        settings["daily_remote_call_limit"] = 1
        settings["profiles"]["high-default"]["endpoint"] = "https://example.invalid/v1"
        self.gateway.update_settings(settings)
        self.assertEqual(self.gateway.preview_cloud_request("hello", purpose="chat")["error"],
                         "model_endpoint_incomplete")
        self.assertEqual(self.gateway.generate("hello", purpose="chat")["error"],
                         "model_endpoint_incomplete")
        self.assertEqual(_Handler.calls, [])

    def test_budget_reserves_before_call(self):
        self.gateway.update_settings({"daily_token_limit": 20, "max_tokens_per_call": 10})
        first = self.gateway.generate("hello", purpose="chat", max_tokens=10)
        self.assertTrue(first["ok"])
        second = self.gateway.generate("hello", purpose="chat", max_tokens=10)
        self.assertEqual(second["error"], "model_budget_exhausted")
        self.assertEqual(len(_Handler.calls), 1)

    def test_invalid_remote_http_and_invalid_json_are_rejected(self):
        settings = self.gateway.get_settings()
        settings["profiles"]["high-default"]["endpoint"] = "http://example.invalid/v1/chat/completions"
        with self.assertRaisesRegex(ValueError, "remote_model_requires_https"):
            self.gateway.update_settings(settings)
        result = self.gateway.generate("hello", purpose="chat", require_json=True)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "UNAVAILABLE")
        with self.assertRaises(ValueError):
            self.gateway.update_settings({"mode": []})

    def test_local_slot_cannot_point_at_remote_https(self):
        settings = self.gateway.get_settings()
        settings["profiles"]["local-default"]["endpoint"] = "https://example.invalid/v1/chat/completions"
        settings["cloud_data_allowed"] = True
        settings["allow_unknown_cost"] = True
        with self.assertRaisesRegex(ValueError, "local_model_requires_loopback"):
            self.gateway.update_settings(settings)
        self.assertEqual(_Handler.calls, [])

    def test_per_goal_budget_and_corrupt_usage_fail_closed(self):
        self.gateway.update_settings({"per_goal_token_limit": 20, "max_tokens_per_call": 10})
        self.assertTrue(self.gateway.generate("hello", purpose="chat", goal_id="goal-a", max_tokens=10)["ok"])
        self.assertEqual(
            self.gateway.generate("hello", purpose="chat", goal_id="goal-a", max_tokens=10)["error"],
            "model_budget_exhausted",
        )
        self.assertTrue(self.gateway.generate("hello", purpose="chat", goal_id="goal-b", max_tokens=10)["ok"])
        self.gateway.usage_path.write_text("broken", encoding="utf-8")
        self.assertEqual(self.gateway.generate("hello", purpose="chat")["error"], "invalid_model_usage_state")

    def test_anthropic_messages_contract_on_local_fixture(self):
        settings = self.gateway.get_settings()
        settings["mode"] = "high"
        settings["profiles"]["high-default"]["protocol"] = "anthropic_messages"
        settings["profiles"]["high-default"]["endpoint"] = self.endpoint.replace("/v1/chat/completions", "/v1/messages")
        self.gateway.update_settings(settings)
        result = self.gateway.generate("return JSON", purpose="goal_plan", require_json=True)
        self.assertTrue(result["ok"])
        self.assertEqual(json.loads(result["text"]), {"goal": "anthropic"})
        self.assertEqual(result["usage"]["total_tokens"], 18)
        self.assertIn("system", _Handler.calls[-1])
        self.assertNotIn("temperature", _Handler.calls[-1])


if __name__ == "__main__":
    unittest.main()
