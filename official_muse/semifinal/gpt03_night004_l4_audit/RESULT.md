# NIGHT-004 L4 边界审查与实际 Mail 持久化故障

2026-10-12（Asia/Shanghai），GPT03。审查范围 **PARTIAL**；新交付的 Mail 持久化组件 **8 阶段、107 项 PASS（原三场景78＋新增实际计时29）**。没有修改生产 Main、SDK、GUI、共享 target 或用户资料，没有启动 Kernel/GUI，没有真实 SMTP、模型费用或 push。原指令附件的 L4 第 373–403 行要求逐项预期状态、最终数据及副作用计数；本报告按这些要求列证据，不把组件数量相加成全链 PASS。

## 固定候选及证据身份

- 实际可读 Main：`c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`。新探针分别从该文件提取调用闭包，其余生产函数经 transport 归一化后逐字一致；仅沿用 7 个 IO/UI renderer 适配及显式 timer/clock/transport 边界。
- Root 签名候选：0.4.0-rc7 candidate-r3，Main `cdb1412b14a25fdbb8f97681e7fe344c855a0adaac50c26ded5eb17f876108d7`。实际 L3 报告包含版本替换＋原 compact 工具重放的字节映射，源为 c892，签名产物为 cdb。新组件执行的是可读生产函数闭包，没有执行完整签名 GUI。
- VM `f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351`；实际 Rust Mail helper `ba37b915b24917be68964c10c38409169b7162489fbd2de22c082a1e05055367`；独立 Python recipient `7be09ed1af4310f5d40bb108d807100d661058cba88f64a48c0504ac50bf5288`。
- 实际 Kernel `56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270`；Root 冻结 Shell test binary `270617f07d6af51bfc6ccda28913925386c74b75942735050ae3764bf8445385`。这些是只读核对的中央证据，本聊天没有运行它们。

`evidence/central-report-index.json` 保存 20 份实际中央报告的路径、原文件 SHA、检查及候选映射。中央原始证据仍在 Root worktree 的 `build/night-004/`，未修改或重新贴版本标签。

## 本轮真正执行的四个小场景

| 场景 | 初始 / 新进程检查 | 实际故障与初始持久化状态 | 新进程最终状态与副作用 |
| --- | --- | --- | --- |
| `crash-after-review` | 13 / 15 PASS | 实际 Mail 服务 accepted、独立 recipient 收到 1 条后，父驱动尚未向 Main 交付 `mail.review_send` 回执即 SIGKILL；VM exit **−9**。磁盘 Draft=`sending`，同 request Action=`in_flight`。 | 新 VM boot 为 Draft/Action=`unknown`；UNKNOWN confirm 没有发出 Review；只读 `compose_status` 对同 compose/request/attempt 核对后 Draft/Action=`accepted`。新增 transport=0、Review=0、recipient 原 message_id/所有字段不变。 |
| `receipt-os-error` | 13 / 15 PASS | 实际 review accepted 回执已交付，下一次保存回执时把自有 `mail-draft.backup.json` 临时换成目录；实际 `Path.write_text` 抛 **IsADirectoryError / errno21**。原 primary/backup SHA 均不变；Draft 持久化仍 `sending`，Action=`in_flight`；内存 Draft 已 accepted，但写入被禁，不能拿它宣称已持久化。 | 新进程 boot 为 UNKNOWN，再显式只读核对为 accepted；原 request/compose/payload/message_id 不变。新增 transport=0、Review=0，没有完成 Goal/Run/Memory。 |
| `review-cancel` | 11 / 11 PASS | 实际 SDK native review 对象执行合成 cancel，service 返回真实取消错误；Draft=`DRAFT`，attempt/preview 清空，原 Action=`failed`，正文保留。 | 新 VM/Mail/recipient 进程仍 Draft=DRAFT、Action=failed；transport=0，recipient=0，Review=0，无自动发送。 |
| `gateway-timeout` | 14 / 15 PASS | 实际service accepted/独立收件1后，fixture网关250ms延迟回包；实际Queue.get(timeout=0.05)等待 **57.603ms** 抛Empty，原reply **255.908ms** 后才入队并丢弃、不转发。Main及持久化Draft/Action=UNKNOWN；重复confirm无新增Review。 | 新VM/Mail/recipient只读同compose/attempt为accepted，Review=0、transport=0、原收件1条/message_id/完整payload不变，无完成Goal/Run/Memory。 |

