# 统一0.4.0-rc2：同候选Mail→Memory→事务→行动链联调

准备状态：只读实际完整SDK和2253e9f0主源；本聊天未启动GUI/Cargo/模型/账号或发送，不修改SDK/main/旧dirty文件。中央唯一构建与执行。候选必须用中央新冻结0.4.0-rc2完整Host、配套Kernel、准入Muse bundle、manifest及源SHA，不能拼r7/r8 ownerMail、旧reference fixture、root rc17证据。

## Discovery/ABI的确定结论

实际构建Cargo.toml:435-437将appstore/hub指向 `build/runtime-closure-full-shell-r1/hub/`；核该路径 `crates/appstore/src/host_api.rs:76-103`，不是只凭旧checkout。

`runtime.list {}` 回调data是 `{schema:1,platform,runtime_features:{feature_name:整数ABI},methods:[{implemented:true,supported:平台bool,configured:null,authorization:"checked-on-call",descriptor:{name,version,capability,...}}],notice}`。没有顶层 `apis/abi` 字段，`configured:null`不是账号已配置或方法不可用。`runtime.describe {method:...}` 对runtime feature返回 `{method,version,kind:"runtime-abi",implemented:true,supported:true,callable_via_host_request:false,...}`，没有descriptor；这是ABI，不可host.request它作为动作。

主源429-450的official_method_available/official_discover与这份契约相符：descriptor.name、version==1、implemented/supported；runtime_features必须对象。`mail_enabled:2831` **只检查host.capabilities()中mail**，所以discovery失败不会直接让邮箱页未启用，但会使compose前的接口门禁拒绝review。缺实际mail grant/准入失败/consent未完成才会阻断Mail调用或启动。这里是源码核对，完整候选真实runtime.list响应仍需中央从该Muse实例实际取证。

当前Mail `api_methods()` 只登记 `mail.compose/compose_status/review_send/send@1`（public_review.rs:249-261）。accounts/add_account虽然真实服务支持，却未在这份发现表登记；不要把它们缺descriptor误判为服务不存在，也不要把它们放required ABI导致合法app被准入拒绝。`HostApiRequirements.check_available`使用**精确**ABI版本（不是最小版本），required未知/版本不等直接拒绝；字段仅required/optional两个method→整数map，`.sheet`方法禁止声明。没有fs.sha256/fs.sha256_file的runtime feature注册证据，不得把猜测storage/fs摘要ABI加入required。实际已核feature注册名：storage.binary_write、video.playback_controls、app_policy.device_consent、app_tools.dispatch；是否已初始化仍需真实runtime.list。

如需声明本轮Mail要求，合法片段为（仍不授予权限）：
```json
"host_api":{"required":{"runtime.list":1,"mail.compose":1,"mail.compose_status":1,"mail.review_send":1}}
```
保留capabilities中的mail/storage；model声明不能用本聊天的无模型流程证明已配置。不要声明mail.sheet.submit/cancel/review_close；这些只属宿主sheet。required只应覆盖候选真实必需且已注册的方法；平台macOS支持review，agent_access为foreground-only。

## 中央同候选最小执行顺序（无模型、无真实发送）

