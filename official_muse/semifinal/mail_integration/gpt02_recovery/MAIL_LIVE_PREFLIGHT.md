# 固定 SDK Mail 实机闭环前置检查

2026-10-11：源码确认，实机未执行。中央独占完整Host/正式包/GUI，本聊天零请求、零发送、零秘密读取、零构建。中央给出的Host前缀30d4d356未在此独立核完整SHA/准入。依据中央 `build/runtime-closure-full-shell-r1/sdk`；脚本锁8个实际源码文件SHA，漂移即拒绝，不用旧overlay/reference VM替代完整Host。

| 同一前台Muse的调用 | 返回/含义 |
|---|---|
| `mail.accounts`, `{}` | `[{id,address}]`，只含此app获权账户；空数组也是成功。没有 `mail.status` 分支，也没有账户连通布尔字段。 |
| `mail.list`, `{account,folder:"INBOX",offset:0,limit:1}` | 缓存 `{folder,total,messages:[{id,sender,address,subject,preview,time,unread}]}`，不联网/改已读；空缓存不是认证结果。 |
| `mail.compose`, `{account,to,subject,body}` | 完整绑定草稿含 `publisher,account,from,draft_id,compose_id,revision,to,subject,body,status,attempts[]`；新稿revision=1/status=draft，不读密码/发送。 |
| `mail.compose_status`, `{account,compose_id}` | 同一完整草稿及attempts；末attempt含operation_id/revision/status/payload、可选receipt。 |
| `mail.review_send`, `{account,to,subject,body,compose_id,expected_revision}` | 打开原生精确审阅；此次仅取消，回调错误 `Review cancelled; nothing was sent`。 |

回调看 `r.is_ok/r.data/r.error`。只支持一个ASCII To，无Cc/Bcc；subject≤512 UTF-8 bytes且无换行/NUL，body≤8192 bytes且无NUL。已有compose须Host实际ID（compose-前缀，≤96字母数字/hyphen）、positive revision；更改文本才revision+1。发现表仅compose/status/review_send/send @1；accounts/list/add_account没有descriptor，勿放required ABI。Agent accounts带account时返回 `{accounts:[...]}`，status只有有界attempt/正文投影；本次精确核验走前台。

中央执行：

1. 固定完整Host/Kernel/已准入Muse身份，确认非mail_demo/替代file-vault，沿用来信监控/模型分析暂停设置。先同Muse读accounts，只选其真实id；不导出私人来信。
2. 脚本只生成请求数据。收件人改为本人已授权邮箱，手写合成稿，不调用模型。compose一次，保存真实返回ID/revision/精确snapshot，再status逐字段核对。默认example.invalid仅供离线演示。
3. 现有Muse路径：“新邮件草稿”→“发送邮件”（应用预览）→“确认发送这封新邮件”（compose后请求native review）。**原生sheet只点Back to editing，绝不点Approve & Send。** 此UI路径已含compose，勿另外手动compose重复创建。
4. 取消后同ID读status，核文本/身份保留、没有sending/accepted。公共ReviewRequest.cancel只retire capability；prepare完成后Host可能仍awaiting_approval，不能强断言回到draft，须与Muse本地DRAFT分开记录。
5. Remote供中央核自有PID/port后用 `/s`、`/snap`和普通UI导航；没有任意host.request HTTP路由，Remote输入也不能制造native trusted_user_input批准。本聊天不发Remote请求。

```sh
python3 official_muse/semifinal/mail_integration/gpt02_recovery/prepare_mail_live.py \
 --sdk '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/runtime-closure-full-shell-r1/sdk'
# 同app真实账号：添加 --account '<id>' --to '<本人授权邮箱>'。
# 仅对应脚本生成的精确稿：再添加 --compose-id '<真实id>' --revision <真实revision>。
```

失败区分：不存在账户=There is no such account；grant不足=This app may not use that account。revision_conflict须保留未存文本并只读重载；身份/绑定错配不重提。Open the app to review是前台不足；no native Mail review surface是hook缺失；workers busy是资源限制。取消明确未发；failed_before_delivery确定投递前失败，outcome_unknown可能已投递，均不自动重发。accepted只代表SMTP受理；本轮零发送不产生独立收件证据。

Keychain复用（只读源码）：Store=`<apps_root>/.host/mail`，accounts.apps决定grant。macOS service=`OctoSense Mail `+SHA256(canonical mail_dir)[:12]；account=SHA256(host+"\n"+username)[:24]。只变secrets_dir不改名称，新home/profile路径则名称不同。SDK只迁移自身旧 `<mail_dir>/secrets/<id>`，没有旧Python Muse任意Keychain命名的导入依据。同官方profile/账户identity/已获权app具备名称复用条件；凭据存在、当前签名访问与网络认证仍未验证。不能拷accounts、改apps或重命名/私读Keychain。空accounts由本人从同Muse的add_account宿主sheet登录，秘密只在sheet输入；取消=Sign-in cancelled，成功={id,address}并追加此app grant。当前Muse登录成功会启用mail_watch，中央需按既定设置处理该副作用。

定位（相对上述sdk）：lib.rs/accounts、list、compose分支；public_review.rs/open、cancel、api_methods；drafts.rs/compose_draft、composer_status、composer_result、retire_public_review；vault.rs/keychain::entry；network.rs/identity；shell apps.rs/register_mail_services、connected_review.rs/可信输入；makepad remote.rs/route。脚本5项离线检查通过；仅源码与请求准备，非实机通过。
