# rc9 独立内部 B 评分与证据审计

审计时间：2026-10-05T07:03:57.316206+08:00（北京时间）。状态：**PARTIAL**。内部工程评分 **70/100**。不是官方评分、排名、READY或完整UI_PARITY结论。

## 审计边界

仅A2现有真实聊天只读核对。Root独写产品。没有新聊天/子智能体、模型/GUI/fixture重跑、产品/SDK/Git改动；没有读取生产库、凭据、竞争作品或私有真实邮件/模型原件。只新增本报告与同名JSON，旧六文件/21文件及其他清单不变。

## 当前身份

分支`codex/muse-rc-finalization`，观察HEAD`862c55e1`；产品`1c9f3b46`/`0.3.26-rc9`。readable`9d01484c`、compact`4c970e04`现场SHA与冻结相同。`14639fe0`为主文档收口，后续`862c55e1`只改重开测试次数参数。manifest版本与storage/model/mail/calendar/glance声明已读，声明不等于真实授权。

运行Host938/SDK3f按冻结及公开实测记录引用；A2本次没有重哈希二进制。现场源码SDK锁da包含待集成Calendar布尔修复，不能拼成运行Host已修。账本tokens不是货币账单，M2.7 class=unknown不改称strong。

## B评分

| 维度 | 分数 | 主要依据与扣分 |
|---|---:|---|
| 任务实现 | 17/25 | `RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`official_muse/rc/startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json`；扣1：真实冲突问询和最终邮件/日历关联记忆未全证；扣2：只受影响D05两个模型通过，完整两模型15题未过；应用守卫问询不等于模型原始质量；扣5：仅历史稳定版真实节点支持；rc9同事项创建/原event改期/get/回复到达全链未完成 |
| 可靠性 | 15/20 | `RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`OVERNIGHT_SOAK.md`、`official_muse/rc/startup/RC9_STABILITY_INTERRUPTION_SUMMARY.json`；扣1：旧fixture按相关函数字节复用；最终真实服务异常/外部修改仍缺；扣3：仅旧V15合成2h支持；rc9 r1 ENOSPC，r2和100重开尚未完成；稳定真Mail5357s绘制FAIL保留；扣1：当前普通重开8.4–9.4s，Shell重启最高17.6s；更正66.055ms历史余量风险和低磁盘中断仍在 |
| 人机协作 | 11/15 | `RC9_LIVE_NODE_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`、`RC_EVIDENCE_INDEX.json`；扣1：真实本地任务已证；外部连续卡片体验未全证；扣1：拒绝、过期和手写保护多为历史fixture；最终真实手写/采用/外发流程待；扣2：rc9六页和编辑通过；历史412×892被夹到412×818并Dock遮挡FAIL，412×700不替代；不称完整UI_PARITY |
| 官方适配 | 12/15 | `RC9_DELTA_BINDING.json`、`official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json`、`SOURCE_DELIVERY.md`、`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json`、`RC_ACCEPTANCE_MATRIX.md`、`RC_CODE_FREEZE.json`；扣1：运行Host938/SDK3f没有源码SDKda的Calendar布尔桥，系统完整链受阻；扣2：本地开发签名/check/catalog不是官方原版或正式publisher/政策/审核通过 |
| 复现交付 | 7/15 | `RC9_DELTA_BINDING.json`、`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`SOURCE_DELIVERY.md`、`official_muse/rc/startup/RC9_STABILITY_INTERRUPTION_SUMMARY.json`、`official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json`、`official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json`；扣2：rc9静态签名镜像可核对，最终薄导出未固定；桌面独立Intel旧包仍rc5，不是最新版成品；扣3：干净SDK12000条目恢复成功，但Host构建因容量中止，无新可执行包；扣3：均未完成，旧机暖运行和Shell进程重启不替代 |
| 差异化 | 8/10 | `RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`；扣1：原事件关联及改期主要fixture，最终外部同事项链待；扣1：本地结果与历史真Mail提醒有证，当前后台真实账号连续体验尚缺。未比较竞争作品，不推断领先 |
| **合计** | **70/100** | 原二十项仍5PASS/14PARTIAL/1BLOCKED；分数不替代门槛 |

### 每分拆解与扣分

#### 任务实现

- 一次性Goal计划、批准、执行、独立回读和首次恢复：8/8（扣0）。证据：`RC9_LIVE_NODE_SUMMARY.json`。本地一次性流程已证；不扩为周期目标或外部系统流程。
- 来源记忆、新聊天召回、更正、遗忘：6/7（扣1）。证据：`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。扣1：真实冲突问询和最终邮件/日历关联记忆未全证。
- 实际模型与自然语言问询：2/4（扣2）。证据：`official_muse/rc/startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json`、`RC_ACCEPTANCE_MATRIX.md`。扣2：只受影响D05两个模型通过，完整两模型15题未过；应用守卫问询不等于模型原始质量。
- Mail/Calendar同事项外部任务：1/6（扣5）。证据：`RC_ACCEPTANCE_MATRIX.md`。扣5：仅历史稳定版真实节点支持；rc9同事项创建/原event改期/get/回复到达全链未完成。

