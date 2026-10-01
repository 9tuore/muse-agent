#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
RUNTIME=$(mktemp -d "${TMPDIR:-/tmp}/g02-appcard.XXXXXX")
trap 'rm -rf "$RUNTIME"' EXIT

printf '%s\n' \
  '{"type":"health"}' \
  '{"type":"terminal_request","argv":["mkdir","bridge-demo"]}' \
  '{"type":"confirm","approved":true}' \
  | PYTHONPATH="$ROOT/app" python3 "$ROOT/app/octosense_appcard.py" "$RUNTIME" > "$RUNTIME/events.jsonl"

PYTHONPATH="$ROOT/app" python3 - "$ROOT/app/octosense_appcard.json" "$RUNTIME/events.jsonl" "$RUNTIME" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert manifest["prototype"] is True
assert manifest["host_contract"]["external_tool_execution"] == "deferred_only"
assert manifest["capabilities"][0]["name"] == "terminal.exec"
events = [json.loads(line) for line in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()]
assert [event["kind"] for event in events] == ["appcard_update"] * 3
assert events[1]["review"] == "required"
assert events[2]["phase"] == "completed"
assert (Path(sys.argv[3]) / "bridge-demo").is_dir()
print("manifest=valid prototype=true deferred_only=true")
print("events=health,terminal_request,confirm")
print("terminal_exec=mkdir bridge-demo returncode=0")
PY
