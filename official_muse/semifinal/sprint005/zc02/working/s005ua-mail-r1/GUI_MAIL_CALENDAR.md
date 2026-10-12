# UID1 合成邮件 → 同一事项的日历候选

当前Main c098；UID1已由Root注入，不再次执行incoming。以下是源码核对后的操作指导，尚非本聊天GUI验收。根目录/活动服务使用Root当前的 `$ROOT`，不硬编码旧端口。

1. 留在当前Chat会话，记下现有“项目/归属”，保持不变。Mail页选择gui-reader账号、INBOX中的 `SPRINT005-ZC05-S005UA-MAIL-R1`；打开实际正文，确认2026-10-14 15:00–15:30、Asia/Shanghai、SPRINT005合成会议室。UID1不是应用message.id或RFC Message-ID，不手填替代ID。
2. Root与ZC05同步本case后，Root配置九字段响应（不用重启server）：

   ```sh
   python3 official_muse/semifinal/sprint005/zc02/control.py --root "$ROOT" model --json official_muse/semifinal/sprint005/zc02/working/s005ua-mail-r1/mail-calendar-policy.json
   ```

3. 在选中邮件的“这封邮件的事项归属”中，`mail_project`（项目）、`mail_owner`（归属）填当前Chat已有值，逐字一致。本人点击“从此邮件安排日程”一次，等待来源/记忆/关联分阶段保存及模型返回。源码会创建或复用该account_id/message_id的Goal，保留source/claim和正文SHA；正常九字段候选含该标题、起止、time_zone/location、question空串、duration_changed=false、完整policy。
4. 若进入Calendar页，可在“这次约定”→“来源与过程”核对Goal ID、`mail:account_id:message_id`和external_claim；记录这个真实Goal ID。该页的旧关联候选不等于官方Calendar已创建；当前 `calendar_enabled()` 固定false，历史私有calendar桥接禁止执行。“查找合适时间”不作为本case官方工具PASS入口。
5. 回Chat同一会话，在行动链中本人选择上一步同一Goal，并打开「来信与结果」。确保项目/归属及Goal仍为planned。Root切换到五字段响应：

   ```sh
   python3 official_muse/semifinal/sprint005/zc02/control.py --root "$ROOT" model --json official_muse/semifinal/sprint005/zc02/working/s005ua-mail-r1/chat-calendar.json
   ```

   Chat输入精确文本：

   > 请为当前事项准备日历候选：标题SPRINT005-ZC05-S005UA-MAIL-R1；开始2026-10-14T15:00:00+08:00，结束2026-10-14T15:30:00+08:00；时区Asia/Shanghai；地点SPRINT005合成会议室。仅准备候选，等待本人核对。

6. 在新日程候选卡点“打开并核对”。当前选中的同一planned Goal会被沿用；若UI报事项/版本不一致，保留失败，不让fixture造ID或创建替代事项。进入官方Calendar候选后，第一个提交手势只查询重叠；用“回读并结清当前请求的官方记录”读回并结清。候选仍匹配且query verified后，另一次明确确认才可创建；工具计划应add_event→get_event真实读回。不要自动重发旧query或自动点击Allow。
7. 工具回执必须是当前request/turn下的真实events/add/get记录，创建后get须同稳定event ID及全部标题/时段/时区/地点一致。仅候选、模型计划或窗口出现都不算成功。Mail确认草稿是后续可选步骤；当前physical发送gate拒绝、SMTP DATA0，不能绕过，不宣称邮件已发送或事项全链完成。

模型分支：Mail关联整理调用 `model.complete`，fixture输出九字段JSON；不走Kernel tools/planner，不需新增wrapper。Chat候选也是schema输出，但必须换为五字段。真正官方Calendar工具回合才使用已交付的SDK request wrapper parser和实际offered工具。

## 独立只读快照

```sh
python3 official_muse/semifinal/sprint005/zc02/readback.py --root "$ROOT" --out "$REPO/build/sprint005/zc05-mail-calendar-readback-NEW.json"
```

每次使用新输出文件名，保留旧证据。无expected时只标SNAPSHOT_ONLY。核对 `calendar_mail_links` 的真实Goal/账号/message/source/claim、candidate；`sources`对应正文SHA须匹配 `mail_messages`；同Goal须出现在当前官方request.binding.goal_id。`official_calendar_request`只投影ID/状态/scope，不替代官方事件get回执。需要断言时按本次实际links index和IDs填写已有readback expected规则；不要预填或伪造IDs。该readback不读取凭据、Keychain或env。
