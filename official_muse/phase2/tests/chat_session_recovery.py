"""LOCAL card-host check for legacy Chat import, session isolation and restart.

This uses a synthetic old chat.json and a real visible card-host window. It
does not call a model or establish Shell full-chain behavior.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from remote import Remote


def click_text(remote: Remote, prefix: str) -> None:
    matches = [widget for widget in remote.widgets() if widget.get("t", "").startswith(prefix)]
    if len(matches) != 1:
        raise AssertionError(f"expected one visible control starting with {prefix!r}; got {len(matches)}")
    x, y, width, height = matches[0]["r"]
    if width < 2 or height < 2:
        raise AssertionError(f"control {prefix!r} is clipped")
    remote.request("/click", x=int(x + width / 2), y=int(y + height / 2))


def launch(host: Path, bundle: Path, state: Path, port: int, log_path: Path):
    env = dict(os.environ, MAKEPAD_REMOTE=str(port))
    command = [str(host), "--bundle", str(bundle), "--app-data", str(state),
               "--allow-unsigned", "--stamp", "--size", "990x539"]
    log = log_path.open("w")
    process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    remote = Remote(port)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            remote.find("goal_input")
            return process, log, remote
        except Exception:
            time.sleep(0.2)
    process.terminate()
    process.wait(timeout=5)
    log.close()
    raise RuntimeError(log_path.read_text()[-4000:])


def stop(process: subprocess.Popen, log, port: int) -> None:
    try:
        urlopen(f"http://127.0.0.1:{port}/quit", timeout=3).read()
    except Exception:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=5)
    log.close()


def wait_file(path: Path, seconds: float = 10) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.1)
    raise AssertionError(f"expected storage file was not created: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--card-host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8262)
    args = parser.parse_args()
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", args.port)) == 0:
            raise RuntimeError(f"port {args.port} is in use")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    bundle = output / "bundle"
    state = output / "state"
    jail = state / "muse-goals"
    shutil.copytree(args.bundle.resolve(), bundle)
    jail.mkdir(parents=True)
    legacy = [
        {"role": "user", "text": "旧会话测试消息", "state": "success", "at": 1},
        {"role": "assistant", "text": "旧版欢迎", "state": "success", "at": 2},
    ]
    legacy_text = json.dumps(legacy, ensure_ascii=False)
    (jail / "chat.json").write_text(legacy_text)
    process, log, remote = launch(args.card_host.resolve(), bundle, state, args.port, output / "first.log")
    try:
        wait_file(jail / "chat-sessions.json")
        stored = json.loads((jail / "chat-sessions.json").read_text())
        assert stored["schema"] == 1 and len(stored["sessions"]) == 1
        assert stored["sessions"][0]["messages"] == legacy
        assert (jail / "chat.json").read_text() == legacy_text
        remote.find("旧版欢迎")
        remote.click("新对话")
        stored = json.loads((jail / "chat-sessions.json").read_text())
        assert len(stored["sessions"]) == 2
        assert stored["selected_id"] == stored["sessions"][1]["id"]
        assert stored["sessions"][1]["messages"] == []
        assert not any(w.get("t") == "旧版欢迎" for w in remote.widgets())
        remote.shot(output / "new-session.png")
        click_text(remote, "原对话 ·")
        stored = json.loads((jail / "chat-sessions.json").read_text())
        assert stored["selected_id"] == stored["sessions"][0]["id"]
        remote.find("旧版欢迎")
        remote.shot(output / "restored-legacy.png")
    finally:
        stop(process, log, args.port)
    process, log, remote = launch(args.card_host.resolve(), bundle, state, args.port, output / "restart.log")
    try:
        remote.wait_for("旧版欢迎", seconds=10)
        stored = json.loads((jail / "chat-sessions.json").read_text())
        assert len(stored["sessions"]) == 2
        assert stored["selected_id"] == stored["sessions"][0]["id"]
        assert stored["sessions"][0]["messages"] == legacy
        assert (jail / "chat.json").read_text() == legacy_text
        remote.shot(output / "restart-restored.png")
    finally:
        stop(process, log, args.port)
    assert (jail / "chat-sessions.backup.json").exists()
    (jail / "chat-sessions.json").write_text("{damaged")
    process, log, remote = launch(args.card_host.resolve(), bundle, state, args.port, output / "damaged-primary.log")
    try:
        remote.wait_for("今天想让 Muse 处理什么？", seconds=10)
        click_text(remote, "原对话 ·")
        repaired = json.loads((jail / "chat-sessions.json").read_text())
        assert len(repaired["sessions"]) == 2
        assert repaired["sessions"][0]["messages"] == legacy
        remote.find("旧版欢迎")
        remote.shot(output / "backup-repaired.png")
    finally:
        stop(process, log, args.port)
    for missing in ("id", "messages"):
        damaged = copy.deepcopy(repaired)
        del damaged["sessions"][0][missing]
        (jail / "chat-sessions.json").write_text(json.dumps(damaged, ensure_ascii=False))
        process, log, remote = launch(args.card_host.resolve(), bundle, state, args.port,
                                      output / f"missing-{missing}.log")
        try:
            remote.wait_for("今天想让 Muse 处理什么？", seconds=10)
            click_text(remote, "原对话 ·")
            repaired = json.loads((jail / "chat-sessions.json").read_text())
            assert repaired["sessions"][0]["messages"] == legacy
            remote.find("旧版欢迎")
            remote.shot(output / f"missing-{missing}-repaired.png")
        finally:
            stop(process, log, args.port)
    report = {"scope": "LOCAL card-host, synthetic legacy chat; no model or Shell",
              "sessions": 2, "legacy_unchanged": True, "restart_restored": True,
              "damaged_primary_recovered_from_backup": True,
              "missing_id_and_messages_recovered_from_backup": True}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
