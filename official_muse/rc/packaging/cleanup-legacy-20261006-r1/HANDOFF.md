# Handoff

## Task

用户要求清旧版留新版；补清9月旧发行产物，codex/muse-rc-finalization。

## Result

PASS：28.app+17旧ZIP/DMG删除，逻辑1.29GB，测后可用6.95GB。PLAN/CLEANUP逐项记录。

## Changed

仅删除未占用的旧发行包，写本目录记录。源码、证据、用户资料/数据库、Host/Hub/模型及Root8493与新候选保留。

## Tests

Git跟踪/lsof/包内数据库前检，45路径删除后不存在；49 ZIP删除前SHA315d670c复核，删除后497158213bytes仍在。无产品源变动。

## Commit

本目录本地--only提交，不push。

## Remaining

旧Git跟踪dist小样本/开发入口保留；新候选独立启动验证另项，不删49交付包。

## Important Boundaries

空间差值受并发活动影响；清理PASS不等于产品或两Mac复现PASS。
