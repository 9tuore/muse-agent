# GPT01 前端接口速递（补丁类型检查与定向测试通过，未live）

沿用真实 `octos.session.open {}` → `octos.turn.start {text,trigger:"app"}` → `octos.session.history {}`。不增加工具调用接口，不把 person 字符串当本人批准。

固定Kernel现有返回：`messages[]` 行的 `role/content/tool_name/tool_call_id/turn_id?/thread_id?/persisted_at`；Broker共享History再加`lane`。没有transport call_id、没有明确工具终态。`calendar_events/calendar_get_event/calendar_add_event/calendar_notify`是固定Kernel的精确模型别名；Relay名称仍dotted。

补丁拟在同一合法History响应增加 `host_calendar_receipts[]`，来源仅Broker真实ToolReply终态和原occurrence缓存：

```
{source:"broker_tool_result", caller:"card.muse-goals", owner:"os.calendar",
 tool:"calendar.events", session_id:"实际session", context_id:"实际context或null",
 turn_id:"实际turn", tool_call_id:"模型调用id", call_id:"ptc传输id",
 args_digest:"实际digest", terminal:"ok"|"error"|"cancelled",
 result:{ok:true,data:实际结果}|{ok:false,error:{kind:实际kind,message:实际message}}}
```

以上是新定义的host字段，不冒称Kernel原生已有。只覆盖合法Muse→Calendar四工具；不增加update/remove/身份/审批/权限。每个结果上限16KiB，超过上限只给result_bytes/result_omitted:true，不能截断充成功正文。最多返回32个真实终态收据，账号generation变化后旧收据不送出。

若Kernel真实role=tool行的session（由本次hydrate请求确定）、turn、tool_call_id和精确四工具名都与host收据一致，行会额外有 `host_calendar_receipt`，并标记 `kernel_persisted:true`。正文仍是该Kernel真实row.content。前端完成判定需要本次完成turn的这条匹配行、terminal=ok、结果完整；不能单看assistant回复或Host收到请求。仅host receipt而暂无对应Kernel行：显示“Host已返回，History待回读”，不能称Kernel已持久化或业务成功。error完整保留实际拒绝/权限原因。

收到/awaiting_confirmation不是terminal，不能生成ok收据。取消收据仅在真实ToolReply.cancel成功时保留terminal:cancelled，不包含虚构result；保留已有真实tool_end/turn_terminal的失败状态，缺终态显示未核验。未知字段/不一致turn或双turn/thread冲突/缺tool_call_id/陌生alias均证据不足，不重试。

收据是现有Broker进程缓存上的补充，未新增持久化存储。进程重启/缓存淘汰后仍能读Kernel工具正文，但transport call_id和host终态可能缺失，须显示未核验；不能伪造或从私人日志补齐。
