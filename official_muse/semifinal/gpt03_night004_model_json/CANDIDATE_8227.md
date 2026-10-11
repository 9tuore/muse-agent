# 8227 同候选组件复验

2026-10-12，Root明确授权的新Main SHA：`8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`。先核对Root实际源码字节，再复制到自有build并重新prepare，实际新进程重跑3场景：**19＋19＋16＝54/54 PASS**。这是新执行，原c892报告与raw没有改版本。

新source identity包含203函数/88global；其摘要与c892相同，逐字提取核对PASS，已存`closure-comparison.json`。SDK/driver/VM/Mail/recipient固定SHA守卫仍生效，实际SDK库运行前后不变。两种坏原始JSON各经实际SDK尝试2次后真实返回invalid_output，原Main回复error、请求finished、持久化trace invalid_json；候选/Goal/Run/Action/完成Memory均0。合法对照实际SDK解析成功。HTTP/SMTP、Calendar/Mail mutation、transport及收件均0。

新raw、SDK Err/Ok及修复request、Main存储、ledger、父驱动与prepared闭包单独保存在`evidence/candidate-8227-r1/`，build原始执行在`build/gpt03-night004-model-json/candidate-8227-run-r1/`。新证据复核和默认旧c892证据复核均PASS；不额外增加54运行计数。

```sh
python3 official_muse/semifinal/gpt03_night004_model_json/verify_evidence.py \
  --evidence official_muse/semifinal/gpt03_night004_model_json/evidence/candidate-8227-r1 \
  --source-sha 8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d
```

Root中央最小重跑（新out，不Cargo/Kernel/GUI）：

```sh
TASK_ROOT='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
TASK_OWN='/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松'
TASK_SCOPE="$TASK_ROOT/official_muse/semifinal/gpt03_night004_model_json"
TASK_OUT="$TASK_ROOT/build/night-004/gpt03-model-json-8227-acceptance-r1"
TASK_SHA='8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d'

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" --source-sha "$TASK_SHA" \
  --probe "$TASK_SCOPE/probe.splash" --out "$TASK_OUT/prepare"

python3 "$TASK_SCOPE/run.py" --source-sha "$TASK_SHA" \
  --prepared "$TASK_OUT/prepare/executed.splash" \
  --runner "$TASK_OWN/build/gpt03-night004/target/debug/gpt03-night004-vm" \
  --mail-binary "$TASK_ROOT/build/night-004/mail-fault-central-final-r2/accepted/mail-bin" \
  --receiver-script "$TASK_ROOT/official_muse/semifinal/mail_integration/gpt02_recovery/night004/receiver.py" \
  --sdk-driver "$TASK_OWN/build/gpt03-night004-model-json/sdk-driver-r1/sdk-model-json-driver" \
  --sdk-build-identity "$TASK_OWN/build/gpt03-night004-model-json/sdk-driver-r1/build-identity.json" \
  --out "$TASK_OUT/run"
```

边界不变：实际SDK decoder/refusal/重试/ledger与原Main VM/文件IO，provider字节/grant/UI/timer为fixture。没有重建SDK、包或新增Host端口。`full_chain_status=NOT_TESTED`；不称真实模型、GUI NativeCreate或最终R4整链通过，中央接收复核由Root执行。
