#!/usr/bin/env python3
"""Limited actual Memory generation/restart delta, isolated native fs; no model."""
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

CASES = ("user_entry", "runtime_entry", "scope_guards", "duplicate_guard", "forget_guards")
FILES = ("memory.json", "memory.backup.json", "memory.pre-global.json", "global-memory-settings.json")
RESTART = '''
fn metadata_restart(){
    let before=fs.read("memory.json")
    core_boot_memory() gm_boot()
    let prepared=gm_prepare()
    let checks={ready:gm_ready && core_memory_ready && gm_enabled prepared:prepared
        no_migration:fs.read("memory.json")==before && !fs.exists("memory.pre-global.json")
        loaded_exact:memory.to_json()==before.parse_json().claims.to_json()
        no_host_requests:metadata_calls.len()==0}
    if metadata_case=="forget_guards" {
        checks.deleted_still_inaccessible=!gm_entry_access(memory[0])
        checks.other_scope_still_accessible=gm_entry_access(memory[1])
    }
    fs.write("metadata-restart-probe.json",checks.to_json())
}
start_timeout(0.1,|| metadata_restart())
'''


def require_free():
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", 8509)) != 0, "Existing instance protected"


def snapshot(state):
    return {name: (state / name).read_bytes() if (state / name).exists() else None for name in FILES}


def timestamps(state):
    return {name: (state / name).stat().st_mtime_ns if (state / name).exists() else None for name in FILES}


def restart(first, out):
    require_free()
    marker = "start_timeout(0.1,|| metadata_start())\n"
    code = (first / "bundle/main.splash").read_text()
    assert code.count(marker) == 1
    bundle = out / "restart-bundle"
    shutil.copytree(first / "bundle", bundle)
    (bundle / "main.splash").write_text(code.replace(marker, RESTART))
    state = first / "state"
    jail = state / "muse-goals"
    before = snapshot(jail)
    before_times = timestamps(jail)
    env = dict(os.environ, MAKEPAD_REMOTE="8509", MAKEPAD_HIDE_WINDOWS="1")
    env.pop("MAKEPAD_FOCUS", None)
    with (out / "restart-runtime.log").open("w") as log:
        proc = subprocess.Popen([str(regression_run.existing.HOST), "--bundle", str(bundle),
                                 "--app-data", str(state), "--allow-unsigned", "--stamp", "--size", "600x700"],
                                cwd=regression_run.existing.HOST.parents[2], env=env, stdout=log, stderr=log)
        try:
            target = jail / "metadata-restart-probe.json"
            deadline = time.monotonic() + 25
            while not target.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("No restart result; original log preserved")
                time.sleep(.1)
            result = json.loads(target.read_text())
            runtime = (out / "restart-runtime.log").read_text()
            if "[E]" in runtime or "script time budget exceeded" in runtime:
                raise RuntimeError("Restart runtime error; original log preserved")
            after = snapshot(jail)
            result["independent_bytes_unchanged"] = before == after
            result["independent_mtime_unchanged"] = before_times == timestamps(jail)
            result["file_hashes"] = {name: {
                "before": hashlib.sha256(before[name]).hexdigest() if before[name] is not None else None,
                "after": hashlib.sha256(after[name]).hexdigest() if after[name] is not None else None,
                "unchanged": before[name] == after[name]} for name in FILES}
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
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=CASES)
    args = parser.parse_args()
    source_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
    assert source_hash == args.expected_source_sha256, "Unexpected source"
    out = args.out.resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    out.mkdir()
    frozen = out / "source-bundle"
    shutil.copytree(args.source.parent, frozen)
    source = (frozen / args.source.name).read_text()
    assert hashlib.sha256(source.encode()).hexdigest() == source_hash
    report = {"status": "RUNNING", "source_sha256": source_hash,
              "card_host_sha256": hashlib.sha256(regression_run.existing.HOST.read_bytes()).hexdigest(),
              "sdk_lock_sha256": hashlib.sha256((ROOT / "dependencies.lock.json").read_bytes()).hexdigest(),
              "cases": {}, "boundary": "Real CardHost/native isolated fs and production Memory functions; synthetic inputs/artifact; no model or external action"}
    for case in args.cases:
        require_free()
        case_out = out / case
        case_out.mkdir()
        probe = case_out / "probe.splash"
        probe.write_text((HERE / "memory_metadata_restart.splash").read_text().replace("__CASE__", case))
        try:
            first = regression_run.run_suite("mail_calendar_chain", source, frozen,
                                             case_out / "first", 8509, probe)
            claims = json.loads((case_out / "first/state/muse-goals/memory.json").read_text())["claims"]
            metadata_ok = bool(claims) and all(entry.get("memory_type") == "source"
                and entry.get("conversation_id") == "" and entry.get("history") == [] for entry in claims)
            first["independent_metadata_readback"] = metadata_ok
            if metadata_ok:
                first["passed"] += 1
            else:
                first["failed"].append("independent_metadata_readback")
            second = restart(case_out / "first", case_out)
            result = {"status": "PASS" if not first["failed"] and not second["failed"] else "FAIL",
                      "initial": first, "restart": second}
        except Exception as error:
            result = {"status": "ERROR", "error": str(error)}
        report["cases"][case] = result
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(case, result["status"], flush=True)
    report["status"] = "FIXTURE_PASS" if all(r["status"] == "PASS" for r in report["cases"].values()) else "FAIL"
    report["passed_cases"] = sum(r["status"] == "PASS" for r in report["cases"].values())
    report["passed_checks"] = sum(r.get("initial", {}).get("passed", 0) + r.get("restart", {}).get("passed", 0)
                                  for r in report["cases"].values())
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return int(report["status"] != "FIXTURE_PASS")


if __name__ == "__main__":
    raise SystemExit(main())
