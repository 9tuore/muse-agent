#!/usr/bin/env python3
"""Isolated official Octos main-profile / local Qwen stdio probe."""

import json
import os
import queue
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BINARY = Path("/Users/mima0000/Documents/ChatGPT/Agent APP黑客松/runtime/octos-lean-target/debug/octos")
QWEN_BASE_URL = os.environ.get("G01_QWEN_BASE_URL", "http://127.0.0.1:8080/v1")
EVIDENCE_NAME = os.environ.get("G01_EVIDENCE_NAME", "muse-g01-official-main-qwen-20260928.json")


def main():
    if not BINARY.is_file():
        raise SystemExit("official_binary_missing")
    with tempfile.TemporaryDirectory(prefix="g01-octos-main-", dir="/tmp") as temp:
        run = Path(temp)
        state, workspace = run / "state", run / "workspace"
        state.mkdir()
        workspace.mkdir()
        (state / "config.json").write_text("{}\n", encoding="utf-8")
        command = [str(BINARY), "serve", "--stdio", "--solo", "--no-network",
                   "--data-dir", str(state), "--config", str(state / "config.json"),
                   "--cwd", str(workspace)]
        environment = {"PATH": "/usr/bin:/bin", "HOME": temp, "OCTOS_HOME": str(state),
                       "OCTOS_NO_NETWORK": "1", "RUST_LOG": "warn"}
        frames = queue.Queue()
        stderr = run / "octos.stderr"
        with stderr.open("w", encoding="utf-8") as errors:
            process = subprocess.Popen(command, cwd=workspace, env=environment,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=errors, text=True, bufsize=1)
            def collect():
                for line in process.stdout:
                    try:
                        frames.put(json.loads(line))
                    except ValueError:
                        frames.put({"invalid_frame": True})
            threading.Thread(target=collect, daemon=True).start()
            notifications = []

            def request(method, params, timeout=30):
                request_id = uuid.uuid4().hex
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": request_id,
                                                "method": method, "params": params}) + "\n")
                process.stdin.flush()
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    try:
                        frame = frames.get(timeout=1)
                    except queue.Empty:
                        if process.poll() is not None:
                            return {"error": {"message": "server_exited", "exit": process.returncode}}
                        continue
                    if frame.get("id") == request_id:
                        return frame
                    notifications.append(frame)
                return {"error": {"message": "request_timeout"}}

            started = time.time()
            session_id = "main:api:g01-" + uuid.uuid4().hex[:12]
            turn_id = str(uuid.uuid4())
            try:
                replies = {
                    "profile": request("profile/local/create", {"name": "G01 isolated local Qwen", "requested_id": "main"}),
                    "upsert": request("profile/llm/upsert", {"profile_id": "main", "selection": {
                        "family_id": "local", "model_id": "qwen3-0.6b",
                        "route": {"base_url": QWEN_BASE_URL, "api_type": "openai"}},
                        "set_primary": True}),
                    "session": request("session/open", {"session_id": session_id,
                                                        "profile_id": "main"}),
                }
                if all("result" in replies[key] for key in ("profile", "upsert", "session")):
                    replies["turn"] = request("turn/start", {"session_id": session_id,
                        "turn_id": turn_id, "input": [{"kind": "text",
                            "text": "用一句中文回答：一加一等于几？只回答数字。"}]}, timeout=30)
                    deadline = time.monotonic() + 100
                    while "result" in replies["turn"] and time.monotonic() < deadline:
                        try:
                            frame = frames.get(timeout=1)
                        except queue.Empty:
                            if process.poll() is not None:
                                break
                            continue
                        notifications.append(frame)
                        if frame.get("method") in {"turn/completed", "turn/error"}:
                            break
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            report = {"started_at_epoch": started, "duration_seconds": round(time.time() - started, 2),
                      "binary": str(BINARY), "official_source_commit": "deb433e9a452c03d8fe7f4f6a26b42785c47ced7",
                      "isolated": True, "qwen_base_url": QWEN_BASE_URL,
                      "session_id": session_id, "turn_id": turn_id,
                      "replies": replies, "notifications": notifications,
                      "process_exit": process.returncode,
                      "stderr_tail": stderr.read_text(encoding="utf-8")[-4000:]}
            terminal = [frame.get("method") for frame in notifications
                        if frame.get("method") in {"turn/completed", "turn/error"}]
            report["outcome"] = terminal[-1] if terminal else "NO_TERMINAL_IN_OBSERVATION_WINDOW"
            output = ROOT / "evidence" / EVIDENCE_NAME
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"output": str(output), "profile_ok": "result" in replies["profile"],
                              "upsert_ok": "result" in replies["upsert"],
                              "session_ok": "result" in replies["session"],
                              "turn_accepted": replies.get("turn", {}).get("result", {}).get("accepted") is True,
                              "outcome": report["outcome"]},
                             ensure_ascii=False))


if __name__ == "__main__":
    main()
