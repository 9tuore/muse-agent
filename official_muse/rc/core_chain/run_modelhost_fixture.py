#!/usr/bin/env python3
"""Run real official ModelHost against a loopback OpenAI wire fixture.

This is LOCAL_MODEL_ONLY_SYNTHETIC transport verification, not model inference.
Requires a fresh Root-prepared candidate with a newly built RC Host.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "official_muse/phase2/tests"))
from remote import Remote
from modelhost_fixture_backend import SCENARIOS, ScenarioBackend

EXPECT = {
    "bad_then_good": {"posts": 2, "state": "success", "format": 1, "retry": 1, "final": 0},
    "bad_twice": {"posts": 2, "state": "error", "format": 2, "retry": 1, "final": 1},
    "refused": {"posts": 1, "state": "error", "format": 0, "retry": 0, "final": 1},
    "truncated": {"posts": 1, "state": "error", "format": 0, "retry": 0, "final": 1},
}


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read(path: Path):
    return json.loads(path.read_text())


def wait_for(check, seconds=60):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(.2)
    raise TimeoutError("Expected isolated Shell state did not arrive")


def port_free(port):
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


def wait_remote(remote, key, seconds):
    # Read-only readiness probes may precede the Shell's port bind. Never
    # retry a click/send to compensate for this startup connection race.
    def ready():
        try:
            return remote.find(key)
        except (OSError, AssertionError):
            return None
    return wait_for(ready, seconds)


def log_events(text):
    names = ("MODEL_FORMAT_ERROR", "MODEL_RETRY", "MODEL_FINAL_FAILURE")
    return {name: sum(name in line and "app=muse-goals" in line for line in text.splitlines())
            for name in names}


def preflight(candidate: Path, expected_source: str, expected_host: str):
    allowed = ROOT / "official_muse/app/build/ui-memory-20261003"
    assert candidate.is_relative_to(allowed), "Use a new isolated Root-prepared candidate"
    meta = read(candidate / "candidate.json")
    assert meta["profile_kind"] == "LOCAL_MODEL_ONLY_SYNTHETIC"
    assert meta["source_sha256"] == expected_source
    assert meta["host_sha256"] == expected_host
    private = candidate / "private"
    assert private.is_dir() and private.resolve().is_relative_to(candidate)
    jail = private / "apps/muse-goals"
    assert digest(jail / "bundle/main.splash") == expected_source
    profile = read(private / "home/octos-home/.octos/profiles/_main.json")
    llm = profile["config"]["llm"]
    primary = llm["primary"]
    assert primary == {"family_id": "local", "model_id": "local-default",
                       "route": {"base_url": "http://127.0.0.1:8879/v1", "api_type": "openai"}}, "Use only the generated key-free loopback primary"
    assert llm["fallbacks"] == [] and profile["config"].get("env_vars", {}) == {}
    host_app = Path(meta["host_app_path"]).resolve()
    assert not host_app.is_relative_to(Path("/Applications")), "Stable installed app is protected"
    binary = host_app / "Contents/MacOS/octosense"
    assert digest(binary) == meta["host_sha256"]
    assert not (private / "apps/.host/mail").exists(), "No Mail account state allowed"
    assert not (jail / "chat-sessions.json").exists(), "Candidate must be fresh"
    assert port_free(8879) and port_free(8490), "Reserved fixture/Shell port is occupied"
    return meta, private, jail, binary


def verify_anchor(candidate: Path, hub: Path, expected_hub: str, anchor: str, out: Path):
    """Verify this mirror with the controller's trusted public anchor, no keys."""
    assert digest(hub) == expected_hub, "Hub CLI differs from controller inventory"
    catalog = candidate / "mirror/catalog.json"
    assert catalog.is_file(), "Candidate catalog is missing"
    result = subprocess.run([str(hub), "verify", str(catalog), "--anchor", anchor],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=30)
    (out / "hub-verify.txt").write_text(result.stdout)
    assert result.returncode == 0, "Actual candidate catalog/anchor verification failed; inspect hub-verify.txt"
    return {"hub_cli_sha256": expected_hub, "catalog_sha256": digest(catalog),
            "anchor": anchor, "verify_exit_code": result.returncode,
            "trust_basis": "Controller supplied public trust anchor; not derived from untrusted catalog"}


