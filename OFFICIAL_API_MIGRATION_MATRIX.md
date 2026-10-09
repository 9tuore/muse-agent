# Muse 官方接口迁移审计

审计基线：Muse `9b247c89` → 布局集成 `062c1028`，`muse-goals / 0.3.27-rc17`。只读源 `official_muse/app/source/main.splash`；活动包为根 `bundle/`，旧路径是相对符号链接。旧 Python 桌面应用不是此 Splash 入口的运行依赖，未按文件名删除。

官方源码固定点：OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654`；App Hub `18cd41d91b326db199fbed4129484a9ba1a8c63d`。Host API 契约 1.10.0。源码存在不代表已安装宿主或发行版可用。现有测试 Host `276b2b68` 仍属旧配套扩展。

| 功能 | 当前实现与入口 | 官方对应接口 | 目标宿主状态 / 商店条件 | 权限 | 重复实现 / 风险 | 策略与验收 |
|---|---|---|---|---|---|---|
| 能力发现 | 原来只读 `host.capabilities()`，无方法发现 | `runtime.list`、`runtime.describe`，契约 1.10.0 | 新源码支持；旧测试 Host 未证实；须 `host-api-v1` | runtime + manifest 方法声明 | 缺少探测，高 | 实现统一发现；缺描述或不支持即拒绝使用；实际 Host 验证待补 |
| 邮箱账号/登录 | `mail_accounts_load / mail_add_account / mail_watch_poll` → `host.request` | `mail.accounts / mail.add_account` | 官方已有；账号是否可用单独查询 | mail、本人登录、宿主凭据库 | Muse 无生产 IMAP/SMTP，低 | 保留，不复制凭据、不另写连接器 |
| 邮箱同步和读信 | `mail_watch_sync / mail_watch_scan / mail_watch_prepare / mail_read_body / mail_open` | `mail.sync / mail.folders / mail.list / mail.message` | 官方已有；需账号授权和同步 | mail、账号 grant | Muse 循环和逐信关联是业务，中 | 保留去重、来源、逐封结果；受理与收件独立核验 |
| 邮件草稿和发送 | `mail_send_step` 原调用 `mail.send`，本地草稿保留用户原文 | `mail.compose / mail.compose_status / mail.review_send` | 新官方源码支持；RC1 不含新公开 composer；原生 foreground review | mail、账号、宿主真实输入确认 | 旧通道不合适，高 | 切换官方 compose + 宿主审阅，持久化 compose ID/revision；UNKNOWN 只读对账；禁止旧 send 回退 |
| 官方内置日历（本轮唯一默认） | 历史 `calendar_*` 事务、来源和回执保留；旧自备 EventKit 调用已隔离 | `os.calendar` 的 `calendar.events / calendar.add_event / calendar.notify` 经官方 App-Agent relay | SYSTEM_APP_ONLY，Muse 不能直接调用；三项共享工具由官方 grant/relay 路由；当前 Native Host 未实测 | octos.*、agent.tools、本人 Agent consent、宿主审批 | 原自备桥退出新候选，风险高 | 用户明确选择内置日历；生产源码已阻止私有桥，当前联动 BLOCKED，待真实 relay；历史身份不改 |
| 内置日历改期/删除/精确不存在核验 | 历史原事件关联、去重与 UNKNOWN 记录保留 | 官方存在 `calendar.update_event / calendar.remove_event`；无 calendar.get | update/remove 当前未 shareable；普通 Muse Agent 无跨应用调用路径；events 有 200 条上限，无分页保证 | 官方 relay 策略及可信批准 | 接口缺项，高 | 准备最小复现和上游反馈；禁止删除重建冒充改期，禁止空列表冒充删除核验 |
| 官方系统日历研究（不在默认运行链） | `research/official-device-calendar/adapter.patch` | `device_calendar.*@1`，契约 1.10.0 | 最新 Shell 源码包含适配器；当前参考 Host 未实现验证；区别于内置 Calendar | device_calendar、平台适配器、OS grant、scoped handle/revision | 独立研究 | 真实 Splash VM 22 项 fixture 通过；保留三次时间精度失败；按用户决定不启用、不替代内置日历 |
| 模型 | `muse_model_request` → `model.complete` | `model.complete` | 已有官方模型调用；具体后端由宿主配置，不等于 Octos Agent | model、官方 provider 配置/预算 | 无新模型代理，中 | 保留调用与错误，模型说完成不代替工具核验 |
| App Agent/工具 | rc17 agent:null；B 隔离原型；正式 Chat 仍使用原 model.complete | `octos.session.open/history / octos.turn.start/interrupt`；AGENT.md / script-tools / `app_tools.dispatch@1` | contained.rs 有普通 Splash 入口；Host 自持 card.muse-goals；自有 tools.json 受短 ID namespace 禁止连字符的限制；无自有工具可先申请共享工具 | 明确 octos 服务声明、agent.tools、原生 consent、signed admission | 缺少真正工具选择，高 | B 审计已集成；不改存储身份；未做真实模型工具选择前为 NOT_TESTED |
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

官方依据：[系统日历源码说明](https://github.com/OctoSense-org/OctoSense/blob/3a4d1e1e557750eac69b412f34d36021306ea654/crates/shell/src/device_calendar/README.md)、[公开 Host API](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/18cd41d91b326db199fbed4129484a9ba1a8c63d/docs/HOST-API.md)、[官方 Mail Service](https://github.com/OctoSense-org/OctoSense/blob/3a4d1e1e557750eac69b412f34d36021306ea654/apps/mail/host-service/src/lib.rs)。
