#!/bin/sh
set -eu

DIST=${1:?pass candidate distribution directory}
REPORT=${2:?pass report path}
DMG="$DIST/GOSIM-Local-Agent-macOS.dmg"
[ -f "$DMG" ]
TEMP=$(mktemp -d '/tmp/gosim-g04-install.XXXXXX')
MOUNT="$TEMP/mount"
mkdir -p "$MOUNT" "$TEMP/Applications" "$TEMP/home" "$TEMP/workspace"
ATTACHED=0
APP_PID=''
cleanup() {
  if [ -n "$APP_PID" ]; then kill "$APP_PID" 2>/dev/null || true; wait "$APP_PID" 2>/dev/null || true; fi
  if [ "$ATTACHED" -eq 1 ]; then /usr/bin/hdiutil detach -quiet "$MOUNT" || true; fi
  rm -rf "$TEMP"
}
trap cleanup EXIT INT TERM
/usr/bin/hdiutil attach -quiet -readonly -nobrowse -mountpoint "$MOUNT" "$DMG"
ATTACHED=1
[ -L "$MOUNT/Applications" ]
/usr/bin/ditto "$MOUNT/GOSIM-Local-Agent.app" "$TEMP/Applications/GOSIM-Local-Agent.app"
APP="$TEMP/Applications/GOSIM-Local-Agent.app"
/usr/bin/codesign --verify --deep --strict "$APP"
[ -x "$APP/Contents/Resources/python/bin/python3" ]
[ -x "$APP/Contents/Resources/llama/llama-server" ]
[ -f "$APP/Contents/Resources/python/lib/python3.12/LICENSE.txt" ]
/usr/bin/env -i HOME="$TEMP/home" PATH='/usr/bin:/bin' AGENT_WORKSPACE="$TEMP/workspace" \
  GOSIM_BACKGROUND_TEST=1 GOSIM_SKIP_ONBOARDING=1 GOSIM_LOCAL_INBOX=0 \
  "$APP/Contents/MacOS/GOSIM-Local-Agent" >"$TEMP/app.stdout" 2>"$TEMP/app.stderr" &
APP_PID=$!
sleep 8
kill -0 "$APP_PID"
if ! /bin/ps -axo ppid=,command= | /usr/bin/grep -F "$APP/Contents/Resources/desktop_worker.py" | /usr/bin/grep -v grep | /usr/bin/grep -q "^ *$APP_PID "; then
  echo 'installed app did not launch its bundled worker' >&2
  exit 1
fi
/usr/bin/codesign --verify --deep --strict "$APP"
if find "$APP/Contents/Resources" -name __pycache__ -print -quit | /usr/bin/grep -q .; then
  echo 'installed app wrote bytecode into signed bundle' >&2
  exit 1
fi
kill "$APP_PID"
wait "$APP_PID" 2>/dev/null || true
APP_PID=''
sleep 1
if /bin/ps -axo command= | /usr/bin/grep -F "$APP/Contents/Resources/desktop_worker.py" | /usr/bin/grep -v grep >/dev/null; then
  echo 'owned worker remained after installed app exit' >&2
  exit 1
fi
mkdir -p "$(dirname "$REPORT")"
{
  printf '%s\n' 'result=PASS_LOCAL' 'source=DMG mounted read-only' 'install=isolated Applications directory' \
    'home=isolated' 'path=/usr/bin:/bin' 'worker=bundled Python' 'signature_before_after=PASS' \
    'bundle_bytecode_after_run=NONE' 'owned_worker_cleanup=PASS' \
    'second_mac=NOT_TESTED' 'new_user_tcc=NOT_TESTED'
  /usr/bin/shasum -a 256 "$DMG"
} >"$REPORT"
cat "$REPORT"
