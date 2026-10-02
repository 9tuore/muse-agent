# Muse

### 让对话变成可核对的行动

Muse 是一个中文 AI 工作台，把模型对话、多目标管理、来源记忆、活动记录和需要用户确认的邮件 / 日历操作放在同一界面中。用户可以查看计划、确认具体动作，并检查结果和读回记录。

这是 **GOSIM Agentic App 2026** 参赛项目的完整源码仓库，包含桌面版 Muse、运行在 OctoSense 官方容器中的 Splash 应用，以及实际使用的宿主与框架源码。

**当前官方应用：0.2.12 · Phase 2 开发候选 · 总体验收：PARTIAL**

![Muse 在 OctoSense 中运行](evidence/phase2-live/20261001/after/layout/shell-wide-three-columns.png)

*真实 OctoSense 窗口截图；图中为历史 0.2.8 布局参考，最新应用源码为 0.2.12。*

## Muse 的工作方式

1. **对话**：通过宿主的 `model.complete` 服务进行中文 AI 对话，保存会话历史。
2. **建立目标**：把任务组织为 Goal，查看计划、当前状态和运行历史。
3. **确认动作**：批准卡绑定具体计划或外部动作，用户确认后才进入执行路径。
4. **核对结果**：保留结果、错误与独立读回，Activity 记录实际发生的事件。
5. **保留来源**：记忆关联来源，并支持更正、置顶和遗忘。

## 页面与核心功能

| 页面 | 内容 |
| --- | --- |
| 聊天 | 真实模型对话、会话记录、输入与回复状态 |
| 目标 | 多 Goal 列表、详情、计划、批准、结果、验证与历史 |
| 记忆 | 来源信息、更正、置顶、遗忘与真实空状态 |
| 活动 | Goal、模型、批准、存储、读回、恢复与错误事件 |
| 邮箱 | 官方 Host 账户入口、同步读取、正文、草稿和发送确认路径 |
| 日历 | 系统日历权限与查询、事件确认、创建 / 修改 / 删除及独立读回 |
| 能力 | manifest capability、已授予能力及可用状态 |
| 设置 | 应用版本、模型 / provider、存储、权限及关于信息 |

官方应用使用 **OctoScript / Splash、Makepad、App Hub、manifest capability 和宿主存储 / 权限体系**。邮箱复用官方 Host Service；系统日历使用隔离的 EventKit 宿主扩展。

## 最新进度与实际边界

**0.2.12 已通过本机 App Hub 更新安装，并在设置页核对版本。** 最新修复包括邮箱 / 日历控件被 Dock 遮挡、日历读回后事件版本未刷新，以及权限轮询清空错误提示。

| 范围 | 实际结果 |
| --- | --- |
| 模型与 Goal 主链 | 先前 0.2.9 / 0.2.10 候选已在真实容器验证模型、批准、存储、读回和重启恢复 |
| 中文与布局 | 先前候选已验证中文页面、三栏与多个窗口尺寸；0.2.12 补充 Dock 遮挡修复 |
| 真实邮箱 | 已授权并实际同步、读取正文；真实确认发送和收件端核验待完成 |
| 系统日历 | 0.2.11 唯一合成事件创建、修改及各次独立读回通过；删除成功与最终清理待核验 |
| 0.2.12 全量回归 | 尚未完成，不使用旧候选的结果代替 |
| 来信主动结果卡 | 持续监听新邮件并主动弹卡尚未实现 |
| 邮件 → 日历同任务 | 最终完整实机链尚未验收 |

Calendar、Metal、脚本入口等补丁是本地扩展候选，**尚未被官方上游接受**。原版 App Hub Gate 仍拒绝 `calendar`；当前安装环境采用本地 ad hoc 签名。

## 完整代码结构

| 路径 | 内容 |
| --- | --- |
| `app/` | 桌面版 Python / Objective-C 源码、Goal / Memory / Capability、连接器与测试 |
| `official_muse/app/bundle/` | 官方 Splash 应用、manifest、listing 与资源 |
| `official_muse/phase2/` | 状态逻辑、实机测试与宿主补丁 |
| `vendor/octosense/` | 完整隔离宿主源码，含邮件服务、EventKit 和模型历史修复 |
| `vendor/app-hub/` | 配套 App Hub 源码及本地 Calendar 准入扩展 |
| `vendor/makepad/` | 锁定框架源码，含 Splash、Metal 与 storage SHA-256 补丁 |
| `vendor/octoscript-makepad/`、`vendor/octoscript/` | 对应脚本运行时和语言源码 |
| `scripts/`、`miniapp/`、`patches/` | 构建、安装、测试脚本与历史源码补丁 |
| `evidence/` | 合成测试、历史真实窗口与版本对应的验收记录 |
| `MUSE_HANDOFF/` | 当前状态、架构和交接入口 |
| `SOURCE_MANIFEST.json` | 来源提交、版本、文件 SHA-256 与相对依赖链接 |

仓库保留完整源码和必要资源；模型权重、编译缓存、安装包、账户配置、私钥、生产数据库及最新涉及真实资料的截图保留在仓库之外。第三方许可证和来源见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 构建与运行

### 环境

- macOS，Rust 工具链与 Apple Command Line Tools。
- Cargo 外部依赖按 `Cargo.lock` 获取。
- 模型由宿主 profile 配置；本机测试使用无 Key 的 Qwen 服务，权重单独提供。
- `vendor/octosense/.sources/` 使用仓库内部相对链接指向交付的配套源码。

### 构建宿主

```sh
cd vendor/octosense
cargo build --locked --release -p octosense --no-default-features --features app-hub
python3 tools/package_calendar_candidate.py --release --output ../../build/Muse-OctoSense.app
```

### 构建 App Hub 与 card-host

```sh
cd vendor/app-hub
cargo build --locked -p octosense-app-hub --bin hub
cargo build --locked -p octosense-card-host --bin card-host
cd ../..
./vendor/app-hub/target/debug/hub check official_muse/app/bundle --allow-unsigned
```

`--allow-unsigned` 用于源码开发检查。真实安装须经过 App Hub 的 Gate、签名检查和 catalog 流程；不能使用 `dev-grant-all` 替代准入。

打包脚本使用本地 ad hoc 签名。运行时应使用新的 `OCTOSENSE_HOME` / `OCTOSENSE_APP_DATA`；账号凭据只输入官方 Host 面板，邮件发送与日历写入分别确认。

vendor 源码是带明确来源记录的快照；原归档没有 Git 对象，因此不能声称 `tools/setup.py` 的 Git provenance 检查已经通过。详细补丁顺序与构建记录见 [宿主说明](official_muse/phase2/host_extension/README.md)。桌面版入口见 [本地运行说明](README_LOCAL_AGENT.md)。

## 文档入口

- [最新源码交付状态](SOURCE_DELIVERY.md)
- [官方应用说明](official_muse/README.md)
- [Phase 2 最终候选 0.2.9 验收](PHASE2_FINAL_TEST_REPORT.md)
- [中文界面实测记录](MUSE_CHINESE_UI_REPORT.md)
- [历史 0.2.8 实机验收](PHASE2_LIVE_TEST_REPORT.md)
- [当前状态与交接](MUSE_HANDOFF/CURRENT_STATE.md)
- [第三方源码与许可](THIRD_PARTY_NOTICES.md)

各份验收报告只证明其标明的候选版本。后续从最终候选继续 Phase 2 收口；GitHub 源码上传不等于功能全部完成、正式签名发布或主办方 issue 提交。
