# GPT01 continuity patch

交付是可审代码；产品状态 **PARTIAL_COST_GATE_NOT_CONNECTED**。SDK 基线 `b95b7b2343615b3f0a1c7654f353fcb669e4517d`，Kernel `b0759a57719fd35b3a2da1c5d969bc67538ed516`；五份原文件的逐文件 SHA 在 `BASELINE.json`。仅本目录有改动，未改共享 SDK、target、用户 profile、Secret 或产品模型顺序。

`GPT01-continuity.patch` 改 SystemChat 的 session/model/mod/view，新增 continuity 与 continuity_tests；原 tests.rs 只复制，未改。Native 面板提供正式 list/create/pause/resume/delete；固定 900 秒，显示当前 profile 主模型标签和 Kernel 真实 7 天/10000 次触发上限。所有请求固定既有 system session/profile，ID 只来自匹配的真实记录；错误/未知回执不成功、不自动重试创建。启用时保留同一 Driver 连接，关窗不暂停；重连先 list 匹配原 ID，未知 create 可由同规格唯一记录恢复。暂停与移除不发送 turn/interrupt，不把 queued 当执行成功。

**费用边界具体接入点：** `SystemHost::continuity_policy()` 是新增 Native 校验入口；生产 `ShellSystemHost` 保持默认拒绝，fixture 的 Ready 仅用于无网络测试。Host 必须核实该 profile 的实际主模型及底层已经实施的费用约束，再返回 Policy；两条显示文本不会实施预算。未经这一步，UI 启用/恢复不可用，刷新/暂停/移除已有 ID 仍可用。Kernel LoopFire 不经过 Host model.complete 的 ledger，因此不能用该 ledger 假称循环费用已受限。

底层核对来源（相对锁定 Kernel 根）：`crates/octos-cli/src/api/ui_protocol_transport.rs:10187` 的创建字段没有可设小配额；`autonomy/agent_orchestrator.rs:96` 固定 7 天/10000 次，`:21181` 给真实 LoopRuntimePolicy 固定 max_fires，`:19437` 恢复 fires_used。`crates/octos-cli/src/config.rs:1600` 的 max_output_tokens 限单次输出，不能限制总费用。SDK `apps/ai-providers/host-service/src/complete/ledger.rs:20` 有 per_minute/calls_per_day/tokens_per_day，`:34` 默认值为 6/100/100000；它只管 model.complete。最小可实施后续边界是给现有 Kernel LoopRuntimePolicy 接通可设置且持久化的小 max_fires，并把总 token/费用预算实施在实际循环模型调用路径、回读其计数，再接 Native policy。以上是后续改动建议，未伪造新 OUP 字段；本补丁没有启用真实付费循环。

窄验证：24 个 continuity fixture 测试 PASS，0 失败；真实 patched Driver/model/controls 与真实 peer contract/ToolReply 编译，Shell 发现与 grant plumbing 为明确 double，Makepad 日志宏只在 harness 改成 log::info。测试涵盖默认停用、明确启用、原 ID 恢复、丢失/错误创建不重试、重复点击、错 scope/多记录、关窗保持、暂停不打断人的回合、过期不能恢复。零 fuzz dry-run/apply/字节回比 PASS。**未编译完整 Shell，未验证 Native kernel cfg 的 profile reader 与 Makepad UI 集成，未跑 GUI/live/官方 full-chain。**

复现（在本目录；所有输出只在本目录）：

```sh
python3 prepare.py
cargo test --offline --locked --manifest-path harness/Cargo.toml --target-dir harness/target --lib continuity
```

中央应用前逐文件核对 BASELINE.json，再在目标 SDK 根执行 `patch -C -p1 -F 0 -i <本目录绝对路径>/GPT01-continuity.patch`；中央负责实际应用和整包验证，当前不占用 WorkBuddy 的共享 GUI/Cargo。
