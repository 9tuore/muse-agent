# NIGHT-004 原聊天行动链恢复补丁

2026-10-12，GPT03 自有 worktree。**最小两行补丁及实际官方 VM 验证完成；中央实际全进程重启复验待 Root 执行。** 本单元未修改共享 main、SDK、Host、GUI、target 或生产资料，未发送跨聊天消息、未 push。先前输入/容量验证独立提交 `a538855d`（48/48，源 e7d）；本补丁是后续单元，不把前一源的检查算作候选源验收。

## 现场失败与因果定位

Root 真正的 native L3 initial 22/22 PASS；全进程 restart 13/14，仅 `original_action_chain_restored` FAIL。原报告位于中央 `build/night-004/native-l3-central-r3/restart/report.json`，身份与断言/节点摘录保留于 [Root 原 FAIL](evidence/Root-original-failure-extract.json)。原 chat 被选回、Goal completed、精确同 ID event、Mail/声明、Run、来源/完成 Memory、新聊天召回和恢复 transport 0 均成功，行动链只有 Goal 节点。

只读核对中央 FIXTURE_ONLY state，复制 16 个已有 fixture 文件和完整结果产物至自有 IO。真实官方 VM 执行生产 boot、新建 chat、回忆、选回原 chat 和原行动链断言。**未改原断言，也没有 fixture 写入新的 completed/verified 状态。** [baseline-r3](evidence/baseline-r3/report.json) 5/6 FAIL 精确复现；记录结构合法、身份/版本/卡片绑定/完整 Goal/Action/payload/声明/Run/来源 SHA 均匹配，唯一完成匹配失败是完整改期记录的 JSON 文本比较。

具体差异：artifact authority.update 与重载 record 是相同的 8057 字符 JSON 值；Python 解析字段和值相同，实际 VM 的结构比较为 true，双方 `to_json()`（包括再次 parse 后 to_json）仍因对象键顺序而不同。首个差异在第 1621 字符：一方先输出 `creation_request_id`，另一方先输出 `creation_turn_id`。没有缺字段或改值。只改该比较后 Calendar 两个节点恢复，但 Mail 仍缺失；[candidate-r1-diagnostic](evidence/candidate-r1-diagnostic/report.json) 证明 Mail 的整个 authority 再次因同一 record 键顺序比较失败，结构值相同。

实际 SDK 的 `platform/script/src/opcodes_ops.rs` 中 `==` / `!=` 调用带工作/时间上限的 `deep_eq_bounded`；`equality.rs` 对对象按键找值、保留数组顺序及字符串内容比较。此能力来自现场源码，并由本轮真正 VM 中结构比较及负例验证，不是猜测接口。

## 可应用补丁与身份

[completion-order.patch](completion-order.patch) 仅改两行：

- `mail_native_completion_matches` 比较整个 parsed authority.update 和整个 canonical record 的结构值；原完整字段、嵌套值、Goal、Action、声明、Run 和产物摘要门禁保留。
- `calendar_agent_authority_current` 对完整 current / supplied authority 各自 JSON round-trip 后比较结构值；只排除对象键输出顺序的影响，不忽略字段、数组顺序或 JSON 字符串内部字节。

| 身份 | SHA-256 |
| --- | --- |
| 冻结基线 main | `e7d665dd7f466e454aeca071895273e81549af169f8613c3490671a3cf8cca20` |
| 最终候选 main | `c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4` |
| 最终两行 patch | `c7ea3e478fb62fa552270f25fd615c64f8ae911b2803914d98d901dfa0db5806` |
| 复用官方 VM runner | `f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351` |

`prepare_patch.py` 核对 e7d 基线、两个替换唯一、函数清单相同、仅上述两个函数正文变化，其余函数逐字一致。对自有 build 中基线副本执行真正 `git apply --check` 和 `git apply`，结果与候选逐字相同，SHA 如表。未向中央 main 应用。

## 已执行的候选验证

| 实际 VM 检查 | 结果 | 提交内证据 |
| --- | --- | --- |
| 原恢复断言及新 chat 隔离 | 6/6 PASS | [candidate-r2](evidence/candidate-r2/report.json) |
| 同一恢复流程与防改写检查 | 22/22 PASS（包含上述 6 项） | [guards-r1](evidence/guards-r1/report.json) |

候选恢复 4 个节点：Goal、“官方日历同ID改期”“改期精确读回”“回复草稿”；Calendar/Mail 为已核验，next 提示该事项完成结果可在全局记忆回读。新增 chat 的行动链仍为空。两份 passing 报告 exit 0、stderr 空、实际外部调用及 transport 意图均为 0。

16 个新增检查覆盖：合法但不同的嵌套 record、新增 record/嵌套字段、不同或新增 authority 字段、JSON 文本字段字节改写、Goal 内容/新增字段/数组变化、Mail payload 改写、缺 verified Action、重复完成 Run、缺结果 Source、结果文件仅加空格导致原字节 SHA 变化，均继续拒绝；恢复原始 bytes/refs 后 matcher 和 Mail authority 恢复为 true，已保存 store 摘要保持原样。没有改成“只比较 request ID”等弱化条件。

原 baseline 三轮 FAIL、只有第一行修复的两轮部分 FAIL 和最终 PASS 均保留；[索引](evidence/index.json) 列出源、executed、probe SHA 与自有 build 原始目录。这里是读取实际 L3 fixture 字节后进行的 L4 生产函数验证，不是新的真实 Kernel/Mail/full-chain PASS。Root 原失败记录不可覆盖，仍需中央集成相同 SHA 后跑真实 restart 原断言。

## 重现与交接

工作目录：`/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松`。

```sh
python3 official_muse/semifinal/gpt03_night004_actionchain/prepare_patch.py \
  --baseline build/gpt03-night004-actionchain/baseline.splash \
  --candidate build/gpt03-night004-actionchain/proposed.splash
python3 official_muse/semifinal/gpt03_night004_actionchain/run.py \
  --source build/gpt03-night004-actionchain/proposed.splash \
  --expected-sha256 c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4 \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --seed-files official_muse/semifinal/gpt03_night004_actionchain/evidence/seed-files.json \
  --probe official_muse/semifinal/gpt03_night004_actionchain/guards.splash \
  --out build/gpt03-night004-actionchain/guards-new
```

基线及候选留在自有 build；复制输入及逐文件摘要随本单元提交，均来自中央显式 FIXTURE_ONLY state。`--out` 必须是新的自有 build 子目录，旧证据不覆盖。七个 IO/UI 适配函数与 transport/timer/clock 是明确测试边界，其余生产函数在 VM 中原样执行；报告保存全部生产函数摘要。

Root 接收最小 patch 或等值实现后，核对中央完整候选 SHA，再做实际全进程 restart 和原 `original_action_chain_restored` 断言；不要改 probe、Calendar 身份守卫或已存收据。正式发布、费用、实际联系人、Host/GUI 与 parent 验收不由本单元执行。根 `CURRENT_STATE.md` / `HANDOFF_TEMPLATE.md` 现场不存在，按本轮只允许专有 namespace+build 的范围在本文件记录交接。未跟踪的 `official_muse/integrated_release/gui_smoke.py` 保留。
