#!/usr/bin/env python3
"""Verify an isolated official Octos profile denies synthetic side-effect tools."""

import json
import hashlib
import tempfile
import threading
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path

from probe_g01_official_approval_fixture import Fixture, KERNEL, ROOT, run_phase


class PolicyFixture(Fixture):
    requests = []


def main():
    if not KERNEL.is_file():
        raise SystemExit("official_octos_binary_missing")
    server = ThreadingHTTPServer(("127.0.0.1", 0), PolicyFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = Path(tempfile.mkdtemp(prefix="g01-policy-", dir="/tmp"))
    state, workspace, home = (root / name for name in ("state", "workspace", "home"))
    for path in (state, workspace, home):
        path.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    try:
        with (root / "bootstrap.stderr").open("w") as errors:
            bootstrap, _, _ = run_phase(state, workspace, home, errors, [
                ("profile/local/create", {"requested_id": "main", "name": "G01 read-only fixture"}),
                ("profile/llm/upsert", {"profile_id": "main", "selection": {
                    "family_id": "local", "model_id": "qwen3-0.6b", "route": {
                        "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                        "api_type": "openai"}}, "set_primary": True})])
        if bootstrap["profile/llm/upsert"].get("result", {}).get("applied") is not True:
            raise RuntimeError("profile_bootstrap_failed")
        profile_path = state / "profiles/main.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["config"]["tool_policy"] = {
            "allow": ["read_file", "glob", "grep", "list_dir"],
            "deny": ["shell", "write_file", "edit_file", "diff_edit"]}
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
        results = []
        for tool_name, arguments in (
            ("shell", {"command": "rm -rf g01_nonexistent_scratch"}),
            ("write_file", {"path": "g01_nonexistent_scratch/marker.txt", "content": "changed\n"}),
        ):
            PolicyFixture.requests = []
            PolicyFixture.forced_tool_name = tool_name
            PolicyFixture.forced_arguments = arguments
            session_id = "main:api:g01-policy-" + uuid.uuid4().hex[:12]
            turn_id = str(uuid.uuid4())
            with (root / f"{tool_name}.stderr").open("w") as errors:
                replies, frames, process_exit = run_phase(
                    state, workspace, home, errors, [
                        ("session/open", {"session_id": session_id, "profile_id": "main"}),
                        ("turn/start", {"session_id": session_id, "turn_id": turn_id,
                                        "input": [{"kind": "text", "text":
                                                   "Use the requested tool in this isolated workspace."}]})],
                    observe_seconds=25)
            opened = replies.get("session/open", {}).get("result", {}).get("opened", {})
            marker = Path(opened.get("workspace_root", "/nonexistent")) / \
                "g01_nonexistent_scratch/marker.txt"
            results.append({"attempted_tool": tool_name, "session_id": session_id,
                            "turn_id": turn_id, "replies": replies, "frames": frames,
                            "fixture_requests": list(PolicyFixture.requests),
                            "process_exit_before_cleanup": process_exit,
                            "marker_preserved": marker.is_file() and
                            marker.read_text(encoding="utf-8") ==
                            "must survive without approval\n",
                            "stderr_tail": (root / f"{tool_name}.stderr").read_text()[-4000:]})
        for item in results:
            # The protocol directory uses the UTF-8 hex encoding of session_id.
            ledger_dir = state / "ui-protocol" / item["session_id"].encode().hex()
            ledger_paths = list(ledger_dir.glob("ledger-*.log"))
            item["ledger"] = [{"path": str(path),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                               "tool_events": [json.loads(line)["event"] for line in
                                               path.read_text(encoding="utf-8").splitlines()
                                               if '"kind":"tool_' in line or
                                               '"kind":"approval_requested"' in line]}
                              for path in ledger_paths]
            completions = [frame["params"] for frame in item["frames"]
                           if frame.get("method") == "tool/completed"]
            item["policy_pass"] = (
                item["marker_preserved"] and
                not any(frame.get("method") == "approval/requested" for frame in item["frames"]) and
                bool(item["fixture_requests"]) and
                item["attempted_tool"] not in item["fixture_requests"][0]["tools"] and
                len(completions) == 1 and completions[0].get("success") is False and
                completions[0].get("output_preview") ==
                "unknown tool: " + item["attempted_tool"] and
                bool(item["ledger"]))
        report = {"run_dir": str(root), "official_binary": str(KERNEL),
                  "policy": profile["config"]["tool_policy"], "results": results}
        output = ROOT / "evidence/muse-g01-official-tool-policy-fixture-20260928.json"
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(json.dumps({"output": str(output), "results": [{
            "attempted_tool": item["attempted_tool"],
            "turn_accepted": item["replies"].get("turn/start", {}).get("result", {}).get("accepted"),
            "advertised_tools": item["fixture_requests"][0]["tools"]
            if item["fixture_requests"] else [],
            "events": [frame.get("method") for frame in item["frames"]],
            "marker_preserved": item["marker_preserved"],
            "policy_pass": item["policy_pass"]} for item in results]}))
        if not all(item["policy_pass"] for item in results):
            raise RuntimeError("official_tool_policy_check_failed")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
