# Muse rc45 真实事项闭环与精简交付

日期：2026-10-05 晚间至 2026-10-06 凌晨，北京时间。

**总体：PARTIAL。** 本轮指定事项已经完成真实邮件、原事件改期、关联确认邮件到达、结果记忆、Shell 重启、新对话召回及合成事件清理。执行节点跨 rc37、rc41、rc45；不能据此宣称同一个最终候选从头整链或原二十项全部通过。用户提出的 20 分钟目标未达成，保留实际失败与耗时。

## 冻结身份

| 对象 | 实际身份 |
|---|---|
| 分支 | codex/muse-rc-finalization |
| 产品 | 0.3.26-rc45 |
| 产品提交 | d306d3c04284413a5891592c26a30a93d2c0866e |
| 可读 Splash SHA-256 | 51c09d4bccb9693891fc60b08a4cafa5807476100c3803380f599fe039c9c053 |
| 实装 Splash SHA-256 | 3f0c9ee008a7365e3652290176e327c1746ed6bc2e4a6602ffe2a6053728339e |
| 官方 token 比较 | 98231，equal |
| 运行 Host SHA-256 | 1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3 |
| Gate 元数据 Git 基线 | be8fef266e88f3861660cdd04052918cc70955a7；Gate 在产品提交前运行，bundle 字节与冻结产品相同 |

本轮未替换 Host、模型入口、manifest grants、VM 执行预算或存储配额，没有新运行时。真实模型沿用官方 model.complete / MiniMax-M3。日历仍是配套宿主最小本地扩展，不能宣称官方原版已准入。稳定 0.3.25、旧独立安装包、生产资料、旧 Tag 与先前未提交 baseline.json 受保护。

## 指定真实事项

事项 ID：`1791214080-2315162597`，唯一合成测试编号：`MUSE-R2-CLOSEDLOOP-20261005-2323`。只使用本人授权测试邮箱与「工作」日历，不公开邮箱内容、凭据或运行资料。

| 节点 | 观察到的结果 | 版本与证据 |
|---|---|---|
| 源测试邮件 | 单次发送、真实同步、自动来信卡、正文读回及本人收件确认 | rc37；once/rc37-source-send.report.json、once/rc37-source-delivery.report.json |
| 安排 | 真实模型生成候选、项目记忆参与、目标日历无冲突；创建一次并独立 get | rc37；once/rc37-create.report.json |
| 改期来源 | 新邮件单次发送、自动提醒、本人确认收到，明确原事项 ID 关联 | rc37；once/rc37-reschedule-source-send.report.json、once/rc37-reschedule-source-delivery.report.json |
| 原事件改期 | 模型生成 16:00–16:30 候选并核验；修改原 EventKit ID，没有创建第二条 | rc41；once/rc41-update.report.json |
| 关联确认邮件 | 从已核验日程构建可编辑稿、独立发送确认、只发一次；本人确认到达 | 发送 rc41，收件核对 rc42；once/rc41-confirmation-send.report.json、once/rc42-confirmation-delivery.report.json |
| 结果结算 | Goal v3 / Run completed，draft/action verified；新结果记忆关联邮件与 Calendar 来源，旧时间事实保留并标记被更新 | rc45；RC45_LINKED_RESULT.json |
| Shell 重启 | 新进程；Goal、Memory、日历关联、草稿、聊天及两份结果共七文件逐字节保持，未重发或重做外部写入 | rc45；RC45_RESTART_BEFORE.json、RC45_RESTART_AFTER.json |
| 新对话记忆 | 新建对话、选择同项目/归属，实际模型从全局记忆回答北京时间 16:00–16:30 与同一事件 ID | rc45；CROSS_SESSION_RECALL.json |
| 清理 | Muse 日期页选择精确事件、输入完整测试 ID、批准一次 delete；独立 get 守卫通过并落 verified，随后完整范围刷新找不到该事件 | rc45；once/rc45-cleanup.report.json、RC45_CLEANUP.json |

原事件 ID：`76046D8C-D99D-41AA-923A-763237FBDC49:DE8C7890-1840-4F0E-93AB-5262DD3729F3`。改期前 2026-10-06 15:00–15:30，改期后 16:00–16:30，Asia/Shanghai；现已清理。六个持久化外部动作 ID 及状态见 LIVE_ACTIONS.json。最终确认邮件是依据已核验事件生成的可编辑稿，这一个节点不能写成模型起草。宿主缺 RFC 邮件线程头，本轮用正文的明确事项 ID 关联，不能写成 RFC 线程验收。

## 实际修复与验证

