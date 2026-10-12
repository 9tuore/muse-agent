# 最终候选模型与业务入口审查

业务补丁已在 `68a81b1b` 交付；本单元只读最新 SDK 与启动入口，并执行隔离的真实 Qwen HTTP tools 请求。没有 GUI、真实 Calendar 工具执行、SMTP、生产账号或 Secret 读写。

全新 profile 的 `config.llm.primary` 使用 `family_id:local`、Qwen alias 与 loopback OpenAI route，符合 Native registry 的无密钥 local 定义。现 SDK 中 `agent.model.needs=[tool_calling]` 与 tier 是声明和审查信息：`crates/app-peers/src/hosted.rs::launch` 没有为 BrokerConfig 设置 model_lane，默认 None；`broker.rs` 只有 Some 才给 peer/prepare 增加 model。实际 contained agent 沿用 `_main` 配置，不会因 Muse 声明 standard/tool_calling 自动变成云端模型。

真实 bundled Qwen 使用当前启动参数和 Calendar 六项官方工具 schema，在 21.765 秒后返回 `calendar_events` tool_call，证明基本结构化工具调用可行。原请求是“查询2026年10月13日的日程”，实际参数却是 `from=2026-10-01, to=2026-10-13, limit=10`，查询范围错误。该样本记为 **TOOL_CALL_SEMANTICS_FAIL**，不能用“有 tool_call”替代业务正确性。仅原始连接层报告的 TOOL_CALL_RETURNED 保留不改，新增 semantic-assessment 明确记录同一响应的语义失败；这不是第二次测试。

证据：`evidence/local-calendar-tools-default/` 中的 request、response、runner 日志与 report。实际 runner SHA `b4b04e4e…`、权重 SHA `7671c0c3…`、tools manifest SHA `bd2cfbce…`。没有执行返回的工具。Qwen 0.5B 可作为基础本地路径，该结果不足以支持全新 local profile 的日历准确性或强模型能力声明。

原 MiniMax 最短复用路径是沿用统一启动器并将 `MUSE_INTEGRATED_STATE` 指向已经授权的原 Muse Data，或包内 launcher.json 的既有 state_root；启动器从该目录复用原 `_main`，无需复制 profile 或任何 Secret。`workbuddy_launcher.sh` 将 shell、apps 和 kernel/.octos 统一置于同一个 state root，单实例锁仍适用。这样会沿用原应用数据，不能标成“全新隔离资料”验收。全新空白包和旧资料云模型验收应分别标识；不建议混接旧 kernel core 与新 shell，也没有将旧 profile 链接或复制进新目录。

如果全新资料要设置云模型，现支持路径是宿主 Native Models 本人设置，当前无人值守不得伪造授权。本单元没有验证旧凭据有效性，也没有发生真实 MiniMax 调用。连续发信现实现已允许 accepted/unknown 后归档旧回执并创建独立草稿；本次针对当前实现未发现新的全局 accepted 锁，真实连续 SMTP 仍由最终 GUI 验收记录。

本次源码依据：SDK `f9f6fea90b52182790cb2641fd0145c425af4d84` 的 `apps/ai-providers/config/src/registry.rs`、`.sources/app-hub/crates/app-contract/src/manifest.rs`、`crates/ai-host/src/contained.rs`、`crates/app-peers/src/hosted.rs` 与 `broker.rs`；Root `official_muse/integrated_release/muse_launcher.m`、`workbuddy_launcher.sh`。没有依赖旧聊天里的运行状态推定云模型通过。
