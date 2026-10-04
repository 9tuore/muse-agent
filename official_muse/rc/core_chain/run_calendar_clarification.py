#!/usr/bin/env python3
"""Related production Calendar clarification checks, synthetic model responses."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run

DATE_CASES = ("date_over_full", "date_gaitian_full", "date_only_duration", "date_only_iso", "date_reambiguous",
              "date_time_only", "date_relative_change", "date_other_owner", "date_other_project",
              "date_expired_ref", "date_illegal_time")
BASE_CASES = ("flow", "waiting_restore", "malformed_meta", "context_guards", "error_types", "cancel_new_intents")
CASES = BASE_CASES + DATE_CASES
RESTART_CASES = ("flow", "waiting_restore", "malformed_meta", "date_gaitian_full", "date_only_duration")


def free_port():
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", 8509)) != 0, "Existing process protected"


def restart(first, out):
    free_port()
    code = (first / "bundle/main.splash").read_text()
    assert code.count('let cc_phase="first"') == 1
    bundle = out / "restart-bundle"
    shutil.copytree(first / "bundle", bundle)
    (bundle / "main.splash").write_text(code.replace('let cc_phase="first"', 'let cc_phase="restart"'))
    state = first / "state"
    target = state / "muse-goals/probe.json"
    target.unlink()
    env = dict(os.environ, MAKEPAD_REMOTE="8509", MAKEPAD_HIDE_WINDOWS="1")
    env.pop("MAKEPAD_FOCUS", None)
    with (out / "restart-runtime.log").open("w") as log:
        proc = subprocess.Popen([str(regression_run.existing.HOST), "--bundle", str(bundle),
                                 "--app-data", str(state), "--allow-unsigned", "--stamp", "--size", "600x700"],
                                cwd=regression_run.existing.HOST.parents[2], env=env, stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 25
            while not target.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("No fresh-process result; log preserved")
                time.sleep(.1)
            result = json.loads(target.read_text())
            runtime = (out / "restart-runtime.log").read_text()
            if "[E]" in runtime or "script time budget exceeded" in runtime:
                raise RuntimeError("Restart runtime error; original log preserved")
            result["failed"] = [k for k, v in result.items() if isinstance(v, bool) and not v]
            result["passed"] = sum(isinstance(v, bool) and v for v in result.values())
            (out / "restart-report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            return result
        finally:
            try:
                urlopen("http://127.0.0.1:8509/quit", timeout=2).read()
            except OSError:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--bundle-template", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=BASE_CASES)
    args = parser.parse_args()
    data = args.source.read_bytes()
    source_hash = hashlib.sha256(data).hexdigest()
    assert source_hash == args.expected_source_sha256, "Source changed; not tested"
    assert (args.bundle_template / "manifest.json").is_file()
    host_hash = hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest()
    assert host_hash == "52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837"
    out = args.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    snapshot = out / "source-bundle"
    shutil.copytree(args.bundle_template, snapshot)
    (snapshot / "main.splash").write_bytes(data)
    report = {"status": "RUNNING", "source_sha256": source_hash, "card_host_sha256": host_hash,
              "sdk_lock_sha256": hashlib.sha256((ROOT / "dependencies.lock.json").read_bytes()).hexdigest(),
              "cases": {}, "boundary": "Actual CardHost/production send, context, schema and storage; synthetic queued model responses; UI rendering replaced; no real model or system action"}
    template = (HERE / "calendar_clarification.splash").read_text()
    template = template.replace("start_timeout(0.1,|| cc_probe())", (HERE / "calendar_date_delta.splash").read_text()
                                + "\nstart_timeout(0.1,|| cc_probe())")
    bound = 2400 - len(("\n用户补充：" + "15:00-16:00").encode())
    for case in args.cases:
        free_port()
        case_out = out / case
        case_out.mkdir()
        probe = case_out / "probe.splash"
        text = template.replace("__CASE__", case)
        for marker, value in [("__OVERLONG_INPUT__", "x" * 2401), ("__BOUND_INPUT__", "x" * bound),
                              ("__BOUND_OVER_INPUT__", "x" * (bound + 1))]:
            text = text.replace(marker, json.dumps(value))
        probe.write_text(text)
        try:
            first = regression_run.run_suite("mail_calendar_chain", data.decode(), snapshot,
                                             case_out / "first", 8509, probe)
            second = restart(case_out / "first", case_out) if case in RESTART_CASES else None
            result = {"status": "PASS" if not first["failed"] and (second is None or not second["failed"]) else "FAIL",
                      "initial": first, "restart": second}
        except Exception as error:
            result = {"status": "ERROR", "error": str(error)}
        report["cases"][case] = result
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(case, result["status"], flush=True)
    report["status"] = "FIXTURE_PASS" if all(c["status"] == "PASS" for c in report["cases"].values()) else "FAIL"
    report["passed_cases"] = sum(c["status"] == "PASS" for c in report["cases"].values())
    report["passed_checks"] = sum(c.get("initial", {}).get("passed", 0) + (c.get("restart") or {}).get("passed", 0)
                                  for c in report["cases"].values())
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return int(report["status"] != "FIXTURE_PASS")


if __name__ == "__main__":
    raise SystemExit(main())
