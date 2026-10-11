# NIGHT-004 native Calendar overlap

状态：Main 补丁提案已准备，纯 VM／离线回放 guard 49/49 PASS；真实接入后 full-chain 未运行。Root 接入、签名和串行执行；本聊天不改中央 Main/SDK/包，不启动 Kernel/GUI/Cargo。

固定基线 source `c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`，signed Main `cdb1412b14a25fdbb8f97681e7fe344c855a0adaac50c26ded5eb17f876108d7`。Root 的 `build/night-004/gpt01-overlap-same-r2/actual-owner-reproduction.json` 已证明同一时段的第一次候选操作将 owner count 1→2；原事件字段未变。原 parent report 的 FAIL/非法最终 JSON 保留，不改成 PASS，也不用重复创建来证明缺口。

## 最小 Main 提案

`native_preflight_main.patch` 只针对固定 c892 的 Main：history 回调、候选提交、query request ID 绑定、一个按钮文案及其 runtime preflight helper。原创建 add/get 校验和 Host 审批规则保持。无新权限 API、SDK/Gate/manifest 变更。`native_preflight_proposal.splash` 是 helper 原文；`prepare_proposal.py` 在本聊天 build 目录构造未应用 Main 与 diff。

最终 proposed source SHA `8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`，patch SHA `b34ac5c26e3d955dcc3358e66caa0323ed15cef2f099376967a6342e21be7ece`，194 行 unified diff。中央只读 `git apply --check` 已通过，尚未应用。

第一次候选操作只发起提示为精确 `calendar.events {"limit":200}` 的 query turn。当前 turn 必须只有一条真实 tool row；person lane、持久化 receipt、thread/turn/tool/call/session、result.call_id、persisted_at 和精确参数 digest 全部匹配。还绑定 History 顶层 session_id 与 context_state.session_id。open reply 没有 session_id，不从该回复杜撰字段。额外工具（包括 mutation）、坏记录、缺 receipt 或 ID 复用均 UNKNOWN。列表达到 200 条，无耗尽标志，UNKNOWN。其他时区、缺 end、无效区间也 UNKNOWN。

比较使用半开区间 `event_start < candidate_end && event_end > candidate_start`，覆盖跨界、候选包含原事件、候选被原事件包含；相邻不重叠。官方 from/to 是完整包含过滤，不能作为重叠查询。重叠是合法 Calendar 事件；Muse 展示当前快照与原标题/时间，等待本人修改时间或另一次明确保留重叠的候选操作。清晰和重叠均需第二次操作，UNKNOWN 不继续创建。

**实际边界：**提示词没有提供按 turn 的工具子集授权，当前声明仍有写工具。本提案只能检查真实 query 的实际记录；额外 mutation 记录使 preflight UNKNOWN、阻止第二次 native create，不能撤回 query 回合已经产生的副作用，也不能承诺模型违例绝无副作用。当前快照不是时段预约；查询和后续创建之间 owner 可变化。账号、本人、Goal/plan、候选内容或版本、后续 query 改变即失效；runtime 检查不持久化，重启须重新查询。原 Host 审批策略仍适用。

## 已执行验证

`run_vm_guard.py` 使用原 frozen CLI VM SHA `f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351`。三进程 exit 0、stderr 空、RPC 0、49 条断言全部 true，记录 `VM_GUARD_RESULT.json` 与本聊天 `build/gpt01-native-overlap-guard-r5/` 原始程序/输出。查询正例是未改写的真实 `{}` receipt，用来回放同一解析器；Main 所需 `{"limit":200}` 会拒绝这个不同 digest。未伪造通过的 Host receipt。异常 History 是明确篡改的负例副本；区间、scope 和 separate gesture 是 unit fixture，dispatch adapter 只计数，不执行动作。

包括 20 条 receipt/History 断言、13 条 interval/cap 断言、16 条实际 production binding/scope/gesture 断言。Scope gate 使用原函数而非假 `binding_current=true`。首次 query 路径、未结清查询不创建、第二次 gesture 消耗检查、UNKNOWN 阻止第二次创建、account/user/Goal/plan/candidate/time/后续 query/重启失效均通过。guard-r3 最初少传实际 `--rpc` 参数，程序输出裸 JSON，parent 判失败；原文件保留，修正参数后 r4/r5 通过。原 R1 reserved `ok` 语法失败及完整 definitions-only 的超时均保留；不计为通过。

## Root / GPT02 接入阶段

接入上述 patch 后，Root 以实际 source/Main SHA 重准备 probe 和既有签名 candidate。无需本单元新增 SDK、权限 API 或大构建。既有 L3 中的通用 query 不会自动成为候选 preflight。

将原单次 `calendar_agent_submit_candidate()` 改为以下三个明确阶段，并分别断言：

```text
calendar_agent_submit_candidate()
// query completed, binding nil, preflight ready/unknown; query实际onlyevents，owner不写
calendar_agent_history_settle = true
calendar_agent_history()
// query archived / state idle，same runtime check retained
calendar_agent_submit_candidate()
// 第二次候选操作；ready才沿原 add/get 精确回读创建，unknown不继续
```

query 与 create 必须是分开的 turn，保留原 create link_result 的 add/get-only contract。发生重叠时第二次操作是另一次明确选择保留当前候选；不把该动作称为不可绕过的服务禁重叠规则，也不保证 add 会出现 Host sheet。尚需 Root 的真实同槽/包含/相邻、变更时间／Goal、未知时区／缺 end 及 GPT02 正向 full-chain。

`prepare_root_case.py` 仅由 Root 使用：每例新目录、只克隆 fixture Main/Mail state 和实际 owner 字节，不复制旧 Kernel ledger。`--source-sha` / `--main-sha256` / `--kernel-config` 接收 Root 接入后已有公开配置。它不运行任何服务或构建，拒绝覆盖旧证据和符号链接。
