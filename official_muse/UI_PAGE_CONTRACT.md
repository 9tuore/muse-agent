# 页面纯显示合同（G03，2026-10-03）

状态：适配器及真实 card-host 合成执行探针 PASS（60/60）；产品界面/系统能力/最终候选验收仍由总控完成。本文件与 `ui_page_adapters.splash`、`ui_memory/tests/page*` 为本聊天唯一写入范围。主界面由总控集成，不在此处修改。基线 dd473352 / 0.2.26，共享分支 codex/muse-ui-global-memory。

## 日历接口（供总控立即集成）

`calendar_display_rows(events, view, cursor)`：events 为当前 `calendar.list` 返回的 `calendar_events`；view 仅 `month` / `week` / `agenda`，cursor 为有效 `YYYY-MM-DD`（1900–2100）。不调用 Host、模型、文件或 UI。

返回形状：

```json
{
  "view": "month", "cursor": "2026-10-03", "label": "2026年10月",
  "start": "2026-10-01T00:00:00+08:00", "end": "2026-11-01T00:00:00+08:00",
  "time_zone": "Asia/Shanghai (UTC+08:00)", "error": "", "skipped": 0,
  "rows": [{"date": "2026-09-28", "day": 28, "weekday": 0,
    "outside": true, "events": []}]
}
```

- `start` / `end` 是建议显式查询的范围（end 不包含），并非已查询证明。总控应比较实际成功查询范围/截断状态才显示完整与空闲。
- 月：周一开始，连续42格；`outside` 表示非 cursor 所在月份，必须显示“未查范围”，不可当空闲。推荐仅查询当月，最长31天满足 Host 上限；月格其他月份不附 events。
- 周：cursor 所在周的周一到下周一，7格；outside 恒 false。需要用户显式刷新该周，切换视图/日期本身不查询。
- agenda：cursor 所在月份，只返回传入真实事件实际覆盖的日期；无事件则 rows=[]，不生成示例。`start` / `end` 同月查询范围。
- 每格 `events` 元素为完整原 Host event 对象，保持 id/calendar_id/version/time_zone/start/end 以及所有其他字段。UI可直接交回现有 `calendar_select_event(event)`。本适配器不改写事件。输出用作只读投影；密集跨日事件的相邻日期可能共享同一 events 数组，UI 不得原地编辑此数组。
- 显示时区固定且明确为 Asia/Shanghai / UTC+08:00（本轮用户时区）；带 Z 或 +/-HH:MM 的真实起止时间先换算到此显示时区，跨日事件覆盖每个真实相交日期，end 恰为午夜不占次日。未带 offset 或坏日期拒绝投影并计 skipped。
- `weekday`: 周一0至周日6；`day`: 日数。rows 按日期递增，events 保留传入 Host 顺序（不在渲染中排序）。
- 无效参数返回空rows、非空error，不补入今天或示例事件。

`calendar_display_move(cursor, view, step)`：返回新的 YYYY-MM-DD；month/agenda 前后一个月（短月 clamp 日数），week 前后7天，step 仅 -1/1，其他返回原cursor。无效cursor返回空串。

`calendar_display_time(value)`：value 为 Host 的 RFC3339 start/end，返回 `YYYY-MM-DD HH:MM +08:00`，无效返回空串。界面若只显示时刻可取结果按空格分隔后的第二段；页面须常驻显示时区。不要在标有 UTC+08:00 的视图中直接显示原 event.start 的 Z 时刻。

`calendar_display_today()`：返回 UTC+08:00 当前 YYYY-MM-DD，仅读取 time_now，不发查询。

## 总控接线约束

显示导航可更新 cursor/view 并 redraw；查询按钮才把上述 start/end 写入现有范围输入并走 `calendar_list_events()`。首次进页面、on_render、resize、会话切换不调用 calendar.list/status/request_access/create/update/delete。已授权刷新/原有轮询保留其原入口。

不能把空 events 说成权限就绪。权限 full_access + 已选真实日历 + 对应成功查询范围 + 非 truncated 才能说明查过；write_only 提示“仅写入权限，无法查询”，未授权/未连接给原宿主入口。未知动作结果保留原保护链。

