#!/usr/bin/env python3
"""Manifest-only CardHost fixture: header merge proposal, no asset copying."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run

OLD = '''    if editing && action == "mail_compose" && chat_mail_reference(message) {
        payload.to = request.candidate_payload.parse_json().to
    }'''
NEW = '''    if editing && action == "mail_compose" {
        if regex("(吗|么|[?？])$","").test(message.trim()) { return false }
        let original_mail = request.candidate_payload.parse_json()
        if !chat_mail_field_edit_requested(message,"to") { payload.to = original_mail.to }
        if !chat_mail_field_edit_requested(message,"subject") { payload.subject = original_mail.subject }
    }'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=ROOT / "official_muse/app/source/main.splash")
    p.add_argument("--expected-source-sha256", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    source = a.source.read_text()
    sha = hashlib.sha256(a.source.read_bytes()).hexdigest()
    assert sha == a.expected_source_sha256
    assert source.count(OLD) == 1
    helper = (HERE / "mail_header_proposal.splash").read_text()
    assert source.count("fn chat_add_proposal(") == 1
    suggestion = source.replace("fn chat_add_proposal(", helper + "\nfn chat_add_proposal(", 1).replace(OLD, NEW, 1)
    out = a.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    # Only the actual manifest and one frozen text source; no image/resource/build copies.
    thin = out / "thin-template"
    thin.mkdir()
    (thin / "manifest.json").write_bytes((ROOT / "official_muse/app/bundle/manifest.json").read_bytes())
    (out / "original-source.splash").write_text(source)
    report = {"status": "RUNNING", "original_source_sha256": sha,
              "proposal_source_sha256": hashlib.sha256(suggestion.encode()).hexdigest(),
              "card_host_sha256": hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest(),
              "variants": {}, "boundary": "Actual production merge/guard functions with synthetic output, UI suppressed, native isolated fs. One fixture-only helper/merge block; no assets copied, build, model, mail/system action or product/SDK/Git mutation."}
    assert report["card_host_sha256"] == "52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837"
    for name, text in [("original", source), ("proposal", suggestion)]:
        with socket.socket() as sock:
            assert sock.connect_ex(("127.0.0.1", 8509)) != 0, "Existing instance protected"
        try:
            report["variants"][name] = regression_run.run_suite("mail_calendar_chain", text, thin,
                out / name, 8509, HERE / "mail_header_delta.splash")
        except Exception as error:
            report["variants"][name] = {"status": "ERROR", "error": str(error)}
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(name, json.dumps(report["variants"][name]), flush=True)
    proposal = report["variants"]["proposal"]
    report["status"] = "PROPOSAL_FIXTURE_PASS_ROOT_REVIEW" if "passed" in proposal and not proposal["failed"] else "FAIL"
    report["known_preserved_keep_prefix_limit"] = "A leading 不要改主题 compound request remains rejected by existing whole-request keep guard. Plain 不改主题 permits body update with headers preserved. No keep routing rule changed."
    report["local_file_bytes"] = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return int(report["status"] == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
