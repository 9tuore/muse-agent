# Handoff

## Task

GPT03：Night真实计时/save导出；Main c892。

## Result

14项PASS，31样本/3预热。Memory中位76.644/p95 91.169ms；Projection中位9.478/p95 12.759ms；空桥接0.207ms。

## Changed

仅新perf目录，旧54/107不改。

## Tests

固定VM、64 Memory/128 Sources/32 Goal/Run/128 Action，真实ns/204标记，统计/绑定/SHA复核PASS。8文件原字节导出至自有baseline-run-r1/gui-scale-export-r2，来源/counts/scope见manifest；无完成/Secret，未补造chat。命令见README。

## Commit

本地SHA见最终回复；未push。

## Remaining

Root新SHA复验；GUI storage/默认scope由Root决定。

## Important Boundaries

debug CLI仅总50M指令，未GUI64ms预算，76ms不能判GUI失败。含桥接/audit；合成资料/UI/clock/timer，未Main/SDK/包修改及Cargo/Kernel/GUI。
