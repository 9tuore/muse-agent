#!/usr/bin/env python3
"""Independent real-Qwen/public-source check of the worker inside a copied app."""

import argparse
import hashlib
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


SOURCE_URL = "https://www.python.org/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--folder-update", action="store_true",
                        help="Also prove a selected-folder event updates the same research goal")
    parser.add_argument("--wait-unchanged-interval", action="store_true",
                        help="Wait for a real 60-second unchanged-source cycle before the file event")
    args = parser.parse_args()
    source_url = args.source_url
    goal_text = f"持续关注 {source_url} 的公开资料变化，整理一份中文 Python 资料提纲并注明来源。"
    if args.wait_unchanged_interval and not args.folder_update:
        parser.error("--wait-unchanged-interval requires --folder-update")
    app = args.app.resolve(strict=True)
    if not (app / "Contents/Resources/desktop_worker.py").is_file():
        raise SystemExit("packaged_worker_missing")
    started_at = datetime.now(timezone.utc).isoformat()
    app_binary = app / "Contents/MacOS/GOSIM-Local-Agent"
    app_binary_sha256 = hashlib.sha256(app_binary.read_bytes()).hexdigest()
    worker_sha256 = hashlib.sha256((app / "Contents/Resources/desktop_worker.py").read_bytes()).hexdigest()
    root = args.output_dir.resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="muse-research-package-"))
    root.mkdir(parents=True, exist_ok=True)
    copied = root / "Muse-Research-Test.app"
    if copied.exists():
        raise SystemExit("output_app_already_exists")
    shutil.copytree(app, copied, symlinks=True)
    workspace = root / "workspace"
    workspace.mkdir()
    selected = root / "selected"
    if args.folder_update:
        selected.mkdir()
    frames = queue.Queue()
    worker_path = copied / "Contents/Resources/desktop_worker.py"
    packaged_python = copied / "Contents/Resources/python/bin/python3"
    if not packaged_python.is_file():
        raise SystemExit("packaged_python_missing")
    environment = dict(os.environ, GOSIM_LOCAL_INBOX="0", PYTHONUNBUFFERED="1",
                       PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                       LOCAL_MODEL_URL="http://127.0.0.1:8080/v1/chat/completions")
    with (root / "worker.stderr").open("w") as stderr:
        worker = subprocess.Popen([str(packaged_python), "-B", str(worker_path), str(workspace)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                                  text=True, bufsize=1, cwd=str(root), env=environment)

        def read_frames():
            for line in worker.stdout:
                try:
                    frames.put(json.loads(line))
                except ValueError:
                    frames.put({"status": "NON_JSON_FRAME"})

        threading.Thread(target=read_frames, daemon=True).start()
        observed = []

        def send(event):
            worker.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
            worker.stdin.flush()

        def await_result(predicate, timeout):
            for record in observed:
                if predicate(record):
                    return record
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    record = frames.get(timeout=min(1, deadline - time.monotonic()))
                except queue.Empty:
                    if worker.poll() is not None:
                        raise AssertionError("packaged_worker_exited_early")
                    continue
                observed.append(record)
                if predicate(record):
                    return record
            raise AssertionError("packaged_worker_response_timeout:" + str(observed[-3:]))

        try:
            ref = "resource:public-url-" + hashlib.sha256(source_url.encode()).hexdigest()[:16]
            refs = [{"ref": ref, "purpose": "合成验收公开网页", "url": source_url}]
            text = goal_text
            if args.folder_update:
                send({"type": "watch_folder_set", "path": str(selected), "approved": True})
                watch = await_result(lambda item: item.get("status") in {"SAVED", "REJECTED"}, 20)
                assert watch["status"] == "SAVED", watch
                refs.append({"ref": watch["watch"]["resource_ref"], "purpose": "已选合成资料目录"})
                text += "当我选定的合成资料目录有文件变化时，更新同一个提纲。"
            send({"type": "goal_propose", "request_id": "packaged-research-1", "text": text,
                  "context_refs": refs})
            draft = await_result(lambda item: item.get("status") in {"DRAFT", "INVALID_PLAN", "MODEL_UNAVAILABLE", "NEEDS_SCOPE"}, 140)
            assert draft["status"] == "DRAFT", draft
            goal_id = draft["goal_id"]
            assert draft["approval_id"] is None
            assert any(step["capability"] == "web.read" for step in draft["plan"]["steps"])
            if args.folder_update:
                assert {trigger["kind"] for trigger in draft["plan"]["triggers"]} == {"interval", "event"}
            assert not list(workspace.rglob("*.md")), "artifact_before_approval"
            send({"type": "goal_decide", "goal_id": goal_id,
                  "revision": draft["revision"], "decision": "approve",
                  "plan_digest": draft["plan_digest"]})
            approved = await_result(lambda item: item.get("goal_id") == goal_id and item.get("status") == "ACTIVE", 20)
            assert approved["approval_id"].startswith("approval:"), approved
            result = await_result(lambda item: item.get("goal_id") == goal_id and item.get("status") in
                                  {"COMPLETED", "WAITING_USER", "BLOCKED", "FAILED"}, 170)
            assert result["status"] == "COMPLETED", result
            receipts = result["receipts"]
            read = next(item for item in receipts if item["capability"] == "web.read")
            saved = next(item for item in receipts if item["capability"] == "workspace.write_artifact")
            assert read["output"]["source_url"] == source_url
            source_text = read["output"]["text"]
            assert read["output"].get("title") and "Python" in read["output"]["title"]
            assert len(source_text) > 500 and "Python" in source_text
            assert "\ufffd" not in source_text
            assert not any(ord(char) < 32 and char not in "\n\r\t" for char in source_text)
            path = workspace / saved["output"]["relative_path"]
            content = path.read_bytes()
            assert hashlib.sha256(content).hexdigest() == saved["verification"]["sha256"]
            assert saved["verification"]["readback_matches"] is True
            assert source_url.encode() in content
            assert "## 来源清单".encode() in content
            assert "事实待核验".encode() in content
            interval_result = None
            second = None
            if args.folder_update:
                if args.wait_unchanged_interval:
                    interval_result = await_result(lambda item: item.get("goal_id") == goal_id and
                                                   item.get("run_id") != result["run_id"] and
                                                   item.get("status") in {"NO_CHANGE", "COMPLETED", "WAITING_USER"}, 85)
                    assert interval_result["status"] == "NO_CHANGE", interval_result
                    assert interval_result["model_tokens"] == 0, interval_result
                else:
                    time.sleep(3)  # Let the resident watcher establish a real baseline.
                (selected / "synthetic-change.md").write_text("合成验收：新增一项资料。\n", encoding="utf-8")
                second = await_result(lambda item: item.get("goal_id") == goal_id and
                                      str(item.get("event_id") or "").startswith("file:") and
                                      item.get("status") in {"COMPLETED", "WAITING_USER", "BLOCKED"}, 170)
                assert second["status"] == "COMPLETED", second
                written = next(item for item in second["receipts"]
                               if item["capability"] == "workspace.write_artifact")
                second_path = workspace / written["output"]["relative_path"]
                assert second_path != path and second_path.is_file()
                assert "synthetic-change.md" in second_path.read_text(encoding="utf-8")
                assert hashlib.sha256(second_path.read_bytes()).hexdigest() == written["verification"]["sha256"]
            print(json.dumps({"status": "PASS", "started_at": started_at,
                              "finished_at": datetime.now(timezone.utc).isoformat(),
                              "app": str(copied), "source_app_binary_sha256": app_binary_sha256,
                              "source_packaged_worker_sha256": worker_sha256,
                              "packaged_python_sha256": hashlib.sha256(packaged_python.read_bytes()).hexdigest(),
                              "worker_pid": worker.pid,
                              "workspace": str(workspace), "goal_id": goal_id,
                              "plan_revision": draft["revision"],
                              "plan_digest": draft["plan_digest"],
                              "planning_model": draft.get("model"),
                              "approval_id": approved["approval_id"], "run_id": result["run_id"],
                              "run_model_tokens": result["model_tokens"],
                              "artifact": str(path), "artifact_sha256": saved["verification"]["sha256"],
                              "second_run_id": second["run_id"] if second else None,
                              "unchanged_interval_run_id": interval_result["run_id"] if interval_result else None,
                              "second_event_id": second["event_id"] if second else None,
                              "same_goal_second_version": second is not None,
                              "source_url": source_url, "source_retrieved_at": read["output"]["retrieved_at"],
                              "source_title": read["output"]["title"],
                              "source_text_length": len(source_text),
                              "source_replacement_chars": source_text.count("\ufffd"),
                              "readback_matches": True}, ensure_ascii=False))
        finally:
            worker.terminate()
            try:
                worker.wait(timeout=5)
            except subprocess.TimeoutExpired:
                worker.kill()
                worker.wait(timeout=5)


if __name__ == "__main__":
    main()
