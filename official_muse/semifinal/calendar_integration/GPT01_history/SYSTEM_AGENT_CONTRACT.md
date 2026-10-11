# GPT01：持续系统代理的现有契约

2026-10-11，只读源码核对；未启动循环、模型、GUI 或外部动作。SDK HEAD `c52c9c0952905e40002bbbc6d4f64e138462484b`；Kernel 锁定 `b0759a57719fd35b3a2da1c5d969bc67538ed516`。这份材料是接入准备，不是运行验收。

源码根：

- **SDK**：`/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/runtime-closure-full-shell-r1/sdk`
- **Kernel**：`/Users/mima0000/.cargo/git/checkouts/octos-a74a59bdc2c07a30/b0759a5`

结论：没有查到 `system_agent/start|stop|enable` RPC。`system_agent` 是 Kernel 对 `peer/input` 启动的 App 回合的来源标记；持续调度复用正式 `loop/*`。以下请求发到现有 Kernel Host OUP 连接；不是 Splash `app.call` 接口。

| 产品动作 | 已有调用及来源 |
| --- | --- |
| 首次启用 | `loop/create`，`session_id` 必填；`profile_id`、`prompt`、`command`、`interval_seconds`、`mode` 可选。响应取真实 `loop_id`。Kernel `crates/octos-cli/src/api/ui_protocol_transport.rs:10187`、`:20945`；实现 `crates/octos-cli/src/autonomy/agent_orchestrator.rs:11347`。 |
| 暂停/恢复/移除 | `loop/pause`、`loop/resume`、`loop/delete`；参数 `loop_id` 必填，建议始终带原 `session_id` 和 `profile_id`。暂停阻止后续 fire，不会停止已运行回合；移除还会清理该循环创建的 cron jobs。Kernel transport `:20978`；orchestrator `:11453`。 |
| 状态 | `loop/list {session_id,profile_id}` → `loops[]`，含 `status`、`mode`、`next_run_at_ms`、`last_run_at_ms`、`expires_at_ms`。`loop/updated`、`loop/fired` 为事件；`fire.queued=true` 只证明入队。Kernel core `crates/octos-core/src/ui_protocol.rs:6195`、`:6215`、`:6252`；orchestrator `:11432`。 |
| 单次立即触发 | `loop/fire_now {loop_id,session_id,profile_id}`。创建只安排未来首次运行，不会立即调用模型。Kernel orchestrator `:11380`、`:11566`。 |
| 当前回合 | `turn/state/get {session_id,turn_id}`；停止已确认归属的回合用 `turn/interrupt`，不要由“暂停循环”直接停止系统会话里任意人的当前回合。Kernel core `:3282`；SDK `crates/shell/src/system_chat/session.rs:436`。 |

最小调用准备（JSON 占位符必须替换为前一步的真实返回值；本次未执行）：

```json
{"jsonrpc":"2.0","id":1,"method":"session/open","params":{"session_id":"_main:api:octosense#system","profile_id":"_main"}}
{"jsonrpc":"2.0","id":2,"method":"loop/list","params":{"session_id":"_main:api:octosense#system","profile_id":"_main"}}
{"jsonrpc":"2.0","id":3,"method":"loop/create","params":{"session_id":"_main:api:octosense#system","profile_id":"_main","mode":"fixed_interval","interval_seconds":900,"prompt":"查看已授权目标的状态；没有可推进工作就结束本回合。需要人员决定时报告；外部动作沿用现有批准。"}}
{"jsonrpc":"2.0","id":4,"method":"loop/pause","params":{"loop_id":"<create返回的loop_id>","session_id":"_main:api:octosense#system","profile_id":"_main"}}
{"jsonrpc":"2.0","id":5,"method":"loop/resume","params":{"loop_id":"<已有loop_id>","session_id":"_main:api:octosense#system","profile_id":"_main"}}
```

