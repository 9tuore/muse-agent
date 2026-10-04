# Muse · OctoSense 脚本应用源码

当前开发候选为 **0.3.19**，稳定基线为 **0.3.16**。本目录是 Muse 在 OctoSense / App Hub 中运行的应用源码与配套开发材料。当前整体验收为 **PARTIAL**；最后冷启动仍触发64ms预算，同一事项完整链尚未通过。

## 官方要求的源码形式

Muse 采用官方的 **OctoScript / Splash script app** 形式，实际程序入口是 [app/bundle/main.splash](app/bundle/main.splash)，由 Makepad 的受限脚本运行环境执行。这个入口包含实际界面、事件处理和状态逻辑。

官方说明：[Script API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md)、[应用包与准入要求](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)。App Hub 提交的是应用的 `bundle/`，完整 GitHub 源码仓库可以另含构建工具、测试和依赖源码。

```text
official_muse/app/
  README.md                    开发与源码入口说明
  AGENTS.md                    官方开发流程说明
  bundle/                      App Hub 的应用包
    main.splash                OctoScript / Splash 主程序
    manifest.json              身份、版本、能力与完整性声明
    listing.json               应用中心展示信息
    assets/icon.svg            图标
    screenshots/01-main.png    展示截图
```

## 各类源码的职责

| 路径 | 职责 | 是否放入应用 bundle |
| --- | --- | --- |
| `app/bundle/main.splash` | 实际参赛脚本应用入口 | 是 |
| `global_memory.splash`、`incoming_mail.splash`、`scheduling.splash` | 开发模块；构建时同步到主入口，不是另一套运行时 | 否 |
| `ui_memory/`、`prelim/tests/` | Python 构建、压缩和测试工具；不会在应用内执行 | 否 |
| `phase2/host_extension/` 及后续宿主补丁目录 | Rust 宿主扩展与框架补丁、对应测试和构建说明 | 否 |
| 仓库根部 `app/` | 保留的旧独立桌面版源码，不是当前参赛应用入口 | 否 |

应用包中没有 Python、Objective-C、Rust、可执行文件或运行数据库。辅助工具使用 Python 不改变应用的 Splash 源码形式；官方开发工具 `tools/octo` 本身也使用 Python。

## 应用运行路径

App Hub 核对 bundle、manifest 和 capability → OctoSense Shell 的 Card runner → Makepad 受限 Splash 环境。AI 对话使用宿主 `model.complete`；账号与密码/授权码由宿主面板处理；存储限制在应用自己的 jail 中。旧独立版不是这个运行路径的依赖。

官方 `model.complete` 是有界单次模型服务，不能称作已经接入完整 octos Agent peer。当前 `manifest.agent` 为 `null`，官方脚本应用允许不声明 agent。

## 仍需明确的准入差异

- **源码语言与目录形式已符合脚本应用形式**；这不表示官方原版已经接纳整个产品。
- 当前 `calendar` capability 与 EventKit 服务依赖本地宿主/准入扩展；必须同时交付补丁、锁定源码和构建环境，不能把扩展 Gate 的通过写成官方原版通过。
- 配套 Mail 后台工作队列、可信框架注册与原生标题渲染属于补丁范围，须保留来源和对应验证。
- 当前 listing 仍有 publisher/support/privacy 的模板值，展示截图也需绑定最终候选更新。当前开发签名不代表正式发布者身份；正式提交流程尚未完成。
- 本人最新要求先同步GitHub：单独同步当前开发源码及脱敏报告，保留PARTIAL；完整二十项和同候选真实外部链全部通过前不创建通过版本Tag或发布应用。历史失败和稳定版本保留。

本轮使用的实际来源、版本和测试边界见仓库根目录 `BUILD_EVIDENCE.json`、`ROUND_ACCEPTANCE.md` 及 `MUSE_HANDOFF/CURRENT_STATE.md`。GitHub 完整源码交付还须逐文件核对 `SOURCE_MANIFEST.json`，排除凭据、私人邮件、生产数据库、模型权重和本机运行资料。
