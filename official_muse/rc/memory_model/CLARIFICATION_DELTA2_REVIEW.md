# Root clarification delta 2 — static review

只读审核 readable SHA `9fefe620f1b98d2fdb480ab0495747ff4ad31bf6527c82397675f059efe436aa`。本轮 A3 未运行 Card、未调用真实模型、未改产品、未动 Git 或8510。A2负责实际Card，Root负责真实M3；旧D05和A3首次失败证据保留。

结论：本次小delta在静态上合理，未发现新增阻断问题。新增两项helper、三处 predicate/regex 调整和一条prompt句子，逆向撤销这六项后，整个文件与旧33d5d2快照字节完全相同。没有其他隐藏变更；完整证明见 CLARIFICATION_DELTA2_STATIC_PROOF.json。

按源码逐片状态推导：最初“过几天/改天”令ambiguous=true；随后一片无模糊词且有明确日期，置false。最新一片含“过几天/改天”，即便同片也有明确日期仍置true；仅补时间、没有日期的片保持先前状态。故旧模糊日期→后天三点到四点可以解除旧阻断；旧“过几天三点到四点”→只补“后天”也可沿用原时间范围。旧明天→新改天仍拒绝；旧模糊→明确日期→最新模糊仍拒绝。以上是静态推导，不是本轮运行结果。

原事项与全部原话未删除，date_known/range_known仍检查combined，payload必要字段、ISO可解析、结束晚于开始、时区检查继续保留。最新时间只给“下午”且模型缺起止字段时payload仍拒绝；模型是否错误保留旧完整时间由实际Card/真实M3测试决定，不能因字符串range_known=true就称时间正确。

范围和过期refs：followup仍要求prior assistant waiting_user+有效metadata、当前project/owner、chat_reply_context_valid以及未retired的clarification_input，combined仍限2400字节。历史三处scope/ref/forget及success/error/cancelled筛选全部字节未改。引用检查仍核对id/account存在、revision、source_ids、冲突、gm_entry_access；后者拒绝resolved/deleted、账号撤销、用户不符、forget，以及valid_until不可解析或已到期。模型回包后captured_refs再次校验也未变。新日期helper无权限输入，也不授予新的action权限。

“明天→后天”：新增prompt明确后续日期/时间更正优先，旧日期作历史，保留未改事项和字段，方向正确。仍由真实模型提取ISO日期，validator未增加自然语言日期对比，因此实际start/end是否对应后天待Root M3验证；此次静态审核不能升级真实日期PASS。

同片“改天，具体后天三点到四点”按Root声明的“最新片含模糊仍拒绝”规则会继续询问；这是当前明确规则的保守行为，不列为未授权扩大范围的修改建议。独立entry validator仍拦截 malformed clarification fields，本次未扩大可接受范围。
