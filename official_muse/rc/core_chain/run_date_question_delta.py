#!/usr/bin/env python3
"""Compare original and one-condition proposal only in isolated fixture copies."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import socket
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run

EXPECTED_SOURCE = "47c56065ab8be64c48734c4c2b1afdb96de1a6fb391dd360e5dd20a4b5b60966"
ORIGINAL = 'if action == "calendar_candidate" && chat_calendar_input_ambiguous(message) {'
PROPOSED = ('if action == "calendar_candidate" && (chat_calendar_input_ambiguous(message) '
            '|| (!editing && !chat_calendar_date_known(message))) {')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source", type=Path, default=ROOT / "official_muse/app/source/main.splash")
    p.add_argument("--bundle-template", type=Path, default=ROOT / "official_muse/app/bundle")
    a = p.parse_args()
    data = a.source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED_SOURCE
    source = data.decode()
    assert source.count(ORIGINAL) == 1
    proposed = source.replace(ORIGINAL, PROPOSED, 1)
    assert proposed.replace(PROPOSED, ORIGINAL, 1) == source
    host_hash = hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest()
    assert host_hash == "52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837"
    out = a.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    bundle = out / "source-bundle"
    shutil.copytree(a.bundle_template, bundle)
    (bundle / "main.splash").write_bytes(data)
    report = {"status": "RUNNING", "original_source_sha256": digest,
              "proposal_source_sha256": hashlib.sha256(proposed.encode()).hexdigest(),
              "card_host_sha256": host_hash,
              "sdk_lock_sha256": hashlib.sha256((ROOT / "dependencies.lock.json").read_bytes()).hexdigest(),
              "fixture_only_suggestion": {"original_condition": ORIGINAL, "proposed_condition": PROPOSED},
              "boundary": "Actual isolated CardHost/production functions with synthetic input/payload; one proposed condition changed only in copied fixture source. No model or Host requests, UI suppressed, no product/SDK/Git edits.",
              "variants": {}}
    for label, text in [("original", source), ("proposal", proposed)]:
        with socket.socket() as sock:
            assert sock.connect_ex(("127.0.0.1", 8509)) != 0, "Existing process protected"
        try:
            result = regression_run.run_suite("mail_calendar_chain", text, bundle, out / label,
                                              8509, HERE / "date_question_delta.splash")
            report["variants"][label] = result
        except Exception as error:
            report["variants"][label] = {"status": "ERROR", "error": str(error)}
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(label, json.dumps(report["variants"][label], ensure_ascii=False), flush=True)
    original = report["variants"]["original"]
    suggestion = report["variants"]["proposal"]
    expected_failures = {"question:which_day_evening", "question:when_meet", "question:evening_range_without_day"}
    passed = set(original.get("failed", [])) == expected_failures and not suggestion.get("failed") and "passed" in suggestion
    report["status"] = "PROPOSAL_FIXTURE_PASS_ROOT_DECISION_REQUIRED" if passed else "FAIL"
    report["baseline_expected_failures_reproduced"] = set(original.get("failed", [])) == expected_failures
    report["product_modified"] = False
    report["original_source_still_unchanged"] = hashlib.sha256(a.source.read_bytes()).hexdigest() == digest
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return int(not passed)


if __name__ == "__main__":
    raise SystemExit(main())
