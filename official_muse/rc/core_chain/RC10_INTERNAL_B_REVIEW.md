# rc10 独立内部 B 审阅准备

审阅时间：2026-10-05T09:59:07.144762+08:00（北京时间）。**PARTIAL，暂计71/100**；当前7200秒soak仍RUNNING，未加分，最终冻结后按精确新增证据只更新一次相关分项。

## 身份和方法

A2现有真实Codex聊天，按本次协调要求标明gpt-6.1-sol证据审阅身份；本次未查询服务端模型身份。独立审阅已有证据，不等于独立重新测试。未操作GUI、模型、外部服务、构建、产品、SDK、Git、生产或凭据；仅新增本报告与同名JSON。Root独写产品与主报告。

## 当前身份

产品A=`6fd5b54b`/`0.3.26-rc10`，观察HEAD=`642aa35b`。当前可读源`a19622e0`/compact`7cdfc751`现场SHA匹配。最终Host938/运行SDK3f未包含源码SDKda的Calendar布尔桥；只读诊断Host0fd另列，不能拼同Host外部链。token等价91244为已有Root记录，本次不重跑tokenizer。

## B分项与逐点依据

| 维度 | 暂计 | 上限 |
|---|---:|---:|
| 任务实现 | 18 | 25 |
| 可靠性 | 15 | 20 |
| 人机协作 | 11 | 15 |
| 官方适配 | 12 | 15 |
| 复现交付 | 7 | 15 |
| 差异化 | 8 | 10 |
| **合计** | **71** | **100** |

沿用rc9子权重。仅“实际模型与自然语言问询”由2/4增至3/4：完整28输入观察已完成，但服务/语义与额外grounding失败仍在。100重开强化已满4分的启动子项，不重复抬分；folder工具14fixture不等于成品导出。

### 任务实现

- **一次性Goal计划、批准、执行、独立回读和首次恢复：8/8，扣0。** rc10一次性本地Goal已证；不是持续周期目标或Mail/Calendar同事项外部全链。 证据：`RC10_LIVE_NODE_SUMMARY.json`。
- **来源记忆、新聊天召回、更正、遗忘：6/7，扣1。** 扣1：双保存零重复、跨聊天召回/更正rev2/遗忘/项目归属已有实际证据，真实冲突问询和最终Mail/Calendar关联仍缺。 证据：`RC10_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`official_muse/rc/startup/RC10_MEMORY_CORRECTION_UI_SUMMARY.json`、`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`。
- **实际模型与自然语言问询：3/4，扣1。** 扣1：两个模型各28输入完整观察原20各19PASS1FAIL；M3 S02 invalid_output/usage未知，M2.7 R02缺回执原因，M01额外grounding失败。完整观察有证，语义全过没有证。 证据：`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`、`RC_ACCEPTANCE_MATRIX.md`。
- **Mail/Calendar同事项外部任务：1/6，扣5。** 扣5：当前隔离profile缺凭据；已授权Host0fd只读schema拒绝；不是最终Host938的外部整链。稳定历史Mail只作节点支持。 证据：`RC_ACCEPTANCE_MATRIX.md`、`official_muse/rc/startup/RC10_MAIL_PROFILE_LOGIN_SUMMARY.json`、`official_muse/rc/startup/RC10_CALENDAR_READONLY_UI_SUMMARY.json`。

### 可靠性

- **持久化、独立回读与首次进程恢复：5/5，扣0。** rc10一次Goal首次Shell恢复8SHA及Memory双保存后恢复已证；不等于电脑重启。 证据：`RC10_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`official_muse/rc/startup/RC10_MEMORY_CORRECTION_UI_SUMMARY.json`。
- **当前70启动及额外100普通重开：4/4，扣0。** 30冷/20重开/20Shell重启与额外100普通重开均完成；同一子项上限4分，不因追加次数超过上限。 证据：`official_muse/rc/startup/RC10_STARTUP_70_SUMMARY.json`、`official_muse/rc/startup/RC10_REOPEN_100_SUMMARY.json`。
- **失败拒绝、绑定、防重放与恢复：4/5，扣1。** 扣1：旧20故障/stale callback保护按未改函数字节复用；当前候选取消/缺时段拒绝有真实模型流程支持，最终服务异常/外部修改仍缺。 证据：`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。
- **长运行：1/4，扣3。** 扣3：当前rc10完整7200秒仍RUNNING，暂只给旧rc9/V15合成驻留支持1分；真实账号长测及稳定Mail5357秒绘制FAIL仍未解决。 证据：`OVERNIGHT_SOAK.md`。
- **性能与容量余量：1/2，扣1。** 扣1：rc10普通重开中位9.389s/最高10.210s、冷启动最高18.882s；64条更正66.055ms历史余量及磁盘中断风险保留，空间合并不是Host重新编译。 证据：`official_muse/rc/startup/RC10_STARTUP_70_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。

