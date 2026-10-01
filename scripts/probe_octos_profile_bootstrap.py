#!/usr/bin/env python3
"""Probe official Octos profile bootstrap with isolated stdio JSON-RPC."""

import json
import os
import queue
import subprocess
import tempfile
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BINARY = ROOT / "runtime/octos-lean-target/debug/octos"


def main():
    if not BINARY.is_file():
        raise SystemExit("octos_binary_missing")
    run = Path(tempfile.mkdtemp(prefix="g01-profile-", dir="/tmp"))
    state = run / "state"
    workspace = run / "workspace"
    state.mkdir()
    workspace.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                   "HOME": str(run), "OCTOS_HOME": str(state),
                   "OCTOS_NO_NETWORK": "1", "RUST_LOG": "info"}
    command = [str(BINARY), "serve", "--stdio", "--solo", "--no-network",
               "--data-dir", str(state), "--config", str(state / "config.json"),
               "--cwd", str(workspace)]
    stderr_path = ROOT / "evidence/muse-g01-octos-profile-bootstrap-20260928.stderr.log"
    stderr_path.parent.mkdir(exist_ok=True)
    frames = queue.Queue()
    with stderr_path.open("w", encoding="utf-8") as errors:
        process = subprocess.Popen(command, env=environment, cwd=workspace,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=errors, text=True, bufsize=1)

        def read_frames():
            for line in process.stdout:
                frames.put(line)

        threading.Thread(target=read_frames, daemon=True).start()

        def request(request_id, method, params):
            payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
            process.stdin.write(json.dumps(payload) + "\n")
            process.stdin.flush()
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    frame = json.loads(frames.get(timeout=1))
                except queue.Empty:
                    if process.poll() is not None:
                        return {"error": "server_exited", "exit_code": process.returncode}
                    continue
                if frame.get("id") == request_id:
                    return frame
            return {"error": "timeout", "exit_code": process.poll()}

        try:
            replies = {
                "capabilities": request("g01-capabilities", "config/capabilities/list", {}),
                "main_before": request("g01-main-before", "session/open", {
                    "session_id": "_main:api:g01-before", "profile_id": "_main"}),
                "create_requested_main": request("g01-create", "profile/local/create", {
                    "name": "G01 isolated profile", "requested_id": "_main"}),
                "main_after": request("g01-main-after", "session/open", {
                    "session_id": "_main:api:g01-after", "profile_id": "_main"}),
            }
            created = replies["create_requested_main"].get("result")
            if isinstance(created, dict) and isinstance(created.get("profile_id"), str):
                profile_id = created["profile_id"]
                replies["created_profile_control"] = request(
                    "g01-created-control", "session/open", {
                        "session_id": profile_id + ":api:g01-control", "profile_id": profile_id})
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    result = {"run_dir": str(run), "command": command, "process_exit": process.returncode,
              "replies": replies}
    output = ROOT / "evidence/muse-g01-octos-profile-bootstrap-20260928.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run), "process_exit": process.returncode,
                      "reply_methods": list(replies), "output": str(output)}))


if __name__ == "__main__":
    main()
