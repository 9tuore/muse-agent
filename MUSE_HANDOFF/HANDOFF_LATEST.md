# Handoff

## Task
ZC-00 NIGHT-004启动/包资源修复收口。基线codex/muse-pivot-20261010，8a80b8ed。

## Result
PASS：签名stub/包fixture 28/28。真实业务整体仍PARTIAL。

## Changed
Launcher/helper/packager统一执行host-runtime/muse-host，避开官方octosense资源目录；更新当前状态和故障台账。外部main未提交修改保留。

## Tests
2026-10-12，nice -n10 python3 -m unittest test_launcher test_package，exit0，49.346s。源码SHA/结果/日志见official_muse/integrated_release/evidence/night004-launcher-20261012/。

## Commit
以本文档所在提交为修复节点。本单元尚未push。

## Remaining
Mail修复完整Shell测试/新Host，Native日历同ID更新和真实Relay，固定候选全链、Memory/重启/20次冷开。目标11:00，09:00冻结高风险变更。

## Important Boundaries
本单元为合成签名可执行文件/模型health fixture，无真实GUI、推理、Calendar或SMTP。新夜测保护生产资料，旧失败证据保留；不公开发布。
