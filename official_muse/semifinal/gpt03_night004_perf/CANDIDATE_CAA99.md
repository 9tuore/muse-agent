# caa99 新源码 benchmark 复验

2026-10-12，Root明确Main SHA `caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce`。核对中央实际字节、冻结自有build、新prepare后实际运行一次；**14项检查PASS，证据复核PASS**。每API31个单次样本、3次预热，共102区间/204条实际VM标记。

| 项目 | 中位 ms | p95 ms | 最小 ms | 最大 ms |
| --- | ---: | ---: | ---: | ---: |
| `bridge_only` | 0.329245 | 0.639138 | 0.202398 | 5.777647 |
| `gm_context` | 88.653645 | 105.173179 | 71.857585 | 134.366532 |
| `ac_projection` | 10.773112 | 15.596808 | 8.742508 | 17.000392 |

父进程perf_counter_ns/mach_absolute_time计时包含回复、IPC/调度和文件IO；Memory每区间1次实际owned审计write，Projection无内部IO；桥接不扣除，p95 nearest rank。

新157函数/65global中，仅core_boot_goals函数摘要改变，其他函数及全部global与8227相同；实际64 Memory/128 Sources/32 Goal/32 Run/128 Action的所有持久化文件SHA与8227相同。比较存baseline-comparison.json。每版本仅一次暖VM运行，未隔离系统负载，计时差异本身不是代码退化证据。数据是在空状态boot后由生产save API构造，本次基准不计规模恢复启动耗时。

新归档evidence/candidate-caa99-r1保存实际report/102原始ns区间/204标记/主备state/parent/prepare/identity/来源manifest。实际完整46,746,259字节stdout仍保留build/gpt03-night004-perf/candidate-caa99-run-r1并存SHA，不复制到Git。旧8227/c892证据不改。

沿用现有exporter导出本次8白名单原字节到build/gpt03-night004-perf/candidate-caa99-run-r1/gui-scale-export-r1/fixture_files，保存manifest/scope/API provenance，0 completed/verified，无chat落盘故absent。只导出，不启动/导入GUI。

```sh
python3 -B official_muse/semifinal/gpt03_night004_perf/verify_evidence.py --evidence official_muse/semifinal/gpt03_night004_perf/evidence/candidate-caa99-r1 --source-sha caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce --export-directory gui-scale-export-r1
```

同源码新执行参数沿用CANDIDATE_8227.md命令，须显式上述SHA、从该源码新prepare并选择全新out。现成debug CLI VM总50M指令，没有64ms时间预算；此结果验证采集/数据与组件行为，不验证性能SLO、Host64ms或GUI完整启动。投影只覆盖API生成Goal/Action、最近64动作/3节点。Root负责R5签包与实际GUI/full-chain。

仅自有组件和build，未Cargo/SDK重编译/GUI/Kernel/helper、未改Main/SDK/包/profile，无push。
