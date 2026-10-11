# Muse 统一候选 0.4.0-rc3

这是统一入口和配套宿主的开发候选。当前不能称正式版验收通过，也没有公开发布。
主源码、全局记忆、多对话、长期事务、邮件和行动链沿用现有实现；不另建 Calendar 或 Mail。

## 构建来源

使用 `build/runtime-closure-full-shell-r1/{sdk,hub}` 的已核验 r8 准备树，
官方 SDK pin 4ccf8e06、Hub pin 95e4831，包含前期待审补丁。
本轮框架变化是 `bounded-source-preparation.patch`：64ms 限额内分段准备源码，
不执行部分应用；宿主主题注册使用现有可信入口，应用执行仍受原限额约束。
Calendar 的三个 INTEGRATED patch 位于 `../semifinal/calendar_integration/`，
然后应用 `muse-cold-launch.patch`。修改前校验 SHA；不能将旧 overlay 整文件覆盖新 SDK。

`build_host.py` 使用官方 `desktop/scripts/package.py` 的资源、路径重映射和打包环境，
离线、锁定依赖、Release 构建，features 为 app-hub、octos-core、app-muse-native-prototype。
中央串行运行 Cargo。`prepare_bundle.py` 从当前主源创建新目录并压缩，保留稳定根 bundle。
`package_app.py` 用显式 Host、Kernel receipt、公开模型和签名镜像输入生成一个 Muse.app。
PACKAGE.json 的 source_host_sha256 是输入 Host，host_sha256 是包内签名后的实际可执行文件；
签名可能改变字节，验收最终运行文件必须使用后者。暂存副本在签名前与输入 SHA 比对。
它只签名 Kernel 的包内副本，再由官方 staging helper 为相同锁定 revision 重建 receipt；
原 Kernel 和 receipt 不改。签名为本机 ad-hoc，不能作为 Developer ID/公证或公开 App Hub 发布。

## 本地签名目录

原版 Hub CLI 保持默认权限上限，拒绝含 calendar.events 的清单；失败证据保留。
`muse_local_catalog.rs` 是本任务的本地 publisher embedding，使用原 Hub gate、packer、
签名和 catalog verifier，只接受 muse-goals 0.4.0-rc3 与本任务固定 publisher。
它只添加配套宿主相同的 events/get_event/add_event/notify 四项上限；
不改验证器、默认 CLI、系统身份或本人 consent，不对其他应用赋权。
本地目录的通过只对这个待审配套宿主有效。

将该文件复制到 Hub `crates/app-hub/examples/muse_local_catalog.rs`，按 SDK 相同打包环境
构建 example。参数为 BUNDLE、NEW_MIRROR、WORKING_KEY、CERTIFICATE_FILE、
ANCHOR_PUBLIC_FILE、SOURCE_COMMIT。只使用本任务新生成的私钥；私钥不是整包输入。
输出目录必须新建，签名清单不得再修改；需要更改时生成新候选。
`muse_calendar_offers.rs` 复制到 Hub `crates/appstore/tests/`，验证真实签名 catalog 的
默认关闭、exact-four、他应用拒绝、撤销、withdrawal、无签名和缺 Muse 条目行为。

## 运行和验收边界

启动器使用独立 `Muse Integrated 0.4` 数据目录；可用 MUSE_INTEGRATED_STATE 指定独立试验目录。
首启走普通 App Hub 安装，后续从相同签名入口启动 Muse。既有来源不匹配时回普通更新流程。
包内 Qwen2.5-0.5B 是基础离线回退，不代表强模型工具调用能力；模型配置由宿主原生界面处理。

产品默认 `package_app.py --model-mode hybrid --model-source ...`，继续携带 Qwen。
运行时接受 Native 注册表的云端主提供方，包括已有 MiniMax，不将其替换成 GPT。
云端主配置缺失时进入真实 Models；此设置入口及 `--models` 均不启动 Qwen、不改 profile。
已有云端主配置时，hybrid 启动本机 loopback 轻量服务，保持到 Host 退出；未配置本地提供方时
云端 profile 原字节保留。只有既存 `local/Qwen2.5-0.5B-Instruct-Q4_0-offline` 回退的端点会
通过系统 plutil 就地更新，云端 primary、其他提供方与凭证字段不改，不解析或迁移 Keychain。
`local-model.json` 给出实际 route_base_url、pid、ready/failed/stopped 与 native_local_selected；
它是服务状态，inference_verified 始终为 false，不能当作模型推理或持续 AI 成功证据。
需要本地 Native 回退时，由本人在仍运行的 Host Models 面板添加 local、上述模型 ID 和实际端点。
此模式不自动添加提供方、不启动付费轮询、不执行邮件或日历动作。旧 `--model-mode offline` 保留。

GPT 开发验证包可选 `package_app.py --model-mode gpt`，省略 `--model-source`，不包含或启动
