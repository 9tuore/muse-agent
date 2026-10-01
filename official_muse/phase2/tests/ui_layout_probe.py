"""Measure Muse's real card-host layout with synthetic, storage-only Goals.

This is a LOCAL probe. It does not call a model, Mail, Calendar, or Shell.
Each size runs a fresh copied bundle and isolated app-data directory.
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

from goal_chain import wait_notice
from remote import Remote


def click_nav(remote: Remote, key: str, window_height: int) -> None:
    for _ in range(12):
        try:
            remote.click(key)
            return
        except AssertionError:
            remote.scroll(60, min(180, window_height // 2), 80)
    raise AssertionError(f"navigation item did not become reachable: {key}")


def run_size(bundle: Path, output: Path, card_host: Path, size: str, port: int) -> dict:
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(f"port {port} is already in use")
    work = output / size
    shutil.copytree(bundle, work / "bundle")
    jail = work / "state" / "muse-goals"
    env = dict(os.environ, MAKEPAD_REMOTE=str(port))
    command = [str(card_host), "--bundle", str(work / "bundle"), "--app-data",
               str(work / "state"), "--allow-unsigned", "--stamp", "--size", size]
    with (work / "card-host.log").open("w") as log:
        process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            remote = Remote(port)
            deadline = time.monotonic() + 20
            while True:
                try:
                    remote.find("goal_input")
                    break
                except Exception:
                    if time.monotonic() >= deadline:
                        raise RuntimeError((work / "card-host.log").read_text()[-3000:])
                    time.sleep(0.2)
            last_rect = None
            stable = 0
            for _ in range(20):
                rect = remote.find("central_main")["r"]
                stable = stable + 1 if rect == last_rect else 0
                if stable >= 2:
                    break
                last_rect = rect
                time.sleep(0.2)
            chat_rect = remote.find("page_content")["r"]
            remote.shot(work / "chat.png")
            title = f"UI 布局验证 {size}"
            source = "；".join(f"资料{i}：合成长文本用于核对滚动和批准按钮可达。" for i in range(1, 9))
            remote.set_text("goal_input", title)
            remote.click("设为目标")
            remote.set_text("source_input", source)
            source_rect = remote.find("source_input")["r"]
            remote.click("生成计划")
            wait_notice(remote, "计划已生成", 10)
            detail_rect = remote.find("detail_view")["r"]
            input_rect = remote.find("goal_input")["r"]
            remote.shot(work / "goal-detail.png")
            remote.click_scroll("批准并执行", "detail_view", attempts=20)
            wait_notice(remote, "已保存并重新读取核对结果", 30)
            remote.shot(work / "goal-result.png")
            goals = json.loads((jail / "goals.json").read_text())
            matching = [goal for goal in goals["goals"] if goal["goal"] == title]
            assert len(matching) == 1 and matching[0]["status"] == "completed"
            result_path = jail / matching[0]["result_path"]
            result = json.loads(result_path.read_text())
            assert result["task_id"] == matching[0]["id"] and result["source_text"] == source
            remote.click("编辑资料")
            edit_rect = remote.find("source_input")["r"]
            assert remote.find("source_input").get("val") == source
            remote.shot(work / "goal-edit.png")
            click_nav(remote, "能力授权", int(size.split("x")[1]))
            remote.click("侧栏")
            rail_rect = remote.find("right_column")["r"]
            remote.shot(work / "capabilities.png")
            return {"size_requested": size, "chat_content": chat_rect,
                    "goal_detail": detail_rect, "goal_input": input_rect,
                    "source_input": source_rect, "source_input_edit": edit_rect,
                    "right_column": rail_rect,
                    "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
                    "screenshots": [str(work / name) for name in
                                    ("chat.png", "goal-detail.png", "goal-result.png", "goal-edit.png", "capabilities.png")]}
        finally:
            try:
                urlopen(f"http://127.0.0.1:{port}/quit", timeout=3).read()
            except Exception:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--card-host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port-base", type=int, default=8450)
    parser.add_argument("--sizes", nargs="+", default=["990x400", "412x892", "990x300", "1280x800"])
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    snapshot = output / "source-bundle"
    shutil.copytree(args.bundle.resolve(), snapshot)
    digest = hashlib.sha256((snapshot / "main.splash").read_bytes()).hexdigest()
    results = []
    for offset, size in enumerate(args.sizes):
        results.append(run_size(snapshot, output, args.card_host.resolve(), size, args.port_base + offset))
        print(size, results[-1]["goal_detail"], flush=True)
    report = {"evidence": "LOCAL card-host; not final Shell or external-service acceptance",
              "main_sha256": digest, "results": results}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
