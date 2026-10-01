#!/usr/bin/env python3
"""Reproduce two different local chat turns without touching user data."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from agent_app import LocalAgent, LocalModelRouter
from memory_store import MemoryStore


with tempfile.TemporaryDirectory(prefix="muse-chat-repeat-") as directory:
    agent = LocalAgent(Path(directory), LocalModelRouter(
        "http://127.0.0.1:8080/v1/chat/completions"))
    turns = []
    for question in ("请只回答颜色：苹果通常是什么颜色？", "请只回答算式结果：二加三等于几？"):
        result = agent.handle({"type": "chat_message", "text": question})
        turns.append({"question": question, "status": result.get("status"),
                      "reply": result.get("chat_reply"), "model": result.get("model")})
    print(json.dumps(turns, ensure_ascii=False, indent=2))

with tempfile.TemporaryDirectory(prefix="muse-chat-fallback-") as directory:
    workspace = Path(directory)
    memory = MemoryStore(workspace)
    for question in ("你好", "你是谁", "现在几点"):
        memory.remember("chat_user", "local_user", question)
        memory.remember("chat_assistant", "local_agent",
                        "模型暂时无法回答。你可以重试；已有记忆仍保存在本机。")
    agent = LocalAgent(workspace, LocalModelRouter(
        "http://127.0.0.1:8080/v1/chat/completions"))
    result = agent.handle({"type": "chat_message", "text": "请只回答算式结果：二加三等于几？"})
    print(json.dumps({"seeded_fallback_status": result.get("status"),
                      "seeded_fallback_reply": result.get("chat_reply"),
                      "seeded_fallback_error": result.get("model", {}).get("error")},
                     ensure_ascii=False))
