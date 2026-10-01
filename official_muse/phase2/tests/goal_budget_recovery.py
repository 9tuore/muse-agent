"""Exercise three real UI Goals and crash-window recovery in isolated card-host.

This is a LOCAL/FIXTURE test. The app, widgets, timer callbacks, and storage
run in the actual card-host; model, Mail, Calendar, and Shell are not tested.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from goal_chain import wait_notice
from remote import Remote


def start(octo: Path, bundle: Path, state: Path, hub: Path, card_host: Path, port: int) -> None:
    env = dict(os.environ, OCTO_HUB=str(hub), OCTO_CARD_HOST=str(card_host))
    command = [sys.executable, str(octo), "run", str(bundle), "--port", str(port),
               "--detach", "--app-data", str(state)]
    result = subprocess.run(command, cwd=octo.parent.parent, env=env,
                            text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)


def stop(port: int) -> None:
    try:
        urlopen(f"http://127.0.0.1:{port}/quit", timeout=3).read()
    except Exception:
        pass
    time.sleep(0.4)


def type_fresh(remote: Remote, key: str, value: str) -> None:
    for _ in range(100):
        if remote.find(key).get("val") == "":
            break
        remote.click(key)
        remote.request("/k", k="down", c="Backspace", wait=1)
    else:
        raise AssertionError(f"{key} did not clear")
    remote.click(key)
    remote.request("/t", t=value, wait=1)
    assert remote.find(key).get("val") == value, key


def run(args: argparse.Namespace) -> dict:
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", args.port)) == 0:
            raise RuntimeError(f"port {args.port} already belongs to another process")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    bundle = output / "bundle"
    state = output / "state"
    jail = state / "muse-goals"
    shutil.copytree(args.bundle.resolve(), bundle)
    state.mkdir()
    source = ["第一项资料；第二项资料；第三项资料",
              "第四项资料；第五项资料；第六项资料",
              "第七项资料；第八项资料；第九项资料"]
    goals = ["计时预算目标一", "计时预算目标二", "计时预算目标三"]
    first_log = ""
    try:
        start(args.octo.resolve(), bundle, state, args.hub.resolve(),
              args.card_host.resolve(), args.port)
        remote = Remote(args.port)
        for title, facts in zip(goals, source):
            remote.click("对话")
            type_fresh(remote, "goal_input", title)
            remote.click("设为目标")
            type_fresh(remote, "source_input", facts)
            remote.click("生成计划")
            wait_notice(remote, "计划已生成", 10)
            remote.click_scroll("批准并执行", "detail_view")
            wait_notice(remote, "已保存并重新读取核对结果", 30)
        first = json.loads((jail / "goals.json").read_text())
        assert len(first["goals"]) == len(first["runs"]) == 3, first
        assert all(g["status"] == "completed" for g in first["goals"]), first
        assert all(r["status"] == "completed" for r in first["runs"]), first
        first_log = (state / "card-host.log").read_text()
        assert "script time budget exceeded" not in first_log
    finally:
        stop(args.port)

    # Recreate only the isolated crash window: artifact exists, Run is running.
    third = first["goals"][-1]
    run = next(r for r in first["runs"] if r["goal_id"] == third["id"])
    payload = (jail / third["result_path"]).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    third["status"] = "running"
    run["status"] = "running"
    run["finished_at"] = 0
    (jail / "goals.json").write_text(json.dumps(first, ensure_ascii=False, separators=(",", ":")))
    try:
        start(args.octo.resolve(), bundle, state, args.hub.resolve(),
              args.card_host.resolve(), args.port)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            restored = json.loads((jail / "goals.json").read_text())
            restored_goal = next(g for g in restored["goals"] if g["id"] == third["id"])
            restored_run = next(r for r in restored["runs"] if r["id"] == run["id"])
            if restored_goal["status"] == restored_run["status"] == "completed":
                break
            time.sleep(0.2)
        else:
            raise AssertionError("restart did not complete the original Goal/Run")
        assert hashlib.sha256((jail / third["result_path"]).read_bytes()).hexdigest() == digest
        events = json.loads((jail / "activity.json").read_text())
        assert any(e["kind"] == "restart restore" and e["goal_id"] == third["id"]
                   and e["run_id"] == run["id"] for e in events)
        assert "script time budget exceeded" not in (state / "card-host.log").read_text()
        notice = Remote(args.port).find("notice").get("t")
        assert "重启后已独立回读结果" in notice, notice
    finally:
        stop(args.port)
    report = {"evidence": "LOCAL/FIXTURE real card-host UI and storage, no model or Shell",
              "goals": goals, "goal_count": 3, "run_count": 3,
              "third_goal": third["id"], "third_run": run["id"],
              "result_sha256_preserved": digest, "restart_notice": notice,
              "time_budget_errors": 0}
    (output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--octo", type=Path, required=True)
    parser.add_argument("--hub", type=Path, required=True)
    parser.add_argument("--card-host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8262)
    print(json.dumps(run(parser.parse_args()), ensure_ascii=False, indent=2))
