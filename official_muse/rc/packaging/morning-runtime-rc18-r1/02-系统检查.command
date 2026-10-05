#!/bin/bash
set -euo pipefail
base="$(cd "$(dirname "$0")" && pwd)"
runtime="$base/04-运行文件"
if [[ "$(uname -m)" != x86_64 ]]; then
  printf '本草稿只核验 Intel x86_64；Apple Silicon 未验证。\n' >&2
  exit 1
fi
version="$(sw_vers -productVersion)"
major="${version%%.*}"
if [[ "$major" -lt 14 ]]; then
  printf '本复现草稿以 macOS 14+ 为测试门槛；Calendar 完整访问要求 macOS 14+。当前：%s\n' "$version" >&2
  exit 1
fi
if [[ ! -f "$runtime/mirror/catalog.json" || ! -f "$runtime/mirror/artifacts/muse-goals-0.3.26-rc18.bundle.pack.json" || ! -f "$base/SHA256SUMS" ]]; then
  printf '开发草稿的公开签名目录或校验清单尚未齐全，不能启动。请使用总控完成材料核验后的整包。\n' >&2
  exit 2
fi
cd "$base"
/usr/bin/shasum -a 256 -c SHA256SUMS >/dev/null
/usr/bin/codesign --verify --deep --strict "$runtime/Muse Host.app"
/usr/bin/codesign --verify --deep --strict "$runtime/Muse Card Host.app"
"$runtime/hub" verify "$runtime/mirror/catalog.json" --anchor 3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840
"$runtime/hub" check "$runtime/mirror/artifacts/muse-goals-0.3.26-rc18.bundle" \
  --publisher-key muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5
printf '包内文件、宿主签名、公开目录和 rc18 载荷检查通过；GUI、模型与业务动作需接收机另测。\n'
