# GPT-02 定向恢复状态

实际结果为PARTIAL；补丁未应用正式源码。source→claim重复恢复未复现，不改已有幂等流程。原core_add_source相同locator/hash/excerpt/scope直接true；重启从JSON回读来源，claim重试仅落一次。

实际备用缺口：官方SDK `drafts.rs:961-975` 将SendFailure::BeforeDelivery落盘为draft.status/attempt.status=failed_before_delivery。原Muse mail_check_host_status只接纳accepted，已确定投递前失败仍永远UNKNOWN。源码绑定合成fixture复现此错误；新增helper要求最终attempt operation_id非空、revision/status及精确to/subject/body匹配，accepted还要求receipt.accepted=true；仅可靠failed_before_delivery沿原unsent receipt phases恢复DRAFT正文、action/run failed。真正unknown/cancelled/awaiting_approval继续保留，不批准、不重发。Host角色/账号绑定的现有callback校验原样保留。

验证入口（新out路径；before预期exit1，after预期exit0）：
```sh
python3 official_muse/semifinal/mail_integration/gpt02_recovery/prepare_patch.py
python3 official_muse/semifinal/mail_integration/gpt02_recovery/test_recovery.py --phase before --out official_muse/semifinal/mail_integration/gpt02_recovery/evidence/before-new
python3 official_muse/semifinal/mail_integration/gpt02_recovery/test_recovery.py --phase after --out official_muse/semifinal/mail_integration/gpt02_recovery/evidence/after-new
```

最新before-r3 26/27、after-r4 44/44。证据保留r1/r2，before-r2是新增receipt phase投影适配器语法错误（不是产品失败）；修好适配后before-r3仍有目标失败。实际提取core_add_source/core_add_claim/mail_send_receipt_step及新增helper并投影到Node，ASCII合成数据，验证intrinsics与commit故障注入为fixture适配器，持久化真实临时JSON；这不是Splash语义完整模拟/官方VM/真实Host/真实两进程重启。重启在fixture中从真实JSON重建内存，不夸称OS进程重启。commit/callback权限边界仍需中央真实VM。

`host_receipt_status_probe.splash`（8向量）可在中央应用补丁后复用已有 `semifinal/tests/run_official_api.py --source <实际含helper的冻结源> --probe <本probe绝对路径> --host <已核reference> --host-cwd <已核cwd> --out <中央新build目录> --port <空闲>`，此处未运行。完整Host后续再核同候选真实status callback/receipt phases；不将reference VM代替Host/native批准。

根main/bundle、受保护Python核心、SDK、共享Cargo target均未修改。未读凭据、未GUI/登录/模型/发送，不push。补丁仅针对基线source SHA，中央若已有并发改动先核上下文，不能强制套用或覆盖正式源。

最终补丁是zero-context diff（避免补丁文本自身空白context造成diff-check噪声），必须先核patch_identity.json的基线source SHA，再使用`git apply --check --unidiff-zero <patch>`；本聊天仅执行check未应用。中央应用也需`--unidiff-zero`，源已漂移则重新生成/手工审阅，不强行覆盖。after-r3为zero-context投影适配器插入位置差一行的历史结果，未匹配expected source SHA，不作为最终身份通过证据；after-r4已修正并强制核预期cc3f17cd，44/44。历史证据未覆盖。

## 真实VM补验（最新）

按中央授权固定9695、只读指定binary/cwd、隐藏窗口。完整mail_check_host_status→mail_send_receipt_step真实异步链before-r3 33/37（四项目标失败），after-r1 37/37，实际磁盘readback通过。每轮仅5次合成compose_status，compose/review/send为0；两轮正常Remote quit/exit0、退出后无Script错误。新增REAL_VM.md、real_vm_summary.json和evidence/real-vm，旧Node/错误fixture结果保留。正式main仍未应用本聊天patch，中央独立按函数位置应用不能替代此处源SHA身份。Memory source→claim尚无真实VM结果，不借Mail37项升级它。

2026-10-11 Mail实机前置检查：MAIL_LIVE_PREFLIGHT.md+prepare_mail_live.py核中央固定SDK 8文件SHA；源码/新稿/已有稿3项生成通过，非法ID/源码漂移2项拒绝通过。没有mail.status；前台/Agent返回不同；公共review取消可能保留Host awaiting_approval。Keychain路径哈希及app grant限制已按源码定位，未读取凭据/账号状态。中央独占实际Host/GUI，零请求/发送/构建；37/37证据不重复。

