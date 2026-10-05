# rc51 当前增量

**总体 PARTIAL；原二十项未全部通过。** 当前产品 `6b46c3c8`，readable `5c182b67` / compact `ed4874d1`，官方 98,560 tokens 等价，Host `1d7d1674` 不变。rc50 首次对话持久记录与关联保存分段，rc51 一次挂载/可见页面刷新及四尺寸受影响 UI 已验证；最终冷启动矩阵和实机回归按[本轮报告](official_muse/rc/rc49-completion-20261006-r1/REPORT.md)分别记录，旧失败不覆盖。

原文及逐项映射：[原二十项](official_muse/rc/rc49-completion-20261006-r1/a3/SOURCE_ORIGINAL20.md)、[03:11 只读审计快照](official_muse/rc/rc49-completion-20261006-r1/a3/rc51/REMAINING20.json)。快照不代替后续最终结果，也不把局部成功改为 20/20。

最终 rc51 冷启动 7/10、应用重开 5/5，完整矩阵 FAIL；Root 真实资料首次启动器也超时，失败保留。同候选内部任务的模型建议、两个显式计划批准、结果读回、Shell 重启无重放和另一已有聊天召回已补证；模型调用在批准前，未测新空聊天，不代替 T18 外部整链。见 [实机记录](official_muse/rc/rc49-completion-20261006-r1/RC51_LIVE_REGRESSION.json)、[恢复](official_muse/rc/rc49-completion-20261006-r1/RC51_REAL_RESTART.json)、[跨聊天](official_muse/rc/rc49-completion-20261006-r1/RC51_CROSS_CHAT.json)。

- T08 原条件为“至多两个，少则不凑”；rc50 只查明确目标半小时且无冲突的一条时段符合条件。以下历史“必须两个”缺口不再作为当前额外要求。
- T19 原生两行等高方案已有本人确认；原条件不要求每个矮窗同时显示四条完整历史。rc51 宽窗可读 fixture 与后三窗 compact fixture 分别记载，窄窗实际 412×813。
- T17 第二 GPT 无 fallback 单次实际请求返回 HTTP200 text/html 而非模型 JSON/SSE，仍 BLOCKED。自定义地址本身不构成失败原因；内置 0.6B 真实同题 0/2，不能作为强模型替代。
- T09/T10/T15/T18 同一最终候选的真实创建、原事件改期、读回后起草及独立发送、重启/新对话整链仍未完成。新日历候选未获窄范围批准，没有写入；源信 IMAP 已同步不代替本人收件声明。
- T20 本地扩展 check/scan/catalog PASS 与官方原版 Calendar 准入、正式 publisher/独立评审分开。OS/接收 Mac 未测；不创建成功 Tag，不正式申请 App Hub。

---

# rc49 增量（历史）

产品e0eb5d82，Gate49-r2；原20完整门槛继续PARTIAL。右侧直接确认回归before6FAIL、最终生产函数10PASS；实机16聊天启动、model.complete实际1204/410tokens候选、右卡确认一次、2条资料Storage/readback/completed/来源记忆、手写composer保留通过。6bundle/23安装前文件SHA保持。rc48恢复/跨聊天/内置小模型验证按原身份支持，未重贴49。原版Hub最终r2 exit1 onlycalendar，本地扩展PASS≠准入。

旧外部链仍跨rc37/41/42/45；同最终完整外链、第二strong、两真实替代、真账号2h、OS/两Mac/正式身份等未因右卡修复而升级。报告：[本轮收口](official_muse/rc/submission-ready-20261006-r1/REPORT.md)。以下历史保留。

---

# rc48 本轮增量（历史）

**总体PARTIAL；原二十项完整门槛未全过，不重算历史5/14/1为20/20。** 产品89bfd399；实际普通任务model候选→批准→Storage/readback→记忆→Shell恢复→另一聊天召回通过。导航/删除缓存/资料意图/启动分片最小修复及旧suite维护均记录版本和原失败。rc47实机启动预算失败保留，rc48当前16聊天实测成功，不能宣称所有冷启动风险消除。

