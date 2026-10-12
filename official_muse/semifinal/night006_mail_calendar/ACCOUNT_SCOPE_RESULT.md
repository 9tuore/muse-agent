# 本地日历与第二邮箱解耦

确认是无关邮箱变化引起的误失效。冻结 Root `27b2e23a`、Main 源 SHA `e043b12e…` 中，已完成 local 日程的 binding 和 request_source 与整个 `gm_accounts.to_json()` 比较。实际 `gm_set_accounts([A,B])` 新增 B 后，本地权限、用户与项目完全未变，当前事件、删除、同 ID 改期、历史读回和重启恢复仍被拒绝。原 18 项定向检查中 8 FAIL，保存在 `evidence/account-scope-baseline`。

仅切换已有邮箱的 `mail_select_account` 本身不更改 gm_accounts；账号列表刷新、新增或返回顺序变化会触发这个错误。

`local-calendar-account-scope.patch` 为最小修复：31 行新增、13 行调整，已经对 Root 当前源码 `git apply --check` 通过。只有明确 local 的绑定或保存完整的 local request_source，不再以无关邮箱列表为身份边界。用户、当前项目/归属/会话、事项版本、local 可访问性和真实工具证据继续核对；Mail 来源的原快照规则保留，撤销来源 A 不会被这个例外放行。

修改覆盖相关的历史、结果显示、当前绑定、改期与重复候选比较。新增邮箱发生在请求中途时，保持历史 accounts 记录和新绑定内部一致；候选准备后、派发前新增邮箱时，新请求保存自己的快照。旧创建证明不被改写，也不会因邮箱变化重新认成一个可重复创建的新候选。

- `evidence/account-scope-final`：25/25 FIXTURE_PASS，包括新增、重排、无关邮箱移除、请求中途变化、恢复、同 ID 改期和重复创建保护。用户/项目/归属/会话/local 撤销/事项版本变化及 Mail 来源撤销均拒绝。
- `evidence/account-scope-full-store`：8/8 PASS，使用完整生产 Goal/Chat 持久化、实际 gm_set_accounts、真实改期候选生成和 update_valid/current，验证旧创建快照与新改期快照账号列表不同时仍能正确保存、校验，换用户仍拒绝。
- `evidence/account-scope-first-fix`：早期 23 项同类检查保留。未重跑其它已通过套件。

最终私有源 SHA：`db82406744e11587707ae660ed3863454c5b1cecbb7de57d0bea711734a8423e`。全部结果属于真实 Splash VM/生产函数、隔离 fixture 存储与 Host 回执，不是 GUI 或真实 Calendar owner 验收。没有修改 Root、SDK、GUI 或原资料；r3 冻结候选保持原样。中央若接收补丁，应重新签候选并重测受影响 GUI 项目。
