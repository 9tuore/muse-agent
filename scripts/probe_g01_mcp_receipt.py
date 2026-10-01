#!/usr/bin/env python3
"""Probe an inert MCP receipt through an isolated official Octos turn."""

import json
import sys
import tempfile
import threading
import time
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path

from probe_g01_official_approval_fixture import Fixture, KERNEL, ROOT, run_phase


TOOL = "g01_inert_receipt"


def serve_mcp():
    log_path = Path(sys.argv[2])
    nonce = sys.argv[3]
    with log_path.open("w", encoding="utf-8") as log:
        for line in sys.stdin:
            frame = json.loads(line)
            log.write(json.dumps(frame, ensure_ascii=False) + "\n")
            log.flush()
            method = frame.get("method")
            if "id" not in frame:
                continue
            if method == "initialize":
                result = {
                    "protocolVersion": frame.get("params", {}).get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "g01-inert-receipt", "version": "1.0.0"},
                }
            elif method == "tools/list":
                result = {"tools": [{"name": TOOL, "description": "Return a fixed inert receipt.",
                                     "inputSchema": {"type": "object", "properties": {}}}]}
            elif method == "tools/call":
                time.sleep(1)
                result = {"content": [{"type": "text", "text": "G01_INERT_RECEIPT:" + nonce}],
                          "isError": False}
            else:
                result = {}
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": frame["id"],
                                         "result": result}) + "\n")
            sys.stdout.flush()


def probe():
    if not KERNEL.is_file():
        raise SystemExit("official_octos_binary_missing")
    Fixture.requests = []
    Fixture.forced_tool_name = TOOL
    Fixture.forced_arguments = {"model_claimed_session": "untrusted-synthetic"}
    model = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    model_thread = threading.Thread(target=model.serve_forever, daemon=True)
    model_thread.start()
    run = Path(tempfile.mkdtemp(prefix="g01-mcp-receipt-", dir="/tmp"))
    state, workspace, home = (run / name for name in ("state", "workspace", "home"))
    for path in (state, workspace, home):
        path.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    nonce = uuid.uuid4().hex
    log_path = run / "mcp-frames.jsonl"
    session_id = "main:api:g01-mcp-" + uuid.uuid4().hex[:12]
    turn_id = str(uuid.uuid4())
    fixture_url = f"http://127.0.0.1:{model.server_port}/v1"
    try:
        with (run / "bootstrap.stderr").open("w") as errors:
            bootstrap, _, _ = run_phase(state, workspace, home, errors, [
                ("profile/local/create", {"requested_id": "main", "name": "G01 MCP receipt"}),
                ("profile/llm/upsert", {"profile_id": "main", "selection": {
                    "family_id": "local", "model_id": "qwen3-0.6b", "route": {
                        "base_url": fixture_url, "api_type": "openai"}}, "set_primary": True})])
        if not bootstrap.get("profile/llm/upsert", {}).get("result", {}).get("applied"):
            raise RuntimeError("official_profile_provision_failed")
        profile_path = state / "profiles/main.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["config"]["mcp_servers"] = [{"command": sys.executable,
                                               "args": [str(Path(__file__).resolve()),
                                                        "--mcp-server", str(log_path), nonce],
                                               "concurrency_class": "exclusive"}]
        profile["config"]["tool_policy"] = {"allow": [TOOL],
                                               "deny": ["shell", "write_file", "edit_file",
                                                        "diff_edit"]}
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
        with (run / "turn.stderr").open("w") as errors:
            turn, events, _ = run_phase(state, workspace, home, errors, [
                ("session/open", {"session_id": session_id, "profile_id": "main"}),
                ("turn/start", {"session_id": session_id, "turn_id": turn_id,
                                "input": [{"kind": "text", "text": "Call the inert receipt tool."}]})],
                observe_seconds=25)
        mcp_frames = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
        call = next((frame for frame in mcp_frames if frame.get("method") == "tools/call"), None)
        completed = [e.get("params", {}) for e in events if e.get("method") == "tool/completed"]
        turn_completed = [e.get("params", {}) for e in events if e.get("method") == "turn/completed"]
        result = {
            "official_binary": str(KERNEL), "run_dir": str(run), "session_id": session_id,
            "turn_id": turn_id, "nonce": nonce, "bootstrap": bootstrap,
            "turn": turn, "events": events, "mcp_frames": mcp_frames,
            "model_requests": Fixture.requests,
            "turn_stderr_tail": (run / "turn.stderr").read_text()[-4000:],
            "mcp_call_has_trusted_session_or_turn": call is not None and any(
                key in scope
                for scope in (call, call.get("params", {}),
                              call.get("params", {}).get("_meta", {}))
                for key in ("session_id", "turn_id", "tool_call_id")),
            "receipt_in_official_tool_completion": any(
                item.get("output_preview") == "G01_INERT_RECEIPT:" + nonce and
                item.get("session_id") == session_id and item.get("turn_id") == turn_id
                for item in completed),
            "turn_completed": any(item.get("session_id") == session_id and
                                  item.get("turn_id") == turn_id for item in turn_completed),
        }
        output = ROOT / "evidence/muse-g01-mcp-inert-receipt-20260928.json"
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(json.dumps({"output": str(output), "mcp_call_seen": call is not None,
                          "receipt_in_official_tool_completion": result["receipt_in_official_tool_completion"],
                          "turn_completed": result["turn_completed"],
                          "mcp_call_has_trusted_session_or_turn": result["mcp_call_has_trusted_session_or_turn"],
                          "events": [e.get("method") for e in events]}))
        if not (call and result["receipt_in_official_tool_completion"] and
                result["turn_completed"]):
            raise RuntimeError("official_mcp_receipt_integration_failed")
    finally:
        model.shutdown()
        model.server_close()
        model_thread.join(timeout=2)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp-server":
        serve_mcp()
    else:
        probe()
