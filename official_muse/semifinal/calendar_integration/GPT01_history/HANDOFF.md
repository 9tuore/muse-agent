# GPT01 Calendar History 交付

独立worktree：/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松；基线e962e4183d844002a22e4f8c91268dfb5b004b19，分支codex/gpt01-calendar-history。中央SDK只读；未用模型/GUI/日历/Secret，没有第二个完整Host构建。

`GPT01-calendar-history.patch` 应用cwd为中央 `build/runtime-closure-full-shell-r1/sdk`，先 `/usr/bin/patch -C -p1 -F 0 -i <absolute patch>`。逐文件before/after SHA、patch SHA见RESULT.json；r2副本零fuzz应用/字节匹配通过。只有9个SDK目标文件：Broker/新Calendar辅助、lib挂载；AppChat模型/辅助/测试/挂载；ToolStatus与既有渲染match。不改工具、Gate、身份、审批、Kernel、主源或bundle。

合法ContextOp::History保持；Broker复用existing InFlight/Occurrence及512上限，在真实结果回调缓存四工具的transport call_id、tool_call_id、真实终态与结果，按session/turn/tool_call_id/name绑定Kernel tool正文。receipt generation不对外输出；换账号后旧receipt不回读。收据响应最多32项/单项16KiB；大结果只报omitted，不截断成功。取消只在实际ToolReply.cancel成功后记cancelled，不伪造结果，保留原取消后的重试行为。

前端字段见上一级GPT01_HISTORY_CONTRACT.md。新host_calendar_receipts及row.host_calendar_receipt明确来自Host，不冒称Kernel已有；只有role=tool实存行绑定后kernel_persisted:true。Shell Ask显示正文、两类调用ID和终态；只有Host成功却缺Kernel行、缺收据、超限均Unverified；错误/取消Failed。非四工具的历史行为保持。

实际定向验证：独立broker-only Cargo harness使用当前SDK实际锁定serde_json1.0.151/tokio1.53.1/uuid1.26.1/log0.4.34；真实patched broker、SystemChat/AppChat两个model完成类型编译，15项History测试PASS（test.log）。测试擦除的仅是无关Host UI plumbing；没有Kernel/provider/GUI/live，不能代替完整Shell编译。独立target build/gpt01-calendar-history/target，观测约152MiB；原E0004失败源副本保留，r1修复后通过。r2仅将已经测试的同一display_tests挂到SDK cfg(test)，无运行时代码变化。

中央过滤器：`-p octosense-app-peers --features broker --lib calendar_history`；完整Host feature集下 `-p octosense-shell --lib app_chat::history_receipt_tests`。中央应用后复用release依赖编译，不必另建大型target。

未完成：中央完整Shell+实际Kernel同候选联通/合法Muse首轮真实工具与UI回读；重启进程后原occurrence缓存消失，Kernel正文仍在但transport id/Host终态显示Unverified。没有新持久化收据系统，没有用私人存储/日志补字段。没有宣称本人或CRUD整链成功。
