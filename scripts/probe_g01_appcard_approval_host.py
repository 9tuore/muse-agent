#!/usr/bin/env python3
"""Observe official AppCard -> Octos tool-approval path without approving it."""

import argparse
import hashlib
import json
import os
import plistlib
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path

from probe_g01_official_approval_fixture import Fixture, KERNEL, ROOT, run_phase
from probe_g01_mcp_receipt import TOOL


APP = Path("/tmp/g01-appcard-build-20260928/target/debug/octos-app")
SOURCE_APP = Path("/tmp/g01-appcard-build-20260928/source/app")
MANUAL_COMMAND = "rm -rf g01_manual_scratch"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--read-only-policy", action="store_true")
    parser.add_argument("--capture-window", action="store_true")
    parser.add_argument("--bundle-window", action="store_true")
    parser.add_argument("--dump-geometry-frames", type=int)
    parser.add_argument("--manual-wait-seconds", type=int)
    parser.add_argument("--mcp-inert-receipt", action="store_true")
    args = parser.parse_args()
    if args.mcp_inert_receipt:
        if args.manual_wait_seconds is not None or args.read_only_policy:
            raise SystemExit("mcp_inert_receipt_conflicts_with_other_modes")
        Fixture.forced_tool_name = TOOL
        Fixture.forced_arguments = {"model_claimed_session": "untrusted-synthetic"}
    if args.manual_wait_seconds is not None:
        if (not 30 <= args.manual_wait_seconds <= 600 or args.dump_geometry_frames
                or args.read_only_policy or args.capture_window):
            raise SystemExit("manual_wait_seconds_invalid_or_conflicting_probe_mode")
        args.bundle_window = True
        Fixture.forced_arguments = {"command": MANUAL_COMMAND}
    if not APP.is_file() or not KERNEL.is_file() or not SOURCE_APP.is_dir():
        raise SystemExit("patched_appcard_or_kernel_missing")
    Fixture.requests.clear()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    run = Path(tempfile.mkdtemp(prefix="g01-appcard-approval-", dir="/tmp"))
    state, workspace, home = run / "state", run / "workspace", run / "home"
    for path in (state, workspace, home):
        path.mkdir()
    (state / "config.json").write_text("{}\n", encoding="utf-8")
    mcp_nonce = uuid.uuid4().hex if args.mcp_inert_receipt else None
    mcp_log = run / "mcp-frames.jsonl"
    fixture_url = f"http://127.0.0.1:{server.server_port}/v1"
    try:
        with (run / "bootstrap.stderr").open("w") as errors:
            bootstrap, _, _ = run_phase(state, workspace, home, errors, [
                ("profile/local/create", {"requested_id": "main", "name": "G01 AppCard approval"}),
                ("profile/llm/upsert", {"profile_id": "main", "selection": {
                    "family_id": "local", "model_id": "qwen3-0.6b",
                    "route": {"base_url": fixture_url, "api_type": "openai"}},
                    "set_primary": True})])
        if not bootstrap.get("profile/llm/upsert", {}).get("result", {}).get("applied"):
            raise RuntimeError("official_profile_provision_failed")
        policy = None
        if args.read_only_policy:
            profile_path = state / "profiles/main.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            policy = {"allow": ["read_file", "glob", "grep", "list_dir"],
                      "deny": ["shell", "write_file", "edit_file", "diff_edit"]}
            profile["config"]["tool_policy"] = policy
            profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
        if args.mcp_inert_receipt:
            profile_path = state / "profiles/main.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["config"]["mcp_servers"] = [{
                "command": sys.executable,
                "args": [str(ROOT / "scripts/probe_g01_mcp_receipt.py"), "--mcp-server",
                         str(mcp_log), mcp_nonce],
                "concurrency_class": "exclusive"}]
            profile["config"]["tool_policy"] = {
                "allow": [TOOL], "deny": ["shell", "write_file", "edit_file", "diff_edit"]}
            profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
        env = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL", "USER", "LOGNAME")
               if key in os.environ}
        env.update(HOME=str(home), OCTOS_APP_CORE_BIN=str(KERNEL),
                   OCTOS_APP_CORE_DIR=str(state), OCTOS_PROFILE_ID="main",
                   OCTOS_NO_NETWORK="1", MAKEPAD_AUTO_PROMPT="Remove the empty isolated scratch folder.",
                   RUST_LOG="info")
        geometry_path = run / "geometry.json" if args.dump_geometry_frames else None
        if geometry_path:
            env["MAKEPAD_DUMP_GEOMETRY"] = str(geometry_path)
            env["MAKEPAD_DUMP_GEOMETRY_FRAMES"] = str(args.dump_geometry_frames)
        app_log = run / "appcard.log"
        app_binary = APP
        if args.bundle_window:
            if shutil.disk_usage(run).free < APP.stat().st_size * 2:
                raise SystemExit("insufficient_free_space_for_isolated_app_bundle")
            contents = run / "G01 Octos Fixture.app/Contents"
            (contents / "MacOS").mkdir(parents=True)
            app_binary = contents / "MacOS/octos-app"
            shutil.copy2(APP, app_binary)
            with (contents / "Info.plist").open("wb") as plist:
                plistlib.dump({"CFBundleExecutable": "octos-app",
                               "CFBundleIdentifier": "org.gosim.fixture.octosapp",
                               "CFBundleName": "G01 Octos Fixture",
                               "CFBundlePackageType": "APPL", "CFBundleVersion": "1"}, plist)
        screenshot = None
        region_screenshot = None
        capture_error = None
        window_debug = None
        activation_code = None
        manual_scratch = None
        with app_log.open("wb") as log:
            process = subprocess.Popen([str(app_binary)], cwd=SOURCE_APP, env=env,
                                       stdin=subprocess.DEVNULL, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                deadline = time.monotonic() + 40
                while time.monotonic() < deadline and process.poll() is None:
                    if Fixture.requests:
                        time.sleep(3)
                        if args.manual_wait_seconds is not None:
                            request = None
                            request_deadline = time.monotonic() + 20
                            while time.monotonic() < request_deadline and not request:
                                for ledger in (state / "ui-protocol").glob("*/ledger-*.log"):
                                    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
                                        try:
                                            event = json.loads(line).get("event", {})
                                        except ValueError:
                                            continue
                                        if event.get("kind") == "approval_requested":
                                            request = event
                                            break
                                    if request:
                                        break
                                if not request:
                                    time.sleep(0.5)
                            command = (request or {}).get("typed_details", {}).get("command", {})
                            cwd = command.get("cwd")
                            if command.get("command_line") != MANUAL_COMMAND or not isinstance(cwd, str):
                                print(json.dumps({"manual_request_ready": False,
                                                  "reason": "expected_approval_request_not_observed"}), flush=True)
                                break
                            manual_scratch = Path(cwd) / "g01_manual_scratch"
                            if not manual_scratch.resolve().is_relative_to(state.resolve()):
                                raise RuntimeError("manual_scratch_outside_isolated_state")
                            manual_scratch.mkdir()
                            (manual_scratch / "marker.txt").write_text(
                                "must survive until a human approves deletion\n", encoding="utf-8")
                            activator = run / "activate_app"
                            compiled = subprocess.run(
                                ["clang", "-framework", "AppKit", "-o", str(activator),
                                 str(ROOT / "scripts/g01_activate_app.m")],
                                capture_output=True, text=True, timeout=30)
                            if compiled.returncode == 0:
                                activated = subprocess.run([str(activator), str(process.pid)],
                                                           capture_output=True, text=True, timeout=10)
                                activation_code = activated.returncode
                            else:
                                capture_error = compiled.stderr[-500:]
                            print(json.dumps({"manual_request_ready": True,
                                              "manual_window_ready": activation_code == 0,
                                              "run_dir": str(run),
                                              "command": MANUAL_COMMAND,
                                              "scratch": str(manual_scratch),
                                              "instruction": "Click Approve or Deny in the AppCard window yourself; this script never sends approval/respond."},
                                             ensure_ascii=False), flush=True)
                            manual_deadline = time.monotonic() + args.manual_wait_seconds
                            while time.monotonic() < manual_deadline and process.poll() is None:
                                decided = False
                                for ledger in (state / "ui-protocol").glob("*/ledger-*.log"):
                                    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
                                        try:
                                            event = json.loads(line).get("event", {})
                                        except ValueError:
                                            continue
                                        if event.get("kind") == "approval_decided":
                                            decided = True
                                            break
                                    if decided:
                                        break
                                if decided:
                                    time.sleep(5)
                                    break
                                time.sleep(0.5)
                            break
                        if args.capture_window:
                            suffix = ("-readonly" if args.read_only_policy else "") + \
                                     ("-bundle" if args.bundle_window else "") + \
                                     (f"-geometry{args.dump_geometry_frames}"
                                      if args.dump_geometry_frames else "")
                            screenshot = ROOT / f"evidence/muse-g01-appcard-window{suffix}-20260928.png"
                            activator = run / "activate_app"
                            activate_compiled = subprocess.run(
                                ["clang", "-framework", "AppKit", "-o", str(activator),
                                 str(ROOT / "scripts/g01_activate_app.m")],
                                capture_output=True, text=True, timeout=30)
                            if activate_compiled.returncode == 0:
                                activated = subprocess.run([str(activator), str(process.pid)],
                                                           capture_output=True, text=True, timeout=10)
                                activation_code = activated.returncode
                                time.sleep(1)
                            helper = run / "window_id"
                            compiled = subprocess.run(
                                ["clang", "-framework", "ApplicationServices", "-o", str(helper),
                                 str(ROOT / "scripts/g01_app_window_id.m")],
                                capture_output=True, text=True, timeout=30)
                            if compiled.returncode == 0:
                                window = subprocess.run([str(helper), str(process.pid)],
                                                        capture_output=True, text=True, timeout=10)
                                window_debug = window.stderr[-1000:]
                                if window.returncode == 0:
                                    window_parts = window.stdout.split()
                                    captured = subprocess.run(
                                        ["screencapture", "-x", "-l" + window_parts[0],
                                         str(screenshot)], capture_output=True, text=True, timeout=20)
                                    if captured.returncode != 0:
                                        capture_error = captured.stderr[-500:]
                                    if len(window_parts) == 6 and window_parts[5] == "1":
                                        region_screenshot = screenshot.with_name(
                                            screenshot.stem + "-region.png")
                                        region = ",".join(window_parts[1:5])
                                        subprocess.run(["screencapture", "-x", "-R" + region,
                                                        str(region_screenshot)], capture_output=True,
                                                       text=True, timeout=20)
                                else:
                                    capture_error = "appcard_window_not_found"
                            else:
                                capture_error = compiled.stderr[-500:]
                        time.sleep(17)
                        break
                    time.sleep(0.5)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
        if args.bundle_window:
            shutil.rmtree(run / "G01 Octos Fixture.app")
        session_files = list((state / "profiles/main/data/sessions").glob("*.jsonl"))
        tool_rows = []
        for path in session_files:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("tool_calls") or row.get("role") == "tool":
                    tool_rows.append({"session_file": path.name, "row": row})
        lifecycle = []
        allowed = {"turn_started", "approval_requested", "approval_decided",
                   "approval_cancelled", "tool_started", "tool_completed",
                   "turn_completed", "turn_error"}
        for path in (state / "ui-protocol").glob("*/ledger-*.log"):
            try:
                session_id = bytes.fromhex(path.parent.name).decode("utf-8")
            except ValueError:
                continue
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                event = record.get("event", {})
                if event.get("kind") in allowed:
                    lifecycle.append({"session_id": session_id, "seq": record.get("seq"),
                                      "event": event})
        lifecycle.sort(key=lambda item: (item["session_id"], item["seq"]))
        manual_requests = [item for item in lifecycle
                           if item["event"]["kind"] == "approval_requested"]
        manual_decisions = [item for item in lifecycle
                            if item["event"]["kind"] == "approval_decided"
                            and any(item["session_id"] == request["session_id"]
                                    and item["event"].get("approval_id") ==
                                    request["event"].get("approval_id")
                                    for request in manual_requests)]
        manual_marker_present_after = ((manual_scratch / "marker.txt").is_file()
                                       if manual_scratch else None)
        manual_wire_verdict = None
        if args.manual_wait_seconds is not None:
            requested_tools = {
                (item["session_id"], item["event"].get("turn_id"),
                 item["event"].get("typed_details", {}).get("command", {}).get("tool_call_id"))
                for item in manual_requests
            }
            completed_success = any(item["event"]["kind"] == "tool_completed"
                                    and item["event"].get("success") is True
                                    and (item["session_id"], item["event"].get("turn_id"),
                                         item["event"].get("tool_call_id")) in requested_tools
                                    for item in lifecycle)
            decisions = [item["event"].get("decision") for item in manual_decisions]
            if not manual_requests or manual_scratch is None:
                manual_wire_verdict = "BLOCKED_REQUEST"
            elif not decisions:
                manual_wire_verdict = "WAITING_HUMAN"
            elif decisions == ["deny"] and manual_marker_present_after and not completed_success:
                manual_wire_verdict = "DENIED_NATIVE_ONLY"
            elif decisions == ["approve"] and not manual_marker_present_after and completed_success:
                manual_wire_verdict = "APPROVED_NATIVE_ONLY"
            else:
                manual_wire_verdict = "INCONSISTENT"
        core_logs = list((state / "logs").glob("serve.*.log"))
        geometry_evidence = None
        if geometry_path and geometry_path.is_file():
            geometry_evidence = ROOT / (
                f"evidence/muse-g01-appcard-approval-geometry-bundle-frames"
                f"{args.dump_geometry_frames}-20260928.json")
            shutil.copy2(geometry_path, geometry_evidence)
        mcp_frames = ([json.loads(line) for line in mcp_log.read_text(encoding="utf-8").splitlines()]
                      if mcp_log.is_file() else [])
        mcp_calls = [frame for frame in mcp_frames if frame.get("method") == "tools/call"]
        receipt_events = [item for item in lifecycle
                          if item["event"]["kind"] == "tool_completed"
                          and item["event"].get("output_preview") == "G01_INERT_RECEIPT:" +
                          str(mcp_nonce)]
        report = {"run_dir": str(run), "appcard_binary": str(APP),
                  "appcard_sha256": hashlib.sha256(APP.read_bytes()).hexdigest(),
                  "bundle_window": args.bundle_window,
                  "geometry_path": str(geometry_evidence) if geometry_evidence else None,
                  "geometry_run_path": str(geometry_path) if geometry_path and geometry_path.is_file() else None,
                  "geometry_frames": args.dump_geometry_frames,
                  "manual_wait_seconds": args.manual_wait_seconds,
                  "manual_decisions": manual_decisions,
                  "manual_scratch": str(manual_scratch) if manual_scratch else None,
                  "manual_marker_present_after": manual_marker_present_after,
                  "manual_wire_verdict": manual_wire_verdict,
                  "official_binary": str(KERNEL), "fixture_url": fixture_url,
                  "tool_policy": policy,
                  "mcp_inert_nonce": mcp_nonce, "mcp_frames": mcp_frames,
                  "mcp_calls": mcp_calls, "mcp_receipt_events": receipt_events,
                  "screenshot": str(screenshot) if screenshot and screenshot.is_file() else None,
                  "region_screenshot": (str(region_screenshot) if region_screenshot and
                                        region_screenshot.is_file() else None),
                  "capture_error": capture_error,
                  "window_debug": window_debug,
                  "activation_code": activation_code,
                  "bootstrap": bootstrap, "appcard_exit_after_stop": process.returncode,
                  "fixture_requests": Fixture.requests, "tool_rows": tool_rows,
                  "official_lifecycle_events": lifecycle,
                  "appcard_log_tail": app_log.read_text(encoding="utf-8", errors="replace")[-12000:],
                  "core_log_tail": core_logs[-1].read_text(encoding="utf-8", errors="replace")[-8000:]
                                   if core_logs else ""}
        suffix = ("-readonly" if args.read_only_policy else "") + \
                 ("-mcp-inert" if args.mcp_inert_receipt else "") + \
                 ("-bundle" if args.bundle_window else "") + \
                 (f"-geometry{args.dump_geometry_frames}"
                  if args.dump_geometry_frames else "") + \
                 (f"-manual-{run.name.rsplit('-', 1)[-1]}"
                  if args.manual_wait_seconds is not None else "")
        output = ROOT / f"evidence/muse-g01-appcard-approval-host{suffix}-20260928.json"
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(output), "fixture_requests": len(Fixture.requests),
                          "tool_rows": len(tool_rows),
                          "approval_requested_in_official_ledger": any(
                              row["event"]["kind"] == "approval_requested" for row in lifecycle),
                          "advertised_tools": (Fixture.requests[0]["tools"]
                                               if Fixture.requests and args.manual_wait_seconds is None else []),
                          "screenshot": report["screenshot"], "capture_error": capture_error,
                          "region_screenshot": report["region_screenshot"],
                          "geometry_path": report["geometry_path"],
                          "manual_decisions": len(manual_decisions),
                          "manual_marker_present_after": manual_marker_present_after,
                          "manual_wire_verdict": manual_wire_verdict,
                          "mcp_calls": len(mcp_calls),
                          "mcp_receipt_events": len(receipt_events),
                          "activation_code": activation_code}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
