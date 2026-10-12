# Muse Intel 宿主兼容源码

[English](README.md) | 简体中文

本构建使用官方 OctoSense `desktop-v0.1.0-rc.6`，提交
`f9f6fea90b52182790cb2641fd0145c425af4d84`，及其固定 App Hub
`386359153ed6377b5f047bd9ed2767a6a2ac2bc7`。产物是基于官方源码的
Muse Intel 兼容构建，不是未修改的官方发行包。分发时保留上游
Apache-2.0 许可证及署名。

`sdk.patch` 增加 Calendar 精确读回、唯一事件 ID、不可读事件存储拒绝处理、有界
Broker 回执和明确共享的日历工具。`app-hub.patch` 将已有的已认证
单应用工具上限移植到当前 Store。最新目录与共享组件实现、Bundle
校验、账号范围、本人授权和原生写入审批保持；不包含模拟或原型日历执行器。

`prepare_official_host.py` 要求两个源码版本精确匹配，拒绝混入其他
未提交改动。它应用两个补丁，或核对已经应用的补丁逐字节一致。
补丁包含对应锁文件：只有五个 App Hub 包由固定 Git 来源改为相同
版本的 `.sources` 补丁源码；Calendar 使用工作区已锁定的 UUID 生成
事件 ID，避免同一时钟刻度内删除后重用身份。旧事件仍可读，锁定依赖版本不变。

SDK 补丁同时将已有 `bounded-source-preparation.patch` 叠加到官方
Makepad 运行时补丁。准备脚本核对原始补丁树与完成后的树，构建器拒绝
漏接该修复；先运行 SDK 的 `python3 tools/setup.py --no-hub`，再进行 Muse 准备。
大于 64 KiB 的页面按每帧 1 KiB 预解析，全部完成后执行一次，
修复实际 600,409 字节 Muse 首次启动超时。日常回调 64 ms 限额不变，
Kernel 源码及配对二进制不变。

SDK 检出必须包含官方 `.cargo` 目录。其中的桌面系统应用配置负责
嵌入 Mail、Calendar 等内置应用；漏掉它会生成没有这些应用的宿主。
构建器会核对配置身份，并在回执中记录系统应用列表。

`build_official_host.py` 提供 `check`、`host`、`kernel`、`hub` 和
`tests`、`startup-tests` 阶段。它使用官方打包参数、移除调试数据、重映射构建路径，
采用隔离 target，记录源码、补丁、锁文件身份、命令、日志和产物哈希。
Host 只构建 `app-hub,octos-core`，链接真实 Mail 和 Calendar 服务。
Kernel 从 SDK 自身 octos pin 构建，并由上游 staging helper 核验。
Hub CLI 使用相同的补丁依赖图。

本机实际构建回执和完整日志保留在指定构建目录。编译成功标记为
`BUILT_NOT_RUNTIME_VERIFIED`，不等于 GUI、真实邮箱或日历外部操作验收。
服务、Broker 和认证工具上限测试采用隔离合成数据。最终 Muse Bundle
仍须在实际宿主中安装并验收。