## 能力就绪文案接口

`page_calendar_readiness(enabled, permission, calendar_id)` 返回 `{ready, label}`：enabled=false→“日历未启用”；write_only→“仅写入权限，无法查询”；full_access 无真实日历→“请选择系统日历”；full_access 有目标→“可查询系统日历”；not_determined→“等待系统授权”；denied/restricted→“系统日历访问受限”；其他→“日历暂不可用”。ready 仅表示具备发起读取的前提，不代表已查过、空闲、可写、动作成功。写入仍依赖目标 writable 及原确认链。

`page_mail_readiness(enabled, account_id, connection_verified)` 返回 `{ready, label}`：未启用/无账号/未实际验证连接均 false，文案分别“邮箱未启用”/“请连接邮箱”/“连接待验证”；只有 enabled + 账号 + 真实同步通过才 true/“邮箱已连接”。不推断SMTP投递或收件人收到。

## Host 通知与长期 Goal 审计（只读，区分稳定基线与后续候选）

以下是本地源码确认，未对用户8401或系统通知做 live 操作。Host根目录 `/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/`；OctoSense是无Git元数据的本地源码副本，App Hub当前HEAD为97d75ac，运行探针绑定真实二进制SHA另列。

- 真实系统日历：`OctoSense/apps/calendar/host-service/src/lib.rs` 的 `valid_range` 限制正范围≤31天、limit≤100；`eventkit.m` 的 `eventValue` 返回 id/calendar_id/title/start/end/time_zone/location/last_modified，Rust decorate 再加version。start/end以UTC Z输出；没有all_day字段。适配按数值offset投影，不把 time_zone 名称当日期切片依据，也不臆造全天属性。月42格只是视觉，Host实际推荐查询当月。Host结果可能truncated，空格不代表无冲突。
- Shell内部通知确实存在：`OctoSense/crates/shell/src/glance.rs` 公开 `glance.publish/withdraw/list`；publish的notify=true进入Shell桌面toast/手机shade，点击打开glance面板。`shell/notifications.rs` 的 `ShellNotifications::notify` 和 `shell/src/lib.rs` 的 `WmRequest::Notify` 是Shell内部窗口管理接口。`shell/src/apps.rs::register_host_services` 注册glance及calendar/mail。
- 该通知入口有 `glance` 能力门禁（`OctoSense-App-Hub/crates/app-policy/src/manifest.rs`）；稳定Muse 0.2.26 manifest只有storage/model/mail/calendar，未申请glance，稳定源码没有发布glance；该基线不能调用此服务或显示已开启通知。本页面适配器未新增权限、未调用notify；Shell内部toast不能冒充macOS Notification Center、Dock badge、系统授权或退出后推送。
- **总控后续候选接线（2026-10-03补充，源码已观察、live未验证）：**共享 `app/bundle/manifest.json` 已声明官方已有glance能力；`main.splash::muse_notify(kind)` 调用官方 `glance.publish`，固定card_id为muse-incoming/muse-result，open.app=muse-goals，notify=true。卡片script只展示，通用标题与通知卡不含邮件正文；新来信与非恢复的结果完成入口已接线，重复card_id替换同类卡；后续源码已改用notification_last_incoming / notification_last_result分别记录两类通知时间，同类别30秒内进入notification_pending去重队列，由单次start_timeout到截止后调用notification_flush；muse_notify保留通知关闭与glance未授权守卫。此项由总控写入main/manifest，不属于本页面适配器提交；没有新增macOS权限、Host/native代码。
- **授权与验收仍待完成：**新增glance是App Hub的应用能力，需本人亲自批准最终候选的新授权；没有代为批准。源码接线、manifest声明和现有Shell API均不等于取得用户授权或真实toast投递。状态保持WAITING_USER / NOT_TESTED：最终候选在真实Shell里的发布、合并、点击打开结果及错误反馈需总控分开验收。先前单一notification_last_at会跨类别抑制通知且没有延迟合并；该旧限制的源码已被上述分类时间戳/去重队列替换。当前不同类别不再共用时间戳，同类延迟合并是已实现的代码路径；队列实际触发、关闭/未授权守卫及跨类别投递仍需真实Shell验证，不能仅凭源码计为PASS。不得宣称候选通知PASS，也不得称macOS Notification Center已接通；这项接线不提供退出后Goal调度/系统自启。
- 独立card-host只泵Host services（`OctoSense-App-Hub/crates/card-host/src/host.rs::handle_event`），其源码没有Shell的glance注册/窗口管理通知桥；8483纯函数探针使用storage能力，不能代表集成Shell通知通过。
- 官方Muse `main.splash` 的 `goal_spec/calendar_goal_spec/mail_goal_spec` 都只有user.message触发；稳定0.2.26的notify字段是Spec记录，主脚本未消费为系统通知。`mail_watch_schedule` 通过start_timeout(30.0)在应用进程内轮询。没有发现通用Goal定时器、关闭App后调度、开机自启或后台守护的官方接线；不把系统Kernel的一般能力等同于Muse已接入。
- Goal有真实持久化、revision/run检查、暂停/继续/取消、产物回读与重启恢复。`core_finish_run` 当前会将对应Goal和Run都写为completed，适用现有一次性受限Goal；不能据此展示一个持续目标永久达成或虚构百分比。建议UI说明“本次执行完成”，后台未接入时直接显示真实限制。核心逻辑不在本聊天所有权内，未修改。
- Shell销毁客户端会调用ModuleHost.teardown；`app-peers/src/broker.rs` 也明确关闭App会中断其运行turn。最小化/仅切换页是否保持轮询未单独live验证，不能据源码推断可跨系统退出常驻。旧独立native App的后台能力属于另一运行路径，不能借作官方Muse通过证据。

