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

所有入口使用同一个签名 Launcher，argv 中先列 Native，再列 Muse／Models 的 test-action。
SDK 在同一启动循环中处理这两个 action；尚未证明 Native 首屏先绘制完成，不能把参数顺序称作 GUI 时序验证。
默认资料在 `Muse.app` 同级的 `Muse Data`，采用 `shell/`、`apps/`、`kernel/.octos/`、
`rinx/`、`config/`、`data/`、`cache/` 布局；Host 保留调用者 HOME，不设置 MAKEPAD_APP_CONFIG。
默认远程参数为 argv `--remote=9696`，可用 MUSE_INTEGRATED_REMOTE 指定另一个有效端口。
可用 MUSE_INTEGRATED_STATE 指定绝对资料目录；复用已有 WorkBuddy 布局时直接选择其根目录，
不复制或迁移 profile／凭证。此前 `home/octos-home/.octos` 目录保留，不自动迁移。

发布目录的 `launch_muse.sh` 与 `Muse.app` 同级，直接运行即可。GitHub 源码使用同一脚本调用
已生成／解压的成品，路径含空格也支持：

```sh
./official_muse/integrated_release/launch_muse.sh '/absolute/path/Muse.app' --models
```

双击应用、仓库脚本及发布脚本都进入同一 Launcher，沿用包资源验签、Kernel pin、签名镜像与单 Host 锁。
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
Qwen。双击该包默认走 GPT 入口；未配置时打开真实 `os.ai-providers` Models 面板，
本人选择 OpenAI/GPT 官方路由、输入凭证并保存，退出后重开。启动器不复制任何已有凭证。
`--models` 直接打开该面板，不再先写离线 profile 或启动 Qwen。

`Muse.app/Contents/MacOS/muse-launcher --gpt-check` 只检查包签名/资源与独立目录的
`config.llm` metadata，不读取 `config.env_vars`、不解析 Keychain、不调用网络或写配置。
返回 0 / `GPT_CONFIG_ONLY` 仅代表主提供方及全部回退为官方 OpenAI/GPT 配置；
返回 3 / `GPT_SETUP_REQUIRED` 表示需要本人配置，2 表示数据路径参数错误，1 表示包检查失败。
兼容 API 的本地端点、第三方路由和非 GPT 回退不计通过。hybrid 包也可显式 `--gpt`，不会启动
Qwen；MiniMax/混合 profile 会进入设置而非被改写，GPT 验证应使用本人配置的独立 GPT-only state。
子 Host 的 shell、core、apps、XDG 路径指向所选资料目录，HOME 原样继承；云端单独配置保持原字节。

本机 `python3 official_muse/integrated_release/test_launcher.py -v` 使用真实编译启动器、
临时 ad-hoc 签名包、stub Host/本地 health endpoint 验证二十一项启动/保留/路径行为；没有运行
Qwen 推理或云端调用，不代表最终 Host 的 GUI、凭证有效性或实调通过。
新增 WorkBuddy argv/env、相对默认目录、同一脚本入口、锁生命周期及旧日志追加用例；
2026-10-11 最终 21/21 通过，37.664 秒。首轮脚本对比断言未归一化包位置，19/20；已修正。
中央最新真实对照：相同 WorkBuddy 脚本直接从 shell 启动仍黑，原 LaunchServices 实例仍正常。
因此配置移植及 fixture 通过不等于黑屏已修复；中央继续验证同候选的 `.app`／LaunchServices 入口。
2026-10-11 只读 config.llm 元数据确认旧 live-acceptance-003 主提供方为 minimax-cn/MiniMax-M3，
route 省略，Native 注册表默认主机 api.minimaxi.com；新默认独立目录尚无 profile，未迁移凭证。

Calendar 页使用已核实的 session.open → turn.start(trigger:app) → session.history 接口；
持久化当前请求 ID，未知结果不自动重做，不允许新 ID 覆盖旧待核对请求。
显式保留记录后可另写不同事项，旧 ID 仍保留用于对账。输入草稿在重绘后保留，
切换账号不显示旧结果，工具详情默认折叠；模型文本不改变业务成功状态。
官方助手也可从宿主「询问 Muse」/Shift+F8 进入，实际 Muse ID 的首次本人启用不可模拟。
多 Chat 的结构化 model.complete 路径保留。Contained 的应用共享历史没有项目隔离/上游遗忘
契约，不能直接替换全部 Chat，也不向其自动注入私人 Memory。
Calendar 四工具须取得实际授予和相同回合工具结果；正文回复、调用映射和窗口出现均不证明成功。
本页自动安排/改期/行动链回执联动、Muse update/remove、真实 Mail 登录/发送/收件仍须单独验证。
UNKNOWN 只读对账，不自动重发。

实际窄测试在 `evidence/`：model wrapper 六项合成回归与当前函数字节一致性；
VM 准备、streaming、硬限额和 Splash 样式日志保留在 build/muse-integrated-0.4.0-rc1/rc2。
编译、签名、fixture 和最终包业务验收分别记录。核心冻结后才进行同一候选 20 次冷启动。

Calendar 接线与回执19项真实参考VM合成协议检查通过，旧解析失败保留；Mail终态恢复完整异步真实VM37/37通过，首轮预算失败与探针错误保留。最新History配套Host30d4d356完整构建和四工具准入安全测试通过；这些结果不能替代同候选真实Calendar/Mail/模型业务通过。
