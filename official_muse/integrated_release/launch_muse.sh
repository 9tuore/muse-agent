#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
APP=${1:-"$SCRIPT_DIR/Muse.app"}
if [ "$#" -gt 0 ]; then shift; fi
LAUNCHER="$APP/Contents/MacOS/muse-launcher"
if [ ! -x "$LAUNCHER" ]; then
    echo "Muse 启动器不存在：$LAUNCHER" >&2
    echo "使用方式：launch_muse.sh /path/to/Muse.app [--models|--gpt|--gpt-check|--hybrid|--check]" >&2
    exit 2
fi
exec "$LAUNCHER" "$@"
