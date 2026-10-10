# 最小合法 Relay 联调入口（只读定位）

2026-10-10。Store签名fixture 10/10不等于正式Relay；中央backend库编译及测试源码类型检查已通过，仍无完整Shell/Relay运行证明。无Cargo/Git/GUI/外发。

|必要项|已核对的真实入口|中央需做/当前缺口|
|---|---|---|
|第三方签名listing与manifest|AppHub Store.install_staged / may_run；Shell host_tools/admission.rs读取已验证catalog及sequence floor|保持ID muse-goals，使用正式publisher/catalog准入；根rc17 manifest当前agent=null、签名为local rehearsal，不能直接拿来证明新Agent请求。生成独立合法Agent候选及listing，根旧包不动|
|宿主工具上限|本轮提案 appstore::host_store → Store::set_agent_tool_offers(app, exact_tools)|默认空；宿主在已验catalog及既有floor后显式配置muse-goals，仅先calendar.events；不能调用system-only setter给Muse。上游未接受|
|本人Agent同意|shell agents.rs::ask → approvals::consent_ask；ShellEnv::consent → consent_granted|从Shell真实本人界面批准/拒绝，不预写consent、不dev grants_all，不用fixture代替|
|代理工具及owner|host_tools/script_apps.rs::from_bundle/install；relay::Catalog::owner_of/may_call|已准入agent.tools请求calendar.events，owner解析为os.calendar；必须加载owner的原shareable声明及执行器，不能自注册Muse为Calendar owner|
|实际service/executor|apps.rs::register_calendar_services注册官方Calendar service；script_apps::install把HostServiceExecutor接入ScriptAppExecutor|需完整Shell的ShellToolHost、peer调用、Event队列/pump、ShellEnv实时双方admission、owner执行器，不只是service直接调用|
|可信输入及逐次审批|relay.rs::trigger_of：只有TurnTrigger::Person映射Person，AppSaysPerson映射App；approvals router处理精确参数与来源|真实Shell surface盖章本人输入，保持参数摘要/来源与原审批；不能用脚本自称Person。先events只读，随后另行安排写入授权|

原Calendar只共享events/add_event/notify；add_event为risk=act，无confirm声明，不能保证逐次本人确认。remove_event虽destructive+confirm:host但owner-only，update同样不共享；本轮不改策略。用户要求的写入确认及共享修改/删除仍需单独合法方案/维护者审阅。

## 已有参考Host的缺口

`build/pivot-builtin-calendar-patched-r5/native` 是card-host衍生，manifest依赖真实appstore与Calendar service，但不依赖octosense-shell。它的原生Calendar UI/组件证据没有ShellToolHost、完整Relay/ShellEnv、agents consent sheet、本人来源盖章或跨应用代理调用证明。`crates/shell/examples/connected-app-host.rs` 是OAuth/connected review示例，不能以名称当作Calendar Relay验收入口。

## 可执行入口建议（只供中央串行，尚未执行）

1. 中央先收完当前完整AppStore/nativeHub check；失败先保留真实错误，成功也只能说明这些库编译。
2. 在已应用统一Hub/Desktop补丁、依赖真实固定的**隔离SDK**，检查真实Shell库：`CARGO_BUILD_JOBS=1 cargo check --offline --manifest-path <隔离SDK>/Cargo.toml -p octosense-shell --lib --no-default-features --features app-hub`。这是含Relay的库检查，不是运行验收；与当前hub-check分开串行。
3. 需要完整本人入口时，使用实际desktop package `octosense`：`CARGO_BUILD_JOBS=1 cargo build --offline --manifest-path <隔离SDK>/Cargo.toml -p octosense --bin octosense --no-default-features --features app-hub`。大构建与GUI须中央另排资源；本任务不执行。
4. 用独立apps root与已验证正式候选，默认空offer应拒绝；宿主显式配置后，真实本人consent允许才可通过原peer→Relay→os.calendar执行器查询。拒绝/撤销consent、撤销offer、错误签名/摘要、非shareable工具都必须拒绝且无写入。先只读，不加重复Store用例。

本清单引用的是现有官方接口与本轮待审host-only补丁，未提供冒用身份或批准绕过。默认空offer尚未启用；正式listing/Agent候选、Shell编译运行、真实consent/Relay/CRUD仍BLOCKED。中央下一步反馈/构建安排不是官方接受。
