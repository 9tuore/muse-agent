#!/usr/bin/env python3
"""Exercise an isolated synthetic Goal with the already running local Qwen."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from agent_app import LocalAgent


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    workspace = root / "runtime" / "muse-g00-source-qwen-20260928"
    workspace.mkdir(parents=True, exist_ok=True)
    evidence = root / "evidence" / "muse-g00-source-qwen-goal-20260928.json"
    started_at = datetime.now(timezone.utc).isoformat()
    agent = LocalAgent(workspace)
    request = {"type": "goal_propose", "request_id": "g00-synthetic-qwen-20260928",
               "text": "为合成验收准备一份中文产品演讲提纲，说明 Muse 的长期目标、显式审批和本机隐私，并保存到隔离工作区。"}
    phases = []
    draft = None
    for attempt in range(2):
        draft = agent.handle(request)
        phases.append({"phase": "propose", "attempt": attempt + 1, "status": draft.get("status"),
                       "error": draft.get("error"), "model": draft.get("model")})
        if draft.get("status") == "DRAFT":
            break
    result = {"test_id": "H2-source-local-synthetic", "phase": "A", "evidence_type": "REAL_LOCAL_QWEN",
              "actual_started_at": started_at, "workspace": str(workspace), "approval_actor": "synthetic_test",
              "phases": phases, "result": "FAIL"}
    if draft.get("status") == "DRAFT":
        artifact = workspace / draft["plan"]["steps"][-1]["args"]["relative_path"]
        result.update(goal_id=draft["goal_id"], revision=draft["revision"],
                      plan_digest=draft["plan_digest"], artifact=str(artifact),
                      artifact_before_approval=artifact.exists())
        if not artifact.exists():
            approved = agent.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                     "revision": draft["revision"], "decision": "approve",
                                     "plan_digest": draft["plan_digest"]})
            result["phases"].append({"phase": "approve", "status": approved.get("status"),
                                     "approval_id": approved.get("approval_id")})
            if approved.get("status") == "ACTIVE":
                tick = agent.handle({"type": "goal_tick"})
                runs = tick.get("results", [])
                result["phases"].append({"phase": "tick", "statuses": [item.get("status") for item in runs],
                                         "errors": [item.get("error") for item in runs]})
                if len(runs) == 1:
                    run = runs[0]
                    result.update(run_id=run.get("run_id"), approval_id=run.get("approval_id"),
                                  model_tokens=run.get("model_tokens"))
                    if run.get("status") == "COMPLETED" and artifact.is_file():
                        contents = artifact.read_bytes()
                        receipt = next((item for item in run["receipts"]
                                        if item.get("capability") == "workspace.write_artifact"), {})
                        result.update(artifact_sha256=hashlib.sha256(contents).hexdigest(),
                                      independent_observation={"bytes": len(contents),
                                                               "starts_with_outline": contents.startswith("提纲".encode()),
                                                               "readback_matches": receipt.get("verification", {}).get("readback_matches")})
                        if contents and receipt.get("verification", {}).get("readback_matches"):
                            result["result"] = "PASS_LOCAL"
    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    evidence.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": result["result"], "evidence": str(evidence), "phases": result["phases"]},
                     ensure_ascii=False))
    if result["result"] != "PASS_LOCAL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
