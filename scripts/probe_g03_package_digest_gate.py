#!/usr/bin/env python3
"""Check a signed package's non-recipe Goal digest gate without GUI or Qwen."""

import argparse
import hashlib
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", required=True, type=Path)
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    app = args.app.resolve(strict=True)
    resources = app / "Contents/Resources"
    python = resources / "python/bin/python3"
    worker = resources / "desktop_worker.py"
    helper = resources / "muse_ax_helper"
    for path in (python, worker, helper):
        if not path.is_file():
            raise AssertionError("missing_package_resource:" + str(path))

    def signatures():
        for command in (["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)],
                        ["/usr/bin/codesign", "--verify", "--strict", str(helper)]):
            subprocess.run(command, check=True, capture_output=True, text=True)

    signatures()
    sys.path.insert(0, str(resources))
    from muse_goal_store import GoalStore
    from muse_goals import validate_plan

    workspace = Path(tempfile.mkdtemp(prefix="gosim-g03-digest-package-"))
    relative_path = "notes/Muse-Test-Digest-Gate.txt"
    content = "Muse exact digest package check.\n"
    resource_ref = "resource:workspace/" + relative_path
    goal_id = "goal:g03-package-digest-" + uuid.uuid4().hex
    plan = {
        "schema_version": "muse.goal/0.1", "goal_id": goal_id, "revision": 1,
        "title": "隔离文件摘要门禁", "objective": "只写入合成验证文件",
        "priority": "normal", "deadline": None, "timezone": "Asia/Shanghai",
        "triggers": [{"kind": "interval", "every_seconds": 60}],
        "context_refs": [{"ref": resource_ref, "purpose": "仅写入合成文件"}],
        "steps": [{"id": "save", "capability": "workspace.write_artifact",
                   "args": {"relative_path": relative_path, "content": content}}],
        "permissions": {"capabilities": ["workspace.write_artifact"],
                        "resource_refs": [resource_ref], "send_message": "deny",
                        "send_rule_ref": None, "cloud_context": "none"},
        "budget": {"period": "goal", "money": {"mode": "capped", "currency": "CNY", "amount": 0},
                   "max_model_tokens": 0, "max_searches": 0, "max_run_seconds": 90},
        "verification": [{"type": "record_readback", "target_ref": "step:save",
                          "expected": {"readback_matches": True}}],
        "notify": {"on_major_update": True, "on_need_decision": True, "on_complete": True},
        "failure_policy": {"max_retries": 0, "escalate": True},
    }
    validate_plan(plan)
    store = GoalStore(workspace)
    draft = store.save_draft(plan, "g03-digest-" + goal_id, {"provider": "host_fixture"})
    artifact = workspace / relative_path
    env = dict(os.environ, PYTHONPATH=str(resources), PYTHONNOUSERSITE="1",
               PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1", GOSIM_LOCAL_INBOX="0")
    process = subprocess.Popen([str(python), "-B", str(worker), str(workspace)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
    frames = queue.Queue()
    threading.Thread(target=lambda: [frames.put(json.loads(line)) for line in process.stdout],
                     daemon=True).start()

    def send(event):
        process.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
        process.stdin.flush()

    def until(predicate, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                item = frames.get(timeout=0.2)
            except queue.Empty:
                if process.poll() is not None:
                    raise AssertionError("worker_exited:" + str(process.returncode))
                continue
            if predicate(item):
                return item
        raise AssertionError("worker_response_timeout")

    record = {"zip_sha256": sha256(args.zip), "source_commit":
              json.loads((resources / "muse_build_info.json").read_text())["source_commit"],
              "approval_actor": "synthetic_host_decision_fixture", "goal_id": goal_id,
              "plan_digest": draft["digest"], "workspace": str(workspace)}
    try:
        base = {"type": "goal_decide", "goal_id": goal_id, "revision": 1, "decision": "approve"}
        for label, digest in (("missing", None), ("wrong", "0" * 64)):
            event = dict(base)
            if digest is not None:
                event["plan_digest"] = digest
            send(event)
            reply = until(lambda x: x.get("status") in {"REJECTED", "ACTIVE"})
            record[label] = {"status": reply.get("status"), "error": reply.get("error"),
                             "draft_preserved": store.get(goal_id)["status"] == "draft",
                             "artifact_exists": artifact.exists()}
            if (reply.get("status"), reply.get("error")) != (
                    "REJECTED", "plan_digest_required_or_changed"):
                raise AssertionError(label + "_digest_accepted")
            if not record[label]["draft_preserved"] or record[label]["artifact_exists"]:
                raise AssertionError(label + "_changed_state")
        send(dict(base, plan_digest=draft["digest"]))
        active = until(lambda x: x.get("status") in {"ACTIVE", "REJECTED"})
        if active.get("status") != "ACTIVE":
            raise AssertionError("exact_digest_rejected:" + str(active))
        run = until(lambda x: x.get("goal_id") == goal_id and x.get("status") in
                    {"COMPLETED", "WAITING_USER", "FAILED"}, 30)
        if run.get("status") != "COMPLETED":
            raise AssertionError("approved_run_failed:" + str(run))
        receipt = next(x for x in run["receipts"] if x.get("capability") == "workspace.write_artifact")
        data = artifact.read_bytes()
        record["exact"] = {"status": active["status"], "approval_id": active["approval_id"],
                           "run_status": run["status"], "run_id": run["run_id"],
                           "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                           "receipt_sha256": receipt["verification"]["sha256"],
                           "readback_matches": receipt["verification"]["readback_matches"],
                           "content_matches": data == content.encode()}
        if not (record["exact"]["sha256"] == record["exact"]["receipt_sha256"] and
                record["exact"]["readback_matches"] and record["exact"]["content_matches"]):
            raise AssertionError("independent_readback_mismatch")
    finally:
        process.terminate()
        process.wait(timeout=5)
    signatures()
    caches = list(app.rglob("__pycache__")) + list(app.rglob("*.pyc"))
    record["signature_before_after"] = "PASS_STRICT"
    record["bytecode_cache_after"] = len(caches)
    if caches:
        raise AssertionError("package_bytecode_cache_created")
    record["result"] = "PASS_NO_GUI"
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"result": record["result"], "evidence": str(args.evidence),
                      "zip_sha256": record["zip_sha256"]}))


if __name__ == "__main__":
    main()
