#!/usr/bin/env python3
"""Exercise one real local-Qwen research Goal through the packaged native UI."""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from test_g04_native_layout import WINDOW_ID_SOURCE
from test_muse_desktop_package import ax, goal_row, wait_for, window_ready


SOURCE = "https://docs.python.org/zh-cn/3.13/whatsnew/3.13.html"
GOAL = (f"持续关注 {SOURCE} 的公开资料变化，整理一份中文 Python 3.13 资料提纲并注明来源。"
        "当我选定的合成资料目录有文件变化时，更新同一个提纲。")
SETUP_WATCH = r'''
import sys
from pathlib import Path
from agent_app import LocalAgent
result = LocalAgent(Path(sys.argv[1])).handle({
    "type": "watch_folder_set", "path": sys.argv[2], "approved": True})
if not result.get("ok"):
    raise RuntimeError(result)
'''
PROBE_WRONG_DIGEST = r'''
import json
import sys
from pathlib import Path
from agent_app import LocalAgent
result = LocalAgent(Path(sys.argv[1])).handle({
    "type": "goal_decide", "goal_id": sys.argv[2], "revision": int(sys.argv[3]),
    "decision": "approve", "plan_digest": sys.argv[4]})
print(json.dumps(result, ensure_ascii=False))
'''


