# 官方日历后的可选 Mail 草稿提案

PARTIAL：本地补丁与定向 fixture 已完成；正式 main、Bundle、SDK 和 GUI 未写，未运行实际 Splash VM/Host、模型或 SMTP。中央应用、真实 VM 与原生审阅仍待中央协调。本提案只处理已精确读回后的关联草稿，不开放改期或整体事项完成。

## 已核对的缺口与改动

基线官方 `calendar_agent_history` 能保存当前事项的 add/get 精确读回，但未写旧私有 `calendar_links`。既有 `mail_compose_from_calendar` 只认旧 links，不能用作官方事件的关联入口。现有 `mail.compose` → `mail.review_send` → `mail.compose_status`、精确预览、UNKNOWN 禁重放与收件端本人声明路径已经存在，继续复用。

补丁增加 Calendar 页的可选“准备或打开关联确认草稿”。必须本人已选当前事项、实际候选仍有效、官方回执 verified，且选择已授权 Mail 账号；邮件来源事项要求同账号，local 事项使用本人显式选择的授权账号。草稿 recipient 留空，内容由精确读回事件生成，保留 goal/plan/project/owner/user/accounts/chat/candidate/request/turn/event 和 add/get proof。重复打开同绑定保留手改原文，覆盖其他可编辑稿之前用既有 archive 保存；其他待确认、accepted 或 UNKNOWN 不覆盖。准备/预览不调用 Host，是否发送由本人单独决定。

在预览、确认、各异步 phase、compose 与原生 review 迟到回调、只读对账、收件声明和行动链展示处检查当前绑定。身份、事项、版本、候选或事件变化不推送旧结果。未完成发送转 UNKNOWN；保留原 payload、Host composer ID 和有界迟到回执，禁止自动重发。已经 accepted/verified 的事实保留为历史，不降格或用于完成新事项。只读对账仍限原 compose_id、账号、revision 与精确收件人/主题/正文，可靠失败仍沿原 unsent 流程恢复可编辑原文。

官方 Calendar 尚未启动 Goal run。已核对 `core_begin_action` 明确允许空 goal/run、revision=0 的独立操作日志。关联邮件因此复用这条路径；草稿保存事项关联，Mail action 独立保存，既有 Goal plan/version/status 不改，Mail 收件声明不调用旧整体完成路径。没有新增 Host 方法或假造 owner 权限。

## 身份与应用

- 基线中央 HEAD：`691bf7c4b22bda3197c03fa5b82e5351253e01f1`。
- 基线完整 source SHA256：`0c17e4cc3168d5c85518c2e177424a4803eb19297c665edcaa392cd3381fce2c`。
- 预期完整 source SHA256：`0c7f9812cf7319cf5120557ddef7caacfe49326c0dcbc5759e689fcac38ce9eb`。
- 补丁与 SHA 见 `calendar-mail.patch` / `calendar-mail-identity.json`。

必须先核完整基线 SHA，再 `git apply --check --unidiff-zero <patch>`；正式源漂移后只能按具名函数重新准备/审阅，不能按行号偏移或整文件覆盖。本聊天只在隔离临时副本 check/apply 并核完整预期 SHA，未应用正式 main。

## 验证

```sh
python3 official_muse/semifinal/mail_integration/gpt02_recovery/prepare_calendar_mail.py --source <0c17基线源码副本>
python3 official_muse/semifinal/mail_integration/gpt02_recovery/test_calendar_mail.py --source <同一基线源码副本> --out <新证据路径>
```

2026-10-11 最新 `evidence/calendar-mail-r9.json`：100/100，external_calls=0。提取 31 个实际函数投影到 Node；UI/Host/授权/日志写入是合成适配器，临时 JSON 写入读回是真实文件。覆盖完整 draft→preview→compose→native-review→accepted→本人收件声明、17种 scope 变化、精确事件字段变化、各未完成 Calendar 状态、迟到 compose/native/status、UNKNOWN 禁重放/可靠失败、旧手稿归档、待确认稿保护、账号一致、存储失败与普通 Mail 回归。fixture 的 core journal 是适配器，不将它说成真实核心持久化或 SMTP 验收。

r1-r5 和 r8 是 Node 适配器语句/回调/对象条件转换错误，证据保留，未运行产品，不算产品失败。r6 80/80 与 r7 100/100 对应旧提案 SHA33427a51；r9 对应最终 SHA0c7f9812，旧结果不作为最终身份。首次生成器边界断言失败发生于输出前，修正具名函数首行插入后才生成补丁。

`evidence/calendar-mail-application.json`：临时副本 `git apply --check` 通过并核完整 SHA；14 个既有函数变化，509 个既有函数字节不变。core action/run、Calendar history/精确配对、Mail receipt classifier 字节不变。

## 中央后续

在冻结正式 source/SDK 后协调真实 Splash VM，再以实际官方 Host 做 draft/review/cancel/UNKNOWN 只读回读及身份切换。任何真实发送仍须本人在原生窗口决定，并独立核验收件端；窗口、卡片、accepted 和本 fixture 均不能代替投递证据。无新权限问题，本聊天已完成被委派的提案范围；不 push。
