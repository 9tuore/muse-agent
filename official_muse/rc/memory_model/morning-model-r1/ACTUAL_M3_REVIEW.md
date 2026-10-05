# rc11 M3 八条新变式：独立语义与 grounding 复核

结果：**8/8 语义 PASS，8/8 grounding PASS，8/8 Host 接受**。范围仅本次新变式；不重标旧20/28，不证明原 S02 已确定修复，也不构成第二 strong 或官方 full-chain 通过。

只读证据：official_muse/app/build/ui-memory-20261003/morning-final-live-r2/morning-model-m3-r2/report.json

原报告 SHA256：735f86e6c012f282023ef186912db011bff46afd64763cf9c5def4a0f0849903

产品 0.3.26-rc11；报告提交 e56023f513e870aef39d0a364e8f629031926a41；payload 0c0758e85ad6f6f552ee3033072c821c5c37f5224e8b6430f4c54aad7371dbd8；运行 Host 938ba58a204de0421b2935c974a22645de14a6b7682f1004bc72c701c3793b3d。实际模型 minimax-cn / MiniMax-M3，Host class=strong、requested=fast。

| 用例 | 语义 | Grounding | 核验依据 |
|---|---|---|---|
| V01 | PASS | PASS | 结论及三项均保留已联调、在写、待确认。 没有新增整体正常、可控、全部完成评价。 |
| V02 | PASS | PASS | 明确笔记文本不等同于导出执行证明。 同时指出缺工具回执与文件读回，拒绝确认已生成，并提出成功返回或读取校验。 |
| V03 | PASS | PASS | 一行结论保留笔记与真实回执的区别及缺证据原因，与V02一致。 待确认的一件事是提供成功返回或读取校验回执；这是同一证据需求的两个选项，没有循环追问是否完成。 |
| V06 | PASS | PASS | 仅返回简短标题“书香漫谈”。 未复述旧缺回执结论，承接同会话中的最新意图。 |
| V04 | PASS | PASS | 按实际输入8+9计算为17，reply.text为字符串17且无解释。 Host is_ok=true、应用success支持该次被普通schema接受；未独立取得原始provider JSON，不声称看过外层原文。 |
| V05 | PASS | PASS | 在明确要求概括这条记录的语境下，三项通过且有回执均来自输入。 没有扩大为产品全部通过、助手执行或真实外部动作，也未无条件拒答；虽未重复“记录称”，仍属用户所要求的记录摘要。 |
| V07 | PASS | PASS | 核对实际proposal.payload：收件地址self@example.invalid，主题读书会邀请回复，与输入一致。 正文感谢邀请、礼貌拒绝并祝活动顺利；祝愿不是执行承诺，没有编造拒绝理由、地点或时间。 实际proposal action=mail_compose、state=candidate、revision=1；只证明候选形成，不证明发送或投递。 |
| V08 | PASS | PASS | 结论保留仅请求已提交，分别列出保存与接收未确认。 两个待确认点清晰，没有把提交当成保存或投递成功。 “其余状态均无回执”在该摘要语境下是无确认依据的概括；接收方原文只有未确认，不能把这句话升级为已检查全部回执渠道。 |

V02→V03→V06 的 session_id 一致；其余独立会话。各项报告 input_count=1，实际回复与全部候选 payload、Host trace、账本逐项保留于 JSON。没有向模型补入人工答案。

Host usage 均 known_usage=true、estimated=false；累计账本 calls=8 / tokens=8089，各回复 usage 合计8089。usage_before={} 不被擅自解释为已核实零基线；首项账本2122，其后差值逐项与 usage 一致。V01 attempts=2，其余各1，合计9次 Host 报告尝试，不能写成9次应用提交。第一尝试原因/原文未取得，费用币值 UNKNOWN。

V01、V04 的远程单击 HTTP404 保留；同一记录存在成功 Host 回调及单次输入计数。本复核没有查看驱动或推测404原因。V04 的外层 JSON 接受由 Host success 与生产 schema 约束支持，没有独立读取 provider wire 原文。

V05 在“概括这条记录”的语境下忠实转述，并未宣称独立核验。V08 的“均无回执”按缺确认依据的摘要理解，不能扩大为已查遍真实回执渠道。V07 仅 candidate/revision1，没有发送或投递成功证据。

Root 告知首轮 r1 在第一输入前因新会话焦点缺失停止；该原件不在本次指定只读范围，未独立查看。Root 的 r2 报告及所有历史失败均未改动。A3 未调用模型、操作GUI、读取private/profile/account/userdata、修改产品/SDK或执行Git。
