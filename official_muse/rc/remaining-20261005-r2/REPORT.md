# Muse rc35 缺项修复与收口

状态：**PARTIAL**。原二十项没有完整重跑或全部通过；此前5 PASS /14 PARTIAL /1 BLOCKED计数保留为原矩阵历史判定，不把本轮局部通过合计成二十项通过。

## 当前候选

- 产品提交 `0f8e027d4e23081681df49a7395e7718cdf79d2c`，版本 **0.3.26-rc35**。
- 可读源码 `de37933e0894a838c17d664f265fa6e9c4ad8f5211a2c133927cca012a94f9e3`。
- compact/实装载荷 `800b11dca4717fb37b100ae4680385a4ea8eae548538d2d187350c698793c2af`，官方96651 tokens逐个相等。
- 运行Host `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`不变。当前源码SDK锁f487df0c相对Host构建锁78a5eef0只多两处测试修改；生产源码相同。
- 真实前台App Hub安装rc35、catalog67；安装六份核心文件SHA保持。signed check/scan/catalog验证PASS属于本地扩展演练，没有独立publisher评审或官方上架。

## 已修复

1. 收件核对分段提交，保留同request绑定、防重复与旧半提交恢复，不重发已受理邮件。
2. 记忆校验复用已接受字节与成对校验、缩小相关冲突检查；逐条64条保存、更正、第65条拒绝及新进程恢复已实际验证。未增大预算或清历史。
3. 日历批准、执行、关联保存、独立get、结果及记忆拆成绑定短回调。异步阶段检查账号/归属/来源/修订/Goal/Run/精确payload；重复点击不清除原批准。
4. 缺RFC回复关联时可由用户明确选原事项；保留同账号、项目和归属约束，不按相同主题猜关联，不新建替代事件。
5. 改期来源、claim、同Goal修订及关联分段保存；模型检索完成后下一短回调再构造请求，并检查记忆更正、遗忘、授权及焦点是否变化。
6. 同一事项的不同已完成内部Run回执是执行历史。rc35避免将日历结果与邮件结果自动当作矛盾；仍核对生成ID、local_runtime、fact、completed Run和Goal绑定，显式contradicts、用户事实及偏好冲突不豁免。

## 真实外部结果

唯一验收事项 `MUSE-R2-REMAINING-20261005-2008`，同一Goal `1791202432-60103582`：

| 节点 | 实际版本与结果 |
|---|---|
| 源邮件/自动来信卡 | rc28发送一次；rc29记录本人收到，实际同步及正文读取 |
| Work日历创建 | rc29创建一次，独立get verified；原失败写前零dispatch保留 |
| 电脑日历外部修改 | 同一UID改到15:10–15:40，rc29刷新发现变化 |
| 改期来信 | rc29发送一次、自动卡与本人收件声明；缺RFC关联安全阻止后提供明确原事项选择 |
| 同原事件改期 | rc34真实模型attempts1生成候选，Work冲突复查、一次批准、同EventKit ID update/get至2026-10-06 16:00–16:30，北京时间 |
| 关联确认邮件 | rc34发送一次；本人确认到达，实际核对按钮令draft/action verified、Goal v4/Run completed |
| Result/记忆 | rc34 mail-v4结果文件独立存在且SHA核对，3条相关执行结果claim保留 |
| Shell恢复 | rc35同资料正常quit/新进程launch，8份文件和模型ledger字节保持、同request、动作数不变，没有重发 |
| 清理 | rc35后按本人授权在macOS原生日历精确UID清理；独立新查询标题/UID均0。首次对象引用错误保留，确认1/1未删后换精确UID删除，仅一次实际删除效果；不是Muse delete/get通过 |

这是跨rc28/29/34/35的真实连续事项，**不标成同一最终候选完整整链PASS**。详细安全投影为本目录RC29、RC34、RC35开头JSON；真实账号/正文截图与运行数据保留private，不公开。

## 模型

- rc34真实安排模型成功，rc35普通科学问答成功，strong/attempts1/known_usage，官方model.complete保持。
- 用户已授权的GPT配置在同一Host/资料/官方model.complete上单独测试，唯一candidate、无fallback，账本44→45 calls，返回provider错误、usage未知。保留 `GPT_SINGLE_REAL_CALL.json`；没有重试冒充通过。
- 该GPT配置使用自定义route，不能证明官方OpenAI endpoint或代理实际后端身份，更不能宣称第二strong语义验收成功。原MiniMax设置已恢复，原始profile哈希未改。
- rc35刚重启后的一个请求在model调用前失败，原记录 `RC35_POST_RESTART_PREFLIGHT_FAILURE.json` 保留；原因未确定。随后稳定后的普通Chat真实成功，不把后者覆盖前者。

## 测试与构建

- SDK默认完整Shell suite：**558 PASS /0 FAIL /0 ignored /0 filtered**；旧release 552/6、修正TMP后554/4失败保留。最终只改两处test-only namespace/中文查询断言。
- 空target release Host完整重建：PASS，1476.884秒、locked/offline/-j2；复用现有Cargo/SDK缓存，不是全新网络和空缓存。新二进制未替换本轮运行Host。
- 最终rc34 manual replan密集测试20 runtime＋27独立磁盘字段检查PASS；其他64容量、引用/关系、收件与Calendar guard按各自源码身份记载，详见a2允许清单与报告，不虚构全部在rc35重跑。
- rc35回执分类及scope/access窄fixture **19 PASS**。使用实际生产函数和真实隔离Card5276，但文档对象是最小合成内存输入，不是OS/模型或DSL持久事务整链。首轮相对路径错误保留；修正为绝对路径后另跑。
- 本轮失败：容量预算、forget时序、rc28写前预算、rc31序列化绑定、rc32检索累计预算、rc33引用构建、rc34首次安装身份不符、回执误冲突、GPT provider与重启后早期失败均保留。没有提高64ms/20M/64MiB或100calls/100000tokens限额。

## 尚未关闭的门槛

- 同一最终候选从源信、创建、两封处理、原ID改期、回复到达、重启到跨聊天记忆的完整链。
- 第二独立strong模型真实可用和冻结语义集全部通过；旧模型语义失败不能由单题成功冲销。
- 最多两个真实核验替代时间、最终真实服务故障/恢复与真实账户2小时观察。
- macOS整机重启、两台接收Mac实测、全新checkout空缓存重建。
- Muse清理UI的本轮导航未完成；不能把原生日历清理冒充Muse delete/get验收。
- 正式隐私政策URL、正式publisher登记/密钥材料、独立审查、最终AppHub提交仍未完成。

## Git与保护

按本轮明确授权普通同步 `9tuore/muse-agent/main`，不force，不移动旧Tag，不创建成功Tag或提交AppHub。公开允许清单和增量审查控制发布范围；不上传凭据、私人邮件、profile、数据库、运行包或新私人截图。稳定0.3.25、旧独立安装包、生产和未提交baseline保留。

最初rc28报告见 [REPORT_RC28_ARCHIVE.md](REPORT_RC28_ARCHIVE.md)，历史版本的失败与边界不改写。
