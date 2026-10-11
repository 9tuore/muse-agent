# Contained Chat 正式集成审查

结论：当前 SDK 可以接通一个应用级 Octos 会话；不能用一处 `model.complete` 替换，在保持现有多 Chat、项目焦点、Memory 更正/遗忘与停止语义的同时完成正式集成。以下是已定位的 API 阻塞，供中枢实施；没有修改主源、SDK、Gate、身份或用户数据。

审查基线：现场 `official_muse/app/source/main.splash` SHA256 `2253e9f00e8a0a57b713c316db2c40d26e5c937beef54703833a52cdee6cb7fa`。这是所读源文件，不能据此声称 rc2 包含该版本。SDK 证据来自现场 `build/runtime-closure-full-shell-r1/sdk/`；没有验证签名 bundle 或运行中的 Host 与该 SDK 一致。

## 已核实的接口

| Contained service | 允许参数 | 已观察的语义 |
| --- | --- | --- |
| `octos.session.open` | `{}` | 返回 `open`、`conversation`、`shared_history` 与可选 model 信息；不返回 UI session 的独立句柄 |
| `octos.turn.start` | `text`、可选 `trigger`/`from` | 同一应用共享上下文；已有 turn 时拒绝；完成返回 `turn_id`、`text`，conversation 路径另有 `speaker`/`lane` |
| `octos.session.history` | `{}` | 返回合并的 person/system_agent 历史，包含此前上下文记录 |
| `octos.turn.interrupt` | `{}` | conversation 路径停止两条 lane；不是按 UI request/turn 精确取消 |

`octos.context.close` 出现在 Native peer wire 服务表中，但不在 Contained `parse` 的允许服务中。Native 的 `client` 也不能直接传给 Splash Contained；额外参数会被拒绝。没有观察到 Contained reset、fork、forget 或项目隔离服务。

定位：`ai-host/src/contained.rs:1-40,348-369,395-417,489-523`；`app-peers/src/broker.rs:3047-3115,3156-3216`，均相对上述 SDK crates 目录。

## 主源现状与缺口

1. `send_chat` 使用 request_id + 原 session_id 接收回复，检查 request 仍 running 及候选绑定。切换可见 Chat 不会把回复写进另一 Chat；更改该 Chat 焦点会使它的请求失效。无需为这一点重复添加全局 selected_id 判断。
2. `muse_model_request` 在派发前检查 Memory、账号、用户、启用状态与焦点；回调检查捕获的 Memory refs。更正改变 revision，遗忘/撤权使引用失效。但回调没有完整重验派发时捕获的账号/用户/启用快照；无引用回复尤其不能仅靠 refs 检查证明身份没有改变。中枢可在回调采用结果前重验这些快照与 `current()`，沿用现有错误路径。不要把当前全局焦点等同原 session 的焦点，避免切换 Chat 错杀有效回复。
3. `chat_reply_context_valid` 对没有 `memory_refs` 的旧回复返回 true。Native 文本及其历史没有天然的 Muse Memory refs；不能将空数组包装当作“遗忘安全”。
4. `chat_stop` 只将本地请求标为 cancelled，阻止采用迟到回复；没有 Host interrupt。接入 Octos 后外部工具可能已执行，本地取消不能宣称停止或回滚外部动作。
5. 现有 `model.complete` 的 schema output 会生成 Mail/Calendar/Goal 待审候选。Octos 返回 `text`，且可能调用工具。两者不能共享一条“成功→候选创建”分支；从文本解析出的 JSON 也不能作为工具执行证据。

主源定位：`send_chat:7906`、`chat_model_request_current:8014`、`muse_model_request` 的派发/回调段、`chat_reply_context_valid:7445`、`chat_focus_save:8393`、`chat_stop:8386`。行号仅针对本次 SHA；集成前重新定位。

## 阻塞正式替换的最小 Host 契约

以下是需要实现和验证的行为要求，**不是现存 API 名称或参数**。

- 为 Muse 本地 Chat/session + 项目/归属 + Host 账号提供稳定独立上下文，恢复时返回可核对的绑定；禁止默认接入其他 Chat 或系统代理的共享历史。
- Memory 更正/遗忘或撤权后，在下一轮模型构造 prompt **之前**排除旧事实及其派生历史。客户端只过滤 History 显示、追加“请忘记”或丢弃旧回调都不满足此项。需要 Host 上游的上下文重建/失效机制，不删除用户原始历史。
- 取消须有可验证的作用域与结果；若 SDK 只能停止两条 lane，UI 必须明确是停止整个应用代理，不能伪装成单 Chat 取消。取消/超时后已派发工具动作保持待核验，不自动重试。
- History 的工具记录必须能够可靠绑定当前上下文、turn_id、call_id、工具名及 Host outcome；若字段缺失或关系歧义，只显示待核验。`text`、speaker.kind 或 person lane 均不能替代执行/人类授权证据。

在此契约实现前，保持现有多 Chat 的结构化草拟路径；共享 Octos 接线仅能声明为应用级代理会话，不能宣传已有项目隔离或遗忘闭环。不要向共享上游注入私人 Memory 来制造表面恢复效果。

## 可直接实施的薄接线顺序

1. 使用经实际 bundle 验证的 manifest 服务声明与既有 Host consent；不添加 Gate 绕过或 profile/identity 参数。
2. 应用级代理会话只允许一个本地待处理 turn；启动前捕获 request/session/项目/归属/账号/Memory 快照。显式 `trigger: app` 用于应用自动发起任务；不能把 `trigger: person` 当作经过核验的真实 Person。SDK 将其记录为 `app_says_person`。
3. `session.open` 完成并核对状态后再 `turn.start`；请求期间不靠模型文字更新执行状态。返回的 turn_id 与本地 request 绑定，之后读取 History 获取工具证据。当前返回 turn_id 在完成时才可获得，不能假装具备派发前的精确 turn 取消句柄。
4. 恢复只通过已持久化绑定核对 Host History；只投影匹配的记录，跨 lane 或身份不明记录不得归因到当前 UI Chat。应用本地互斥不能阻止 shell/system_agent 的其他入口，SDK busy 拒绝照实展示。
5. 回调重验原请求/身份/焦点/Memory；失效结果不得生成新候选、污染 Prompt 或更新 verified。History 显示过滤仍不能解决上游记忆污染，必须继续标注上述接口阻塞。

## 验证与交接

已完成只读源码审查和源文件 SHA 核对；未跑模型、GUI、Cargo、外部动作或新测试，未改主源/SDK，未做 Git 操作。本文件是 API 审查与实施边界，不是正式版验收通过证据。

中枢最小后续验收：两 Chat/两项目不会共享事实；更正后不用旧 revision；遗忘后上游不重现旧事实；恢复不会错绑 History；单 Chat 停止不会意外停止别的 lane；取消/超时后的工具 outcome 仍可核验。这些要求待 Host 契约与实际 bundle 完成后验证。
