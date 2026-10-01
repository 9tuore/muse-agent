import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from muse_models import ModelGateway
from muse_provider_protocols import build_request, parse_response, parse_stream, reasoning_efforts


class ProviderProtocolTests(unittest.TestCase):
    def test_openai_responses_request_and_tool_proposal(self):
        payload = build_request(
            "openai_responses", "gpt-6-astra", "inspect file", 128, False, "high",
            [{"name": "read_file", "description": "Read an approved file",
              "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}], False)
        self.assertFalse(payload["store"])
        self.assertEqual(payload["reasoning"], {"effort": "high"})
        self.assertEqual(payload["tools"][0]["type"], "function")
        parsed = parse_response("openai_responses", {
            "status": "completed", "model": "gpt-6-astra",
            "output": [{"type": "function_call", "call_id": "call-1", "name": "read_file",
                        "arguments": '{"path":"approved.txt"}'}],
            "usage": {"input_tokens": 15, "output_tokens": 7}})
        self.assertEqual(parsed["tool_calls"][0]["arguments"], {"path": "approved.txt"})
        self.assertEqual(parsed["text"], "")
        self.assertEqual(reasoning_efforts("openai_responses", "unknown-model"), ())
        with self.assertRaisesRegex(ValueError, "reasoning_effort_unsupported"):
            build_request("openai_responses", "unknown-model", "x", 8, False, "high", None, False)

    def test_deepseek_stream_usage_and_tool_arguments(self):
        payload = build_request(
            "deepseek_chat", "deepseek-flash", "hello", 64, True, "low", None, True)
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["stream_options"], {"include_usage": True})
        frames = [
            {"model": "deepseek-flash", "choices": [{"delta": {"tool_calls": [
                {"index": 0, "id": "call-1", "function": {"name": "lookup", "arguments": "{\"q\":"}}]}}]},
            {"choices": [{"delta": {"tool_calls": [
                {"index": 0, "function": {"arguments": "\"Muse\"}"}}]}}]},
            {"choices": [{"delta": {}, "finish_reason": "tool_calls"}],
             "usage": {"prompt_tokens": 12, "completion_tokens": 5}},
        ]
        stream = io.BytesIO(b"".join(b"data: " + json.dumps(frame).encode() + b"\n\n"
                                    for frame in frames) + b"data: [DONE]\n")
        parsed = parse_stream("deepseek_chat", stream)
        self.assertEqual(parsed["tool_calls"], [{"call_id": "call-1", "name": "lookup",
                                                   "arguments": {"q": "Muse"}}])
        self.assertEqual((parsed["prompt_tokens"], parsed["completion_tokens"]), (12, 5))
        with self.assertRaisesRegex(ValueError, "model_stream_usage_missing"):
            parse_stream("deepseek_chat", io.BytesIO(b'data: {"choices": []}\n'))


class _ProviderFixture(BaseHTTPRequestHandler):
    requests = []

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).requests.append(request)
        if request.get("stream") and self.path == "/v1/responses":
            final = {"status": "completed", "model": request["model"],
                     "output": [{"type": "message", "content": [
                         {"type": "output_text", "text": "GPT streamed fixture"}]}],
                     "usage": {"input_tokens": 12, "output_tokens": 8}}
            encoded = b'data: ' + json.dumps({"type": "response.completed", "response": final}).encode() + b'\n\n'
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            self.wfile.write(encoded)
            return
        if self.path == "/v1/responses" and isinstance(request.get("input"), list):
            body = {"status": "completed", "model": request["model"],
                    "output": [{"type": "message", "content": [
                        {"type": "output_text", "text": "Verified result received"}]}],
                    "usage": {"input_tokens": 18, "output_tokens": 9}}
        elif self.path == "/v1/responses" and request.get("tools"):
            body = {"status": "completed", "model": request["model"],
                    "output": [{"type": "function_call", "call_id": "call-1",
                                "name": "read_file", "arguments": '{"path":"approved.txt"}'}],
                    "usage": {"input_tokens": 12, "output_tokens": 8}}
        elif self.path == "/v1/responses":
            body = {"status": "completed", "model": request["model"],
                    "output": [{"type": "message", "content": [
                        {"type": "output_text", "text": '{"answer":"GPT fixture"}'}]}],
                    "usage": {"input_tokens": 12, "output_tokens": 8}}
        elif self.path == "/chat/completions" and request.get("tools") and \
                not any(message.get("role") == "tool" for message in request["messages"]):
            body = {"model": request["model"], "choices": [{"message": {
                "role": "assistant", "content": None, "reasoning_content": "synthetic private reasoning",
                "tool_calls": [{"id": "dk-call-1", "type": "function", "function": {
                    "name": "lookup", "arguments": '{"q":"Muse"}'}}]}}],
                    "usage": {"prompt_tokens": 9, "completion_tokens": 4}}
        else:
            body = {"model": request["model"], "choices": [{"message": {"content": "DeepSeek fixture"}}],
                    "usage": {"prompt_tokens": 9, "completion_tokens": 4}}
        encoded = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        pass


class ModelGatewayProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _ProviderFixture)
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
        _ProviderFixture.requests.clear()

    def tearDown(self):
        self.temp.cleanup()

    def _configure(self, protocol, path, model):
        settings = self.gateway.get_settings()
        settings["mode"] = "high"
        settings["profiles"]["high-default"]["protocol"] = protocol
        settings["profiles"]["high-default"]["endpoint"] = f"http://127.0.0.1:{self.server.server_port}{path}"
        settings["profiles"]["high-default"]["model"] = model
        self.gateway.update_settings(settings)

    def test_local_fixture_openai_responses_and_deepseek_requests(self):
        self._configure("openai_responses", "/v1/responses", "gpt-6-astra")
        first = self.gateway.generate("reply JSON", purpose="chat", require_json=True,
                                      reasoning_effort="high")
        self.assertTrue(first["ok"], first)
        self.assertEqual(json.loads(first["text"]), {"answer": "GPT fixture"})
        self.assertFalse(_ProviderFixture.requests[-1]["store"])
        streamed = self.gateway.generate("stream", purpose="chat", stream=True)
        self.assertTrue(streamed["ok"], streamed)
        self.assertEqual(streamed["text"], "GPT streamed fixture")
        proposed = self.gateway.generate(
            "read", purpose="chat", tools=[{"name": "read_file", "description": "Read approved file",
                                             "parameters": {"type": "object", "properties": {}}}])
        self.assertFalse(proposed["ok"])
        self.assertEqual(proposed["status"], "TOOL_PROPOSAL")
        self.assertEqual(proposed["tool_calls"][0]["arguments"], {"path": "approved.txt"})
        completed = self.gateway.continue_tool_calls(
            proposed["proposal_id"], [{"call_id": "call-1", "output": {"verified": True}}])
        self.assertTrue(completed["ok"], completed)
        self.assertEqual(completed["text"], "Verified result received")
        self.assertEqual(_ProviderFixture.requests[-1]["input"][-1]["type"], "function_call_output")
        self.assertEqual(self.gateway.continue_tool_calls(proposed["proposal_id"], [])["error"],
                         "tool_proposal_expired")
        self._configure("deepseek_chat", "/chat/completions", "deepseek-flash")
        second = self.gateway.generate("hello", purpose="chat", reasoning_effort="low")
        self.assertTrue(second["ok"], second)
        self.assertEqual(second["text"], "DeepSeek fixture")
        self.assertEqual(_ProviderFixture.requests[-1]["reasoning_effort"], "low")
        self.assertNotIn("temperature", _ProviderFixture.requests[-1])
        proposed_deepseek = self.gateway.generate(
            "lookup", purpose="chat", tools=[{"name": "lookup", "description": "Lookup",
                                               "parameters": {"type": "object", "properties": {}}}])
        self.assertEqual(proposed_deepseek["status"], "TOOL_PROPOSAL")
        self.assertNotIn("reasoning", json.dumps(proposed_deepseek))
        continued_deepseek = self.gateway.continue_tool_calls(
            proposed_deepseek["proposal_id"], [{"call_id": "dk-call-1", "output": {"found": True}}])
        self.assertTrue(continued_deepseek["ok"], continued_deepseek)
        self.assertEqual(_ProviderFixture.requests[-1]["messages"][-1]["role"], "tool")
        self.assertEqual(_ProviderFixture.requests[-1]["messages"][-2]["reasoning_content"],
                         "synthetic private reasoning")

    def test_persisted_effort_changes_wire_and_old_settings_migrate(self):
        old = self.gateway.get_settings()
        old.pop("selected_reasoning_effort")
        old.pop("backup_high")
        old["version"] = 1
        self.gateway.settings_path.write_text(json.dumps(old), encoding="utf-8")
        self.assertEqual(self.gateway.get_settings()["version"], 3)
        self.assertEqual(self.gateway.get_settings()["backup_high"], "")
        old = self.gateway.get_settings()
        old.pop("backup_high")
        old["version"] = 2
        self.gateway.settings_path.write_text(json.dumps(old), encoding="utf-8")
        self.assertEqual(self.gateway.get_settings()["version"], 3)
        self._configure("deepseek_chat", "/chat/completions", "deepseek-flash")
        saved = self.gateway.update_settings({"selected_reasoning_effort": {"high-default": "max"}})
        self.assertEqual(saved["selected_reasoning_effort"]["high-default"], "max")
        self.assertEqual(self.gateway.profile_capabilities("high-default")["selected_reasoning_effort"], "max")
        reply = self.gateway.generate("hello", purpose="chat")
        self.assertTrue(reply["ok"], reply)
        self.assertEqual(_ProviderFixture.requests[-1]["reasoning_effort"], "max")
        settings = self.gateway.get_settings()
        settings["profiles"]["high-default"]["model"] = "unknown-model"
        with self.assertRaisesRegex(ValueError, "reasoning_effort_unsupported"):
            self.gateway.update_settings(settings)


if __name__ == "__main__":
    unittest.main()
