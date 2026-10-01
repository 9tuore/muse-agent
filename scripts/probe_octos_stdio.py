#!/usr/bin/env python3
"""Exercise the real, local Octos AppUI stdio transport in an isolated home."""

import argparse
import json
import os
import queue
import subprocess
import tempfile
import threading
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--stderr", type=Path, required=True)
    args = parser.parse_args()
    if not args.binary.is_file():
        raise SystemExit("binary_missing")
    args.stderr.parent.mkdir(parents=True, exist_ok=True)
    frames = queue.Queue()
    # Octos creates a Unix control socket below its state root; macOS has a
    # short SUN_LEN limit, so use a deliberately short path under /tmp.
    with tempfile.TemporaryDirectory(prefix="mo-", dir="/tmp") as home, args.stderr.open("w") as errors:
        isolated = Path(home)
        (isolated / "workspace").mkdir()
        environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": home,
                       "XDG_CONFIG_HOME": str(isolated / "config"),
                       "XDG_DATA_HOME": str(isolated / "data"),
                       "OCTOS_HOME": str(isolated / "octos")}
        command = [str(args.binary), "serve", "--stdio", "--solo", "--no-network",
                   "--data-dir", str(isolated / "octos"),
                   "--instance-data-dir", str(isolated / "instance"),
                   "--cwd", str(isolated / "workspace")]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=errors, text=True, bufsize=1, env=environment)
        def read_frames():
            for line in process.stdout:
                frames.put(line)

        reader = threading.Thread(target=read_frames, daemon=True)
        reader.start()
        notifications = 0

        def request(method, params, request_id):
            nonlocal notifications
            payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
            process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
            process.stdin.flush()
            deadline = time.monotonic() + 90
            while True:
                try:
                    line = frames.get(timeout=1)
                except queue.Empty:
                    if process.poll() is not None:
                        return {"error": {"message": "server_exited", "process_exit": process.poll()}}
                    if time.monotonic() >= deadline:
                        return {"error": {"message": "response_timeout", "process_exit": process.poll()}}
                    continue
                try:
                    frame = json.loads(line)
                except ValueError:
                    return {"error": {"message": "non_json_protocol_frame"}}
                if frame.get("id") == request_id:
                    return frame
                notifications += 1

        try:
            capability = request("config/capabilities/list", {}, "capabilities-1")
            advertised = capability.get("result") if isinstance(capability.get("result"), dict) else {}
            capabilities = advertised.get("capabilities") if isinstance(advertised.get("capabilities"), dict) else {}
            methods = capabilities.get("supported_methods") if isinstance(capabilities.get("supported_methods"), list) else []
            profile = request("profile/local/create", {"name": "GOSIM Muse isolated probe"}, "profile-1")
            profile_result = profile.get("result")
            profile_id = profile_result.get("profile_id") if isinstance(profile_result, dict) else None
            session = (request("session/open", {"profile_id": profile_id,
                                                "session_id": f"{profile_id}:local:muse#probe"}, "session-1")
                       if isinstance(profile_id, str) else {"error": {"message": "profile_unavailable"}})
            report = {"binary": str(args.binary), "transport": "octos serve --stdio --solo",
                      "capabilities_ok": "result" in capability,
                      "capabilities_error": capability.get("error"),
                      "capability_result_keys": sorted(advertised),
                      "supported_methods_type": type(capabilities.get("supported_methods")).__name__,
                      "advertised_methods": {name: name in methods for name in
                                             ("profile/local/create", "session/open", "turn/start")},
                      "profile_ok": isinstance(profile_id, str),
                      "profile_id": profile_id,
                      "profile_error": profile.get("error"),
                      "session_ok": "result" in session,
                      "session_result_keys": sorted(session["result"]) if isinstance(session.get("result"), dict) else [],
                      "session_error": session.get("error"),
                      "notifications_seen": notifications,
                      "process_exit": process.poll()}
            print(json.dumps(report, ensure_ascii=False, indent=2))
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