#### 可靠性

- 持久化、独立回读与首次进程恢复：5/5（扣0）。证据：`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`。8SHA和账本相等已证，明确不是电脑重启。
- 当前70次启动/重开/进程重启：4/4（扣0）。证据：`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`。30/20/20磁盘记录齐且每条通过。
- 失败拒绝、绑定、防重放与恢复：4/5（扣1）。证据：`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。扣1：旧fixture按相关函数字节复用；最终真实服务异常/外部修改仍缺。
- 长运行：1/4（扣3）。证据：`OVERNIGHT_SOAK.md`、`official_muse/rc/startup/RC9_STABILITY_INTERRUPTION_SUMMARY.json`。扣3：仅旧V15合成2h支持；rc9 r1 ENOSPC，r2和100重开尚未完成；稳定真Mail5357s绘制FAIL保留。
- 性能与容量余量：1/2（扣1）。证据：`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。扣1：当前普通重开8.4–9.4s，Shell重启最高17.6s；更正66.055ms历史余量风险和低磁盘中断仍在。

#### 人机协作

- 计划、确认、结果与解释：5/6（扣1）。证据：`RC9_LIVE_NODE_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。扣1：真实本地任务已证；外部连续卡片体验未全证。
- 权限与用户编辑控制：3/4（扣1）。证据：`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。扣1：拒绝、过期和手写保护多为历史fixture；最终真实手写/采用/外发流程待。
- 导航、输入、标题和响应式界面：3/5（扣2）。证据：`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`、`RC_EVIDENCE_INDEX.json`、`RC_ACCEPTANCE_MATRIX.md`。扣2：rc9六页和编辑通过；历史412×892被夹到412×818并Dock遮挡FAIL，412×700不替代；不称完整UI_PARITY。

#### 官方适配

- 官方运行语言、Shell、Makepad、App Hub入口：7/7（扣0）。证据：`RC9_DELTA_BINDING.json`、`official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json`、`SOURCE_DELIVERY.md`。已证官方运行体系；明确本地扩展范围。
- 实际model.complete和官方存储回读：3/3（扣0）。证据：`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json`。真实模型调用与Storage/Readback已证，不由开发Agent代做。
- manifest权限与宿主服务集成：2/3（扣1）。证据：`RC_ACCEPTANCE_MATRIX.md`、`RC_CODE_FREEZE.json`。扣1：运行Host938/SDK3f没有源码SDKda的Calendar布尔桥，系统完整链受阻。
- 官方准入与发布认可：0/2（扣2）。证据：`official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json`、`SOURCE_DELIVERY.md`。扣2：本地开发签名/check/catalog不是官方原版或正式publisher/政策/审核通过。

#### 复现交付

- 版本、源码、运行时和证据可追踪：3/3（扣0）。证据：`RC9_DELTA_BINDING.json`、`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json`。SHA及提交绑定明确，源码SDK和旧运行SDK分开。
- 生产资料保护和证据保留：2/2（扣0）。证据：`RC_ACCEPTANCE_MATRIX.md`、`SOURCE_DELIVERY.md`、`official_muse/rc/startup/RC9_STABILITY_INTERRUPTION_SUMMARY.json`。原失败保留；不将私有资料纳入交付。本审计未检查生产文件，不宣称全仓无Secret。
- 当前可复现交付材料：2/4（扣2）。证据：`official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json`、`SOURCE_DELIVERY.md`。扣2：rc9静态签名镜像可核对，最终薄导出未固定；桌面独立Intel旧包仍rc5，不是最新版成品。
- clean全构建与新Host：0/3（扣3）。证据：`official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json`。扣3：干净SDK12000条目恢复成功，但Host构建因容量中止，无新可执行包。
- 第二Mac/ARM/电脑重启：0/3（扣3）。证据：`official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json`、`RC_ACCEPTANCE_MATRIX.md`。扣3：均未完成，旧机暖运行和Shell进程重启不替代。

#### 差异化

