#!/bin/sh
# Same native entry as Muse.app; no downloads, credentials or install bypass.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
fail() { printf '\nMuse 启动未完成：%s\n' "$1" >&2; exit 1; }
case "${1:-}" in ''|--check|--models) ;; *) fail '使用方式：RUN_MUSE.command [--check|--models]' ;; esac
[ "$(uname -s)" = Darwin ] || fail '此运行包需要 macOS。'
[ "$(uname -m)" = x86_64 ] || fail '此运行包仅验证 Intel Mac；Apple Silicon 尚未验证。'
MAJOR=$(/usr/bin/sw_vers -productVersion | /usr/bin/cut -d . -f 1)
[ "$MAJOR" -ge 14 ] || fail '完整日历授权路径需要 macOS 14 或更新版本。'
BIN="$HERE/Muse.app/Contents/MacOS/muse-launcher"
[ -x "$BIN" ] || fail '配套 Runtime 缺失，请重新解压完整发行 ZIP。Git 源码目录不附二进制。'
exec "$BIN" "$@"
