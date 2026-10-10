#!/usr/bin/env python3
"""Two reference-VM processes, one synthetic jail; never a live Calendar claim."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "official_muse/round2/tests"))
from runtime_probe import replace_function, WIDGET
sys.path.insert(0, str(ROOT / "official_muse/prelim/tests/calendar_sync"))
from run import functions_in


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", type=Path, required=True)
    parser.add_argument("--host-cwd", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--probe", type=Path, default=ROOT / "official_muse/semifinal/stability_integration/unknown_restart_proposal.splash")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    host = args.host.resolve(strict=True)
    source_path = args.source.resolve(strict=True)
    out = args.out.resolve()
    if not out.is_relative_to(ROOT / "build") or out.exists():
        raise ValueError("Use a new worktree build directory; existing evidence stays intact")
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", args.port)) == 0:
            raise RuntimeError("Port occupied; existing process untouched")
    out.mkdir(parents=True)
    bundle = out / "bundle"
    input_bundle = args.bundle.resolve(strict=True)
    input_manifest_sha256 = sha(input_bundle / "manifest.json")
    shutil.copytree(input_bundle, bundle)
    manifest = json.loads((bundle / "manifest.json").read_text())
    manifest["integrity"] = {}
    (bundle / "manifest.json").write_text(json.dumps(manifest) + "\n")
    source = source_path.read_text()
    marker = re.search(r"^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)", source, re.M)
    if marker is None:
        raise ValueError("Production boot marker missing")
    prefix = source[:marker.start()]
    before = functions_in(prefix)
    prefix = prefix.replace("host.request(", "fixture_request(")
    for name, body in {"redraw": "fn redraw(){}", "set_page": "fn set_page(next){page=next}"}.items():
        prefix = replace_function(prefix, name, body)
    after = functions_in(prefix)
    changed = [name for name in before if before[name] != after[name].replace("fixture_request(", "host.request(")]
    if sorted(changed) != ["redraw", "set_page"]:
        raise ValueError("Unexpected production-function substitution")
    probe = args.probe.resolve(strict=True)
    transport = '''\nlet fixture_calls = []
fn fixture_request(service,payload,callback){
    fixture_calls.push({service:service payload:payload})
    callback({is_ok:false error:"Synthetic restart test forbids external operations"})
}\n'''
    (bundle / "main.splash").write_text(prefix + transport + probe.read_text() + WIDGET)
    state, home = out / "state", out / "home"
    home.mkdir()
    core = home / "kernel/.octos"
    core.mkdir(parents=True)
    env = dict(os.environ, MAKEPAD_REMOTE=str(args.port), MAKEPAD_HIDE_WINDOWS="1",
               OCTOSENSE_HOME=str(home), OCTOSENSE_APP_DATA=str(state), OCTOS_APP_CORE_DIR=str(core))
    env.pop("MAKEPAD_FOCUS", None)
    report = {"kind": "TWO_PROCESS_SYNTHETIC_REFERENCE_VM_RECOVERY", "status": "ERROR",
              "source_sha256": sha(source_path), "host_sha256": sha(host), "probe_sha256": sha(probe),
              "runner_sha256": sha(Path(__file__)), "executed_sha256": sha(bundle / "main.splash"),
              "probe_path": str(probe.relative_to(ROOT)),
              "input_manifest_sha256": input_manifest_sha256,
              "fixture_manifest_not_candidate_admission": True,
              "fixture_manifest_host_api": manifest.get("host_api", {}),
              "production_substitutions": changed, "calendar_enabled_unmodified": True,
              "live_mail": False, "live_calendar": False, "native_consent": False, "phases": [],
              "started_at": datetime.datetime.now().astimezone().isoformat()}
    try:
        for phase in (1, 2):
            output = state / "muse-goals/probe.json"
            if output.exists():
                output.rename(out / "phase1-probe.json")
            log_path = out / ("phase" + str(phase) + ".log")
            with log_path.open("wb") as log:
                proc = subprocess.Popen([str(host), "--bundle", str(bundle), "--app-data", str(state),
                                         "--allow-unsigned", "--stamp", "--size", "600x700"],
                                        cwd=args.host_cwd.resolve(strict=True), env=env, stdout=log, stderr=log)
                entry = {"phase": phase, "pid": proc.pid}
                report["phases"].append(entry)
                try:
                    deadline = time.monotonic() + 30
                    while not output.exists():
                        if proc.poll() is not None or time.monotonic() > deadline:
                            raise RuntimeError("No fresh phase report; original log and jail retained")
                        time.sleep(.1)
                    time.sleep(.1)
                    data = json.loads(output.read_text())
                    shutil.copy2(output, out / ("phase" + str(phase) + "-result.json"))
                    errors = [line for line in log_path.read_text().splitlines()
                              if "[E]" in line or "script time budget exceeded" in line]
                    entry.update(result=data, runtime_errors=errors)
                    if errors or data.get("forbidden_calls") or data.get("zero_transport") is not True:
                        raise RuntimeError("Runtime error or forbidden transport observed")
                finally:
                    entry["shutdown"] = "remote_quit"
                    try:
                        urlopen("http://127.0.0.1:" + str(args.port) + "/quit", timeout=2).read()
                    except OSError:
                        entry["shutdown"] = "terminate"
                        proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        entry["shutdown"] = "kill"
                        proc.kill()
                        proc.wait()
                    errors = [line for line in log_path.read_text().splitlines()
                              if "[E]" in line or "script time budget exceeded" in line]
                    entry.update(exit=proc.returncode, runtime_errors=errors, log_sha256=sha(log_path))
            report["processes_distinct"] = len({row["pid"] for row in report["phases"]}) == len(report["phases"])
        failed = []
        required = {
            1: ["boot_ready", "verified_history_available", "goal_saved", "run_saved", "action_saved",
                "link_saved", "persisted_in_flight", "zero_transport"],
            2: ["boot_ready", "phase_marker_valid", "original_records_exist", "action_unknown", "link_unknown",
                "action_identity_payload_retained", "link_identity_payload_retained", "verified_history_available",
                "verified_history_retained", "same_request_rejected", "same_payload_calendar_guard",
                "rejected_attempt_no_journal_change", "zero_transport"],
        }
        for row in report["phases"]:
            failed.extend("phase" + str(row["phase"]) + ":" + key for key in required[row["phase"]]
                          if row["result"].get(key) is not True)
            if row["runtime_errors"]:
                failed.append("phase" + str(row["phase"]) + ":runtime_errors")
            if row["exit"] != 0 or row["shutdown"] != "remote_quit":
                failed.append("phase" + str(row["phase"]) + ":unclean_exit")
        if not report["processes_distinct"]:
            failed.append("processes_distinct")
        report["failed"] = failed
        missing_history = {"phase1:verified_history_available", "phase2:verified_history_available",
                           "phase2:verified_history_retained"}
        report["unknown_recovery_checks_pass"] = not (set(failed) - missing_history)
        report["status"] = ("FIXTURE_PASS" if not failed else "PARTIAL_MISSING_VERIFIED_HISTORY"
                            if report["unknown_recovery_checks_pass"] else "FAIL")
    except Exception as error:
        report["error"] = str(error)
    report["finished_at"] = datetime.datetime.now().astimezone().isoformat()
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: report.get(key) for key in ("status", "failed", "error", "processes_distinct")}, ensure_ascii=False))
    return 0 if report["status"] == "FIXTURE_PASS" else 2 if report["status"] == "PARTIAL_MISSING_VERIFIED_HISTORY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
