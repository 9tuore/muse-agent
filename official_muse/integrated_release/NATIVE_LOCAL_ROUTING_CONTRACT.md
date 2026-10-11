# GPT-03：Native 本地 provider 与弱任务路由

2026-10-11。下文保留只读提案基线；后续已交付实际可应用单元 [routing/README.md](routing/README.md)，仍未应用到共享SDK或构建Host。黑屏工作按中央新安排停止；未改 Launcher、SDK、profile，未启动 GUI、Cargo、模型或网络。当前 Launcher 代码仍为 `332bf7e96d2af06870dcd9e483ee62cc011897c3`。

## 已核对的官方入口

- SDK：中央 `build/runtime-closure-full-shell-r1/sdk` 的实际文件；Makepad 构建归另一 AI，本文不申请或占用构建权。
- `apps/ai-providers/config/src/registry.rs:91` 已有 `local` family，无必需 key，默认端点 `http://127.0.0.1:8080/v1`。Launcher 实际使用动态 loopback 端口，不能照抄默认 8080。
- `apps/ai-providers/host-service/src/lib.rs:1122` 的 `llm.add_provider` 打开官方 Host sheet；`llm.sheet.submit` 只接受该 sheet。调用方不能直接传 provider JSON 绕过它。
- 添加 local 使用自定义模型 `Qwen2.5-0.5B-Instruct-Q4_0-offline`、custom route、`openai` 协议、当前 `state/local-model.json` 的 `route_base_url`（带 `/v1`；`base_url` 仅健康检查根地址），不填 key。alias 与 Launcher `--alias` 一致。已有 MiniMax primary 保留，新 provider 在尾部追加；已有相同 route 会拒绝重复。
- 保存 profile 后 `changed()` 重启现有 Kernel。配置应在启用持续任务前完成；不要在活动回合中反复调整 provider。
- Launcher 332bf 只刷新这个精确 local alias 的既有 route，不自动添加 provider；Model 页不会启动 Qwen。要添加时保持正常 hybrid 启动的本地服务存活，再进入 Models；否则测试不能成功。此次未操作 GUI。

## 当前排序的关键事实

`apps/ai-providers/host-service/src/complete/mod.rs:642`：所请求 class 排 0，其他已知 class 排 1，目录未知排 2，同 rank 保持 primary/fallback 顺序。

当前 `minimax-cn/MiniMax-M3` 是 strong；`local/local-default` **也是 strong**，不能将它当作官方 fast alias。Launcher 的精确 Qwen alias 不在目录中。故当前 MiniMax primary + 命名 Qwen fallback，无论请求 fast 或 strong，MiniMax 都先于未知 Qwen。

最小产品修改提案：在 `apps/ai-providers/config/data/model_catalog.json` 的 `models` 数组追加一条记录，不修改 `local-default`，不改路由算法：

```json
{
  "provider": "local/Qwen2.5-0.5B-Instruct-Q4_0-offline",
  "type": "fast",
  "default": false,
  "cost_in": 0,
  "cost_out": 0,
  "context_window": 4096
}
```

这是**产品目录覆盖**，不再是上游目录原字节；中央若采用需记录 patch 和新 hash。当前 catalog 使用 `include_str!`，需由有构建权的一方重新构建；仅改外部安装资源不会生效。4096 来自 Launcher 当前 ctx-size，不声称质量或上下文溢出行为已经实测。

针对当前双 provider 配置，上述提案使 fast → Qwen → MiniMax；strong → MiniMax → Qwen。另加同 class provider 后仍按本人列表顺序，不保证所有配置下 local 永远第一。无需改现有 hybrid Launcher，Native 的 `meta.class` 也会从 unknown 变成 fast。

## 费用、持续任务和验证边界

- `model.complete` 只接受 task/input/schema/class/allow_urls，不接受 provider、model、local_only。网络/HTTP/无文本失败会尝试下一个 provider；结构化输出被拒两次后直接报错，不因质量拒绝而自动升级云模型。
- `class:fast` 是偏好，不是零云端调用保证。现有 daily ledger 限调用/Token，不是货币费用上限。若中央要本地失败直接停止，需要另改候选过滤/策略，不能以本文一条 catalog 记录宣称已实现。
- 仅分类、短摘要、字段提取等有界任务应经 `model.complete`。它无工具、记忆、历史；Main Agent / Calendar Relay / Kernel loop 仍走 `_main` provider 配置。本文不把弱任务排序当成后台持续协同。
- 实际完成：只读源码、当前 catalog 元数据与排序的 Python fixture 检查；`NATIVE_LOCAL_ROUTING_FIXTURE.json` 含五个合成断言和源 SHA。Python 复现排序不是 Rust 测试或实际 provider 调用。未应用 catalog 提案，未测试 Qwen 推理、云推理、保存/restart 或真实 Agent 协同。
- 后续最窄验证：官方 Models 保存后核对非 Secret 的 family/model/route；重启 Launcher 更新动态端口；使用现有 fake Transport 测试 fast/strong 和本地失败回退；最后由中央在已授权范围内做两端各一次有界实调并从 Host 确认归因。App 返回的 meta 不含 provider/model，不能仅凭它证明走本地。

## 只读基线 SHA256

| SDK 相对文件 | SHA256 |
| --- | --- |
| apps/ai-providers/config/data/model_catalog.json | `65ee8b16156b33705e9937b8c9dc926e27aa247e30c7689f5ce3185313b91bf6` |
| apps/ai-providers/host-service/src/complete/mod.rs | `79ce9ed937208d8df1dca27110001c7af1c0bc365a4a605c1154b57053d7d2fe` |
| apps/ai-providers/host-service/src/lib.rs | `2c9685eec1aeea1e196154bbc074eeac0acfa831acbd779f049b60803859a538` |
| apps/ai-providers/config/src/registry.rs | `41067c516521c767880e7c197f72efb2f1d81225435f669cfa2ada2d73e2401d` |
