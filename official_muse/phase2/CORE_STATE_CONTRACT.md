# Phase 2 Goals / Runs / Memory / Activity 状态契约

此契约供 `main.splash` 集成。实现为 [core_logic.splash](core_logic.splash)，正式 bundle 仍只有一个入口文件，因此 G-01 应将其函数内联到 `main.splash` 的根 Widget 之前，删除同名旧状态与 `record_event/save_task`。G-02 不修改正式入口。

## 启动与存储

- 依次调用 `core_boot_goals()`、`core_boot_activity()`、`core_boot_memory()`，完成后再渲染。任一返回 `false` 时展示 `core_error`，禁用相应写入动作。`core_storage_ready/core_activity_ready/core_memory_ready` 是独立写入门禁；不可把损坏记录当空状态继续覆盖。旧 Activity 条目缺少 `kind/detail/at` 时拒读并保护原文件。
- `goals.json`：`{schema:2,goals:[...],runs:[...],actions:[...],selected_id}`。旧 `current.json` 首次仅复制到一个 Goal；若其已有批准且处于 running/completed/failed，为恢复路径生成同 ID 的 `legacy:<goal_id>` Run。原文件、`results/` 与 `chat.json` 不改。迁移写失败时 `core_storage_ready=false`、保留旧 Goal 供只读展示，不能继续创建。
- `goals.backup.json`、`memory.backup.json`、`activity.backup.json` 保存上一个成功回读的快照。每次先写备份，再写主记录并回读相等才更新内存；主记录损坏或格式不完整时经校验从备份读取，不自动重写坏主记录。Splash `fs` 无 rename 或跨文件事务，突然断电时可能需要人工用备份对账。任何失败显示 `core_error`，不得把 UI 乐观状态当持久状态。
- 单文件 1 MiB、应用空间 16 MiB 的锁定宿主限制下，应用限制 Goals 32、Runs 128、Actions 128、Activity 200、Memory claims 64、sources 128、forget tombstones 256；单次记录达到上限返回 `false`，不静默删历史。容量未来需分片扩展。

## 状态与函数

全局 `goals=[]`、`runs=[]`、`actions=[]`、`selected_id=""`、`task=nil`、`activity=[]`、`memory=[]`、`memory_sources=[]`、`memory_forget=[]`、`core_error=""`。`task` 只是选中 Goal 的 UI 镜像；异步回调不能以 `task` 确定归属。`core_*` 函数均不直接渲染 UI，也不调用 Mail/Calendar。

| 函数 | 用途与返回 |
| --- | --- |
| `core_add_goal(new_task)` | 创建唯一 Goal，沿用原 `task` 字段（`id/version/goal/status/result_path/goal_spec/...`），返回 bool；成功后选中。 |
| `core_select_goal(id)` | 持久化选择，更新 `task` 镜像，返回 bool。 |
| `core_upsert_goal(updated_task)` | 保存现有 Goal 的 UI/计划字段；先用 `task.to_json().parse_json()` 拷贝，再改字段，避免失败时污染镜像。 |
| `core_archive_goal(id)`、`core_cancel_goal(id)` | 运行中不能归档/取消；取消不删除已有结果。 |
| `core_replan_goal(goal_id,next_task)` | 同一 Goal 后续 Run：要求新 task `id` 不变、`version=旧+1`、`status="planned"`、使用新结果路径；原 Run/结果保留，批准时间清零。 |
| `core_update_model_summary(goal_id,plan_revision,summary)` | 模型异步返回时按捕获的 Goal ID 和版本写建议；旧版或非 planned 拒绝。 |
| `core_start_run(goal_id,plan_revision,request_id)` | **UI 完成输入/GoalSpec/宿主授权核对且用户明确批准后**调用；持久化 `running` 与独立 `run_id`，失败返回 nil。此函数不替 UI 获取批准。 |
| `core_finish_run(goal_id,run_id,status,result_path)` | 仅允许原 Goal/Run/版本；completed 还须从应用存储读取该路径且 `task_id` 一致。调用者仍需核对写入字节和业务内容。 |
| `core_begin_action(goal_id,run_id,plan_revision,service,action_scope,request_id,payload_json)` | 外部动作调用宿主前持久化 `in_flight` 和用户确认过的完整 payload。独立邮箱动作用 `"","",0`；联动用真实 Goal/Run/版本。唯一 request ID，重复调用返回 false。 |
| `core_finish_action(request_id,status)` | status 为 `accepted/verified/failed/unknown`。`accepted` 仅是服务受理，独立读回后才可标 `verified`。崩溃后 `in_flight` 在启动时转 `unknown`，不得自动重试。 |
| `core_record_event(kind,detail,goal_id,run_id,request_id,account_scope)` | 真实事件发生后记录 Activity；失败返回 false。`core_boot_activity()` 将旧版 `task_id` 条目在内存中规范化为 `goal_id` 与空 Run/request/account 字段，避免新页面读取缺失属性；首次新事件连旧历史一起安全写入。 |

