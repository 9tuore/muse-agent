#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MODEL=${LOCAL_MODEL_PATH:-$ROOT/runtime/models/Qwen3-0.6B-Q8_0.gguf}
SERVER_URL=${LOCAL_MODEL_URL:-http://127.0.0.1:8080/v1/chat/completions}
WORKSPACE=${AGENT_WORKSPACE:-$ROOT/runtime/user-demo}
SERVER_PID=""

if ! curl -fsS --max-time 2 http://127.0.0.1:8080/health >/dev/null 2>&1; then
  if [ ! -x "$ROOT/runtime/llama-b11178/llama-server" ] || [ ! -f "$MODEL" ]; then
    echo "Qwen runtime or model is missing; run the setup documented in README.md" >&2
    exit 2
  fi
  "$ROOT/scripts/start_qwen_server.sh" >"$ROOT/runtime/qwen-server.log" 2>&1 &
  SERVER_PID=$!
  trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT INT TERM
  i=0
  while ! curl -fsS --max-time 2 http://127.0.0.1:8080/health >/dev/null 2>&1; do
    i=$((i + 1))
    [ "$i" -lt 30 ] || { echo "Qwen server did not become healthy" >&2; exit 1; }
    sleep 1
  done
fi

export LOCAL_MODEL_URL="$SERVER_URL"
mkdir -p "$WORKSPACE"

if [ "${1:-}" = "--gui" ]; then
  shift
  exec "$ROOT/scripts/run_octosense_appcard.sh" "$@"
fi

printf '%s\n' \
  '{"type":"health"}' \
  '{"type":"user_input","text":"请写入一条本地测试记录"}' \
  '{"type":"confirm","approved":true}' \
  '{"type":"terminal_request","argv":["mkdir","mini-app-proof"]}' \
  '{"type":"confirm","approved":true}' \
  | PYTHONPATH="$ROOT/app" python3 "$ROOT/app/octosense_appcard.py" "$WORKSPACE"
