#!/usr/bin/env python3
"""Exercise native Goal approval, pause, restart, resume, cancel, and reject with a local fixture."""
import argparse
import fcntl
import json
import os
import shutil
import sqlite3
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from test_muse_desktop_package import ax, goal_row, wait_for, window_ready


PLAN = {
    "title": "合成目录更新提纲", "objective": "持续关注已选合成目录并更新中文提纲",
    "kind": "file_monitor", "artifact": "notes/muse-synthetic-monitor.md",
    "content": "提纲\n一、只记录已授权合成目录的文件变化。\n二、每次更新保存新版本并回读核对。",
    "interval_seconds": 3600,
}
GOAL = "持续关注我选定的合成文件夹；文件有变化时更新同一个中文提纲。"
COMPOSE = "提纲\n一、已授权合成目录发生文件变化。\n二、保存本次更新并核对文件内容。\n"


class Fixture(BaseHTTPRequestHandler):
    calls = 0

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = json.dumps(payload.get("messages", []), ensure_ascii=False)
        text = json.dumps(PLAN, ensure_ascii=False) if "只输出一个JSON对象" in prompt else COMPOSE
        Fixture.calls += 1
        response = {"model": payload["model"], "choices": [{"message": {"content": text}}],
                    "usage": {"prompt_tokens": 40, "completion_tokens": 70}}
        body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


SETUP = r'''
import sys
from pathlib import Path
from muse_models import ModelGateway
gateway = ModelGateway(Path(sys.argv[1]))
settings = gateway.get_settings()
settings["mode"] = "local"
settings["profiles"][settings["active_local"]]["endpoint"] = sys.argv[2]
settings["profiles"][settings["active_local"]]["model"] = "local-fixture"
gateway.update_settings(settings)
from agent_app import LocalAgent
watch = LocalAgent(Path(sys.argv[1])).handle({
    "type": "watch_folder_set", "path": sys.argv[3], "approved": True})
if not watch.get("ok"):
    raise RuntimeError(watch)
'''


def watch_ref(workspace):
    path = workspace / ".muse-watch-registry.sqlite3"
    if not path.exists():
        return None
    with sqlite3.connect(str(path), timeout=3) as db:
        row = db.execute("SELECT resource_ref FROM watched LIMIT 1").fetchone()
    return row[0] if row else None


def status(database, goal_id):
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
    return row[0] if row else None


def runs(database, goal_id):
    with sqlite3.connect(str(database), timeout=3) as db:
        rows = db.execute("SELECT result_json FROM muse_goal_runs WHERE goal_id=? AND status='completed' ORDER BY started_at",
                          (goal_id,)).fetchall()
    return [json.loads(row[0]) for row in rows if row[0]]


def launch(app, env, root, suffix):
    stdout = (root / f"app-{suffix}.stdout").open("w")
    stderr = (root / f"app-{suffix}.stderr").open("w")
    proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                            env=env, stdout=stdout, stderr=stderr)
    wait_for("Muse window", lambda: window_ready(proc.pid))
    return proc, stdout, stderr


