# Handoff

## Task

NIGHT-004 ZC01：Calendar 与真实 Relay 的隔离验证。自有 codex/gpt01-calendar-history，中央基线2395a70c。

## Result

PARTIAL。真实 CalendarService::call 九个独立进程生命周期、旧快照/外 owner 拒绝和重启持久化通过。

## Changed

GPT01_NIGHT004 内小型适配器、构建/运行脚本、源码指纹和逐步结果；SDK业务源码未修改。

## Tests

2026-10-12，python3 run_owner.py；nice10/jobs1离线Rust构建14.481秒，九步九进程通过。实际 CalendarService/handle/storage/ui/cards；OWNER_RESULT.json和owner-build.log保存命令、binary SHA、请求及结果。

## Commit

本开发单元本地提交，SHA见Git/聊天；未push。

## Remaining

真实 Relay、授权拒绝与撤销继续验证；中央负责唯一完整Host构建及GUI。

## Important Boundaries

合成事件/隔离目录，Replier/ServiceHost/权限为fixture。没有本人真实Agent consent、GUI或真实外部动作；不以此次PASS冒充官方Agent full-chain。
