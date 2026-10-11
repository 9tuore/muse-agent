# Handoff

## Task
ZC-00：统一 WorkBuddy 启动、GitHub 同源回归、rc4 集成。

## Result
PARTIAL。现场保留能显示的 WorkBuddy PID90055；完整 Muse 尚未安装并验收。

## Changed
统一 Launcher/launch_muse.sh 已合入；rc4版本、签名目录校验、包元数据同步。新增 GitHub macOS 启动 fixture workflow；主源码已有 Calendar→当前事项行动链。

## Tests
2026-10-11 编译 Launcher 与临时签名 stub：21/21；Qwen catalog：12/12。原错误命令日志保留；这些是零外部调用的 fixture。证据见 integrated_release/evidence/portable-launcher-rc4-fixture.json。当前 Host 编译中。

## Commit
随本单元本地提交；按用户授权正常推开发分支，随后核对远端 SHA。

## Remaining
完整 Muse 的可见安装、真实 Calendar/Mail/行动链同候选业务、T18、20冷启动与重启。Native持续循环默认停用，真实预算尚未实施。GitHub结果尚待实际运行。

## Important Boundaries
窗口可见与 fixture 不等于日历写入、真实投递或正式候选稳定通过。
