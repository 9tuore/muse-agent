# Muse · 星海队

Muse 将邮件中的约定、项目记忆、系统日历和回复串成可追溯的一件事。普通聊天使用官方模型服务；外部动作以宿主回执和独立读回为准。

## 当前交付状态

本页随夜间候选收口更新。目前为 **PARTIAL / 开发验收中**，不是正式 App Hub 上架记录。公开稳定版仍为 0.3.25；当前 0.3.26-rc5 在独立分支测试。未冻结候选不进入公开 main，旧 Tag 保留。

最终代码、脚本、宿主、SDK 锁和测试的精确身份以 `MORNING_CHAMPIONSHIP_REPORT.md` 和 `RC_EVIDENCE_INDEX.md` 为准。未生成的报告不代表测试已经执行。

## 看什么

1. `CHAMPIONSHIP_DEMO.md`：2分40秒演示脚本，区分已做和等待本人操作的部分。
2. `RC_ACCEPTANCE_MATRIX.md`：原 T01–T20 的实际门槛；fixture、真实宿主协议和系统动作分别记账。
3. `SOURCE_STRUCTURE_AUDIT.md`：本轮失败定位、最小修复、模块职责和保留限制。
4. `MUSE_CLEANROOM_FINAL.md`：独立实现、官方来源和本地扩展声明。
5. `UPSTREAM_CALENDAR_CONTRIBUTION.md`：宿主 Calendar 接口贡献草稿；没有把本地扩展通过写成上游接受。
6. `MORNING_HUMAN_QUEUE.md`：无人值守期间仍需本人处理的准确缺项。

## 源码与运行路线

- 产品入口：`official_muse/app/source/main.splash`。
- App Hub 交付入口：`official_muse/app/bundle/main.splash`，由可读源码做 token 等价的空白/注释压缩生成。
- 执行：官方 OctoSense / App Hub、Makepad / Splash；模型走已有 `model.complete`。
- `official_muse/global_memory.splash`、`incoming_mail.splash`、`activity_archive.splash`、`storage_io.splash` 等模块通过 `sync_modules.py` 嵌入入口，避免维护两份手写业务。
- 依赖：`dependencies.lock.json` 固定官方 commit；`sdk-overlays/` 提供本地差异，`scripts/bootstrap_sdk.py` 恢复 SDK 并逐树核验。
- 仓库中的 Python 负责构建、隔离测试和历史独立版；官方应用的运行时不是 Python。

本轮受隔离文件摘要和 Calendar EventKit 接口属于声明的本地 SDK/Host 扩展。原 64ms 执行预算、文件上限和权限边界保留。配套扩展 Hub 的 Gate 不等于未修改官方 Hub 的准入结果。

## 可复现检查

从固定 commit 在新目录运行 `official_muse/rc/packaging/clean_room.py`，使用新 SDK 树、Cargo home 和 target。输入只包括 Git 来源、精确 commit、新目录和公开验证公钥；不复制真实邮箱、模型凭据或生产资料。实际构建完成后才标 `CLEAN_BUILD_PASS_LOCAL_EXTENDED_HUB`。

原安装包、用户数据库、旧失败日志和唯一证据都保留。交付不包含私人邮件、生产数据库、凭据、编译缓存或重复运行包。
