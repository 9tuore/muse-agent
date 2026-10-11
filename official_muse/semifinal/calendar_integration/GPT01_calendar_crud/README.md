# Calendar CRUD 最小增量

正式删除工具是 `calendar.remove_event`。源码已经有 owner-service 新建、更新、删除与精确回读；此候选补齐 Muse 的显式 Host ceiling、manifest 与终态回执识别。当前状态、未完成项和原工作配对边界见 [CURRENT_STATE.md](CURRENT_STATE.md)、[HANDOFF.md](HANDOFF.md)。

| 增量 | 应用根目录 | 内容 |
|---|---|---|
| GPT01-calendar-crud-sdk.patch | 原配对 SDK 根目录 | 两个工具的 Broker/history/调用映射及定向测试，精确读回指导 |
| GPT01-calendar-crud-hub.patch | 原配对 App Hub 根目录 | Muse 编译授权 ceiling 由四个工具扩至六个 |
| GPT01-calendar-crud-release.patch | Muse 工程根目录 | manifest 请求、AGENT 约束、候选说明和签名 fixture 预期 |

先用 `python3 verify_baseline.py` 检查生成时的三处来源文件。应用其他已确认的原工作源码环境前，要逐项核 BASELINE.json 的 before SHA。每份 patch 在相应根目录执行 `/usr/bin/patch -C -p1 -F 0 -i <该 patch 的绝对路径>`；所有匹配后才应用。不把项目包含目录 Git HEAD 当作 upstream SDK revision。

21 项 Rust fixture 已通过，命令和日志保存在 RESULT.json。真实 owner-service 使用随机新建的临时目录，退出删除这些合成数据；ServiceHost 注册/消息投递适配器直接 panic，测试不能触达生产 service。历史测试编译真实当前 Broker/Conversation，只有依赖模块映射和 strip-note 是明确 adapter。静态检查验证 manifest 与 Host ceiling 恰为六个日历工具，更新/删除仍为 destructive、Host 确认、禁止自动批准、schema 必须有 id/expected。

原工作 Host 源码构建来源、真实 Host 确认、签名 catalog fixture、官方 Agent/GUI full-chain、生产换包均未验证。工具结果中的 `removed:true` 与随后的精确不存在回读才支持本次成功删除；工具 `Done` 只说明该 RPC 的真实终态，不自行证明事件不存在或 GUI 投影已刷新。投影失败会有 `card_warning`，必须保留；不得把卡片出现当作 Calendar CRUD 证据。

新制 fixture 的 `prepare.py` 会拒绝覆盖已存在的自有 `build/gpt01-calendar-crud`，旧证据应保留；重跑应明确使用另一自有 stage，而不能删除本轮目录或共享 target。此脚本不会启动 Cargo 或修改共享源码。
