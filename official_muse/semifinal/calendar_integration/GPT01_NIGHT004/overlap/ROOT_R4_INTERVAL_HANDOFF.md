# R4 compact native interval probes

状态 PREPARED_NOT_RUN。实际中央 source SHA `8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`、产品 commit `197d16d785533469b0e90ab720d4f110f3ebe505` 已只读核对。中央同 Main 的 guard 49/49/RPC0 PASS；这不是三例真实 signed runtime 结果。R4 signed Main SHA 与公开 kernel-config 由 Root 从实际新包核对。

共同 probe 的最终格式函数只读取已完成的 scalar observations/checks：`let result_json = (...).to_json()` 后 `return result_json`。无 fixture_rpc 在格式表达式中；raw History/owner/receipt/counters 保存在原 parent trace/Kernel JSONL/owner store，不在 final JSON 嵌套。精确 final assignment 与精确 local-string 出口用保存真实字段在原 VM exit0/stderr空/RPC0，1384字节合法 JSON；仅format-only，不是新旅程PASS。记录 COMPACT_OUTPUT_VM_RESULT.json。

新准备目录（每例338 production functions／184 globals，逐字归一化断言通过）如下，身份见 R4_INTERVAL_PREP_R6_RESULT.json。使用实际中央 Main source 与 explicit8227 SHA，未覆盖任何旧out/r1/r2。

| Case | Prepared absolute path | 预期 |
| --- | --- | --- |
| same | `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r6/same/executed.splash` | 新候选第一次query后owner1/SHA不变，显示原事项重叠与修改指导，不作第二次选择 |
| contained | `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r6/contained/executed.splash` | 同上；旧bounded from/to完整包含过滤不返回原事件，完整query须发现实际包含重叠 |
| adjacent | `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r6/adjacent/executed.splash` | 第一次query不写，显式history settle后第二次candidate操作创建并精确add/get读回，owner2 |

三例原事件 `ev-1791775730787` 七字段不变；不完成Goal/Run，不发Mail。query实际精确 `{"limit":200}` 的receipt由Main guard核验，parent保留原始记录。模型candidate/tool choice和UI选择仍fixture。manual overlap合法；提示词不是按turn权限隔离；额外mutation只能让UNKNOWN/no第二次nativecreate，不能撤回query副作用；snapshot不预约时段，原Host边界保留。

Root只需为每个case选独立全新F；脚本只copy Main/Mail fixture与实际原owner字节，不复制旧Kernel ledger，不启动服务，不签名。下面 `R4_MAIN_SHA` 和 `R4_KERNEL_CONFIG` 必须是Root实际新candidate字段，`CASE`为same/contained/adjacent，`F`为中央build/night-004新目录。

```sh
O='/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松'
C='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
P="$O/official_muse/semifinal/calendar_integration/GPT01_NIGHT004/overlap"
python3 "$P/prepare_root_case.py" --out "$F" \
  --source-sha 8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d \
  --main-sha256 "$R4_MAIN_SHA" --kernel-config "$R4_KERNEL_CONFIG"
python3 "$C/official_muse/semifinal/mail_integration/gpt02_recovery/night004/l3/run.py" \
  --prepared "$O/build/gpt01-native-overlap-prepared-r6/$CASE/executed.splash" \
  --runner "$C/build/night-004/native-l3-central-r4/initial/vm-bin" \
  --mail-binary "$C/build/night-004/native-l3-central-r4/initial/mail-bin" \
  --state-root "$F/state" --mail-root "$F/mail-state" --out "$F/run" \
  --kernel-bridge "$C/official_muse/semifinal/calendar_integration/GPT01_NIGHT004/kernel_bridge/bridge.py" \
  --kernel-test-binary "$C/build/night-004/frozen-runtime-testbin-r8/shell-test-bin" --kernel-test-frozen \
  --kernel-binary "$C/build/muse-integrated-0.4.0-rc6-standalone-r2/Muse.app/Contents/Resources/host-runtime/octos-kernel" \
  --kernel-config "$F/kernel-config.json"
```

旧baseline的第一次重叠写已由真实owner/Broker证明，原failed report和非法JSON保持原样；不再为旧baseline造成功结果。无SDK/Cargo/中央Main/生产状态写入。