### 人机协作

- **计划、确认、结果与解释：5/6，扣1。** 扣1：真实本地Goal计划/批准/结果已证，最终外部连续卡片仍缺。 证据：`RC10_LIVE_NODE_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`。
- **权限与用户编辑控制：3/4，扣1。** 扣1：E04实际候选正文更正保持to/subject、holdout保留/取消通过；最终真实手写/采用/外发确认完整体验尚缺。 证据：`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`、`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`。
- **导航、输入、标题和响应式界面：3/5，扣2。** 扣2：六页/输入/100重开及Memory双保存可靠性通过；412×892实际夹到412×818且Dock遮挡旧FAIL保留，不授予完整UI_PARITY。 证据：`official_muse/rc/startup/RC10_STARTUP_70_SUMMARY.json`、`RC_EVIDENCE_INDEX.json`、`RC_ACCEPTANCE_MATRIX.md`。

### 官方适配

- **官方运行语言、Shell、Makepad、App Hub入口：7/7，扣0。** 实际官方Splash/Makepad/Shell运行和App Hub入口已证；本地扩展不冒充上游原版。 证据：`RC10_DELTA_BINDING.json`、`MORNING_CHAMPIONSHIP_REPORT.md`、`SOURCE_DELIVERY.md`。
- **实际model.complete和官方存储回读：3/3，扣0。** 真实模型调用与Storage/Readback已证，不由开发Agent代做 证据：`RC10_LIVE_NODE_SUMMARY.json`、`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`。
- **manifest权限与宿主服务集成：2/3，扣1。** 扣1：源码SDKda布尔桥未进入最终Host938/SDK3f；另一个Host0fd实际读取仍schema拒绝。 证据：`RC_ACCEPTANCE_MATRIX.md`、`RC_CODE_FREEZE.json`、`official_muse/rc/startup/RC10_CALENDAR_READONLY_UI_SUMMARY.json`。
- **官方准入与发布认可：0/2，扣2。** 扣2：本地开发Gate/签名及七题scan packet不等于独立reviewer、正式publisher/政策或官方正式准入。 证据：`MORNING_CHAMPIONSHIP_REPORT.md`、`SOURCE_DELIVERY.md`。

### 复现交付

- **版本、源码、运行时和证据可追踪：3/3，扣0。** SHA及提交绑定明确，源码SDK和旧运行SDK分开 证据：`RC10_DELTA_BINDING.json`、`RC10_LIVE_NODE_SUMMARY.json`、`official_muse/rc/startup/RC10_STARTUP_70_SUMMARY.json`。
- **生产资料保护和证据保留：2/2，扣0。** 旧资料和失败保护按文档与公开证据核对，未检查生产目录，不声称全仓无Secret。 证据：`RC_ACCEPTANCE_MATRIX.md`、`SOURCE_DELIVERY.md`、`OVERNIGHT_SOAK.md`。
- **当前可复现交付材料：2/4，扣2。** 扣2：folder导出工具14最小fixture/边界守卫通过，但只1725字节合成源，正式F/桌面导出未做；旧Intel087包仍rc5，当前薄包不是独立可运行成品。 证据：`MORNING_CHAMPIONSHIP_REPORT.md`、`SOURCE_DELIVERY.md`、`official_muse/rc/packaging/RC10_SOURCE_FOLDER_TOOL_SUMMARY.json`。
- **clean全构建与新Host：0/3，扣3。** 扣3：clean SDK12000恢复有证，完整新Host构建受容量中止；资源32闭合副本合并只保持内容/签名，无编译成功。 证据：`official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json`。
- **第二Mac/ARM/电脑重启：0/3，扣3。** 扣3：均未完成，旧机暖运行和Shell进程重启不替代 证据：`official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json`、`RC_ACCEPTANCE_MATRIX.md`。

### 差异化

