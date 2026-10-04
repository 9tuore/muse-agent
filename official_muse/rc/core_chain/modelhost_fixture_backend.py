#!/usr/bin/env python3
"""Loopback-only OpenAI chat-completions fixture for a real ModelHost test.

Provider wire envelope follows the locked official `complete/wire.rs` parser.
No inference, key, prompt content, external request, or real account is used.
"""

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading


SCENARIOS = ("bad_then_good", "bad_twice", "refused", "truncated")
GOOD = '{"reply":"本地合成协议响应；未调用真实模型。"}'
BAD = "This is deliberately not JSON."


class ScenarioBackend:
    def __init__(self, port: int = 8879):
        self.port = port
        self.scenario = None
        self.requests = []
        self.lock = threading.Lock()
        backend = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                size = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(size) if 0 < size <= 1_000_000 else b""
                try:
                    body = json.loads(raw)
                except (ValueError, UnicodeDecodeError):
                    body = None
                with backend.lock:
                    scenario = backend.scenario
                    attempt = len(backend.requests) + 1
                    turns = body.get("messages", []) if isinstance(body, dict) else []
                    last = turns[-1].get("content", "") if turns and isinstance(turns[-1], dict) else ""
                    backend.requests.append({
                        "attempt": attempt,
                        "path": self.path,
                        "body_sha256": hashlib.sha256(raw).hexdigest(),
                        "body_bytes": len(raw),
                        "model": body.get("model") if isinstance(body, dict) else None,
                        "stream": body.get("stream") if isinstance(body, dict) else None,
                        "roles": [turn.get("role") for turn in turns if isinstance(turn, dict)],
                        "repair_hint": isinstance(last, str) and "Your previous answer was refused:" in last,
                        "token_cap_present": isinstance(body, dict) and any(
                            key in body for key in ("max_tokens", "max_completion_tokens", "max_output_tokens")),
                    })
                if self.path != "/v1/chat/completions" or not isinstance(body, dict) or not turns or attempt > 2:
                    self._json(400, {"error": {"message": "Fixture boundary rejected request"}})
                    return
                if scenario == "bad_then_good":
                    content, finish, refusal = (BAD if attempt == 1 else GOOD), "stop", None
                elif scenario == "bad_twice":
                    content, finish, refusal = BAD, "stop", None
                elif scenario == "refused":
                    content, finish, refusal = None, "stop", "synthetic refusal"
                elif scenario == "truncated":
                    content, finish, refusal = '{"reply":', "length", None
                else:
                    self._json(400, {"error": {"message": "Fixture scenario not configured"}})
                    return
                message = {"role": "assistant", "content": content}
                if refusal is not None:
                    message["refusal"] = refusal
                self._json(200, {
                    "id": f"muse-fixture-{attempt}", "object": "chat.completion",
                    "choices": [{"index": 0, "message": message, "finish_reason": finish}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                })

            def _json(self, status, value):
                payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, _format, *_args):
                pass  # Never log prompt bodies or headers.

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def configure(self, scenario: str):
        if scenario not in SCENARIOS:
            raise ValueError(scenario)
        with self.lock:
            self.scenario = scenario
            self.requests = []

    def snapshot(self):
        with self.lock:
            return list(self.requests)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        if self.thread:
            self.thread.join(timeout=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--port", type=int, default=8879)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    backend = ScenarioBackend(args.port)
    backend.configure(args.scenario)
    backend.start()
    print(json.dumps({"ready": True, "port": args.port, "scenario": args.scenario}), flush=True)
    try:
        threading.Event().wait()  # Ctrl-C only; standalone manual mode.
    except KeyboardInterrupt:
        pass
    finally:
        (args.out / "requests.json").write_text(json.dumps(backend.snapshot(), indent=2) + "\n")
        backend.stop()


if __name__ == "__main__":
    main()
