# Handoff

## Task
a2：冻结 rc49/e0eb5d82 的 T19 独立可见 UI 验收；基线 codex/muse-rc-finalization / d2b14b24。

## Result
PARTIAL。实际 990×380 历史区只有40点高，初始无标题/删除按钮。990×539 初始仅2条完整标题，不可称4条可见。请求412×892实际412×809。

## Changed
仅本 a2 目录：隔离测试脚本、报告、几何快照、合成截图及哈希清单。主源码未改。

## Tests
2026-10-06，官方 packaged card-host 52768f57…；宽1400×760、普通990×539、实际窄412×809的首尾选择/删除预览取消/16标题保存通过；四尺寸输入/空发送校验/折叠恢复/长正文滚动通过。矮窗口历史检查失败。运行命令及旧脚本误判见 REPORT.md，失败未覆盖。

## Commit
本地提交，提交号见 Git；未推送。

## Remaining
Root 最小修改 sidebar 的 shortcuts/history 高度分配，再验证矮窗；四条可见标准不能降低。最终 Shell 同二进制全链未在本任务复测。

## Important Boundaries
合成 fixture；独立8517。未控制8493/主profile；无模型费用、邮箱发送、系统日历改动。未更新共享 CURRENT_STATE，主状态由 Root 汇总。
