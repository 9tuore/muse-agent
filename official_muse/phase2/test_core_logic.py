#!/usr/bin/env python3
"""Run Phase 2 core state in the real card-host with synthetic app-jail data.

This is a LOCAL/FIXTURE test. It does not call model, Mail, Calendar, or Shell.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
WS = HERE.parents[2] / "official-ws"
OCTO = WS / "OctoScript-App-Design-Flow/tools/octo"
HUB = WS.parent / "phase2-host/OctoSense-App-Hub/target/debug/hub"
CARD_HOST = WS.parent / "phase2-host/OctoSense/target/release/card-host"


def wait_file(path: Path, timeout: float = 8) -> dict:
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        if path.exists():
            return json.loads(path.read_text())
        time.sleep(0.1)
    raise AssertionError(f"card-host did not write {path.name}")


def launch(bundle: Path, state: Path, port: int) -> str:
    env = dict(os.environ, OCTO_HUB=str(HUB), OCTO_CARD_HOST=str(CARD_HOST))
    command = [sys.executable, str(OCTO), "run", str(bundle), "--port", str(port),
               "--hidden", "--detach", "--app-data", str(state)]
    result = subprocess.run(command, cwd=OCTO.parent.parent, env=env,
                            text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout


def quit_host(port: int) -> None:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/quit", timeout=3).read()
    except Exception:
        pass
    time.sleep(0.3)


def assert_all(report: dict) -> None:
    expected = ("old_ok", "legacy_activity", "legacy_recovered", "second", "third", "select", "write_ok", "finish2",
                "double_finish_rejected", "old_revision_rejected", "duplicate_send_rejected", "model_isolated",
                "verify_started", "accepted", "verified", "double_verify_rejected",
                "other_account_hidden", "isolated", "replanned", "run2_again", "standalone", "action",
                "added_source", "added_claim", "found", "corrected", "pinned",
                "corrected_found", "deleted", "after_delete", "reimport_rejected",
                "activity_ok", "alias_added", "alias_reimport_rejected", "missing_hash_rejected", "pinned_added", "hash_matches")
    for key in expected:
        assert report.get(key) is True, f"{key}: {report}"
    assert report.get("goal_count") == 3, report
    assert report.get("run_count") == 4, report


def run(port: int) -> dict:
    for executable in (OCTO, HUB, CARD_HOST):
        if not executable.is_file():
            raise FileNotFoundError(executable)
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(f"port {port} belongs to another process")

    root = HERE / ".local-state" / "core-contract-test"
    if root.exists():
        shutil.rmtree(root)
    bundle = root / "bundle"
    state = root / "state"
    jail = state / "muse-goals"
    shutil.copytree(REPO / "official_muse/app/bundle", bundle)
    bundle.joinpath("main.splash").write_text(
        HERE.joinpath("core_logic.splash").read_text()
        + "\n" + HERE.joinpath("core_logic_probe.splash").read_text()
    )
    jail.joinpath("results").mkdir(parents=True)
    old = {"schema": 1, "id": "g1", "version": 1, "goal": "旧目标",
           "status": "running", "result_path": "results/old.json",
           "updated_at": 42, "approved_at": 1}
    jail.joinpath("current.json").write_text(json.dumps(old, ensure_ascii=False))
    jail.joinpath("activity.json").write_text(json.dumps([
        {"kind": "Goal created", "detail": "旧目标", "at": 42, "task_id": "g1"}
    ], ensure_ascii=False))
    old_result = '{"task_id":"g1","result":"旧结果"}'
    jail.joinpath("results/old.json").write_text(old_result)

    try:
        launch(bundle, state, port)
        report = wait_file(jail / "test-report.json")
        assert_all(report)
        quit_host(port)
        launch(bundle, state, port)
        restart = wait_file(jail / "test-restart.json")
        assert restart["goal_count"] == 3, restart
        assert restart["selected_id"] == "g1", restart
        assert restart["old_result"] == old_result, restart
        assert restart["action_status"] == "unknown", restart
        assert restart["standalone_status"] == "unknown", restart
        assert restart["memory_count"] == 1 and restart["pinned_restored"] is True and restart["forgotten"] == 2, restart
    finally:
        quit_host(port)

    sys.path.insert(0, str(REPO / "app"))
    from muse_dsl import validate_document  # pylint: disable=import-outside-toplevel

    memory = json.loads(jail.joinpath("memory.json").read_text())
    assert memory["claims"][0]["document"]["payload"]["deleted"] is True
    validate_document(memory["claims"][0]["document"])
    from muse_memory_graph import MemoryGraph
    graph = MemoryGraph(root / "compatibility.sqlite")
    for source in memory["sources"]:
        graph.put_source({key: source[key] for key in
                          ("source_id", "kind", "locator", "content_sha256", "observed_at", "updated_at")},
                         source["scope"])
    active = [claim for claim in memory["claims"] if not claim["document"]["payload"]["deleted"]]
    for claim in active:
        validate_document(claim["document"])
        graph.put_claim(claim["document"])
        assert graph.get_claim(claim["document"]["id"], claim["document"]["scope"]) == claim["document"]
    assert jail.joinpath("current.json").read_text() == json.dumps(old, ensure_ascii=False)

    # Malformed records must fail closed and remain byte-for-byte untouched.
    bad_jail = root / "bad-state" / "muse-goals"
    bad_jail.mkdir(parents=True)
    bad_records = {
        "goals.json": "{malformed",
        "activity.json": '[{"kind":"Goal created","at":42,"task_id":"g1"}]',
        "memory.json": '{"schema":9,"claims":[],"sources":[],"forget":[]}',
    }
    for name, contents in bad_records.items():
        bad_jail.joinpath(name).write_text(contents)
    bundle.joinpath("main.splash").write_text(
        HERE.joinpath("core_logic.splash").read_text()
        + "\n" + HERE.joinpath("core_logic_corrupt_probe.splash").read_text()
    )
    try:
        launch(bundle, bad_jail.parent, port)
        corrupt = wait_file(bad_jail / "test-corrupt.json")
        assert all(corrupt[key] is False for key in corrupt), corrupt
    finally:
        quit_host(port)
    for name, contents in bad_records.items():
        assert bad_jail.joinpath(name).read_text() == contents, name

    # A valid backup must be usable even when the primary parses to a bad object.
    backup_jail = root / "backup-state" / "muse-goals"
    backup_jail.mkdir(parents=True)
    for name, contents in bad_records.items():
        backup_jail.joinpath(name).write_text(contents)
        backup_jail.joinpath(name.replace(".json", ".backup.json")).write_text(
            jail.joinpath(name).read_text()
        )
    bundle.joinpath("main.splash").write_text(
        HERE.joinpath("core_logic.splash").read_text()
        + "\n" + HERE.joinpath("core_logic_backup_probe.splash").read_text()
    )
    try:
        launch(bundle, backup_jail.parent, port)
        backup = wait_file(backup_jail / "test-backup.json")
        assert backup["goals_ok"] and backup["activity_ok"] and backup["memory_ok"], backup
        assert backup["goal_count"] == 3 and backup["activity_count"] > 0, backup
    finally:
        quit_host(port)
    for name, contents in bad_records.items():
        assert backup_jail.joinpath(name).read_text() == contents, name
    outcome = {"evidence": "LOCAL/FIXTURE card-host, not Shell or live service",
               "first_boot": report, "restart": restart,
               "old_result_preserved": True, "dsl_tombstone_valid": True,
               "desktop_source_and_claim_compatible": True,
               "malformed_records_protected": corrupt,
               "valid_backup_recovered": backup}
    root.joinpath("result.json").write_text(json.dumps(outcome, ensure_ascii=False, indent=2))
    return outcome


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8262)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.port), ensure_ascii=False, indent=2))
