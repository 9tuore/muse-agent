> L4 parent R3: Root actual cdb141 R2 passed retry/restart and both destructive Deny cases. Actual Stop/pending-terminal/approval-cancelled match turn 9266a3df; parent then failed in a concurrent JSONL read before reconciliation. R3 reads only LF-completed bytes, defers unfinished tails, rejects malformed complete JSON/UTF-8, and saves the original traceback. Cancellation proof now requires one actual started ID plus matching Stop ID/lane and interrupted terminal; completion races remain NOT_TESTED. Original R2 logs are read-only and unchanged; 23 local framing/replay checks PASS. No new Kernel/Cargo/SDK/Main/model/History changes. Root must rerun with its existing R8 binary; all five live cases are not yet complete.

> L4 parent R2：真实R1 stable/restart已PASS；Deny实际在Kernel native HostApproval执行前发生，hostappr UID＋handled_by_host/decided deny＋原persisted tool row，不存在未执行HostToolCall的broker receipt。parent原错用hosttool执行阶段链。R2严格绑定native approval/turn/session/toolcall/typedargs/审计/fixture/原row，已执行工具bound_receipt逐字不变；真实原日志离线回放＋4缺证据拒绝PASS，原store SHA/count1核对不变。--main-sha256必填，cfg/bundle/ready精确一致，版本取真实signed manifest。未启动Kernel/改SDK/driver/Main。最终Main重打包需同最终manifest新withdrawal公开catalog。

> Bridge L4 parent已准备：kernel_bridge/run_l4_bridge.py仅供Root执行，冻结Main643009/testsource0426/实际R8 testbin SHA必填。5必要case：同request重试/重启、真实update/remove Host sheet Deny、真实interrupt＋只读Kernel/owner对账、签名caller withdrawal。匹配hosttool:call_id审计与persisted declined/真实lane；竞态NOT_TESTED，缺同anchor更高sequence公开撤销catalog只能PARTIAL。Python compile/AST/help/JSON及实际contract静态PASS；未启动Kernel/GUI/中央build/state写入。driver未改，旧证据保留。

> Bridge conversation/trigger R5（Root R8接入）：真实R7 session.open返回conversation/shared_history=false；2条真实tool row有persisted receipt但无lane。只改test driver两行：open_context→生产无client入口open_conversation；Turn→现场ContextOp::TurnFrom＋公开TurnTrigger::from_args原payload。person仅AppSaysPerson，app为App，未知/自报system_agent为Unknown，不造可信手势。e6036b6f→0426f4db，patch/逐字/full syn/实际生产contract静态PASS，未typecheck/runtime。Main/parent/gate/公开包不变，日志仅只读记SHA。

> 外部owner CAS受限helper已准备并本机验证：独立gpt01-night004-external-owner/脚本只接受指定fixture_root→apps/.host、双FIXTURE_ONLY及绑定host/event_id/request_id的写marker；真实CalendarService update_event，不手写store/History。自有小build1.38秒，12实际步骤PASS，6guard、只读preflight、外进程更新、真实stale CAS拒绝后新事件保留。binary e7dc8908，旧reader b603e254未变。中央store/full-chain未运行；协议EXTERNAL_OWNER_PROTOCOL.md，实际执行留总控。GPT02同步文案备妥，待本人直接发送授权。

> Bridge policy registry R4：实际正式包requires host-api-v1隐式要求app_policy.device_consent@1；生产Card/AppStore入口register_policy_runtime_features按原feature guard登记。增量patch调用真实入口并用实际AppManifest::check_host_apis检查全部explicit+implicit：Mail3/runtime.list/device_consent共5项。3c59e9ff→e6036b6f；应用/逐字/full syn及全部requirements静态核对PASS，尚未typecheck/运行。公开signed包/门禁不变；原L3 failure保留。代码commit2d927bde。外部owner CAS helper第二优先。

> History/异步准备已补：kernel_bridge/BRIDGE_HISTORY_ASYNC_PREP.md，9条JSON请求解析/唯一ID通过，仅PREPARED_NOT_RUN。原始历史/重启当前context与RAM receipt边界、同步archive只能idle、interrupt竞态和180秒unknown均据实际源码说明；无driver改动/新build/运行。

> GPT01 NIGHT-004 Bridge Host registry R3：中央R5真实Kernel CRUD/Deny/revocation result=PASS（fixture模型/授权，非产品L3）；首次signed public bridge实际失败于缺三项Mail API，原日志保留。自有test-only最小补丁调用生产同源真实MailService::register并检查service/实际supported versions，不注入描述、不改manifest/gates，不调Mail、不访问Secret。fb74bd8e→3c59e9ff，patch replay/逐字/full syn通过；新补丁未typecheck/运行，待中央唯一编译。证据KERNEL_BRIDGE_HOST_REGISTRY_R3_RESULT.json。

