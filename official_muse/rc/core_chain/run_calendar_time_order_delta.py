#!/usr/bin/env python3
"""One-function order proposal, actual CardHost, manifest-only isolated copies."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import socket
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "official_muse/app/source/main.splash")
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == args.expected_source_sha256
    source = raw.decode()
    replacement = (HERE / "calendar_time_order_proposal.splash").read_text()
    replacement = replacement[replacement.index("fn chat_candidate_input_error("):].strip()
    proposed = regression_run.existing.replace_function(source, "chat_candidate_input_error", replacement)
    assert regression_run.existing.replace_function(source, "chat_candidate_input_error", "") == regression_run.existing.replace_function(proposed, "chat_candidate_input_error", "")
    out = args.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    thin = out / "thin-template"
    thin.mkdir()
    (thin / "manifest.json").write_bytes((ROOT / "official_muse/app/bundle/manifest.json").read_bytes())
    (out / "original-source.splash").write_bytes(raw)
    (out / "proposal.patch").write_text("".join(difflib.unified_diff(source.splitlines(True), proposed.splitlines(True), fromfile="original/main.splash", tofile="proposal/main.splash")))
    host_hash = hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest()
    assert host_hash == "52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837"
    report = {"status": "RUNNING", "original_source_sha256": digest,
              "proposal_source_sha256": hashlib.sha256(proposed.encode()).hexdigest(),
              "card_host_sha256": host_hash, "sdk_lock_sha256": hashlib.sha256((ROOT / "dependencies.lock.json").read_bytes()).hexdigest(),
              "all_source_outside_one_function_identical": True, "variants": {},
              "boundary": "Production validation/candidate/storage functions in actual isolated CardHost; synthetic input/payload, no model or Host requests; one fixture-only function order/text proposal; no product/SDK/Git change or resource/build copies."}
    for label, text in [("original", source), ("proposal", proposed)]:
        with socket.socket() as sock:
            assert sock.connect_ex(("127.0.0.1", 8509)) != 0, "Existing process protected"
        try:
            result = regression_run.run_suite("mail_calendar_chain", text, thin,
                out / label, 8509, HERE / "calendar_time_order_delta.splash")
            jail = out / label / "state/muse-goals"
            disk = json.loads((jail / "chat-sessions.json").read_text())
            facts = {"independent_python_chat_schema": disk["schema"] == 1,
                     "independent_python_no_system_artifact": not (jail / "calendar-state.json").exists()}
            result["disk_checks"] = facts
            result["passed"] += sum(facts.values())
            result["failed"] += [k for k, v in facts.items() if not v]
            report["variants"][label] = result
        except Exception as error:
            report["variants"][label] = {"status": "ERROR", "error": str(error)}
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(label, json.dumps(report["variants"][label], ensure_ascii=False), flush=True)
    controls = ["mail_valid", "mail_invalid", "goal_valid", "goal_invalid"]
    maps = {}
    for label in ["original", "proposal"]:
        path = out / label / "report.json"
        if path.exists():
            maps[label] = {d["id"]: d["actual_error"] for d in json.loads(path.read_text())["details"] if d["id"] in controls}
    report["mail_goal_outputs_identical"] = len(maps) == 2 and maps["original"] == maps["proposal"]
    baseline = report["variants"]["original"]
    suggestion = report["variants"]["proposal"]
    wanted = {"known_date_empty_slot:wording", "known_date_reverse_slot:wording", "known_date_guessed_slot:wording"}
    report["baseline_three_order_failures_reproduced"] = set(baseline.get("failed", [])) == wanted
    report["status"] = "PROPOSAL_FIXTURE_PASS_ROOT_REVIEW" if "passed" in suggestion and not suggestion["failed"] and report["mail_goal_outputs_identical"] and report["baseline_three_order_failures_reproduced"] else "FAIL"
    report["local_file_bytes"] = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return int(report["status"] == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
