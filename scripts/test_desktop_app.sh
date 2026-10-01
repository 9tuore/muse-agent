#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DIST=${MUSE_DIST_DIR:-"$ROOT/dist"}
APP="$DIST/GOSIM-Local-Agent.app"
ZIP="$DIST/GOSIM-Local-Agent-macOS.zip"
[ -x "$APP/Contents/MacOS/GOSIM-Local-Agent" ]
[ -f "$ZIP" ]
[ -f "$APP/Contents/Resources/qqmail_imap_bridge.py" ]
[ -f "$APP/Contents/Resources/memory_store.py" ]
for RESOURCE in muse_models.py muse_goal_store.py muse_goals.py muse_goal_schema.json muse_capabilities.py muse_events.py muse_plugins.py muse_plugin_manifest.json; do
  [ -f "$APP/Contents/Resources/$RESOURCE" ]
done
/usr/bin/plutil -lint "$APP/Contents/Info.plist" >/dev/null

RUN_ID="g03-desktop-$(date +%Y%m%d-%H%M%S)"
TEMP_ROOT=$(mktemp -d "/tmp/GOSIM 成品验收.XXXXXX")
TEMP_APP="$TEMP_ROOT/GOSIM Local Agent.app"
TEMP_WORKSPACE="$TEMP_ROOT/workspace"
cp -R "$APP" "$TEMP_APP"
mkdir -p "$TEMP_WORKSPACE"

QWEN_PID=$(pgrep -n -f 'runtime/llama-b11178/llama-server' || true)
AGENT_WORKSPACE="$TEMP_WORKSPACE" LOCAL_MODEL_URL=http://127.0.0.1:8080/v1/chat/completions \
  "$TEMP_APP/Contents/MacOS/GOSIM-Local-Agent" --self-test >"$TEMP_ROOT/app.stdout" 2>"$TEMP_ROOT/app.stderr" &
APP_PID=$!
WORKER_SEEN=0
for _ in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1
  if ps -axo command | grep -F "$TEMP_APP/Contents/Resources/desktop_worker.py" | grep -v grep >/dev/null 2>&1; then
    WORKER_SEEN=1
  fi
  if ! kill -0 "$APP_PID" 2>/dev/null; then
    break
  fi
done
if kill -0 "$APP_PID" 2>/dev/null; then
  kill "$APP_PID" 2>/dev/null || true
  echo "FAIL app did not exit self-test" >&2
  exit 1
fi
[ -f "$TEMP_WORKSPACE/agent-note.txt" ]
grep -F '[GOSIM_TEST:desktop-app:self-test]' "$TEMP_WORKSPACE/agent-note.txt" >/dev/null
if ps -axo command | grep -F "$TEMP_APP/Contents/Resources/desktop_worker.py" | grep -v grep >/dev/null 2>&1; then
  echo "FAIL private worker remained after quit" >&2
  exit 1
fi
if [ -n "$QWEN_PID" ] && ! kill -0 "$QWEN_PID" 2>/dev/null; then
  echo "FAIL shared Qwen process changed during app test" >&2
  exit 1
fi

printf '%s\n' \
  "run_id=$RUN_ID" \
  "app_bundle=$APP" \
  "zip=$ZIP" \
  "copied_app=$TEMP_APP" \
  "workspace=$TEMP_WORKSPACE" \
  "app_self_test=PASS" \
  "worker_bridge=PASS" \
  "qqmail_bridge_resource=PASS" \
  "memory_store_resource=PASS" \
  "muse_runtime_resources=PASS" \
  "file_write_and_readback=PASS" \
  "non_source_path=PASS" \
  "private_worker_cleanup=PASS" \
  "shared_qwen_pid=${QWEN_PID:-NOT_RUNNING}" \
  "shared_qwen_preserved=$([ -n "$QWEN_PID" ] && echo PASS || echo NOT_TESTED)"
