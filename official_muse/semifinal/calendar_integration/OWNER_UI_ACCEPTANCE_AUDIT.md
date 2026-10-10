# Calendar owner UI 合成验收窄审计

本轮只读现场源码，未运行GUI/Cargo，未写共享SDK/私有store/补丁。中央当前唯一Cargo97204继续；服务10/10及test-only默认Confirm严格断言修正为中央报告，不是本任务测试。本审计基于当前文件，不将r3日期界面可见称为冷启动空白已修复。

## 可做：正常owner UI合成CRUD，与Muse Relay分开

已有本人批准合成范围MUSE-N002-20261011-A：2026-10-12 15:00–15:30、Asia/Shanghai、Muse synthetic acceptance；同一事件改16:00–16:30，重启后删除。可在全新隔离home通过官方launcher打开真实Calendar owner及正常控件进行自动化；不以--system重新授予Muse或加载伪造os.calendar bundle，不直接调用handle/host.request、不注入DSL、不读写.host/calendar/events.json。

真实调用链（路径相对完整SDK或其Hub）：
- sdk/apps/calendar/bundle/main.splash:refresh:88：calendar.view，获取month/day/timezone/events/focused；每秒正常刷新。
- edit_new/edit_existing:116/131：e_title/e_date/e_start/e_end_date/e_end/e_zone/e_place/e_notes；已有事件从selected填写。
- save:147–172：正常Save控件，args={title,start,end,timezone,location,notes}；新增add_event，已有selected时update_event+id=selected.id+expected=selected。UI不填写request_id，MUSE-N002标识应用作合成title，不能声称已使用稳定request_id去重。
- remove:182–188：第一次Delete event仅设置delete_pending并改Confirm delete；第二次正常点击才remove_event({id:selected.id,expected:selected})。不点击Show in Glance（notify超出本轮CRUD范围）。
- hub/crates/appstore/src/cardapp.rs:158–180：CardAppView正常事件处理，services::pump(cx,&self.app_id,&self.host_dir,...)；services.rs:471–503从实际card heap创建ServiceCall，app_id来自宿主，不由UI payload伪造。
- sdk/apps/calendar/host-service/src/lib.rs:438–442：CalendarService::call以call.app_id/call.method()/call.args/call.host_dir调用handle；handle仍检查APP=os.calendar。它是官方owner服务，非Muse或Agent调用。

当前CalendarService仅实现family/call，未覆盖api_methods（HostService默认services.rs:272空Vec）；call不检查may_prompt/from_sheet，也不调用Host sheet。services::dispatch:318–340保留sheet身份与已描述ForegroundOnly方法限制，但该Calendar CRUD并非sheet方法。源码未发现这些正常owner UI写路径的可信本人输入门禁；因此授权范围内正常UI自动化可做，不需冒充Person。该结论不是建议绕过审批：若现场实际出现系统权限、consent或Host可信确认，立即停于HUMAN_REQUIRED，由本人完成，不用remote替代。

正常UI可以验证字段显示、变更后重启恢复、两步删除与重启后列表显示；不能仅靠title/time像素证明同ID、完整JSON或权威删除缺席，必须另有合法只读结果。Save返回card_warning时当前代码停留editor，不应为追截图重复Save；保留实际错误/警告。

## 不可做：把自动化当Person或独立精确get

Makepad platform/src/remote.rs:1000明确UntrustedInputGuard，/click与/m是实际定义路由（1808、1995–1997）；--remote只提供调试输入/截图。不可将remote输入、默认不可信事件或Card UI普通Confirm delete描述为trusted Person、Agent审批或Muse Relay成功。Shell首次Native consent仍HUMAN_REQUIRED。

现有owner UI只调用calendar.view/add_event/update_event/remove_event/notify，没有get_event控件或调用，不能凭新增Host方法自行添加隐藏输入/eval入口。完整SDK host_tools::system_call_test（mod.rs:209–239）允许remote /event?data=system-call:<tool> <json>，仅声明risk=read，仍经system_call/Relay授权。ShellEnv::system_tools（mod.rs:663–665）取system_chat::grants::host_tools；grants.rs:188的CALENDAR_TOOLS当前仅events/add_event/notify，get_event不在System grant。relay.rs:673要求System工具在env.system_tools或已有dev grant；不可启dev-grant-all、修改grant或假System/owner。故**独立精确get目前不可通过该入口成功取得**；应记录NOT_GRANTED/HUMAN_REQUIRED对应实际返回，不预造成功状态。

既有合法events System只读入口可在已加载/声明的owner与正常现有grant下返回合成id/字段，用于辅助同ID前后对照；events列表存在limit cap，不能冒称精确get或权威删除缺席。不得为独立读回直接读私有store；旧probe的raw-read/private文件oracle仅是组件fixture，不能移作当前GUI验收。当前批准的写范围也不等于新增System get grant授权。

结论：可以独立做owner UI合成操作/像素与正常列表回读，但当前仅UI路径不能满足完整精确get验收。报告应分别标记OWNER_UI、合法LIST_READBACK与EXACT_GET_BLOCKED，不创造既有产品状态，不将其合并成Muse Relay PASS。

## 隔离与CLI证据

复用NATIVE_PROTOTYPE_HOME.json记录的OCTOSENSE_HOME/OCTOSENSE_APP_DATA/OCTOS_APP_CORE_DIR新子进程路径与现有已核验完整Shell可执行文件、相邻packaged Kernel/receipt；完整Shell不能用CardHost专属--bundle/--app-data/--system。保留实际PID/窗口与remote端口，按/s、/snap、/g抓相同窗口；不启动第二Runtime、不借生产profile/accounts/Settings/旧consent。只给操作与截图工具新home，禁止读取其私有store。本轮不提供执行脚本或运行命令。

## private_data 最小意见（暂不改）

建议新增calendar.get_event声明private_data:true，与当前calendar.events（tools.json:42）一致。精确get返回event完整title/start/end/location/notes/request_id/timezone，语义上含人的私有日历数据，即使当前验收数据全是合成。

Hub app-policy/src/agent.rs:183–187定义private_data结果语义；:406–410对local_only共享工具要求显式false，防止向不能选择模型的caller泄露；不能为了共享把私有日历结果标false。:523的强制true仅在check_host_method对受审SHARED_HOST_METHODS分支，本get为implemented_by=host-service、未声明host_method，所以不能声称当前遗漏true必然导致解析拒绝或该字段自动完成隐私隔离。Shell script_apps.rs:73–96的declaration当前不向kernel复制private_data，该标记也不替代Store/shared准入、真实consent或grant。最小提案仅给get工具增加一行private_data:true；暂不动冻结patch、更新/删除声明或权限。
