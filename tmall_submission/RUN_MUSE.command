#!/bin/sh
# Thin, fixed Runtime entry. No account access, install bypass or downloads.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RUNTIME="$HERE/runtime/OctoSense Host.app"
BIN="$RUNTIME/Contents/MacOS/octosense"
MIRROR="$HERE/runtime/mirror"
BUNDLE="$MIRROR/artifacts/muse-goals-0.3.26-rc51.bundle"
fail() { printf '\nMuse 启动未完成：%s\n' "$1" >&2; exit 1; }
case "${1:-}" in ''|--check) ;; *) fail '使用方式：RUN_MUSE.command [--check]' ;; esac
[ "$(uname -s)" = Darwin ] || fail '此运行包需要 macOS。'
[ "$(uname -m)" = x86_64 ] || fail '此运行包仅验证 Intel Mac；Apple Silicon 尚未验证。'
MAJOR=$(/usr/bin/sw_vers -productVersion | /usr/bin/cut -d . -f 1)
[ "$MAJOR" -ge 14 ] || fail '完整日历授权路径需要 macOS 14 或更新版本。'
[ -x "$BIN" ] || fail '配套 Runtime 缺失。请解压完整发行 ZIP；Git 源码目录不附 Host 二进制。'
[ -f "$MIRROR/catalog.json" ] && [ -f "$BUNDLE/manifest.json" ] || fail 'Muse 配套目录缺失，请重新解压完整 ZIP。'
/usr/bin/codesign --verify --deep --strict "$RUNTIME" 2>/dev/null || fail 'Runtime 签名校验失败，请使用完整配套包。'
ACTUAL=$(LC_ALL=C /usr/bin/shasum -a 256 "$BIN" | /usr/bin/cut -d ' ' -f 1)
[ "$ACTUAL" = '1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3' ] || fail 'Runtime 与固定版本不一致。'
ACTUAL=$(LC_ALL=C /usr/bin/shasum -a 256 "$BUNDLE/main.splash" | /usr/bin/cut -d ' ' -f 1)
[ "$ACTUAL" = 'ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da' ] || fail 'Muse 程序与固定版本不一致。'
ACTUAL=$(LC_ALL=C /usr/bin/shasum -a 256 "$BUNDLE/manifest.json" | /usr/bin/cut -d ' ' -f 1)
[ "$ACTUAL" = 'b75fd9686e25697a1766f276b4aaf9aa527c466446215cac8879d61047c69a75' ] || fail 'Muse manifest 与固定版本不一致。'
ACTUAL=$(LC_ALL=C /usr/bin/shasum -a 256 "$MIRROR/catalog.json" | /usr/bin/cut -d ' ' -f 1)
[ "$ACTUAL" = '6f86b03cf0695102d8b269d4944e3819a82cfb56b08acd54a7b1b897186c5ddb' ] || fail '配套目录与固定版本不一致。'
if [ "${1:-}" = --check ]; then
    printf 'PASS：Muse 0.3.26-rc51 / 固定 OctoSense Agent Runtime；未启动窗口。\n'
    exit 0
fi
STATE="$HOME/Library/Application Support/Muse Tmall Experience rc51"
ACTION=launch-apphub
INSTALLED="$STATE/apps/muse-goals/bundle/main.splash"
if [ -f "$INSTALLED" ]; then
    ACTUAL=$(LC_ALL=C /usr/bin/shasum -a 256 "$INSTALLED" | /usr/bin/cut -d ' ' -f 1)
    [ "$ACTUAL" = 'ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da' ] || fail '本体验目录中的 Muse 版本不同。请在应用中心处理版本，不覆盖资料。'
    ACTION=launch-hub:muse-goals
else
    printf '首次体验：请在应用中心安装并打开 Muse。\n'
fi
umask 077
mkdir -p "$STATE/home" "$STATE/apps" "$STATE/logs"
LOCK="$STATE/launch.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
    OWNER=$(cat "$LOCK/pid" 2>/dev/null || true)
    case "$OWNER" in ''|*[!0-9]*) fail '启动入口正在准备，或上次异常退出留下锁。请查看运行指南。' ;; esac
    if kill -0 "$OWNER" 2>/dev/null; then fail '此体验窗口已经在运行，请切回 OctoSense。'; fi
    rm -f "$LOCK/pid"
    rmdir "$LOCK" && mkdir "$LOCK" || fail '无法处理上次退出的启动锁；未修改应用资料。'
fi
printf '%s\n' "$$" > "$LOCK/pid"
CHILD=''
cleanup() { rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null || true; }
stop() { if [ -n "$CHILD" ]; then kill -TERM "$CHILD" 2>/dev/null || true; fi; }
trap cleanup EXIT
trap 'stop; exit 130' INT
trap 'stop; exit 143' TERM HUP
export OCTOSENSE_HOME="$STATE/home"
export OCTOSENSE_APP_DATA="$STATE/apps"
export OCTOS_APP_CORE_DIR="$STATE/home/octos-home/.octos"
export OCTOSENSE_HUB="$MIRROR"
export OCTOSENSE_HUB_ANCHOR=3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840
# Keep this experience visible and independent of developer remote settings.
unset MAKEPAD_REMOTE MAKEPAD_HIDE_WINDOWS
export MAKEPAD_APP_CONFIG='{}'
cd "$RUNTIME/Contents/MacOS"
printf '正在打开 Muse。退出 OctoSense 后本启动入口结束。\n'
"$BIN" --test-action "$ACTION" >> "$STATE/logs/runtime.log" 2>&1 &
CHILD=$!
wait "$CHILD"
