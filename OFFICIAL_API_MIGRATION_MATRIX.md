## 最新补充 / 2026-10-11 06:41

完整待审配套Desktop r8实际构建运行，内置os.calendar正常owner UI创建、原ID改期、实际重启、删除已完成，固定System events全字段有界读回与缺席成立。精确get仍NOT_GRANTED、权威不存在及Muse自身Agent Relay未通过；本人首次consent仍HUMAN_REQUIRED。不是EventKit/device_calendar，也未冒用身份、增加System grants或改准入。官方Mail原生中文QQ登录UI通过，真实账号/审阅/投递仍待本人动作。当前证据与完整身份统一见MUSE_RUNTIME_CLOSURE_20261011_REPORT.md；以下旧记录保留，不能拼接为最新全链PASS。

# Muse 官方接口迁移审计

审计基线：Muse `9b247c89` → 布局集成 `062c1028`，`muse-goals / 0.3.27-rc17`。只读源 `official_muse/app/source/main.splash`；活动包为根 `bundle/`，旧路径是相对符号链接。旧 Python 桌面应用不是此 Splash 入口的运行依赖，未按文件名删除。

官方源码固定点：OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654`；App Hub `18cd41d91b326db199fbed4129484a9ba1a8c63d`。Host API 契约 1.10.0。源码存在不代表已安装宿主或发行版可用。现有测试 Host `276b2b68` 仍属旧配套扩展。

| 功能 | 当前实现与入口 | 官方对应接口 | 目标宿主状态 / 商店条件 | 权限 | 重复实现 / 风险 | 策略与验收 |
|---|---|---|---|---|---|---|
| 能力发现 | 原来只读 `host.capabilities()`，无方法发现 | `runtime.list`、`runtime.describe`，契约 1.10.0 | 新源码支持；旧测试 Host 未证实；须 `host-api-v1` | runtime + manifest 方法声明 | 缺少探测，高 | 实现统一发现，严格ABI1（2不兼容）；候选准备器补runtime与host-api-v1、runtime.list/compose/status/review@1必需声明；当前原生新Host待补 |
| 邮箱账号/登录 | `mail_accounts_load / mail_add_account / mail_watch_poll` → `host.request` | `mail.accounts / mail.add_account` | 官方已有；账号是否可用单独查询 | mail、本人登录、宿主凭据库 | Muse 无生产 IMAP/SMTP，低 | 保留，不复制凭据、不另写连接器 |
| 邮箱同步和读信 | `mail_watch_sync / mail_watch_scan / mail_watch_prepare / mail_read_body / mail_open` | `mail.sync / mail.folders / mail.list / mail.message` | 官方已有；需账号授权和同步 | mail、账号 grant | Muse 循环和逐信关联是业务，中 | 保留去重、来源、逐封结果；受理与收件独立核验 |
| 邮件草稿和发送 | `mail_send_step` 原调用 `mail.send`，本地草稿保留用户原文 | `mail.compose / mail.compose_status / mail.review_send` | 新官方源码支持；RC1 不含新公开 composer；原生 foreground review | mail、账号、宿主真实输入确认 | 旧通道不合适，高 | 切换官方 compose + 宿主审阅，持久化 compose ID/revision；UNKNOWN 只读对账；禁止旧 send 回退 |
| 官方内置日历（本轮唯一默认） | 历史 `calendar_*` 事务、来源和回执保留；旧自备 EventKit 调用已隔离 | `os.calendar` 的 `calendar.events / calendar.add_event / calendar.notify` 经官方 App-Agent relay | SYSTEM_APP_ONLY，Muse 不能直接调用；三项共享工具由官方 grant/relay 路由；当前 Native Host 未实测 | octos.*、agent.tools、本人 Agent consent、宿主审批 | 原自备桥退出新候选，风险高 | 用户明确选择内置日历；生产源码已阻止私有桥，当前联动 BLOCKED，待真实 relay；历史身份不改 |
| 内置日历改期/删除/精确不存在核验 | 历史原事件关联、去重与 UNKNOWN 记录保留 | 官方存在 `calendar.update_event / calendar.remove_event`；无 calendar.get | update/remove 当前未 shareable；普通 Muse Agent 无跨应用调用路径；events 有 200 条上限，无分页保证 | 官方 relay 策略及可信批准 | 接口缺项，高 | 准备最小复现和上游反馈；禁止删除重建冒充改期，禁止空列表冒充删除核验 |
| 官方系统日历研究（不在默认运行链） | `research/official-device-calendar/adapter.patch` | `device_calendar.*@1`，契约 1.10.0 | 最新 Shell 源码包含适配器；当前参考 Host 未实现验证；区别于内置 Calendar | device_calendar、平台适配器、OS grant、scoped handle/revision | 独立研究 | 真实 Splash VM 22 项 fixture 通过；保留三次时间精度失败；按用户决定不启用、不替代内置日历 |
| 模型 | `muse_model_request` → `model.complete` | `model.complete` | 已有官方模型调用；具体后端由宿主配置，不等于 Octos Agent | model、官方 provider 配置/预算 | 无新模型代理，中 | 保留调用与错误，模型说完成不代替工具核验 |
| App Agent/工具 | rc17 agent:null；隔离原型；正式 Chat 仍使用原 model.complete | `octos.session.open/history / octos.turn.start/interrupt`；AGENT.md / script-tools / `app_tools.dispatch@1` | contained.rs有普通入口；自有工具受namespace限制。无自有工具的原型最新原生Gate仍因calendar.events不在商店默认offered_tools拒绝；空工具对照通过，不能作为业务候选 | 明确octos服务、agent.tools、原生consent及合法工具offer/签名准入 | 官方工具准入阻塞，高 | 已补#182 comment6095096789；不改system身份/放宽Gate。覆盖0/16，BLOCKED_NATIVE_GATE，无真实模型工具选择 |
| 存储 | `storage_write/storage_read` → 官方 jailed `fs.write/read/exists/mkdir/sha256[_file]` | 官方 Splash filesystem jail，非任意系统路径 | 当前 VM 真实使用；原子性由现有日志/备份/读回补偿 | storage、应用 jail | Muse 的动作/恢复日志必须保留，中 | 不直接访问 Host 私有目录；写、读回、重启按同一包验证 |
| 全局记忆 | `gm_*` 检索、冲突、更正、遗忘，写入上述 jail | 使用官方存储和 model；DSL/授权归属是 Muse 业务 | 已实现，语义质量依后端；不能视作基础设施重复 | 当前项目/归属/账号授权过滤 | 不重复，中 | 保留来源、上下文上限与跨会话检索，禁止整库灌入 |
| 提醒 | `muse_notify` → `glance.publish` | `glance.publish` | 官方能力；系统通知具体平台另验 | glance | 无重复，低 | 保留有效结果卡，失败不假通知成功 |

## 调用链与边界

正式入口 `bundle/main.splash` 仍冻结 rc17，SHA `90351cba`，总包 770,540 字节。可读源正准备 rc18，尚未覆盖活动包，因此不能宣称二者同 token。所有现实操作均经 `host.request`；历史 Calendar 动态 service 已改到 fail-closed 兼容入口。`fs` 只在应用 jail；未观察到此入口导入旧 `app/*.py`、直接 SMTP/IMAP、HTTP 模型代理、系统进程或 Keychain 接口。

Muse 事务路径：来信来源 → 作用域/记忆 → 候选/计划 → 精确预览 → 持久动作登记 → 官方宿主原生审阅 → 返回标识/收据 → 独立只读查询 → 结果/记忆 → 重启只读恢复。源 ID、原事件和幂等日志继续属于 Muse。

**准入不等于执行**：旧扩展 hub check 不能证明新版官方契约；布局检查不能证明 publisher/tag-push 发布。当前生产稳定包不覆盖，候选采用新版本独立验证。

## 2026-10-09 当前候选证据

Mail 迁移后真实参考 Splash VM 的 synthetic Host 协议共 11 项通过：能力发现失败可重试、宿主 compose 身份与 revision 持久化、原生取消保留正文、服务受理不等于投递、UNKNOWN 不重发和只读对账。零真实发信、零系统日历写入、零付费调用。详情见 `official_muse/semifinal/evidence/mail-protocol-r2.json`。真实新版 Shell 接入及可信手势发送均待完成。

回滚路径：保留根目录 rc17 活动包与 Git 基线；rc18 可读源和实验包仅在隔离 worktree。没有覆盖旧安装或生产数据。

### 当晚补充

- Mail 两独立真实参考 VM 进程的中断持久化/恢复及六种只读对账变体通过（7/7），见 `evidence/mail-restart-r3.json`。原生Host、真实外发和收件未补。r1/r2测试支架动态View报错均保留FAIL。
- rc17稳定基线20次完整进程冷启动通过；新rc18与行动链仍未合并，不算最终候选通过。
- 今日正式发布 `desktop-v0.1.0-rc.2` 源 `4ccf8e068399b1da139771a9ed94cef05fa6ae60`。Mac公开成品仅arm64，本机Intel，当前未安装升级。前轮源码获取网络失败保留；13:13核对精确Tag已完整checkout、status干净，官方setup锁定framework完成，全功能图下载停滞，13:46停止；最小offline构建同样缺octoscode，exit101；改取官方固定归档仍在下载。稳定环境保留。
- [App Hub #182](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/182) 请求连字符应用身份与自有工具namespace兼容；[OctoSense #427](https://github.com/OctoSense-org/OctoSense/issues/427) 请求共享改期/删除及精确读回。已向后者[公开提交实现代码](https://github.com/OctoSense-org/OctoSense/issues/427#issuecomment-6083645335)，两文件补丁SHA `e5545d88382f689faf99d050f0053c4bdf7a99486dc07384195314880f1a4d9b`；相关文件在rc2与原审计源码blob一致。原核心7+2、补丁9+1、原Hub schema1均为隔离实际测试，完整Host/原生批准/调用方admission未验证。owner-only限制是官方明示策略，扩共享为维护者审阅的政策提案，未接受或安装。

官方依据：[系统日历源码说明](https://github.com/OctoSense-org/OctoSense/blob/3a4d1e1e557750eac69b412f34d36021306ea654/crates/shell/src/device_calendar/README.md)、[公开 Host API](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/18cd41d91b326db199fbed4129484a9ba1a8c63d/docs/HOST-API.md)、[官方 Mail Service](https://github.com/OctoSense-org/OctoSense/blob/3a4d1e1e557750eac69b412f34d36021306ea654/apps/mail/host-service/src/lib.rs)。

## 2026-10-10 截止核对

研究源5e2e84fe及r4包未安装。最新官方Hub95e4831单独锁定构建通过，r4正确digest的unsigned结构Gate通过，scan生成7问；正式publisher准入、reviewer和新Shell运行均未通过。Desktop精确rc.2源码/framework准备通过，但依赖归档仍不完整、下载已超时停止，未使用部分归档，未安装升级。

普通开发分支同步超时、远端ref404；未同步，不动main/Tag。新Host未就绪时真实Mail/native确认和内置Calendar relay仍缺，旧配套全链不能计入本候选。Phone只完成旧rc16配套Home资源修补与真实模拟器启动/重启，细节MUSE_PHONE_RESUME_REPORT.md，不代表升级官方运行环境。
