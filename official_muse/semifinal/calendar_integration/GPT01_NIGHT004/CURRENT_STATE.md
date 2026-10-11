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
