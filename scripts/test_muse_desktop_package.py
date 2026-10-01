#!/usr/bin/env python3
"""Exercise a copied Muse app through its native UI and resident worker."""

import argparse
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PLAN = {
    "title": "Muse 演讲提纲",
    "objective": "准备介绍 Muse 长期目标、显式审批与本机隐私的中文演讲提纲",
    "kind": "speech",
    "artifact": "notes/muse-speech.md",
    "content": "提纲\n一、介绍 Muse 如何把用户目标整理成可审阅计划，批准前不写入目标文件。\n"
               "二、说明批准与计划修订绑定，执行后读取写入文件核对内容。\n"
               "三、介绍本机记忆由用户控制，可在应用内停止记录、纠正或删除。",
    "interval_seconds": 3600,
}
GOAL = "为明天的产品演讲准备一份中文提纲，说明 Muse 的长期目标、显式审批和本机隐私，并保存到工作区。"


class FixtureHandler(BaseHTTPRequestHandler):
    calls = 0

    def do_POST(self):
        FixtureHandler.calls += 1
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if request.get("messages") is None:
            self.send_error(400)
            return
        body = {
            "model": request["model"],
            "choices": [{"message": {"content": json.dumps(PLAN, ensure_ascii=False)}}],
            "usage": {"prompt_tokens": 40, "completion_tokens": 110},
        }
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        pass


def wait_for(label, check, seconds=25):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(0.25)
    raise AssertionError("timed out waiting for " + label)


def ax(pid, action):
    script = ('tell application "System Events" to tell first application process '
              'whose unix id is %d to %s' % (pid, action))
    result = subprocess.run(["/usr/bin/osascript", "-e", script], capture_output=True,
                            text=True, timeout=8)
    if result.returncode:
        raise AssertionError("native UI action failed: " + result.stderr.strip())
    return result.stdout.strip()


def window_ready(pid):
    try:
        return ax(pid, 'get name of window "Muse · GOSIM"') == "Muse · GOSIM"
    except AssertionError:
        return False


def goal_row(database):
    if not database.exists():
        return None
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT goal_id,revision,status,approval_id FROM muse_goals LIMIT 1").fetchone()
        if not row:
            return None
        return dict(zip(("goal_id", "revision", "status", "approval_id"), row))


def completed_run(database):
    if not database.exists():
        return None
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT status,result_json FROM muse_goal_runs ORDER BY started_at DESC LIMIT 1").fetchone()
    return json.loads(row[1]) if row and row[0] == "completed" and row[1] else None


def capture_screen(path):
    try:
        subprocess.run(["/usr/sbin/screencapture", "-x", str(path)],
                       capture_output=True, timeout=6, check=False)
    except (OSError, subprocess.TimeoutExpired):
        pass


def worker_pid(app_pid):
    output = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,command="], capture_output=True,
                            text=True, check=True).stdout
    for line in output.splitlines():
        parts = line.strip().split(maxsplit=2)
        if len(parts) == 3 and parts[1] == str(app_pid) and "desktop_worker.py" in parts[2]:
            return int(parts[0])
    return None


def process_metrics(*pids):
    output = subprocess.run(["/bin/ps", "-o", "pid=,ppid=,%cpu=,rss=", "-p",
                             ",".join(str(pid) for pid in pids)], capture_output=True,
                            text=True, check=True).stdout
    return {int(parts[0]): {"ppid": int(parts[1]), "cpu_percent": float(parts[2]),
                             "rss_kib": int(parts[3])}
            for line in output.splitlines() if len(parts := line.split()) == 4}


