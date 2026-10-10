## Central observed result — 2026-10-11 05:50

The isolated complete SDK now contains the exact reviewed raw-sheet-only patch, source SHA724c7d7f. Bytes outside signin_sheet raw source are unchanged. The original-source six Mail protocol tests remain evidence for the unchanged backend, not evidence of new live login.

Actual visible reference runs at 412×892 and 990×539 each passed all14 checks, normal quit/exit0 and final error-log rescan. Central viewed both initial PNGs; the narrow instructions wrap, and short-window input/buttons remain reachable by real scroll events. See evidence/native-full-shell-r1/qq-login-ui/result.json. The managed reference intentionally displays its password-input guard in English and never accepts a credential; no claim of runtime masking, actual native Host sheet, QQ login, Vault or Person approval is made.

Fresh optional preparation replays the exact Native/Calendar/privacy/QQ patches and matches seven relevant files; it is PREPARED_NOT_BUILT. The complete canonical Desktop r7 is being built separately. Old Host, root rc17 and production data remain unchanged.

# QQ 登录宿主 UI 最小补丁（未应用）

目标：`build/runtime-closure-full-shell-r1/sdk/apps/mail/host-service/src/lib.rs`，仅 `signin_sheet()` 的 Splash 生成 UI/handlers 字符串。

- 原文件 SHA256：`5b9bbd082d7df01b9068bf1c830c30ff4f3d35ba31f182a387bea071fb2fc50e`
- 补丁 SHA256：`0415463dc87bba93b8867d1476f12260ac366eaf7be9a2c9380640d8437d5b25`
- 应用后的预期文件 SHA256：`724c7d7faee03d1303b8caf20b33e6958f385a03f01bf29a92a704a477fcbf7c`

删除单独用户名输入；实际官方 JSON 键是 `username`，不是 `login`。保持原协议键不变，`address/username` 均取完整 `ui.address.text().trim()`。`password` 键与保密输入控件名保持原样，用户文案只称“授权码”。`mail.sheet.submit/cancel`、service、Vault、权限、账号字段和后台发送/审阅全部未改；原后端错误 `r.error` 原样显示，未在 UI 隐藏错误。

QQ 初始 IMAP `imap.qq.com:993`、SMTP `smtp.qq.com:465`，TLS不变；保留 POP3，未编辑收件字段时切换为 `pop.qq.com:995`。任一收件服务器/端口用户编辑都会锁住这对输入，此后协议切换只更改协议与标题，不覆盖输入（包括手填成默认值或清空）。SMTP 始终可编辑且不随协议切换；其他邮箱可自定义。未编辑时可在 IMAP/POP3 默认值间往返。

来源：已读项目 `docs/USER_GUIDE.zh-CN.md:12-36` 和既有 QQ 登录修正记录 `official_muse/rc/improvement-20261005-r1/REPORT.md:34`。项目教程使用 QQ 官方帮助入口 https://service.mail.qq.com/cgi-bin/help ，本次自动读取仍不可访问；没有将其标为正文已验证。实际取得正文的[华为官方授权码教程](https://consumer.huawei.com/cn/support/content/zh-cn16108643/)确认网页登录→设置→IMAP/SMTP服务→本人验证→获取授权码。UI 只写这些稳定步骤，入口以当前账号页面为准，不猜新网页按钮。服务器默认沿用项目已核配置；POP3 995亦沿用原程序 TLS 协议端口。

静态核对：差异仅限 `signin_sheet()`；提交 JSON 键集合保持原样；无 `ui.username/ui.login`；无 Gmail 默认。`.trim()` 已核于 `apps/ai-providers/bundle/main.splash:102`。`TextInput.on_change` 定义已核于 SDK `.sources/makepad/widgets/src/text_input.rs:675,698-699`，既有 Splash 使用见 `apps/photos/bundle/main.splash:858`；`set_text`（同文件2426）不调用 change handler。以上是源码静态核对，尚无 Splash 编译或事件执行证明。

中央已报告原源码六项官方 Mail 测试 `SIX_COMPONENT_FIXTURES_PASS`，这仅是原源码 fixture，不能替代本补丁验收。本补丁未应用共享 SDK，未编译，未运行 GUI、Cargo、登录或邮件动作。中央应用前核原 SHA；应用后需要验证 sheet 可见、中文指引可读、完整地址提交、QQ 默认往返、手填服务器/端口切换保持、授权码遮罩。真实登录与 native review/收件仍需本人操作和独立证据。

窄窗补充：新增中文标题、授权码保管说明及三条 QQ 指引共五个 Label 均显式 `draw_text.wrap: Words`；现有 ScrollYView、尺寸、间距、布局与权限保持。语法已核 `apps/reference/src/lib.rs:23` 与 `apps/muse-native-prototype/src/lib.rs:29`。仅内存核对补丁上下文与边界，尚未编译或验证 412 宽窗口的实际换行/可见性。
