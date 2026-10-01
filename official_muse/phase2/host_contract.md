# 当前实机更新：Muse 0.2.8（2026-10-01）

最终真实打包Shell中，三个新模型Goal与23文件正常重启核验通过；Calendar full_access，合成事件create/get/update/get/delete/get通过并清理。Chat指定三轮复测2/3，仍不稳定；真实Mail与邮件→日历同Goal未验收。原版Gate拒calendar，扩展签名check通过；scan自审human-review。最终报告见仓库根目录PHASE2_LIVE_TEST_REPORT.md。以下保留基线、补丁构建过程与历史观察；0.2.1/2/3/7状态不代表最终8。

---

# Phase 2 宿主接口契约（G-03）

状态：Mail 为锁定源码核验；Calendar 为**本地宿主扩展候选**，截至本文尚非原版 API。隔离扩展 Shell、App Hub CLI、Release card-host 已通过离线 locked 编译；Release card-host 和隔离 Release Shell 均真实加载并显示最终四能力 Muse 0.2.1。Shell 中的 `calendar.status` 实际返回 `write_only`，UI 正确声明未具备完整读取权限；未请求系统授权或操作真实事件。Shell 第一条含模型 Goal 与重启恢复、第二条 Goal 通过；第三条 Goal 在写入和读回后遇到脚本回调预算超时，完整多 Goal 回归未通过。锁定基线为 OctoSense `7f962547cd8035ed2bb05962cf7824d8aa33e3a3`、App Hub `e8601b80ce104db2e48208094714bdcffdce6b5a`。App Hub 的 Git 对象已在本机 Cargo 缓存核实；OctoSense 只有无 `.git` 的源码归档，不能把其标签等同于本地已核实的 Git HEAD。补丁和重现说明见 [host_extension/README.md](host_extension/README.md)。

## Mail：已由当前源码核实

宿主在 `crates/shell/src/apps.rs` 注册 `octosense_mail_service`；实现位于 `apps/mail/host-service/src/lib.rs`。应用申请 `mail` capability 后可以调用：

| 方法 | 参数 | 结果与边界 |
| --- | --- | --- |
| `mail.accounts` | `{}` | 本应用获授账号 `[{id,address}]`；账号是宿主作用域 |
| `mail.add_account` | `{}` | 打开宿主自有登录面板；只有面板可提交密码；取消返回错误 |
| `mail.remove_account` | `{account}` | 撤销本应用账号访问；无其他应用使用时才删除账号 |
| `mail.folders` | `{account}` | 文件夹列表，IMAP 支持多文件夹，POP3 只有收件箱 |
| `mail.sync` | `{account,folder?}` | 通过 IMAP/POP3 拉取新邮件，返回 `{new,total}` |
| `mail.list` | `{account,folder?,offset?,limit?}` | 分页，`limit` 被宿主钳在 1–200；返回 `{folder,total,messages:[{id,sender,address,subject,preview,time,unread}]}` |
| `mail.message` | `{account,folder?,message}` | 返回 `{id,sender,address,subject,body,html,attachments,date,time}`，读取会标记已读 |
| `mail.mark_read` | `{account,folder?,message}` | 标记已读 |
| `mail.send` | `{account,to,subject,body}` | 仅单个收件人；返回的 `accepted` 表示 SMTP 服务受理，不等于收件端验证 |

宿主在每次账号操作以 host pump 提供的 `app_id` 核对账号 grant。`mail.message` **未暴露**已解析的 `Reply-To`、`Message-ID`、`References`；底层解析器存过这些头，但目前服务没有返回。`mail.send` 当前没有接收或传递 `In-Reply-To`、`References` 参数，因此只能把它标成“新邮件”，不能声称是原线程回复。若 SMTP `DATA` 后连接中断，结果应记为未知，禁止自动重发。

## Calendar：本地宿主候选接口，已完成系统 CRUD 读回

能力名称拟为精确的 `calendar`；原版 App Hub `KNOWN_CAPABILITIES` 不包含它。只有本地扩展 App Hub Gate 接受并且应用实例获得 `calendar` grant 后，隔离运行时才可调用 `calendar.*`。`ServiceCall.app_id` 必须来自宿主 pump，不从脚本参数接收。EventKit 权限由宿主查询；脚本提供的 `approved`、`permission` 或 `app_id` 字段一律不作为授权。

