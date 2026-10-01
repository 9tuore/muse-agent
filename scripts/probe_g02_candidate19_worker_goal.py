"""Run one candidate19 packaged worker Goal with local Qwen and synthetic folder events."""

import argparse
import hashlib
import json
import os
import queue
import sqlite3
import subprocess
import tempfile
import threading
import time
from pathlib import Path


SOURCE = "https://docs.python.org/zh-cn/3.13/whatsnew/3.13.html"
REQUEST = (f"持续关注 {SOURCE} 的公开资料变化，整理一份中文 Python 3.13 资料提纲并注明来源。"
           "当我选定的合成资料目录有文件变化时，更新同一个提纲。")


class Worker:
    def __init__(self, resources, workspace, home):
        env = dict(os.environ, HOME=str(home), PYTHONPATH=str(resources),
                   PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                   GOSIM_LOCAL_INBOX="0",
                   LOCAL_MODEL_URL="http://127.0.0.1:8080/v1/chat/completions")
        self.process = subprocess.Popen(
            [str(resources / "python/bin/python3"), "-B",
             str(resources / "desktop_worker.py"), str(workspace)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, env=env)
        self.events = queue.Queue()
        self.errors = []
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.err_reader = threading.Thread(target=self._read_error, daemon=True)
        self.reader.start()
        self.err_reader.start()

    def _read(self):
        for line in self.process.stdout:
            if line.startswith("{"):
                try:
                    self.events.put(json.loads(line))
                except json.JSONDecodeError:
                    self.errors.append("invalid_worker_json")

    def _read_error(self):
        for line in self.process.stderr:
            self.errors.append(line.strip()[:300])

    def send(self, event):
        self.process.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

    def wait(self, predicate, *, timeout, seen):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                item = self.events.get(timeout=max(0.0, min(1.0, deadline - time.monotonic())))
            except queue.Empty:
                if self.process.poll() is not None:
                    raise AssertionError({"worker_exited": self.process.returncode,
                                          "stderr": self.errors[-5:]})
                continue
            seen.append(item)
            if predicate(item):
                return item
        raise AssertionError({"timed_out": timeout, "last_events": seen[-4:],
                              "stderr": self.errors[-5:]})

    def ask(self, event, predicate, *, timeout, seen):
        self.send(event)
        return self.wait(predicate, timeout=timeout, seen=seen)

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=8)
        self.reader.join(timeout=1)
        self.err_reader.join(timeout=1)
        if self.process.returncode != 0 or self.errors:
            raise AssertionError({"worker_exit": self.process.returncode,
                                  "stderr": self.errors[-6:]})


def listener():
    return subprocess.run(["/usr/sbin/lsof", "-tiTCP:8080", "-sTCP:LISTEN"],
                          capture_output=True, text=True, check=False).stdout.strip()


def runs(database, goal_id):
    with sqlite3.connect(database, timeout=5) as db:
        rows = db.execute("SELECT result_json FROM muse_goal_runs WHERE goal_id=? "
                          "ORDER BY started_at", (goal_id,)).fetchall()
    return [json.loads(row[0]) for row in rows if row[0]]