- T04/T05/T14：新任务结果来源记忆、同rc48跨聊天正确召回；复杂历史门槛仍按原标准。
- T07/T17：真实strong/attempts1模型候选和回忆；内置0.6B不是第二strong，实际误答保留。
- T11/T19：精确已核验delete缓存移除fixture15PASS，真实“打开并核对”进入任务详情无预算错误；未重放已清理系统事件、未重跑全尺寸。
- T20：新AppHub安装6SHA/22文件不变；同资料Shell重启主要状态/ledger/result保持，Activity/收信轮询正常变化；256消息完整校验及坏尾条拒绝fixture通过，未做OS/两Mac。
- T18：旧唯一外部事项闭环为rc37/41/42/45跨版本，rc48没有从头新外部全链，继续PARTIAL。

用户本轮授权普通push已执行；正式publisher/独立审核未齐全，本地Gate PASS与原版calendar REFUSED分开；报告及最终包/视频身份见 [收口报告](official_muse/rc/submission-ready-20261006-r1/REPORT.md)。以下保留历史判定。

---

# rc45 真实事项与交付增量（历史）

**总体 PARTIAL；原二十项完整标准未全过。** 本地产品d306d3c0，运行Host1d7不变。本轮未push/Tag/正式提交。以下新证据按实际版本记载；不把历史5/14/1局部重算为20/20。

| 项 | 新增真实证据 | 剩余边界 |
|---|---|---|
| T02/T03/T13/T16 | rc37源信和改期信单次发送、真实同步/自动卡/本人到达；rc41同Goal关联确认信单次发送，本人到达已在rc42核对 | 跨版本；并非同最终所有来信/断连/2h真账号测试 |
| T04/T05/T14 | rc45 completed Run内部结果恢复、三来源结果记忆及旧时间事实标记被更新；3组密集/64容量fixture各15PASS；新对话M3读取16:00–16:30/同UID | 真实问题部分被理解成核验时间戳；保留语义限制和原失败 |
| T07/T17 | rc41 M3真实候选按项目偏好生成准确改期，rc45真实Chat召回结果 | 第二strong完整独立语义与原模型完整题集未补齐 |
| T08/T09/T10/T12 | 同Goal/原EventKit ID：rc37create/get，rc41update/get至16:00–16:30，目标Work冲突查询实际通过 | 未核验两个替代时间；从头固定最终候选门槛未满足 |
| T11 | rc45 Muse日期页精确事件/完整测试ID删除一次；实际独立get守卫通过、verified动作/收据，完整刷新该事件不存在 | 删除后缓存仍显示旧项，必须手动刷新；不是任意用户事件删除授权 |
| T18 | 同一事项外部操作、本人到达、结果记忆、重启与新对话、清理完成 | 源rc37/改期发送rc41/结算恢复rc45，不拼成同最终从头PASS |
| T19 | rc40正文与直接原事项改期按钮真实可见；rc45实际1400×807可操作清理 | “查看关联目标”预算超时未修；最终全尺寸未重测 |
| T20 | rc45实装六SHA、安装状态保护，Shell新进程七状态/结果字节保持；<500MB ZIP的CRC/SHA/载荷与解压/签名/启动器检查 | 非OS重启或两接收Mac；rc45包装GUI未重跑，真账号2h等缺项仍在 |

详细：[真实闭环报告](official_muse/rc/closed-loop-rc36-20261005-r1/REPORT.md)。本地扩展Hub check/scan/catalog PASS，不代表正式上架或Calendar上游准入。以下为历史证据。

---

# rc35 本轮增量证据（历史）

**总体PARTIAL，原20项完整标准未全部通过。** 当前0.3.26-rc35 /0f8e027d，可读de37933e/实装800b11dc，Host1d7，官方96651 tokens一致。以下是增量节点；原5/14/1计数是保留的历史全矩阵判定，没有以局部测试重新计算通过数。

