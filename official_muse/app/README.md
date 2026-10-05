# Muse 脚本应用

这是 Muse 的实际 OctoSense / App Hub 应用开发目录。

**入口：[bundle/main.splash](bundle/main.splash)。源码语言：OctoScript / Splash。**

`bundle/` 是 App Hub 应用包，包含主程序、`manifest.json`、`listing.json`、图标与展示截图。构建脚本、测试、旧桌面版和 Rust 宿主源码放在包外。不要把仓库根部的 Python 桌面程序当作当前参赛入口。

开发遵循本目录的 [AGENTS.md](AGENTS.md) 和[官方脚本 API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md)。当前能力包括 storage、model、mail、calendar、glance，其中 calendar 依赖本地宿主扩展；原版准入与本地扩展验证须分别报告。

本地修改后按现有构建流程生成候选、重新 stamp/sign/check，再从该候选验证。当前候选 0.3.26-rc48 的二十项回归尚未全部完成，不能将开发 Gate 通过当作正式提交或全链通过。

完整源码分类、官方格式和未完成的准入项见 [../README.md](../README.md)。

可读开发源码在`source/main.splash`；`bundle/main.splash`为同token的实际compact版本。日历局部修复验收见根目录MUSE_CALENDAR_REPAIR_REPORT.md。