| 方法 | 当前候选参数 | 当前候选结果 |
| --- | --- | --- |
| `calendar.status` | `{}` | `{permission,calendars:[{id,title,writable}]}`；无完整读取许可时不返回事件/日历内容 |
| `calendar.request_access` | `{}` | macOS 14+ 宿主调用 EventKit `requestFullAccessToEventsWithCompletion`，在 `not_determined` 或 `write_only` 时由本人处理系统授权；返回 `{permission}`；仅走真实 TCC；本轮用户明确授权后由 Agent 点击实际完整访问按钮，不改 TCC 数据库。若结果仍为 `write_only`，本次会话 UI 停止重复请求并引导系统设置。 |
| `calendar.list` | `{calendar_id,start,end,limit?}` | `{calendar_id,start,end,events:[{id,calendar_id,title,start,end,time_zone,location,last_modified,version}],truncated}`；单个日历、区间不超过 31 天、最多 100 项；事件时间按 UTC 字符串返回，原时区另在 `time_zone` |
| `calendar.get` | `{calendar_id,event_id}` | 存在：`{found:true,event:{id,calendar_id,title,start,end,time_zone,location,last_modified,version}}`；精确事件不存在或日历不匹配：`{found:false}`。权限撤销、服务失败仍返回错误，因而删除后读回可区分两者 |
| `calendar.create` | `{calendar_id,title,start,end,time_zone,location?,request_id}` | 仅在宿主确认授权、目标日历可写、时间合法后建非重复、无参会者事件；返回需再 `get` 核验的 `{event_id,version}` |
| `calendar.update` | `{calendar_id,event_id,expected_version,changes,request_id}` | 宿主读当前事件并比较版本，仅允许标题、开始、结束、时区、地点；返回 `{event_id,version}`，应用随后 `get`；当前只允许修改本应用创建的非重复、无参会者事件 |
| `calendar.delete` | `{calendar_id,event_id,expected_version,request_id}` | 宿主核对精确事件及版本后返回 `{deleted:true}`；应用随后 `get` 应报告不存在；当前只允许删除本应用创建的非重复、无参会者事件 |

`start/end` 使用带 UTC 偏移的 RFC 3339 时间字符串（例如 `2026-10-03T14:00:00+08:00`），`time_zone` 使用 IANA 时区 ID（例如 `Asia/Shanghai`）。宿主核对时区与绝对时刻，拒绝结束不晚于开始；不从“明天下午”等相对短语猜日期。`version` 是宿主对 EventKit 事件标识、日历标识、修改时间和可见字段的 JSON 计算的 SHA-256 不透明摘要；只供预期版本并发检查，脚本不得自行生成。日历 ID/事件 ID 来自 EventKit，不是 Muse JSON 中的模拟对象。请求 ID 由应用为单个动作生成并持久化；宿主在动作前写持久化 journal，结果未知时拒绝自动重做，需要人工对账。未来若要支持跨崩溃自动恢复，还须核验 EventKit URL 标记及系统读回。

权限可能为 `not_determined`、`full_access`、`write_only`、`denied`、`restricted`、`unavailable`。本轮的查询/读回/修改/删除要求 `full_access`，`write_only` 不算达标。系统弹窗由真实宿主组件触发，由本人亲自处理；若缺少 macOS usage description 或签名/打包权利，保持 BLOCKED，不能绕过 TCC。应用的确认卡还须独立绑定 `request_id`、日历 ID、事件字段、版本、有效期；宿主能力 grant 和 TCC 不替代用户对具体外部动作的批准。

## 当前验收边界

- 锁定原版：`mail` 已注册；`calendar` 不存在，原版 Gate 应拒绝其 capability。
- 扩展候选：App Hub `calendar` 准入单测通过；Calendar crate 的 3 个离线单测、EventKit 桥语法检查、扩展 Shell 的离线 locked `check`、Debug/Release `build` 均通过。Release card-host 和隔离 Release Shell 均真实显示四能力 Muse 中文主界面；扩展 `hub check --allow-unsigned` 对同一 bundle 为 PASS。最终 Release Shell 已另打含 `NSCalendarsFullAccessUsageDescription` 的隔离 `.app`，本地 ad hoc 签名校验通过；这不代表正式签名或上游接受。运行中的隔离 Shell 已真实响应 `calendar.status`，报告 `write_only`；UI 因此禁用需要完整读取权限的操作。未请求 TCC 升权，系统事件列表/写入、独立日历读回、完整幂等和邮件到日历任务尚未验证。Shell 的第三条 Goal 在结果写入/读回后、状态完成持久化前遭遇脚本回调预算超时；完整多 Goal 链仍 FAIL。Splash 首次启动的 64 ms 样式/脚本共享预算问题另有隔离 Makepad 补丁，两个 VM entry 仍各守原预算；它不改变后续 timer handler 的预算。
- 不读取旧独立版生产数据库，不改已运行 Shell 二进制，不触碰用户现有日历或邮箱。真实账号登录、TCC 和发送由本人完成。

## 2026-10-01 最新成品边界

Muse 0.2.7 成品使用隔离 `.app` 和 App Hub 正常安装。macOS 实际返回 full_access，已列出四个系统日历；只对指定的合成测试事件操作。0.2.3/0.2.5 真实 create/get/update/get/delete/get 完成；0.2.6 创建和修改通过，删除测试编号校验缺口在 0.2.7 修复并独立读回不存在。最终 0.2.7 重复全链的精确结果见根目录 PHASE2_LIVE_TEST_REPORT.md，覆盖上文的历史状态。未触碰真实用户日程。

原版 Gate 仍拒绝 calendar，本地扩展没有获得上游接受。普通新邮件 Host 接口未扩充线程头，真实邮箱登录/本人收件地址/最终发送与投递尚待本人；不能把早期 mail_demo 当真实收发。
