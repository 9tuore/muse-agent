# Root 最小接收复验

本单元3场景54项PASS。完整路径、SDK源/库身份与边界见[RESULT.md](RESULT.md)。只读核对保存证据：

```sh
python3 official_muse/semifinal/gpt03_night004_model_json/verify_evidence.py
```

接收commit后，Root在其worktree执行下列两条命令；复用自有现成VM、Mail helper及已链接SDK driver，不需要Cargo、Kernel、GUI或包重建。out必须新建；parent严格校验Main、helper及SDK库/driver的SHA。实际driver及原build identity保留在GPT03自有build。

```sh
TASK_ROOT='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
TASK_SCOPE="$TASK_ROOT/official_muse/semifinal/gpt03_night004_model_json"
TASK_OWN='/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松'
TASK_OUT="$TASK_ROOT/build/night-004/gpt03-model-json-acceptance-r1"

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" \
  --source-sha c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4 \
  --probe "$TASK_SCOPE/probe.splash" \
  --out "$TASK_OUT/main-prepare"

python3 "$TASK_SCOPE/run.py" \
  --prepared "$TASK_OUT/main-prepare/executed.splash" \
  --runner "$TASK_OWN/build/gpt03-night004/target/debug/gpt03-night004-vm" \
  --mail-binary "$TASK_ROOT/build/night-004/mail-fault-central-final-r2/accepted/mail-bin" \
  --receiver-script "$TASK_ROOT/official_muse/semifinal/mail_integration/gpt02_recovery/night004/receiver.py" \
  --sdk-driver "$TASK_OWN/build/gpt03-night004-model-json/sdk-driver-r1/sdk-model-json-driver" \
  --sdk-build-identity "$TASK_OWN/build/gpt03-night004-model-json/sdk-driver-r1/build-identity.json" \
  --out "$TASK_OUT/run"
```

预期：19＋19＋16=54 PASS，两坏JSON均SDK实际attempts2/invalid_output、Main error/finished、无候选或完成记录；合法对照来自实际SDK成功解析。Calendar/Mail mutation、transport、HTTP、SMTP均0。全链`NOT_TESTED`。

原实际执行在`build/gpt03-night004-model-json/run-r1/`；本目录evidence包含3份完整报告、stdio、原始model/provider bytes、真实SDK Err/Ok及修复request、实际Main存储、SDK源码快照、链接身份、Main调用闭包及实际执行parent。binary仍保留自有build，不把约50MB可重建driver复制入Git。

`build_driver.py`可在必要时重新链接同一SDK库；它仅运行rustc，自有out，不调用Cargo。Root接收复验可直接使用上面的现成binary。
