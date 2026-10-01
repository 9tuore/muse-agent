#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PORT=${QWEN_PORT:-8080}
WORKSPACE=${AGENT_WORKSPACE:-$ROOT/runtime/user-demo}
PROOF_DIR="terminal-proof-$(date +%s)"

mkdir -p "$WORKSPACE"
if ! curl -fsS --max-time 3 "http://127.0.0.1:$PORT/health" >/dev/null; then
  echo "Qwen server is not reachable at 127.0.0.1:$PORT" >&2
  echo "Run ./scripts/start_qwen_server.sh in another terminal first." >&2
  exit 1
fi

printf '%s\n' \
  '{"type":"health"}' \
  '{"type":"user_input","text":"请把这一轮实测记录保存到本地"}' \
  '{"type":"confirm","approved":true}' \
  "{\"type\":\"terminal_request\",\"argv\":[\"mkdir\",\"$PROOF_DIR\"]}" \
  '{"type":"confirm","approved":true}' \
  "{\"type\":\"terminal_request\",\"argv\":[\"touch\",\"$PROOF_DIR/ready.txt\"]}" \
  '{"type":"confirm","approved":true}' \
  | LOCAL_MODEL_URL="http://127.0.0.1:$PORT/v1/chat/completions" \
    python3 "$ROOT/app/agent_app.py" "$WORKSPACE"

printf '\nworkspace=%s\n' "$WORKSPACE"
printf 'proof_dir=%s\n' "$WORKSPACE/$PROOF_DIR"
find "$WORKSPACE" -maxdepth 2 -print | sort