PID 证据：崩溃 VM `48211 → 48264`，Mail `48209 → 48262`，recipient `48233 → 48270`；OS 写错 VM `48285 → 48350`；取消 VM `48370 → 48416`。各阶段报告记录完整 PID 及退出码；计时网关VM `86648 → 86750`，Mail `86647 → 86749`，recipient `86665 → 86768`。四个恢复均有不同的实际 VM/Mail/recipient PID。

崩溃不是“完成之后再 kill”：杀死 Main 时 review RPC 仍在等待，accepted reply 没有转发，应用的 accepted 回执/Action 终态尚未落盘。它覆盖 Main 的发信不确定窗口；没有覆盖 Kernel、Mail 服务或所有进程同时崩溃。现有全链 restart 是 VM/Mail/recipient/Kernel **正常退出后**的新进程恢复，与这里的 SIGKILL 分别列证据。

每个场景使用独立、带 marker 的合成 state。真实过程是官方 VM、实际 Mail service dispatch/draft/review engine、独立 recipient 子进程、文件系统写入和 SIGKILL；Vault、review 手势、MockTransport、UI、时钟及 timer queue 为 fixture。实际 SMTP=0。恢复只 drain 明确的只读核对，后台 Mail poll 仍排队未 drain。Goal/Run/Memory 为 0 是本组件的预期，没有凭空构造全链完成。

`verify_evidence.py` 另对保留报告核对 recipient 与实际 host attempt 的完整 payload、message_id、原请求、顺序、不同进程及 OS 前后 SHA，PASS。这是证据复核，不增加107项运行检查计数。原三场景的parent/闭包保留原字节；新增网关用更新的initial闭包及`executed-parent-gateway-r1.py`，报告记录实际执行脚本SHA。两批summary原78/29计数不改。

## 原指令 19 项对照

下表的 PASS 都带具体层级；“注入路径 PASS”不等于故障发生机制已验证。

