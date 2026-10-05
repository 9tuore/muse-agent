# RC25：连接测试、语义完成与 fallback 的边界

结论：现有证据不足以把普通 Chat 的成功归因到 GPT-4o，也不足以断言已经 fallback。最先应核对的是**候选排序与响应封装解析**，然后区分**同候选格式重试**。这是排查顺序，不是对实际故障概率的估计；T17 仍未验证。

本次只读冻结 SDK。Root 提供的“GPT-4o direct llm.test 已连接 845ms、设首选后普通 Chat success / attempts=2 / estimated=true、已恢复 M3 首选”作为外部观察记录，未由本评审复现。未读取真实 profile、Secret、模型响应原文或现场日志，未调用模型、GUI、Host、Git，也未运行测试。

## 代码已证明的边界

1. **连接测试直接选指定 ID，且仅验证 HTTP 2xx。** `src/lib.rs:1167–1175` 按 ID 取 provider 后调用 probe。`src/probe.rs:28–55` 发送 ping：OpenAI/Anthropic 的 max_tokens=1，Responses 的 max_output_tokens=16。`143–168,184–187` 在 2xx 时直接返回 ok；HTTP 200 的空文本、错误封装甚至非 JSON 都不会在此失败。“已连接”因此不能证明普通聊天所需的有效文本、JSON/schema、usage 或最终回答者身份。

2. **首选设置不等于 model.complete 必定先用该项。** `src/complete/mod.rs:433–443` 按 profile 顺序收集可用候选，`752–762` 再按请求 class 排序：匹配 class、其他已知 class、未知 catalog。用户顺序只在同一 rank 内保留。未读取现场 profile 和该次请求的完整路由证据，不能断言 RC25 第一跳是谁。

3. **两种“不是 JSON”位于不同层。** `src/complete/wire.rs:114–160` 解析 HTTP 响应封装并提取文本；封装非 JSON 或无文本会从 send 返回错误，经 `mod.rs:669–680` 在尚未格式重试、且非 timeout 时转下一候选。反之，封装合法但 content 不是目标 JSON/schema，是 `accept` 层错误：`mod.rs:683–708` 只在 usage 完整等条件满足时对当前候选重试一次。不能把两类错误都归为普通 JSON 格式重试。

4. **attempts=2 / estimated=true 有至少两条可行路径。**

| 路径 | 第一次 | 第二次 | 结果来源 |
|---|---|---|---|
| fallback | 非 timeout 的已发送失败：HTTP 错误、封装解析失败或无文本等 | 下一候选成功 | 备用候选；失败使 estimated 标记保留 |
| 格式重试 | 封装/usage 完整，但 content 的 JSON/schema 校验失败 | 同候选修正成功，但 usage 缺失或不完整 | 同一候选；第二次 usage 估算 |

`mod.rs:370` 对 estimated 做 OR；`724` 只在实际进入 transport 前计次。首次缺 usage 且 content 无效会直接拒绝而不格式重试；timeout、refused、truncated 也不能笼统当作可 fallback。成功元数据 `392–402` 只含 class/requested/attempts/usage/budget，未含 provider/model 身份；`tests/complete.rs:197–211` 还明确断言身份不暴露。class 不能替代唯一模型身份证明。

## 最小下一步验证

1. **先利用已有固定事件。** 若 Root 已有可按一次独立请求窗口归属的 Host 证据，只提取 `MODEL_FORMAT_ERROR app=… attempts=1` 与 `MODEL_RETRY app=… attempts=2` 等固定字段。代码位置 `mod.rs:656–657,684–685`。配对且能准确归属时支持“格式重试”；现有行没有请求 ID，并发可能混杂，缺行或截断日志不能反证 fallback。无需获取请求体、响应体、headers、URL、profile 或 Secret。本轮没有读取日志。

2. **如需复现机制，用现成离线注入点。** `tests/complete.rs:31–68,89–108` 已有 Fake Transport、Fixed Providers、Rig，以及 `Options.providers/transport` 注入。用合成 A/B 候选和假响应验证：① 2xx 坏封装→B 成功；② A 完整 usage 的无效 content→A 有效 content 但无 usage；两者都可得到 attempts=2 / estimated=true，而 fake 捕获的候选序列不同。另对同一 2xx 坏封装比较 `probe::describe_response` 与 `wire::parse_reply`，直接证明连接与语义解析边界。仅提议这些窄 fixture，本轮没有新增或执行测试；不能用 fixture 证明真实 GPT 已响应。

3. **真实身份结论维持未验证。** 先看既有且已授权的 Host 内部证据能否关联最终成功候选；若不能，在当前不改 Host、不读生产配置、不发模型调用的边界内，就没有可靠途径补出身份。保留备用模型、旧失败和 T17 未完成状态。不建议通过删备用项、伪造 provider 参数、改生产路由或扩建 Host 模型架构来“验证”。

现有相关测试源码：`tests/complete.rs:262` 格式重试、`:448` class 排序和 fallback、`:564` 首次 timeout 不 fallback、`:614` usage 不完整不格式重试。它们是已读测试定义，**不是本轮测试 PASS 证据**。

## 交付与范围

仅新增本目录 `PROBE_FALLBACK_REVIEW.md/.json`。冻结源码绝对路径及逐文件 SHA-256 保存在 JSON。产品源码、主报告、生产配置、GUI、模型、Git 均未改动。下一步离线验证为建议项，尚未执行；实际后端身份仍未验证。
