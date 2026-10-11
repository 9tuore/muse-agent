# Handoff

## Task

GPT03：NIGHT-004 L4只读审查与自有探针。基线detached 0e4dd0f1，Main c892/签名cdb。

## Result

PARTIAL：新Mail组件8阶段107项PASS（78＋29）；L4仍缺两项机制证据。

## Changed

仅本目录probe/prepare/parent/证据/19项对照；生产Main/SDK/GUI/共享target未改。

## Tests

2026-10-12实际run.py：SIGKILL在accepted、Main回执未转发且sending/in_flight落盘时；receipt OS写错errno21；Review取消；网关50msdeadline真实等57.603ms后Empty，250ms回包255.908ms入队丢弃。各自新VM/Mail/recipient恢复，无重发。107/107，证据复核PASS。命令见README；raw在evidence及自有build/gpt03-night004-l4-audit/{run-r1,gateway-r1}。无运行FAIL。

## Commit

本交接所在本地提交；最终回复给SHA，未push。

## Remaining

SDK无效model JSON解析、native Calendar冲突。overlap query仅prepare。Deny/CAS/Kernel及实际网关计时已有PASS。

## Important Boundaries

实际VM/Mail/recipient/OS/SIGKILL/网关等待；Vault/approval/MockTransport/UI/clock/Splash timer为fixture。全链NOT_TESTED、SMTP0，不称真实网络timeout或REAL_E2E_PASS。无跨聊天消息/子智能体。
