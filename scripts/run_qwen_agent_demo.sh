#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PORT=${QWEN_PORT:-8080}
WORKSPACE=$(mktemp -d "${TMPDIR:-/tmp}/gosim-agent-demo.XXXXXX")
trap 'rm -rf "$WORKSPACE"' EXIT

if ! curl -fsS --max-time 3 "http://127.0.0.1:$PORT/health" >/dev/null; then
  echo "Qwen server is not reachable at 127.0.0.1:$PORT" >&2
  echo "Run ./scripts/start_qwen_server.sh in another terminal first." >&2
  exit 1
fi

printf '%s\n' \
  '{"type":"health"}' \
  '{"type":"user_input","text":"请把本轮 Qwen 实测记录保存到本地"}' \
  '{"type":"confirm","approved":true}' \
  | LOCAL_MODEL_URL="http://127.0.0.1:$PORT/v1/chat/completions" \
    python3 "$ROOT/app/agent_app.py" "$WORKSPACE"

if [ -f "$WORKSPACE/agent-note.txt" ]; then
  printf 'created_file=%s\n' "$WORKSPACE/agent-note.txt"
  cat "$WORKSPACE/agent-note.txt"
fi
