# Calendar clarification review — changes required

只读评审 root 未提交补丁；仅写 A3 所有目录。实际 r2 Card Host、现有 regression_run/runtime_probe、合成输入；无真实模型、Mail、Calendar 或系统权限动作。未运行 send_chat 完整回调链；不宣称 RC_READY/full-chain/全应用 PASS。

## Confirmed actionable finding [P1]

`chat_calendar_followup_message` 将旧输入与最新补充串接，`chat_calendar_input_clear` 和 `chat_candidate_input_error` 对串接全文检查 `过几天` / `改天`。复现：原话“请安排过几天会议”→等待补充→补充“后天下午三点到四点”。串接原话仍含“过几天”，即使输出五字段完整且时间明确，候选校验依旧返回“请明确哪一天，以及开始和结束时间。”。`改天` 同样失败。send_chat 源码随后依据相同 input_clear=false 再存 waiting_user。只读证明是状态分支推导；实际 fixture 直接执行上述生产 helper，未执行 send_chat 回调。

最小修改边界：这些补充合并/时间校验 helper 与其 send_chat 调用参数。保留原始会话文本、scope/ref/forget 和 2400 字节门限；把“原始事项上下文”与“本轮已明确的时间字段”区分，使后者能够替代旧模糊日期。root 决定并实施；A3 未修改产品。

## Guard evidence and limits

首次真实 Card fixture：43 个布尔检查，40 true、3 false；日志无 [E] 或 script budget 错误。有效 waiting_user 被保留，普通 success 保留；error/cancelled 与无 metadata 的 waiting_user 不进入历史。新增 metadata 缺字段、错误角色/state/action、nil/number/bool/array/object/空串、2401 字节与坏引用均被 entry validator 拒绝。旧无 metadata waiting_user 仍可加载，过滤不放入模型上下文。

跨 project/owner、deleted/resolved/missing memory、source_ids 变更、账号撤销、forget 原输入均阻止历史或补充合并；账号有效时可合并。合并恰好 2400 字节可通过，2401 字节返回当前消息。status、mail、无时间普通消息、cancelled 不合并。

第三个首次 false 是 ref_guard_12（fixture 内修改 revision）。未直接归为产品缺陷。单独诊断以独立 JSON 明确构造 document revision 2 / ref revision 1：context_guard=false、历史 turns=[]、补充合并被拒绝，revision_mismatch_denied=true。首次 mutation fixture 原因未定位，保留原样。诊断 runner 仍将 raw context_guard=false 当作失败断言，这是顶层报告形状错误；该摘要也保留，不把它改成全绿。

“请安排明天会议”→“改成后天下午三点到四点”两条原话确实保留，合并仍选择 calendar_candidate。muse_model_request 的最后 query 仍为本轮原话，原事项经 chat_model_history 进入历史；合并文本不直接注入 task/query。candidate_input_error 没有把模型 ISO 日期和最新日期逐项比较；本 fixture 只证实不存在确定性比较，**没有证明真实模型选错日期**。root 应保留真实 D05 日期覆盖验证；A3 未读取私有 raw D05。

chat_reply_is_context 本身可接受空 clarification_input，但持久化 validator 已拒绝空串，send_chat 的非空原话也不会生成空串；当前没有可达绕过证据，未列为独立阻断问题。

## Source binding

Readable `33d5d2ae8126e9d9431ab63db5d9dace22904287e76b3b87970fc580ffa4c2ed`；使用仓库现有 compact_bundle 做纯注释/空白压缩后的 payload `ed596500508ec0437ab2c943749e76ce68998a23d9c97cdd54bf03a188927d34`；Host `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。当前 root 工作文件是否仍同 snapshot 见 CLARIFICATION_REVIEW_SOURCE_BINDING.json。不把后续 root 源码视为本次已验证。

首次原始 probe/report/log：clarification-followup-review-r1/clarification_followup_review_r1/。独立 revision 诊断：clarification-revision-diagnostic-r1/clarification_revision_diagnostic_r1/。原始源副本、bundle、状态、日志只保留本机，不加入公共 staging whitelist。8510 已释放；未执行 Git 操作。

## Root followup: smallest necessary suggestion, no implementation

对 root 追加问题的直接回答：当前 SHA33d5d2 **不能**用后续明确日期覆盖最初过几天/改天，完整日期+起止时间补充也被拒绝。最小建议将两处整串 ambiguity 判断统一为同一条“有效时间信息”规则：最新补充若给出明确日期，让它覆盖旧模糊日期；起止时间若最新没有更改，可沿用原用户已明确提供的时间。最新仍模糊、或合并后仍缺日期/开始/结束，保持 waiting_user。完整 combined 与历史原话继续原样保存，只改提取/校验视角，不删除事项，也不丢弃 scope/ref/forget/boundary guards。特别注意只说“后天”可能需要沿用原来已明确的起止时间，不能要求每条补充独立重复全部字段。

“明天→后天”已证实合并保留两者、action仍calendar_candidate；没有实测模型择日结论。最小提示词建议明确：后续更正的日期/时间覆盖旧值，未更改事项和字段保留。现有确定性 validator只校验结构/时区/时间范围，不核对自然语言日期，应由root串行真实模型断言payload.start/end对应后天；失败不能升级为通过。无需改历史success/error/cancelled过滤规则。全部是建议，A3未改产品。
