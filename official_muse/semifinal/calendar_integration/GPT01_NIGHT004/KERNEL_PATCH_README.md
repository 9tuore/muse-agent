> Bridge conversation/trigger R5（Root R8接入）：真实R7 session.open返回conversation/shared_history=false；2条真实tool row有persisted receipt但无lane。只改test driver两行：open_context→生产无client入口open_conversation；Turn→现场ContextOp::TurnFrom＋公开TurnTrigger::from_args原payload。person仅AppSaysPerson，app为App，未知/自报system_agent为Unknown，不造可信手势。e6036b6f→0426f4db，patch/逐字/full syn/实际生产contract静态PASS，未typecheck/runtime。Main/parent/gate/公开包不变，日志仅只读记SHA。

> Bridge policy registry R4：实际正式包requires host-api-v1隐式要求app_policy.device_consent@1；生产Card/AppStore入口register_policy_runtime_features按原feature guard登记。增量patch调用真实入口并用实际AppManifest::check_host_apis检查全部explicit+implicit：Mail3/runtime.list/device_consent共5项。3c59e9ff→e6036b6f；应用/逐字/full syn及全部requirements静态核对PASS，尚未typecheck/运行。公开signed包/门禁不变；原L3 failure保留。代码commit2d927bde。外部owner CAS helper第二优先。

> GPT01 NIGHT-004 Bridge Host registry R3：中央R5真实Kernel CRUD/Deny/revocation result=PASS（fixture模型/授权，非产品L3）；首次signed public bridge实际失败于缺三项Mail API，原日志保留。自有test-only最小补丁调用生产同源真实MailService::register并检查service/实际supported versions，不注入描述、不改manifest/gates，不调Mail、不访问Secret。fb74bd8e→3c59e9ff，patch replay/逐字/full syn通过；新补丁未typecheck/运行，待中央唯一编译。证据KERNEL_BRIDGE_HOST_REGISTRY_R3_RESULT.json。

# NIGHT-004 real Kernel Calendar journey

R5最新接入：中央R4真实Kernel已完成create/stable retry(1 event)/get，随后deny-add案例实际保存第二event并失败；官方add是act、不强制Host sheet，未观察到Deny决定，不支持遗留Once grant假设。R5只把deny案例改为官方destructive+confirm:host的update，要求新Router Deny和原事件/bytes不变。单独修补NIGHT004_kernel_denial_r5.patch；若同次编译桥接，使用NIGHT004_kernel_and_bridge_r2.patch。b9765284基线→联合fb74bd8e。patch/syn通过，未运行新版本。原失败日志及SHA、全部指纹在KERNEL_DENIAL_AND_BRIDGE_R2_RESULT.json。

状态PARTIAL：中央R2及Answer导入修正已release编译，实际Kernel runtime失败，非skip。已读取run-r2/test.log：os.calendar system bundle未注册，被当作未安装store app，模型收到NO TOOL。R4初始化补丁的应用检查、逐字比对和syn语法解析通过；本聊天未编译运行R4，中央负责重新运行。

R4根因：CalendarService::register只注册服务。App Hub system_apps首次调用才注册编译system packs；system::system_app只读取已有registry。原fixture没有调用factory，script_apps::load(Muse)中的owner ensure_loaded失败只记日志，留下空offer。修补参照已有prepare_news：官方factory找到Calendar pack，真实system::prepare校验digest/policy，显式load os.calendar和签名Muse，再用实际ShellToolHost.declarations断言六工具都有os.calendar owner，最后启动model。

中央当前962b87ec基线应用NIGHT004_real_kernel_calendar_r4_init.patch；原始bc44d2d干净基线使用r4_full.patch。最终源码SHA为0f519651e05a1f3f3f6f31686b5959c212759f34d9a3eb0bb49cf07755538f97。指纹、原失败日志路径与SHA在KERNEL_PATCH_R4_RESULT.json。没有改权限gates、生产实现或工具schema，没有手写tools声明。R1-R3证据保留。

R3修正Answer导入至approvals::sheet::Answer，最终源码SHA962b87eca40b79a4f500aa170c4d882316c0fc851a76b8aaaaeefdfe78f5d7d3，与中央已修正源码一致；R1/R2补丁和结果保留。中央已应用R2并修正此导入，可按该最终SHA核对，不需重复应用。干净bc44d2d基线用NIGHT004_real_kernel_calendar_r3.patch，R3指纹在KERNEL_PATCH_R3_RESULT.json。

NIGHT004_real_kernel_calendar_r2.patch只追加SDK crates/shell/src/host_tools/real_kernel_tests.rs一个测试及其局部闭包，不改Kernel/Calendar业务实现。before/after/patch SHA在KERNEL_PATCH_R2_RESULT.json。该SDK所在项目的Git HEAD不是upstream revision，适用性按文件SHA核对。

精确filter：host_tools::real_kernel_tests::real_kernel_muse_calendar_crud_exact_readback_and_revocation_fixture。中央在当前构建流程中纳入补丁并编译测试binary后，设置OCTOS_SHELL_TEST_KERNEL为已核对的rc6-standalone-r2/Muse.app/Contents/Resources/host-runtime/octos-kernel，运行该filter --exact --nocapture --test-threads=1。固定Kernel SHA为56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270；缺Kernel会失败，不跳过。

旅程使用现有Core/Broker/local mock_agent_llm.py/HostToolHandle/ShellToolHost/pump/script_apps::load/HostServiceExecutor/CalendarService。签名synthetic Muse manifest/catalog声明准确六个Calendar工具，并走真实admission；Fixture sheet_tap只对当前os.calendar、tool、完整args和Muse caller匹配的待审批请求答Once或Deny，无开发者全放行。

断言：model已收到六工具且无shell/read_file；创建完整title/start/end/timezone/location/notes→request_id独立owner读取→同request_id和完整args第二个Kernel turn重试，独立events读取须仅1条且原字段/ID不变→同IDget→deny不写→update完整字段→独立owner回读断言id/request_id保留且六个新字段全匹配→get→stale expected拒绝不写→remove→get absent；实际ContextOp::History调用Kernel session/hydrate，四类tool行须有实际broker receipt且kernel_persisted/owner/caller匹配。没有手工添加History/receipt。签名catalog撤下后旧context新turn必须拒绝且store不变。独立读取使用真实owner handle，而非模型文本判成。

Synthetic bundle不是正式Muse product bundle；localhost模型和consent/手势为fixture；不冒充本人Agent授权、GUI或产品full-chain。失败应保留stdout/stderr，按实际错误修正；原始历史证据不要覆盖。

中央GUI reader为可直接执行的read_calendar.py（shebang+0755已测）；argv1指向CENTRAL/build/night-004/calendar-gui-r1/state/apps/.host，目录需已有FIXTURE_ONLY，stdin/输出协议见CURRENT_STATE.md。read-only binary SHA在READONLY_RESULT.json。helper不建中央目录、不复制DB、不开放写。

2026-10-12 R2最小参数核验：python3 verify_full_fields.py，复用现有owner-service binary七个独立实际调用PASS；重复add reused=true、store bytes不变/event count=1，更新保留id/request_id且新字段全匹配。证据OWNER_FULL_FIELDS_RESULT.json。这是L1参数核验，不是新增Kernel测试运行证据。
