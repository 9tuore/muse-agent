# Muse RC 二十项验收矩阵

当前工作版本：0.3.26-rc2。当前状态：进行中 / PARTIAL。
开始 2026-10-04 21:51:29，截止 2026-10-05 00:51:29（北京时间）。
原二十项标准不变；原18/20允许门槛不用于本轮READY。下面的历史支持不等于最终候选真实整链通过。

| 项 | 状态 | 当前证据及判定边界 | 尚需完成 |
|---|---|---|---|
| T01 | PASS | 独立分支、公开基线与原开发HEAD核对；旧未提交证据、生产资料、旧安装保护；RC_BASELINE.md | 最终身份另记录 |
| T02 | PARTIAL | RC2 incoming 40项fixture及核心28项/重启4项；嵌套request_id导致恢复异常已修。历史真实提醒仅为支持 | 同RC真实多封新信/重连与恢复 |
| T03 | PARTIAL | 无模型许可仍提醒与手写的守卫有fixture和历史实机支持；新paid调用0 | 同RC官方账号默认提醒、授权开关 |
| T04 | PARTIAL | account preflight 12项、来源记忆/项目账号隔离8项fixture | 同RC指定真实邮件归属/相关记忆 |
| T05 | PARTIAL | 单动作24项Memory/新进程9项通过；64条记忆boot诊断成功；组合58项64ms失败保留 | 64条更正/遗忘、同RC模型跨对话召回 |
| T06 | PASS | 原定义的软硬约束、窄授权与未批准零写入守卫未变；RC2 calendar policy 24项与scheduling 102项通过；历史精确批准支持 | 新外部写入仍需精确确认 |
| T07 | PARTIAL | 不用了取消8项、绑定回复9项、错误UI10项、日期与约束fixture；未把fixture当模型推理 | 最终真实模型语义15题 |
| T08 | PARTIAL | 最多两替代/四天/只查目标日历由102项fixture覆盖 | 同RC真实查询核验两替代 |
| T09 | PARTIAL | RC2核心创建/独立get/存储断言通过；旧真实创建不拼入T18 | 同RC邮件Goal真实创建与读回 |
| T10 | PARTIAL | RC2同Goal/version/原事件改期/独立get核心和25项稿件变体通过 | 第二真实邮件修改同事件并独立读回 |
| T11 | PASS | 原定义的多匹配/缺事件/错来源/只读/撤销阻断由当前fixture及未改历史支持证明 | 新宿主系统授权需本人核对 |
| T12 | PARTIAL | stale callback 12项、旧批准失效与UNKNOWN恢复有fixture；原失败保留 | 最终实机异常恢复/外部Calendar刷新 |
| T13 | PARTIAL | 逐封处理、同事项绑定、重启4项及稿件重启6项fixture通过 | 两封真实来信顺序处理 |
| T14 | PARTIAL | 同事项结果连续性有核心/稿件fixture；日程失败显式重试/手填有10项检查 | 同RC真实卡逐状态与截图 |
| T15 | PARTIAL | 手写稿/采用新稿/原时间与建议时间25项fixture及6项新进程检查通过 | 最终真实自动稿、手写保护/采用选择 |
| T16 | PASS | 原定义的独立发送批准、防重复、未知投递保护由当前守卫及历史本人发送/到达支持 | 本轮新发信须分别批准与确认到达 |
| T17 | BLOCKED | 已有MiniMax-M3；第二个独立较强模型未配置。localhost协议响应不算第二模型 | 本人提供独立通道及有界费用依据 |
| T18 | BLOCKED | 当前同RC合成核心28项、重启4项、稿件25项与重启6项通过 | 同RC真实邮件→记忆→日历→改期→自动稿→确认发送/到达→重启→跨会话 |
| T19 | PASS | 原生两行、省略、54px等高和完整标题存储未改，本人此前确认方案；历史可见视口支持 | 最终RC窄/矮/宽可见截图 |
| T20 | PARTIAL | 原Host诊断实测非空16对话/256消息/64记忆；分批校验最大24.896ms；预算未变 | 新Host固定候选10次完整Shell冷启动、5次重开、电脑重启 |

## 版本证据

- 可读入口SHA256：e51a395628804ae8d6585f5699dbb376e8b2476325f3cf7231bf05a8fc338dd4。
- compact入口SHA256：95364c035be80d1fd7265d0711c10842a199ef18bff756f2b5d7782935b7a655。
- 官方tokenizer：88,282 token逐项相同，包括字符串和换行语义。证据 official_muse/rc/startup/token-equivalence.json。
- RC2根回归：official_muse/app/build/ui-memory-20261003/rc2-root-regression/report.json，133项通过，fixture生产函数/本地隔离存储。
- 核心链：official_muse/rc/core_chain/t18-result.json。新宿主协议测试尚未运行，不计模型推理。
- 记忆/模型：official_muse/rc/memory_model/RC2_RETEST_REPORT.md；原始组合预算错误、探针启动错误保留，不删除失败测试。
- 新宿主、Hub构建与最终签名、check/scan：待后续真实结果，未运行项不补PASS。

## 必要旧门槛

Goal→Plan→用户批准→model.complete→Storage→Readback→Shell Restart Restore仍须在同一最终候选验证。编译通过、窗口/卡出现、模型说完成、SMTP受理都不能代替实际动作、独立读回或收件到达。Calendar为声明的本地EventKit扩展，不称官方原版已接受。全二十项及旧关键门槛全过才READY、合并或创建新成功Tag。
