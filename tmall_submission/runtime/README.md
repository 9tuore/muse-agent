# 配套 OctoSense Agent Runtime

发行 ZIP 由本包构建脚本附带既有 `OctoSense Host.app`、Muse 的签名目录和正常 App Hub mirror。Git 中仅记录 pin、检查脚本与运行说明，不重复提交 Host 二进制或 SDK。

`RUN_MUSE.command` 检查 Host SHA-256、代码签名和 Muse `0.3.26-rc51` bundle 摘要；不修改 Host。首次用 `--test-action launch-apphub` 打开应用中心；安装后用已核对的 `--test-action launch-hub:muse-goals`。该入口继续运行宿主原有目录准入、storage 准备和权限路径。

核对来源：锁定源码 `crates/shell/src/lib.rs` 的 `run_test_actions` / `launch_app_with_args`，`crates/shell/src/apps.rs` 的 `installed_launch_id` / `installed_card_apps`，以及 App Hub `crates/appstore/src/lib.rs` 的 `installed_apps`。没有猜测 `--app` 参数，没有直接复制到已安装目录来绕过 App Hub。

精简包不含本地模型权重，需要用户在官方设置配置 Provider；此前完整 rc51 包仍保留基础离线模型。Runtime 和 Calendar 是配套本地扩展，不宣称官方原版 Calendar 准入通过。摘要与资源清单见 `RUNTIME_LOCK.json`。
