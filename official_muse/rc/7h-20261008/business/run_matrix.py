#!/usr/bin/env python3
"""Freeze one candidate, then exercise the isolated production-function matrix."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(args):
    out = args.out.resolve()
    assert out.is_relative_to(HERE), "Evidence must stay in Business ownership"
    out.mkdir(parents=True, exist_ok=False)
    frozen = out / "frozen-bundle"
    shutil.copytree(args.source_bundle.resolve(strict=True), frozen)
    source_sha = sha(frozen / "main.splash")
    runs = []

    def run(name, probe, port, seed=None, case=None, flags=()):
        target = out / name
        command = [sys.executable, str(HERE / "run.py"),
                   "--source-bundle", str(frozen), "--host", str(args.host.resolve()),
                   "--host-cwd", str(args.host_cwd.resolve()), "--probe", str(HERE / probe),
                   "--out", str(target), "--port", str(port)]
        if seed: command += ["--seed", str(seed)]
        if case: command += ["--case", case]
        command += list(flags)
        result = subprocess.run(command, capture_output=True, text=True)
        (out / (name + ".runner.log")).write_text(result.stdout + result.stderr)
        report = target / "summary.json"
        if report.exists():
            summary = json.loads(report.read_text())
            record = {key: summary.get(key) for key in (
                "status", "checks", "passed", "failed", "error", "source_sha256",
                "host_sha256", "probe_sha256", "transport_sha256", "executed_sha256",
                "all_other_functions_byte_equal", "external_service_calls", "real_model_inference")}
            record["summary_sha256"] = sha(report)
            record["source_matches_frozen"] = summary["source_sha256"] == source_sha
        else:
            record = {"status": "HARNESS_ERROR", "error": "No summary; inspect runner log"}
        record.update(name=name, exit_code=result.returncode,
                      evidence=str(target.relative_to(HERE)))
        print(json.dumps({key: record.get(key) for key in ("name", "status", "passed", "checks", "failed")}), flush=True)
        return record

    chain = run("chain", "chain.splash", args.port_base, flags=("--require-settlement",))
    runs.append(chain)
    if chain["status"] == "DRY_RUN_PASS":
        seed = out / "chain/state"
        runs.append(run("restart", "restart.splash", args.port_base, seed))
        cases = ["ambiguous_matter", "external_version", "revoked_approval", "malformed_model",
                 "late_model", "storage_failure", "delete_receipt_failure", "delete_accept_failure",
                 "delete_unknown", "delete_unknown_still_present", "linked_memory_failure",
                 "linked_result_failure", "mail_accepted_receipt_failure"]

        # Source preparation has an official wall-clock budget. Concurrent Host
        # starts caused one observed compile timeout; do not inflate that budget.
        for case in cases:
            flags = ["--fault-storage"] if case in {
                "storage_failure", "delete_receipt_failure", "delete_accept_failure",
                "linked_memory_failure", "linked_result_failure", "mail_accepted_receipt_failure"} else []
            if case.startswith("delete_"): flags += ["--delete-reconcile"]
            if case.startswith("linked_"): flags += ["--require-settlement"]
            runs.append(run(case, "failure.splash", args.port_base, seed, case, flags))
        accepted = next(record for record in runs if record["name"] == "mail_accepted_receipt_failure")
        if accepted["status"] == "DRY_RUN_PASS":
            runs.append(run("accepted_receipt_restart", "interruption_restart.splash", args.port_base,
                            out / "mail_accepted_receipt_failure/state"))
        interrupted = run("interrupted_send", "interrupted_send.splash", args.port_base, seed)
        runs.append(interrupted)
        if interrupted["status"] == "DRY_RUN_PASS":
            runs.append(run("interruption_restart", "interruption_restart.splash", args.port_base,
                            out / "interrupted_send/state"))
    passed = all(record["status"] == "DRY_RUN_PASS" and record.get("source_matches_frozen") for record in runs)
    complete = len(runs) == 18
    aggregate = {
        "kind": "DRY_RUN_PRODUCTION_FUNCTIONS", "status": "DRY_RUN_PASS" if passed and complete else "PARTIAL",
        "candidate_source_sha256": source_sha, "runs": runs, "complete": complete,
        "checks": sum(record.get("checks") or 0 for record in runs),
        "passed": sum(record.get("passed") or 0 for record in runs),
        "external_service_calls": 0, "real_model_inference": False,
        "boundary": "Official card VM and actual jailed storage; synthetic Mail/Calendar/Model transport. Not live service, OS calendar, visual or real inference evidence.",
    }
    (out / "aggregate.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: aggregate[key] for key in ("status", "checks", "passed", "complete")}), flush=True)
    return 0 if aggregate["status"] == "DRY_RUN_PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-bundle", type=Path, required=True)
    parser.add_argument("--host", type=Path, required=True)
    parser.add_argument("--host-cwd", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port-base", type=int, default=8661)
    raise SystemExit(main(parser.parse_args()))
