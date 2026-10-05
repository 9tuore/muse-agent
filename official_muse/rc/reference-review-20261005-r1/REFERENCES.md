# Muse rc18 定向参考：只读审查与独立实现建议

范围：仅核对五个公开作品、现有源码快照和Muse相关代码；无竞品脚本执行、模型/GUI调用、Git操作或产品修改。仅提出以下三项改进，未实施、未新增评分。

本地榜单确认前三并列88：BUNotesAI Invoice-Reconciliation、WeiR-h buwei、codezzzsleep OnCue。Loom84、VibeMail83。**这是本地源码评审、自定权重，非官方竞赛榜。** 不承诺名次，不把源码可见机制当真实闭环通过。

| 公开仓库 | 当前默认分支commit | 应用许可证 |
|---|---|---|
| [BUNotesAI/Invoice-Reconciliation](https://github.com/BUNotesAI/Invoice-Reconciliation) | 17d8198fc22826facdd0c8f1fd60c55d55affdd1 | [Apache-2.0](https://github.com/BUNotesAI/Invoice-Reconciliation/blob/17d8198fc22826facdd0c8f1fd60c55d55affdd1/LICENSE) |
| [WeiR-h/buwei](https://github.com/WeiR-h/buwei) | baeb57d74b3f30f6017962f869cd4939dff6172d | [Apache-2.0](https://github.com/WeiR-h/buwei/blob/baeb57d74b3f30f6017962f869cd4939dff6172d/LICENSE) |
| [codezzzsleep/OnCue](https://github.com/codezzzsleep/OnCue) | 7b7b2e241628a27f4fa5de541af8f187950cf1c1 | [Apache-2.0](https://github.com/codezzzsleep/OnCue/blob/7b7b2e241628a27f4fa5de541af8f187950cf1c1/LICENSE) |
| [yzbtdiy/VibeMail](https://github.com/yzbtdiy/VibeMail) | 5f703910e6907ecda99a94367297680030a14705 | [Apache-2.0](https://github.com/yzbtdiy/VibeMail/blob/5f703910e6907ecda99a94367297680030a14705/LICENSE) |
| [dyingforge/loom](https://github.com/dyingforge/loom) | b0f7af71fd758862a9bc563f084f75b717880aa6 | [未找到应用许可证，仅概念参考](https://github.com/dyingforge/loom) |

当前commit由公开仓库页currentOid核对，均与本地逐项审查一致；GitHub API限流403已如实保留为方法限制。选取的许可证及源码从固定commit raw地址读取，与已有快照字节一致；未下载整个仓库。Loom根LICENSE返回404，快照未找到应用LICENSE/COPYING；README提及字体OFL，不能作为应用代码授权。所有建议均独立设计，不直接复制竞品代码。

## R1 · 用已确认边界校验搜索范围，模型不能扩大约定

来源：[dyingforge/loom · server/domain/scheduling.py · free_slots](https://github.com/dyingforge/loom/blob/b0f7af71fd758862a9bc563f084f75b717880aa6/server/domain/scheduling.py#L26)；[dyingforge/loom · server/domain/constraints.py · validate](https://github.com/dyingforge/loom/blob/b0f7af71fd758862a9bc563f084f75b717880aa6/server/domain/constraints.py#L10)；[BUNotesAI/Invoice-Reconciliation · bot/src/validate.rs · explanations / explanation_rules](https://github.com/BUNotesAI/Invoice-Reconciliation/blob/17d8198fc22826facdd0c8f1fd60c55d55affdd1/bot/src/validate.rs#L242)。

已核实机制：Loom按输入范围裁剪可用区间并对完整候选再验证；Invoice把模型解释与允许事实引用、确定性状态分别校验。不是声称竞品直接实现Muse的同一规则。

Muse现状：schedule_policy_error已检查格式、4日上限、时区和preferred属于hard；schedule_candidate_error检查候选位于policy。已读代码未见与独立的本次已确认窄范围作交集的检查，因此模型自洽仍不足。

建议：在现有calendar link保存已明确且来源绑定的本次约束边界（如现有字段不足，新增字段是拟议接口，不声称已存在）。接收模型结果时，以独立确认边界约束search/hard/preferred；超出则拒绝为候选并说明缺项，不能只依赖模型reason。区间计算沿用calendar_iso_epoch等既有路径。已确认改期使用新要求边界，不把旧事件时间当新硬边界；自然语言未明确时询问，不扩大默认范围。

落点：calendar_model_candidate, schedule_policy_error, schedule_candidate_error, schedule_free_slots, schedule_find_slots。仍在官方Splash候选校验及既有Host calendar.list/get流程内；不引入Loom Python服务、任务拆解或新runtime。

验收边界：同一来源明确10月5日时，生成5日至8日policy必须被拒绝或在展示前确定性裁剪；空交集须澄清；获准改为新日期时按新范围。原rc17范围FAIL保留，以上只是未来验证要求，本轮未运行。

许可：Loom无应用许可证可核实，仅取区间/完整候选校验概念，独立设计；Invoice Apache-2.0也不直接复制。

## R2 · 以同一外部事件和请求身份贯通改期、回复与恢复

来源：[WeiR-h/buwei · native/crates/action-receipts/src/lib.rs · Journal::execute / finish / reconcile](https://github.com/WeiR-h/buwei/blob/baeb57d74b3f30f6017962f869cd4939dff6172d/native/crates/action-receipts/src/lib.rs#L388)；[dyingforge/loom · server/runtime/reconcile.py · verify_calendar](https://github.com/dyingforge/loom/blob/b0f7af71fd758862a9bc563f084f75b717880aa6/server/runtime/reconcile.py#L32)；[codezzzsleep/OnCue · oncue/bundle/main.splash · cue_save_text](https://github.com/codezzzsleep/OnCue/blob/7b7b2e241628a27f4fa5de541af8f187950cf1c1/oncue/bundle/main.splash#L854)。

已核实机制：BuWei按账号/目标/digest/operation匹配外部证据，未知状态只查询不重发；Loom检查获准版本及完整回读快照；OnCue写后逐字回读、失败保留编辑内容。

Muse现状：Muse已有request_id/expected_version、calendar.get字段核验、结果写回读、unknown禁止重发和SMTP accepted区分；这些无需重做。最高缺口是同最终链的实际衔接与恢复证据，不能由竞品源码填充。

建议：在现有恢复与完成条件中逐项核对已保存link/receipt/draft所指同一个calendar_id、event_id、version、source及request_id；只修发现的断点。改期必须update原事件，恢复不得把已受理/未知邮件降回可发送草稿；若Host无可核实收件回执则维持accepted/unknown。展示断在哪一段并保留精确确认，不新建总控框架或SQLite。

落点：calendar_action_payload, calendar_prior_attempt, calendar_readback_written, calendar_finish_link, calendar_restore, mail_send_confirmed, mail_finish_linked_result, mail_save。复用官方Host calendar.get/update与mail.send既有调用、应用存储及现有link/receipt；不移植BuWei adapter或Loom远程服务，不假造mail投递查询API。

验收边界：在用户已有具体外部授权范围内，后续由Root用同一最终事件证明原ID改期、独立读回、另确认回复、恢复身份一致；缺真实结果仍PARTIAL。代码已有同等检查则仅补证据，不重复实现。本轮不执行该外部链。

许可：BuWei/OnCue Apache-2.0；Loom仅概念。全部独立实现，无直接复制。

## R3 · 同一状态只展示一次，来源和动作阶段清楚可见

来源：[yzbtdiy/VibeMail · bundle/main.splash · summary_state_word / summary_lines](https://github.com/yzbtdiy/VibeMail/blob/5f703910e6907ecda99a94367297680030a14705/bundle/main.splash#L570)；[yzbtdiy/VibeMail · bundle/main.splash · detail_screen](https://github.com/yzbtdiy/VibeMail/blob/5f703910e6907ecda99a94367297680030a14705/bundle/main.splash#L1784)；[codezzzsleep/OnCue · oncue/bundle/main.splash · cue_set_status](https://github.com/codezzzsleep/OnCue/blob/7b7b2e241628a27f4fa5de541af8f187950cf1c1/oncue/bundle/main.splash#L26)；[codezzzsleep/OnCue · oncue/bundle/main.splash · cue_save_text](https://github.com/codezzzsleep/OnCue/blob/7b7b2e241628a27f4fa5de541af8f187950cf1c1/oncue/bundle/main.splash#L854)。

已核实机制：VibeMail区分模型摘要/正文截取/不可用来源，在一个详情区域组织内容；OnCue给出明确保存结果，失败保留输入。仅借鉴状态呈现，不借其视觉资产或文案。

Muse现状：已有technical_toggle、activity_summary及right_content/right_page_content两套布局；代码重复不证明两者同时可见，本轮无GUI复现。mail_send_confirmed明确accepted未核验投递，而activity_summary的已发送措辞值得统一。

建议：让桌面右栏与窄屏详情共享同一当前动作选择结果，优先显示需确认或失败的当前项；同request/event/revision不重复列完整结果，只保留一个详情入口。正文默认展示来源、候选/已核验状态、下一动作；技术ID与历史放现有technical_open。把受理与投递文案统一为真实阶段，保留失败原文于详情。只改已有展示和必要共用状态选择，不新建Goal页或新功能。

落点：activity_summary, technical_toggle, right_content, right_page_content。原官方Splash部件/响应布局，Host调用与授权确认不变。

验收边界：后续只需核对宽/窄布局、pending/accepted/unknown/verified几种现有状态不会重复和误称完成；本轮仅源码评审，未声称视觉已修。

许可：VibeMail/OnCue Apache-2.0，但按用户要求独立实现、不直接复制；不采用VibeMail的accepted→sent简化或可变数组下标异步绑定。

## 交接边界

优先R1，其次收口R2的同一最终外部链，再做R3。R2中Muse已有的机制无需重复实现；没有证据时不把待验证改成完成。保留rc17扩范围FAIL、G02普通语义FAIL及旧28失败。GPT-4o备用项出现在官方设置不等于已连接、真实调用成功或第二strong通过；本建议不新增provider或runtime。

Muse源码只读绑定 SHA256：f86384dca2fba10f11825690726e07bf238711bf9d6b657fcc18cf37ed0813e8。Root可能并发修改；JSON记录各函数/布局的定位行号，实施前应核对当前版本。未修改主报告、共享矩阵、代码、测试、profile或Git；仅本目录REFERENCES.md/json。

完整仓库、commit、文件SHA256、license、函数定位与建议结构见REFERENCES.json。
