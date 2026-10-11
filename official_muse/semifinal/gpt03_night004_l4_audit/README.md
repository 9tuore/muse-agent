# Root 接收与最小复验命令

本目录仅含探针、父驱动、证据和审查，生产代码没有变化。读取 [RESULT.md](RESULT.md) 的状态边界。`verify_evidence.py` 可直接核对已保留的107项及故障时序，无新进程/副作用：

```sh
python3 official_muse/semifinal/gpt03_night004_l4_audit/verify_evidence.py
```

Root 接收该独立 commit 后，在 Root worktree 执行下列命令即可复验同一 c892 候选的四个场景；各 out 要不存在，保留旧结果。没有 Kernel/GUI 参数，不占中央共享 target。实际旧 runner/Mail binary 的字节身份固定，parent 拒绝漂移；recipient 脚本同样有 SHA 守卫。

```sh
TASK_ROOT='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
TASK_SCOPE="$TASK_ROOT/official_muse/semifinal/gpt03_night004_l4_audit"
TASK_OUT="$TASK_ROOT/build/night-004/gpt03-l4-acceptance-r1"
TASK_SOURCE_SHA='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" \
  --source-sha "$TASK_SOURCE_SHA" \
  --probe "$TASK_SCOPE/initial.splash" \
  --out "$TASK_OUT/initial-prepare"

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" \
  --source-sha "$TASK_SOURCE_SHA" \
  --probe "$TASK_SCOPE/restart.splash" \
  --out "$TASK_OUT/restart-prepare"

python3 "$TASK_SCOPE/run.py" \
  --runner '/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松/build/gpt03-night004/target/debug/gpt03-night004-vm' \
  --mail-binary "$TASK_ROOT/build/night-004/mail-fault-central-final-r2/accepted/mail-bin" \
  --receiver-script "$TASK_ROOT/official_muse/semifinal/mail_integration/gpt02_recovery/night004/receiver.py" \
  --initial-prepared "$TASK_OUT/initial-prepare/executed.splash" \
  --restart-prepared "$TASK_OUT/restart-prepare/executed.splash" \
  --gateway-deadline-ms 50 --gateway-delay-ms 250 \
  --out "$TASK_OUT/run"
```

预期 summary：8 phases/107 checks PASS；全链 `NOT_TESTED`。crash 初始 VM exit−9 是预期，其他 VM exit0、全部 Mail driver exit0；通过标准还要求真实 accepted/recipient、持久化pending状态、实际Queue期限/晚回包时序、各阶段检查和计数，不能仅看退出码。

GPT03 的实际结果在自有 `build/gpt03-night004-l4-audit/run-r1/`，包含 marker state、helper binary 副本与 raw logs；新增实际计时在自有`build/gpt03-night004-l4-audit/gateway-r1/`；本目录`evidence/`保存完整8报告、原始stdio、OS故障备份、实际执行parent、prepared closures/identity。没有归档可重建的18MB helper二进制。

原三场景`executed-parent-r1.py`保持原字节；新增实际网关由`executed-parent-gateway-r1.py`运行，report记录parent/receiver SHA。两批summary保留78/29计数，`summary-all.json`列合计107。新增实际计时不改旧立即timeout注入的边界。

仅复验新增网关时，在上面run命令追加`--modes gateway-timeout`，使用新out；预期2 phases/29 checks。仅复验原三场景用`--modes crash-after-review receipt-os-error review-cancel`，预期6 phases/78。fixture网关不改变生产超时，也不称实际SMTP断连。

## 尚未执行的 native overlap query

只准备 [overlap_query.splash](overlap_query.splash)，没有运行 Kernel。Root若执行，应从 c892重新prepare，交给既有 GPT02 `night004/l3/run.py`实际Kernel parent，并使用复制出的标记 Main L3 state/checkpoint和实际owner fixture配置。需要标准四个Kernel参数；该脚本已定义此契约，不在此发明新的CLI。

该探针要求原L3 checkpoint的event仍在actualowner中，检查真实 persisted `calendar.events`回执/digest/同字段event、owner SHA不变、无mutation/Mail运输。它只证明重叠原事件可见；`production_conflicts`只作观察，**不授予“冲突警告或创建阻断PASS”**。不要为了通过而手写history/receipt或启用被禁的legacy Calendar路径。
