#!/usr/bin/env python3
"""Actual CardHost/production functions; queued synthetic model callbacks only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CASES = ("flow", "card", "switch_early", "switch_late")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--expected-source-sha256", required=True)
    p.add_argument("--host", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--cases", nargs="+", choices=CASES, default=CASES)
    a = p.parse_args()
    source = a.source.resolve(strict=True)
    assert sha(source) == a.expected_source_sha256, "Source changed; no relabeling"
    host = a.host.resolve(strict=True)
    host_sha = sha(host)
    assert host_sha == "52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837"
    out = a.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists(), "Only fresh owned output"
    out.mkdir()
    readable = out / "readable-bundle"
    bundle_template = source.parent if (source.parent / "manifest.json").is_file() else ROOT / "official_muse/app/bundle"
    shutil.copytree(bundle_template, readable)
    (readable / "main.splash").write_bytes(source.read_bytes())
    compact = out / "compact-bundle"
    transform = subprocess.run([sys.executable, str(ROOT / "official_muse/ui_memory/compact_bundle.py"),
                                "--source", str(readable), "--out", str(compact)],
                               capture_output=True, text=True, check=True)
    compact_binding = json.loads(transform.stdout)
    (out / "compact-binding.json").write_text(json.dumps(compact_binding, indent=2) + "\n")
    frozen = (compact / "main.splash").read_text()
    os.environ["MUSE_CARD_HOST"] = str(host)
    sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
    sys.path.insert(0, str(HERE.parent))
    import regression_run
    from run_calendar_clarification import restart
    assert regression_run.existing.HOST == host
    report = {"status": "RUNNING", "readable_source_sha256": a.expected_source_sha256,
              "tested_compact_source_sha256": sha(compact / "main.splash"),
              "host_sha256": host_sha, "host_path": str(host),
              "copied_manifest_version": json.loads((readable / "manifest.json").read_text())["version"],
              "sdk_source_lock_sha256": sha(ROOT / "dependencies.lock.json"),
              "instrumentation": "Existing regression_run: mock Host transport, replace redraw/set_page/calendar_enabled/mail_redraw and copied widgets; production send/schema/history/storage unchanged.",
              "real_model": False, "real_mail": False, "real_calendar": False,
              "tokenizer_equivalence_rechecked": False, "cases": {}}
    template = (HERE / "probe.splash").read_text()
    for case in a.cases:
        case_out = out / case
        case_out.mkdir()
        probe = case_out / "probe.splash"
        text = template.replace("__CASE__", case)
        probe.write_text(text)
        try:
            first = regression_run.run_suite("mail_calendar_chain", frozen, compact,
                                             case_out / "first", 8509, probe)
            second = restart(case_out / "first", case_out) if case in ("flow", "card") and not first["failed"] else None
            result = {"status": "PASS" if not first["failed"] and
                      (second is None or not second["failed"]) else "FAIL",
                      "initial": first, "restart": second}
        except Exception as exc:
            result = {"status": "ERROR", "error": str(exc)}
        report["cases"][case] = result
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(case, result["status"], flush=True)
    report["status"] = "FIXTURE_PASS" if all(c["status"] == "PASS" for c in report["cases"].values()) else "FAIL"
    report["passed_cases"] = sum(c["status"] == "PASS" for c in report["cases"].values())
    report["passed_checks"] = sum(c.get("initial", {}).get("passed", 0) +
                                  (c.get("restart") or {}).get("passed", 0) for c in report["cases"].values())
    report["current_source_unchanged_since_freeze"] = sha(source) == a.expected_source_sha256
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return int(report["status"] != "FIXTURE_PASS")


if __name__ == "__main__":
    raise SystemExit(main())
