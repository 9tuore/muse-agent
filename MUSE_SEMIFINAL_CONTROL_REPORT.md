# Muse 复赛中央总控检查点

2026-10-10 17:00前收口，北京时间；**PARTIAL**。完整夜间结果见 `MUSE_OVERNIGHT_20261010_REPORT.md`；任务不能删减，见 `MUSE_NIGHT_TASK_LEDGER.md`。代码/Phone证据检查点efce444a，后续仅文档收口。owned模拟器和夜间心跳已停止，新增真实外发/日历写入/付费均0。

最新原生Hub锁定构建与rc18研究r4 unsigned结构Gate通过；scan7问只是材料，未正式准入/发布。Desktop新Intel环境依赖网络失败，尚未升级。contained Agent实际Gate因未offer calendar.events而拒绝，正式覆盖0/16，不能把loader或fixture成功计作原生工具执行。

Phone单函数目录解析修补已解决旧配套Home缺资源崩溃：第三次APK构建/资源核对/验签通过，API35两次Home冷启动和force-stop恢复有真实截图。仍不是rc18/Kernel/Bridge/手机Muse全链，实体DEVICE_NOT_TESTED。#458已补实际运行comment6095819625供审阅，未被接受。

官方内置Calendar relay/共享写入与精确读回、原生Mail审阅、同最终外部链及新候选20次仍缺。行动链仍隔离，未合正式候选。普通开发分支同步超时且远端ref404，未同步；main与旧Tag不动。

## 评审四项整改

1. **邮件发送通道**：rc18研究源迁入官方 `mail.compose → mail.review_send`，中断用 `mail.compose_status`只读核对；无旧send回退。原生可信审阅/真实投递尚未通过。
2. **日历归宿**：按用户最新决定，以官方内置 `os.calendar`为唯一默认。新源阻止自备EventKit调用。共享改期/删除/精确读回缺口已反馈及提交最小实现供审阅；未被接受，不能宣称主线全链完成。
3. **单文件可维护性**：先补现有状态机与恢复边界文档，核心协议保持；不为拆文件另造Runtime。行动链为约247行只读投影、隔离验证，未合入。
4. **根bundle发布入口**：根 `bundle/` 已是唯一活动rc17入口，旧路径为相对链接。rc18研究包单独准备Host API方法要求；正式发布Gate/准入仍待同候选新Host验证。

## 次序与接手

稳定性P0 → 官方Mail → 内置Calendar/Octos → 授权记忆 → 性能与轻量化 → Phone → 行动链。16:00后只验证、严重回归修复与交接。普通开发分支可按既有授权同步；未达门槛不动正式候选、旧Tag及正式Hub发布。

需本人动作的缺项集中保留：新Host运行后原生Mail审阅、Agent首次consent；如果缺失，继续隔离验证。没有请求新的费用或复制生产凭据。