2026-10-11 登录隐式恢复修补：watch-pause.patch仅删除mail_add_account成功分支中的旧注释和mail_watch_toggle（2行），保留mail_accounts_load、失败/取消路径及默认enabled=true/现有30秒schedule。没有增加即时poll：账号刷新设置mail_pending，poll守卫会跳过；刷新结束后的既有timer使用最新granted accounts。迟到登录/账号刷新不再写enabled，也不替换当前选中的账号。
固定中央源码SHA86f86e3ee0263bb3d34bfb92d3ed7f9d2952e3fdc949cf4b9699085846552c09，预期4516b660e66a2d47365ee9dca31c58d1169b763e06bceb27918a2122c9d97d24；完整身份见watch-pause-identity.json。零上下文patch须先核完整SHA再git apply --check --unidiff-zero，来源已漂移时只按mail_add_account具名边界重新准备，不按行号偏移应用。
定向测试：test_watch_pause.py --source build/gpt02-watch-pause-source-r1/before.splash --phase before/after --out <独立报告>；Node提取4个真实函数fixture，before15/19（4个暂停恢复失败），after19/19，非法外部调用0。保留两次Node适配器语句分隔错误说明；不是产品失败。临时副本git apply --check通过、修补后完整SHA匹配。没有正式源码写入、GUI、Cargo、真实VM/Host/模型/SMTP/秘密操作。实际Splash VM未验证，等待中央协调；正式包由中央应用和验证。

2026-10-11 官方Calendar行动链提案：calendar-chain.patch/identity，中央新模型基线271b1beb→0c17e4cc，六个既有函数+Calendar UI及有界新helper。本人选择事项后结构化候选绑定goal/plan/project/owner/account/request/turn；Broker add/get精确配对才verified，未知/归档同候选不重发、身份版本迟到不投射。合成Node r7 65/65+临时副本git apply --check通过，全部非目标旧函数保持字节一致。不是实际VM/GUI/外部写入；Mail依赖/改期/整体事项完成未接通，UI明确提示。详见CALENDAR_CHAIN.md；零正式main修改/GUI/Cargo/模型/SMTP/秘密。

2026-10-11 官方Calendar→可选Mail草稿提案：calendar-mail.patch/identity 固定中央0c17e4cc→0c7f9812；复用compose/review_send/compose_status，保存goal/plan/chat/candidate/identity/event/proof，准备/预览无Host，未猜收件人。迟到scope不推当前完成，UNKNOWN不重放，原文/Host ID/有界旧回执保留；独立Mail action不改事项plan/version/run、不执行旧整体完成。最终Node r9 100/100、临时副本git apply --check+SHA通过、14既有函数变化/509不变；6次适配器错误证据保留，r6/r7旧SHA不算最终身份。详见CALENDAR_MAIL.md。实际VM/Host/原生审阅/收件仍待中央协调；零正式main/Bundle/SDK/GUI/Cargo/模型/SMTP/秘密，不push。

2026-10-11 中央已应用Calendar→Mail 0c7f9812后，新增calendar_mail_vm_probe.splash+calendar-mail-vm-expectations.json及CALENDAR_MAIL_VM_PROBE.md，供现有run_official_api.py --suite production真实VM执行。原业务/持久化函数不替换，仅既有UI三函数/transport；覆盖有效草稿/空recipient/手改重开、未verified、matter/user/project/owner/plan变化、迟到compose稳定ID+UNKNOWN、只读禁重发及普通Mail取消。只完成离线source/runner边界检查，508其他prefix函数不变；期待值不是PASS报告。未运行VM/GUI/Cargo/Node/模型/SMTP，未写正式0c7源码。中央执行与完整check集合核验待完成。

2026-10-11 Calendar→Mail VM r1 中央实测入口失败：ac_selected_chat不在runner prefix；正式let9771/9772及ac_field/ac_goal_allowed/ac_current_goal均在boot截断之后。原report/log保留中央build/muse-integrated-calendar-mail-rc4-vm-r1。本聊天仅修probe：逐字携带7个生产action-chain全局+3个所需真实尾部函数，未替换绑定/选择逻辑；更新probe SHA/来源哈希，40预期不变。离线核114可达函数调用/裸赋值声明及字节身份，不称VM测试。正式main/runner/Host未改，等待中央新out重跑。

2026-10-11 r2/r3中央启动解析限额（view=false、业务未到）后，只准备compact追加probe：现有compact_bundle.py仅作用合成部分，生产prefix、7尾部let/3真实函数原字节、全部字符串/换行/40检查保持。追加15973→13610字节，r3同runner候选537473；新calendar_mail_vm_compact.splash/identity及prepare_calendar_mail_compact.py。未重新VM/GUI/Cargo/Node，不能宣称解除启动限额；旧ERROR/log未动。现有--probe可直接选新产物，无runner补丁，正式main/dirty runner/Host预算不改。