1. 冻结记录同一Host/Kernel receipt/manifest/installed bundle/source及运行PID；root rc17保留。在标准r8/新rc2 Host里从合法安装的 **Muse实际manifest ID** 前台打开（当前源码原ID muse-goals；以新manifest最终值为准）。使用真实App Hub准入，不复制账号设置/凭据，不以os.mail/独立测试app身份代替Muse。Native只读原型仍不是完整Muse Mail页。
2. 在该Muse实例确认host.capabilities含mail/storage，并真实runtime.list，按上述字段核三composer/review方法version1 supported；保存非secret元数据。若被准入/consent阻挡，明确HUMAN_REQUIRED/ADMISSION_REQUIRED，不改policy/身份。先暂停mail_watch，不让连接账号后自动轮询、AI分析扩为此最小测试的额外动作。
3. 同Muse点“连接账号”，本人先取消一次宿主sheet；应得到Sign-in cancelled，mail.accounts仍只显示原有此app授权账户。本人再从同Muse进入sheet登录QQ，授权码仅本人在native sheet输入。add_account成功返回{id,address}，同Muse accounts是数组[{id,address}]，核该id。os.mail登录/owner accounts不能代替这一步。未本人登录可完成其他工程联调，但不得造account granted。
4. **Mail→Memory需真实消息来源**：由本人选择同账号里一封明确用于测试的合成内容邮件，或本人先自行准备一封自收件测试信。本驱动不发该信、不读取私人其他邮件；只在Muse选择该测试邮件。核mail.message返回id/subject/body与选中account；按真实UI选project/owner并“记住邮件”。`memory_remember_mail:2917-2948`用实际正文fs.sha256、mail:account:message locator、runtime_receipt source、external_claim claim，scope含account/user/project/owner。不可将本地伪造mail_selected对象、独立app回执或compose草稿称真实收件来源。
5. 同Muse记忆页核source+claim引用、正文摘要、source SHA、scope和revision；重启同候选/同隔离profile后回读。实际fs摘要失败/读写异常保留失败，不换假哈希。再用合成值做一条明确用户纠正/忘记，核历史与tombstone、访问范围；不批量扫描私人Memory。用现成UI路径与已有边界，不开启新大fixture测试。
6. 同Muse选择“自己写回复（不调用AI）”或手动新邮件入口，输入本人自地址、唯一case subject与纯合成body；保留来源/Memory refs。核Goal/run/action存在并绑定实际request_id、payload、account、project/owner与同revision，不调用Goal裸函数造完成。邮件编辑或Memory refs失效应撤销旧preview；不能让旧approval对应新正文。
7. Muse精确预览后普通确认按钮只请求native review：实际路径 `mail_send_step→mail_compose_before_review→mail_review_host`。新compose由Host生成compose_id/revision，Muse保存后才review。核返回account/to/subject/body与context.snapshot完全相同、持久host_compose_id/revision；review_send携带它们和完整文本。API准备/后台保存不算SMTP/Person批准。
8. 本人只点native **Back to editing**，不点Approve & Send。实际public_review.cancel返回精确 `Review cancelled; nothing was sent`（无句末点）。主源4687回调识别该错误，`mail_send_receipt_step` phase0恢复DRAFT并清attempt/preview、保留正文和Host composer ID；phase1 action=failed；phase2绑定run=failed；phase3 MAIL_NOT_SENT活动。核这些实际落盘/回读状态；failed是“明确未发送”的当前内部记账，不称发送失败后重试。UI不会授权自动再次review。
9. 用同Muse账号与返回compose_id只读 `mail.compose_status {account,compose_id}`。Host cancelled review可能保留awaiting_approval attempt，不能要求状态一定cancelled；应没有SMTP accepted/receipt/sending，且同publisher/account/正文/revision保留。取消回调和Host状态分别存证，不拿owner历史draft_id替代。
10. **UNKNOWN保持/恢复必须真实有限试验或诚实未测**：本轮无批准/发送时，不能把取消强称UNKNOWN。可由中央在尚未批准review阶段关闭自己Muse/正常重启，观察action in_flight→unknown及Host只读状态；此处属于中断取消/恢复，不模拟SMTP不确定性。若要测试真正SMTP UNKNOWN，需另行明确本人发送授权与真实故障证据，当前不执行。未知结果只read status，禁止recompose/review/resend；accepted只是服务受理，不能mark verified/run completed或独立收件通过。
11. 正常停止同候选进程、quit0、退出后日志无Script错误，并保留失败/中断旧证据。验收标签拆开：同Musegrant、实际消息→Memory、事务恢复、compose原生取消、UNKNOWN（若实际测到）、真实发送/收件/Person（当前NOT_TESTED）。窗口/卡片/编译不等于行动成功。

## 最后工程缺口

- **正式准入与同app账号**仍是live入口，不由root manifest、discovery或ownerMail登录替代。
- **Memory source/claim并非单一原子事务**：memory_remember_mail依次core_add_source再core_add_claim；claim失败会留下已保存source，重试路径需核真实恢复/去重，不宣称已具跨两写原子性。目标/run/action的core_commit_goals是另一事务域。
- **回执分phase落盘**：mail_save→core_finish_action→core_finish_run→activity各步失败有保护，但不是Host与Muse跨进程原子提交。必须在同候选核中断后不重复动作；旧reference通过不能补新Host证据。
- **哈希Native ABI**已实现不等于有discovery登记，不能编造required ABI。三composer方法discovery正常时不需重写官方发现解析。
- **Calendar仍独立缺口**：主源calendar_enabled=false，历史calendar.*走拒绝适配；r8 ownerCRUD不能替代Muse Relay，本文不扩该分支。

源码依据：实际hub/appstore/host_api.rs，hub/app-contract/host_api.rs；SDK Mail lib.rs:687-759,848-881，drafts.rs:1111-1248,1322-1371，public_review.rs:119-261，connected_review.rs:113-114,325-336；Muse主源429-450、2831、2917-2948、4646-4759、5397-5420。以上为源码证据，不是本聊天执行的live结果。