def stop(proc, stdout, stderr):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    stdout.close()
    stderr.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    app = root / "GOSIM-Local-Agent.app"
    shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
    workspace = root / "workspace"
    selected = root / "selected"
    workspace.mkdir()
    selected.mkdir()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}/v1/chat/completions"
    resources = app / "Contents/Resources"
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
               GOSIM_LOCAL_INBOX="0", PYTHONPATH=str(resources))
    subprocess.run([str(resources / "python/bin/python3"), "-B", "-c", SETUP,
                    str(workspace), endpoint, str(selected)], env=env, check=True,
                   capture_output=True, text=True)
    database = workspace / "memory.sqlite3"
    selected_ref = watch_ref(workspace)
    assert selected_ref
    lock_path = Path("/tmp/gosim-muse-5agent-20260928/gui.lock")
    lock_path.parent.mkdir(mode=0o700, exist_ok=True)
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    lock_held = True
    processes = []
    try:
        proc, stdout, stderr = launch(app, env, root, "before-restart")
        processes.append((proc, stdout, stderr))
        time.sleep(0.7)
        ax(proc.pid, 'click pop up button 1 of group 2 of window "Muse · GOSIM"')
        choices = ax(proc.pid, 'get name of menu items of menu 1 of pop up button 1 of group 2 of window "Muse · GOSIM"')
        assert selected.name in choices, choices
        ax(proc.pid, 'click menu item 2 of menu 1 of pop up button 1 of group 2 of window "Muse · GOSIM"')
        ax(proc.pid, 'set value of text field "即时对话输入" of group 2 of window "Muse · GOSIM" to ' +
           json.dumps(GOAL, ensure_ascii=False))
        ax(proc.pid, 'click button "设为长期目标" of group 2 of window "Muse · GOSIM"')
        draft = wait_for("native Goal draft", lambda: row if (row := goal_row(database)) and row["status"] == "draft" else None,
                         seconds=40)
        goal_id = draft["goal_id"]
        with sqlite3.connect(str(database), timeout=3) as db:
            spec = json.loads(db.execute("SELECT spec_json FROM muse_goal_revisions WHERE goal_id=?", (goal_id,)).fetchone()[0])
        assert selected_ref in spec["permissions"]["resource_refs"]
        assert {item["kind"] for item in spec["triggers"]} == {"event"}
        assert not list(workspace.glob("notes/muse-synthetic-monitor*"))
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_held = False
        ax(proc.pid, 'click button "批准计划" of group 3 of window "Muse · GOSIM"')
        wait_for("approved Goal", lambda: status(database, goal_id) == "active")
        (selected / "event-one.txt").write_text("one\n")
        first = wait_for("first file event run", lambda: values[0] if (values := runs(database, goal_id)) else None,
                         seconds=40)
        assert first["event_id"].startswith("file:")
        ax(proc.pid, 'click button "暂停目标" of group 3 of window "Muse · GOSIM"')
        wait_for("paused Goal", lambda: status(database, goal_id) == "paused")
        (selected / "while-paused.txt").write_text("paused\n")
        time.sleep(5)
        assert len(runs(database, goal_id)) == 1, "new run while paused"
        stop(proc, stdout, stderr)
        processes.clear()
        proc, stdout, stderr = launch(app, env, root, "after-restart")
        processes.append((proc, stdout, stderr))
        assert status(database, goal_id) == "paused"
        wait_for("resume button after restart", lambda: "继续目标" in ax(proc.pid,
            'get name of buttons of group 3 of window "Muse · GOSIM"'), seconds=15)
        ax(proc.pid, 'click button "继续目标" of group 3 of window "Muse · GOSIM"')
        wait_for("resumed Goal", lambda: status(database, goal_id) == "active")
        (selected / "event-two.txt").write_text("two\n")
        second = wait_for("second file event run", lambda: values[-1] if len(values := runs(database, goal_id)) >= 2 else None,
                          seconds=40)
        assert second["event_id"].startswith("file:")
        ax(proc.pid, 'click button "取消目标" of group 3 of window "Muse · GOSIM"')
        wait_for("cancelled Goal", lambda: status(database, goal_id) == "cancelled")
        (selected / "after-cancel.txt").write_text("cancelled\n")
        time.sleep(5)
        assert len(runs(database, goal_id)) == 2, "new run after cancel"
        ax(proc.pid, 'click pop up button 1 of group 2 of window "Muse · GOSIM"')
        ax(proc.pid, 'click menu item 2 of menu 1 of pop up button 1 of group 2 of window "Muse · GOSIM"')
        ax(proc.pid, 'set value of text field "即时对话输入" of group 2 of window "Muse · GOSIM" to ' +
           json.dumps(GOAL, ensure_ascii=False))
        ax(proc.pid, 'click button "设为长期目标" of group 2 of window "Muse · GOSIM"')
        def second_draft():
            with sqlite3.connect(str(database), timeout=3) as db:
                row = db.execute("SELECT goal_id FROM muse_goals WHERE goal_id!=? AND status='draft' LIMIT 1",
                                 (goal_id,)).fetchone()
            return row[0] if row else None
        rejected_goal = wait_for("second native Goal draft", second_draft, seconds=40)
        ax(proc.pid, 'click button "拒绝计划" of group 3 of window "Muse · GOSIM"')
        wait_for("rejected Goal", lambda: status(database, rejected_goal) == "rejected")
        assert not runs(database, rejected_goal)
        output = {"status": "PASS_FIXTURE", "goal_id": goal_id, "watch_ref": selected_ref,
                  "watch_source": "fixture_preapproved",
                  "first_run": first["run_id"], "second_run": second["run_id"],
                  "paused_survived_restart": True, "no_run_while_paused_or_after_cancel": True,
                  "rejected_goal_id": rejected_goal, "no_run_after_rejection": True,
                  "fixture_model_calls": Fixture.calls}
        (root / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
        print(json.dumps(output, ensure_ascii=False))
    finally:
        if lock_held:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
        for proc, stdout, stderr in processes:
            stop(proc, stdout, stderr)
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
