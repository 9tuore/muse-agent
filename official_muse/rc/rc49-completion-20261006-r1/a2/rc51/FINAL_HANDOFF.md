# Handoff

## Task
准确汇总rc51各尺寸实际源码、fixture载荷和Root官方token等价来源，仅更新文档。

## Result
4个尺寸有有效UI fixture PASS；候选产品PARTIAL，旧矮窗r1失败保留。宽窗输入5c182b67，其他3组输入ed4874；不称同字节运行。Root记录官方token均98560且序列相同。

## Changed
仅FINAL_REPORT、FINAL_SUMMARY、FINAL_HANDOFF及哈希清单。列出ordinary=visible-990x539-r2、narrow=visible-412x892-r2；窄实际412×813。

## Tests
本次native运行0。只读旧report、实际fixture主文件及RC51_TOKEN_EQUIVALENCE，重新计算载荷SHA。宽fixture29e2f10e，R2 fixture b39bfc83，完整值见报告。

## Commit
本地精确文件提交，未push。

## Remaining
Root/A4完成最终冷启动及候选收口；本任务不再启动窗口。

## Important Boundaries
token等价不是字节相同，也不替代UI/Host/full-chain。本轮不将旧启动失败归因于mount，不提高产品结论。