| 项 | 新增实际证据 | 尚缺/边界 |
|---|---|---|
| T02/T03/T13/T16 | rc28源信自动卡，rc29收件/改期来信核对，rc34关联回复发送一次且本人收到、实际核对draft/action verified | 节点跨版本；最终候选全部来信/断连及两小时真实账号未跑 |
| T04/T05/T14 | 同Goal v4、结果SHA、三条关联结果记忆；rc35内部不同completed Run回执误冲突修复19 fixture，64保存/更正/容量/恢复按各轮身份通过 | 同最终跨会话外部事项记忆全链；原真实语义失败保留 |
| T07/T17 | rc34真实模型日程候选attempts1；rc35MiniMax普通Chat strong/attempts1/known usage | GPT唯一候选无fallback的真实调用provider失败、usage未知；自定义route后端身份未证明；完整冻结语义门槛不变 |
| T08/T09/T10/T12 | rc29 Work真实create/get、外部Calendar改期刷新；rc34明确选原事项，同ID改至16:00–16:30并独立get | 最多两真实核验替代、最终异常恢复；不是同最终从头完整链 |
| T11 | 本人批准唯一事件清理，macOS日历精确UID删除，独立标题/UID皆0；首次引用错误及1/1未删除证明保留 | 本轮Muse删除界面导航未完成，不把原生清理当Muse delete/get通过 |
| T18 | 真实账号/权限/精确事件确认均已获得；同事项的模型/原IDupdate/get、关联回复本人收到、结果和Memory通过 | 原“缺账号授权”原因已解除；同一最终候选完整业务链仍未通过，不能据跨版本节点解除全链门槛 |
| T19 | rc27真实Dock/侧栏/正文滚动与宽/矮/窄证据保持；后续改动主要业务/Memory，不宣称所有rc35新尺寸重测 | 本轮Calendar嵌套滚动导航未到删除控件；请求412×892曾被Host夹尺寸的失败仍保留 |
| T20 | 默认Shell 558/0单测、空target release Host重建PASS；rc35同profile Shell重启八文件/ledger一致、零重发 | 非全新Cargo/SDK缓存、未换运行Host；OS重启/接收机/最终真账号2h未完，早期model前失败未定因 |

细项与身份见[本轮报告](official_muse/rc/remaining-20261005-r2/REPORT.md)。本地扩展Hub check/scan/catalog PASS不是独立评审或官方上架。源代码按授权同步GitHub，不创建成功Tag。以下旧记录保留原身份与原结论。

---

# rc27 傍晚增量核对

当前已安装0.3.26-rc27（17698129 / compacte5461fd7），Host1d7d1674 / SDKlock78a5eef0。**原20仍5PASS/14PARTIAL/1BLOCKED，总体PARTIAL。** 不把局部新证据升级为完整门槛。

| 项 | 本轮实际证据 | 剩余边界 |
|---|---|---|
| T07 | 解释后缀52/10生产fixture按字节复用；原失败问题最终真实M3一次尝试正确回答 | 未重跑完整冻结语义题集，GPT两尝试仍不能排除fallback |
| T08/T13/T15 | 完整en-dash/空格与不完整拒绝34/5新fixture；原候选同ID修改保时间 | 非真实系统写入或两真实替代核验，旧2FAIL保留 |
| T19 | 原生16标题/首尾删除预览取消、两侧折叠及宽/矮/窄渲染；真实Shell Dock工作区修复，输入/最大化/恢复PASS | native412×809为实际尺寸，不冒充412×892；其他未知“无法标签”含义尚未获澄清 |
| T20 | rc27同目录实际AppHub安装和首次Shell重启六SHA一致；SDK全12000文件、Host增量构建/严格验签、几何8项PASS | 全Shell单测已有launcher错误BLOCKED；完整clean/OS/接收机/最终真账号2h仍缺 |
| T02/T18 | 新Host识别QQ账号，缓存提醒仍在；新日历最新显示完整访问 | 新同步尚无回执；最新完整访问已生效，真实写入仍遵守精确授权；本人旧信核对及最终关联外部整链未过 |

本轮REPORT和UI_RC27_LIVE等保存实际身份。以下为历史记录，不代表当前宿主连接已验证。

---

# rc24 下午增量核对

已安装0.3.26-rc24，产品a6a1f8ba，readable0699524137/compact4345edc8；Host3de610b8/SDKlock64ca58c7。本轮详细报告：official_muse/rc/improvement-20261005-r1/REPORT.md。**整体PARTIAL，原二十项仍5PASS/14PARTIAL/1BLOCKED**，不以新增局部节点替换完整标准。