启用先 `list` 查原循环，重连后恢复同一记录，避免每次打开 UI 都创建一个。系统会话常量来自 SDK `crates/shell/src/system_chat/session.rs:45`。若客户端显式协商特性，需要同时声明 `coding.autonomy.v1`、`coding.loop_runtime.v1`；`loop_runtime=unavailable` 就停在不可用状态，不做本地计时替代。Kernel core `:199`；transport `:2614`、`:12225`。

**周期与恢复。** `fixed_interval` 范围 60–86400 秒；`self_paced` 使用模型返回 `<<loop-next-in: …>>`，缺失时 900 秒；`maintenance` 会在触发时解析维护提示。记录最多存续 7 天、最多 10000 次 fire，并非无限代理。Kernel orchestrator `:96`、`:10565`、`:21048`。持久化依赖 supervisor store 配置成功：无 store 时 `persist_loop_state_with_store` 直接返回，不能宣称重启恢复（`:19842`）。启动配置和恢复在 Kernel `crates/octos-cli/src/commands/serve.rs:954`、orchestrator `:19437`；`--solo` 默认将旧 active loops 暂停（serve `:961`），需以真实 `list` 结果为准，不绕过。serve 自带 5 秒后台 drain 与连接内 2 秒调度，stdio 也启用；复用它，无需新增无限轮询（transport `:27725`、`:7395`；serve `:1957`）。

**Host 存活是待接入边界。** SDK `crates/kernel/src/lib.rs:569`：私有 Kernel 的最后一个连接释放即停止。System Chat `Command::Close` 会在无当前回合时释放连接（`crates/shell/src/system_chat/session.rs:391`）。中央若启用持续模式，需让现有 Driver/Host consumer 在启用期间保持连接与工具注册，并将关窗和停止持续任务分开；仅创建 loop 不能保证关窗后继续。恢复连同同一 session 的 `session/open`、`session/hydrate` 和 `peer/tools/register` 已有于 session driver `:10`、`:25`、`:498`、`:686`；重连不会把中断旧回合当成完成（`:519`）。

**模型 profile。** `loop/create` 没有 `model/provider` 字段；循环绑定 `session_id + profile_id`，继承 Kernel profile。SDK 已有 `llm.providers`、`llm.set_model {id,model}`、`llm.set_primary {id}`、`llm.move {id,to}`（`apps/ai-providers/host-service/src/lib.rs:9`、`:1135`），属于获 `llm` 权限的系统 app 服务，不是 OUP RPC。provider 保存会重启 Kernel（`:287`）。Profile 正式结构 `config.llm.primary/fallbacks` 在 `apps/ai-providers/config/src/profile.rs:62`、`:100`；已有 Qwen/MiniMax family 目录在 `apps/ai-providers/config/src/registry.rs:73`。保留已有 Qwen 与云 MiniMax；当前没有核对用户真实 profile，也未证明本地 Qwen endpoint 已被这个 Kernel 选中。无 per-loop 模型固定接口，不应把开发 GPT profile 作为产品 profile，或把自动 fallback 当作已授权费用。

**person lane 隔离。** App peer 自有会话中，只有真正 `peer/input` 的 turn 可标为 `system_agent`；`share_history` request context 是 person lane，拒绝该标记（Kernel transport `:28499`、`:28563`、`:28637`）。脚本传 `trigger:system_agent` 无法冒充（SDK `crates/app-peers/src/contract.rs:128`）；普通 App 定时任务用 `schedule/background` 会被标为 App。现有 `app_chat::stop()` 仅停 person；`stop_system_agent()` 仅停当前 App 的系统代理 lane（`crates/shell/src/app_chat/mod.rs:410`、`:424`）。两者均不暂停 Kernel loop。系统会话内的人类对话和 loop 回合也不能被假称为两个独立执行 lane；中央须只中断已确认归属的 turn。

中央最小接入范围：在现有 Host/System Chat driver 上增加 loop 启停/状态控制、启用时保持连接、重连查同一 loop、按真实 turn/工具终态显示结果；真实周期、关窗恢复、Qwen/MiniMax profile 和费用策略尚待中央集成验证。