- rc37：邮件批准、Run、保存、动作记录、Host 派发分为短回调；每步重查绑定，未知发送保护与防重复保持。
- rc40：恢复可见原邮件正文，提供同一事项的直接改期入口；rc38/39 的原生渲染失败仍保留。
- rc41：模型日程请求优先检索已授权且相关的项目偏好，继续使用原检索数量/字节限制；普通 Chat 顺序保持。regression_schedule_priority.splash：15 项 fixture 通过。
- rc42–45：结果来源、结果事实、旧事实更新和审计分段提交；已有完整结果文件不重写；完整 Run 可恢复未完成的内部结算，不重放外部动作。缓存只复用已校验/已读回的完全相同字节；变化数据仍经原校验。
- rc45 真实内部结算无新增 VM 错误；3 组隔离生产函数 fixture 各 15 项通过，包含密集历史、64 容量及 completed Run 恢复。见 result-phases-rc45-r1/report.json。fixture 不代表 SMTP / EventKit / model.complete 实际动作。
- rc42 结果 fixture 新进程恢复 2 组各 12 项通过，rc43 原有结果保留保护检查通过。保留早期等待不足、错误 cwd、不同 Host、摘要不匹配等失败，没有删除失败测试或提高产品预算。
- rc43 的中断恢复发生 JSON 字节表示改变；新来源使用当前内容摘要后缀记录，旧来源与失败证据保留。不能宣称旧摘要所指字节已恢复。
- 真实 App Hub 安装 rc45 六个核心文件 SHA 匹配，七个状态文件及模型 ledger 安装前后保持。真实可见 Shell 的截图保存在本地 *.private.png，不将含账号的截图上传公开 Git。

新结果回归脚本使用本地 A2 的合成测试辅助文件。公共冻结源码不保证包括全部未跟踪辅助 fixture，不宣称 ZIP 能直接运行所有本机验收脚本。

## Hub 与交付

gate-rc45-r1/check.txt：PASSED；scan 写入 review packet；本地演练 catalog sequence 77 / 71 entries 验证通过。NO_PROFILE、演练发布者、无独立 reviewer；这是配套扩展 Host 的本地 Gate，不是正式 App Hub 提交、签名或上架。

桌面交付：`Muse-0.3.26-rc45-Intel精简运行与源码-d306d3c0-2026-10-06` 文件夹及同名 ZIP。公开源码 1389 个文件，约 70.34 MB；保留一个运行 Host、当前 Muse bundle、教程及现有启动器，排除 .git、编译缓存、模型权重、个人资料和重复运行分发。

ZIP 在本报告生成前为 131,287,461 字节，SHA-256 `bd4eb1a6977b40f643f8b9f2553bc2df0fccf9bcb75ed4e3201e9c93d01fa1a6`。Root 独立核对摘要、1940 个成员 CRC 和运行/源码 Muse payload 一致；包装聊天完成 ditto 解压、文件/模式/符号链接、签名与启动器资源检查。若外层附入本报告后重包，以最终 DELIVERY.json 与桌面 .sha256.txt 为准，产品字节冻结不变。

使用边界：Intel x86_64、macOS 14+、本地 ad hoc 未公证。首次打开建立空的隔离 profile，接收人需自己配置模型、邮箱与系统权限。不附账号与模型权重。rc45 包装聊天没有重复 GUI 烟测，先前 rc41 同 Host 空资料目录的 App Hub 安装/聊天界面证据只作为历史证据；Root 的 rc45 原授权目录真实运行不替代第二台 Mac 验收。

## 剩余问题与下一步

1. 原二十项完整标准未全过：同一最终候选从头外部链、独立第二 strong 完整语义验证、最多两个真实替代时间、真账号持续两小时、整机/接收机等门槛仍缺；不重算历史 5 PASS / 14 PARTIAL / 1 BLOCKED 为当前全通过。
2. rc45 新对话回答读到了正确日程，但将「最新核验的时间」部分理解为核验时间戳。CROSS_SESSION_RECALL.json 保留完整合成问题、实际回答与语义限制。
3. rc45 日历「查看关联 目标」在当前聊天记录下触发 script time budget exceeded，停在日历页；具体内部子调用尚未独立定位。见 RC45_NAVIGATION_FAILURE.json。清理通过现有日期/事件选择 UI 完成，没有绕过宿主或直接修改系统数据库。
4. 删除后旧月视图缓存仍显示事件，手动点击刷新后的完整系统查询已确认不存在；应补最小缓存移除/失效处理。默认技术详情隐藏，删除 notice 没有作为可见 Label 展示，未伪称看到该文字。
5. 本轮仅本地提交；没有 push、改公开 Tag、正式发布或将本地扩展说成官方原版已接受。后续应先修上面两个界面问题，再固定候选补仍缺的完整门槛。