## 实际测试与失败修复

2026-10-03 01:10–01:11 +08:00，在隔离8483执行本文件对应的真实card-host，合成Host格式事件60/60 PASS。Python datetime作独立日期/时区oracle；没有替代产品算法。范围：月42格/周7天/agenda真实日期、闰年1900/2000/2024、跨年、前后导航短月clamp、UTC/正负/半小时偏移、跨日/午夜end不占次日、fractional seconds、无offset/坏日期/空或倒序事件拒绝、原Host事件所有字段保留、空agenda、nil events、100条单日与100条跨月长事件、readiness、今天时区、重复显示不改输入、纯函数无effectful API、可见时间格式。

初始集中重放、排序、逐格扫描以及密集跨日逐日重复列表均真实触发2,000万指令限制，日志保留在忽略build下；未提高Host预算。最终逐场景回调，直接按相交日期分配；密集投影在日期边界没有改变时复用只读列表，修复后同一60项全部通过。最终函数不排序、不修改事件、不隐藏事件，skipped只指无效时间数据。

复现（用新的output目录，旧证据禁止覆盖）：

```sh
/usr/bin/python3 official_muse/ui_memory/tests/page_calendar_probe.py --port 8483 --output official_muse/app/build/ui-memory-20261003/page-probe-rerun
```

默认output带Asia/Shanghai时间戳。端口已占用会退出，不关闭其他进程。完整结果/运行日志：`official_muse/app/build/ui-memory-20261003/page-probe-final-release/{report.json,runtime.log}`。可提交摘要：`official_muse/ui_memory/tests/page_probe_report.json`。adapter SHA256 `75a9a3bf1117f5c4bf879f2f083cb9eb222a7dc48984cf86f1a2aeaf501a3743`；card-host SHA256 `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`。这是本组件fixture执行通过，不是新的系统日历或最终候选全链通过。

## 本聊天交接（按HANDOFF模板，owned范围内）