| 要求 | 当前证据与终态 / 副作用 | 判断与边界 |
| --- | --- | --- |
| 重复邮件 | c892 Main CAS 初始 23 项：重复 incoming 不增加同一 Memory；来源保留。 | **PASS，实际 Main/Memory API，合成来信。** |
| 重复请求 | Main create/update 重复 confirm 不增加 turn；Kernel 同 request 同进程及新进程返回 `reused=true`、同 event ID、owner count=1/SHA 不变；Mail 同 compose 重审不重复运输。 | **PASS，实际 Main＋Kernel＋Mail，分别保留层级。** |
| 网络断开 | Mail `before` 分支实际调用 MockTransport 后 `failed_before_delivery`，Main DRAFT/Action failed；transport=1、received=0，恢复 transport=0；`unknown` 分支 actual recipient=1、Main UNKNOWN，不重发。 | **合成故障路径 PASS。** 没有实际 socket/SMTP 断连；无人值守模拟不需要真人邮箱。 |
| 请求超时 | 新网关14＋15：实际accepted后reply pending，50msdeadline实际等待57.603ms后Queue.Empty，250ms延迟reply于255.908ms入队并丢弃；Main UNKNOWN、repeat无Review，新进程只读accepted，初始transport1/恢复0。 | **PASS，明确fixture网关的实际计时deadline。** 旧立即注入只算丢回包；真实SDK/SMTP/network deadline未验证。 |
| Host 拒绝 | Main Deny 初始24＋新进程12 PASS；实际 native Kernel approval 在 peer tool call 前 Deny，owner 字节/单事件不变，Mail transport=0，无完成 Goal/Run/Memory。Main record `turn_completed/receipt_status=unknown`，重启仍 unknown。Kernel update/remove 两个真实 Deny PASS。 | **PASS，实际拒绝门禁及保守恢复。** 未执行的 tool 没有 Broker 执行回执；Main 不伪造 failed/verified，真实 approval audit/declined row 与执行 receipt 不混用。 |
| 权限撤销 | Kernel cdb 同 manifest、可信签名更高 sequence 目录撤回；真实新 turn 被 `App agent is unavailable … withdrawn` 拒绝，owner count=1/SHA 不变。 | **PASS，实际签名准入撤回。** 不是实际 OS 用户撤销权限或 Mail 全链撤权；旧 Mail L2 grant 移除是组件历史证据。 |
| 模型返回无效 JSON | c892 inputs26：真实生产 model callback 收到 fixture `invalid_output`，分类正确、无副作用；schema mismatch/URL 同样阻断。 | **PARTIAL：Main 处理 PASS；原始无效模型字节经当前 SDK parser 产生该错误的机制未验证。** parent review malformed JSON 是另一个边界，不能充当模型 JSON。 |
| 邮件正文包含错误指令 | inputs26：原内容以 external_claim 保存，context 无执行 authority；恶意文本仍只生成候选、waiting_user，无 Run/Action/send；未授权外部效果=0。 | **PASS，实际 Main 回调/Memory，模型与来信是 fixture。** |
| 进程异常退出 | 本轮 SIGKILL 13＋15，发生在实际收件 accepted、Main 尚 pending 回执且 sending/in_flight 未完成落盘时；新进程同请求只读恢复、不重发。Kernel 原 pending turn interrupt 的 interrupted 列表非空、同 turn/lane，实际 terminal `turn interrupted by client`，owner 无副作用。 | **PASS，Main Mail 不确定窗口＋实际 Kernel turn 中断。** turn interrupt 与进程 SIGKILL分别记录，不宣称全进程崩溃。 |
| 存储写失败 | Root真实 OS 写错发生在任何 compose/review 前：errno21、primary/backup SHA 不变、transport/received=0；同源 update99 的 journal/Goal 保存失败无 dispatch。 | **PASS，真实 OS 预派发失败＋生产控制路径。** update99 IO failure flag 仍是 fixture。 |
| 回执落盘失败 | 本轮实际接受/收件后，receipt phase 的 backup 写入 errno21；持久化 sending/in_flight，写入封闭，原字节保留；新进程 UNKNOWN→accepted，无重复运输。completion33 另有结果准备/Run 重写失败重试同 Run。 | **PASS，实际 OS Mail 回执写错。** Goal result/Run 重写的 existing IO failure 是 fixture，不能称同一真实 OS 故障。 |
| 数据损坏 | Root实际坏 JSON 写入合成 Goal/Memory 主备、update journal、Mail draft；新 VM boot 拒绝，原坏 bytes 不改，Goal/Run/Memory 不制造完成、transport=0。 | **PASS，实际文件＋新进程 fail closed。** |
| 原事件外部变化 | Main CAS 初始23＋新进程11：独立实际 CalendarService 对同 event 改 notes；实际 Kernel persisted CAS error + exact update args digest；owner 新值/原 ID/request 不被覆盖，事件文件 SHA 不变，旧草稿阻断、transport=0、无假完成；重启仍 unknown。 | **PASS，真正 owner 写入＋Kernel CAS＋Main 保守恢复。** |
| Calendar 冲突 | scale22 的 conflict node 只是投影 fixture；L3 查询时 owner 原为空。当前 native create 路径没有已验证的“已有重叠事件”场景。旧 `calendar_check_conflicts` 依赖被禁的历史 `calendar.list` 路径，不能拿来补 native PASS。 | **NOT_TESTED，原生重叠冲突处理缺证据。** 自有 `overlap_query.splash` 只准备实际 native query 可见性探针，尚未执行；即使它通过，也不证明警告/阻断创建。 |
| 用户批准过期 | update99 的 user/accounts/project/owner/version/candidate/selection/refs 变更阻断旧 confirmation；旧 draft preview 失效不发送；inputs26 旧/取消 callback不接新 chat。 | **版本、内容、身份绑定失效 PASS。** 当前没有批准时间 TTL 的机制或实际 deadline 证据；不推测时间过期规则。 |
| 大量 Memory | c892 scale22：64 Memory/128 Sources 保存；scope48/8/8，context5项/2125字节，6项/2200上限；第65/129拒绝且原存储不变。 | **PASS，实际生产 API 的容量与隔离。** 未测 GUI frame、heap 或延迟 benchmark。 |
| 多事务交错 | inputs26 两 chat callback/Goal 绑定，旧 A 不重绑 B；scale32 Goal/32 Run/128 Action 最终32＋128绑定一致；binding11 拒绝其他Goal/矛盾card；source/ref/revision守卫保留。 | **PASS，生产 API、合成并发回调顺序。** 实际 OS 并发线程/网络竞态未在该 scope。 |
| 大量行动链历史节点 | scale22：128 actions保留、每轮最新scan3窗口、projection最多12、picker最多8、节点unique且属于当前Goal；guard22含完整链恢复6及16篡改拒绝，无外部调用。 | **PASS，生产 API 容量/恢复/投影。** 不额外称 UI 速度合格。 |
| 重启后恢复 | 同候选实际 L3 初始28＋全进程正常restart15 PASS：Goal/Run completed、3条Memory（2 external_claim＋1 verified fact）、原行动链4节点、同event/compose/message/request；新chat召回、恢复 transport0/turn0/review0。另有实际Deny/CAS恢复、本轮3场景新进程恢复。 | **PASS，明确正常退出与故障恢复边界。** 组件证明不替代官方本人真实授权 E2E。 |

