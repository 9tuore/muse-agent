# Calendar Host Extension 上游贡献草稿

状态：DRAFT / NOT_SUBMITTED。源头是 Muse 官方迁移时需要完整 Calendar 读写与独立回读的实际需求，不是新造比赛功能。A4 没有发布 Issue/PR、没有修改产品/SDK 源码、没有进行真实 Calendar 变更。

## Problem / Why Store Apps need it

固定官方 OctoSense `7f962547cd8035ed2bb05962cf7824d8aa33e3a3` 的原始精确 archive 中，没有 `apps/calendar/host-service/`。当前本地实现增加该服务及 Shell 接入；本地 App Hub policy 将 `calendar` 加入 capability 集合。脚本 Store App 无法把原生 EventKit 代码放进自己的 bundle，因此需要宿主提供一个受能力与 OS 权限约束的 Calendar API。

单纯返回写入接受不够：安排工作流需要查询冲突、保存系统 event_id、独立 get 验证、改期时更新原事件，以及在崩溃/超时后避免盲重试。这里的贡献是可复用宿主机制；Muse 的 Mail/Memory/模型业务不应随 PR 混入。

Calendar 源码最后修改 provenance commit：`eba2924db8a8531a3affe8882a7c5b89fb0c220d`。A4 暖构建当前 SDK lock SHA `a7518162af7858f0d556806aa157a57056c94f6c5437bedc2b16231c768675a1`；整棵 OctoSense overlay tree `406dee1ec74a6cf9b85cef41700ffe081aabf9bed4f7f67e77b2484afa686780` 还包含其他既有扩展及模型 logger，**不能当作 Calendar-only patch**。最终审阅需总控给出新冻结 Muse commit 与单独最小 patch。

## API（当前已实现）

| 方法 | 必要输入 / 输出 |
| --- | --- |
| `calendar.status` | permission；full_access 时列出 calendar id/title/writable |
| `calendar.request_access` | 由用户处理 macOS 提示；返回 permission，超时或拒绝显式错误 |
| `calendar.list` | calendar_id、RFC3339 offset start/end、limit 1–100；events、truncated |
| `calendar.get` | calendar_id、event_id；found、event、version |
| `calendar.create` | request_id、calendar_id、title、start/end、time_zone，可选 location；event_id、version |
| `calendar.update` | 同一 event_id、request_id、expected_version、changes（title/start/end/time_zone/location）；event_id、version |
| `calendar.delete` | event_id、request_id、expected_version；deleted；今晚禁止真实执行 |

请求 ID 为 8–100 ASCII 字母/数字/下划线/连字符；查询/创建时间范围最多 31 天；文本按 UTF-8 bytes 有界，不能将 bytes 限制写为字符数。返回时间用 UTC ISO8601，保留 event.time_zone。所有 native 调用在 worker 上，系统权限提示上限 120 秒，不堵塞 UI 线程。

## Permission model / EventKit behavior

两层现状：App Hub isolate 检查 `calendar` capability；EventKit 每次检查宿主 full_access 及目标 Calendar。write_only 不足以独立回读，显式拒绝。当前新权限请求仅 macOS 14+；其他平台 native shim 返回不支持。A4 只实编 Intel，ARM compatibility 尚待实际构建。

Host 校验 calendar_id 存在/可写，但并未保存一个额外的“用户选定 Calendar token”。每次动作的人工确认属于当前 Muse 应用层流程，不能声称宿主额外实现了不可绕过的逐动作确认。上游应决定是否拆分 read/write capability、要求 trusted sheet 选择目标及逐动作批准凭据。

更新/删除只允许当前 app 创建的非重复、无参会人、非 detached 事件；原生检查 `event.URL` 的 `muse-calendar://<app-id-sha256>/<request-id>` 归属标记和 last_modified。它限制 app 之间修改；上游审阅应考虑通用 namespace 与防误删策略。当前策略有意不覆盖重复会议、邀请及其他 app 创建的事件。

## Readback / Failure semantics

Rust 对返回 event 序列化结果做 SHA256 version。update/delete 先独立 get 比较 expected_version，再让 native 校验 expected_last_modified；过期内容拒绝并要求 review。

create/update 的接受回执为 event_id/version，来自写入后的 native eventValue；**不是独立验证**。业务调用者随后新发 `calendar.get`，比较实际系统事件，才能标记 EXTERNAL_RESULT_VERIFIED。

变更使用每 app 的持久 journal，文件名是 app_id 哈希。request_id + 方法/args fingerprint 相同且 done 才回放先前结果；同 ID 不同内容拒绝；pending/不确定结果拒绝盲重试。journal pending 在 native 动作前 fsync；原生失败或提交后本地结果保存失败，保留 reconcile 要求。不要把系统事件可能已改变的错误写成“肯定没有执行”。

## Privacy / limitations to review

不需要远程 Calendar 账号或 model key。OS EventKit 可能同步到用户自己的 Calendar 服务；不能宣传完全离线。数据包括 Calendar ID、事件字段、version/fingerprint 和变更回执。当前 journal 不保存原始完整事件内容，但保存 event_id/version；应核对生命周期、文件访问权限和用户删除策略。

需要上游评审的具体项：当前 journal BTreeMap 未实现持久记录 retention 上限；批准强度目前在 app 层；本地 capability 与原版准入兼容尚未验证；归属 URI 使用 Muse 前缀；事件 version 受系统字段变化影响；Apple Silicon/其他平台未实测。这些是未完成审阅项，不写成生产就绪。

## Tests / compatibility / evidence

- A4 实际 release Host 编译成功，完整 app 三组资源并严格 ad hoc 验签；签后 Host SHA `d5000c8319ed7eb7237594d2cc6824a1510f7b3024bf84f78d68d5c1b72b1742`。它包含全部当前 SDK 扩展，不能当 Calendar-only 构建。
- 五 SDK exact archive 恢复与当前 tree/count verify 实际通过，12,000 files。
- Calendar source 中三项纯测试实际 3/3 PASS，覆盖 invalid range/request ID、损坏 journal 拒绝、相同请求重放/不同内容拒绝/pending 拒绝；无 EventKit、无真实 Calendar 变更。`CALENDAR_PURE_TEST_RESULTS.json` / `calendar-pure-tests.log` 记录实际命令、exit=0 与源文件 SHA `9ed94317c35a7b8b487798c434c63078f34b50e72f4a8f8d8a968ea744229588`。
- 当前真实 Calendar CRUD/readback、权限丢失、系统外部改动、崩溃后 reconcile 的完整集成证据由总控绑定最终版本提供。A4 未执行这些 LIVE 动作，晚上只可用 isolated/fake backend。
- Calendar API 的独立源码 SHA/测试/最终 commit 应在正式 PR 前补入，不能拼接旧截图或把 Fixture 当系统 EventKit。

## Patch scope / proposed reviewable series

1. App Hub：只加 Calendar capability 及拒绝/批准边界测试；不带 Muse bundle/listing 或其他扩展。
2. OctoSense：新增 Calendar crate + EventKit bridge + request/version/journal 机制与 focused pure/fake-native tests。
3. Shell：workspace 依赖、`app-hub` feature 的注册、plist full-access description、资源/构建说明；不带模型日志、Mail/UI 中文化或产品流程。
4. 官方文档/API contract、平台与限制、人工授权和独立 readback 示范。

这是计划，不是已经创建的 commit series。总控可在最终稳定源的隔离分支准备最小 patch，用户醒来决定是否提交；今晚不创建正式 upstream Issue/PR。
