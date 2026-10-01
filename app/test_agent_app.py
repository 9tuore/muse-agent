import io
import json
import os
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from agent_app import HighTierClient, LocalAgent, LocalModelRouter, run_stream
from memory_store import MemoryStore


class _ModelHandler(BaseHTTPRequestHandler):
    response = {"route": "task_card"}

    def do_POST(self):  # noqa: N802 - stdlib handler API
        length = int(self.headers["Content-Length"])
        json.loads(self.rfile.read(length))
        body = json.dumps({"choices": [{"message": {"content": json.dumps(self.response)}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def _model_server(response):
    _ModelHandler.response = response
    server = HTTPServer(("127.0.0.1", 0), _ModelHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


class _HighTierHandler(BaseHTTPRequestHandler):
    calls = 0

    def do_POST(self):  # noqa: N802 - stdlib handler API
        _HighTierHandler.calls += 1
        length = int(self.headers["Content-Length"])
        json.loads(self.rfile.read(length))
        body = json.dumps(
            {
                "model": "test-high-tier",
                "choices": [{"message": {"content": json.dumps({"summary": "高阶摘要已返回"})}}],
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def _high_tier_server():
    _HighTierHandler.calls = 0
    server = HTTPServer(("127.0.0.1", 0), _HighTierHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


class LocalAgentTests(unittest.TestCase):
    def _connected_mail_contacts(self, workspace):
        (workspace / ".qqmail_bridge_health.json").write_text(json.dumps({"status": "CONNECTED"}))
        contacts = [
            {"contact_id": "alice-id", "name": "Alice", "address": "alice@example.com",
             "subject": "周末", "message_id_header": "<alice-message@example.com>",
             "source_message_id": "qqmail:11"},
            {"contact_id": "bob-id", "name": "Bob", "address": "bob@example.com",
             "subject": "资料", "message_id_header": "<bob-message@example.com>",
             "source_message_id": "qqmail:12"},
        ]
        (workspace / ".qqmail_contacts.json").write_text(json.dumps({
            "version": 1, "source": "qqmail_imap_recent_inbox_headers", "contacts": contacts,
        }))
        return contacts

    def test_contact_reply_works_without_incoming_result_card_and_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self._connected_mail_contacts(workspace)
            agent = LocalAgent(workspace)
            self.assertEqual(agent.result_cards.snapshot()["count"], 0)
            listing = agent.handle({"type": "mail_contacts_list"})
            self.assertEqual([item["address"] for item in listing["contacts"]],
                             ["alice@example.com", "bob@example.com"])
            changed = agent.handle({"type": "mail_reply_start", "contact_id": "bob-id",
                                    "source_message_id": "qqmail:old"})
            self.assertEqual(changed["error"], "mail_contact_changed_refresh_list")
            opened = agent.handle({"type": "mail_reply_start", "contact_id": "bob-id",
                                   "source_message_id": "qqmail:12"})
            self.assertEqual(opened["status"], "MANUAL_REPLY_CHOICE")
            card_id = opened["result_card"]["id"]
            self.assertFalse((workspace / "outbox").exists())
            agent.handle({"type": "mail_choice", "card_id": card_id, "choice": "reply_custom"})
            blocked = agent.handle({"type": "mail_reply_content", "card_id": card_id,
                                    "body": "资料已收到。"})
            self.assertEqual(blocked["error"], "explicit_send_confirmation_required")
            queued = agent.handle({"type": "mail_reply_content", "card_id": card_id,
                                   "body": "资料已收到。", "confirmed": True})
            self.assertEqual(queued["status"], "REPLY_QUEUED")
            request = json.loads(next((workspace / "outbox" / "qqmail-replies").glob("*.json")).read_text())
            self.assertEqual(request["to"], "bob@example.com")
            self.assertEqual(request["in_reply_to"], "<bob-message@example.com>")
            self.assertEqual(request["body"], "资料已收到。")

    def test_chat_can_select_exact_mail_contact_without_cloud_or_send(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self._connected_mail_contacts(workspace)
            agent = LocalAgent(workspace)
            prompt = "帮我给 Alice <alice@example.com> 回邮件"
            self.assertEqual(agent.handle({"type": "chat_preview", "text": prompt,
                                           "request_id": "reply:1"})["status"], "LOCAL")
            reply = agent.handle({"type": "chat_message", "text": prompt})
            self.assertIn("alice@example.com", reply["chat_reply"])
            self.assertEqual(agent.pending_mail_reply["sender"], "alice@example.com")
            self.assertFalse((workspace / "outbox").exists())
            contacts = agent.handle({"type": "chat_message", "text": "邮箱有哪些联系人？"})
            self.assertIn("Bob", contacts["chat_reply"])

    def test_contact_reply_rejects_stale_mail_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self._connected_mail_contacts(workspace)
            os.utime(workspace / ".qqmail_contacts.json", (0, 0))
            agent = LocalAgent(workspace)
            result = agent.handle({"type": "mail_reply_start", "contact_id": "alice-id"})
            self.assertEqual(result["status"], "REFRESHING")
            self.assertFalse((workspace / "outbox").exists())

    def test_selected_contact_temporarily_pauses_existing_mail_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self._connected_mail_contacts(workspace)
            agent = LocalAgent(workspace)
            incoming = agent.handle({"type": "message_event", "source": "qqmail",
                                     "message_id": "qqmail:incoming", "direction": "incoming",
                                     "sender_id": "friend@example.com", "text": "周末见吗？",
                                     "metadata": {"sender": "friend@example.com", "subject": "周末"}})
            first_card = incoming["result_card"]["id"]
            agent.handle({"type": "mail_choice", "card_id": first_card, "choice": "reply_custom"})
            selected = agent.handle({"type": "mail_reply_start", "contact_id": "bob-id"})
            self.assertEqual(agent.pending_mail_reply["sender"], "bob@example.com")
            self.assertEqual(agent.queued_mail_replies[0]["state"], "DRAFT_READY")
            agent.handle({"type": "mail_choice", "card_id": selected["result_card"]["id"],
                          "choice": "skip"})
            self.assertEqual(agent.pending_mail_reply["card_id"], first_card)
            self.assertEqual(agent.pending_mail_reply["state"], "DRAFT_READY")
            self.assertFalse((workspace / "outbox").exists())

    def test_agent_reports_live_mail_ability_without_spending_model_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agent = LocalAgent(workspace)
            question = "你能监测 QQ 邮箱吗？"
            offline = agent.handle({"type": "chat_message", "text": question})
            self.assertIn("没有已验证的连接", offline["chat_reply"])
            self.assertEqual(offline["capability_status"]["qqmail"]["monitor_status"], "NOT_CONNECTED")
            self.assertEqual(offline["model"]["usage"]["total_tokens"], 0)

            health = workspace / ".qqmail_bridge_health.json"
            health.write_text(json.dumps({"status": "CONNECTED",
                                          "checked_at": datetime.now(timezone.utc).isoformat()}))
            preview = agent.handle({"type": "chat_preview", "text": question, "request_id": "mail:1"})
            connected = agent.handle({"type": "chat_message", "text": question})
            self.assertEqual(preview["status"], "LOCAL")
            self.assertIn("正在监听", connected["chat_reply"])
            self.assertIn("你确认", connected["chat_reply"])
            self.assertEqual(connected["capability_status"]["qqmail"]["monitor_status"], "CONNECTED")

            os.utime(health, (0, 0))
            stale = agent.handle({"type": "chat_message", "text": question})
            self.assertIn("监听目前中断", stale["chat_reply"])
            self.assertEqual(stale["capability_status"]["qqmail"]["monitor_status"], "INTERRUPTED")

    def test_local_model_receives_runtime_capability_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            captured = {}

            def fake_generate(prompt, **kwargs):
                captured["prompt"] = prompt
                captured["messages"] = kwargs.get("local_messages")
                return {"ok": True, "text": "你好", "provider": "fixture", "model": "fixture"}

            agent.muse_models.generate = fake_generate
            result = agent.handle({"type": "chat_message", "text": "你好"})
            self.assertEqual(result["chat_reply"], "你好")
            self.assertIn("QQ邮箱尚未连接", captured["prompt"])
            if captured["messages"] is not None:
                self.assertIn("QQ邮箱尚未连接", captured["messages"][0]["content"])

    def test_local_chat_preview_needs_no_cloud_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            result = agent.handle({"type": "chat_preview", "request_id": "chat:local",
                                   "text": "你好"})
            self.assertEqual(result["status"], "LOCAL")
            self.assertEqual(result["request_id"], "chat:local")
            self.assertNotIn("request_body", result)

    def test_high_only_chat_works_without_local_router_and_excludes_memory(self):
        class HighFixture:
            def __init__(self):
                self.prompts = []

            def get_settings(self):
                return {"mode": "high", "active_high": "high-test",
                        "profiles": {"high-test": {"endpoint": "https://models.example.test/v1/responses"}}}

            def _slot(self, settings, purpose):
                self.purpose = purpose
                return "high"

            def preview_cloud_request(self, prompt, *, purpose, max_tokens):
                self.previews = [prompt]
                return {"ok": True, "status": "PREVIEW", "destination": {"model": "test"},
                        "request_body": {"input": prompt}, "sha256": "a" * 64}

            def generate(self, prompt, *, purpose, max_tokens, cloud_preview_sha256):
                self.preview_digest = cloud_preview_sha256
                self.prompts.append(prompt)
                return {"ok": True, "text": "已收到当前问题", "provider": "high-fixture",
                        "model": "test", "route": "high", "usage": {"total_tokens": 3}}

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            MemoryStore(workspace).remember("fact", "local", "PRIVATE_MEMORY_SENTINEL")
            agent = LocalAgent(workspace)
            fixture = HighFixture()
            agent.muse_models = fixture
            blocked = agent.handle({"type": "chat_message", "text": "现在怎么走？"})
            self.assertEqual(blocked["status"], "PREVIEW_REQUIRED")
            self.assertEqual(fixture.prompts, [])
            preview = agent.handle({"type": "chat_preview", "request_id": "chat:1",
                                    "text": "现在怎么走？"})
            self.assertEqual(preview["status"], "PREVIEW")
            self.assertEqual(preview["request_id"], "chat:1")
            result = agent.handle({"type": "chat_message", "text": "现在怎么走？",
                                   "cloud_preview_sha256": preview["sha256"]})
            self.assertEqual(result["status"], "REPLIED")
            self.assertEqual(result["cloud_context"], "current_message_only")
            self.assertEqual(result["memory_scopes_used"], [])
            self.assertEqual(len(fixture.prompts), 1)
            self.assertIn("现在怎么走？", fixture.prompts[0])
            self.assertNotIn("PRIVATE_MEMORY_SENTINEL", fixture.prompts[0])
            self.assertEqual(fixture.prompts, fixture.previews)
            self.assertEqual(fixture.preview_digest, preview["sha256"])

    def test_builtin_plugin_requires_direct_approval_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agent = LocalAgent(workspace)
            self.assertEqual(agent.handle({"type": "plugin_list"})["plugins"][0]["status"], "DISABLED")
            self.assertEqual(agent.handle({"type": "plugin_run", "plugin_id": "builtin.text_stats",
                                           "input": {"text": "你好\n世界"}})["status"], "BLOCKED")
            self.assertEqual(agent.handle({"type": "plugin_decide", "plugin_id": "builtin.text_stats",
                                           "decision": "enable"})["status"], "NEEDS_APPROVAL")
            approved = agent.handle({"type": "plugin_decide", "plugin_id": "builtin.text_stats",
                                     "decision": "enable", "approved": True})
            self.assertEqual(approved["status"], "ENABLED")
            restarted = LocalAgent(workspace)
            result = restarted.handle({"type": "plugin_run", "plugin_id": "builtin.text_stats",
                                       "input": {"text": "你好\n世界"}})
            self.assertEqual(result["output"], {"characters": 5, "lines": 2})
            self.assertEqual(restarted.handle({"type": "plugin_decide", "plugin_id": "builtin.text_stats",
                                               "decision": "disable"})["status"], "DISABLED")
            self.assertEqual(restarted.handle({"type": "plugin_run", "plugin_id": "builtin.text_stats",
                                               "input": {"text": "你好"}})["status"], "BLOCKED")

    def test_chat_recalls_verified_goal_summary_without_raw_mail(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            memory = MemoryStore(workspace)
            memory.remember("goal_result", "goal-7", "午餐安排 已完成并验证", scope="personal",
                            account_scope="qqmail:account-7", record_type="fact", confirmed=True)
            memory.remember("mail_raw", "qqmail", "午餐安排 私密原文", scope="personal",
                            account_scope="qqmail:account-7")
            agent = LocalAgent(workspace, LocalModelRouter("http://127.0.0.1:8080/v1/chat/completions"))
            captured = {}

            def fake_generate(prompt, **_kwargs):
                captured["prompt"] = prompt
                return {"ok": True, "text": "已找到结果", "provider": "fixture", "model": "fixture"}

            agent.muse_models.generate = fake_generate
            default = agent.handle({"type": "chat_message", "text": "午餐安排怎么样"})
            self.assertEqual(default["goal_memory_matches"], [])
            response = agent.handle({"type": "chat_message", "text": "午餐安排怎么样",
                                     "memory_scopes": ["qqmail:account-7"]})
            self.assertEqual(response["chat_reply"], "已找到结果")
            self.assertEqual(response["goal_memory_matches"][0]["account_scope"], "qqmail:account-7")
            self.assertIn("已完成并验证", captured["prompt"])
            self.assertNotIn("私密原文", captured["prompt"])

    def test_memory_management_rejects_explicit_foreign_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            memory = MemoryStore(workspace)
            memory.remember("fact", "fixture", "foreign private record", "foreign:1",
                            account_scope="other-fixture")
            agent = LocalAgent(workspace)
            for event in ({"type": "memory_list", "account_scope": "other-fixture"},
                          {"type": "memory_settings_set", "account_scope": "other-fixture", "enabled": False},
                          {"type": "memory_list", "scope": "school"}):
                with self.subTest(event=event):
                    result = agent.handle(event)
                    self.assertEqual(result["status"], "REJECTED")
                    self.assertEqual(result["error"], "memory_scope_not_authorized")
            self.assertEqual(agent.handle({"type": "memory_list"})["records"], [])
            self.assertTrue(memory.recording_enabled(account_scope="other-fixture"))

    def test_system_status_returns_bounded_device_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = LocalAgent(Path(tmp)).handle({"type": "system_status"})
            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "READY")
            self.assertIn(result["system"]["platform"], {"Darwin", "Linux", "Windows"})
            self.assertTrue(result["system"]["machine"])
            self.assertEqual(result["system"]["workspace"], str(Path(tmp).resolve()))
            self.assertIn("workspace.write_readback", result["system"]["capabilities"])
            self.assertEqual(result["system"]["message_queue"]["queue_depth"], 0)

    def test_status_surfaces_expose_local_only_access_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            system = agent.handle({"type": "system_status"})["system"]
            message = agent.handle({"type": "message_status"})
            for payload in (system, message):
                profile = payload["access_profile"]
                self.assertEqual(profile["id"], "local_only")
                self.assertEqual(profile["sensitive_actions"], "user_confirmation_required")
                self.assertIn("audit.message_records", profile["grants"])
            self.assertEqual(message["access_profile"]["external_connectors"]["wechat"], "BLOCKED_UNVERIFIED")
            self.assertEqual(message["sources"]["qqmail"]["status"], "LOCAL_IMAP")

    def test_task_card_route_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = LocalAgent(Path(tmp)).handle({"type": "user_input", "text": "复习英语单词"})
            self.assertTrue(result["ok"])
            self.assertEqual(result["route"], "task_card")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_write_requires_confirmation_and_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            proposed = agent.handle({"type": "user_input", "text": "写入今天完成了测试"})
            self.assertTrue(proposed["task_card"]["requires_confirmation"])
            self.assertEqual(list(Path(tmp).iterdir()), [])
            result = agent.handle({"type": "confirm", "approved": True})
            self.assertTrue(result["ok"])
            created = Path(result["created"])
            self.assertEqual(created.read_text(encoding="utf-8"), "写入今天完成了测试\n")

    def test_rejection_and_invalid_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            agent.handle({"type": "user_input", "text": "保存一条记录"})
            rejected = agent.handle({"type": "confirm", "approved": False})
            self.assertEqual(rejected["task_card"]["status"], "rejected")
            self.assertEqual(list(Path(tmp).iterdir()), [])
            self.assertEqual(agent.handle({"type": "wat", "x": 1})["error"], "unsupported_event")

    def test_stream_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = io.StringIO(json.dumps({"type": "health"}) + "\nnot-json\n")
            sink = io.StringIO()
            run_stream(LocalAgent(Path(tmp)), source, sink)
            lines = [json.loads(line) for line in sink.getvalue().splitlines()]
            self.assertTrue(lines[0]["ok"])
            self.assertEqual(lines[1]["error"], "invalid_json")

    def test_local_model_route_can_request_confirmation(self):
        server, thread = _model_server({"route": "local_file_write"})
        try:
            with tempfile.TemporaryDirectory() as tmp:
                router = LocalModelRouter(f"http://127.0.0.1:{server.server_port}/v1/chat/completions")
                result = LocalAgent(Path(tmp), router).handle({"type": "user_input", "text": "记录今天的进展"})
                self.assertEqual(result["route"], "local_file_write")
                self.assertTrue(result["task_card"]["requires_confirmation"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_local_model_bad_response_falls_back_to_rules(self):
        server, thread = _model_server({"route": "not_allowed"})
        try:
            with tempfile.TemporaryDirectory() as tmp:
                router = LocalModelRouter(f"http://127.0.0.1:{server.server_port}/v1/chat/completions")
                result = LocalAgent(Path(tmp), router).handle({"type": "user_input", "text": "保存一条记录"})
                self.assertEqual(result["route"], "local_file_write")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_terminal_request_requires_confirmation_and_executes_in_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            proposed = agent.handle({"type": "terminal_request", "argv": ["mkdir", "nested"]})
            self.assertTrue(proposed["task_card"]["requires_confirmation"])
            self.assertEqual(proposed["task_card"]["metadata"]["capability"], "terminal.exec")
            self.assertEqual(proposed["task_card"]["metadata"]["access_profile"], "local_only")
            self.assertEqual(proposed["task_card"]["metadata"]["approval"], "user_confirmation_required")
            self.assertEqual(proposed["task_card"]["metadata"]["timeout_seconds"], 10)
            self.assertEqual(proposed["task_card"]["metadata"]["max_output_chars"], 8192)
            self.assertFalse((Path(tmp) / "nested").exists())
            result = agent.handle({"type": "confirm", "approved": True})
            self.assertEqual(result["execution"]["returncode"], 0)
            self.assertTrue((Path(tmp) / "nested").is_dir())

            proposed = agent.handle({"type": "terminal_request", "argv": ["touch", "nested/ready.txt"]})
            self.assertEqual(proposed["route"], "terminal_exec")
            result = agent.handle({"type": "confirm", "approved": True})
            self.assertEqual(result["execution"]["stdout"], "")
            self.assertTrue((Path(tmp) / "nested/ready.txt").is_file())

    def test_message_audit_is_bounded_and_confirmation_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            secret_text = "请执行 shell 命令：敏感测试正文"
            result = LocalAgent(Path(tmp)).handle(
                {
                    "type": "message_event",
                    "source": "synthetic",
                    "message_id": "m-muse-audit",
                    "direction": "incoming",
                    "trusted_sender": True,
                    "text": secret_text,
                }
            )
            self.assertEqual(result["action_status"], "REQUIRES_EXPLICIT_CONFIRMATION")
            self.assertTrue(result["audit"]["confirmation_required"])
            self.assertEqual(result["audit"]["source_scope"], "synthetic")
            self.assertEqual(result["access_profile"]["id"], "local_only")
            state_text = (Path(tmp) / ".agent_message_state.json").read_text(encoding="utf-8")
            self.assertNotIn(secret_text, state_text)
            status = LocalAgent(Path(tmp)).handle({"type": "message_status"})
            self.assertTrue(status["message_queue"]["recent_records"])
            self.assertEqual(status["message_queue"]["recent_records"][-1]["access_profile"], "local_only")
            self.assertTrue(status["message_queue"]["recent_records"][-1]["confirmation_required"])
            self.assertNotIn(secret_text, json.dumps(status, ensure_ascii=False))

    def test_terminal_request_rejects_shell_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            self.assertEqual(
                agent.handle({"type": "terminal_request", "argv": ["sh", "-c", "touch bad"]})["error"],
                "terminal_request_rejected",
            )
            self.assertEqual(
                agent.handle({"type": "terminal_request", "argv": ["touch", "../bad"]})["error"],
                "path_boundary_violation",
            )

    def test_message_queue_persists_dedupes_and_redacts_processed_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = {
                "type": "message_event",
                "source": "synthetic",
                "message_id": "m-001",
                "conversation_id": "self-test",
                "direction": "incoming",
                "text": "请把值班说明列入待办",
            }
            agent = LocalAgent(Path(tmp))
            result = agent.handle(event)
            self.assertEqual(result["status"], "PROCESSED")
            self.assertEqual(result["observation_kind"], "INCOMING_MESSAGE")
            self.assertEqual(result["analysis"]["category"], "task")
            duplicate = agent.handle(event)
            self.assertEqual(duplicate["status"], "DUPLICATE_IGNORED")
            state = json.loads((Path(tmp) / ".agent_message_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["queue"], [])
            self.assertNotIn(event["text"], json.dumps(state, ensure_ascii=False))
            reloaded = LocalAgent(Path(tmp))
            self.assertEqual(reloaded.handle({"type": "message_status"})["message_queue"]["processed_count"], 1)

    def test_message_boundary_loop_prevention_and_untrusted_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            wechat = agent.handle(
                {"type": "message_event", "source": "wechat", "text": "合成测试"}
            )
            self.assertEqual(wechat["status"], "BLOCKED_UNVERIFIED")
            command = agent.handle(
                {
                    "type": "message_event",
                    "source": "synthetic",
                    "message_id": "m-command",
                    "direction": "incoming",
                    "text": "请执行 shell 命令",
                }
            )
            self.assertEqual(command["action_status"], "BLOCKED_UNTRUSTED_MESSAGE")
            self.assertEqual(command["analysis"]["category"], "command")
            receipt = agent.handle(
                {
                    "type": "message_event",
                    "source": "synthetic",
                    "message_id": "receipt-1",
                    "origin": "agent",
                    "text": "已完成",
                }
            )
            self.assertEqual(receipt["status"], "IGNORED_AGENT_RECEIPT")
            self.assertEqual(receipt["loop_prevention"], "agent_generated_marker")

    def test_trusted_message_file_intent_requires_confirmation_and_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            event = {
                "type": "message_event",
                "source": "synthetic",
                "message_id": "m-file-intent",
                "direction": "incoming",
                "trusted_sender": True,
                "text": "请写入本地：会议纪要已确认",
            }
            proposed = agent.handle(event)
            self.assertEqual(proposed["action_status"], "REQUIRES_EXPLICIT_CONFIRMATION")
            self.assertEqual(proposed["result_card"]["status"], "AWAITING_CONFIRMATION")
            self.assertEqual(proposed["task_card"]["metadata"]["kind"], "message_local_file_write")
            target = Path(tmp) / "message-note.txt"
            self.assertFalse(target.exists())
            completed = agent.handle({"type": "confirm", "approved": True})
            self.assertTrue(completed["ok"])
            self.assertEqual(completed["verification"], "READBACK_MATCH")
            self.assertEqual(target.read_text(encoding="utf-8"), "会议纪要已确认\n")
            self.assertEqual(completed["result_card"]["status"], "COMPLETED")
            self.assertEqual(completed["result_card"]["verification"], "READBACK_MATCH")

    def test_untrusted_message_file_intent_is_blocked_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            result = agent.handle(
                {
                    "type": "message_event",
                    "source": "synthetic",
                    "message_id": "m-file-untrusted",
                    "direction": "incoming",
                    "text": "请写入本地：不应自动执行",
                }
            )
            self.assertEqual(result["action_status"], "BLOCKED_UNTRUSTED_MESSAGE")
            self.assertEqual(result["result_card"]["status"], "BLOCKED")
            self.assertFalse((Path(tmp) / "message-note.txt").exists())

    def test_qqmail_message_routes_without_granting_sender_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = LocalAgent(Path(tmp)).handle(
                {
                    "type": "message_event",
                    "source": "qqmail",
                    "message_id": "qqmail:7",
                    "direction": "incoming",
                    "text": "主题：手机测试\n请把这封邮件列入待办",
                }
            )
            self.assertEqual(result["status"], "PROCESSED")
            self.assertEqual(result["source"], "qqmail")
            self.assertEqual(result["action_status"], "MAIL_REPLY_CHOICE_REQUIRED")
            self.assertEqual(result["result_card"]["status"], "AWAITING_USER_CHOICE")

    def test_qqmail_result_card_choices_queue_suggested_and_custom_replies(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            event = {
                "type": "message_event",
                "source": "qqmail",
                "message_id": "qqmail:reply-flow",
                "sender_id": "friend@example.com",
                "direction": "incoming",
                "text": "主题：周末\n周六一起吃饭吗？",
                "metadata": {
                    "sender": "friend@example.com",
                    "subject": "周末",
                    "message_id_header": "<reply-flow@example.com>",
                },
            }
            agent = LocalAgent(workspace)
            initial = agent.handle(event)
            card = initial["result_card"]
            self.assertEqual(card["status"], "AWAITING_USER_CHOICE")
            self.assertEqual([item["id"] for item in card["options"]], ["reply_suggested", "reply_custom", "skip"])

            awaiting = agent.handle({"type": "mail_choice", "card_id": card["id"], "choice": "reply_custom"})
            self.assertEqual(awaiting["status"], "DRAFT_READY")
            self.assertFalse((workspace / "outbox").exists())
            rejected = agent.handle({"type": "mail_reply_content", "card_id": card["id"], "body": "好的，周六见！"})
            self.assertEqual(rejected["error"], "explicit_send_confirmation_required")
            queued = agent.handle({"type": "mail_reply_content", "card_id": card["id"], "body": "好的，周六见！", "confirmed": True})
            self.assertEqual(queued["status"], "REPLY_QUEUED")
            request_files = list((workspace / "outbox" / "qqmail-replies").glob("*.json"))
            self.assertEqual(len(request_files), 1)
            request = json.loads(request_files[0].read_text(encoding="utf-8"))
            self.assertEqual(request["to"], "friend@example.com")
            self.assertEqual(request["body"], "好的，周六见！")

            sent = agent.handle({"type": "qqmail_reply_result", "request_id": queued["request_id"], "status": "SENT"})
            self.assertEqual(sent["status"], "REPLY_SENT")
            self.assertEqual(sent["result_card"]["verification"], "SMTP_ACCEPTED")

            generic = dict(event, message_id="qqmail:generic", text="主题：资料\n请确认收到资料。")
            generic["metadata"] = dict(event["metadata"], subject="资料")
            generic_card = agent.handle(generic)["result_card"]
            suggested = agent.handle({"type": "mail_choice", "card_id": generic_card["id"], "choice": "reply_suggested"})
            self.assertEqual(suggested["status"], "AWAITING_USER_GUIDANCE")
            self.assertIn("希望回复什么", suggested["result_card"]["question"])
            self.assertEqual(len(list((workspace / "outbox" / "qqmail-replies").glob("*.json"))), 1)

    def test_mail_invitation_and_followup_ask_user_before_sending(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agent = LocalAgent(workspace)
            inbox = workspace / "inbox" / "events.jsonl"
            inbox.parent.mkdir(parents=True)
            first_event = {
                "type": "message_event", "source": "qqmail", "message_id": "qqmail:meal-1",
                "sender_id": "friend@example.com", "direction": "incoming",
                "text": "主题：晚饭\n今天晚上出来吃饭吗？",
                "metadata": {"sender": "friend@example.com", "subject": "晚饭"},
            }
            inbox.write_text(json.dumps(first_event, ensure_ascii=False) + "\n", encoding="utf-8")
            first = agent.handle(first_event)
            first_id = first["result_card"]["id"]
            proposed = agent.handle({"type": "mail_choice", "card_id": first_id, "choice": "reply_suggested"})
            self.assertEqual(proposed["status"], "AWAITING_USER_GUIDANCE")
            self.assertFalse((workspace / "outbox").exists())

            second_event = {
                "type": "message_event", "source": "qqmail", "message_id": "qqmail:meal-2",
                "sender_id": "friend@example.com", "direction": "incoming",
                "text": "主题：晚饭\n几点出来？",
                "metadata": {"sender": "friend@example.com", "subject": "晚饭"},
            }
            with inbox.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(second_event, ensure_ascii=False) + "\n")
            second = agent.handle(second_event)
            self.assertEqual(second["result_card"]["status"], "AWAITING_USER_CHOICE")
            self.assertEqual(len(agent.queued_mail_replies), 0)
            first_record = next(item for item in agent.result_cards.state["cards"] if item["id"] == first_id)
            self.assertEqual(first_record["status"], "SUPERSEDED_BY_FOLLOWUP")
            self.assertEqual(agent.pending_mail_reply["source_message_id"], "qqmail:meal-2")
            self.assertIn("吃饭", agent.pending_mail_reply["context"][0] if agent.pending_mail_reply["context"] else "")
            next_choice = agent.handle({"type": "mail_choice", "card_id": second["result_card"]["id"], "choice": "reply_suggested"})
            self.assertEqual(next_choice["status"], "AWAITING_USER_GUIDANCE")
            self.assertIn("时间", next_choice["result_card"]["question"])
            unrelated = agent.handle({
                "type": "message_event", "source": "qqmail", "message_id": "qqmail:other",
                "sender_id": "other@example.com", "direction": "incoming",
                "text": "主题：报告\n请看一下报告。",
                "metadata": {"sender": "other@example.com", "subject": "报告"},
            })
            self.assertEqual(unrelated["result_card"]["status"], "QUEUED_FOR_USER")
            draft = agent.handle({"type": "mail_guidance", "card_id": second["result_card"]["id"], "text": "晚上七点"})
            self.assertEqual(draft["status"], "DRAFT_READY")
            self.assertIn("七点", draft["result_card"]["draft"])
            self.assertFalse((workspace / "outbox").exists())

    def test_qqmail_result_card_skip_has_no_outbox_side_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agent = LocalAgent(workspace)
            initial = agent.handle({
                "type": "message_event",
                "source": "qqmail",
                "message_id": "qqmail:skip-flow",
                "sender_id": "friend@example.com",
                "direction": "incoming",
                "text": "主题：通知\n这是通知。",
                "metadata": {"sender": "friend@example.com", "subject": "通知"},
            })
            skipped = agent.handle({"type": "mail_choice", "card_id": initial["result_card"]["id"], "choice": "skip"})
            self.assertEqual(skipped["status"], "SKIPPED")
            self.assertFalse((workspace / "outbox").exists())

    def test_rejected_message_file_intent_updates_result_card_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            agent.handle(
                {
                    "type": "message_event",
                    "source": "synthetic",
                    "message_id": "m-file-reject",
                    "direction": "incoming",
                    "trusted_sender": True,
                    "text": "请保存到本地：用户拒绝的内容",
                }
            )
            rejected = agent.handle({"type": "confirm", "approved": False})
            self.assertEqual(rejected["task_card"]["status"], "blocked")
            self.assertEqual(rejected["result_card"]["status"], "BLOCKED")
            self.assertEqual(rejected["result_card"]["verification"], "USER_REJECTED_NO_ACTION")
            self.assertFalse((Path(tmp) / "message-note.txt").exists())

    def test_high_tier_call_is_explicit_and_recorded(self):
        server, thread = _high_tier_server()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                client = HighTierClient(f"http://127.0.0.1:{server.server_port}/v1/chat/completions")
                result = LocalAgent(Path(tmp), high_tier_client=client).handle(
                    {
                        "type": "message_event",
                        "source": "synthetic",
                        "message_id": "m-high",
                        "text": "请给出值班摘要",
                        "request_high_tier": True,
                    }
                )
                self.assertEqual(result["high_tier"]["status"], "USED")
                self.assertEqual(result["high_tier"]["model"], "test-high-tier")
                self.assertEqual(_HighTierHandler.calls, 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_codex_app_server_channel_uses_read_only_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "fake-codex"
            fake.write_text(
                """#!/usr/bin/env python3
import json, sys
thread_id = 'fake-thread'
for line in sys.stdin:
    request = json.loads(line)
    method = request.get('method')
    request_id = request.get('id')
    if method == 'initialize':
        response = {'jsonrpc': '2.0', 'id': request_id, 'result': {'platformOs': 'macos'}}
    elif method == 'thread/start':
        response = {'jsonrpc': '2.0', 'id': request_id, 'result': {'thread': {'id': thread_id}}}
    elif method == 'turn/start':
        response = {'jsonrpc': '2.0', 'id': request_id, 'result': {'turn': {'status': 'inProgress'}}}
        print(json.dumps(response), flush=True)
        print(json.dumps({'jsonrpc': '2.0', 'method': 'item/agentMessage/delta', 'params': {'delta': '{\\"summary\\":\\"fake app-server PASS\\"}'}}), flush=True)
        print(json.dumps({'jsonrpc': '2.0', 'method': 'turn/completed', 'params': {'threadId': thread_id, 'turn': {'status': 'completed'}}}), flush=True)
        continue
    else:
        continue
    print(json.dumps(response), flush=True)
""",
                encoding="utf-8",
            )
            os.chmod(fake, 0o755)
            client = HighTierClient(codex_bin=str(fake), workspace=Path(tmp))
            result = client.summarize("请给出测试摘要")
            self.assertEqual(result["status"], "USED")
            self.assertEqual(result["channel"], "codex_app_server")
            self.assertEqual(result["summary"], "fake app-server PASS")


if __name__ == "__main__":
    unittest.main()