| 项 | 实际新增证据 | 尚缺 |
|---|---|---|
| T02/T03/T13/T16 | 新QQ完整邮箱登录/授权码UI与同步有效；原未知投递保护保留 | 旧信本人事实核对及同最终两封来信/回复到达整链 |
| T07 | rc23原混合邮件短语48+12；rc24历史副本协议106+25；M3原长问及一句总结实际成功 | 旧语义失败保留；没有重新跑全套题集或扩大通过数 |
| T08 | rc20安排范围15组101/5恢复，原无关任选扩范围反例已修 | 最多两条替代的真实日历核验仍缺 |
| T09/T10 | rc22精确授权事件真实create/get，同IDupdate/get，Muse日期显示正确 | 这些是独立Calendar节点，非来信来源绑定的同最终事项 |
| T11/T12 | 完整测试ID15组105；真实单次delete/get明确不存在 | 电脑日历外部改动后刷新、最终异常恢复 |
| T17 | rc24 M3首选attempts1两次有效回答；GPT首选一回答有效 | GPT attempts2/estimatedtrue不能排除fallback；第二strong独立语义门槛仍未过 |
| T18 | 邮箱/Calendar授权已生效；独立系统CRUD/读回/重启/清理通过 | BLOCKED保留：待本人收件事实答复及最终Mail→Goal→Calendar→reply整链 |
| T19 | 简化导航/卡片、六页长文本、四尺寸可见fixture，rc24 UI字节绑定复用 | 412×892实际夹为412×817，不能写请求尺寸通过 |
| T20 | 新QQHost验签/同目录安装六SHA保持；rc22真实事件存在时Shell重启5SHA/0重放 | OS重启、接收机、同rc24真账号2h及全新完整clean Host仍缺 |

---

# rc18 晨间最终增量核对（历史）

当前应用A=b8545265，0.3.26-rc18；详见RC_MORNING_FINAL_REPORT.md。原20项保持5PASS/14PARTIAL/1BLOCKED，以下rc10矩阵保留为历史证据，不能作为当前宿主身份。

| 项目 | 最新进展 | 当前边界 |
|---|---|---|
| T02/T03 | 真实一次源信发送、自动卡、独立正文读回 | 源自rc15，用户收件核对/最终rc18全链待 |
| T04/T05 | 来源namespace/短回调、真实冲突采用及跨聊天召回 | 同最终邮件日历结果记忆整链缺 |
| T07 | 新M3变式8/8，收件人补充真实通过 | 原错误及裸地址普通语义误答保留 |
| T08 | 新Host完整访问，真实目标日历查询成功 | policy扩大查询范围FAIL，实际替代核验未做 |
| T09/T14 | rc18真实正常普通Goal全链及来源记忆通过 | 外部同事项全链缺 |
| T17 | M3实际调用并引用有效记忆 | 只有一个strong，原失败未清 |
| T18 | 账号/系统授权已生效 | 精确系统写入待答，同最终外部全链未完成 |
| T20 | 新Host全新编译/验签；rc18首Shell重启11SHA/零重放PASS | OS重启/接收机/真实账号2h未完 |

---

# Muse 原二十项验收矩阵 · 0.3.26-rc10

**PARTIAL：5 PASS / 14 PARTIAL / 1 BLOCKED。** 产品A=6fd5b54beeba7cc9892916c3de7f01106ab8a158，readable a19622e0 / compact7cdfc751，91244官方token等价。原二十项及既有关键门槛全部通过才能READY；没有采用18/20、push、成功Tag或正式提交App Hub。

