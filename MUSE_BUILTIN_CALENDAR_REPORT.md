# Muse 内置 Calendar 接通研究与验收

2026-10-10，分支 `codex/muse-pivot-20261010`。**正式 Muse 工具链仍 BLOCKED；内置 Calendar 原版及隔离补丁的组件/UI验证通过。**

## 正式架构

目标是 OctoSense 内置 `os.calendar`，读写其自身的 `.host/calendar/events.json`，不是 macOS EventKit、device_calendar 或 Google。未替换旧稳定 Host、活动 rc17 Bundle，也未读取或改写生产日历。Muse 的 ID 保持 `muse-goals`。

正式接通需要同时成立：商店签名/目录准入、宿主工具 offer、本人 Agent 同意、Calendar 共享声明、逐工具 grant、所属 Calendar 执行器及实际审批。`calendar` capability 或 macOS 完整访问不能替代这些条件。官方 `set_agent_tool_offer` 只允许系统应用，不能给 Muse 冒用。

## 实际运行证据

固定源码：Desktop RC2 `4ccf8e068399b1da139771a9ed94cef05fa6ae60`；App Hub `95e4831afca7227b640f075b252c04355bb63865`。依赖来自已核验固定 checkout；Calendar 原始库与实际 Appstore 一起编译，没有替换 service/存储/传输实现。

| 检查 | 结果 | 证据与边界 |
|---|---|---|
| 原版 Calendar | 原有7测试通过 | `build/pivot-builtin-calendar-original-r5`，源码逐字一致 |
| 原版独立进程CRUD/恢复 | 11检查通过 | `build/pivot-builtin-calendar-independent-r1`；每个操作启动新进程，独立读取实际文件，不是 Shell/Agent 调用 |
| 原版真实可见界面 | 7检查通过 | `build/pivot-builtin-calendar-native-r3`；创建、原ID改期、恢复、二次删除确认、删除后恢复；原 `os.calendar` Bundle 在参考宿主中合法使用系统开发模式，Muse没有使用系统模式 |
| 原版缺口复现 | 已保留 | 无 `get_event`；损坏文件被当空库，创建覆盖原内容。只在合成隔离文件中复现 |
| 最终隔离补丁 | 10 Rust测试、20进程/策略检查、7缺口检查通过 | `build/pivot-builtin-calendar-patched-r5`；7原测试保留、3新增回归 |
| 补丁真实可见界面 | 7检查通过 | `build/pivot-builtin-calendar-patched-native-r2`；明确绑定冻结Host SHA与补丁摘要 |
| Muse 在新版开发参考Host启动 | FAIL，保留 | `build/pivot-action-rc2-native-r1`，64ms脚本时间预算超时，尚无有效输入框；优化构建核对中，不提高预算、不清空历史 |
| 正式 Shell 准入/模型自主工具/人工审批链 | BLOCKED | 本机完整新版 Shell 尚未构建；默认商店工具 offer 仍不提供 Calendar。上述组件与UI通过不能替代这一项 |

早期原版 r2 报告的 `hub_head` 被Git向上查找误记为Muse HEAD；实际使用固定Hub checkout，r5已改用 preparation identity 的真实Hub SHA。原始报告保留，这个元数据错误不隐瞒。r3/r4准备支架失败、native r1/r2截图驱动失败均留在build；补丁r2签名fixture配置失败及r3改期风险声明失败也保留。

## 可审阅的最小补丁

补丁触及 Calendar 的 `src/lib.rs`、`src/ui.rs` 与 `bundle/tools.json`：

- 工具/UI用可失败的存储读取；JSON损坏或读取错误时拒绝写入及虚假空结果，保留原文件。
- 新增 `calendar.get_event`，通过一个精确event ID或request ID读回；明确缺失返回 `{found:false,event:null}`，损坏或多个匹配返回错误。
- 提议共享原事件更新与删除。保留原 `expected` 比对和所属服务检查；共享删除schema要求精确预期记录。
- 官方 `act` + `confirm:host` 仍属不需本人确认的监督方式。提议将更新既有记录声明为 `destructive`，与删除一样走Host确认，`auto_approvable:false`。这是需要维护者审阅的共享/风险策略调整。
- 没有改Relay身份检查、签名验证、默认Store offer、预算或Muse正式ID。更新/删除共享在当前官方说明中属于owner-only策略，不能自行称官方已经批准。

`HostLimits::with_offered_tools` 的实际策略组件已证明：宿主显式提供一个工具后可解析保持Muse身份的请求；额外删除请求、摘要篡改和缺签名仍拒绝。测试使用明确的无签名开发fixture，不是商店签名准入、原生授权或完整Relay的成功证据。

## 复现

Python需要3.11或更新版（系统3.9缺 `tomllib`，首次错误保留）。

```sh
python3 official_muse/semifinal/tests/run_builtin_calendar.py \
  --sdk /absolute/official-rc2-checkout \
  --hub /absolute/prepared-hub/app-hub \
  --out build/calendar-original-new-run --target build/official-hub-rc2-target \
  --protocol --native
```

追加 `--patch-calendar` 才测试提议补丁。UI脚本需显式提供该次 `--service-report` 和冻结的 `out/bin/muse-calendar-reference-host`。所有外部邮件/模型/生产日历操作数均为0。

## 下一步

向已有 #427 / #182 补充本轮编译、可见UI、存储故障和策略证据，请维护者确认商店应用的宿主offer及共享修改/删除正式路径。未经正式准入和同候选真实Relay/审批/读回，不移除行动链的“受阻”，不宣称自动日历闭环。
