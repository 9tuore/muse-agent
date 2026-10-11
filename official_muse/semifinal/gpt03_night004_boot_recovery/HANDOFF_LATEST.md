# Handoff

## Task

GPT03：Root R4恢复超预算；基线27709cae，Main8227。

## Result

PARTIAL：最小patch、6例46项VM功能PASS；Host64ms待Root R5。

## Changed

仅本目录patch/probe/verifier/证据文档；core_boot_goals一次克隆、统一unknown、一次commit。

## Tests

2026-10-12缓存真实VM：0/1/128in_flight、备份写/主写/主回读失败。0不写，1/128总2写2提交回读；128原主字节作backup。失败恢复旧内存，完整结构仅status变化，无dispatch。证据evidence/report.json；初始probe保留字错误修正，旧日志保留。

## Commit

本地SHA见最终回复；无push。

## Remaining

Root合入8227、签R5、同fixture GUI验证预算和完整boot。

## Important Boundaries

现有debug CLI总50M指令，无64ms预算；计时含IPC/IO。主回读失败可能主已落盘，备份/旧内存保留。未改Root Main/SDK/包，未Cargo/Kernel/GUI，未编译helper。
