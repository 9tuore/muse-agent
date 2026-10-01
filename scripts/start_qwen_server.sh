#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MODEL=${QWEN_MODEL_PATH:-$ROOT/runtime/models/Qwen3-0.6B-Q8_0.gguf}
PORT=${QWEN_PORT:-8080}

if [ ! -x "$ROOT/runtime/llama-b11178/llama-server" ]; then
  echo "missing llama-server: $ROOT/runtime/llama-b11178/llama-server" >&2
  exit 1
fi
if [ ! -s "$MODEL" ]; then
  echo "missing Qwen model: $MODEL" >&2
  exit 1
fi

exec "$ROOT/runtime/llama-b11178/llama-server" \
  -m "$MODEL" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --ctx-size 4096 \
  --reasoning off \
  --alias qwen3-0.6b
