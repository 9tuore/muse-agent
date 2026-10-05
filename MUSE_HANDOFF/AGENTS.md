# Muse 接手规则

从仓库根目录的 `AGENTS.md` 可直接进入本文件。先读 [README.md](README.md) 和 [CURRENT_STATE.md](CURRENT_STATE.md)，再核对现场 `git branch`、`HEAD`、`git status`。需要理解接口时再读 [ARCHITECTURE.md](ARCHITECTURE.md)；不用读完整聊天或等待用户填写任务表。

**默认直接开工：**在没有更具体的新请求时，从 `CURRENT_STATE.md` 的优先级中自行挑一个影响最大的**非核心**问题，检查相关文件，实现、测试、记录结果并本地提交。项目内的非核心源码、UI、连接器、插件、构建/安装脚本、测试和文档均可按需要修改；不要求先列允许文件清单。用户的新指令始终优先。

**核心保护区：**未经用户明确要求，不改 `app/agent_app.py`、`app/desktop_worker.py`、`app/muse_events.py`、`app/muse_dsl.py`、`app/muse_goals.py`、`app/muse_goal_store.py`、`app/muse_action_bus.py`、`app/muse_capabilities.py`、`app/muse_capability_catalog.py`、`app/muse_models.py`、`app/muse_model_costs.py`、`app/memory_store.py`、`app/muse_memory_graph.py`、`app/muse_keychain.py`、`app/muse_goal_schema.json`、`app/muse_memory_schema.json`、`app/muse_capability_schema.json`，也不直接改生产 SQLite 或用户资料。若选中的问题必须修改这些位置，先完成只读定位和可复现证据，说明需要修改的最小边界，再请用户决定。

改动应沿用现有结构。测试必须区分 fixture、本机 live 与官方 full-chain；不要把编译、窗口或卡片出现当作动作成功。涉及真实联系人、系统权限、密钥、费用或公开发布，沿用用户已有授权；没有授权时只推进其他分支，不猜测、不绕过。不要寻找或输出 Secret，也不要把 Secret 写入日志、Memory、DSL 或 Git。保留旧证据和未提交改动。

**GitHub 当前指令（用户2026-10-05晚间）：**继续本地开发和测试，暂停推送或公开最新版。按本人明确要求，远端 `9tuore/muse-agent/main` 已从 `bce33551` 恢复到本轮同步前的 `39e2b20d`（0.3.26-rc27），API读回一致；本地rc35及其提交保留。此指令覆盖此前“每次更新自动推送”。不要把旧远端合并成产品回滚，不修改旧Tag或正式提交App Hub。后续重新公开须有本人新指令。

做完后更新 [CURRENT_STATE.md](CURRENT_STATE.md)，用 [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) 写简短交接，注明测试和未完成项，再做本地 commit。路径未标绝对位置时，相对仓库根目录。