| 项 | 状态 | 已观察证据 | 尚缺与范围 |
|---|---|---|---|
| T01 | PASS | 保护稳定0.3.25、旧独立安装、生产、历史与未提交baseline；Git小步本地提交 | 最終导出只收明确Git普通文件，不收私人运行资料 |
| T02 | PARTIAL | 今晚稳定0.3.25真实自发自收一次、自动提醒、独立mail.message正文SHA匹配；rc10诊断缓存可读 | rc10独立profile实际同步凭据缺失，零发送尝试；最终多封来信/重连/恢复 |
| T03 | PARTIAL | 默认来信提醒/模型分析开关/手写守卫fixture保持，稳定真实Mail没有未授权模型调用 | 最终真实账号默认提醒与开关；合成2h不代替 |
| T04 | PARTIAL | 来源/账号/用户/项目/归属/墓碑28变体支持；rc10两模型实际其他项目/老师无检索泄漏 | 同最终真实Mail/Calendar的归属和项目关联 |
| T05 | PARTIAL | rc10双保存无回退且零重复写入；首次Shell恢复10SHA；两模型实际同claim更正rev2、遗忘墓碑/空检索、新会话相关召回；metadata91支持 | 真实冲突询问及Mail/Calendar关联；64条更正墙钟66.055ms的性能余量风险保留 |
| T06 | PASS | 窄范围授权、软硬约束、未批准零写入24policy/102安排守卫保持 | 新系统写入沿用精确窄授权，不把读取授权扩为任意修改 |
| T07 | PARTIAL | 315业务契约/否定取消支持；rc10原20各19PASS/1FAIL、setup2/holdout6均PASS，Chat没有降成模板 | M3 S02格式无效/未知usage；M27 R02省略缺回执原因；M01两模型无依据评价保留 |
| T08 | PARTIAL | 最多两替代/只查目标/四天范围102fixture，rc10两模型缺时段/日期准确追问且旧候选不变 | 当前rc10已授权Host0fd真实只读schema拒绝；桥源码未进入Host938，真实替代核验未过 |
| T09 | PARTIAL | rc10实际模型计划/建议、一次本地批准、Storage/独立Readback及首Shell重启8SHA保持 | 同邮件事项真实Calendar create/get |
| T10 | PARTIAL | 原event ID/同事项绑定/版本/改期/独立get fixture保持 | 第二实际来信关联原event ID修改及get |
| T11 | PASS | 缺事件/多匹配/错来源/只读/权限撤销安全拒绝；新Host not_determined不写 | 最终身份完整权限外部链另属T18 |
| T12 | PARTIAL | 20故障/3新进程、12stale callback/未知状态不重放守卫支持 | 最终真实服务异常及电脑日历外部修改后刷新 |
| T13 | PARTIAL | 逐封/同事项恢复28+4、稿件25+6支持；rc10实际同候选正文更正保留to/subject | 同最终候选两封真实来信顺序处理 |
| T14 | PARTIAL | rc10任务真实结果/首恢复截图、同事项fixture、真实Model候选修订保持同ID | 外部事项结果卡完整连续体验 |
| T15 | PARTIAL | 手写不覆盖/选择原或建议时段25+6支持；rc10两个实际模型E04仅修改同候选正文 | 最终真实自动稿/手写稿及采用选择 |
| T16 | PASS | 发信独立确认/防重复/未知投递守卫保持；稳定真实SMTP仅发一次并独立收件读回 | 最终发送到达属T18；不伪造本人收件核对或把稳定结果换标签 |
| T17 | PARTIAL | 同rc10两个实际模型各28唯一输入完整观察；冻结原20各19PASS/1FAIL，setup2/holdout6全PASS，无fallback/预算提高 | 原失败保留；M2.7 runtime classunknown不称strong；服务成功不等于语义全部通过 |
| T18 | BLOCKED | rc10真实模型/记忆/一次性任务/存储/读回/首次Shell恢复通过；稳定真实Mail与当前旧授权Host只读定位支持 | 最终profile凭据、新Calendar桥Host/权限/精确事件写入授权；同候选Mail→Memory→create/原ID改期/get→回复到达→首次恢复/跨聊天未完成 |
| T19 | PASS | 本人确认原生最多两行省略、54px等高、完整标题存储保持；未改渲染路径，宽/矮/长文本支持 | 412×892实际夹为412×818且Dock遮挡FAIL保留；412×700不是替代 |
| T20 | PARTIAL | rc10新30完整Shell进程启动/20重开/20Shell重启均PASS，非空16聊天256消息64记忆65来源、六页/输入/焦点/存储与ledger保持 | 同rc10额外100重开全部PASS，同rc10完整7200.220574秒/241样本合成驻留PASS；OS重启/clean/新Calendar Host/真实账号长测仍缺 |

## 证据身份与复用

当前RC10_LIVE_NODE_SUMMARY、RC10_MEMORY_CORRECTION_UI_SUMMARY、RC10_STARTUP_70_SUMMARY及RC10_FROZEN28_SEMANTIC_REVIEW绑定同产品。模型前缀驱动因保存后控件消失停止，失败保留；只提交未见后缀，没有重放输入或挑选通过答案。两模型M01的额外grounding问题单列，不改冻结语义规则。

Runtime Host938/SDK3f、Card5276/Hubde684；Source SDKda与92b1Calendar布尔修复没有进入它。诊断Host0fd是另一已授权身份，严格分开，不拼成同Host整链。本地扩展check/scan/catalog通过不等于官方原版准入或独立评审通过。

未受影响fixture及原生标题按rc10除memory_correct和版本文字外路径字节保持复用，未宣称全部rc10重跑。历史矩阵与日志留Git原版本：rc9 Memory回退、rc6启动预算、rc7邮件主题、rc8D05、所有ENOSPC、旧真实Mail5357秒原生绘制FAIL、各provider/observer失败均保留。没有更换标准或由助手“完成”推断外部成功。
