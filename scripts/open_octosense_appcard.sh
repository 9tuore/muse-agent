#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OFFICIAL_ROOT="${OCTOSENSE_OFFICIAL_ROOT:-/Users/mima0000/Documents/Codex/2026-09-24/gosim-agentic-app-2026-git-gosim-2/work/official}"
BINARY="$OFFICIAL_ROOT/octosense/target/debug/octosense"
MODEL="${LOCAL_MODEL_PATH:-$ROOT_DIR/runtime/models/Qwen3-0.6B-Q8_0.gguf}"
APP="$ROOT_DIR/runtime/OctoSense-AppCard.app"
CONTENTS="$APP/Contents"
PID_FILE="$ROOT_DIR/runtime/octosense.pid"
LOG_FILE="$ROOT_DIR/runtime/octosense.log"

if [[ ! -x "$BINARY" ]]; then
  echo "missing official binary: $BINARY" >&2
  echo "run ./scripts/run_octosense_appcard.sh once to build it" >&2
  exit 2
fi
if [[ ! -f "$MODEL" ]]; then
  echo "missing local model: $MODEL" >&2
  exit 2
fi

# A previous background launch could leave a live process with no usable
# window.  Reusing it makes every subsequent click appear to do nothing, so
# replace only the exact official OctoSense command owned by this launcher.
while IFS= read -r pid; do
  [[ -z "$pid" ]] && continue
  if ps -p "$pid" -o command= 2>/dev/null | grep -Fq "$BINARY --module appcard"; then
    kill "$pid" 2>/dev/null || true
  fi
done < <(pgrep -f "$BINARY --module appcard" 2>/dev/null || true)
for _ in {1..20}; do
  if ! pgrep -f "$BINARY --module appcard" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done
while IFS= read -r pid; do
  [[ -z "$pid" ]] && continue
  kill -9 "$pid" 2>/dev/null || true
done < <(pgrep -f "$BINARY --module appcard" 2>/dev/null || true)
rm -f "$PID_FILE"

mkdir -p "$CONTENTS/MacOS" "$CONTENTS/Resources"
cat > "$CONTENTS/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleDisplayName</key><string>OctoSense AppCard</string>
<key>CFBundleExecutable</key><string>OctoSense-AppCard</string>
<key>CFBundleIdentifier</key><string>org.gosim.octosense.appcard</string>
<key>CFBundleName</key><string>OctoSense AppCard</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>0.1.0</string>
<key>CFBundleVersion</key><string>0.1.0</string>
<key>LSMinimumSystemVersion</key><string>10.15</string>
<key>NSHighResolutionCapable</key><true/>
<key>LSUIElement</key><false/>
</dict></plist>
PLIST

cat > "$CONTENTS/MacOS/OctoSense-AppCard" <<LAUNCHER
#!/bin/sh
set -eu
ROOT_DIR="$ROOT_DIR"
OFFICIAL_ROOT="$OFFICIAL_ROOT"
export OCTOSENSE_HOME="$ROOT_DIR/runtime/octosense-home"
export MAKEPAD_AI_CHAT_MODEL="$MODEL"
export MAKEPAD_FOCUS="${MAKEPAD_FOCUS:-1}"
unset MAKEPAD_HIDE_WINDOWS MAKEPAD_NO_FOCUS MAKEPAD_REMOTE
mkdir -p "\$OCTOSENSE_HOME"
cd "\$OFFICIAL_ROOT"
exec "$OFFICIAL_ROOT/octosense/target/debug/octosense" --module appcard --test-action launch-appcard "\$@" >>"$LOG_FILE" 2>&1
LAUNCHER
chmod +x "$CONTENTS/MacOS/OctoSense-AppCard"

/usr/bin/open -n "$APP"
for _ in {1..20}; do
  pid="$(pgrep -f "$BINARY --module appcard" 2>/dev/null | tail -1 || true)"
  if [[ -n "$pid" ]]; then
    echo "$pid" > "$PID_FILE"
    break
  fi
  sleep 0.25
done
if [[ ! -s "$PID_FILE" ]]; then
  echo "OctoSense exited during launch; see $LOG_FILE" >&2
  tail -40 "$LOG_FILE" >&2 || true
  exit 1
fi
echo "opened: $APP (pid=$(cat "$PID_FILE"))"
echo "log: $LOG_FILE"
