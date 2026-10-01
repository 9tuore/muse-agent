#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
RUNTIME=$(mktemp -d "${TMPDIR:-/tmp}/g02-agent-app.XXXXXX")
trap 'rm -rf "$RUNTIME"' EXIT

printf '%s\n' \
  '{"type":"health"}' \
  '{"type":"user_input","text":"写入本轮应用测试已完成"}' \
  '{"type":"confirm","approved":true}' \
  | python3 "$ROOT/app/agent_app.py" "$RUNTIME"

test "$(cat "$RUNTIME/agent-note.txt")" = "写入本轮应用测试已完成"
echo "created_file=$RUNTIME/agent-note.txt"
