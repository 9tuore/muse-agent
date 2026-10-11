# Handoff

## Task

GPT03：同候选复验的显式Main SHA契约；基线4db56e，默认c892。

## Result

参数契约16项PASS；原c892实际SDK/Main的54项归档复核PASS。未来候选运行NOT_TESTED。

## Changed

仅本目录prepare/run参数及文档。--source-sha默认c892；case/summary用显式实参，启动前校验prepared source/executed摘要。

## Tests

默认冻结、显式替代身份、错SHA/坏格式/篡改执行文件拒绝均通过。替代源只追加注释，是身份fixture；未新运行VM/SDK/Mail。旧raw、report、parent、manifest未改；旧manifest活动文件摘要对照4db56e。报告见source-sha-contract.json，命令见README。

## Commit

本地提交SHA见最终回复；未push。

## Remaining

Root核对实际新Main SHA，以同值重新prepare/run，新out保留旧结果。

## Important Boundaries

未自动抓当前SHA，未改Main/SDK/包，未Cargo/Kernel/GUI。旧54项只属于c892。
