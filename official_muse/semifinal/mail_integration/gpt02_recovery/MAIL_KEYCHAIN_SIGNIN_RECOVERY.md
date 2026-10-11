# Mail Keychain 与登录失败恢复：只读核对

2026-10-11；GPT-02。中央 HEAD `291e74b39621d3187bbdc5fa1050ca5d7f86cf6e`，现场 main SHA `6e0f2b7009367409173b990522e4078746eeaf9e1bc46dc649bdb8d2838ead6f`。核对的是指定 SDK 源码，不是运行中 Host 的二进制身份或真实账号。收到的错误 `Platform secure storage failure: invalid Info.plist(plist or signature have been modified)`、Host ec83 脱离 .app 的情况均来自中央报告，本聊天没有重现或验签。签名打包由 Root/GPT03 负责。

## 已核源码行为

1. 正常 macOS `register()` → `register_with()` → `vault::platform()` 默认 Keychain；并非所有模式都只能 Keychain：源码有显式 file-vault override，demo 注册也用 FileVault。本聊天未读实际环境/配置，不能断言候选采用哪种。不要用 file/demo 绕过签名问题。依据：`lib.rs:398-407,466-473`、`vault.rs:163-176`、`shell/src/apps.rs:186-204`。
2. 账号保存是两部分：授权码通过 `Keychain::put/set_password` 保存；`accounts.json` 保存 address/username/服务器参数/id/signed_in/apps 等元数据，没有 password 字段。服务名 `OctoSense Mail ` + canonical mail_dir 路径哈希前12位，item username 为账号 id；应维持原 host_dir/profile、账号 identity 和 Muse app_id/grant，不搬元数据或改授权。依据：`lib.rs:485-520,735-758`、`vault.rs:186-195`。本聊天没读实际账号文件或 Keychain。
3. `mail.sheet.submit` 先验证表单，执行 transport.test，再使 draft review capability 失效、准备元数据，最后 `vault.put(...).and_then(save_accounts)`。put 失败不写新元数据，不 close_sheet，不消费 pending 的 add_account 回调；旧元数据仍可能存在。成功才关闭 sheet、广播 Added、回 `{id,address}` 给等待应用。注意失败不能视作完全无副作用：验证成功后的 draft invalidation 已发生。依据：`lib.rs:720-768`。
4. 同一未关闭表单失败只 `ui.status.set_text(r.error)`，没有清除地址/授权码/服务器输入；可在该表单修正后重试。取消关闭 sheet 并回 `Sign-in cancelled.`。重开 Host 或重开新 sheet 会按构造器创建空地址/授权码，不承诺跨进程保留输入。依据：`lib.rs:713-719,956-984,1013-1016`。仅源码结论，未做实际 GUI 验证。
5. Keychain `get` 的 NoEntry 会尝试旧 secret 文件迁移；迁移 put 失败仍可返回读到的旧 secret。这是旧版读取兼容路径，**不是新登录 put 失败后改写文件的 fallback**。其他 get 错误直接返回。依据：`vault.rs:149-159,197-201`。不能由“同步成功”独立推出已写入新 Keychain。

## 正确签名 Host 重开后的最短本人路径

1. Root/GPT03 完成签名并保持原 profile/apps_root/Muse 身份；通过完整 .app 启动宿主。本人进入同一已获邮箱权限的 Muse → Mail → “连接账号”。
2. 本人在 OctoSense 宿主表单重新输入邮箱和授权码，保持自己的服务器参数，点顶部“连接账号”。该动作含真实服务器验证，凭据不应交给聊天。QQ 源码默认 IMAP `imap.qq.com:993`、SMTP `smtp.qq.com:465`，TLS；这里只记录现有表单默认，不作当前服务商说明。
3. 等待宿主成功关闭表单，Muse 提示“宿主已完成账号连接。”，然后“查看账号”确认授权列表出现。不要把仍显示 Keychain 错误的表单或原先已有账号列作为本次保存成功证据。源码此成功分支不再自动启用 mail_watch。
4. 如仍失败，停在错误表单；由本人保留错误文字给中央排查。不要重建授权关系、拷账号文件或切换 file/demo。原错误表单的输入不会迁移到新 Host，需本人重新输入。

## Root 可用的真实接口及验证限度

| 用途 | 已核请求 | 返回与限度 |
|---|---|---|
| 前台同 Muse 列账号 | `host.request("mail.accounts", {}, callback)` | `r.is_ok/r.data/r.error`；data 为 `[{id,address}]`，仅当前 app 获授权账号；元数据读取，不调用 vault.get。 |
| 本人登录 | `mail.add_account`, `{}` | 需要可展示 sheet 的前台；成功 `{id,address}`；失败提交留在 sheet，pending 直到成功/取消/替换。内部 submit 为 `mail.sheet.submit`，不可自动收集凭据调用。 |
| Agent 已绑定账号 | `mail.accounts`，工具声明 args `{}`，可信宿主注入 account | `{accounts:[{id,address}]}`；不枚举其他账号。勿把 Agent object 当成前台 array。 |
| 草稿投递对账 | `mail.compose_status`, `{account,compose_id}` | 草稿/attempt/receipt 状态，不能证明账号 Keychain 持久化。 |
| 后续真实认证/收信 | `mail.sync`, `{account,folder}` | incoming.collect → account_for → vault.get → transport.fetch；有网络和缓存变化，不是只读 Keychain 探针。本聊天未执行。 |

依据：`lib.rs:165-171,687-711,829-836`、`public_review.rs:247-261`、`incoming.rs:112-131`、`tools.json:5-26`、Muse main `4964-5001,10754-10760`。没有已实现/声明的通用 `mail.status`。点击账号地址会触发 `mail_select_account` → folders/list，可能读取凭据/联网；最窄保存检查只点“查看账号”。

登录成功回调按源码顺序证明本次 vault.put 与 save_accounts 返回成功；重开后列账号只能证明持久化元数据和 app grant。要进一步确认实际签名访问和真实认证，需中央在本人授权范围完成后续 live 操作并记录候选/profile 身份，不能由本只读核对升级为 live PASS。

## 本聊天验证与产物

仅读取七个指定源码文件、搜索接口/分支、记录 SHA，写 own namespace 的本文/evidence/CURRENT_STATE/HANDOFF。本机 runtime、环境、账号、凭据、签名、网络、GUI、Cargo、模型均未操作；源码核对已完成，实际恢复未验证。首次误用 main.splash/HANDOFF.md 路径返回 No such file，随后以 rg --files 定位真实路径；无修改发生。部分输出截断后补读必要区段，未当作完整结果。旧 Node/VM 证据不重复、也不充当此次真实账号证据。
