# Handoff

## Task
邮箱登录简化，codex/muse-ui-global-memory，总控冻结main基线8dc4752。Host基线无Git元数据，以source_provenance.json逐文件SHA标识。

## Result
PASS：隔离Host源码patch、Release、严格ad hoc签名、实际空白登录UI。真实登录WAITING_USER。

## Changed
只改副本mail lib：移除用户名输入，新登录trim邮箱并作为username；保留旧存储、网络、Calendar。交付patch、复现脚本、报告与两张原始截图。总控负责main和最终验收文档。

## Tests
2026-10-03 locked/offline Rust 11通过/0失败/2原测试跳过；Release app-hub构建通过；8495实际Host sheet切换IMAP/POP3通过，截图已查看。setup检查因共享依赖非空失败，日志保留；错误启动ID与TIME_WAIT重试失败已记录。

## Commit
本地提交本目录和MAIL_LOGIN_SIMPLIFICATION.md；未push，提交号见Git日志。

## Remaining
本人真实账号登录；总控已选此冻结Host做0.3.3最终候选其余验收。启动入口launch_host.py，普通模式为独立空账号profile。

## Important Boundaries
Rust为fixture，UI为真实新包+mail_demo。没有凭据输入、登录提交、真实发信、日历写入、权限申请；旧Host/安装版/8401不改。冻结binary f5989ea3…，不得重编覆盖本包。
