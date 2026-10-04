#!/usr/bin/env python3
"""Limited production chat_apply_proposal goal_plan delta; no actual model/account."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run
CASES = ("missing_focus", "blank_source", "invalid_items", "write_failure",
         "success_duplicate", "project_scope", "owner_scope", "dismissed", "stale_memory")


def run_case(case, source, template, out):
    with socket.socket() as port:
        assert port.connect_ex(("127.0.0.1", 8509)) != 0, "Existing port instance is protected"
    probe = out / "probe.splash"
    probe.parent.mkdir()
    probe.write_text((HERE / "goal_card_consumption.splash").read_text().replace("__CASE__", case))
    # The existing runner executes synchronously. A thread only waits for the
    # synthetic disk-fault handshake; it never performs a product operation.
    import threading
    fault = {}
    stopped = threading.Event()
    def inject():
        if case != "write_failure":
            return
        jail = out / "fixture/state/muse-goals"
        deadline = time.monotonic() + 25
        while not stopped.is_set() and time.monotonic() < deadline:
            if (jail / "goal-card-fault-ready.json").exists():
                target = jail / "goals.json"
                assert not target.exists(), "Fresh fault path was unexpectedly populated"
                target.mkdir()
                fault.update(kind="actual_directory_collision", target="goals.json")
                (jail / "goal-card-fault-go.json").write_text("{}")
                return
            time.sleep(.03)
    worker = threading.Thread(target=inject, daemon=True)
    worker.start()
    try:
        result = regression_run.run_suite("mail_calendar_chain", source, template,
                                          out / "fixture", 8509, probe)
        return {"status": "PASS" if not result["failed"] else "FAIL", "checks": result, "disk_fault": fault}
    except Exception as error:
        return {"status": "ERROR", "error": str(error), "disk_fault": fault}
    finally:
        stopped.set()
        worker.join(timeout=1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    out = a.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    source = a.source.read_text()
    report = {"status": "RUNNING", "source_sha256": hashlib.sha256(a.source.read_bytes()).hexdigest(),
              "card_host_sha256": hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest(),
              "sdk_lock_sha256": hashlib.sha256((ROOT / "dependencies.lock.json").read_bytes()).hexdigest(),
              "tested_function": "chat_apply_proposal goal_plan branch and actual make_plan/core_add_goal",
              "cases": {}, "boundary": "Real isolated card-host/production functions, synthetic candidate; no model/Host/system action",
              "expiry_semantics": "Valid schema has candidate/opened/dismissed states; tests cover dismissed and stale Memory refs. No separate Goal-card TTL is asserted."}
    for case in CASES:
        report["cases"][case] = run_case(case, source, a.source.parent, out / case)
        (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        print(case, report["cases"][case]["status"], flush=True)
    report["status"] = "FIXTURE_PASS" if all(v["status"] == "PASS" for v in report["cases"].values()) else "FAIL"
    report["passed_cases"] = sum(v["status"] == "PASS" for v in report["cases"].values())
    report["passed_checks"] = sum(v.get("checks", {}).get("passed", 0) for v in report["cases"].values())
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return int(report["status"] != "FIXTURE_PASS")


if __name__ == "__main__":
    raise SystemExit(main())