def artifact(workspace, run):
    receipt = next(item for item in run["receipts"]
                   if item.get("capability") == "workspace.write_artifact")
    relative_path = receipt["output"]["relative_path"]
    file_path = workspace / relative_path
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    assert digest == receipt["verification"]["sha256"] and receipt["verification"]["readback_matches"]
    return {"relative_path": relative_path, "disk_sha256": digest,
            "receipt_sha256": receipt["verification"]["sha256"],
            "bytes": file_path.stat().st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_app", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    resources = args.package_app.resolve(strict=True) / "Contents/Resources"
    root = Path(tempfile.mkdtemp(prefix="gosim-g02-c19-worker-goal-"))
    workspace, selected, home = (root / name for name in ("workspace", "selected", "home"))
    for path in (workspace, selected, home):
        path.mkdir()
    database = workspace / "memory.sqlite3"
    before_listener = listener()
    assert before_listener, "local_qwen_listener_absent"
    seen = []
    phase = "start"
    result = {"status": "IN_PROGRESS", "package_app": str(args.package_app),
              "workspace": str(workspace), "selected": str(selected),
              "approval_actor": "synthetic_host_decision", "source_url": SOURCE,
              "qwen_listener_before": before_listener}

    def save():
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")

    save()
    worker = Worker(resources, workspace, home)
    try:
        phase = "watch_and_propose"
        watch = worker.ask({"type": "watch_folder_set", "path": str(selected), "approved": True},
                           lambda item: item.get("status") == "SAVED" and "watch" in item,
                           timeout=20, seen=seen)
        watch_ref = watch["watch"]["resource_ref"]
        draft = worker.ask({"type": "goal_propose", "request_id": "g02-c19-real-qwen-goal",
                            "text": REQUEST,
                            "context_refs": [{"ref": watch_ref,
                                              "purpose": "用户选定的隔离合成资料目录"}]},
                           lambda item: item.get("status") in {"DRAFT", "REJECTED", "INVALID_PLAN"}
                           and "goal_id" in item, timeout=150, seen=seen)
        assert draft["status"] == "DRAFT", draft
        goal_id, digest = draft["goal_id"], draft["plan_digest"]
        spec = draft["plan"]
        assert {step["capability"] for step in spec["steps"]} == {
            "web.read", "model.compose", "workspace.write_artifact"}
        assert {trigger["kind"] for trigger in spec["triggers"]} == {"interval", "event"}
        assert watch_ref in spec["permissions"]["resource_refs"]
        assert next(step for step in spec["steps"] if step["capability"] == "web.read")["args"]["url"] == SOURCE
        assert not list(workspace.glob("notes/*-v*.md"))
        result.update(goal_id=goal_id, plan_digest=digest, watch_ref=watch_ref,
                      plan_capabilities=[step["capability"] for step in spec["steps"]])
        save()

        phase = "digest_and_v1"
        wrong = worker.ask({"type": "goal_decide", "goal_id": goal_id, "revision": 1,
                            "decision": "approve", "plan_digest": "0" * 64},
                           lambda item: item.get("status") == "REJECTED" and
                           item.get("error") == "plan_digest_required_or_changed",
                           timeout=20, seen=seen)
        with sqlite3.connect(database, timeout=5) as db:
            assert db.execute("SELECT status FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone()[0] == "draft"
            assert db.execute("SELECT COUNT(*) FROM muse_goal_approvals WHERE goal_id=?",
                              (goal_id,)).fetchone()[0] == 0
        assert not list(workspace.glob("notes/*-v*.md"))
        approved = worker.ask({"type": "goal_decide", "goal_id": goal_id, "revision": 1,
                               "decision": "approve", "plan_digest": digest},
                              lambda item: item.get("status") == "ACTIVE" and
                              item.get("goal_id") == goal_id, timeout=20, seen=seen)
        first = worker.wait(lambda item: item.get("goal_id") == goal_id and
                            item.get("status") in {"COMPLETED", "WAITING_USER"} and "run_id" in item,
                            timeout=190, seen=seen)
        assert first["status"] == "COMPLETED" and first["verification"] == "CHECKS_PASSED", first
        read = next(item for item in first["receipts"] if item["capability"] == "web.read")
        assert read["output"]["source_url"] == SOURCE
        v1 = artifact(workspace, first)
        result.update(wrong_digest_error=wrong["error"], approval_id=approved["approval_id"],
                      v1_run_id=first["run_id"], v1=v1, v1_model_tokens=first["model_tokens"])
        save()

        phase = "no_change"
        unchanged = worker.wait(lambda item: item.get("goal_id") == goal_id and
                                item.get("status") in {"NO_CHANGE", "WAITING_USER"} and
                                item.get("run_id") != first["run_id"], timeout=100, seen=seen)
        assert unchanged["status"] == "NO_CHANGE" and unchanged["model_tokens"] == 0, unchanged
        assert len(list(workspace.glob("notes/*-v*.md"))) == 1
        result.update(no_change_run_id=unchanged["run_id"],
                      no_change_model_tokens=unchanged["model_tokens"])
        save()

        phase = "event_v2"
        (selected / "synthetic-change.md").write_text(
            "合成验收：新增一项 Python 3.13 资料。\n", encoding="utf-8")
        second = worker.wait(lambda item: item.get("goal_id") == goal_id and
                             str(item.get("event_id") or "").startswith("file:") and
                             item.get("status") in {"COMPLETED", "WAITING_USER"},
                             timeout=190, seen=seen)
        assert second["status"] == "COMPLETED" and second["verification"] == "CHECKS_PASSED", second
        v2 = artifact(workspace, second)
        assert v2["relative_path"] != v1["relative_path"] and v2["disk_sha256"] != v1["disk_sha256"]
        assert "synthetic-change.md" in (workspace / v2["relative_path"]).read_text(encoding="utf-8")
        result.update(v2_run_id=second["run_id"], v2_event_id=second["event_id"], v2=v2)
        save()

        phase = "pause_restart_cancel"
        paused = worker.ask({"type": "goal_control", "goal_id": goal_id, "action": "pause"},
                            lambda item: item.get("goal_id") == goal_id and item.get("status") == "PAUSED",
                            timeout=20, seen=seen)
        worker.close()
        count_at_pause = len(runs(database, goal_id))
        worker = Worker(resources, workspace, home)
        after_restart = worker.ask({"type": "goal_get", "goal_id": goal_id},
                                   lambda item: item.get("goal_id") == goal_id and
                                   item.get("status") == "PAUSED", timeout=20, seen=seen)
        assert len(runs(database, goal_id)) == count_at_pause
        resumed = worker.ask({"type": "goal_control", "goal_id": goal_id, "action": "resume"},
                             lambda item: item.get("goal_id") == goal_id and item.get("status") == "ACTIVE",
                             timeout=20, seen=seen)
        cancelled = worker.ask({"type": "goal_control", "goal_id": goal_id, "action": "cancel"},
                               lambda item: item.get("goal_id") == goal_id and
                               item.get("status") == "CANCELLED", timeout=20, seen=seen)
        worker.close()
        worker = Worker(resources, workspace, home)
        after_cancel = worker.ask({"type": "goal_get", "goal_id": goal_id},
                                  lambda item: item.get("goal_id") == goal_id and
                                  item.get("status") == "CANCELLED", timeout=20, seen=seen)
        time.sleep(4)
        assert len(runs(database, goal_id)) == count_at_pause
        result.update(paused=paused["status"], paused_after_restart=after_restart["status"],
                      resumed=resumed["status"], cancelled=cancelled["status"],
                      cancelled_after_restart=after_cancel["status"])
        save()

        phase = "memory_and_database"
        claim = worker.ask({"type": "memory_claim_get", "claim_id": "memory:" + first["run_id"]},
                           lambda item: item.get("status") in {"READY", "NOT_FOUND"} and
                           ("claim" in item or item.get("status") == "NOT_FOUND"),
                           timeout=20, seen=seen)
        assert claim["status"] == "READY", claim
        document = claim["claim"]["document"]
        sources = claim["claim"]["sources"]
        assert document["origin"] == {"type": "local_runtime", "ref": "muse-goal-service"}
        assert any(source.get("kind") == "url" and source.get("locator") == SOURCE and
                   source.get("content_sha256") == read["output"]["content_sha256"]
                   for source in sources), sources
        with sqlite3.connect(database, timeout=5) as db:
            db.row_factory = sqlite3.Row
            goal_row = dict(db.execute("SELECT status,approval_id,approval_digest,next_due,pending_event_id,"
                                       "run_count FROM muse_goals WHERE goal_id=?", (goal_id,)).fetchone())
            approval = dict(db.execute("SELECT approval_id,digest FROM muse_goal_approvals WHERE goal_id=?",
                                       (goal_id,)).fetchone())
            search_receipt_rows = db.execute("SELECT COUNT(*) FROM muse_action_receipts WHERE run_id IN "
                                             "(SELECT run_id FROM muse_goal_runs WHERE goal_id=?)",
                                             (goal_id,)).fetchone()[0]
            integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        all_runs = runs(database, goal_id)
        receipt_count = sum(len(item["receipts"]) for item in all_runs)
        assert [item["status"] for item in all_runs] == ["COMPLETED", "NO_CHANGE", "COMPLETED"]
        assert [[receipt["capability"] for receipt in item["receipts"]] for item in all_runs] == [
            ["web.read", "model.compose", "workspace.write_artifact"], ["web.read"],
            ["web.read", "model.compose", "workspace.write_artifact"]]
        assert goal_row["status"] == "cancelled" and goal_row["next_due"] is None
        assert goal_row["pending_event_id"] is None and goal_row["run_count"] == 3
        assert goal_row["approval_id"] == approval["approval_id"] == approved["approval_id"]
        assert goal_row["approval_digest"] == approval["digest"] == digest
        assert receipt_count == 7 and search_receipt_rows == 0 and integrity == "ok"
        assert listener() == before_listener
        usage_path = workspace / ".muse_model_usage.json"
        usage = json.loads(usage_path.read_text()) if usage_path.exists() else {}
        assert usage.get("remote_calls", 0) == 0 and not usage.get("reservations")
        result.update(status="PASS_LOCAL_REAL_QWEN", phase=phase, run_statuses=[r["status"] for r in all_runs],
                      goal_row=goal_row, goal_run_receipt_count=receipt_count,
                      web_search_receipt_rows=search_receipt_rows,
                      memory_origin=document["origin"], memory_source_count=len(sources),
                      memory_url_source_verified=True, sqlite_integrity=integrity,
                      qwen_listener_after=listener(), remote_calls=0)
        save()
    except Exception as exc:
        result.update(status="FAIL", phase=phase, error=f"{type(exc).__name__}: {exc}"[:1200],
                      worker_stderr=worker.errors[-6:])
        save()
        raise
    finally:
        worker.close()
    print(json.dumps({"status": result["status"], "goal_id": result.get("goal_id"),
                      "run_statuses": result.get("run_statuses"), "output": str(args.output)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