例：`model.complete` 发送前捕获 `goal_id` 和 `plan_revision`，回调 `core_update_model_summary(captured_id,captured_revision,summary)`；即使用户期间选了别的 Goal，也只改原 Goal。受限 Goal 执行前捕获 `run_id`，结果先写入和独立回读，再调用 `core_finish_run(captured_goal,captured_run,"completed",path)`。`core_record_event` 只在真实调用/核验之后写，计划本身不能记成功。

## Memory

`memory.json` 为 `{schema:1,claims:[{document,pinned,source_history}],sources:[...],forget:[...]}`。`document` 采用现有 `muse.dsl/1` 的 `kind:"memory"` envelope 和 `muse.memory` payload 字段；`source_history` 保存更正前后的全部来源 ID，删除时为同一 account/subject/predicate 的每个来源建墓碑。删除的 `document.payload.value/source_ids/relations` 清空，列表不再返回。官方应用只处理自己经授权获得的来源，不读独立版生产 SQLite 或钥匙串。

| 函数 | 用途 |
| --- | --- |
| `core_memory_scope(account_scope)` | `{project:"muse-goals",account,visibility:"personal"}`。 |
| `core_utc_iso(time_now())` | 生成 UTC ISO 日期时间，供 DSL 时间字段使用。 |
| `core_add_source(source)` | 登记真实来源；要求 source ID 稳定、scope 与 account 明确。Mail/Calendar/结果映射为 `kind:"runtime_receipt"`，其 `locator` 应包含宿主稳定 ID，不用显示名代替。 |
| `core_add_claim(document)` | 加入 source 已登记且同账号的初始 `muse.dsl/1` 记忆；删除墓碑拦截旧来源回流。 |
| `core_find_memory(query,account_scope,goal_id)` | 在账号和可选 Goal 范围内检索，返回非删除条目；当前为区分大小写的子串匹配。 |
| `core_correct_memory(id,value,account_scope)` | 新 revision、用户更正来源、`user_statement`；保留旧 source ID 供以后遗忘。 |
| `core_pin_memory(id,pinned,account_scope)` | 持久化固定状态。 |
| `core_delete_memory(id,account_scope)` | 仅留被擦除的 DSL 墓碑和防回流来源键；不恢复原值。 |

Splash 的 `scope` 是保留字：对象字面量不能写 `scope: ...`，读取也必须用 `obj["scope"]`。先构造不含 scope 的对象，再执行 `obj["scope"] = core_memory_scope(account)`。来源记录要求 `source_id/kind/locator/content_sha256/observed_at/updated_at/support_excerpt/scope`；`content_sha256` 缺少可验证的宿主摘要时只能为 nil，**不得编造**。这和独立版 `MemoryGraph.put_source()` 要求 SHA-256 的来源表尚不完全兼容；Memory DSL document 与更正/墓碑语义可用，旧版来源图的完整导入仍属缺口。支持片段是来源数据，不得执行其中指令。

## 已跑验证与边界

`python3 official_muse/phase2/test_core_logic.py --port 8262` 在现有官方 `card-host` 的隔离 app jail 四次启动 PASS。验证 0.1.10 `current.json` 形状的合成 running 副本及已保存结果迁移为可回读的 legacy Run、旧 Activity 条目兼容、三 Goal、切换期间原 Goal 的 Run/模型回写、后续 Run、旧版本/双完成/重复发信 request 拒绝、Memory 来源/检索/更正/固定/删除/跨账号/防回流、重启原结果保留与外部动作 `unknown`。第三次用坏 `goals.json`、缺少 detail 的旧 Activity 条目和不支持的 Memory 版本验证拒读、拒写及原文件逐字节保留；第四次验证坏主记录能从有效备份恢复且不自动重写主记录。最终 JSON 在忽略目录 `official_muse/phase2/.local-state/core-contract-test/result.json`；Python 还用原独立版 `muse_dsl.validate_document` 检查删除后的 envelope。

证据性质为 **LOCAL/FIXTURE**，未调用真实 `model.complete`、Mail、Calendar，未验证正式三栏 main 的集成或 Shell 重启。由 G-00 对最终候选版本独立做这些验收。缺少原子 rename，邮件或日历调用实际发生而本地写回失败时必须先查询外部状态对账，不可把 `unknown` 当失败后重做。
