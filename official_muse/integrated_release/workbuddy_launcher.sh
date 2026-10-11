#!/bin/sh
set -eu
CONTENTS=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
RESOURCES="$CONTENTS/Resources"
HELPER="$CONTENTS/MacOS/muse-launcher"
case "${1:-}" in
    --check|--gpt-check) exec "$HELPER" "$1" ;;
    --models|--gpt|--hybrid) MODE_FLAG=$1 ;;
    *) MODE_FLAG= ;;
esac
STATE=${MUSE_INTEGRATED_STATE:-$(/usr/bin/plutil -extract state_root raw -o - "$RESOURCES/launcher.json" 2>/dev/null || true)}
if [ -z "$STATE" ] || [ "$STATE" = null ]; then
    STATE=$(CDPATH= cd "$CONTENTS/../.." && pwd)/'Muse Data'
fi
case "$STATE" in /*) ;; *) echo 'MUSE_INTEGRATED_STATE 必须是绝对路径。' >&2; exit 2 ;; esac
export MUSE_INTEGRATED_STATE="$STATE"
mkdir -p "$STATE/shell" "$STATE/apps" "$STATE/kernel/.octos" "$STATE/rinx" \
         "$STATE/config" "$STATE/data" "$STATE/cache" "$STATE/logs"
export OCTOSENSE_HOME="$STATE/shell"
export OCTOSENSE_APP_DATA="$STATE/apps"
export OCTOS_APP_CORE_DIR="$STATE/kernel/.octos"
export RINX_DATA_DIR="$STATE/rinx"
export ROBRIX_DATA_DIR="$STATE/rinx"
export XDG_CONFIG_HOME="$STATE/config"
export XDG_DATA_HOME="$STATE/data"
export XDG_CACHE_HOME="$STATE/cache"
export OCTOSENSE_DEV_MODE=0
export MAKEPAD_FOCUS=1

unset MAKEPAD_HIDE_WINDOWS MAKEPAD_NO_FOCUS MAKEPAD_NO_GAUSS MAKEPAD_REMOTE \
      MAKEPAD_DISABLE_GAUSS MAKEPAD_SPLASH_BUDGET_MS MAKEPAD_STYLE \
      MAKEPAD_SPLASH_THEME MAKEPAD_WM_TEST_APP MAKEPAD_APP_CONFIG \
      OCTOSENSE_CONTAINED_APPS OCTOS_APP_CORE_BIN OCTOSENSE_KERNEL_ANY_REVISION \
      OCTOSENSE_KERNEL_BIN OCTOSENSE_ALLOW_ANY_KERNEL_REVISION \
      OCTOSENSE_HUB OCTOSENSE_HUB_ANCHOR OCTOSENSE_HUB_CATALOG 2>/dev/null || true

export OCTOSENSE_HUB_CATALOG=legacy
export OCTOSENSE_HUB="$RESOURCES/mirror"
export OCTOSENSE_HUB_ANCHOR=543ffbe45b6700c23e1824157ea694f8bd7839090e0ede464c11758d350b1412

READY="$STATE/launch-$$.ready"
rm -f "$READY"
if [ -n "$MODE_FLAG" ]; then
    "$HELPER" --supervise "$$" "$MODE_FLAG" >> "$STATE/logs/launcher.log" 2>&1 &
else
    "$HELPER" --supervise "$$" >> "$STATE/logs/launcher.log" 2>&1 &
fi
GUARDIAN_PID=$!
trap 'kill "$GUARDIAN_PID" 2>/dev/null || true; rm -f "$READY"' EXIT
trap 'exit 143' TERM INT
while [ ! -f "$READY" ]; do
    if ! kill -0 "$GUARDIAN_PID" 2>/dev/null; then
        wait "$GUARDIAN_PID"
        echo "Muse 校验/守护未就绪：$STATE/logs/launcher.log" >&2
        exit 1
    fi
    sleep 0.1
done
PORT=${MUSE_INTEGRATED_REMOTE:-9696}
exec "$RESOURCES/host-runtime/octosense" "--remote=$PORT" \
    --test-action launch-muse-native-prototype >> "$STATE/logs/host.log" 2>&1
