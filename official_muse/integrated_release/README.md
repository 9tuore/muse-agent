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

启动器使用独立 `Muse Integrated 0.4` 数据目录；可用 MUSE_INTEGRATED_STATE 指定独立试验目录。
首启走普通 App Hub 安装，后续从相同签名入口启动 Muse。既有来源不匹配时回普通更新流程。
包内 Qwen2.5-0.5B 是基础离线回退，不代表强模型工具调用能力；模型配置由宿主原生界面处理。

产品默认继续携带 Qwen，并保留已有 MiniMax 等云端配置。开发团队使用 GPT；产品云端选择与开发模型分别配置。hybrid 模式接线正在实现，尚不宣称持续协同实机通过。

可选 GPT 开发验证包使用 `package_app.py --model-mode gpt`，省略 `--model-source`，不包含或启动
Qwen。双击该包默认走 GPT 入口；未配置时打开真实 `os.ai-providers` Models 面板，
本人选择 OpenAI/GPT 官方路由、输入凭证并保存，退出后重开。启动器不复制任何已有凭证。
`--models` 直接打开该面板，不再先写离线 profile 或启动 Qwen。

`Muse.app/Contents/MacOS/muse-launcher --gpt-check` 只检查包签名/资源与独立目录的
`config.llm` metadata，不读取 `config.env_vars`、不解析 Keychain、不调用网络或写配置。
返回 0 / `GPT_CONFIG_ONLY` 仅代表主提供方及全部回退为官方 OpenAI/GPT 配置；
返回 3 / `GPT_SETUP_REQUIRED` 表示需要本人配置，2 表示数据路径参数错误，1 表示包检查失败。
兼容 API 的本地端点、第三方路由和非 GPT 回退不计通过。已有离线包也可显式 `--gpt`。
子 Host 的 HOME、core、apps、XDG 路径均指向独立目录；已有配置保持原字节。

本机 `python3 official_muse/integrated_release/test_launcher.py -v` 使用真实编译启动器、
临时 ad-hoc 签名包与 stub Host 验证九项启动/保留/隔离行为；不代表最终 Host 的 GUI、
凭证有效性或 GPT 实调通过。2026-10-11 现场默认独立目录无 profile，仍需本人配置。

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
