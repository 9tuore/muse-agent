# UI 与全局记忆集成边界

基线：0.2.26，dd473352a802fa44b3ff62b668c551cc6db587e2。隔离分支 `codex/muse-ui-global-memory`。本地输入和真实账号副本仅在忽略的 build 目录，禁止导出。

## 文件所有权

- 总控：`app/bundle/main.splash`、版本与本地集成、聊天异步归属、页面布局、最终回归及交接。只有总控写主界面。
- 记忆执行：新建 `global_memory.splash`、`GLOBAL_MEMORY_CONTRACT.md`、`ui_memory/tests/memory*`。不得改主界面或 native 核心。
- 页面执行：新建 `ui_page_adapters.splash`、`UI_PAGE_CONTRACT.md`、`ui_memory/tests/page*`。纯显示适配，不改宿主或主界面。
- 验证执行：`ui_memory/tests/visual*`、`ui_memory/tests/regression*`、`evidence/ui-memory/`。隔离窗口与合成数据；不操作现用 8401。

协作已按用户最新要求切换为三个真实 Codex 聊天；原子智能体已中断，未参与写入。三个真实聊天分别为全局记忆 `01a0fd85-2562-72e3-a09e-78a6731aff72`、页面适配 `01a0fd85-69e5-7dc3-ad5e-cdacb7c431df`、独立验收 `01a0fd85-b70b-7ac0-a882-2f333a015b48`。没有新建第二个主界面写入者。

## 集成接口

记忆扩展以当前 `memory.json` 和 `core_commit_memory` 为唯一权威存储，继续 `muse.dsl/1`，保留旧字段并增量扩展。禁止另建同内容的第二事实库。启动 hook `gm_boot()`；当前授权账号输入 `gm_set_accounts(ids)`（local 恒为本机用户资料，其他账号必须明确授权）。每轮 `gm_context(query, conversation_id, goal_id)` 返回 `{text, hits, bytes, truncated, conflicts}`，文本有来源、置信与作用域且严格限额。用户记忆写入、修正、遗忘和冲突处理接口由执行者在合同中精确列出；调用实际核心持久化及独立读回。所有项目/归属标记都保留，检索绝不把记忆当授权。

页面适配只读取实际 `calendar_events`；月/周/日程切换和日期导航不写系统日历。公开 `calendar_display_rows(events, view, cursor)` 等已实际定义的接口，在合同中记录参数与返回形状。查询、创建、修改、删除继续原能力和确认链。OS 通知、长期后台能力先核对宿主现实，缺少时明示限制，不伪造。

异步聊天按请求 id、原会话 id、原消息绑定；切换会话不改变归属。取消的返回不得写入聊天、全局记忆或触发动作。计划和回复调用前均做限额记忆检索。

根启动会等待 `gm_boot_pending` 分批校验结束后再恢复 Goal/日历；新模型请求逐次通过 `mail.accounts` 更新账号授权集合，失败仅用 local。`gm_retired_text` 同时过滤 recent/earlier 的更正历史与遗忘原话。侧栏状态保存到 `ui-layout.json` 并读回。确认删除会话会净化主文件和备份，单独保存的全局记忆仍保留。

持续任务卡复用原 `mail-watch.json` 和原30秒定时器，不另建调度。其状态不会被普通 Goal 的一次执行完成覆盖；关闭 Muse 后停止。通知复用官方 `glance.publish`，只代表 OctoSense Shell 通知卡，不宣称 macOS 通知中心。日历月/周/日程均投影真实 `calendar.list` 结果，CRUD与独立 `calendar.get` 保持原链。

设置里的记忆暂停阻止 `gm_save` 与 Prompt 检索；既有任务来源、核验记录仍保留。严格导入限同 profile、已授权账号与规范导出格式，暂不支持大库自动分片导入。功能与限制详见两个模块合同。

## 验证口径

fixture、真实模型、本机系统动作与最终候选回归分开报告。旧稳定版证据不作为新候选 PASS。最终真实外发/系统写入需要精确内容确认，其他开发不中断。真实截图来自正确渲染的可见窗口。原安装版与生产数据不改；不公开、不 push。