def soak(process, workspace, root, duration):
    child = wait_for("private worker PID", lambda: worker_pid(process.pid))
    requests_at_idle = FixtureHandler.calls
    begin = datetime.now().astimezone().isoformat()
    started = time.monotonic()
    samples = 0
    path = root / "resident-30m.jsonl"
    with path.open("w", encoding="utf-8") as log:
        while True:
            assert process.poll() is None, "desktop app exited during resident test"
            metrics = process_metrics(process.pid, child)
            assert process.pid in metrics and child in metrics, "private worker exited during resident test"
            with sqlite3.connect(str(workspace / "memory.sqlite3")) as db:
                runs = db.execute("SELECT COUNT(*) FROM muse_goal_runs").fetchone()[0]
                events = db.execute("SELECT COUNT(*) FROM muse_goal_events").fetchone()[0]
                goal_status = db.execute("SELECT status FROM muse_goals LIMIT 1").fetchone()[0]
            usage = json.loads((workspace / ".muse_model_usage.json").read_text(encoding="utf-8"))
            entry = {"time": datetime.now().astimezone().isoformat(), "elapsed_seconds": round(time.monotonic() - started, 2),
                     "app_pid": process.pid, "worker_pid": child, "processes": metrics,
                     "goal_status": goal_status, "run_count": runs, "goal_event_count": events,
                     "model_request_count": FixtureHandler.calls, "model_used_tokens": usage["used_tokens"]}
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")
            log.flush()
            samples += 1
            remaining = duration - (time.monotonic() - started)
            if remaining <= 0:
                break
            time.sleep(min(30, remaining))
    assert FixtureHandler.calls == requests_at_idle, "model was called while goal was idle"
    return {"start": begin, "end": datetime.now().astimezone().isoformat(),
            "duration_seconds": round(time.monotonic() - started, 2), "samples": samples,
            "app_pid": process.pid, "worker_pid": child,
            "idle_model_requests": FixtureHandler.calls - requests_at_idle,
            "log": str(path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, default=Path(os.environ.get("MUSE_DIST_DIR", "dist")) / "GOSIM-Local-Agent.app")
    parser.add_argument("--output-dir", type=Path, help="Keep copied app, workspace and logs for inspection")
    parser.add_argument("--real-local-model", action="store_true", help="Use the running local Qwen instead of the deterministic fixture")
    parser.add_argument("--revise-before-approve", action="store_true", help="Exercise the native revision dialog before approval")
    parser.add_argument("--check-technical-details", action="store_true", help="Verify the developer panel still exposes the restricted terminal")
    parser.add_argument("--soak-seconds", type=int, default=0, help="Keep the copied app resident and sample it every 30 seconds")
    args = parser.parse_args()
    if args.soak_seconds < 0 or (args.soak_seconds and args.real_local_model):
        parser.error("soak test needs a positive duration and the local fixture model")
    source = args.app.resolve()
    assert (source / "Contents/MacOS/GOSIM-Local-Agent").is_file(), source
    root = args.output_dir.resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="muse-package-ui-"))
    if args.output_dir:
        root.mkdir(parents=True, exist_ok=False)
    copied_app = root / "Muse-Package-Test.app"
    workspace = root / "workspace"
    shutil.copytree(source, copied_app)
    workspace.mkdir()
    server = None if args.real_local_model else ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True) if server else None
    if server_thread:
        server_thread.start()
    process = None
    try:
        sys.path.insert(0, str(copied_app / "Contents/Resources"))
        spec = importlib.util.spec_from_file_location("packaged_muse_models", copied_app / "Contents/Resources/muse_models.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        gateway = module.ModelGateway(workspace)
        settings = gateway.get_settings()
        if server:
            settings["profiles"]["local-default"]["endpoint"] = "http://127.0.0.1:%d/v1/chat/completions" % server.server_port
            settings["profiles"]["local-default"]["model"] = "packaged-local-fixture"
        settings["timeout_seconds"] = 60
        gateway.update_settings(settings)

        env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_DEV_UI="0",
                   GOSIM_LOCAL_INBOX="0", GOSIM_SKIP_ONBOARDING="1")
        with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
            process = subprocess.Popen([str(copied_app / "Contents/MacOS/GOSIM-Local-Agent")],
                                       env=env, stdout=stdout, stderr=stderr)
            wait_for("Muse window", lambda: window_ready(process.pid))
            if args.check_technical_details:
                ax(process.pid, 'click button "查看计划" of group 3 of window "Muse · GOSIM"')
                wait_for("technical details window", lambda: ax(process.pid,
                    'get name of window "Muse · 技术详情"') == "Muse · 技术详情")
                assert ax(process.pid, 'get name of button "提出请求" of group 2 of window "Muse · 技术详情"') == "提出请求"
                ax(process.pid, 'click button 1 of window "Muse · 技术详情"')
            ax(process.pid, "set value of text field \"即时对话输入\" of group 2 of window \"Muse · GOSIM\" to " +
               json.dumps(GOAL, ensure_ascii=False))
            ax(process.pid, 'click button "设为长期目标" of group 2 of window "Muse · GOSIM"')
            database = workspace / "memory.sqlite3"
            draft = wait_for("draft from native UI", lambda: (row if (row := goal_row(database)) and row["status"] == "draft" else None),
                             seconds=140 if args.real_local_model else 25)
            assert draft["revision"] == 1 and draft["approval_id"] is None, draft
            with sqlite3.connect(str(database)) as db:
                plan = json.loads(db.execute("SELECT spec_json FROM muse_goal_revisions WHERE goal_id=? AND revision=1",
                                             (draft["goal_id"],)).fetchone()[0])
            artifact = workspace / plan["steps"][-1]["args"]["relative_path"]
            assert not artifact.exists(), "draft wrote an artifact before approval"
            assert wait_for("enabled approve button", lambda: ax(process.pid, 'get enabled of button "批准计划" of group 3 of window "Muse · GOSIM"') == "true")
            shown_plan = ax(process.pid, 'get value of text area 1 of scroll area 1 of group 3 of window "Muse · GOSIM"')
            assert "尚未批准" in shown_plan and "目标：" in shown_plan, shown_plan
            capture_screen(root / "muse-draft.png")
            if args.revise_before_approve:
                ax(process.pid, 'click button "修改目标" of group 3 of window "Muse · GOSIM"')
                ax(process.pid, 'set value of text field "目标修订要求" of window 1 to "改成三分钟演讲，先说明审批再说明本机隐私。"')
                ax(process.pid, 'click button "生成新版计划" of window 1')
                draft = wait_for("revised draft from native UI", lambda: (
                    row if (row := goal_row(database)) and row["status"] == "draft" and row["revision"] == 2 else None),
                    seconds=140 if args.real_local_model else 25)
                assert draft["approval_id"] is None and not artifact.exists(), draft
                wait_for("revised plan in native UI", lambda: "修订 2" in ax(
                    process.pid, 'get value of static text 2 of group 3 of window "Muse · GOSIM"'))
            ax(process.pid, 'click button "批准计划" of group 3 of window "Muse · GOSIM"')
            approved = wait_for("revision-bound approval", lambda: (row if (row := goal_row(database)) and row["approval_id"] else None))
            assert approved["revision"] == draft["revision"] and approved["approval_id"].startswith("approval:")
            run = wait_for("autonomous resident worker run", lambda: completed_run(database),
                           seconds=140 if args.real_local_model else 25)
            assert run["status"] == "COMPLETED" and run["approval_id"] == approved["approval_id"], run
            assert artifact.exists() and "提纲" in artifact.read_text(encoding="utf-8")
            assert any(receipt.get("verification", {}).get("readback_matches") is True
                       for receipt in run["receipts"]), run["receipts"]
            wait_for("native result status", lambda: "产物已生成并核对" in ax(
                process.pid, 'get value of static text 2 of group 3 of window "Muse · GOSIM"'))
            time.sleep(0.8)
            capture_screen(root / "muse-completed.png")
            notification_file = workspace / ".agent_notification_status.json"
            notification = json.loads(notification_file.read_text(encoding="utf-8")) if notification_file.exists() else {}
            resident = soak(process, workspace, root, args.soak_seconds) if args.soak_seconds else None
            print(json.dumps({"status": "PASS", "app": str(copied_app), "workspace": str(workspace),
                              "model_source": "real_local_qwen" if args.real_local_model else "local_fixture",
                              "goal_id": draft["goal_id"], "revision": draft["revision"],
                              "approval_id": approved["approval_id"], "run_id": run["run_id"],
                              "artifact": str(artifact), "readback_matches": True,
                              "ui_plan_before_approval": True, "resident_tick": True,
                              "notification_request_status": notification.get("status", "NOT_OBSERVED"),
                              "draft_screenshot": str(root / "muse-draft.png"),
                              "completed_screenshot": str(root / "muse-completed.png"),
                              "resident": resident}, ensure_ascii=False))
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if server:
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=2)
        if not args.output_dir:
            shutil.rmtree(root)


if __name__ == "__main__":
    main()
