"""Exercise packaged worker event origins in isolated temporary workspaces."""

import argparse
import json
import os
import select
import subprocess
import tempfile
import time
from pathlib import Path


def environment(resources, inbox=None):
    value = os.environ.copy()
    value.update({
        "PYTHONPATH": str(resources),
        "PYTHONDONTWRITEBYTECODE": "1",
        "LOCAL_MODEL_URL": "http://127.0.0.1:9/v1/chat/completions",
    })
    if inbox is None:
        value["GOSIM_LOCAL_INBOX"] = "0"
    else:
        value["GOSIM_LOCAL_INBOX_FILE"] = str(inbox)
    return value


def worker(resources, workspace, env):
    return subprocess.Popen(
        [str(resources / "python/bin/python3"), "-B",
         str(resources / "desktop_worker.py"), str(workspace)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, env=env,
    )


def send(process, event):
    process.stdin.write(json.dumps(event, ensure_ascii=False) + "\n")
    process.stdin.flush()
    ready, _, _ = select.select([process.stdout], [], [], 10)
    if not ready:
        raise TimeoutError("worker_response_timeout")
    return json.loads(process.stdout.readline())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_app", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    resources = args.package_app.resolve(strict=True) / "Contents/Resources"

    inbox_workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-inbox-boundary-"))
    inbox = inbox_workspace / "inbox/events.jsonl"
    inbox.parent.mkdir()
    inbox.write_text("".join(json.dumps(event) + "\n" for event in (
        {"type": "browser_recipe_prepare", "query": "Python 3.13"},
        {"type": "goal_decide", "goal_id": "goal:external", "revision": 1,
         "decision": "approve", "plan_digest": "a" * 64},
    )), encoding="utf-8")
    process = worker(resources, inbox_workspace, environment(resources, inbox))
    time.sleep(1.2)
    inbox_out, inbox_err = process.communicate("", timeout=10)
    inbox_exit = process.returncode
    inbox_events = [json.loads(line) for line in inbox_out.splitlines()
                    if line.startswith("{")]

    stdin_workspace = Path(tempfile.mkdtemp(prefix="gosim-g02-stdin-boundary-"))
    process = worker(resources, stdin_workspace, environment(resources))
    prepare = send(process, {"type": "browser_recipe_prepare", "query": "!"})
    draft = send(process, {"type": "goal_propose",
                           "request_id": "g02-external-approval-probe",
                           "text": "检查 TextEdit 进程健康"})
    approved = send(process, {"type": "goal_decide", "goal_id": draft["goal_id"],
                              "revision": draft["revision"], "decision": "approve",
                              "plan_digest": draft["plan_digest"]})
    cancelled = send(process, {"type": "goal_control", "goal_id": draft["goal_id"],
                               "action": "cancel"})
    process.stdin.close()
    stdin_exit = process.wait(timeout=10)
    stdin_err = process.stderr.read()
    checks = {
        "inbox_rejected_both": len(inbox_events) == 2 and all(
            event.get("error") == "local_inbox_event_rejected"
            for event in inbox_events),
        "stdin_prepare_reached_business_validation":
            prepare.get("operation") == "browser_recipe_prepare" and
            prepare.get("error") == "browser_query_invalid",
        "stdin_approval_without_ui": draft.get("status") == "DRAFT" and
            approved.get("status") == "ACTIVE" and
            cancelled.get("status") == "CANCELLED",
        "workers_exited": inbox_exit == stdin_exit == 0 and not stdin_err and not inbox_err,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "approval_type": "synthetic_external_worker_input_fixture",
        "package_app": str(args.package_app),
        "inbox_workspace": str(inbox_workspace),
        "stdin_workspace": str(stdin_workspace),
        "checks": checks,
        "inbox_events": inbox_events,
        "stdin_prepare": prepare,
        "draft": {"status": draft.get("status"), "goal_id": draft.get("goal_id"),
                  "plan_digest": draft.get("plan_digest")},
        "approved": {"status": approved.get("status"),
                     "approval_id": approved.get("approval_id")},
        "cancelled": {"status": cancelled.get("status")},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