def selected(jail: Path):
    state = read(jail / "chat-sessions.json")
    return next(session for session in state["sessions"] if session["id"] == state["selected_id"])


def forbidden_actions(jail: Path):
    state_path = jail / "goals.json"
    if not state_path.exists():
        return []
    actions = read(state_path).get("actions", [])
    return [a.get("service") for a in actions if a.get("service") in
            ("mail.send", "mail.delete", "calendar.create", "calendar.update", "calendar.delete")]


def limits(ledger: Path):
    return read(ledger).get("limits", {}) if ledger.exists() else {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-host-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--hub-anchor", required=True, help="Explicit Root-verified anchor for this candidate mirror")
    parser.add_argument("--hub-cli", type=Path, required=True, help="Controller-inventoried local Hub executable")
    parser.add_argument("--expected-hub-sha256", required=True)
    parser.add_argument("--preflight-only", action="store_true", help="Verify candidate and catalog only; do not start Shell or backend")
    args = parser.parse_args()
    assert len(args.hub_anchor) == 64 and all(c in "0123456789abcdef" for c in args.hub_anchor), "Expected verified 32-byte anchor hex"
    candidate = args.candidate.resolve()
    out = args.out.resolve()
    assert out.is_relative_to(HERE), "Keep A2 evidence in rc/core_chain"
    assert all(len(value) == 64 and all(c in "0123456789abcdef" for c in value)
               for value in (args.expected_source_sha256, args.expected_host_sha256, args.expected_hub_sha256))
    meta, private, jail, binary = preflight(candidate, args.expected_source_sha256,
                                            args.expected_host_sha256)
    out.mkdir(parents=True, exist_ok=False)
    anchor_verification = verify_anchor(candidate, args.hub_cli.resolve(),
                                        args.expected_hub_sha256, args.hub_anchor, out)
    if args.preflight_only:
        (out / "preflight.json").write_text(json.dumps({
            "status": "PREFLIGHT_ONLY_PASS", "source_sha256": meta["source_sha256"],
            "host_sha256": meta["host_sha256"], "anchor_verification": anchor_verification,
            "shell_started": False, "backend_started": False,
        }, ensure_ascii=False, indent=2) + "\n")
        print("PREFLIGHT_ONLY_PASS; Shell and backend not started")
        return
    backend = ScenarioBackend(8879)
    backend.start()
    remote = Remote(8490)
    ledger = private / "apps/.host/model/ledger.json"
    before_limits = limits(ledger)
    report = {
        "kind": "REAL_OFFICIAL_MODELHOST_SYNTHETIC_HTTP_TRANSPORT",
        "status": "RUNNING", "version": meta["version"],
        "source_sha256": meta["source_sha256"], "host_sha256": meta["host_sha256"],
        "profile_kind": meta["profile_kind"], "model_endpoint": "127.0.0.1:8879/v1",
        "real_model_inference": False, "paid_calls": False,
        "hub_anchor": args.hub_anchor, "anchor_source": "Explicit Root-verified CLI input",
        "anchor_verification": anchor_verification,
        "scenarios": [], "budget_limits_before": before_limits,
        "current_scenario": None,
    }
    def save():
        (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    save()
    env = dict(os.environ)
    env.update({
        "OCTOSENSE_HOME": str(private / "home"), "OCTOSENSE_APP_DATA": str(private / "apps"),
        "OCTOS_APP_CORE_DIR": str(private / "home/octos-home/.octos"),
        "OCTOSENSE_HUB": str(candidate / "mirror"), "OCTOSENSE_HUB_ANCHOR": args.hub_anchor,
        "MAKEPAD_REMOTE": "8490", "MAKEPAD_APP_CONFIG": "{}",
    })
    env.pop("MAKEPAD_HIDE_WINDOWS", None)
    proc = None
    with (out / "host.log").open("w") as host_log:
        try:
            # Direct packaged executable keeps the actual ModelHost stderr for audit.
            proc = subprocess.Popen([str(binary), "--test-action", "launch-apphub"], env=env,
                                    cwd=binary.parent, stdout=host_log, stderr=host_log)
            wait_remote(remote, "已安装", 30)
            remote.click("打开")
            wait_remote(remote, "goal_input", 30)
            for scenario in SCENARIOS:
                backend.configure(scenario)
                report["current_scenario"] = scenario
                save()
                remote.click_scroll("对话", "shortcuts")
                remote.click("＋ 新对话")
                session = wait_for(lambda: selected(jail), 10)
                before_messages = len(session["messages"])
                before_log = (out / "host.log").read_text()
                prompt = "请回答一条合成协议测试短句。编号 " + scenario
                remote.set_text("goal_input", prompt)
                remote.click("发送")
                answer = wait_for(lambda: next((s["messages"][-1] for s in read(jail / "chat-sessions.json")["sessions"]
                                                if s["id"] == session["id"] and len(s["messages"]) >= before_messages + 2), None), 75)
                time.sleep(.2)  # Allow the ModelHost stderr write to reach the file.
                requests = backend.snapshot()
                new_log = (out / "host.log").read_text()[len(before_log):]
                events = log_events(new_log)
                expected = EXPECT[scenario]
                checks = {
                    "post_count": len(requests) == expected["posts"] and len(requests) <= 2,
                    "wire_contract": all(r["path"] == "/v1/chat/completions" and r["model"] == "local-default"
                                         and r["stream"] is False and r["roles"][:1] == ["system"]
                                         and not r["token_cap_present"] for r in requests),
                    "repair_note": requests[1]["repair_hint"] if expected["posts"] == 2 else not requests[0]["repair_hint"],
                    "reply_state": answer["state"] == expected["state"],
                    "synthetic_success_only": ("本地合成协议响应" in answer["text"]) == (scenario == "bad_then_good"),
                    "format_event": events["MODEL_FORMAT_ERROR"] == expected["format"],
                    "retry_event": events["MODEL_RETRY"] == expected["retry"],
                    "final_only_on_failure": events["MODEL_FINAL_FAILURE"] == expected["final"],
                    "no_external_action": not forbidden_actions(jail),
                }
                trace_path = jail / "model-last-response.json"
                trace = read(trace_path) if trace_path.exists() else {}
                if scenario == "bad_then_good":
                    checks["host_attempt_metadata"] = trace.get("meta", {}).get("attempts") == 2
                    budget = trace.get("meta", {}).get("budget", {})
                    checks["default_budget_not_raised"] = (
                        budget.get("per_minute") == 6 and budget.get("calls_per_day") == 100
                        and budget.get("tokens_per_day") == 100_000)
                else:
                    checks["failed_usage_not_claimed_free"] = trace.get("is_ok") is False and trace.get("known_usage") is False
                record = {"scenario": scenario, "checks": checks, "requests": requests,
                          "answer_state": answer["state"], "answer_sha256": hashlib.sha256(answer["text"].encode()).hexdigest(),
                          "modelhost_events": events}
                report["scenarios"].append(record)
                save()
                if not all(checks.values()):
                    raise AssertionError(f"{scenario} failed: {[key for key, value in checks.items() if not value]}")
            after_limits = limits(ledger)
            report["budget_limits_after"] = after_limits
            report["budget_not_raised"] = before_limits == after_limits == {}
            report["no_mail_calendar_write"] = not forbidden_actions(jail)
            report["http_posts_max"] = max(len(row["requests"]) for row in report["scenarios"])
            report["current_scenario"] = None
            report["status"] = "SYNTHETIC_HOST_PROTOCOL_PASS" if report["budget_not_raised"] and report["no_mail_calendar_write"] else "FAIL"
            save()
            if report["status"] != "SYNTHETIC_HOST_PROTOCOL_PASS":
                raise AssertionError("Budget limits or external action changed")
        except Exception as error:
            report["status"] = "ERROR"
            report["error"] = f"{type(error).__name__}: {error}"
            report["failed_scenario_requests"] = backend.snapshot()
            save()
            raise
        finally:
            (out / "backend-requests.json").write_text(json.dumps(report["scenarios"], ensure_ascii=False, indent=2) + "\n")
            backend.stop()
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
    print(json.dumps({"status": report["status"], "source_sha256": report["source_sha256"],
                      "host_sha256": report["host_sha256"], "scenarios": len(report["scenarios"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
