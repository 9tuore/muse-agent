"""Exercise the visible chat session controls in an isolated real card-host.

LOCAL/FIXTURE only: imports synthetic legacy chat.json and never calls a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from remote import Remote


def run_host(bundle: Path, state: Path, log: Path, size: str, port: int):
    env = dict(os.environ, MAKEPAD_REMOTE=str(port))
    command = [str(CARD_HOST), "--bundle", str(bundle), "--app-data", str(state),
               "--allow-unsigned", "--stamp", "--size", size]
    handle = log.open("w")
    process = subprocess.Popen(command, env=env, stdout=handle, stderr=subprocess.STDOUT)
    remote = Remote(port)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            remote.find("page_content")
            return process, handle, remote
        except Exception:
            time.sleep(0.2)
    stop_host(process, handle, port)
    raise RuntimeError(log.read_text()[-3000:])


def stop_host(process, handle, port: int):
    try:
        urlopen(f"http://127.0.0.1:{port}/quit", timeout=3).read()
    except Exception:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=5)
    handle.close()


def click_in_content(remote: Remote, key: str):
    for _ in range(12):
        item = remote.find(key)
        x, y, width, height = item["r"]
        cx, cy, cw, ch = remote.find("page_content")["r"]
        if width >= 2 and height >= 2 and cy <= y and y + height <= cy + ch:
            remote.click(key)
            return
        remote.scroll(int(cx + cw / 2), int(cy + ch / 2), 80 if y > cy else -80)
    raise AssertionError(f"session control not reachable: {key}")


def find_in_content(remote: Remote, key: str):
    for _ in range(30):
        try:
            return remote.find(key)
        except AssertionError:
            x, y, width, height = remote.find("page_content")["r"]
            remote.scroll(int(x + width / 2), int(y + height / 2), 80)
            time.sleep(0.2)
    raise AssertionError(f"chat item not reachable: {key}")


def stable_rect(remote: Remote, key: str):
    last = None
    same = 0
    for _ in range(20):
        rect = remote.find(key)["r"]
        same = same + 1 if rect == last else 0
        if same >= 3:
            return rect
        last = rect
        time.sleep(0.2)
    return last


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--card-host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port-base", type=int, default=8460)
    args = parser.parse_args()
    global CARD_HOST
    CARD_HOST = args.card_host.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    bundle = output / "bundle"
    shutil.copytree(args.bundle.resolve(), bundle)
    digest = hashlib.sha256((bundle / "main.splash").read_bytes()).hexdigest()
    results = []
    for offset, size in enumerate(("990x400", "990x300")):
        port = args.port_base + offset
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"port {port} is occupied")
        work = output / size
        jail = work / "state" / "muse-goals"
        jail.mkdir(parents=True)
        legacy = [{"role": "user", "text": "合成旧会话：苹果", "state": "success", "at": 1},
                  {"role": "assistant", "text": "合成旧回复：苹果", "state": "success", "at": 2}]
        (jail / "chat.json").write_text(json.dumps(legacy, ensure_ascii=False))
        process, handle, remote = run_host(bundle, work / "state", work / "first.log", size, port)
        try:
            remote.wait_for("新对话", 10)
            content_rect = stable_rect(remote, "page_content")
            input_rect = stable_rect(remote, "goal_input")
            imported = json.loads((jail / "chat-sessions.json").read_text())
            assert len(imported["sessions"]) == 1 and imported["sessions"][0]["messages"] == legacy
            remote.shot(work / "legacy.png")
            click_in_content(remote, "新对话")
            saved = json.loads((jail / "chat-sessions.json").read_text())
            assert len(saved["sessions"]) == 2 and saved["sessions"][0]["messages"] == legacy
            assert saved["selected_id"] == saved["sessions"][1]["id"]
            remote.shot(work / "new.png")
            old_label = next(w["t"] for w in remote.widgets()
                             if w.get("t", "").startswith("原对话 · "))
            click_in_content(remote, old_label)
            saved = json.loads((jail / "chat-sessions.json").read_text())
            assert saved["selected_id"] == saved["sessions"][0]["id"]
            find_in_content(remote, "合成旧回复：苹果")
            remote.shot(work / "restored-old.png")
        finally:
            stop_host(process, handle, port)
        process, handle, remote = run_host(bundle, work / "state", work / "restart.log", size, port)
        try:
            find_in_content(remote, "合成旧回复：苹果")
            remote.shot(work / "after-restart.png")
            assert json.loads((jail / "chat.json").read_text()) == legacy
        finally:
            stop_host(process, handle, port)
        results.append({"size": size, "page_content": content_rect, "goal_input": input_rect,
                        "legacy_import": True, "new_session": True, "switch": True,
                        "restart": True, "legacy_unchanged": True})
    report = {"evidence": "LOCAL/FIXTURE real card-host, no model or Shell",
              "main_sha256": digest, "results": results}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
