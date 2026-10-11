# Handoff

## Task

GPT03：Night Memory检索/行动链投影真实计时；基线c2c65cd2，Main c892。

## Result

baseline采集成功，14项PASS；每项31样本/3预热。gm_context中位76.644147ms/p95 91.168581ms；ac_projection中位9.477834ms/p95 12.758504ms。空桥接中位0.206595ms。

## Changed

仅新perf目录prepare/probe/parent/证据/文档；原54/107项不改。

## Tests

真实固定VM，生产save APIs建立64 Memory/128 Sources/32 Goal/Run/128 Action。真实perf_counter_ns配对204条标记，无完成或外部动作；范围/绑定/前后SHA及统计复核PASS。命令见README，raw在自有build/gpt03-night004-perf/baseline-run-r1。

## Commit

本地提交SHA见最终回复；未push。

## Remaining

等Root新Main明确SHA，以同显式SHA及新out重新prepare/run并另存候选证据。

## Important Boundaries

含RPC/VM开销与检索audit写入，未扣空桥接；合成资料/UI/clock/timer，单进程暖测，无GUI/网络结论或性能SLO。未Main/SDK/包修改，未Cargo/Kernel/GUI。
