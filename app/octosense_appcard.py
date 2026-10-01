#!/usr/bin/env python3
"""Prototype bridge from LocalAgent JSONL events to an AppCard envelope.

This is deliberately a host adapter draft. It does not modify or impersonate
the official OctoSense runtime or claim official schema compatibility.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from agent_app import LocalAgent, LocalModelRouter


MANIFEST = Path(__file__).with_name("octosense_appcard.json")


def appcard_result(result: Dict[str, Any]) -> Dict[str, Any]:
    card = result.get("task_card")
    envelope = {
        "kind": "appcard_update",
        "app_id": "g02.local.agent",
        "host_contract": "claim_dispatch_complete",
        "result": result,
    }
    if card:
        envelope["review"] = "required" if card.get("requires_confirmation") else "none"
        envelope["phase"] = card.get("status", "proposed")
    return envelope


def run(workspace: Path, source: Any = sys.stdin, sink: Any = sys.stdout) -> None:
    # Keep the bridge usable without a model, while opting into the already
    # running localhost Qwen service when the launcher supplies its URL.
    model_url = os.environ.get("LOCAL_MODEL_URL")
    agent = LocalAgent(workspace, model_router=LocalModelRouter(model_url))
    for line in source:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            result = agent.handle(event)
            output = appcard_result(result)
        except (json.JSONDecodeError, TypeError) as exc:
            output = appcard_result({"ok": False, "error": "invalid_json", "detail": str(exc)})
        sink.write(json.dumps(output, ensure_ascii=False) + "\n")
        sink.flush()


def main() -> None:
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "runtime"
    workspace.mkdir(parents=True, exist_ok=True)
    run(workspace)


if __name__ == "__main__":
    main()
