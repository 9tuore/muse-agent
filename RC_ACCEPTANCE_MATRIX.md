# Muse 原二十项验收矩阵

最终产品：0.3.26-rc5 / V15，冻结代码 `b48618acef0ff291ad3dc23b09946b0b15fa4f2f`。当前 **PARTIAL**：5 PASS、13 PARTIAL、2 BLOCKED。完整标准保留，18/20不用于本轮READY。后续维护/报告提交不改变这一产品冻结；不同版本的真实节点不拼接成同候选整链。

| 项 | 状态 | 已观察证据 | 剩余门槛与范围 |
|---|---|---|---|
| T01 | PASS | 原稳定版、分支/HEAD、未提交工作和旧安装保护；RC_BASELINE、freeze身份 | 最终来源与摘要记录持续更新 |
| T02 | PARTIAL | 稳定0.3.25今晚真实自发自收、自动新信提醒、独立正文SHA匹配；现有incoming/core重启fixture | V15官方账号多封新信、重连与首次恢复 |
| T03 | PARTIAL | 原默认提醒及未授予模型时手写守卫fixture；真实稳定Mail后台观察没有新增模型调用 | V15真实账号的默认提醒与分析授权开关 |
| T04 | PARTIAL | 来源/项目/归属/账号隔离fixture；最终V15墓碑守卫28变体通过 | 同V15指定真实邮件与项目记忆归属 |
| T05 | PARTIAL | V15三次真实MiniMax跨对话检索、更正revision2、遗忘空检索PASS；5组91项来源metadata及首次恢复PASS；64条分页/搜索/磁盘SHA通过 | 大库更正墙钟66.055ms超过64ms，虽然无运行错误仍有性能余量风险；真实冲突问询与Mail/Calendar关联记忆待 |
| T06 | PASS | 既有软/硬约束、窄授权、未批准零写入守卫；24policy/102scheduling fixture支持，相关边界保留 | 新系统写入仍需本轮精确确认 |
| T07 | PARTIAL | 315当前业务契约及否定/取消守卫；真实V15科学解释、追问和SMTP解释已观察 | 实际模型15题未完整通过；通用解释有不准确表述；第三题remote帧错误保留，第四题未运行 |
| T08 | PARTIAL | 最多两替代/四天/只查询目标日历的102项fixture | 旧授权Host真实读取成功，但truncated返回数字导致产品UI拒绝；桥一行源码已修，未重编译，V15真实查询与替代核验待 |
| T09 | PARTIAL | 合成创建后独立get与存储守卫；最终真实本地Goal模型/计划/批准/结果读回PASS | V15同邮件Goal真实Calendar创建/独立get |
| T10 | PARTIAL | 同Goal/version/原事件改期/独立get与25稿件、6新进程fixture | 第二真实来信关联并修改原event ID，独立get |
| T11 | PASS | 多匹配、缺事件、错来源、只读、撤销阻断fixture；新宿主not_determined实际停止系统操作 | 本人确认新系统权限后验证真实操作 |
| T12 | PARTIAL | 20故障+3新进程、12stale callback及未知状态不重放；原读写失败已修复并保留 | V15真实服务异常、电脑日历外部变化刷新 |
| T13 | PARTIAL | 逐封处理及同事项恢复的core28+4、稿件25+6fixture支持 | 同V15两封真实来信按顺序处理 |
| T14 | PARTIAL | 真实V15本地任务结果卡/首次恢复与Memory分页截图；同事项fixture | 真实外部事项结果卡逐状态与连续体验 |
| T15 | PARTIAL | 手写稿、采用选择、原时段/建议时段25fixture与6次新进程 | V15真实自动稿、手写不覆盖和明确采用选择 |
| T16 | PASS | 既有独立发信确认、防重复、未知投递保护；今晚授权稳定版本实际发送一次、独立收件读回 | V15真实发送及到达仍归T18，不复用旧版 |
| T17 | BLOCKED | 现有MiniMax-M3真实可用；原生ModelHost4case/6POST/41assert协议fixturePASS | 第二个独立较强模型未配置，localhost协议后端不算 |
| T18 | BLOCKED | 最终V15真实模型、记忆、Goal本地批准/存储/读回/首次重启已过；今晚真实稳定自发自收支持 | 同一最终候选邮箱登录＋系统权限＋真实创建/改期/独立get＋关联回复/到达＋首次恢复/跨会话；夜间未授权新日历修改 |
| T19 | PASS | 原生最多两行、省略、54px等高、完整存储未改；本人已确认原生方案 | 990×539、990×400、1200×700六页/长输入/滚动PASS；412×892受900px桌面夹成412×818且footer被Dock遮挡，FAIL保留；额外412×700 PASS，不替代原尺寸门槛 |
| T20 | PARTIAL | V15非空16对话256消息64记忆65来源预检和64条分页通过；原64ms预算不变；30冷启动/20普通重开/20Shell重启均已完整PASS，六页/编辑/受保护SHA保持 | 最终2h合成运行仍在进行；稳定真Mail观察5357s绘制层FAIL保留；本人电脑重启未做；新Calendar桥Host未重编译 |

## 原有关键门槛

V15真实顺序为模型候选→Plan→模型建议→一次本地批准→Storage→独立Readback→首次Shell重启，八项文件/用量SHA完全不变、一个Goal/Run、无重放，见RC_FINAL_LIVE_REPORT。实际顺序不改写成“批准后才调用模型”；这不代替真实Calendar/Mail整链。

## 证据身份

可读 `af68b897addd0a3e9f81256a9192b58ae95bf9de72951d4ce05a36949f29c583`；compact `5092becd21ece0cdc456ffa60b9a7b85ff01e34b65c68d7743658e7b945b4cd8`，官方tokenizer90,541个token完全相等。Shell938ba58a、Card52768f57、SDK锁3f1bbb4e、Hubde6840e5，完整SHA见RC_CODE_FREEZE。

Core20fault/315contracts等标为fixture；原生Host协议不是实际模型推理。历史未受影响检查按函数字节证明复用，不写成本V15重跑全部。新的完整冷启动、恢复和真实模型证据绑定本V15。

本地扩展Hubcheck/scan仅LOCAL_EXTENDED_HUB，不表示原版官方calendar准入接受。严格clean build因磁盘不足受控中止，暖构建运行包不能替代复现成功。电脑重启、正式隐私/publisher/短视频与上架仍未通过。仅全二十项和旧门槛全过才READY/成功Tag/正式提交。公开main保留稳定版，未push。

## 新的宿主缺陷与身份分离

实际Calendar只读诊断证实旧Host把truncated编码为数字0/1，应用严格布尔守卫拒绝。92b1df15仅改EventKit桥一行、更新SDK锁da756dde；Foundation三边界及原生桥编译通过，SDK12000文件验证通过。可运行Host938/SDK3f未包含此修复；完整新Host因磁盘容量不足未构建，源码修复不记为运行修复。产品source5092仍不变。详见RC_CALENDAR_READONLY_REPORT。
