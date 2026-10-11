# Muse → Octos → 内置 Calendar 宿主接线候选

状态：**PROPOSED_NOT_COMPILED_NOT_LIVE**。本聊天没有执行 Cargo、GUI、模型、日历操作、外发或 Git。中央串行审阅/应用/编译；仅生成新 INTEGRATED_* 文件，没有改旧未提交 history.rs、SDK、Hub 或主源。2026-10-11，基线是 build/runtime-closure-full-shell-r1/{hub,sdk} 的实际文件字节，逐文件 SHA 和 patch SHA 在 INTEGRATED_RESULT.json；没有用 HEAD 代替未提交文件校验。

## 立即可应用的三个薄 patch

|文件|应用 cwd|范围|
|---|---|---|
|INTEGRATED_HUB.patch|build/runtime-closure-full-shell-r1/hub|appstore 的宿主内存开关及 exact-four setter；正式 AppHub Backend 接受缓存、验证 sequence floor 后配置；刷新验证/记 floor/成功持久化后配置|
|INTEGRATED_SDK.patch|build/runtime-closure-full-shell-r1/sdk|Shell register_host_services 的 Once 初始化显式启用；每次 script agent admission、Glance admission 在既有 catalog/floor 检查后再配置|
|INTEGRATED_WITNESS.patch|build/runtime-closure-full-shell-r1/sdk|可选，ShellToolHost::tool_call 增加限定 muse-goals→os.calendar 四工具的白名单调用映射；不改执行/授权/结果通道|

依次 HUB → SDK；WITNESS 独立。使用 `/usr/bin/patch -C -p1 -F 0 -i <绝对patch>` 先核对，然后中央再应用。3份都已在本目录 INTEGRATED_PATCHCHECK 内的原字节副本实际完成零 fuzz dry-run、apply、最终逐字节匹配；日志保留。补丁尚未编译，不得称接线实机通过。INTEGRATED_PREPARE.py 是生成记录，已运行过；它拒绝覆盖现有 INTEGRATED_PATCHCHECK，勿原样重跑。

增加的 API 均由补丁定义：`set_muse_calendar_integration_enabled(bool)` 与 `configure_muse_calendar_offers(&mut Store)`。开关在独立 AppStore 默认 false，Shell 的原宿主注册入口显式设为 true，不读取环境/配置文件，不暴露脚本服务，也不写 consent。exact set 仅四项：calendar.events、calendar.get_event、calendar.add_event、calendar.notify。非 Muse、os.*、无 catalog 条目、withdrawn、未认证 manifest 都不会得到这个额外上限；设置仍调用原 `Store::set_agent_tool_offers` 的认证 setter。对不存在/withdrawn Muse 清空旧上限；setter 验签失败先清空再传播错误。

宿主开关 false 在下一次 patched admission/catalog configure 清空共享 Store 配置；它没有设置界面，也不承诺直接切 flag 后已持有 Store 的所有调用立刻变化。中央若测试 ceiling 撤销，应先 false，再调用 configure 清空，再验证 clone/staging/new Store 拒绝，避免只关 flag 就宣称即时撤销。正式用户 Agent 撤销沿用原 Native consent，独立于该 ceiling。

## 精确合法链和保留的缺口

1. `muse-goals` 第三方实际签名/认证 catalog 条目与 bundle digest 必须先通过原 Gate。这个 patch 只增加宿主 ceiling，不能伪造 Hub listing/签名、跳过 GitHub v2 channel、floor、withdrawal、digest 或 install consent。已知根 bundle/manifest.json 是 0.3.27-rc17、agent:null、local rehearsal；本轮没有读取中央新 0.4.0-rc2 manifest，不把旧文件当新候选。中央新候选若仍 agent:null，四工具不会凭 ceiling 自动出现。
2. Muse 的 reviewed manifest `agent.tools` 必须准确申请这四个 dotted 名称；若还含 update/remove，默认上限应拒绝。Agent 选择现有合法 profile，agent.instructions 指向自身已打包指导文本；重新计算 bundle digest 并走真实签名/catalog，不能直接改已安装 manifest。若 UI 通过 contained app 服务发起 turn，还须申请精确四项 capabilities：octos.session.open、octos.session.history、octos.turn.start、octos.turn.interrupt。它们不是 calendar 原始 service capability。现有脚本调用 raw host.request("calendar.*") 仍会被 Calendar 服务拒绝，不能以 capability calendar 假定成功。
3. Shell `host_tools/admission.rs::installed_bundle_with_anchor` 验证 catalog、既有 `check_verified_catalog_floor` 后配置 ceiling，再 `may_run` 校验实际 installed release。`script_apps::from_bundle` 读取 digest-checked AgentBundle；dotted generic_tools 进入 `Loaded.asks`；install 给原 caller grant；owner_for 由 namespace 固定为 os.calendar。`script_apps::load` 在 caller 拿声明前冷装载这些 owner 的合法 system bundle 和执行器。
4. 真实 native consent 对实际 Muse ID 单独有效。`muse-native-prototype` 的既有 consent 不会迁移成 `muse-goals`。本人授权保留 native consent，不预写同意、不使用 dev grants_all、不自动点击 Allow。允许后 Broker/ShellEnv 在实际 turn/call 再检查 admission、consent、account/context。
5. Relay `Catalog::may_call` 要求 owner 的 shareable declaration 与 caller grant。调用者始终 muse-goals，owner 执行器内部 `ServiceCall.app_id=os.calendar` 是 Relay 已授权后的原 owner 执行路径，不能由 Muse直接指定该身份。Calendar `handle` 首行只接受 APP/os.calendar；不要删此检查或改成接受Muse。服务返回通过原 reply queue → schema/size validation → peer/tool/result → Kernel。

