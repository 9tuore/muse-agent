import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_app import LocalAgent, LocalModelRouter, MODEL_FAILURE_REPLY
from memory_store import MemoryStore


class MemoryStoreTests(unittest.TestCase):
    def test_chat_is_persisted_and_searchable_without_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            # The chat path now always attempts the model; stub it as unavailable
            # so the test verifies persistence of the user message alone.
            agent.muse_models.generate = lambda *args, **kwargs: {
                "ok": False, "status": "UNAVAILABLE", "error": "URLError"}
            first = agent.handle({"type": "chat_message", "text": "我周末喜欢做开源项目"})
            self.assertEqual(first["status"], "MODEL_UNAVAILABLE")
            search = agent.handle({"type": "memory_search", "query": "开源项目"})
            self.assertTrue(search["memory_matches"])
            self.assertEqual(search["memory_matches"][0]["kind"], "chat_user")
            self.assertEqual([item["kind"] for item in MemoryStore(Path(tmp)).recent(4)],
                             ["chat_user"])

    def test_chat_attempts_model_even_without_legacy_router_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            # No LocalModelRouter URL is supplied, yet the model must still be
            # called via ModelGateway (the persisted settings), not silently
            # skipped and turned into the fixed failure sentence.
            agent = LocalAgent(Path(tmp))
            seen = []
            def answer(prompt, **_kwargs):
                seen.append(prompt)
                return {"ok": True, "text": "真实回答"}
            agent.muse_models.generate = answer
            result = agent.handle({"type": "chat_message", "text": "你好"})
            self.assertEqual(result["status"], "REPLIED")
            self.assertEqual(result["chat_reply"], "真实回答")
            self.assertEqual(len(seen), 1)

    def test_local_chat_fits_model_context_and_keeps_current_question(self):
        def llama_response(request, timeout):
            url = request.full_url if hasattr(request, "full_url") else request
            if url.endswith("/props"):
                value = {"default_generation_settings": {"n_ctx": 1024}}
            else:
                content = json.loads(request.data)["content"]
                value = {"tokens": [1] * len(content)}
            return io.BytesIO(json.dumps(value).encode())

        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            context = [{"kind": "fact", "content": "旧记忆" * 100}] * 4
            history = [{"kind": "chat_user", "content": "旧对话" * 100}] * 4
            with patch("agent_app.urllib.request.urlopen", side_effect=llama_response):
                fitted = agent._bounded_local_chat_prompt(
                    "当前问题是什么？", context, [], history, "local")
                oversized = agent._bounded_local_chat_prompt(
                    "超长输入" * 150, [], [], [], "local")
            self.assertIsNotNone(fitted)
            self.assertIn("当前问题是什么？", fitted)
            self.assertLessEqual(len(fitted), 1024 - 384 - 96)
            self.assertIsNone(oversized)

    def test_old_failure_reply_is_not_sent_back_as_chat_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            memory = MemoryStore(workspace)
            memory.remember("chat_user", "local_user", "第一问")
            memory.remember("chat_assistant", "local_agent", MODEL_FAILURE_REPLY)
            agent = LocalAgent(workspace, LocalModelRouter(
                "http://127.0.0.1:8080/v1/chat/completions"))
            seen = []

            def answer(prompt, **_kwargs):
                seen.append(prompt)
                return {"ok": True, "text": "第二问的真实答案"}

            agent.muse_models.generate = answer
            result = agent.handle({"type": "chat_message", "text": "第二问"})
            self.assertEqual(result["status"], "REPLIED")
            self.assertNotIn(MODEL_FAILURE_REPLY, seen[0])
            self.assertIn("第二问", seen[0])

    def test_prefixed_failure_reply_is_filtered_and_not_relearned(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            memory = MemoryStore(workspace)
            legacy_failure = "你好，" + MODEL_FAILURE_REPLY
            memory.remember("chat_user", "local_user", "你好")
            memory.remember("chat_assistant", "local_agent", legacy_failure)
            agent = LocalAgent(workspace)
            prompts = []

            def answer(prompt, **_kwargs):
                prompts.append(prompt)
                return {"ok": True, "text": legacy_failure if len(prompts) == 1 else "你好！"}

            agent.muse_models.generate = answer
            result = agent.handle({"type": "chat_message", "text": "你好"})
            self.assertEqual(result["status"], "REPLIED")
            self.assertEqual(result["chat_reply"], "你好！")
            self.assertEqual(len(prompts), 2)
            self.assertTrue(all(MODEL_FAILURE_REPLY not in prompt for prompt in prompts))
            self.assertEqual(MemoryStore(workspace).recent(1)[0]["content"], "你好！")

    def test_second_question_retries_when_model_repeats_first_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            memory = MemoryStore(workspace)
            memory.remember("chat_user", "local_user", "你可以帮我干什么？")
            memory.remember("chat_assistant", "local_agent", "我可以帮你找图片。")
            agent = LocalAgent(workspace)
            calls = []

            def answer(_prompt, **kwargs):
                calls.append(kwargs["local_messages"])
                return {"ok": True, "text": ("我可以帮你找图片。" if len(calls) == 1
                                            else "我还可以帮你整理资料。")}

            agent.muse_models.generate = answer
            result = agent.handle({"type": "chat_message", "text": "其他的还可以干什么？"})
            self.assertEqual(result["status"], "REPLIED")
            self.assertEqual(result["chat_reply"], "我还可以帮你整理资料。")
            self.assertEqual([item["role"] for item in calls[0]],
                             ["system", "user", "assistant", "user"])
            self.assertEqual([item["role"] for item in calls[1]], ["system", "user"])

    def test_user_selected_folder_indexes_bounded_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "selected"
            root.mkdir()
            (root / "notes.md").write_text("用户偏好简洁中文回复", encoding="utf-8")
            (root / "ignored.bin").write_bytes(b"not indexed")
            result = LocalAgent(Path(tmp) / "workspace").handle(
                {"type": "memory_index_folder", "path": str(root)}
            )
            self.assertTrue(result["ok"])
            self.assertEqual(result["memory_index"]["indexed"], 1)
            self.assertEqual(MemoryStore(Path(tmp) / "workspace").count(), 1)


if __name__ == "__main__":
    unittest.main()