Task：G03页面显示与能力现实审计，codex/muse-ui-global-memory，基线dd473352/0.2.26。
Result：适配器FIXTURE PASS；整个候选UI/REGRESSION仍PARTIAL待总控。
Changed：仅ui_page_adapters.splash、UI_PAGE_CONTRACT.md、ui_memory/tests/page_calendar_probe.py、page_probe_report.json。
Tests：上述8483命令真实执行，60/60；fixture events与本机Host运行分开标注。
Commit：本地owned文件提交，交付聊天提供实际提交号；未push。
Remaining：总控须将**最终SHA对应源文件**集成/重新同步到唯一main写者，尤其旧拷贝可能仍有排序/逐格扫描；采用calendar_display_time统一时刻；后续已只读确认CalendarUI两个事件显示入口都调用该函数，统一+08:00文字，但最终可见界面仍待总控验收。新候选截图/尺寸/日历授权与读写回归、OS通知/后台生命周期未在本聊天执行，不得继承旧版PASS。schema迁移/全局记忆不在本聊天范围。
Boundaries：未写main/Host/native/生产数据，未碰旧安装和8401窗口，未外发邮件/写系统日历/新增权限/付费/公开，不使用子智能体。全局MUSE_HANDOFF更新由总控完成，避免越过owned边界。

## 持续监听 Goal：剩余要求与最小接入建议（仅建议，未实现/未测试）

2026-10-03后续只读核对共享main：`approve → core_start_run → finish_result → core_finish_run` 是一次性storage任务；plan_error仅接纳单个storage.write步骤，core_start_run只接纳planned，core_finish_run同时把Goal/Run写completed。pause_task只暂停planned；resume_task恢复为planned并要求再批准；core_cancel_goal拒绝running。mail_watch.enabled/30秒timer真实存在，但mail-watch.json与Goal没有父子关系，来信Activity目前传空goal_id/run_id。不能将这条一次性链重新命名为持续执行已通过。

**最小范围可做“持续监听已选收件箱，仅提醒”。**复用mail_watch的账号同步、seen去重、静默初次基线、alert正文读取与原回复卡；新增一种明确的监听Goal类型和专用批准/Run完成分支，由总控在main真实定义。下述字段/分支是拟新增接口，现有源码尚不存在；不能给普通storage Goal换个标题、写一个DSL触发字段就称后台已接通，也不调用不存在的mail.watch Host服务。

1. 批准卡显示实际账号ID对应可读账号名、INBOX、30秒、持续到暂停/取消、仅查询/应用内或已授权Shell通知；不包含AI自动起草、发信、日历写入。保存固定goal_id、计划version、已批准revision与账号集合后才启动。Goal与批准状态使用现有goals.json/core_commit_goals原子写入并独立回读；mail-watch.json只负责seen/alerts及绑定信息，enabled须从该Goal有效状态派生，不能另有两份各自决定授权的开关。旧用户监听不应因新增UI自动伪造已批准Goal；首次启用这一持续目标需明确批准，迁移保留旧seen/alerts。
2. 同一Goal同一批准revision持续运行。现有core_start_run/core_finish_run的普通路径保持一次性语义；新增监听专用开始/完成处理，用真实core_commit_goals提交：每批真正新来信才生成关联Run，每个alert带父goal_id、plan_revision和run_id，并按account_id:message_id唯一键关联。完成该Run只写Run.completed和结果/Activity，父Goal保持running；不靠把completed Goal重新设planned或重复批准来循环。没有新邮件的空轮询不建Run/不调模型，避免30秒一条耗尽当前128 Run上限。每批结果用唯一run结果路径、明确父Goal与原邮件来源，保存后独立回读；不要覆盖同一固定结果文件冒充历史。达到当前32Goal/128Run/128Action或900KB上限时应显式暂停并说明，不能自动删审计或无限写入。
3. 增加/缩减账号、改变文件夹/间隔或权限范围属于新计划revision，清除旧批准后重批；原core_replan_goal对running的拒绝仍有意义，应先暂停。每轮mail.accounts返回后只同步该已批准账号集合，不能让以后新连接账号自动扩大持续Goal的范围。账号撤销/Host拒绝/状态存储坏则暂停或报错，保留旧证据；来信正文读取同样依赖当前有效账号授权。
4. 所有mail.accounts/sync/list/message异步请求捕获原goal_id、version、运行generation、账号/邮件key；返回前验证Goal仍running、批准revision仍相等、账号仍在授权范围、generation未失效，验证后才能修改seen/alerts、记录Run、通知或记忆。不能依赖当前task/selected_id；换会话、查看另一个Goal不能改变归属。当前sync回调缺少这种Goal/generation检查，scan仅检查enabled/writable：加入绑定时必须补足，不能只在timer入口检查。
5. 暂停/取消立即使持久化generation失效并关闭后续读请求/结果发布；现存Run按明确中断语义收口，保留结果与审计。恢复同一未变化已批准范围可继续，无需再次授予发信/日历权限；取消不能自动复活。running监听Goal需要专用暂停/取消入口，不能直接复用当前拒绝running的core_cancel_goal。
6. 启动先恢复并校验Goal/批准/绑定、mail-watch.json的seen/alerts，再启动现有单timer（mail_watch_timer守卫）。仅恢复同revision的已批准running监听Goal；paused/cancelled/损坏/账号不再授权均不启动。原UNKNOWN/in_flight邮件与日历动作按既有保护继续对账、不重做；保留初次静默基线和已有message去重，不为建Goal清空seen。新的启动generation作废旧回调，Run与结果回读匹配原Goal/run/revision。

