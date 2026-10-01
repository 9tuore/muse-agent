#!/usr/bin/env python3
"""Drive real isolated Octos AppUI against a synthetic loopback model response."""

import argparse
import json
import queue
import subprocess
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KERNEL = Path("/Users/mima0000/Documents/ChatGPT/Agent APP黑客松/runtime/octos-lean-target/debug/octos")


class Fixture(BaseHTTPRequestHandler):
    requests = []
    forced_tool_name = "shell"
    forced_arguments = {"command": "rm -rf g01_nonexistent_scratch"}

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        tools = [tool.get("function", {}).get("name") for tool in body.get("tools", [])]
        self.requests.append({"path": self.path, "stream": body.get("stream", False),
                              "model": body.get("model"), "tools": tools,
                              "message_count": len(body.get("messages", []))})
        if len(self.requests) == 1:
            call = {"index": 0, "id": "call_g01_fixture", "type": "function",
                    "function": {"name": self.forced_tool_name,
                                 "arguments": json.dumps(self.forced_arguments)}}
            delta = {"tool_calls": [call]}
            reason = "tool_calls"
        else:
            delta = {"content": "Fixture completed."}
            reason = "stop"
        self.send_response(200)
        if body.get("stream"):
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for payload in (
                {"choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                {"choices": [{"index": 0, "delta": {}, "finish_reason": reason}]},
                {"choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 10}},
            ):
                self.wfile.write(("data: " + json.dumps(payload) + "\n\n").encode())
                self.wfile.flush()
            self.wfile.write(b"data: [DONE]\n\n")
        else:
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            message = {"role": "assistant", "content": delta.get("content"),
                       "tool_calls": [dict(call, index=None)] if reason == "tool_calls" else None}
            self.wfile.write(json.dumps({"model": body.get("model"), "choices": [
                {"message": message, "finish_reason": reason}], "usage": {
                    "prompt_tokens": 100, "completion_tokens": 10}}).encode())

    def log_message(self, *_args):
        pass


def launch(state, workspace, home, stderr):
    command = [str(KERNEL), "serve", "--stdio", "--solo", "--no-network",
               "--data-dir", str(state), "--config", str(state / "config.json"),
               "--cwd", str(workspace)]
    env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "OCTOS_HOME": str(state),
           "OCTOS_NO_NETWORK": "1", "RUST_LOG": "warn"}
    return subprocess.Popen(command, cwd=workspace, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=stderr, text=True, bufsize=1)


def stop(process):
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def run_phase(state, workspace, home, stderr, actions, observe_seconds=0, deny=False):
    frames = queue.Queue()
    process = launch(state, workspace, home, stderr)

    def collect():
        for line in process.stdout:
            try:
                frames.put(json.loads(line))
            except ValueError:
                frames.put({"invalid_json_frame": line[:200]})

    thread = threading.Thread(target=collect, daemon=True)
    thread.start()
    observed = []

    def request(method, params):
        request_id = uuid.uuid4().hex
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": request_id,
                                        "method": method, "params": params}) + "\n")
        process.stdin.flush()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                frame = frames.get(timeout=1)
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if frame.get("id") == request_id:
                return frame
            observed.append(frame)
        return {"error": {"message": method + "_timeout_or_exit",
                          "process_exit": process.poll()}}

    try:
        replies = {}
        for name, params in actions:
            replies[name] = request(name, params)
            if name == "session/open":
                opened = replies[name].get("result", {}).get("opened", {})
                root = opened.get("workspace_root")
                if root:
                    scratch = Path(root) / "g01_nonexistent_scratch"
                    scratch.mkdir(exist_ok=True)
                    (scratch / "marker.txt").write_text("must survive without approval\n")
        deadline = time.monotonic() + observe_seconds
        while time.monotonic() < deadline and process.poll() is None:
            if deny and any(item.get("method") in {"turn/error", "turn/completed"}
                            for item in observed):
                break
            try:
                frame = frames.get(timeout=1)
            except queue.Empty:
                continue
            observed.append(frame)
            if frame.get("method") == "approval/requested" and deny:
                response = {
                    "session_id": frame["params"]["session_id"],
                    "approval_id": frame["params"]["approval_id"],
                    "decision": "deny"}
                replies["approval/respond"] = request("approval/respond", response)
                replies["approval/respond/repeated"] = request("approval/respond", response)
                continue
            if frame.get("method") in {"approval/requested", "turn/error", "turn/completed"}:
                break
        return replies, observed, process.poll()
    finally:
        stop(process)
        thread.join(timeout=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deny", action="store_true")
    args = parser.parse_args()
    if not KERNEL.is_file():
        raise SystemExit("official_octos_binary_missing")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    run = Path(tempfile.mkdtemp(prefix="g01-approval-", dir="/tmp"))
    state, workspace, home = run / "state", run / "workspace", run / "home"
    for path in (state, workspace, home):
        path.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    session_id = "main:api:g01-" + uuid.uuid4().hex[:12]
    turn_id = str(uuid.uuid4())
    fixture_url = f"http://127.0.0.1:{server.server_port}/v1"
    try:
        with (run / "bootstrap.stderr").open("w") as errors:
            bootstrap, bootstrap_events, bootstrap_exit = run_phase(
                state, workspace, home, errors, [
                    ("profile/local/create", {"requested_id": "main", "name": "G01 isolated approval"}),
                    ("profile/llm/upsert", {"profile_id": "main", "selection": {
                        "family_id": "local", "model_id": "qwen3-0.6b", "route": {
                            "base_url": fixture_url, "api_type": "openai"}}, "set_primary": True})])
        with (run / "turn.stderr").open("w") as errors:
            turn, notifications, turn_exit = run_phase(
                state, workspace, home, errors, [
                    ("session/open", {"session_id": session_id, "profile_id": "main"}),
                    ("turn/start", {"session_id": session_id, "turn_id": turn_id,
                                    "input": [{"kind": "text", "text":
                                        "Remove the g01_nonexistent_scratch folder in this isolated workspace."}]})],
                observe_seconds=45, deny=args.deny)
        with (run / "rehydrate.stderr").open("w") as errors:
            rehydrated, rehydrate_events, rehydrate_exit = run_phase(
                state, workspace, home, errors, [
                    ("session/open", {"session_id": session_id, "profile_id": "main"}),
                    ("session/hydrate", {"session_id": session_id,
                                         "include": ["turns", "pending_approvals"]})])
        opened = turn.get("session/open", {}).get("result", {}).get("opened", {})
        marker = Path(opened.get("workspace_root", "/nonexistent")) / "g01_nonexistent_scratch/marker.txt"
        report = {"run_dir": str(run), "fixture_url": fixture_url,
                  "script_response": "deny" if args.deny else None,
                  "official_binary": str(KERNEL), "official_binary_version": "2.0.3-rc.11 deb433e9",
                  "session_id": session_id, "turn_id": turn_id,
                  "bootstrap": bootstrap, "bootstrap_events": bootstrap_events,
                  "bootstrap_exit_before_cleanup": bootstrap_exit,
                  "turn": turn, "notifications": notifications,
                  "turn_exit_before_cleanup": turn_exit,
                  "rehydrate": rehydrated, "rehydrate_events": rehydrate_events,
                  "rehydrate_exit_before_cleanup": rehydrate_exit,
                  "fixture_requests": Fixture.requests,
                  "scratch_marker_preserved": marker.read_text() == "must survive without approval\n"
                  if marker.is_file() else False,
                  "bootstrap_stderr_tail": (run / "bootstrap.stderr").read_text()[-2000:],
                  "turn_stderr_tail": (run / "turn.stderr").read_text()[-4000:],
                  "rehydrate_stderr_tail": (run / "rehydrate.stderr").read_text()[-2000:]}
        suffix = "-deny" if args.deny else ""
        output = ROOT / f"evidence/muse-g01-official-approval-fixture{suffix}-20260928.json"
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(output), "turn_accepted": turn.get("turn/start", {})
                          .get("result", {}).get("accepted") is True,
                          "events": [frame.get("method") for frame in notifications],
                          "fixture_calls": len(Fixture.requests),
                          "rehydrated_pending": len(rehydrated.get("session/hydrate", {})
                                                    .get("result", {}).get("pending_approvals", [])),
                          "scratch_marker_preserved": report["scratch_marker_preserved"]}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
