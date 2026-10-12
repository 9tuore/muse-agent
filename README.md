## 当前交付边界：R5固定保底，0.4.0-rc8候选准备中

NIGHT-004固定R5保底入口是本机 `build/night-004/rc7-integrated-candidate-r5/package/Muse.app`（`0.4.0-rc7`），必须经随包Launcher与配套OctoSense Host打开。它基于官方源码并包含待审修复；R5结论是隔离 `SIMULATION_PASS`，生产 `REAL_E2E_NOT_TESTED`。本轮保留该包和生产资料，不覆盖保底。

SPRINT-005当前可读Main SHA-256为 `947c52915c507f9a7a7a896c554b43f1c1e0a9ec11bee490bed5304d054b642b`。`0.4.0-rc8`准备输出位于本机 `build/sprint005/rc8-main-r1`：stamped readable为 `a5af07e9…`，compact artifact为 `0491807b…`；这是不同构建层，完整身份以Root新冻结回执为准。准备包或catalog序列更新不代表已经安装、通过三轮GUI或正式上架。配套CA测试Host仍由Root独立编译/验收，不继承R5结论。

根目录 [bundle/](bundle/) 保留 `0.3.27-rc17` 历史包（Main `90351cba7ec5c493befb6673212bfb1aa9639dbfbc2ce28b83e24b98f3e05bdc`），旧别名仍指向它；它不是当前rc8候选发布入口。上述build路径是未跟踪的本机构建产物，干净检出需重新准备、签名并同身份验收。后续根发布bundle替换、push/tag或比赛提交均由Root按既有授权单独收口，本说明不执行或授权发布。

当前进展见 [当前状态](MUSE_HANDOFF/CURRENT_STATE.md)，R5历史证据见 [NIGHT-004报告](MUSE_STABILIZATION_20261012_REPORT.md)；[复赛布局与发布边界](docs/semifinal-release-layout.md)及旧版证据保留。

# Muse · 让记忆推动行动

![Muse · 星海队](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/Muse-rc51-cover-v2.png)

**星海队｜中文 AI Agent｜邮件 · 日历 · 全局记忆**

把你想做的事告诉 Muse。它结合当前讨论与相关记忆，帮助你整理计划、处理来信、安排日程，并把行动结果和来源保留下来。切换对话后，相关的全局记忆依然可以继续使用。

[观看中文产品演示](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/Muse-rc51-product-demo.zh-CN.mp4) · [查看封面](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/Muse-rc51-cover-v2.png) · [问题反馈](https://github.com/9tuore/muse-agent/issues)

## Muse 能帮你做什么

| 能力 | 交互 |
| --- | --- |
| 中文对话 | 围绕当前项目讨论，生成计划，并结合相关记忆继续交流 |
| 邮件处理 | 新来信提醒、逐封处理、按意图起草、手写回复、发送前确认 |
| 日历安排 | 查询目标日历、查看日期上的真实事件、创建安排与关联原事件改期 |
| 全局记忆 | 跨对话相关检索，保留来源与资料归属，支持更正、遗忘和冲突处理 |
| 可核对的行动 | 计划、确认、执行结果、独立读回与恢复记录相互关联 |

### 同一事项，可以接着做

一封邮件可以成为日程讨论的来源，后续改期继续关联原事件；回复内容由你决定，发送前单独确认。结果卡保留当前事项的关键内容，让讨论与行动保持连续。

### 新对话，也能接着记

对话负责聚焦当前讨论，全局记忆保存同一用户授权范围内的相关知识。Muse 每轮检索相关资料，保留来源、项目和归属；用户明确纠正或遗忘后，后续检索使用更新后的记录。

### 界面聚焦你正在做的事

- 左侧：聊天历史与邮箱、日历、记忆快捷入口，可折叠。
- 中间：当前讨论与输入。
- 右侧：来信、有效结果与关键动作确认，详情按需展开。

## 官方技术路线

应用使用 **OctoScript / Splash / Makepad**，在 OctoSense 容器中运行。模型通过官方 `model.complete` 调用，存储、权限与系统服务接入 Host；日历配套宿主扩展与依赖锁定源码一并提供。

| 路径 | 内容 |
| --- | --- |
| [bundle/](bundle/) | 唯一官方应用入口、manifest、listing 与资源；旧路径为兼容别名 |
| [official_muse/app/source/main.splash](official_muse/app/source/main.splash) | 可读的 Splash 主界面与应用逻辑 |
| `official_muse/global_memory.splash` | 记忆 DSL 与相关检索 |
| `official_muse/incoming_mail.splash`、`scheduling.splash` | 来信处理、安排与改期 |
| [dependencies.lock.json](dependencies.lock.json)、[sdk-overlays/](sdk-overlays/) | 官方 SDK 固定来源及配套扩展 |
| [scripts/bootstrap_sdk.py](scripts/bootstrap_sdk.py) | 依赖恢复与逐文件核对 |

布局迁移基线：**0.3.27-rc17**。日历仍依赖配套 Host 扩展；A 线后续业务整改不属于本轮目录迁移验收。

## 源码构建

开发环境：macOS、Rust、Apple Command Line Tools、Python 3。

```sh
python3 scripts/bootstrap_sdk.py
python3 scripts/bootstrap_sdk.py --verify
cd vendor/octosense
cargo build --locked --release -p octosense --bin octosense --no-default-features --features app-hub
python3 tools/package_calendar_candidate.py --release --output ../../build/Muse-OctoSense.app
```

以上命令构建既有配套 Shell；本轮未重建或运行 Host。应用提交入口是根 `bundle/`，构建输出、模型和本地资料都在包外。既有 ZIP 与验收记录保留各自历史版本，不代表这次复赛发布。

## 发布前检查

```sh
python3 scripts/check_release_layout.py
```

`.github/workflows/publish-app.yml` 保留仅手动触发的只读布局检查草稿。正式 GitHub publisher 证明要求官方 tag-push 流程；现有本地 rehearsal 签名按原字节保留，尚不能作为该流程的可编辑发布源。审查步骤与未完成项见 [发布布局说明](docs/semifinal-release-layout.md)。

## 新手使用教程

[中文版使用教程](docs/USER_GUIDE.zh-CN.md)：Muse 参赛版打开方式、QQ 邮箱授权码获取、邮箱连接、日历完整授权、模型切换、聊天与记忆、常见报错。

## 技术资料与支持

- [来源与交付说明](SOURCE_DELIVERY.md) · [第三方许可证](THIRD_PARTY_NOTICES.md)
- [运行与验收记录](official_muse/rc/rc49-completion-20261006-r1/REPORT.md) · [测试矩阵](RC_ACCEPTANCE_MATRIX.md)
- [源码清单](SOURCE_MANIFEST.json) · [完整分发核对](official_muse/rc/packaging/rc51-solid-envelope-r2/FINAL_REPORT.md)
- [隐私说明](docs/PRIVACY_POLICY.md) · [Issues 支持入口](https://github.com/9tuore/muse-agent/issues)

**Muse · 星海队**
