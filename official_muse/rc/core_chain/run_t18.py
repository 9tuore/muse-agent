#!/usr/bin/env python3
"""Isolated synthetic T18 probe against a frozen production Splash snapshot."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run
from regression_run import run_suite


RESTART_PROBE = '''
fn chain_restart_probe(){
    chat_boot() core_boot_activity() core_boot_memory() gm_boot() core_boot_goals() calendar_boot()
    mail_draft = fs.read("mail-draft.json").parse_json()
    mail_watch_boot()
    start_timeout(0.3,|| chain_restart_assert())
}
fn chain_restart_assert(){
    let link_ok = calendar_links.len() == 1 && calendar_links[0].event_id == "fixture-chain-event"
        && calendar_links[0].version == "fixture-v2" && calendar_links[0].status == "verified"
    let goal_ok = goals.len() == 1 && goals[0].version == 3 && goals[0].status == "running"
    let reply_ok = mail_watch.alerts.len() == 1 && mail_watch.alerts[0].status == "accepted"
        && mail_draft.status == "accepted"
    let no_write = chain_count("calendar.create") == 0 && chain_count("calendar.update") == 0
        && chain_count("mail.send") == 0
    fs.write("restart-probe.json",{link_ok: link_ok goal_ok: goal_ok reply_ok: reply_ok
        no_write: no_write host_calls: chain_calls}.to_json())
}
start_timeout(0.1,|| chain_restart_probe())
'''

PROPOSAL_RESTART_PROBE = '''
fn chain_restart_probe(){
    chat_boot() core_boot_activity() core_boot_memory() gm_boot() core_boot_goals() calendar_boot()
    if fs.exists("mail-draft.json") { mail_draft = fs.read("mail-draft.json").parse_json() }
    mail_watch_boot()
    start_timeout(0.3,|| chain_restart_assert())
}
fn chain_restart_assert(){
    let key = "synthetic-account:fixture-reschedule"
    let draft = mail_watch_draft(key)
    let current_ok = draft != nil && draft.body == "我确认新的约定；这句是用户手写内容。"
    let proposed = nil
    if draft != nil { proposed = draft["proposed"] }
    let proposal_ok = proposed != nil && proposed.body.search("建议改期至") >= 0
        && proposed.base_body == draft.body
    let untouched = chain_count("mail.send") == 0 && chain_count("calendar.create") == 0
        && chain_count("calendar.update") == 0
    let adopted = false let adopt_no_send = false let explicit_send_once = false
    if proposed != nil {
        mail_watch_adopt_proposed(key,proposed.to_json().parse_json())
        adopted = mail_watch_draft(key).body.search("建议改期至") >= 0
        adopt_no_send = chain_count("mail.send") == 0
        let shown = mail_watch_draft(key).to_json().parse_json()
        mail_watch_send(key,shown)
        mail_watch_draft_status()
        mail_watch_send(key,shown)
        explicit_send_once = chain_count("mail.send") == 1 && mail_draft.status == "accepted"
    }
    fs.write("restart-probe.json",{current_ok: current_ok proposal_ok: proposal_ok untouched: untouched
        adopted: adopted adopt_no_send: adopt_no_send explicit_send_once: explicit_send_once
        host_calls: chain_calls}.to_json())
}
start_timeout(0.1,|| chain_restart_probe())
'''


def run_restart(first_output: Path, output: Path, proposal_mode: bool):
    original = first_output / "bundle/main.splash"
    code = original.read_text()
    marker = "start_timeout(0.1,|| probe())\n"
    if code.count(marker) != 1:
        raise RuntimeError("Fixture probe marker absent or ambiguous")
    bundle = output / "restart-bundle"
    shutil.copytree(first_output / "bundle", bundle)
    (bundle / "main.splash").write_text(code.replace(
        marker, PROPOSAL_RESTART_PROBE if proposal_mode else RESTART_PROBE))
    state = first_output / "state"
    env = dict(os.environ, MAKEPAD_REMOTE="8509", MAKEPAD_HIDE_WINDOWS="1")
    env.pop("MAKEPAD_FOCUS", None)
    with (output / "restart-runtime.log").open("w") as log:
        proc = subprocess.Popen([str(regression_run.existing.HOST), "--bundle", str(bundle),
                                 "--app-data", str(state), "--allow-unsigned", "--stamp", "--size", "600x700"],
                                env=env, cwd=regression_run.existing.HOST.parents[2], stdout=log, stderr=log)
        try:
            result_path = state / "muse-goals/restart-probe.json"
            deadline = time.monotonic() + 20
            while not result_path.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("No restart probe report; inspect restart-runtime.log")
                time.sleep(.2)
            result = json.loads(result_path.read_text())
            runtime_log = (output / "restart-runtime.log").read_text()
            if "[E]" in runtime_log or "script time budget exceeded" in runtime_log:
                raise RuntimeError("Restart runtime logged an error; evidence preserved")
            (output / "restart-report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
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
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=ROOT / "official_muse/app/source/main.splash")
    parser.add_argument("--proposal-restart", action="store_true",
                        help="Stop before proposal adoption and verify current/proposal across a fresh Host process")
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source_bytes = args.source.read_bytes()
    original_source = source_bytes.decode()
    source = regression_run.existing.replace_function(original_source, "mail_watch_refresh", "fn mail_watch_refresh(){}")
    regression_run.existing.WIDGET = regression_run.existing.WIDGET.replace(
        '    Label{text:',
        '    mail_to := TextInput{width: Fill}\n'
        '    mail_subject := TextInput{width: Fill}\n'
        '    mail_body := TextInput{width: Fill}\n'
        '    mail_intent := TextInput{width: Fill}\n'
        '    Label{text:', 1)
    snapshot = output / "source-bundle"
    shutil.copytree(ROOT / "official_muse/app/bundle", snapshot)
    (snapshot / "main.splash").write_bytes(source_bytes)
    probe = "t18_proposal_restart.splash" if args.proposal_restart else "t18_chain.splash"
    result = run_suite("mail_calendar_chain", source, snapshot, output / "fixture", 8509,
                       Path(__file__).with_name(probe))
    restart = run_restart(output / "fixture", output, args.proposal_restart) if not result["failed"] else None
    report = {
        "kind": "SYNTHETIC_TRANSPORT_PRODUCTION_SPLASH",
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "instrumented_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_path": str(args.source),
        "result": result,
        "variant": "proposal_restart" if args.proposal_restart else "full_chain",
        "restart": restart,
        "limitations": ["Synthetic mail, model and Calendar Host responses", "UI redraw and mail-watch rendering replaced in copied source", "No live account, system Calendar or mail send"],
    }
    (output / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(bool(result["failed"] or (restart is not None and
                                       any(v is False for v in restart.values()))))


if __name__ == "__main__":
    raise SystemExit(main())
