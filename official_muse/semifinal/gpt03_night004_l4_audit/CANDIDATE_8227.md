# 8227 同候选 Mail 故障复验

2026-10-12，Root明确新Main SHA：`8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`。先核对Root实际源码字节，再冻结自有build并重新prepare；实际8阶段**107/107 PASS**，本轮4场景合并一次执行，原c892的78＋29两批证据保持原字节。

实际SIGKILL exit−9发生于SDK accepted/独立recipient已收件、Main review回复尚未转发且sending/in_flight落盘时；accepted后receipt真实OS写错errno21保留旧主备摘要；实际Review cancel恢复DRAFT/failed；网关deadline50ms实际等待**52.204408ms**后Empty，250ms延迟reply实际**259.614452ms**入队并丢弃，没有转发。各自新VM/Mail/recipient readonly恢复同request/compose/message/payload，恢复review/transport0、没有Goal/Run/完成Memory。不是SMTP/生产网络故障。

新initial闭包144函数/65global，restart285/155；函数/global摘要均与c892逐项相同，comparison及逐字提取identity保留。本107探针不执行新GUI NativeCreate，所以目前无需新增类型/UI/backend适配；不据此授予NativeCreate guard或最终整链PASS。

实际父驱动、8份报告/raw、OS故障原backup、prepared闭包/identity单独保存在`evidence/candidate-8227-r1/`；实际完整state/helper副本仍在`build/gpt03-night004-l4-audit/candidate-8227-run-r1/`。新归档与默认旧归档证据核对均PASS。

```sh
python3 official_muse/semifinal/gpt03_night004_l4_audit/verify_evidence.py \
  --evidence official_muse/semifinal/gpt03_night004_l4_audit/evidence/candidate-8227-r1 \
  --source-sha 8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d --combined
```

Root最小中央重跑（新out，固定binary，不Cargo/Kernel/GUI）：

```sh
TASK_ROOT='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
TASK_OWN='/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松'
TASK_SCOPE="$TASK_ROOT/official_muse/semifinal/gpt03_night004_l4_audit"
TASK_OUT="$TASK_ROOT/build/night-004/gpt03-l4-8227-acceptance-r1"
TASK_SHA='8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d'

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" --source-sha "$TASK_SHA" \
  --probe "$TASK_SCOPE/initial.splash" --out "$TASK_OUT/initial-prepare"

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" --source-sha "$TASK_SHA" \
  --probe "$TASK_SCOPE/restart.splash" --out "$TASK_OUT/restart-prepare"

python3 "$TASK_SCOPE/run.py" --source-sha "$TASK_SHA" \
  --runner "$TASK_OWN/build/gpt03-night004/target/debug/gpt03-night004-vm" \
  --mail-binary "$TASK_ROOT/build/night-004/mail-fault-central-final-r2/accepted/mail-bin" \
  --receiver-script "$TASK_ROOT/official_muse/semifinal/mail_integration/gpt02_recovery/night004/receiver.py" \
  --initial-prepared "$TASK_OUT/initial-prepare/executed.splash" \
  --restart-prepared "$TASK_OUT/restart-prepare/executed.splash" \
  --gateway-deadline-ms 50 --gateway-delay-ms 250 --out "$TASK_OUT/run"
```

VM/Mail/receiver固定SHA均匹配；真实进程/SDK Mail/recipient/OS故障及实际期限，transport/Vault/approval/UI/clock为fixture，SMTP0。`full_chain_status=NOT_TESTED`。只改自有证据与verifier/文档，Main/SDK/共享target/包未改，中央接收复核待Root。
