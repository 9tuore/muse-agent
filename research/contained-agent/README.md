# 官方 contained Agent 隔离入口

对应官方源码：OctoSense `3a4d1e1e` 的 `crates/ai-host/src/contained.rs`、`crates/app-peers/src/{contract,broker}.rs`。四个 `octos.*` 调用通过 `host.request`；start 只传 text/trigger，没有任意 session、account、profile 或 provider。官方共享工具目前只请求只读 `calendar.events`。

保留 `muse-goals`，没有自有 tools.json，绕开的是无需声明自有工具的产品范围，应用没有修改官方校验器。宿主仍需真实准入、每应用 Agent consent 和支持 tool_calling 的现有模型。

**状态：NOT_TESTED_NATIVE。** 文件属于隔离原型，没有加入活动根 `bundle/` 或正式 Chat。零真实模型工具调用结果。`agent_state=needs_verification` 明确区分回答与完成事实，未知请求禁止自动重跑。

该官方接口绑定单个 card.muse-goals/device 的合并历史；当前没有从 Splash 为每个 Muse 项目选择独立 Host context 的已验证路径。为保护个人/老师/账号资料归属，本原型只能使用独立合成环境。正式 Chat 继续使用现有按作用域检索的 model.complete。

夜间接续：先完成新版官方 Shell 固定依赖构建和应用准入，再用免费或预算已核清的配置验证真实模型选择 calendar.events。参考 VM 的合成协议测试不能代替这一步。需要本人原生 consent 时标 HUMAN_REQUIRED。

## 已执行的协议隔离验证（2026-10-10）

参考Splash VM15/15检查通过：请求前持久化、待处理去重、恢复UNKNOWN不重跑、旧回调拒绝、停止后拒绝晚到结果、只读history不解除保护、打开拒绝不发turn、不完整turn拒绝、模型说完成仍待核验、损坏日志保留并停止。真实jailed fs，传输/视图由fixture替换，fixture manifest移除Agent准入要求；无真实模型选择、官方工具执行或原生授权。不是完整进程重启证据，不计入原生Agent覆盖率。报告evidence/protocol.json，复现tests/run_protocol.py。此原型未进入活动根bundle。
