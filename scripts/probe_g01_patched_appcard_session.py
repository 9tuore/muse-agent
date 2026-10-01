#!/usr/bin/env python3
"""Run a patched official AppCard with an officially provisioned local profile."""

import argparse
import hashlib
import json
import os
import queue
import re
import signal
import subprocess
import tempfile
import threading
import time
import urllib.parse
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KERNEL = Path("/Users/mima0000/Documents/ChatGPT/Agent APP黑客松/runtime/octos-lean-target/debug/octos")
DEFAULT_APP = Path("/tmp/g01-appcard-build-20260928/target/debug/octos-app")


def provision(state, workspace):
    command = [str(KERNEL), "serve", "--stdio", "--solo", "--no-network",
               "--data-dir", str(state), "--config", str(state / "config.json"),
               "--cwd", str(workspace)]
    environment = {"PATH": "/usr/bin:/bin", "HOME": str(state.parent),
                   "OCTOS_HOME": str(state), "OCTOS_NO_NETWORK": "1", "RUST_LOG": "warn"}
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, bufsize=1,
                               cwd=workspace, env=environment)
    frames = queue.Queue()

    def collect():
        for line in process.stdout:
            try:
                frames.put(json.loads(line))
            except ValueError:
                pass

    threading.Thread(target=collect, daemon=True).start()

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
        raise RuntimeError(method + "_timeout")

    try:
        created = request("profile/local/create", {"requested_id": "main",
                                                    "name": "G01 isolated AppCard"})
        upserted = request("profile/llm/upsert", {"profile_id": "main", "selection": {
            "family_id": "local", "model_id": "qwen3-0.6b",
            "route": {"base_url": "http://127.0.0.1:8080/v1", "api_type": "openai"}},
            "set_primary": True})
        if created.get("result", {}).get("profile_id") != "main" or \
                upserted.get("result", {}).get("applied") is not True:
            raise RuntimeError("official_profile_provision_failed")
        return {"profile_id": "main", "llm_upsert_applied": True}
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--appcard-binary", type=Path, default=DEFAULT_APP)
    parser.add_argument("--seconds", type=int, default=45)
    args = parser.parse_args()
    app = args.appcard_binary.resolve()
    if not app.is_file() or not KERNEL.is_file() or not 10 <= args.seconds <= 90:
        raise SystemExit("official_binary_or_duration_invalid")
    run = Path(tempfile.mkdtemp(prefix="g01-patched-appcard-", dir="/tmp"))
    state, workspace, home = run / "core", run / "workspace", run / "home"
    for directory in (state, workspace, home):
        directory.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    provisioned = provision(state, workspace)
    log_path = run / "appcard.log"
    environment = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL", "USER", "LOGNAME")
                   if key in os.environ}
    environment.update(HOME=str(home), OCTOS_APP_CORE_BIN=str(KERNEL),
                       OCTOS_APP_CORE_DIR=str(state), OCTOS_PROFILE_ID="main",
                       OCTOS_NO_NETWORK="1", RUST_LOG="info")
    child_pids = set()
    with log_path.open("wb") as log:
        process = subprocess.Popen([str(app)], cwd=str(app.parent.parent.parent / "source/app"),
                                   env=environment, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + args.seconds
            while time.monotonic() < deadline and process.poll() is None:
                rows = subprocess.run(["ps", "-axo", "pid=,ppid=,command="],
                                      capture_output=True, text=True, check=True).stdout
                for line in rows.splitlines():
                    parts = line.strip().split(None, 2)
                    if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit() and \
                            int(parts[1]) == process.pid and str(state) in parts[2] and \
                            "serve --stdio" in parts[2]:
                        child_pids.add(int(parts[0]))
                time.sleep(0.5)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
    remaining = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True,
                               text=True, check=True).stdout
    for line in remaining.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and int(parts[0]) in child_pids and \
                str(state) in parts[1] and "serve --stdio" in parts[1]:
            os.kill(int(parts[0]), signal.SIGTERM)
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    core_logs = sorted((state / "logs").glob("serve.*.log")) if (state / "logs").is_dir() else []
    core_text = core_logs[-1].read_text(encoding="utf-8", errors="replace") if core_logs else ""
    sessions = sorted(set(re.findall(r"session/open (main:api:[^\s]+)", log_text)))
    ledger_dir = state / "profiles/main/data/context_ledgers"
    persisted = []
    for path in ledger_dir.glob("*.json") if ledger_dir.is_dir() else []:
        try:
            ledger = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        session_id = ledger.get("state", {}).get("session_id")
        if session_id == urllib.parse.unquote(path.stem):
            persisted.append(session_id)
    report = {"run_dir": str(run), "appcard_binary": str(app),
              "appcard_sha256": hashlib.sha256(app.read_bytes()).hexdigest(),
              "official_source_commit": "a3d0230a0dadb2e6ae73fa8a518fb7ef6d2f7a18",
              "patch": "patches/octoscript-appcard-stdio-profile-env.patch",
              "provisioned": provisioned, "appcard_exit": process.returncode,
              "core_child_pids": sorted(child_pids), "session_open_requests": sessions,
              "persisted_official_session_ids": sorted(persisted),
              "all_requested_sessions_persisted": bool(sessions) and set(sessions) <= set(persisted),
              "profile_unresolved_in_logs": "profile_unresolved" in log_text + core_text,
              "appcard_log_tail": log_text[-12000:], "core_log_tail": core_text[-12000:]}
    output = ROOT / "evidence/muse-g01-patched-appcard-session-20260928.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "core_child_seen": bool(child_pids),
                      "session_open_requests": len(sessions),
                      "all_requested_sessions_persisted": report["all_requested_sessions_persisted"],
                      "profile_unresolved_in_logs": report["profile_unresolved_in_logs"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
