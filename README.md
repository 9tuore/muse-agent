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

当前源码候选：**0.4.0-rc16**。日历通过配套 OctoSense Host 的 Calendar Relay 接入内置 Calendar。

## 当前源码与发布入口

新发布流程仅使用仓库根目录 **`bundle/`**。`official_muse/app/bundle` 是指向它的相对兼容链接，不维护第二份应用包。

- `bundle/main.splash`：当前 rc16 应用入口。
- `official_muse/app/source/main.splash`：对应可读源码。
- `official_muse/integrated_release/`：统一 Host 补丁、Intel 启动器与打包工具。
- [统一构建与启动说明](official_muse/integrated_release/README.md)：沿用已验证的 Muse.app / WorkBuddy 启动路径。

```sh
python3 scripts/check_release_layout.py --for-github-release
python3 scripts/check_current_bundle.py
```

持续事务页围绕项目评审展示：保存目标和偏好，调用模型选择下一步，读取内置日历，整理确认草稿；补充新时间后失效旧计划，更新原日程并恢复同一事务。真实运行和验收记录见 [当前状态](MUSE_HANDOFF/CURRENT_STATE.md)。

根 Bundle 是供正式发布工具准备的可编辑源包；本地 .app 使用另行签名的镜像。代码同步不会自动创建比赛提交或 GitHub Release。正式发布流程见 [发布布局说明](docs/semifinal-release-layout.md)。

## 新手使用教程

[中文版使用教程](docs/USER_GUIDE.zh-CN.md)：Muse 参赛版打开方式、QQ 邮箱授权码获取、邮箱连接、日历完整授权、模型切换、聊天与记忆、常见报错。

## 技术资料与支持

- [来源与交付说明](SOURCE_DELIVERY.md) · [第三方许可证](THIRD_PARTY_NOTICES.md)
- [运行与验收记录](official_muse/rc/rc49-completion-20261006-r1/REPORT.md) · [测试矩阵](RC_ACCEPTANCE_MATRIX.md)
- [源码清单](SOURCE_MANIFEST.json) · [完整分发核对](official_muse/rc/packaging/rc51-solid-envelope-r2/FINAL_REPORT.md)
- [隐私说明](docs/PRIVACY_POLICY.md) · [Issues 支持入口](https://github.com/9tuore/muse-agent/issues)

**Muse · 星海队**
