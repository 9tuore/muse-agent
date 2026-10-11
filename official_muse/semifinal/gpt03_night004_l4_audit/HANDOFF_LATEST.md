# Handoff

## Task

GPT03：同候选复验的显式Main SHA契约；基线4db56e，默认c892。

## Result

参数契约20项PASS；原c892的107项归档复核PASS。未来候选运行NOT_TESTED。

## Changed

仅本目录prepare/run参数及文档。--source-sha默认c892，报告记录实参；运行前校验initial/restart的source/executed摘要。

## Tests

默认冻结、显式注释身份fixture、错SHA/坏格式/执行篡改、混用两阶段版本拒绝均通过，拒绝发生在out/子进程之前。无新VM/Mail运行，旧raw/report/parent未改。契约报告见source-sha-contract.json，命令见README。

## Commit

本地提交SHA见最终回复；未push。

## Remaining

Root核对新SHA，用新out重prepare/rerun。restart静态含Calendar启动闭包，当前不调用NativeCreate；未来声明/UI/backend适配边界见README。

## Important Boundaries

旧107项仍属c892；未改Main/SDK/包，未Cargo/Kernel/GUI，不称新候选PASS。