**范围上限：**这只能称“应用运行期间持续监听Goal，批准一次覆盖固定读取/提醒范围”。切页和后台失焦不能停止timer，但是否正常工作仍须最终真实运行验证。退出Shell/终止App进程后不会继续执行；未接launchd/daemon、开机自启、系统级计划任务或通用自主Goal调度，不能这样宣传。其它持续Goal类型仍未实现。来信提醒、Run/Goal分离的源码接线及批准/暂停/恢复/重启行为都未在本聊天执行，状态NOT_IMPLEMENTED/NOT_TESTED；本聊天只给出最小方案，不新增功能测试，不改main/core/Host。

后续候选实际归属补充（仅只读源码核对）：日历可视视图投影真实calendar_events，原calendar.list/CRUD/独立calendar.get链保留，不以合成JSON替代系统事件；Goals页新增“持续任务·来信提醒”卡并复用同一mail-watch.json/原30秒loop，普通Goal标“本次任务”，聊天“持续监听邮箱”跳转Goals且不自动启用。本次是持续任务UI接线，未实现上述拟议的监听GoalStore/Run调度分离，不宣称通用持续Goal或退出进程daemon；真实候选链验收由总控记录，本聊天未新增测试。

## 0.3.2最终冻结主源绑定复验（原60项，不扩大范围）

2026-10-03 02:36:23 +08:00，8483原60项FIXTURE全部PASS。冻结main SHA256 `36bcd8703f103abda767280dfb7c3c5f2fa9cf1380c6c59479640ed4494dd126`；主源在字节偏移3244处包含唯一一份完整adapter，提取SHA256为原 `75a9a3bf1117f5c4bf879f2f083cb9eb222a7dc48984cf86f1a2aeaf501a3743`。从保存的最终main快照提取这份生产函数执行原探针/原Python oracle，60个断言未增加或修改；执行后main与adapter哈希仍相同。现场Git HEAD为09e14fb，主源SHA是本次实际执行绑定依据。manifest读取版本0.3.2，SHA `cf0a311c098794a2250b386bef8b59626707c091c22eebcbba29d6a9f3280cc8`。

命令：`/usr/bin/python3 official_muse/ui_memory/tests/page_final_snapshot_probe.py --expected-main-sha 36bcd8703f103abda767280dfb7c3c5f2fa9cf1380c6c59479640ed4494dd126 --port 8483 --output official_muse/app/build/ui-memory-20261003/page-final-032`。旧输出不覆盖；重跑必须选择新目录。owned摘要 `ui_memory/tests/page_final_probe_report.json`，完整真实运行报告与日志 `app/build/ui-memory-20261003/page-final-032/runtime/{report.json,runtime.log}`；同目录保存main-frozen.splash、adapter-from-main.splash和bound-report.json。

这是0.3.2最终主源中日历显示/日期导航/就绪文案函数的合成输入执行通过，测试窗口仍是storage-only fixture宿主，未执行整个最终UI/真实calendar.list/系统CRUD/独立get/通知投递。8401用户窗口、生产数据、main/Host未写入；root负责8411真实Shell的Calendar与通知验收，系统写入需要精确本人确认，不得用本fixture代替其LIVE证据。原page_probe_report.json及失败日志继续保留。
