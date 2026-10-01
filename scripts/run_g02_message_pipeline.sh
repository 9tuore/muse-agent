#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/g02-message-pipeline.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

PYTHONPATH="$ROOT_DIR/app" WORK_DIR="$WORK_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path

from agent_app import LocalAgent

work = Path(os.environ["WORK_DIR"])
event = {
    "type": "message_event",
    "source": "synthetic",
    "message_id": "g02-script-001",
    "conversation_id": "contract-test",
    "direction": "incoming",
    "text": "请把值班说明列入待办",
}
first = LocalAgent(work).handle(event)
duplicate = LocalAgent(work).handle(event)
blocked = LocalAgent(work).handle({"type": "message_event", "source": "wechat", "text": "合成测试"})
loop = LocalAgent(work).handle(
    {
        "type": "message_event",
        "source": "synthetic",
        "message_id": "g02-script-receipt",
        "origin": "agent",
        "text": "已完成",
    }
)

assert first["status"] == "PROCESSED", first
assert first["analysis"]["category"] == "task", first
assert duplicate["status"] == "DUPLICATE_IGNORED", duplicate
assert blocked["status"] == "BLOCKED_UNVERIFIED", blocked
assert loop["status"] == "IGNORED_AGENT_RECEIPT", loop
state = json.loads((work / ".agent_message_state.json").read_text(encoding="utf-8"))
assert state["queue"] == [], state
assert event["text"] not in json.dumps(state, ensure_ascii=False), state

print(json.dumps({
    "queue_file": str(work / ".agent_message_state.json"),
    "processed": first,
    "duplicate": duplicate,
    "wechat_boundary": blocked,
    "loop_prevention": loop,
}, ensure_ascii=False, indent=2))
PY
