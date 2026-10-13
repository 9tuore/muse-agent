# Muse｜让记忆推动行动

**不止完成任务，更会把事情继续办下去。**

Muse 是以持续行动记忆为核心的个人 AI 工作台。行动链把事务来源、计划变化和执行结果连接起来，让用户看见一件事情如何被持续处理。

- [110 秒产品视频](https://github.com/9tuore/muse-agent/releases/download/v0.4.0-rc23/Muse-Demo-110s.mp4)
- [Intel Mac 应用与源码下载](https://github.com/9tuore/muse-agent/releases/tag/v0.4.0-rc23)
- [作品介绍与三个创新亮点](参赛材料/Muse-最终提交文案.txt)
- [使用教程](参赛材料/Muse-使用教程.txt)

![Muse 视频封面](参赛材料/Muse-视频封面.png)

110 秒视频已加入真实邮件收发、来信处理及内置日历结果截图，并保留跨会话记忆、同一日程改期、行动链和 DSL 的展示。

当前冻结版本：**0.4.0-rc23**。日历可用中文表达事项和开始时间，默认一小时，地点可留空；新时间沿原事项改期。工作台包含对话、全局记忆、邮箱、日历与行动链。

## 运行与构建

下载 Release 中完整的 Intel Mac 应用包并解压，双击 Muse.app。首次启动在应用旁建立独立 `Muse Data`；按界面配置自己的模型和邮箱。

本候选使用配套 OctoSense 宿主，官方基线为 `desktop-v0.1.0-rc.6`，附 Calendar Relay 与 Shell 工作区补丁。准确源码和补丁由 `dependencies.lock.json` 固定。它按原生宿主扩展交付，不声明原版 App Hub 已审核接纳。构建步骤、运行条件见 [原生交付说明](docs/NATIVE_DELIVERY.md)。

```sh
python3 scripts/bootstrap_sdk.py --verify
python3 scripts/check_current_bundle.py
python3 scripts/check_release_layout.py --for-github-release
```

## 源码结构

- `bundle/`：唯一应用发布入口。
- `official_muse/app/source/main.splash`：可读产品源码。
- `official_muse/integrated_release/`：Intel 启动器、宿主补丁与打包脚本。
- `scripts/`：固定依赖恢复与一致性检查。
- `media-tools/`：真实窗口录制、字幕和视频合成工具。
- `参赛材料/`：作品文案、字幕、封面和录制说明；视频通过 Release 分发。
- `CURRENT_STATE.md`：各版本实测范围与证据归属。

本目录从独立源码继续收口；迁移来源见 `SOURCE_ORIGIN.json`。账号、用户资料、私钥和本机构建缓存不进入 Git。第三方组件及许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
