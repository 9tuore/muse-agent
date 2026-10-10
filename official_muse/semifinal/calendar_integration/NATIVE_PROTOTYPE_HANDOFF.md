# 独立 Native 原型交接

**GENERATED_NOT_APPLIED_NOT_COMPILED。** 这是可审查的真实 Rust AppModule 实现与官方生成器输出，尚未证明类型检查、链接、GUI 或 Relay 成功。只写本专项目录；中央 SDK/build、主源、Git、Calendar 资料均未修改。

## 交付与身份

- 源码：native-prototype/Cargo.toml、native-prototype/src/lib.rs，集成位置 apps/muse-native-prototype/。
- NATIVE_PROTOTYPE_ENTRY.json 是完整 reviewed registry row。官方 ID 正则 `[a-z][a-z0-9-]*` 接受 muse-native-prototype；service-bus slug 独立使用 muse_native_prototype，符合其 `[a-z0-9_]{1,24}` 正则。
- native-prototype-sdk.patch 添加 workspace member、原型源码、native row，生成 root/Shell/desktop feature 与 native registry/ai-host policy。仅 opt-in app-muse-native-prototype，不加入默认功能；没有自建 Broker、Kernel 或 Runtime。
- native-prototype-hub-reserved.patch 只向原 RESERVED_NAMES **增加**独立 ID，继续拒绝脚本冒用。必须协调使用这一份受审契约，不能删名单或跳过 apps.rs 的既有检查。
- 旧 NATIVE_AGENT_FRAGMENT.json 保留历史内容，标记 SUPERSEDED_UNSAFE_SAME_ID_NOT_REGISTERED。禁止登记 muse-goals；旧片段 tools=[] 不符合官方生成器，新的无自有工具原型用 tools=null。

## 实际入口

模块 create 通过 injection::claim(APP_ID, handles.scope) 接收原 Shell module_host 在首次 consent 门控后提供的 Arc<dyn OctosAppService>。原 ai-host::offer_with → hosted::launch → Broker(CoreConnector::shell()) 使用共享 Kernel；原型依赖 app-peers 的 contract/injection 默认特性，不直接开启 broker/octos-core 或启动进程。

原型无登录账号（accounts=false），仅采用官方 peer_link::DEVICE="device" 的标准设备键。点击读取按钮后，通过注入服务 open_conversation(ContextSpec) 和 ContextOp::TurnFrom 请求模型使用 calendar.events(limit=10)。来源明确为 TurnTrigger::App，没有伪造 Person 或自动批准。按钮是联调入口；模型可能拒绝或未选择工具，Host 接受/完成均不显示“读取成功”。可从原 Shell 的 Ask App 会话及 Relay 记录核对实际工具结果。停止/关闭只关闭实例 context、丢弃迟到结果并 release；不 shutdown 共享 runtime。

唯一跨应用 grant 是 os.calendar/calendar.events；无 generic/own/system tools、文件 workspace、外部文件、网络或进程权限。没有直接读取 Calendar 文件或冒用系统服务身份。配套 native-granted-owner-preparation.patch 在原 Host declarations 路径加载既有 grant owner/executor；该补丁也尚未编译。原 grant/shareable/双方 admission/consent/审批仍决定真实调用。

## 中央集成顺序

1. 对受审隔离 SDK/Hub 核对输入字节与 NATIVE_PROTOTYPE_RESULT.json，再审查应用 SDK、Hub reserved、native owner 补丁。禁止直接应用到共享 .local-state/.sources。中央已有 root 依赖重写可能需对等移植生成的最小差异；不要覆盖统一图和既有 Store 接线。
2. 重新运行官方 native generator 检查及原 Native/reserved 测试；中央在唯一 Cargo target 做 Shell 类型检查和带 opt-in feature 的完整候选构建。源码准备和补丁检查不能替代此步。
3. prepare_isolated_native_home.py 只创建全新目录与 NATIVE_PROTOTYPE_HOME.json 的子进程环境，**不启动**。显式 OCTOS_APP_CORE_DIR 阻止 kernel/dirs.rs 的旧 provider-profile 自动迁移；OCTOSENSE_DEV_MODE=0。不得加 --dev-grant-all、developer-profile，或拷贝旧 consent/个人 Calendar/旧设置。中央须核实实际 Host layout、approval home、kernel core 路径，使用经核验的 Kernel artifact 与授权的 Host 设置。
4. 在真实 Shell 重新取得此 ID 的 consent；首次拒绝无服务，允许后需重新打开实例。先核对冷启动 offered declaration 只有 calendar.events、owner executor 已就绪、拒绝/撤销仍拒绝，再做真实只读选择与结果检查。此原型不提供创建/更新/删除 grant；合成写入仍等待合法原生确认和受审 owner 契约。

Native 是 reviewed Shell 编译分发路线。普通 AppHub 脚本 bundle 后缀/准入门禁未更改，也不支持塞入 native dylib/executable；本补丁不是官方接收、发布或安装包。

## 本次已执行

prepare_native_prototype.py 使用真实官方 validate、main(--no-lock)、main(--check,--no-lock)，exit 0；无 Cargo。SDK/Hub patch 在本目录原始基线副本上 `/usr/bin/patch -C -p1 -F 0` 均 exit 0，未应用到 SDK。两个 Python 脚本 AST parse 通过；fresh home 准备 exit 0。详细输入/输出 SHA 和符号定义路径见 NATIVE_PROTOTYPE_RESULT.json，日志见两份 .patch.check.log。

rustfmt --help 报 stable toolchain 未安装组件；未安装或改工具链。Rust 宏展开/类型检查/链接、系统 pack、完整候选冻结、Kernel receipt、真实 consent、GUI、Agent 工具选择与 Relay/Calendar 结果均未验证。此前纯 projection 7 项与中央 Store/backend 组件证据保留，不能移作此原型执行证据。

后续：中央已应用三补丁；本任务静态引用核对见INTEGRATION_CHECK，一页待执行步骤见NATIVE_READONLY_ACCEPTANCE.md。本人stage/applycheck临时副本已按授权清理，原stage路径作为历史保留；逐文件摘要见TEMP_CLEANUP，日志/patch/失败证据/fresh home保留。仍未构建或运行。
