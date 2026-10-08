#!/usr/bin/env python3
"""Production Splash functions in official card-host, isolated synthetic services.

This runner never dispatches Mail, Calendar or Model Host services. It preserves
production state-machine functions and uses actual jailed fs/VM/timers. A restart
is a new process with a copied synthetic jail, not a call to boot in one process.
"""
import argparse
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "official_muse/round2/tests"))
from runtime_probe import replace_function, WIDGET
sys.path.insert(0, str(ROOT / "official_muse/prelim/tests/calendar_sync"))
from run import functions_in


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(args):
    out = args.out.resolve()
    assert out.is_relative_to(HERE), "Keep isolated evidence inside Business ownership"
    assert args.probe.resolve().is_relative_to(HERE)
    host = args.host.resolve(strict=True)
    host_cwd = args.host_cwd.resolve(strict=True)
    assert not host.is_relative_to(Path("/Applications")), "Installed baseline is protected"
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", args.port)) != 0, "Existing port owner untouched"
    out.mkdir(parents=True, exist_ok=False)
    snapshot = out / "source-bundle"
    shutil.copytree(args.source_bundle.resolve(), snapshot)
    source = (snapshot / "main.splash").read_text()
    bundle = out / "bundle"
    shutil.copytree(snapshot, bundle)
    marker = re.search(r"^start_timeout\(0\.05,\s*\|\|\s*boot\(\)\)", source, re.M)
    assert marker, "Verified production startup marker required"
    prefix = source[:marker.start()]
    original = functions_in(prefix)
    prefix = prefix.replace("host.request(", "business_request(")
    substitutions = {
        "redraw": "fn redraw(){}",
        "set_page": "fn set_page(next){page=next}",
        "mail_redraw": "fn mail_redraw(){}",
        "calendar_enabled": "fn calendar_enabled(){return true}",
        "mail_enabled": "fn mail_enabled(){return true}",
    }
    if args.fault_storage:
        body = original["storage_write"].replace(
            "return try { fs.write(path,data) }", 
            'if be_fault_path==path {be_fault_hits=be_fault_hits+1 return "synthetic_storage_failure"}\n'
            "    return try { fs.write(path,data) }")
        assert body != original["storage_write"]
        substitutions["storage_write"] = body
    for name, body in substitutions.items():
        prefix = replace_function(prefix, name, body)
    retained = functions_in(prefix)
    assert original.keys() == retained.keys()
    changed = [name for name in original
               if original[name] != retained[name].replace("business_request(", "host.request(")]
    assert sorted(changed) == sorted(substitutions), changed
    widget = WIDGET.replace('    Label{text:', '''    mail_to := TextInput{width: Fill}
    mail_subject := TextInput{width: Fill}
    mail_body := TextInput{width: Fill}
    mail_intent := TextInput{width: Fill}
    mail_test_id := TextInput{width: Fill}
    session_focus_project := TextInput{width: Fill}
    session_focus_owner := TextInput{width: Fill}
    calendar_range_start := TextInput{width: Fill}
    calendar_range_end := TextInput{width: Fill}
    calendar_panel := View{width: Fill height: Fit on_render: || {}}
    Label{text:''', 1)
    manifest = json.loads((bundle / "manifest.json").read_text())
    manifest["integrity"].pop("signature", None)
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    common = HERE / "transport.splash"
    probe_text = args.probe.read_text().replace('"__CASE__"', json.dumps(args.case))
    instrumented = prefix + common.read_text() + probe_text + widget
    assert "host.request(" not in instrumented, "No real service dispatch can remain"
    (bundle / "main.splash").write_text(instrumented)
    state = out / "state"
    seed_hashes = {}
    if args.seed:
        seed = args.seed.resolve(strict=True)
        assert seed.is_relative_to(HERE) and seed.is_dir()
        for path in seed.rglob("*"):
            assert not path.is_symlink()
            if path.is_file(): seed_hashes[str(path.relative_to(seed))] = sha(path)
        shutil.copytree(seed, state)
        (state / "muse-goals/probe.json").unlink(missing_ok=True)
    home = out / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home), MAKEPAD_REMOTE=str(args.port),
               MAKEPAD_HIDE_WINDOWS="1", PYTHONDONTWRITEBYTECODE="1")
    for name in ("MAKEPAD_FOCUS", "OCTOSENSE_HOME", "OCTOSENSE_APP_DATA", "OCTOS_APP_CORE_DIR"):
        env.pop(name, None)
    summary = {
        "kind": "DRY_RUN_PRODUCTION_FUNCTIONS", "status": "RUNNING",
        "source_sha256": sha(snapshot / "main.splash"), "host_sha256": sha(host),
        "probe_sha256": sha(args.probe), "transport_sha256": sha(common), "executed_sha256": sha(bundle / "main.splash"),
        "production_functions": len(original), "retained_functions": len(retained),
        "substitutions": sorted(changed), "all_other_functions_byte_equal": True,
        "storage_fault_injection": args.fault_storage, "case": args.case,
        "external_service_calls": 0, "real_model_inference": False,
        "seed_hashes": seed_hashes, "budget": "Unchanged official VM/script budgets",
        "boundary": "Synthetic Host responses and minimal widgets; real official VM, timers and jailed storage. No OS EventKit, SMTP delivery or paid model evidence.",
    }
    proc = None
    log_path = out / "runtime.log"
    try:
        with log_path.open("w") as log:
            proc = subprocess.Popen([str(host), "--bundle", str(bundle), "--app-data", str(state),
                                     "--allow-unsigned", "--stamp", "--size", "600x700"],
                                    cwd=host_cwd, env=env, stdout=log, stderr=log)
            report = state / "muse-goals/probe.json"
            deadline = time.monotonic() + args.timeout
            while not report.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("No fresh report; inspect retained runtime.log/progress/state")
                time.sleep(.1)
            time.sleep(.2)
            result = json.loads(report.read_text())
            errors = [line for line in log_path.read_text().splitlines()
                      if "[E]" in line or "script time budget exceeded" in line]
            checks = {name: value for name, value in result.items() if isinstance(value, bool)}
            failed = [name for name, value in checks.items() if not value]
            if errors: failed.append("runtime_error")
            if result.get("forbidden_calls"): failed.append("forbidden_calls")
            summary.update(status="DRY_RUN_PASS" if not failed else "FAIL",
                           checks=len(checks), passed=sum(checks.values()), failed=failed,
                           result=result, runtime_errors=errors)
    except Exception as error:
        summary.update(status="ERROR", error=str(error))
    finally:
        if proc is not None:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
    summary["runtime_log_sha256"] = sha(log_path)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({name: summary.get(name) for name in ("status", "checks", "passed", "failed", "error")}, ensure_ascii=False))
    return 0 if summary["status"] == "DRY_RUN_PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-bundle", type=Path, required=True)
    parser.add_argument("--host", type=Path, required=True)
    parser.add_argument("--host-cwd", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8661)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--case", default="default")
    parser.add_argument("--fault-storage", action="store_true",
                        help="Allow explicit one-path failure before real jailed fs.write")
    raise SystemExit(execute(parser.parse_args()))