**update/remove：**当前 staged tools.json 已包含先前提案的 shareable:true、destructive、confirm:host、auto_approvable:false；这不是新运行时 Muse 授权证据。本 patch 不 offer/grant/调用它们，也不改变声明/Gate/审批。正式 Muse 的改期/删除整链仍有缺口，应保留 owner UI 路径或等待独立明确授权的共享变更，不能借 os.calendar 身份完成。四工具接通不能记作 Muse CRUD 完成。

**冷启动 UI 路径限制：**本候选配置正式 `app-hub-app::Backend` 与 Shell agent/Glance gates。老 `AppStoreView` 与 `CardAppView` 没有调用 configure；正式 Hub Backend 先加载 catalog 会将同一共享配置带到 CardAppView。若中央启动器绕过 Backend 直接冷开 CardAppView，需先让 Shell agent admission 或正式 Backend 完成 authenticated catalog/floor/configure；否则会以 does-not-offer 拒绝。不要在 CardAppView 的未检查 floor 位置强行设置 offer，也不要引入 appstore→app-hub-app 循环依赖。中央必须确认其 launcher 使用的真实路径；本候选不把所有第三方 runner 都声称已覆盖。

## 首轮 result / History 契约

脚本路径（当前 verified `crates/ai-host/src/contained.rs::parse`）只接受：

|service|args|含义|
|---|---|---|
|octos.session.open|{}|自身 scoped context|
|octos.turn.start|{text:非空受限字符串, trigger:"app"}|发起 Muse App turn；不能直接传 tool/args、context_id/session_id/account/owner|
|octos.session.history|{}|同一 scoped context 的合法 History|
|octos.turn.interrupt|{}|停止自身 turn|

`trigger:"person"` 从脚本会变成 AppSaysPerson；不能用它作本人见证。真正 Person 仍来自 Shell Ask composer。App、Person 与 system_agent 回合分别保存 actual context/session/turn；lane=person 同时容纳 App turn，不能由 lane 或用户行的 You 标签判断本人。

首轮先只读：请求模型选 calendar.events，limit=10；Complete 不是工具成功证据。等待实际 Complete 对应 turn，再请求同一 context History。必须接受并展示该回合 role=tool 的真实正文/真实错误，并关联实际 tool_call_id。固定 Kernel b0759a5 的 `model_name=tool.name.replace('.',"_")`：History 可能是 calendar_events/calendar_get_event/calendar_add_event/calendar_notify，而 Relay 名仍 dotted。只接受这四组精确别名；不要普遍做 underscore 归一化。原 own history.rs 仅 events 的未提交候选保持不动，本轮不把它扩成四工具 UI。

Kernel hydrate 当前 turn_id=None、thread_id 来自 Message；仅在 actual mapping 证明该 thread 与刚完成 turn 一致时绑定。双方 turn/thread 同时存在必须一致；缺失/冲突/迟到、另一个 context、错误 lane、tool_call_id 缺失或未知名均显示证据不足。不要取另一回合或 assistant 文本补正文。建议沿用已有 bounded History 原则：最多4096行、正文4096字节、最多4条、总展示8192字节；超过限制保留不足状态，不截断冒充完整结果。

WITNESS 是 **broker_checked_received 元数据，不是授权或执行成功**：仅接收 Broker 已验证 peer/context/generation/account 并 stamped calling_app/client/origin/trigger 的实际新 occurrence，产生 `[muse-calendar-call-map]`。IDs 仅256字节白名单字符，否则标 missing/invalid；account 仅 device/[other]；Incoming不输出from；不记录args正文、事件ID/标题/notes、token/Secret、模型文本或结果正文。仅 events 的 limit 作为整数保留。call_id 与 tool_call_id 是不同字段，不能相等替代。

收据连接：mapping 的 call_id ↔ Host已有 tool-calls.jsonl 同 call_id received→done ok/error/cancelled；mapping 的 session/context/turn/tool_call_id ↔ 同次合法 History role=tool。args_digest 与 Host重新计算值一致。实际参数 limit=10 须取 mapping.limit，不取提示词。只有同回合真实 tool正文和 Host ok 才记工具成功；没有工具记 MODEL_NO_TOOL，有 error 保存实际 error。Shell Ask 的当前 model::Conversation::load_history 仍将 Tool.detail 置为空字符串，这个补丁不改变它；Person 正文展示仍需中央新增严格绑定的 UI 收据或合法 History 读取，不读 Kernel 私有存储。

