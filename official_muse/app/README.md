# Muse 可读源码与兼容入口

唯一应用包位于仓库根目录 [bundle/](../../bundle/)。本目录的 `bundle` 是相对 symlink `../../bundle`，指向同一个目录；兼容既有调用路径，不保留第二份包。

可读业务源码仍在 [source/main.splash](source/main.splash)，本轮 B 线未修改它。迁移基线为实际活动 **0.3.27-rc17** compact 包，六个文件与资源按原字节迁移，包含现有本地 rehearsal 签名；后续发布需要单独审查新版本、可编辑源和官方 GitHub publisher 流程。

开发规则仍见 [AGENTS.md](AGENTS.md)，根目录布局与当前验证边界见 [复赛发布布局](../../docs/semifinal-release-layout.md)。历史报告保留其固定版本与源路径；当前日历能力仍依赖配套宿主扩展，不视为原版容器验收。