- 可追溯记忆和跨聊天更正遗忘：4/4（扣0）。证据：`RC9_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`。真实当前记忆六步支持产品特性。
- 统一任务上下文和同事项版本绑定：2/3（扣1）。证据：`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。扣1：原事件关联及改期主要fixture，最终外部同事项链待。
- 主动提醒、批准与验证的产品组合：2/3（扣1）。证据：`RC_ACCEPTANCE_MATRIX.md`、`RC9_LIVE_NODE_SUMMARY.json`。扣1：本地结果与历史真Mail提醒有证，当前后台真实账号连续体验尚缺。未比较竞争作品，不推断领先。

## 已核对的实际证据

- 当前记忆六步/三次M3、一次Goal两次模型/一次批准/Storage/独立Readback/首次Shell重启，来自`fa89b675`版本公开`RC9_LIVE_NODE_SUMMARY.json`；八项前后SHA对逐项相同。A2未读其私有raw report，因此是公开摘要审计，不冒充独立实测。
- 当前D05两个真实模型，公开摘要由`fa89b675`记录；每模型一次UI输入/一次Host attempt、无fallback、零候选/外部写入。应用守卫产出问句，不证明模型原始输出质量；完整T17仍PARTIAL。
- rc9启动摘要目前未跟踪，证据按文件SHA绑定而非虚构commit。合成raw报告SHA`6a260539…`独立核对；30冷/20重开/20Shell重启共70条，逐条pass、protected_state_equal、model_ledger_equal、input_editable=true。不是电脑重启/OS清缓存，也无实际Mail/模型后台。
- 两张公开rc9原生截图文件存在，SHA与provenance一致；A2未视觉打开截图，不声称独立完整UI对照。
- 本地扩展签名镜像check/catalog记录为静态PASS；没有本次重新运行hub check，也没有官方正式准入证据。
- 当前100普通重开和独立2h r2依委派仍RUNNING，不计完成，不拼旧V15/rc8时间。原rc9 r1 ENOSPC、稳定真Mail5357秒绘制FAIL仍保留。

## Root文本矛盾 / 滞后

- **A01 DOCUMENT_STALE**：以上当前摘要仍写rc9 r2 70启动进行中；独立startup摘要及raw同SHA报告已30/20/20 PASS。 涉及：`RC_ACCEPTANCE_MATRIX.md`、`COLD_START_PROFILE.md`、`RC_CODE_FREEZE.json`、`MORNING_CHAMPIONSHIP_REPORT.md`、`RC_FINAL_LIVE_REPORT.md`、`SOURCE_DELIVERY.md`。建议：Root补充当前70启动结果；T20仍PARTIAL，不计2h/100重开/电脑重启/clean。
- **A02 IDENTITY_LABEL_MISMATCH**：product_commit=1c9f3b46但顶层status仍CURRENT_RC8_PARTIAL；索引有rc9节点但没有当前rc9完整70启动行。 涉及：`RC_EVIDENCE_INDEX.json`。建议：Root纠正版本标签并加入精确rc9 startup摘要/报告SHA，不改旧rc8行。
- **A03 DOCUMENT_STALE**：06:20静态打包记录的root_rc9_70_startup_2h_memory_goal_both_D05=PENDING_NOT_PASSED聚合字段早于后续实际完成；其中记忆/Goal/D05已证，70也后续完成，2h仍未完成。 涉及：`official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json`。建议：保留原观察时间/记录，新增分项当前状态，避免聚合pending掩盖已完成或全PASS掩盖未完成。
- **A04 SCOPE_WARNING_NOT_CONTRADICTION**：T19 PASS只支撑本人确认的两行等高标题；同一行保留412×892失败。T06/T11/T16部分依据fixture，不能改写为最终真实系统整链PASS。 涉及：`RC_ACCEPTANCE_MATRIX.md`。建议：保留窄项PASS及详细范围；UI_PARITY/外部live验收须独立判定。

## 不得升级的范围

最终Mail→项目记忆→Calendar创建/同原event改期/独立get→回复到达→首次恢复仍缺；历史稳定版Mail与Calendar读取不计rc9同链。Calendar桥源码、Foundation边界/Clang编译不能替代实际运行Host；新身份TCC不自动继承。完整双模型15题、电脑重启、clean、新Mac/ARM、正式publisher/政策/媒体仍缺。

任务实现17+可靠性15+人机11+官方12+复现7+差异化8，是当前工程证据的透明主观内部估计；无竞争作品比较、官方权重推断或95分目标倒推。整体PARTIAL不变。

## 精确新增两文件

1. `official_muse/rc/core_chain/RC9_INTERNAL_B_REVIEW.md`
2. `official_muse/rc/core_chain/RC9_INTERNAL_B_REVIEW.json`

每项证据SHA、最后提交/未跟踪身份、各子项得分与扣分都在同名JSON。Root自行审查并明确stage这两项；A2不改主矩阵、现有清单或Git。
