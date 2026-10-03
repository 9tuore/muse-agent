# Handoff

## Task

Root 委派的启动预算单点修补；分支 `codex/muse-prelim-stability`。main 固定 `2e50c5a7…`，Mail 固定 `b1344bd7…`，本聊天不改二者。

## Result

PARTIAL：源码边界、Release 构建（12分41秒）、资源与严格签名检查通过；实际启动由 Root 验收。

## Changed

完整 matched SDK 复制到 `app/build/ui-memory-20261003/prelim-host/sdk-trusted-theme`，只将 `widgets/src/splash.rs:285` 的宿主主题注册改用既有 trusted 入口。可重放补丁为 [splash-trusted-theme.patch](patches/splash-trusted-theme.patch)。正文、事件与预算实现逐字节保持；64ms／64ms／512 与正文 200000 指令上限均未调整。

## Tests

2026-10-03：`python3 official_muse/prelim/tests/startup_host_verify.py` 通过，比较 8726 项，唯一 SDK 变化为 splash.rs。新包 `prelim-host/OctoSense trusted-theme Host candidate.app`；包内可执行文件 SHA `61d7fc0b5632cd88380cbbf1d644e788a992d691cd1db8f38012cc6c925a03d6`，raw SHA `f1d3c4b048c296068499c86069b66b969406340c4f9b0f8cfc6593a16868c3ee`。原 SDK 链接已恢复，旧 App／raw57 备份哈希保持。完整路径、补丁 SHA 与记录见 [evidence-index.json](evidence/startup-host/evidence-index.json)。

## Commit

本聊天未 stage／commit／push；Root 负责整合。

## Remaining

Root 复核新 Host 实际 Shell 启动、主题预算失败、白屏与最终 source／Host 配对。trusted API 不主动清除外层已有预算，残余失败以 live 日志为准。

## Important Boundaries

源码检查／构建／签名均不代表启动成功。未操作窗口、账号、模型、Calendar、外发、用户端口或安装版；原 SDK、旧签名 App 与 raw57 备份保持。