> R5 denial与Bridge R2联合单元：已读中央R4真实失败日志，create/stable retry/get确实经Kernel保存；deny add无sheet仍保存第二条。官方add是act且无Host确认，未见遗留Once证据。只把deny改为真实destructive update并核对新Deny/原事件不变；bridge未获显式fixture once的add在dispatch前报协议错，不能叫Kernel Deny。b9765284到联合fb74bd8e，patch/完整syn通过，未typecheck/运行。联合补丁便于中央一次编译；R1原证据保留。

> Kernel JSONL桥接补丁（2026-10-12）：ignored test-only driver及Python协议wrapper/local plan model已准备；只读当前R4 Debug修正基线b9765284，append后25afb61a。实际signed public Muse bundle/mirror/main SHA必填，官方Calendar factory/admission、真实Broker/Relay/Kernel History；原VM prompt不替换，tool plan/审批为fixture。异步turn/interrupt与owner诊断、实际历史session回读/quit；不重建RAM收据。patch/完整Rust syn/Python语法通过；尚未typecheck/运行，无共享写/大build。协议kernel_bridge/CLI_PROTOCOL.md。

> Kernel R4（2026-10-12）：中央R2及import修正release实际runtime FAILED，非skip。已读原日志并记SHA；CalendarService已注册但官方system pack registry未初始化，owner lazy load只log错误。自有R4使用官方factory、真实system::prepare、显式owner/Muse加载及六工具preflight。267f5f16已提交补丁；当前962b87ec用r4_init.patch，最终0f519651；应用检查/逐字比对/syn通过，未编译运行R4。未写共享SDK/target。L4单元d9e99025保持已提交。文档更新脚本UTF-8读取失败后改用文件补丁补齐交接，代码不受影响。

> JSONL/L4单元（2026-10-12）：真实Relay/Schema/审批Router/CalendarService JSONL helper已建成，自有小target增量9.75秒+3.03秒。写/读只接受自有或中央build/night-004内已有FIXTURE_ONLY根；协议CLI_PROTOCOL.md。L4_RESULT.json首轮25步PASS（3次helper进程）：外部真实owner-service修改、stale expected、审批后撤grant、deny/缺consent/撤下、坏输入与坏存储JSON、实际文件写失败/恢复、重启稳定request_id无重复、删后重启无记录。最终event count=0，稳定重试count=1。权限/账号/手势均fixture；没有KernelHistory/Muse receipt。首编译E0277/E0382日志保留，修正后通过。Kernel R3只同步中央发现的Answer导入错误，最终SDK文件SHA962b87ec…匹配；运行仍由中央核验。

> R2（2026-10-12）：中央接入NIGHT004_real_kernel_calendar_r2.patch，完整end/location/notes与同稳定request_id重试已纳入；创建和更新六字段、id/request_id与存储event count=1均有断言。实际owner binary七步参数核验PASS（OWNER_FULL_FIELDS_RESULT.json）；R2 apply check/逐字比对/syn解析PASS，未编译未运行Kernel。R1补丁/结果保留。只读reader已在46f3a773交付，路径/权限未变。

# NIGHT-004 ZC01

2026-10-12：中央基线2395a70c/main SHA768e295d。首单元30bc0fdc，L1真实CalendarService九个独立进程完成创建、同ID回读/更新、旧expected与外owner拒绝、删除、不存在和重启持久化；OWNER_RESULT.json和owner-build.log保持原样。

真实Relay/Schema/审批Router组件fixture：RELAY_ATTEMPT2.json/raw relay-attempt2.log记录6通过0失败，nice10/jobs1、22.543秒。包含owner生命周期、错误caller/owner/system、缺consent/签出、owner/caller撤下、审批拒绝/dispatch前撤grant、缺expected拒绝。第一次编译E0282真实失败（133.729秒）与日志保留，修正局部Arc类型后重试。审批sheet手势/consent/catalog为synthetic fixture，不是本人真实同意；此项为L2组件证据，无Kernel。

只读helper read_calendar.py兼容中央runner：argv[1]=CENTRAL/build/night-004/calendar-gui-r1/state/apps/.host，stdin={owner:os.calendar,method:events|get_event,args:{...}}，stdout={fixture_authorization,process_id,result:{ok,data|error}}。root必须已标FIXTURE_ONLY；Rust guard只接受gpt01-night004-*临时根或中央build/night-004内的canonical目录；只开放读方法。READONLY_RESULT.json：两次真实读及Python/Rust两层写拒绝PASS，事件文件SHA不变。重新构建binary SHA见该证据。GUI/root具体接入待中央验证。

状态PARTIAL：真实Kernel+局部模型fixture的签名Muse→Calendar旅程补丁已准备；patch check/逐字比对/现有syn语法解析PASS，本测试未编译未运行，待中央唯一完整Host构建。新增精确filter/命令协议见KERNEL_PATCH_README.md。reader已加shebang/0755，中央runner直接exec协议实测PASS。无共享SDK/main/bundle/target写入、无生产资料、无费用或外部动作。
