# Handoff

## Task

NIGHT-004 ZC01，Kernel denial案例与JSONL桥接联合修补。

## Result

PARTIAL。中央R4实际create/retry/get通过后deny-add失败；R5及bridge R2补丁准备，未typecheck/运行。

## Changed

deny改为官方destructive update并断言新Deny/bytes不变。bridge add需显式fixture once，否则派发前协议拒绝；不造Kernel拒绝。联合/分步patch与协议已更新。

## Tests

读取中央原日志和官方声明：add为act，无强制Host sheet，未观察Deny，不支持遗留Once假设。b9765284到单独R5 3ae543a8、联合fb74bd8e，三个补丁应用/逐字/syn通过；Python语法保持通过。无Cargo/共享写。

## Commit

桥接R1 f64398a0；本单元local commit见Git/聊天；未push。旧失败/R1-R4证据保留。

## Remaining

中央接收联合r2 patch一次编译，并运行新旅程/ignored bridge；GPT02按kernel_bridge/CLI_PROTOCOL.md接VM，之后判L3。

## Important Boundaries

signed公开候选必填；原prompt不替换。计划/手势fixture，History真实且不重建收据。生产gates/风险/schema不变。