get_event 参数须恰好一个 id 或 request_id；{found:false,event:null} 仅在该真实 get_event 成功时代表权威不存在，空 events 列表不等价。add_event 使用本人已同意的稳定request_id及完整字段，重试不得新建key；notify 用实际保存的event id，结果card_id才能证明发布调用成功。add_event/notify 现有 risk:act、auto_approvable 默认行为由原Kernel/Shell审批决定，本候选不扩大批准、不假设 consent 等于本次外向批准。

## 错误及撤销见证

|状态|合法见证|不能宣称|
|---|---|---|
|fresh/no consent或本人关闭|actual Agent UI拒绝/状态；若实际call到Relay可为consent_pending；若Broker先拒绝则无call receipt|仅audit为空就PASS；伪造call id|
|wrong owner/grant|真实现有fixture `not_granted`；live只保存自然产生的拒绝|手写call冒充Person/os.calendar|
|withdrawn/digest/floor失败|原Gate错误或Relay app_unavailable；保留actual installed/catalog身份|offer覆盖这些检查|
|账号退出/变化|signed_out 或 Broker `The account changed; reopen this app`|重用旧context|
|context关闭/应用关闭|`This app's assistant access was closed`/`The app was closed`；实际cancelled/interrupt如有|迟到正文作成功|
|invalid args / budget|invalid_args / budget_exceeded，实际回合绑定|自动重试增预算|
|owner未就绪|实际 app_not_running/执行器错误，按当次结果保留|开窗或有声明就算动作成功|

开关/consent关闭后至少测试新的read turn拒绝，且原pending不会再获得成功UI；停用本人通过Native设置，不能改consent.json。已有正在完成的实际副作用不由本薄patch撤销，不把关闭按钮宣称回滚。

## 中央窄验证过滤器（本聊天均未运行）

HUB cwd，已存在的 Store签名fixture：package octosense-app-hub、`--test per_app_offer`；重点 `default_is_closed_and_one_app_offer_does_not_extend_another`、`exact_offer_cannot_admit_a_second_requested_tool`、`offer_refuses_unverified_publisher_and_unsigned_manifests`、`shared_offer_revocation_reaches_clone_staging_independent_and_fresh_store`、`exact_shared_set_replacement_does_not_leak_or_accumulate_tools`。这些验证原setter，不能当新Runtime helper测试。

HUB cwd，package octosense-app-hub-app，精确 filters `catalog::tests::a_failed_withdrawal_save_prevents_replay_across_backend_instances`、`catalog::tests::launch_gate_refuses_the_unsaved_newer_catalog_floor`、`catalog::tests::withdrawal_after_consent_refuses_install_and_open`。确认 floor 未被接线改变。

SDK cwd，package octosense-shell，复用中央完整 feature set：`host_tools::tests::cold_mail_loads_calendar_without_preparing_its_agent`、`host_tools::tests::admitted_mail_calendar_grants_route_to_the_real_calendar_store`、`host_tools::tests::another_apps_agent_needs_a_grant_and_the_system_agent_its_own`、`host_tools::tests::consent_and_a_signed_out_account_refuse_calls`、`host_tools::tests::a_grants_owner_is_the_namespaces_app_never_the_first_declarer`；App Ask `app_chat::tests::the_panel_opens_a_sharing_context_and_sends_person_turns_there`。Mail fixture 只能证Relay原路径，不能冒充Muse live。

新增Runtime helper还需中央的最小实际签名Muse fixture验证：false默认拒绝→true仅exact four请求准入；含update/remove请求仍拒绝；另一ID拒绝；无Muse条目不阻断其余合法app；撤回/无效签名/floor拒绝；false+configure后clone/new Store及下一admission拒绝。未新增或执行这些fixture，不将旧10/10数字挪作新测试。

下一步中央：逐hunk核基线→应用HUB/SDK（WITNESS可选）→确认新Bundle agent/capabilities/catalog身份与冷启动入口→同一个配套Host串行编译及窄fixture→实际本人consent保留后首轮只读Result/History→再按既有批准做四工具业务验收。结构性剩余项：authenticated Muse catalog/manifest、contained UI 从raw服务改走Octos并展示绑定收据、绕过Backend的冷启动接线、Person History正文、Muse update/remove共享权与新候选业务live。当前交付不宣称正式整链完成。

## 最后只读现场复核

生成后复核发现共享Hub/SDK上述6个目标文件已全部与本候选after SHA一致（不是本聊天写入）。请勿重复apply；以INTEGRATED_RESULT.json的source_baselines_after_generation为准。仍无本聊天编译或live验证，中央实际运行结果需另外记录。
