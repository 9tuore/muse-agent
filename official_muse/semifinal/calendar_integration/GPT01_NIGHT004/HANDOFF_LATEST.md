# Handoff

## Task

NIGHT-004 ZC01，codex/gpt01-calendar-history；中央2395a70c/main768e295d。

## Result

PARTIAL。L1真实CalendarService九进程生命周期/重启PASS；真实Relay和审批Router的L2组件fixture六项PASS；只读helper及直接exec PASS；完整字段/稳定request_id重试L1七步PASS。

## Changed

GPT01_NIGHT004隔离harness、来源指纹、原始日志、结果、read_calendar.py。实际SDK业务代码按字节复制，未改共享源码。

## Tests

10-12：owner14.481秒；Relay首轮E0282失败133.729秒保留，修复Arc类型后6/0、22.543秒。nice10/jobs1/offline。只读helper两次读、两层写拒绝，store SHA不变。JSON与对应日志在本目录。

## Commit

首单元30bc0fdc；helper与R1 patch46f3a773；R2本单元本地提交，SHA见Git/聊天；未push。

## Remaining

真实Kernel R2 patch含完整字段/幂等重试；apply check/语法解析PASS，未编译未运行。中央负责正式Host、精确新增filter、隔离GUI及同目录回读。

## Important Boundaries

事件/目录/consent/审批手势为synthetic fixture。无本人Agent同意、GUI或完整Kernel PASS；撤grant证据发生在dispatch前。