## 最小剩余工作

fixture网关实际计时超时已新增29项PASS，不再列为缺口。50ms/250ms是明确fixture参数；真实monotonic/queue/thread证明等待过期，没有修改生产函数或生产时限，不称真实SDK/SMTP/network超时。
1. **无效模型 JSON 的解析机制**：用当前 SDK 原 decoder 接收确定的合成坏输出，使它真实产生 `invalid_output`，再接原 Main callback；检查分类及 Goal/Action/transport=0。无需真人模型或付费调用；不能直接填写该 error 就宣称 decoder PASS。
2. **原生 Calendar 重叠冲突**：复用同候选标记 state 的既有合成事件，实际 `calendar.events` 读出与待选候选相同起止的原事件，然后观察 production warning/confirmation 是否阻断或要求新的明确选择；owner SHA、mutation tool count、Mail count不得改变。`overlap_query.splash` 已从 c892 准备 275 函数/159 global 的真实调用闭包，但 **PREPARED_NOT_EXECUTED**，只解决读取可见性，不能代替完整冲突行为。未修改 Main。

Host Deny、同 request 复用、签名撤回、实际中断及外部 Calendar CAS 已读回新中央结果，不继续列成未完成，不重复执行。时间 TTL 若并无产品规则，应在最终结果明确批准绑定版本/内容的范围；不能臆造 TTL 测试或接口。GUI/Calendar owner 的绘制问题由 Root 处理，不属于本次 L4 代码或测试。

**建议最终状态：L3 可按已有同候选证据保持 SIMULATION_PASS；本单元 Mail 组件 PASS；L4 总体 PARTIAL，直到上述必要缺口有实际证据。REAL_E2E_PASS 不成立。**

## 2026-10-12 caa99 新执行

107/107 PASS；新prepare/新进程/新归档，只有core_boot_goals摘要改变。详见CANDIDATE_CAA99.md与evidence/candidate-caa99-r1。旧证据不改，Host64ms/GUI/full-chain不计入。