- **可追溯记忆和跨聊天更正遗忘：4/4，扣0。** 真实当前记忆六步支持产品特性 证据：`RC10_LIVE_NODE_SUMMARY.json`、`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`。
- **统一任务上下文和同事项版本绑定：2/3，扣1。** 扣1：原事件关联及改期主要fixture，最终外部同事项链待 证据：`official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`、`RC_ACCEPTANCE_MATRIX.md`。
- **主动提醒、批准与验证的产品组合：2/3，扣1。** 扣1：本地结果与历史真Mail提醒有证，当前后台真实账号连续体验尚缺。未比较竞争作品，不推断领先 证据：`RC_ACCEPTANCE_MATRIX.md`、`RC10_LIVE_NODE_SUMMARY.json`。

## 关键核对

- 70新启动raw报告SHAdf8adb74核对，30/20/20条逐项pass、受保护状态及ledger一致；100重开raw SHAeabaefce核对，恰100普通重开通过，无cold/restart条目。不是170次电脑重启。
- 当前55行证据索引路径均存在；私有raw路径仅检查存在，不打开。公开Memory双保存/无回退/零重复写入/首恢复及Goal一批准/8SHA/no-replay按同产品摘要审阅。没有独立实测或新模型调用。
- A3冻结review每模型28唯一行，原20各19PASS1FAIL/setup2与holdout6均PASS。M3 S02 provider原文/usage不可见，只能称Host invalid_output；M2.7 R02未说明缺回执原因。M01冻结语义PASS同时有额外grounding失败，不改规则将其强改PASS或FAIL。28输入含4本地步骤，不是28次model.complete。
- folder10+4最小fixture结果SHA均核对；1725字节合成源不证明正式全源S/F导出、接收者安装或运行。
- 32个闭合字节相同分发文件合并，分批实际可用观测增210481152字节，包含并发分配影响；既不按320MB逻辑尺寸算净回收，也不当新Host编译。

## Root文档与缺证据

- **C01 STALE_SCORECARD_SCOPE**：CHAMPIONSHIP_SCORECARD.md标题rc9，却段落写当前候选/当前内部A/B并称原28尚待；MORNING报告已经明确rc9是历史截点、rc10已完成28观察。 建议：Root最终冻结后将旧70显式标历史，引用本轮审阅；保留原FAIL，不以新观察把旧证据换版本。
- **C02 TRACEABILITY_GAP_NOT_FAILURE_PROOF**：MORNING报告声称当前rc10六文件/Git/mirror/pack、catalog与本地Gate通过；当前55行索引未有对应rc10 gate/scan直接行。A2没有重跑或读取私有gate目录，不能独立证成这项检查。 建议：Root加入已存在的确切check/catalog/scan摘要路径/SHA和版本；没有独立reviewer仍须记录。
- **C03 EXPECTED_UNFINISHED_GATE**：folder工具14fixture真实范围明确；正式F/桌面导出仍NOT_YET_PERFORMED，不能把工具测试PASS写成交付已完成。 建议：测试冻结后Root执行正式导出并固定S/F与manifest；本轮准备评分不给成品/clean/跨机分。
- **C04 SCOPE_GUARD**：模型original20是冻结聊天输入组，不等于产品T01–T20矩阵。56唯一输入含8本地setup/cancel步骤，不能写56次模型业务调用。M01冻结PASS与额外grounding失败并存。 建议：保留两层语义结论与known_usage/attempts未知；不改原20期待、不称模型全部通过。

## PARTIAL边界

原产品20项仍5PASS/14PARTIAL/1BLOCKED。T17不全过，T18仍BLOCKED，T20仍PARTIAL。隔离Mail凭据缺失，没有真实同步/发送；旧授权Host0fd只读Calendar被schema拒绝，没有创建/改期/get链。旧稳定版自发自收/历史系统读取不改标rc10全链。

待完成：rc10独立完整7200秒合成驻留、正式F/桌面导出、final Host Calendar桥与身份授权、精确系统事件写入授权、最终Mail/Calendar/回复同事项全链、电脑重启、clean构建、第二Mac/ARM及正式publisher/政策/业务视频/独立审核。合成驻留即使通过也不替代真实账号长测。

本次未宣称官方评分、95分、第一名、READY、完整UI_PARITY或完整官方准入。旧失败保留；本审阅不改主矩阵/scorecard/清单。

## 精确新增文件

1. `official_muse/rc/core_chain/RC10_INTERNAL_B_REVIEW.md`
2. `official_muse/rc/core_chain/RC10_INTERNAL_B_REVIEW.json`

各子项commit/file/test/SHA、静态核对与扣分见JSON证据registry。等待Root精确新增7200摘要后，仅一次更新相关分项，其他未完成门槛不预加分。
