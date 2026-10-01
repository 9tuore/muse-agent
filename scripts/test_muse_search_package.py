#!/usr/bin/env python3
"""Exercise an approved no-URL research Goal in a copied packaged worker."""

import argparse
import hashlib
import json
import os
import plistlib
import queue
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


GOAL_TEXT = "持续整理 Python 3.13 公开资料，写中文提纲并注明来源。"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_codesign(path):
    result = subprocess.run(["codesign", "--verify", "--deep", "--strict", "--verbose=2", str(path)],
                            capture_output=True, text=True)
    return {"ok": result.returncode == 0, "exit_code": result.returncode,
            "detail": (result.stderr or result.stdout).strip()[:500]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--goal-text", default=GOAL_TEXT)
    args = parser.parse_args()
    source = args.app.resolve(strict=True)
    root = args.output_dir.resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="muse-search-package-"))
    root.mkdir(parents=True, exist_ok=True)
    copied = root / "Muse-Search-Test.app"
    if copied.exists():
        raise SystemExit("output_app_already_exists")
    shutil.copytree(source, copied, symlinks=True)
    resources = copied / "Contents/Resources"
    worker_path = resources / "desktop_worker.py"
    python_path = resources / "python/bin/python3"
    binary_path = copied / "Contents/MacOS/GOSIM-Local-Agent"
    if not all(path.is_file() for path in (worker_path, python_path, binary_path)):
        raise SystemExit("packaged_runtime_missing")
    workspace = root / "workspace"
    workspace.mkdir()
    info = plistlib.loads((copied / "Contents/Info.plist").read_bytes())
    build_info_path = resources / "muse_build_info.json"
    build_info = json.loads(build_info_path.read_text(encoding="utf-8")) if build_info_path.is_file() else {}
    if build_info and (build_info.get("source_sha256", {}).get("app/desktop_worker.py") != sha256(worker_path)
                       or build_info.get("source_sha256", {}).get("app/agent_app.py") !=
                       sha256(resources / "agent_app.py")):
        raise AssertionError("package_build_info_source_mismatch")
    distribution_zip = source.parent / "GOSIM-Local-Agent-macOS.zip"
    started = time.monotonic()
    record = {"test_id": "G02-PACKAGED-QWEN-NO-URL-SEARCH", "phase": "A",
              "actual_started_at": datetime.now(timezone.utc).isoformat(),
              "app_version": info.get("CFBundleShortVersionString"),
              "runner_commit": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
                  text=True).strip(),
              "package_source_commit": build_info.get("source_commit", "NOT_EMBEDDED"),
              "app_binary_sha256": sha256(binary_path), "worker_sha256": sha256(worker_path),
              "package_sha": sha256(distribution_zip) if distribution_zip.is_file() else None,
              "evidence_type": "LIVE_PACKAGED_LOCAL_MODEL_PUBLIC_WEB",
              "preconditions": "copied app, fresh isolated workspace, localhost Qwen, public web",
              "input": args.goal_text, "workspace": str(workspace), "copied_app": str(copied),
              "evidence_path": str(root / "result.json")}
    environment = dict(os.environ, GOSIM_LOCAL_INBOX="0", PYTHONUNBUFFERED="1",
                       PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                       LOCAL_MODEL_URL="http://127.0.0.1:8080/v1/chat/completions")
    frames = queue.Queue()
    worker = None
    observed = []
    with (root / "worker.stderr").open("w") as stderr:
        try:
            record["codesign_before"] = strict_codesign(copied)
            if not record["codesign_before"]["ok"]:
                raise AssertionError("copied_app_signature_invalid_before")
            worker = subprocess.Popen([str(python_path), "-B", str(worker_path), str(workspace)],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                                      text=True, bufsize=1, cwd=str(root), env=environment)
            record["worker_pid"] = worker.pid

            def read_frames():
                for line in worker.stdout:
                    try:
                        frames.put(json.loads(line))
                    except ValueError:
                        frames.put({"status": "NON_JSON_FRAME"})

            threading.Thread(target=read_frames, daemon=True).start()

            def send(event):
                worker.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
                worker.stdin.flush()

            def await_result(predicate, timeout):
                for item in observed:
                    if predicate(item):
                        return item
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    try:
                        item = frames.get(timeout=min(1, max(0.01, deadline - time.monotonic())))
                    except queue.Empty:
                        if worker.poll() is not None:
                            raise AssertionError("packaged_worker_exited_early")
                        continue
                    observed.append(item)
                    if predicate(item):
                        return item
                raise AssertionError("packaged_worker_response_timeout")

            send({"type": "goal_propose", "request_id": "packaged-no-url-research-1", "text": args.goal_text})
            draft = await_result(lambda item: item.get("status") in
                                 {"DRAFT", "INVALID_PLAN", "MODEL_UNAVAILABLE", "NEEDS_SCOPE"}, 140)
            record["draft_status"] = draft.get("status")
            record["draft_error"] = draft.get("error")
            if draft.get("status") != "DRAFT":
                raise AssertionError("draft_not_ready")
            record["goal_id"] = draft["goal_id"]
            record["revision"] = draft["revision"]
            record["plan_digest"] = draft["plan_digest"]
            search_steps = [step for step in draft["plan"]["steps"] if step["capability"] == "web.search"]
            reads = [step for step in draft["plan"]["steps"] if step["capability"] == "web.read"]
            if len(search_steps) != 1 or [step["args"].get("selected_rank") for step in reads] != list(range(5)):
                raise AssertionError("five_candidate_plan_missing")
            record["search_query"] = search_steps[0]["args"]["query"]
            if list(workspace.rglob("*.md")):
                raise AssertionError("artifact_before_approval")
            send({"type": "goal_decide", "goal_id": draft["goal_id"],
                  "revision": draft["revision"], "decision": "approve", "plan_digest": "0" * 64})
            wrong_digest = await_result(lambda item: item.get("status") == "REJECTED" or
                                        (item.get("goal_id") == draft["goal_id"] and
                                         item.get("status") == "ACTIVE"), 20)
            record["wrong_digest_error"] = wrong_digest.get("error")
            if wrong_digest.get("status") != "REJECTED" or wrong_digest.get("error") != "plan_digest_required_or_changed":
                raise AssertionError("wrong_plan_digest_accepted")
            if list(workspace.rglob("*.md")):
                raise AssertionError("artifact_after_wrong_digest")
            send({"type": "goal_decide", "goal_id": draft["goal_id"],
                  "revision": draft["revision"], "decision": "approve",
                  "plan_digest": draft["plan_digest"]})
            approved = await_result(lambda item: item.get("goal_id") == draft["goal_id"] and
                                    item.get("status") in {"ACTIVE", "REJECTED"}, 20)
            record["approval_status"] = approved.get("status")
            if approved.get("status") != "ACTIVE":
                raise AssertionError("approval_not_active")
            result = await_result(lambda item: item.get("goal_id") == draft["goal_id"] and
                                  item.get("status") in {"COMPLETED", "WAITING_USER", "BLOCKED", "FAILED"}, 170)
            record.update(run_id=result.get("run_id"), run_status=result.get("status"),
                          run_error=result.get("error"), failure=result.get("failure"),
                          source_failures=result.get("source_failures"), source_skips=result.get("source_skips"),
                          fact_verification=result.get("fact_verification"))
            accepted = [item for item in result.get("receipts", [])
                        if item.get("capability") == "web.read" and item.get("accepted_source") is True]
            record["accepted_source_urls"] = [item["output"]["source_url"] for item in accepted]
            writes = [item for item in result.get("receipts", [])
                      if item.get("capability") == "workspace.write_artifact"]
            if result.get("status") != "COMPLETED" or len(accepted) != 3 or len(writes) != 1:
                raise AssertionError("three_source_report_not_completed")
            saved = writes[0]
            path = workspace / saved["output"]["relative_path"]
            content = path.read_bytes()
            if (hashlib.sha256(content).hexdigest() != saved["verification"]["sha256"] or
                saved["verification"].get("readback_matches") is not True or
                result.get("fact_verification") != "NOT_VERIFIED"):
                raise AssertionError("artifact_verification_failed")
            report = content.decode("utf-8")
            if "## 来源清单" not in report or "未逐字审阅网页全文" not in report or any(
                url not in report for url in record["accepted_source_urls"]
            ):
                raise AssertionError("source_report_incomplete")
            record.update(result="PASS_LIVE", artifact=str(path), artifact_sha256=sha256(path),
                          independent_observation="packaged worker wrote and read back three-source report")
        except Exception as exc:
            record.update(result="FAIL", test_error=type(exc).__name__ + ":" + str(exc)[:160],
                          independent_observation="See draft/run status and worker stderr")
        finally:
            if worker is not None:
                worker.terminate()
                try:
                    worker.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    worker.kill()
                    worker.wait(timeout=5)
            record["codesign_after"] = strict_codesign(copied)
            if not record["codesign_after"]["ok"]:
                record.update(result="FAIL", test_error="copied_app_signature_invalid_after",
                              independent_observation="See codesign_before and codesign_after")
            record["actual_finished_at"] = datetime.now(timezone.utc).isoformat()
            record["duration_seconds"] = round(time.monotonic() - started, 3)
            record["cleanup"] = "copied worker stopped; shared Qwen and production workspace untouched"
            (root / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))
    raise SystemExit(0 if record["result"] == "PASS_LIVE" else 1)


if __name__ == "__main__":
    main()
