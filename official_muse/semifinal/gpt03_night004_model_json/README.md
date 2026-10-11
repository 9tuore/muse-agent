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
TASK_SOURCE_SHA='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" \
  --source-sha "$TASK_SOURCE_SHA" \
  --probe "$TASK_SCOPE/probe.splash" \
  --out "$TASK_OUT/main-prepare"

python3 "$TASK_SCOPE/run.py" \
  --source-sha "$TASK_SOURCE_SHA" \
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

prepare和run的`--source-sha`默认均固定c892。复验新Main时，Root须将`TASK_SOURCE_SHA`显式设为已核对的新候选SHA，并选择新的`TASK_OUT`；两个命令传同值，重新prepare后运行。脚本不读取当前HEAD或自动接受当前文件SHA；runner在创建out、读取binary或启动子进程前，校验prepared的source身份与executed字节SHA。case/summary记录本次显式SHA。

旧54项报告、实际执行parent/SDK快照及`evidence-manifest.json`仍属于提交4db56e的c892执行。该历史manifest中的活动脚本/文档摘要应对照4db56e内容；修改后的runner不得被冒充为旧执行parent。`verify_evidence.py`仍只核对旧归档，不能用来为新候选授予54项PASS。新SHA参数契约的检查见`source-sha-contract.json`；其中替代SHA是仅追加注释的明确身份fixture，不是未来Main业务或全链运行。
