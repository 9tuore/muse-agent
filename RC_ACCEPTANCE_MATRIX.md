# 当前候选：0.3.26-rc10 · PARTIAL

产品A=6fd5b54beeba7cc9892916c3de7f01106ab8a158，可读a19622e0 / compact7cdfc751，91244个官方token一致。rc9的真实Memory UI旧值回退已复现并修复；rc10连续两次保存、零重复写入和第一次Shell重启PASS。新70启动、两小时及两个模型完整28步均在运行，以下rc9矩阵是历史快照，不改标签为rc10通过；最终矩阵待新结果。运行Host/SDK未变，Calendar T18仍BLOCKED。

---

# Muse 原二十项验收矩阵 · 0.3.26-rc9

**PARTIAL：5 PASS / 14 PARTIAL / 1 BLOCKED。** 产品冻结1c9f3b46，payload4c970e04，可读9d01484c；官方91,195 token等价。原二十项和既有关键门槛必须全部通过才READY；未采用18/20，没有push、新成功Tag或正式App Hub提交。

| 项 | 状态 | 已观察证据 | 尚缺验收与范围 |
|---|---|---|---|
| T01 | PASS | 稳定0.3.25、独立安装、生产资料及未提交工作保护；Git小步本地提交 | 交付仅允许的Git文件，不收私人运行资料 |
| T02 | PARTIAL | 今晚稳定版真实自发自收一次、自动提醒、独立mail.message正文SHA一致；收信/重连fixture | 最终rc9真实账号多封来信、重连及首次恢复 |
| T03 | PARTIAL | 默认提醒、模型分析授权开关及手写守卫fixture；稳定真Mail后台未新增模型调用 | 最终真实账号的默认提醒与授权开关 |
| T04 | PARTIAL | 来源/项目/归属/账号隔离、墓碑28变体 | 最终指定真实邮件与项目记忆归属 |
| T05 | PARTIAL | rc9真实M3六步/三模型调用：新聊天召回、更正同ID/revision2、遗忘后空检索；首次任务恢复八SHA相同；metadata91项及64条分页支持 | 真实冲突询问、Mail/Calendar关联记忆；64条更正墙钟66.055ms性能余量风险保留 |
| T06 | PASS | 窄范围授权、软/硬约束、未批准零写入守卫；24policy/102scheduling支持 | 新日历写入仍须精确授权 |
| T07 | PARTIAL | 315业务契约/否定取消守卫；rc8真实M3八题全通过、rc9受影响追问通过 | 原20题/2准备/6变体与实际通用聊天质量尚未全过，保留服务/语义失败 |
| T08 | PARTIAL | 最多两替代、只查询目标日历、四天范围102项fixture；rc9两个真实模型缺时段追问通过 | 实际Host截断字段为数字而非布尔；桥源码已修但未进入运行Host，真实替代核验未过 |
| T09 | PARTIAL | rc9真实本地任务：模型计划/建议、一次批准、保存/独立读回成功 | 同邮件事项的真实系统Calendar创建/get |
| T10 | PARTIAL | 原事件绑定、版本、同Goal改期和独立get fixture | 第二真实来信关联原event ID并修改、独立get |
| T11 | PASS | 缺事件、多匹配、错来源、只读/撤销阻断fixture；新Host not_determined实际拒绝系统写入 | 新身份真实完整授权后的外部验证尚缺 |
| T12 | PARTIAL | 20故障/3新进程、12stale callback、未知状态不重放 | 最终真实服务异常与电脑日历外部修改后刷新 |
| T13 | PARTIAL | 逐封与同事项恢复core28+4、稿件25+6fixture | 同最终候选两封真实来信顺序处理 |
| T14 | PARTIAL | rc9真实任务结果卡/首次恢复截图；同事项fixture | 外部事项结果卡的完整连续体验 |
| T15 | PARTIAL | 手写不覆盖、采用选择、原时段/建议时段25fixture/6新进程 | 最终真实自动稿/手写稿/明确采用选择 |
| T16 | PASS | 独立发信确认、防重复/未知投递守卫；今晚稳定版实际仅发送一次并独立收件读回 | 最终发送到达属于T18，不把稳定版结果改标签 |
| T17 | PARTIAL | rc8 M3八题PASS/M2.7七PASS一D05 FAIL；修复后rc9 D05两个真实模型PASS，无fallback/预算提高 | 同最终两模型原20题/2准备/6变体尚未过；M2.7实际class=unknown，不宣称strong或回答普遍更准确 |
| T18 | BLOCKED | rc9真实模型/记忆/一次任务/Storage/Readback/首次重启通过；稳定版真实Mail支持 | 最终Mail→记忆→Calendar创建/原事件改期/get→回复到达→首次重启/跨聊天未完成；新Host桥集成、身份授权及新的精确日历写入授权待 |
| T19 | PASS | 本人已确认原生两行省略/54px等高，标题存储不变、无JS/hover | 旧990×539/990×400/1200×700六页/长文本/滚动支持；412×892实际夹为412×818且Dock遮挡，FAIL保留，412×700不替代 |
| T20 | PARTIAL | rc8完整30冷/20重开/20Shell重启PASS；rc9 r1因ENOSPC中断：磁盘记录30冷/13重开通过；r2同source30/20/20全PASS，另100次连续普通重开全PASS | rc9两小时r1仅19样本542.154s后ENOSPC，不PASS；r2完整两小时进行；旧真Mail5357s原生绘制FAIL，电脑重启/clean/新Calendar Host仍缺 |

## 关键门槛与证据身份

rc9实际顺序：模型候选→Plan→模型建议→一次本地批准→Storage→独立Readback→第一次Shell进程重启。八项SHA包含模型账本均相等，一个Goal/Run，无重复执行。不是电脑重启，也不是系统Mail/Calendar全链。见RC9_LIVE_NODE_SUMMARY.json。

运行Host938ba58a、Card52768f57、Hubde6840e5、运行SDK锁3f1bbb4e。源码SDK锁da756dde另行记录；92b1df15的Calendar布尔桥修复尚未进入此Host。本地扩展Hubcheck/scan/catalog签名通过不等于官方原版准入或独立评审通过。

首轮所有失败保留：rc6冷2预算失败；旧M3 S02/M2.7 D07 UNKNOWN；rc7 E04擅改主题；rc8 M2.7 D05问错；rc6/7/9 ENOSPC中断；真Mail5357s绘制FAIL。未受影响的历史验证仅按字节绑定复用，未说rc9全部重跑。正式publisher/隐私政策/实际短视频及跨机器复现仍缺。
