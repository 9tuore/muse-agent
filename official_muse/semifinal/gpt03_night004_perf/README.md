# 真实性能测量与显式候选复验

当前c892 baseline：`gm_context`中位76.644147ms、p95 91.168581ms；`ac_projection`中位9.477834ms、p95 12.758504ms。14项测量/数据检查PASS；真实值和边界见[RESULT.md](RESULT.md)。每项31个单次样本，另3次预热；桥接开销不扣除。

现成VM为target/debug中的debug CLI binary，仅设置50,000,000总指令上限；未启用正式GUI的64ms回调预算。不能将本次76ms等同GUI预算失败。

只读复核已存证据，不新启动VM：

```sh
python3 official_muse/semifinal/gpt03_night004_perf/verify_evidence.py
```

GPT03实际执行命令（旧out已存在，重现必须改为新out）：

```sh
python3 official_muse/semifinal/gpt03_night004_perf/prepare.py \
  --source build/gpt03-night004-l4-audit/main.splash \
  --source-sha c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4 \
  --out build/gpt03-night004-perf/baseline-prepare-r1

python3 official_muse/semifinal/gpt03_night004_perf/run.py \
  --prepared build/gpt03-night004-perf/baseline-prepare-r1/executed.splash \
  --source-sha c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4 \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --samples 31 --warmups 3 \
  --out build/gpt03-night004-perf/baseline-run-r1
```

Root接收后可复用固定VM；新Main必须等明确核对的SHA，把下方`TASK_SOURCE_SHA`显式替换为该值，并使用全新`TASK_OUT`，同值传prepare/run。默认固定c892，不抓当前HEAD或自动接受当前源。parent在创建out/启动进程前核对source、executed和VM SHA；任何非fixture backend失败。没有Kernel/GUI/Cargo/SDK/Host参数。

```sh
TASK_ROOT='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
TASK_OWN='/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松'
TASK_SCOPE="$TASK_ROOT/official_muse/semifinal/gpt03_night004_perf"
TASK_SOURCE_SHA='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'
TASK_OUT="$TASK_ROOT/build/night-004/gpt03-perf-acceptance-r1"

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" \
  --source-sha "$TASK_SOURCE_SHA" --out "$TASK_OUT/prepare"

python3 "$TASK_SCOPE/run.py" \
  --prepared "$TASK_OUT/prepare/executed.splash" --source-sha "$TASK_SOURCE_SHA" \
  --runner "$TASK_OWN/build/gpt03-night004/target/debug/gpt03-night004-vm" \
  --samples 31 --warmups 3 --out "$TASK_OUT/run"

# 可选：原字节导出本次生产save输出，仅写新的fixture bundle，不导入GUI。
python3 "$TASK_SCOPE/export_fixture.py" \
  --run "$TASK_OUT/run" --source-sha "$TASK_SOURCE_SHA" \
  --out "$TASK_OUT/gui-scale-export"
```

`verify_evidence.py`只验证固定c892归档，不能代替新候选实际run。未来结果单独保存，不改baseline report/样本/manifest。比较时须保留相同数据、VM、warmup/sample数量和计时边界，报告系统负载未控制；本测量不提供GUI帧率或真实Calendar/Mail网络结论。

已实际导出8个白名单文件到GPT03自有`build/gpt03-night004-perf/baseline-run-r1/gui-scale-export-r2/fixture_files`，同目录manifest列每文件生产API来源/摘要/数量，scope.json保留全部实际scope字段。实际导出命令：

```sh
python3 official_muse/semifinal/gpt03_night004_perf/export_fixture.py \
  --run build/gpt03-night004-perf/baseline-run-r1 \
  --source-sha c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4 \
  --out build/gpt03-night004-perf/baseline-run-r1/gui-scale-export-r2
```

两份chat未落盘，所以明确absent；backup是原前一状态（127 Sources、127 Actions、63 activity），未伪造为primary。没有completed/verified或Secret输入，未读Root profile、未自行GUI导入。SDK storage路径/Host默认scope尚由Root核对决定；不把export当GUI规模验收PASS。
