#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export LOCAL_MODEL_URL="${LOCAL_MODEL_URL:-http://127.0.0.1:8080/v1/chat/completions}"
export LOCAL_APP_WORKSPACE="${LOCAL_APP_WORKSPACE:-$ROOT_DIR/runtime/user-demo}"
export LOCAL_APP_PORT="${LOCAL_APP_PORT:-8766}"
exec python3 app/web_app.py
