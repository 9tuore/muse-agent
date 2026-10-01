#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OFFICIAL_ROOT=${OCTOSENSE_OFFICIAL_ROOT:-/Users/mima0000/Documents/Codex/2026-09-24/gosim-agentic-app-2026-git-gosim-2/work/official}
MODEL=${LOCAL_MODEL_PATH:-$ROOT/runtime/models/Qwen3-0.6B-Q8_0.gguf}

if [ ! -d "$OFFICIAL_ROOT/octosense" ] || [ ! -d "$OFFICIAL_ROOT/makepad" ] || [ ! -d "$OFFICIAL_ROOT/octoscript" ]; then
  echo "official OctoSense runtime is incomplete under $OFFICIAL_ROOT" >&2
  exit 2
fi
if [ ! -f "$MODEL" ]; then
  echo "local model is missing: $MODEL" >&2
  exit 2
fi

export OCTOSENSE_HOME=${OCTOSENSE_HOME:-$ROOT/runtime/octosense-home}
export MAKEPAD_AI_CHAT_MODEL="$MODEL"
export MAKEPAD_FOCUS="${MAKEPAD_FOCUS:-1}"
unset MAKEPAD_HIDE_WINDOWS MAKEPAD_NO_FOCUS MAKEPAD_REMOTE
mkdir -p "$OCTOSENSE_HOME"

cd "$OFFICIAL_ROOT/octosense"
exec cargo run --locked --features app-appcard -- --module appcard --test-action launch-appcard "$@"
