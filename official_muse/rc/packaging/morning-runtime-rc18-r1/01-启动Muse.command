#!/bin/bash
set -euo pipefail
base="$(cd "$(dirname "$0")" && pwd)"
if [[ "${1:-}" == "--check" ]]; then
  exec /bin/bash "$base/02-系统检查.command" --quiet
fi
/bin/bash "$base/02-系统检查.command" --quiet
umask 077
state="$HOME/Library/Application Support/Muse Reproduction rc18 Ab8545265 Host7eebe833"
mkdir -p "$state/home/octos-home/.octos/profiles" "$state/apps" "$state/logs"
if [[ -f "$state/host.pid" ]] && kill -0 "$(cat "$state/host.pid")" 2>/dev/null; then
  printf '这个复现环境已在运行，请用 ⌘Q 退出宿主后再打开。\n' >&2
  exit 1
fi
cd "$base/04-运行文件/Muse Host.app/Contents/MacOS"
host_pid=''
finish() {
  if [[ -n "$host_pid" ]]; then kill "$host_pid" 2>/dev/null || true; fi
  rm -f "$state/host.pid"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
/usr/bin/env -i HOME="$state/home" PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  TMPDIR="${TMPDIR:-/tmp}" LANG=zh_CN.UTF-8 \
  OCTOSENSE_HOME="$state/home" OCTOSENSE_APP_DATA="$state/apps" \
  OCTOS_APP_CORE_DIR="$state/home/octos-home/.octos" \
  OCTOSENSE_HUB="$base/04-运行文件/mirror" \
  OCTOSENSE_HUB_ANCHOR=3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840 \
  MAKEPAD_APP_CONFIG='{}' ./octosense --test-action launch-apphub \
  >> "$state/logs/host.log" 2>&1 &
host_pid=$!
printf '%s\n' "$host_pid" > "$state/host.pid"
printf 'Muse 开发复现环境运行中。日志：%s/logs/host.log\n请保留此终端窗口，退出宿主使用 ⌘Q。\n' "$state"
set +e
wait "$host_pid"
result=$?
host_pid=''
exit "$result"
