# Muse 晨间收口报告

**PARTIAL · 0.3.26-rc5 / V15**。本页仍在等待最终两小时采样完成，最后更新：2026-10-05 03:22北京时间。

| 项目 | 当前结果 |
| --- | --- |
| 昨晚开始 | 10月4日21:51:29开始RC；23:13:37转整夜任务，原稳定0.3.25保护 |
| 现在 | 冷启动/恢复、记忆、真实模型及Goal修复已验证；原20项5PASS/13PARTIAL/2BLOCKED |
| 内部排名目标 | 目标超过给定AI基准；当前证据未达到，不宣称比赛排名或第一 |
| A score | 66/100，按已计证据和缺项的内部估计 |
| B score | 65/100，同上；没有官方评分 |
| T18 | BLOCKED：同最终候选真实Mail→Calendar创建/改期→回复→电脑重启未完成 |
| Stability | V15 30冷启动+20普通重开+20Shell重启全部PASS；合成2h仍运行；旧真Mail5357s绘制层FAIL保留 |
| Source | 产品b48618ac；新发现Calendar一行桥修复92b1df15，Foundation及object编译PASS，完整新Host尚未构建 |
| Hub | LOCAL_EXTENDED_HUB开发验证；正式政策/publisher/最终视频/本人摘要未齐，不提交/上架 |
| 需要用户做的 | 新Host构建后授权及登录、精确测试事件操作、第二独立模型、电脑重启、最终材料确认；按MORNING_HUMAN_QUEUE |

## 详细证据与交付边界

- [原二十项](RC_ACCEPTANCE_MATRIX.md)：没有用18/20降低本轮门槛。
- [真实模型、记忆、Goal及自发自收](RC_FINAL_LIVE_REPORT.md)：V15三次真实记忆检索验证更正/遗忘，两个模型参与的一次任务；首次Shell重启八文件SHA不变、无动作或模型重放。真实邮箱支持来自原稳定版本，不能拼成V15整链。
- [70次启动](COLD_START_PROFILE.md)：非空16对话256消息、64记忆65来源全部恢复；冷启动可交互中位13.093秒，最慢24.844秒，预算仍64ms。不是电脑重启或OS缓存清除。
- [日历实际读取与一行修复](RC_CALENDAR_READONLY_REPORT.md)：系统真实读取成功，宿主错误编码数字0/1导致UI拒绝；布尔修复原生边界通过但新Host因空间未编译。旧运行包仍有该缺陷。
- [长运行](OVERNIGHT_SOAK.md)：合成与真实账号分别记录。真实Mail 89分钟失败不改成2小时通过。
- [证据索引](RC_EVIDENCE_INDEX.md)：实际截图/日志/JSON的本地位置及SHA；公开交付不含私人邮件、凭据或生产资料。
- [源码结构](SOURCE_STRUCTURE_AUDIT.md)、[独立实现](MUSE_CLEANROOM_FINAL.md)：保留官方技术路线，无第二Runtime，未恢复长期Goal页面。
- [内部计分](CHAMPIONSHIP_SCORECARD.md)、[演示脚本](CHAMPIONSHIP_DEMO.md)：脚本不是已录视频，评分不是正式名次。
- [晨间队列](MORNING_HUMAN_QUEUE.md)：按步骤补实际证据；构建资源、第二模型、材料缺项可能超过一小时。

源码和运行包分开交付：最新源码使用SDK锁da756dde，现有暖运行Host938ba58a仍来自SDK3f1bbb4e。不能把旧Host标为已集成日历修复。另一Mac/ARM/完整clean构建尚未通过。只做本地小步提交，无push、成功Tag或正式AppHub提交；旧安装、用户资料、旧失败及旧Tag保留。
