## 最新本机独立APP

桌面 `Muse-rc8-正式版-20261012.app` 已实际启动，配套Host为Intel x86_64；嵌入产品提交d550b975，包含邮箱账号移除与多账号入口。保留原正式资料，不含模拟账号/生产数据。正式资料当前已安装仍rc7，App Hub已打开rc8更新权限页；最新模块尚未完成原生Install和GUI验收。24项账号管理定向VM通过仅为fixture，不能称真实邮箱通过。详情见 [当前状态](MUSE_HANDOFF/CURRENT_STATE.md)。

## 当前交付边界：0.4.0-rc8 seq8 本机候选，独立验收尚未完成

最新产品冻结提交 `9a61040c86efbe967b207a058f717733df422391`，可读Main SHA-256 `c09836478cdd5fe58f34634002400ebc517185deb30fe4a29a469705c1ac6bd7`；签名compact Main `58b97a56…`、manifest `8d2f8ee9…`、catalog `b05b01b8…`/seq8。Intel本机候选 `build/sprint005/rc8-candidate-r4/Muse.app` 使用统一WorkBuddy Launcher入口和原配套Host。独立GUI验收包 `build/sprint005/zc05-final-r4/Muse.app` 使用限定双marker/loopback CA的专用测试Host，实际窗口已显示，日历query/create有真实owner回执和独立保存读回；合成模型/账号/数据只计 `SIMULATION_PASS`。

最终三轮尚未完成。官方Mail原生发送要求本人physical activation，自动化被拒绝且SMTP DATA=0，不能称真实发送或自发自收通过。生产资料及R5保底 `build/night-004/rc7-integrated-candidate-r5/package/Muse.app` 保留；新候选未在生产资料中完成安装/整链验收。详细状态见 [当前状态](MUSE_HANDOFF/CURRENT_STATE.md)、[七小时报告](MUSE_SPRINT_20261012_7H_REPORT.md) 和 [独立三轮报告](MUSE_USER_ACCEPTANCE_3ROUNDS_REPORT.md)。

根 [bundle/](bundle/) 保留 `0.3.27-rc17` 历史包；build是未跟踪的本机产物，干净检出需重新准备、签名与验收。正常开发分支同步不等于公开发布或比赛提交。R5历史范围见 [NIGHT-004报告](MUSE_STABILIZATION_20261012_REPORT.md)，不能拼作本候选三轮。

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
