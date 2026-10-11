# 当前事项 → 官方 Calendar Agent → 行动链

这是可应用源码提案，正式main未改，真实Splash VM/GUI未执行。中央基线8279a606，源码SHA271b1beb3a0b334af8b2182550fe0536e3ea1d4361d18ce554e7b2438f062958，包含已应用Mail暂停修补与新的strong/fast模型选择；本补丁保留两者。修补后SHA0c17e4cc3168d5c85518c2e177424a4803eb19297c665edcaa392cd3381fce2c，完整身份见calendar-chain-identity.json。

实际连接：本人在行动链选择当前事项→Chat日程候选“打开并核对”转官方Calendar页→核对候选后单独提交→现有octos.session.open/octos.turn.start→现有octos.session.history的Host回执→当前事项行动链。普通手写官方请求仍可独立使用，不自动绑定事项。没有调用旧calendar.status/list/get/EventKit，没有owner替身、共享Memory注入或直接Host工具写入。

派发前保存goal_id/plan_revision/project_id/owner_id/user_id/account_id/accounts/session_id/candidate_id/candidate_revision及精确候选；实际request_id写入官方add参数，turn_id保存到同一请求。本人选择、候选版本/正文/账号、计划版本、项目/归属/会话或用户变化时，旧回调不显示当前事项成功。迟到turn_id仍保存为unknown便于核对。归档保存完整binding；同一归档候选禁止重派发，重启in_flight转unknown不重做。

回执只走现有calendar_agent_receipt_status：同person回合、Kernel持久的broker工具结果，caller/owner/tool/call绑定正确。只有add稳定id及start与精确get的found/event一致，request_id、title/start/end/timezone/location/notes全匹配，才记录verified。add只有受理时accepted；错误/取消按failed分类，错配/省略/旧回合/无Host回执未知。模型文字不算成功。当前核验限定Asia/Shanghai整分钟（SDK落盘是时区墙钟分钟）；其他时区保持独立官方请求，未假造通用时区转换。

事项整体不标completed，不接旧calendar_links/mail确认依赖，不冒称改期已接通；页面和行动链明确提示这些剩余依赖。历史核验对象保留在binding.verification，当前身份或版本变化后不投射为当前事项。

定向合成测试65/65：17个真实函数投影到Node；临时JSON真实写入/读回，scope/UI/时间/Host为fixture适配。覆盖有效配对、thread fallback、稳定ID/字段/身份版本错配、错误/取消、add-only/model-only、重启、不重发、归档、写入失败及不可读核验记录。前五次适配器错误日志保留（语句/循环投影和缺fixture gm_has），不当作产品失败；r6 63/63为旧基线，r7 65/65为最终基线。Node不是实际Splash VM或外部创建证据。

```sh
python3 official_muse/semifinal/mail_integration/gpt02_recovery/prepare_calendar_chain.py --source <完整SHA匹配的副本before.splash>
python3 official_muse/semifinal/mail_integration/gpt02_recovery/test_calendar_chain.py --source <同一before.splash> --out <新报告.json>
```

零上下文patch只在完整source SHA匹配时使用git apply --check --unidiff-zero。来源漂移须按具名边界重新准备，不覆盖整个main。应用检查已确认仅改变6个既有函数及Calendar页面UI；calendar_enabled/muse_calendar_request/receipt_status/chat_model_config/mail_add_account保持原字节。中央安排正式包真实VM/UI与本人批准；本聊天未启动GUI/Cargo/模型/SMTP或读取秘密。
