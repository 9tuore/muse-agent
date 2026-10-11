# 8227 同候选真实计时与fixture导出

2026-10-12，Root明确Main SHA：`8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`。核对Root源码字节后新prepare、新VM实际执行，**14项测量/数据检查PASS，归档复核PASS**。原c892报告/样本/manifest不改版本。

| 每项31个单次样本、另3次预热 | 中位 ms | p95 ms | 最小 ms | 最大 ms |
| --- | ---: | ---: | ---: | ---: |
| `gm_context` | **80.070419** | **98.548852** | 68.888477 | 106.934903 |
| `ac_projection` | **12.784918** | **16.689480** | 8.192569 | 17.065377 |
| 空RPC桥接对照 | 0.235053 | 0.282137 | 0.187259 | 0.284463 |

实际parent `perf_counter_ns`（mach_absolute_time）配对204条VM标记；计时包含start回复、IPC/调度和原函数。Memory每区间有一次实际owned审计write及资料clock RPC，Projection无内部IO；资料clock不是计时来源。p95 nearest rank，桥接不扣除。

VM仍是SHA `f48060d9…c5351`的现成**debug CLI**，源码只设置总50,000,000指令上限，**未启用正式GUI的64ms回调预算，80ms不能被记为GUI预算失败**。这是采集有效性，不是性能SLO通过。没有GUI/网络性能结论。

新157函数/65global与c892摘要相同；实际64 Memory/128 Sources/32 Goal/32 Run/128 Action及每个持久化文件SHA也与baseline完全相同。新旧数据/闭包比较保存`baseline-comparison.json`。两次均单进程暖测、各一个run、未隔离系统负载，因此表中差异本身不是代码退化证据。投影仍只覆盖API生成的Goal/Action分支、最近64动作/3节点，不称所有12节点/Calendar/Mail分支最坏耗时。

独立归档`evidence/candidate-8227-r1/`保留report、102原始ns区间、204原VM请求、实际Main状态、执行parent/prepare、闭包identity、dataset比较及export provenance。全IO stdout仍保留自有`build/gpt03-night004-perf/candidate-8227-run-r1/`并存SHA，不复制46MB入Git。

新候选8个白名单文件由本次生产save APIs生成并原字节导出至`build/gpt03-night004-perf/candidate-8227-run-r1/gui-scale-export-r1/fixture_files/`。manifest记录每文件API来源/SHA/数量，scope.json保留完整实际字段。primary规模64/128/32/32/128，backup仍64/127 Memory/Sources、32/32/127 Goal/Run/Action、63 activity；无completed/verified/Secret输入，chat未落盘故absent。Scope与baseline相同，合成user_id与foreign/空scope来源保留；未改Root profile或猜测Host默认scope。GUI import `NOT_TESTED`。

证据复核：

```sh
python3 official_muse/semifinal/gpt03_night004_perf/verify_evidence.py \
  --evidence official_muse/semifinal/gpt03_night004_perf/evidence/candidate-8227-r1 \
  --source-sha 8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d \
  --export-directory gui-scale-export-r1
```

Root最小中央命令（全新out，不Cargo/SDK/Kernel/GUI）：

```sh
TASK_ROOT='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松'
TASK_OWN='/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松'
TASK_SCOPE="$TASK_ROOT/official_muse/semifinal/gpt03_night004_perf"
TASK_SHA='8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d'
TASK_OUT="$TASK_ROOT/build/night-004/gpt03-perf-8227-acceptance-r1"

python3 "$TASK_SCOPE/prepare.py" \
  --source "$TASK_ROOT/official_muse/app/source/main.splash" --source-sha "$TASK_SHA" \
  --out "$TASK_OUT/prepare"

python3 "$TASK_SCOPE/run.py" \
  --prepared "$TASK_OUT/prepare/executed.splash" --source-sha "$TASK_SHA" \
  --runner "$TASK_OWN/build/gpt03-night004/target/debug/gpt03-night004-vm" \
  --samples 31 --warmups 3 --out "$TASK_OUT/run"

# 可选只导出，不启动或导入GUI。
python3 "$TASK_SCOPE/export_fixture.py" \
  --run "$TASK_OUT/run" --source-sha "$TASK_SHA" --out "$TASK_OUT/gui-scale-export"
```

中央同SHA复核、SDK实际storage位置/Host默认scope及合法GUI适配仍由Root决定。只改自有目录/证据，Main/SDK/包不改；`full_chain_status=NOT_TESTED`，不称最终R4通过。