def goal_status(database, goal_id):
    with sqlite3.connect(str(database), timeout=3) as db:
        row = db.execute("SELECT status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()
    return row[0] if row else None


def recorded_runs(database, goal_id):
    with sqlite3.connect(str(database), timeout=3) as db:
        rows = db.execute("SELECT result_json FROM muse_goal_runs WHERE goal_id=? "
                          "ORDER BY started_at", (goal_id,)).fetchall()
    return [json.loads(row[0]) for row in rows if row[0]]


def listener():
    return subprocess.run(["/usr/sbin/lsof", "-tiTCP:8080", "-sTCP:LISTEN"],
                          capture_output=True, text=True, check=False).stdout.strip()


def capture_window(root, pid, title, stem):
    source = root / f"{stem}-window-id.m"
    source.write_text(WINDOW_ID_SOURCE.replace('@"Muse · GOSIM"', f'@"{title}"'), encoding="utf-8")
    helper = root / f"{stem}-window-id"
    subprocess.run(["/usr/bin/clang", "-fobjc-arc", "-framework", "Cocoa", "-framework", "CoreGraphics",
                    str(source), "-o", str(helper)], check=True, capture_output=True, text=True)
    window_id = subprocess.check_output([str(helper), str(pid)], text=True).strip()
    image = root / f"{stem}.png"
    subprocess.run(["/usr/sbin/screencapture", "-x", "-l", window_id, str(image)], check=True)
    assert image.is_file()
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--package-zip", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--full-chain", action="store_true")
    parser.add_argument("--review-url-gate", action="store_true")
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
    database = workspace / "memory.sqlite3"
    resources = app / "Contents/Resources"
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_SKIP_ONBOARDING="1",
               GOSIM_LOCAL_INBOX="0", PYTHONPATH=str(resources), PYTHONDONTWRITEBYTECODE="1",
               LOCAL_MODEL_URL="http://127.0.0.1:8080/v1/chat/completions")
    subprocess.run([str(resources / "python/bin/python3"), "-B", "-c", SETUP_WATCH,
                    str(workspace), str(selected)], env=env, check=True, capture_output=True, text=True)
    with sqlite3.connect(str(workspace / ".muse-watch-registry.sqlite3"), timeout=3) as db:
        watch_ref = db.execute("SELECT resource_ref FROM watched LIMIT 1").fetchone()[0]
    listener_before = listener()
    assert listener_before, "shared local Qwen listener is absent"
    progress = {"status": "IN_PROGRESS", "source_url": SOURCE,
                "watch_source": "synthetic_preapproved", "watch_ref": watch_ref,
                "shared_qwen_listener_before": listener_before,
                "native_approval_clicked": False, "source_app": str(args.app.resolve()),
                "copied_app": str(app)}
    if args.package_zip:
        progress["package_zip_sha256"] = hashlib.sha256(args.package_zip.read_bytes()).hexdigest()
    result_path = root / "result.json"

    def save():
        result_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n")

    save()
    lock_path = Path("/tmp/gosim-muse-5agent-20260928/gui.lock")
    lock_path.parent.mkdir(mode=0o700, exist_ok=True)
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    lock_held = True
    with (root / "app.stdout").open("w") as stdout, (root / "app.stderr").open("w") as stderr:
        proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                env=env, stdout=stdout, stderr=stderr)
        try:
            wait_for("Muse window", lambda: window_ready(proc.pid))
            time.sleep(0.7)
            ax(proc.pid, 'click pop up button 1 of group 2 of window "Muse · GOSIM"')
            choices = ax(proc.pid, 'get name of menu items of menu 1 of pop up button 1 of group 2 of window "Muse · GOSIM"')
            assert selected.name in choices, choices
            ax(proc.pid, 'click menu item 2 of menu 1 of pop up button 1 of group 2 of window "Muse · GOSIM"')
            ax(proc.pid, 'set value of text field "即时对话输入" of group 2 of window "Muse · GOSIM" to '
               + json.dumps(GOAL, ensure_ascii=False))
            ax(proc.pid, 'click button "设为长期目标" of group 2 of window "Muse · GOSIM"')
            draft = wait_for("real Qwen native Goal draft", lambda: row if (row := goal_row(database)) and
                             row["status"] == "draft" else None, seconds=140)
            goal_id = draft["goal_id"]
            with sqlite3.connect(str(database), timeout=3) as db:
                revision = db.execute("SELECT spec_json,digest FROM muse_goal_revisions WHERE goal_id=? "
                                      "ORDER BY revision DESC LIMIT 1", (goal_id,)).fetchone()
            spec, digest = json.loads(revision[0]), revision[1]
            assert {step["capability"] for step in spec["steps"]} == {
                "web.read", "model.compose", "workspace.write_artifact"}, spec["steps"]
            assert {trigger["kind"] for trigger in spec["triggers"]} == {"interval", "event"}
            assert watch_ref in spec["permissions"]["resource_refs"]
            assert next(step for step in spec["steps"] if step["capability"] == "web.read")["args"]["url"] == SOURCE
            def reviewed_card():
                value = ax(proc.pid, 'get value of text area 1 of scroll area 1 of group 3 of window "Muse · GOSIM"')
                return value if digest in value else None
            card = wait_for("native draft card", reviewed_card, seconds=15)
            assert not list(workspace.glob("notes/*-v1.md")), "artifact before native approval"
            progress.update(goal_id=goal_id, plan_digest=digest, native_draft_reviewed=True,
                            source_url_visible_in_card=SOURCE in card)
            if args.review_url_gate:
                assert SOURCE in card, "full web.read URL absent from native draft card"
                (root / "native-draft-card.txt").write_text(card + "\n", encoding="utf-8")
                capture_window(root, proc.pid, "Muse · GOSIM", "native-draft-card")
                try:
                    ax(proc.pid, 'set value of scroll bar 1 of scroll area 1 of group 3 '
                       'of window "Muse · GOSIM" to 0.35')
                    capture_window(root, proc.pid, "Muse · GOSIM", "native-draft-card-scrolled")
                except AssertionError:
                    pass
                ax(proc.pid, 'click button "查看计划" of group 3 of window "Muse · GOSIM"')
                wait_for("native technical detail window", lambda: ax(
                    proc.pid, 'get name of window "Muse · 技术详情"') == "Muse · 技术详情")
                details = []
                for group in range(1, 5):
                    try:
                        details.append((group, ax(proc.pid, f'get value of text area 1 of scroll area 1 '
                                                            f'of group {group} of window "Muse · 技术详情"')))
                    except AssertionError:
                        continue
                technical_group, technical = next(((group, value) for group, value in details
                                                   if digest in value), (None, ""))
                assert SOURCE in technical, "full web.read URL absent from native technical detail"
                (root / "native-technical-plan.txt").write_text(technical + "\n", encoding="utf-8")
                capture_window(root, proc.pid, "Muse · 技术详情", "native-technical-plan")
                try:
                    ax(proc.pid, f'set value of scroll bar 1 of scroll area 1 of group {technical_group} '
                       'of window "Muse · 技术详情" to 0.35')
                    capture_window(root, proc.pid, "Muse · 技术详情", "native-technical-plan-scrolled")
                except AssertionError:
                    pass
                ax(proc.pid, 'click button 1 of window "Muse · 技术详情"')
                wrong_digest = "0" * 64
                assert wrong_digest != digest
                probe = subprocess.run([str(resources / "python/bin/python3"), "-B", "-c",
                                        PROBE_WRONG_DIGEST, str(workspace), goal_id,
                                        str(draft["revision"]), wrong_digest],
                                       env=env, check=True, capture_output=True, text=True)
                wrong_result = json.loads(probe.stdout)
                assert wrong_result.get("status") == "REJECTED" and wrong_result.get(
                    "error") == "plan_digest_required_or_changed", wrong_result
                assert goal_status(database, goal_id) == "draft"
                assert not list(workspace.glob("notes/*-v1.md"))
                progress.update(technical_details_url_visible=True,
                                native_card_and_technical_digest_visible=True,
                                wrong_digest_rejected=True,
                                wrong_digest_kept_draft_without_artifact=True,
                                wrong_digest_error=wrong_result["error"])
            save()
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_held = False
            ax(proc.pid, 'click button "批准计划" of group 3 of window "Muse · GOSIM"')
            progress["native_approval_clicked"] = True
            save()
            first = wait_for("real Qwen first run", lambda: values[0] if
                             (values := recorded_runs(database, goal_id)) else None, seconds=170)
            assert first.get("status") == "COMPLETED", first
            write = next(item for item in first["receipts"] if item["capability"] == "workspace.write_artifact")
            read = next(item for item in first["receipts"] if item["capability"] == "web.read")
            artifact = workspace / write["output"]["relative_path"]
            sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
            assert read["output"]["source_url"] == SOURCE
            assert sha == write["verification"]["sha256"] and write["verification"]["readback_matches"]
            with sqlite3.connect(str(database), timeout=3) as db:
                approval_digest = db.execute("SELECT approval_digest FROM muse_goals WHERE goal_id=?",
                                             (goal_id,)).fetchone()[0]
            assert approval_digest == digest
            progress.update(v1_run_id=first["run_id"], v1_artifact=write["output"]["relative_path"],
                            v1_sha256=sha, approval_digest_matches=True)
            save()
            if args.full_chain:
                unchanged = wait_for("real Qwen 60 second NO_CHANGE", lambda:
                    next((run for run in recorded_runs(database, goal_id)
                          if run["run_id"] != first["run_id"] and run.get("status") == "NO_CHANGE"), None),
                    seconds=95)
                assert unchanged["model_tokens"] == 0, unchanged
                assert len(list(workspace.glob("notes/*-v*.md"))) == 1
                progress.update(unchanged_run_id=unchanged["run_id"],
                                unchanged_model_tokens=unchanged["model_tokens"])
                save()
                (selected / "synthetic-change.md").write_text("合成验收：新增一项 Python 3.13 资料。\n",
                                                                encoding="utf-8")
                second = wait_for("real Qwen file event v2", lambda:
                    next((run for run in recorded_runs(database, goal_id)
                          if str(run.get("event_id") or "").startswith("file:") and
                          run.get("status") == "COMPLETED"), None), seconds=170)
                second_write = next(item for item in second["receipts"]
                                    if item["capability"] == "workspace.write_artifact")
                second_path = workspace / second_write["output"]["relative_path"]
                second_sha = hashlib.sha256(second_path.read_bytes()).hexdigest()
                assert second_path != artifact and "synthetic-change.md" in second_path.read_text(encoding="utf-8")
                assert second_sha != sha and second_sha == second_write["verification"]["sha256"]
                assert second_write["verification"]["readback_matches"]
                progress.update(v2_run_id=second["run_id"], v2_event_id=second["event_id"],
                                v2_artifact=second_write["output"]["relative_path"], v2_sha256=second_sha)
                save()
            wait_for("native pause button", lambda: "暂停目标" in ax(proc.pid,
                'get name of buttons of group 3 of window "Muse · GOSIM"'), seconds=15)
            ax(proc.pid, 'click button "暂停目标" of group 3 of window "Muse · GOSIM"')
            wait_for("native paused", lambda: goal_status(database, goal_id) == "paused")
            progress["native_paused"] = True
            save()
            if args.full_chain:
                run_count_before_restart = len(recorded_runs(database, goal_id))
                proc.terminate()
                proc.wait(timeout=8)
                proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                        env=env, stdout=stdout, stderr=stderr)
                wait_for("restarted Muse window", lambda: window_ready(proc.pid))
                assert goal_status(database, goal_id) == "paused"
                assert len(recorded_runs(database, goal_id)) == run_count_before_restart
                progress["native_paused_survived_restart"] = True
                save()
            wait_for("native resume button", lambda: "继续目标" in ax(proc.pid,
                'get name of buttons of group 3 of window "Muse · GOSIM"'), seconds=15)
            ax(proc.pid, 'click button "继续目标" of group 3 of window "Muse · GOSIM"')
            wait_for("native resumed", lambda: goal_status(database, goal_id) == "active")
            progress["native_resumed"] = True
            save()
            ax(proc.pid, 'click button "取消目标" of group 3 of window "Muse · GOSIM"')
            wait_for("native cancelled", lambda: goal_status(database, goal_id) == "cancelled")
            progress["native_cancelled"] = True
            if args.full_chain:
                run_count_before_cancel_restart = len(recorded_runs(database, goal_id))
                proc.terminate()
                proc.wait(timeout=8)
                proc = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent")],
                                        env=env, stdout=stdout, stderr=stderr)
                wait_for("cancelled Muse restart", lambda: window_ready(proc.pid))
                time.sleep(5)
                assert goal_status(database, goal_id) == "cancelled"
                assert len(recorded_runs(database, goal_id)) == run_count_before_cancel_restart
                progress["native_cancelled_survived_restart"] = True
            progress["shared_qwen_listener_after"] = listener()
            assert progress["shared_qwen_listener_after"] == listener_before
            usage_path = workspace / ".muse_model_usage.json"
            usage = json.loads(usage_path.read_text()) if usage_path.exists() else {}
            assert usage.get("remote_calls", 0) == 0 and not usage.get("reservations"), usage
            settings_path = workspace / ".muse_model_settings.json"
            settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
            assert all(not item.get("keychain_service")
                       for item in settings.get("profiles", {}).values()), settings
            progress["remote_calls"] = 0
        except Exception as exc:
            progress.update(status="FAIL", error=f"{type(exc).__name__}: {exc}"[:700])
            save()
            raise
        finally:
            if lock_held:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            if proc.poll() is None:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
            time.sleep(1)
            subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
    progress["signature_valid_after"] = True
    progress["status"] = ("PASS_REVIEW_URL_GATE" if args.review_url_gate else
                          "PASS_LIVE_WITH_REVIEW_GAP" if args.full_chain and
                          not progress["source_url_visible_in_card"] else "PASS_LIVE")
    save()
    print(json.dumps(progress, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
