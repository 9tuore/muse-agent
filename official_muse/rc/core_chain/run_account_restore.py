#!/usr/bin/env python3
"""Minimal actual production mail_select_account replay, synthetic transport."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    original = args.source.read_text()
    prior = args.baseline.read_text()
    function = "mail_select_account"
    same_rest = (regression_run.existing.replace_function(original, function, "") ==
                 regression_run.existing.replace_function(prior, function, ""))
    (out / "delta.json").write_text(json.dumps({
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "baseline_source_sha256": hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        "only_changed_function": function if same_rest else None,
        "rest_byte_identical": same_rest,
    }, indent=2) + "\n")
    assert same_rest, "Source changes extend beyond mail_select_account; do not reuse baseline proof"
    result = regression_run.run_suite("mail_calendar_chain", original, args.source.parent,
                                      out / "fixture", 8509, HERE / "account_restore.splash")
    report = {
        "status": "FIXTURE_PASS" if not result["failed"] else "FAIL",
        "cases": 8, "checks": result, "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "host_sha256": hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest(),
        "sdk_lock_sha256": hashlib.sha256((ROOT / "dependencies.lock.json").read_bytes()).hexdigest(),
        "baseline_proof": "V8 28+4 / 25+6 / 20 faults+3 restarts; unchanged code only",
        "changed_function": function, "rest_byte_identical": same_rest,
        "pending_model_guard": "mail_model_pending (mail draft generation)",
        "boundary": "Synthetic account/Host callbacks, actual production function and isolated card-host storage; no live-account action",
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return int(bool(result["failed"]))


if __name__ == "__main__":
    raise SystemExit(main())
