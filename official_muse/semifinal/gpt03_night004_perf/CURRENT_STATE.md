# GPT03 NIGHT-004 perf

最新2026-10-12：Root明确8227bbb3…acde0d的新prepare/新VM真实重测14项PASS；31单次样本/3预热，Memory中位80.070419/p95 98.548852ms、Projection中位12.784918/p95 16.689480ms。evidence/candidate-8227-r1独立保存，闭包和全部落盘dataset SHA同c892；新旧归档复核PASS。新8文件export/全scope在candidate-8227-run-r1/gui-scale-export-r1。debug CLI无GUI64ms预算，未控负载差异不记代码退化；中央命令见CANDIDATE_8227。

2026-10-12 04:42（Asia/Shanghai）：c892 baseline真实计时完成，14项测量/数据/运行检查PASS，归档复核PASS。每API 31个正式单次样本、3次预热；gm_context中位76.644147ms/p95 91.168581ms，ac_projection中位9.477834ms/p95 12.758504ms，空桥接中位0.206595ms。

数据由现有scale生产save APIs生成64 Memory/128 Sources/32 Goal/32 Run/128 Action，无完成/核验或外部dispatch。实际parent perf_counter_ns含RPC/VM调度及原检索audit write；不是fixture clock计时，也不称GUI/网络性能。固定VM及157函数/65global身份保留；未改Main/SDK/包或旧54/107项，未Cargo/Kernel/GUI。

未来Main须等Root明确SHA，以同显式参数、新out重prepare/run并独立归档；当前新候选NOT_TESTED。命令见README，结果/边界见RESULT，短交接见HANDOFF_LATEST。完整46MB raw stdout在自有build，归档保存SHA及原204条perf标记。

Root追加的白名单export完成：8个本次生产save输出原字节副本、每文件API来源/SHA/counts、全scope字段在自有out/gui-scale-export-r2。无完成/核验或Secret输入；backup保留真实127 Sources/127 Actions/63 activity，未生成未落盘chat。GUI导入/Host默认scope适配仍NOT_TESTED。debug CLI VM只有总50M指令上限，未启用正式GUI64ms预算，Memory76ms不等同GUI预算失败。
