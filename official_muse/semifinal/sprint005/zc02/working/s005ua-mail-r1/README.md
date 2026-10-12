# S005UA Mail R1 工作副本（未注入）

incoming.json 是现有 /__fixture/incoming 接口的四字段公开JSON：account、sender、subject、body。仅server合成来信，不写SDK业务库，不发送现实SMTP。
标题 SPRINT005-ZC05-S005UA-MAIL-R1；明确2026-10-14 15:00–15:30 Asia/Shanghai，地点SPRINT005合成会议室。

**Message-ID限制：**当前serve.py State.incoming无可指定Message-ID字段，实际生成 `<SPRINT005-{time.time_ns()}@sprint005.example.invalid>`；添加message_id字段会被忽略。请求的稳定头 `<s005ua-r1-mail@sprint005.example.invalid>` 未能由现有schema实现。正文有s005ua-r1-mail追踪标签，但不能冒充Message-ID。Root若选择使用现有接口，应保存一次注入返回的实际message_id/uid/raw_sha256，并以该回执关联后续读取；不要重复注入冒充同一封。未修改服务或绕过存储。

chat-mail.json 是Chat邮件候选三字段工作副本；mail-calendar-policy.json 是邮件日程整理九字段/policy工作副本，只用于calendar_model_candidate入口。不能将其当作Chat Calendar五字段响应。原39样本、catalog与身份全部未变。

由Root/ZC05先同步具体case，再决定注入/配置；本批未调用任何控制写端点。示例路径相对仓库：

```sh
python3 official_muse/semifinal/sprint005/zc02/control.py --root "$ROOT" incoming --json official_muse/semifinal/sprint005/zc02/working/s005ua-mail-r1/incoming.json
python3 official_muse/semifinal/sprint005/zc02/control.py --root "$ROOT" model --json official_muse/semifinal/sprint005/zc02/working/s005ua-mail-r1/mail-calendar-policy.json
```

当前GUI f9/seq7、后续c098/seq8仅Root提供的运行说明；本批不做新的Main身份绑定，不操作GUI或shared target。
