# NIGHT-004 real Kernel Calendar journey

状态：PREPARED；git apply --check、临时副本逐字比对和现有syn::parse_file语法解析PASS。没有编译本测试，没有运行本测试。中央负责唯一Shell/Host构建；不要使用当前旧测试binary宣称本新增测试通过。

中央本次应用NIGHT004_real_kernel_calendar_r2.patch；R1补丁及KERNEL_PATCH_RESULT.json保留旧证据。R2结果与SHA在KERNEL_PATCH_R2_RESULT.json。

NIGHT004_real_kernel_calendar_r2.patch只追加SDK crates/shell/src/host_tools/real_kernel_tests.rs一个测试及其局部闭包，不改Kernel/Calendar业务实现。before/after/patch SHA在KERNEL_PATCH_R2_RESULT.json。该SDK所在项目的Git HEAD不是upstream revision，适用性按文件SHA核对。

精确filter：host_tools::real_kernel_tests::real_kernel_muse_calendar_crud_exact_readback_and_revocation_fixture。中央在当前构建流程中纳入补丁并编译测试binary后，设置OCTOS_SHELL_TEST_KERNEL为已核对的rc6-standalone-r2/Muse.app/Contents/Resources/host-runtime/octos-kernel，运行该filter --exact --nocapture --test-threads=1。固定Kernel SHA为56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270；缺Kernel会失败，不跳过。

旅程使用现有Core/Broker/local mock_agent_llm.py/HostToolHandle/ShellToolHost/pump/script_apps::load/HostServiceExecutor/CalendarService。签名synthetic Muse manifest/catalog声明准确六个Calendar工具，并走真实admission；Fixture sheet_tap只对当前os.calendar、tool、完整args和Muse caller匹配的待审批请求答Once或Deny，无开发者全放行。

断言：model已收到六工具且无shell/read_file；创建完整title/start/end/timezone/location/notes→request_id独立owner读取→同request_id和完整args第二个Kernel turn重试，独立events读取须仅1条且原字段/ID不变→同IDget→deny不写→update完整字段→独立owner回读断言id/request_id保留且六个新字段全匹配→get→stale expected拒绝不写→remove→get absent；实际ContextOp::History调用Kernel session/hydrate，四类tool行须有实际broker receipt且kernel_persisted/owner/caller匹配。没有手工添加History/receipt。签名catalog撤下后旧context新turn必须拒绝且store不变。独立读取使用真实owner handle，而非模型文本判成。

Synthetic bundle不是正式Muse product bundle；localhost模型和consent/手势为fixture；不冒充本人Agent授权、GUI或产品full-chain。失败应保留stdout/stderr，按实际错误修正；原始历史证据不要覆盖。

中央GUI reader为可直接执行的read_calendar.py（shebang+0755已测）；argv1指向CENTRAL/build/night-004/calendar-gui-r1/state/apps/.host，目录需已有FIXTURE_ONLY，stdin/输出协议见CURRENT_STATE.md。read-only binary SHA在READONLY_RESULT.json。helper不建中央目录、不复制DB、不开放写。

2026-10-12 R2最小参数核验：python3 verify_full_fields.py，复用现有owner-service binary七个独立实际调用PASS；重复add reused=true、store bytes不变/event count=1，更新保留id/request_id且新字段全匹配。证据OWNER_FULL_FIELDS_RESULT.json。这是L1参数核验，不是新增Kernel测试运行证据。
