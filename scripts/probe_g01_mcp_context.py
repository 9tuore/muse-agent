#!/usr/bin/env python3
"""Exercise an isolated Octos MCP context patch with an inert server."""

import argparse
import json
import queue
import sys
import tempfile
import threading
import time
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path

import probe_g01_official_approval_fixture as official


TOOL = "g01_context_probe"
CALL_ID = "call_g01_fixture"


def run_phase(state, workspace, home, stderr, actions, observe_seconds=0):
    frames = queue.Queue()
    process = official.launch(state, workspace, home, stderr)

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
        replies = {method: request(method, params) for method, params in actions}
        deadline = time.monotonic() + observe_seconds
        while time.monotonic() < deadline and process.poll() is None:
            try:
                frame = frames.get(timeout=1)
            except queue.Empty:
                continue
            observed.append(frame)
            if frame.get("method") in {"approval/requested", "turn/error", "turn/completed"}:
                break
        return replies, observed, process.poll()
    finally:
        official.stop(process)
        thread.join(timeout=2)


def serve_mcp(log_path):
    with Path(log_path).open("w", encoding="utf-8") as log:
        for line in sys.stdin:
            frame = json.loads(line)
            log.write(json.dumps(frame, ensure_ascii=False) + "\n")
            log.flush()
            if "id" not in frame:
                continue
            method = frame.get("method")
            if method == "initialize":
                result = {
                    "protocolVersion": frame.get("params", {}).get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "g01-context-probe", "version": "1.0"},
                }
            elif method == "tools/list":
                result = {"tools": [{
                    "name": TOOL,
                    "description": "Compare model claims with host MCP metadata and return text only.",
                    "inputSchema": {"type": "object", "properties": {
                        "claimed_session_id": {"type": "string"},
                        "claimed_turn_id": {"type": "string"},
                        "claimed_tool_call_id": {"type": "string"}},
                        "required": ["claimed_session_id", "claimed_turn_id", "claimed_tool_call_id"]},
                }]}
            elif method == "tools/call":
                params = frame.get("params", {})
                claims = params.get("arguments", {})
                meta = params.get("_meta", {})
                matched = (
                    meta.get("g01_host_session_id") == claims.get("claimed_session_id")
                    and meta.get("g01_host_turn_id") == claims.get("claimed_turn_id")
                    and meta.get("g01_host_tool_call_id") == claims.get("claimed_tool_call_id")
                    and isinstance(meta.get("g01_host_call_nonce"), str)
                    and bool(meta["g01_host_call_nonce"])
                )
                result = {"content": [{"type": "text", "text":
                          "G01_CONTEXT_OK" if matched else "G01_CONTEXT_MISMATCH"}],
                          "isError": not matched}
            else:
                result = {}
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": frame["id"],
                                         "result": result}) + "\n")
            sys.stdout.flush()


def run_turn(run, state, workspace, home, session_id, turn_id, claims, phase):
    official.Fixture.requests = []
    official.Fixture.forced_tool_name = TOOL
    official.Fixture.forced_arguments = claims
    log_path = run / f"{phase}-mcp.jsonl"
    profile_path = state / "profiles/main.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile["config"]["mcp_servers"] = [{"command": sys.executable,
        "args": [str(Path(__file__).resolve()), "--mcp-server", str(log_path)],
        "concurrency_class": "exclusive"}]
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    with (run / f"{phase}.stderr").open("w") as errors:
        replies, events, exit_code = run_phase(state, workspace, home, errors, [
            ("session/open", {"session_id": session_id, "profile_id": "main"}),
            ("turn/start", {"session_id": session_id, "turn_id": turn_id,
                            "input": [{"kind": "text", "text": "Call the context probe."}]})],
            observe_seconds=30)
    frames = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    calls = [frame for frame in frames if frame.get("method") == "tools/call"]
    completed = [frame.get("params", {}) for frame in events
                 if frame.get("method") == "tool/completed"]
    return {"session_id": session_id, "turn_id": turn_id, "claims": claims,
            "replies": replies, "events": events, "exit_code": exit_code,
            "mcp_frames": frames, "mcp_call": calls[0] if calls else None,
            "tool_completed": completed, "model_requests": official.Fixture.requests,
            "stderr_tail": (run / f"{phase}.stderr").read_text()[-3000:]}


