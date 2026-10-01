# Muse Architecture

本文件把目标分层映射到当前代码。下图中的组件不是全部完成；状态以 [CURRENT_STATE.md](CURRENT_STATE.md) 为准。

```text
Muse Desktop (app/desktop_app.m, AppKit; scripts/build_desktop_app.sh)
  ↓ 受保护 JSONL / 本机 worker
Muse Runtime (app/agent_app.py, app/desktop_worker.py)
  ├─ Event Bus: muse_events.py, worker inbox/watcher, qqmail_imap_bridge.py
  ├─ Context Collector: muse_activity.py, muse_events.py, memory_store.py（有限范围）
  ├─ Attention Layer: agent_app.py 路由、muse_brief.py（部分主动性）
  ├─ Goal Engine: muse_goals.py, muse_goal_store.py
  ├─ Muse DSL: muse_dsl.py, muse_*_schema.json, muse_capability_catalog.py
  ├─ Memory: memory_store.py, muse_memory_graph.py
  ├─ Model Router: muse_models.py, muse_provider_protocols.py, muse_model_costs.py
  ├─ Policy Engine: muse_action_bus.py, muse_capabilities.py, muse_search_policy.py
  ├─ Capability Runtime: muse_capabilities.py, muse_textedit_recipe.py,
  │                     muse_browser_recipe.py, muse_calendar.py
  ├─ Plugin Runtime: muse_plugins.py, muse_plugin_sdk.py
  └─ OctoSense Adapter: muse_official_bridge.py, muse_official_session.py,
                       official_event_adapter.py（未形成官方完整链）
```

原生 AppKit 层显示统一聊天、技能/结果卡、Goal、Memory、活动和设置，发受保护事件给 worker；UI 自身不应直接做危险系统动作。`desktop_worker.py` 独占工作区，推进定时 Goal、消费本地事件和用户决策。`agent_app.py` 是事件分发与服务集成入口。持久数据位于用户的 `~/Library/Application Support/GOSIM Local Agent/workspace/`，包括 SQLite、事件与有限状态；模型文件在同一应用支持目录的 `models/`，不在 Git。旧 `HANDOFF.md`、`STATUS.md` 和 `docs/MUSE_5A_ACCEPTANCE_20260928.md` 是历史证据，不应代替动态状态文件。

## 模型与 DSL

本地模型路径为 Qwen3-0.6B，经应用管理或复用的 loopback llama 服务提供推理。`ModelGateway` 管理 local/high/mixed 路由、Provider 配置、Primary / Backup、请求预览、Keychain 引用、模型特定的 reasoning effort、用量和预算。`muse_provider_protocols.py` 有 OpenAI Responses 与 DeepSeek Chat Completions 的请求/回包适配；当前它们主要有 fixture 证据，不能据此声称真实远端调用成功。所谓 Provider Proxy 目前主要是进程内网关，不是独立的透明代理服务。Backup 有同源和协议边界，不是任意跨厂商无感切换。

`muse.dsl/1` 统一包装 Goal、Memory、Capability 文档。Goal DSL 由 `muse_goals.py` 语义校验、`muse_goal_store.py` 保存修订/审批/运行；Memory DSL 由 `muse_memory_graph.py` 记录 source、claim、scope、关系及修订；Capability DSL 由 `muse_capability_catalog.py` 登记、批准与撤销。原始来源 → 有界抽取 → Fact/Inference → Entity/Relation → 检索 → 当前任务上下文，这条链在选定来源和本机数据上部分可用，尚不是整机自动知识图谱。

## 能力与接入

| 能力 | 当前代码入口 | 边界 |
| --- | --- | --- |
| Files / System | `muse_capabilities.py`, `g01_capabilities.py` | 受限工作区写入与回读、进程/设备只读状态；不等于全盘权限 |
| Terminal | `agent_app.py` 的既有受限命令路径 | 固定动作及确认，无无限 shell |
| Browser | `muse_browser.py`, `muse_browser_recipe.py`, `muse_web_search.py` | 隔离 Edge/CDP 和公开网页，域名/计划限制 |
| Mail / Messaging | `qqmail_imap_bridge.py`, `muse_events.py`, `agent_app.py` | QQ IMAP/SMTP 与本机结果卡；微信/robrix2 消息未接成同等 live 路径 |
| Calendar | `muse_calendar.py`, `muse_calendar_helper.m` | EventKit 实现受当前 `WRITE_ONLY` 权限限制 |
| App UI / Accessibility | `muse_ax_adapter.py`, `muse_ax_helper.m`, `muse_app_learning.py`, TextEdit/Browser recipe | 有限目标和配方，不是通用操控 |
| Notifications | `desktop_app.m` | macOS 结果通知及应用内卡片；展示不等于动作成功 |

App Learning 的实际链为观察 UI Tree → 映射唯一控件 → 提出带摘要的 Capability/recipe → 授权范围内试运行 → 读回验证 → 持久化映射。`RecipeStore` 有通用框架，但本机实测主要集中于 TextEdit 与 Edge，不能外推到任意软件。插件 SDK 只允许已审查的声明式清单与受限委托；未知第三方代码不能因为存在 manifest 就执行。

OctoSense/Octos/AppCard 和 robrix2 由独立适配层处理。`muse_official_bridge.py` 可表达待决请求与本机收据，`muse_official_session.py` 校验会话字段；`official_event_adapter.py` 仍标记 prototype/deferred。官方真实会话与局部审批请求已有历史证据，但与同一个 Muse Goal 的可信人工确认、动作回读、官方结果回传尚未闭合。

## 架构硬规则

1. UI 不直接执行危险系统动作；模型不获得无限 shell。
2. 实际动作经 Capability Runtime，重要操作经 Policy 和用户确认；完成状态以真实 Verify 为准。
3. mock、fixture、编译、窗口或卡片出现都不等于真实端到端通过。
4. Memory 不等于原文件全文；Secret 不进入 Memory、DSL、日志、Git 或插件。
5. OctoSense Adapter 与 Muse Core 解耦；新 Provider 或新 App 不应迫使核心 Runtime 重写。
6. 外部应用操作优先级：API > UI Tree / Accessibility > 受限 Terminal > Vision。
