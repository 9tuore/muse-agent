# Muse 夜间工程与关机后续跑报告

状态：**PARTIAL / 开发窗口尚未结束**。本检查点为2026-10-10 14:15（北京时间）。用户延长到17:00，16:00冻结大改。电脑关机期间没有运行或测试，不计作持续开发时间。

## 版本与保护

- A分支：`codex/muse-semifinal-a-20261009`，检查点提交 `14d76df6`。
- 正式根目录仍是rc17，载荷SHA-256 `90351cba7ec5c493befb6673212bfb1aa9639dbfbc2ce28b83e24b98f3e05bdc`，没有覆盖旧安装和生产资料。
- rc18研究源SHA-256 `5e2e84fe51b168fc4966346c9670189d95d314f2a00f50fe1c4fc70b2867906f`；`build/semifinal-candidate-r3`仅准备，未签名、未准入、未安装。
- 行动链隔离提交 `266f9c66`，未合入A。不使用子代理；已有B聊天已停止写入并移交。

## 已复现并修复

| 问题 | 最小修改 | 实际证据 |
|---|---|---|
| 取消宿主邮件审阅后，关联Run一直运行 | 确认未发送时关闭精确绑定的Run，UNKNOWN保持待核对 | 修前3项FAIL保留；修后16项协议通过，7个独立双VM恢复案例通过 |
| 日历中断后仅凭本地产物文件显示完成 | 运行中的日历任务不晋升完成、不显示未核验结果；历史已完成记录保留 | 修前3项FAIL；修后10项恢复检查、零外部写入 |
| Host方法ABI 2被当成ABI 1 | 精确要求ABI 1 | 修前版本检查FAIL；修后19项能力与邮件协议检查通过 |
| 候选漏声明runtime与必需方法 | 独立候选准备器声明runtime、host-api-v1与四项@1方法 | manifest文件核对完成；尚无新Host原生准入证据 |

全部失败记录保留在 `official_muse/semifinal/evidence/` 或其对应ignored build原始目录，没有硬编码模型答案。

## 验证范围

| 任务 | 目前结论 | 限制 |
|---|---|---|
| rc17稳定基线冷启动 | 真实Shell 20/20，非空16对话/256消息/64记忆 | 不是rc18或最新官方Host的20次 |
| rc18邮件审阅/UNKNOWN/恢复 | 19项合成协议，7/7独立双VM恢复 | 不是原生审批、SMTP投递或收件证明 |
| 授权全局记忆 | DSL 62项；真实jailed文件/元数据/双VM 91项 | 合成授权项目；不是本轮真实模型语义全链 |
| 日历恢复 | 10项真实VM检查 | 官方内置Calendar真实relay仍缺；不恢复自备EventKit默认 |
| 真实可见UI | 参考card-host输入/日历阻塞/非空历史/九文件哈希保持 | 源fa25ccda；当前5e2仅一行ABI判断不同，不能冒充新Host实跑 |
| 官方Agent隔离原型 | 15项协议/jailed存储检查 | 没有真人consent、实际模型选工具或原生准入；正式Chat仍model.complete |
| 行动链 | 25项状态检查、四种可见窗口尺寸、一次进程重启 | 明色未测、事务切换未做；独立树未合主线 |
| Phone | 历史r7 Home APK已构建验签，Bridge曾模拟器UI通过 | 旧七小时截止报告不改；Home运行/新模拟器续验待做，实体DEVICE_NOT_TESTED |
| 同候选完整外部链 | **未通过** | 原生Mail审阅、新Host、Calendar relay、真实工具选择仍受阻 |

## 官方升级与缺口

固定Desktop `desktop-v0.1.0-rc.2 / 4ccf8e068399b1da139771a9ed94cef05fa6ae60`，Host契约1.10.0。源码完整checkout及官方framework setup/--check通过；公开Mac成品只有arm64，本机Intel。

全图Git依赖下载在293322763字节停滞12分钟，13:46停止；最小锁定offline构建exit101；官方octoscode归档下载14:04超时exit28，收到72167452字节但归档未完整。新Host未构建、未安装。失败日志保留，继续独立官方Hub构建，不改锁和准入规则。

AppHub #182、OctoSense #427仍OPEN。Calendar最小实现补丁已贴#427评论6083645335供维护者审阅，**没有官方接受或合入证明**。update/remove目前owner-only，精确get缺失；范围列表缺项不等于精确不存在。

## 操作与授权

本检查点新增真实发信0、日历写入0、付费调用0。外发限已登录QQ本人自发自收、最多20封合成；原生可信批准仍需本人输入，缺失则HUMAN_REQUIRED。内置Calendar与旧EventKit“工作”日历的授权不混用。不push main、不force、不移动旧Tag、不正式发布。

完整任务及下一检查点以 `MUSE_NIGHT_TASK_LEDGER.md` 为准；本文件17:00收口前仍需更新，不能作为全部任务通过声明。

## 2026-10-10 14:51 后续检查点

- 最新官方Hub构建完成、锁未变。rc18研究r4 unsigned结构check通过；scan生成7问，reviewer未跑，正式准入未测。原空integrity字段拒绝与修复后原生Gate证据在evidence/native-hub-rc2，提交4af1f02e。
- Phone API35新隔离模拟器boot=1、r7 APK安装成功；Home实际崩溃：ThemeCatalog缺mobile-presets.json。packager依赖路径拆空格错误已复现，最新Makepad32d同函数仍相同；单函数补丁Rust检查修前4FAIL、修后6PASS，工具重建中。原日志/截帧保留，不标Home运行通过。