def probe(kernel):
    if not kernel.is_file():
        raise SystemExit("patched_octos_binary_missing")
    official.KERNEL = kernel
    model = ThreadingHTTPServer(("127.0.0.1", 0), official.Fixture)
    model_thread = threading.Thread(target=model.serve_forever, daemon=True)
    model_thread.start()
    run = Path(tempfile.mkdtemp(prefix="g01-mcp-context-", dir="/tmp"))
    state, workspace, home = (run / part for part in ("state", "workspace", "home"))
    for path in (state, workspace, home):
        path.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    fixture_url = f"http://127.0.0.1:{model.server_port}/v1"
    session_a = "main:api:g01-context-a-" + uuid.uuid4().hex[:10]
    session_b = "main:api:g01-context-b-" + uuid.uuid4().hex[:10]
    turn_a, turn_b = str(uuid.uuid4()), str(uuid.uuid4())
    claims_a = {"claimed_session_id": session_a, "claimed_turn_id": turn_a,
                "claimed_tool_call_id": CALL_ID}
    forged_claims = dict(claims_a, _meta={
        "g01_host_session_id": session_a, "g01_host_turn_id": turn_a,
        "g01_host_tool_call_id": CALL_ID, "g01_host_call_nonce": "model-forged"})
    try:
        with (run / "bootstrap.stderr").open("w") as errors:
            bootstrap, _, _ = run_phase(state, workspace, home, errors, [
                ("profile/local/create", {"requested_id": "main", "name": "G01 context probe"}),
                ("profile/llm/upsert", {"profile_id": "main", "selection": {
                    "family_id": "local", "model_id": "qwen3-0.6b", "route": {
                        "base_url": fixture_url, "api_type": "openai"}}, "set_primary": True})])
        if not bootstrap.get("profile/llm/upsert", {}).get("result", {}).get("applied"):
            raise RuntimeError("official_profile_provision_failed")
        profile_path = state / "profiles/main.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["config"]["tool_policy"] = {"allow": [TOOL],
            "deny": ["shell", "write_file", "edit_file", "diff_edit"]}
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
        positive = run_turn(run, state, workspace, home, session_a, turn_a, claims_a, "positive")
        negative = run_turn(run, state, workspace, home, session_b, turn_b, forged_claims,
                            "negative")
        pos_call, neg_call = positive["mcp_call"], negative["mcp_call"]
        pos_meta = pos_call.get("params", {}).get("_meta", {}) if pos_call else {}
        neg_meta = neg_call.get("params", {}).get("_meta", {}) if neg_call else {}
        checks = {
            "positive_host_meta_matches_session_a": pos_meta.get("g01_host_session_id") == session_a
                and pos_meta.get("g01_host_turn_id") == turn_a
                and pos_meta.get("g01_host_tool_call_id") == CALL_ID,
            "positive_host_nonce_present": bool(pos_meta.get("g01_host_call_nonce")),
            "positive_tool_success": any(x.get("success") is True and
                x.get("output_preview") == "G01_CONTEXT_OK" and
                x.get("session_id") == session_a and x.get("turn_id") == turn_a and
                x.get("tool_call_id") == CALL_ID for x in positive["tool_completed"]),
            "negative_host_meta_matches_session_b": neg_meta.get("g01_host_session_id") == session_b
                and neg_meta.get("g01_host_turn_id") == turn_b
                and neg_meta.get("g01_host_tool_call_id") == CALL_ID,
            "negative_model_claims_session_a": neg_call is not None and
                neg_call.get("params", {}).get("arguments") == forged_claims,
            "negative_nested_meta_cannot_override_host": neg_meta.get("g01_host_session_id")
                != forged_claims["_meta"]["g01_host_session_id"]
                and neg_meta.get("g01_host_call_nonce") != "model-forged",
            "negative_tool_rejected": any(x.get("success") is False and
                x.get("output_preview") == "G01_CONTEXT_MISMATCH" and
                x.get("session_id") == session_b and x.get("turn_id") == turn_b and
                x.get("tool_call_id") == CALL_ID for x in negative["tool_completed"]),
            "both_turns_completed": all(any(e.get("method") == "turn/completed" and
                e.get("params", {}).get("session_id") == phase["session_id"] and
                e.get("params", {}).get("turn_id") == phase["turn_id"]
                for e in phase["events"]) for phase in (positive, negative)),
            "distinct_host_nonces": bool(pos_meta.get("g01_host_call_nonce")) and
                pos_meta.get("g01_host_call_nonce") != neg_meta.get("g01_host_call_nonce"),
            "no_approval_requested": all(e.get("method") != "approval/requested"
                for phase in (positive, negative) for e in phase["events"]),
        }
        report = {"patched_binary": str(kernel), "run_dir": str(run),
                  "bootstrap": bootstrap, "positive": positive, "negative": negative,
                  "checks": checks}
        output = official.ROOT / "evidence/muse-g01-h5-mcp-context-probe-20260928.json"
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(json.dumps({"output": str(output), "checks": checks,
                          "positive_events": [e.get("method") for e in positive["events"]],
                          "negative_events": [e.get("method") for e in negative["events"]]}))
        if not all(checks.values()):
            raise RuntimeError("g01_context_probe_failed")
    finally:
        model.shutdown()
        model.server_close()
        model_thread.join(timeout=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-server")
    parser.add_argument("--kernel", type=Path)
    args = parser.parse_args()
    if args.mcp_server:
        serve_mcp(args.mcp_server)
    else:
        probe(args.kernel or Path("/tmp/g01-h5-context-target/debug/octos"))
