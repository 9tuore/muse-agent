# NIGHT-004 Mail/Memory CLI 桥接

结果为 **PARTIAL**。真实官方 ScriptVm→生产 Muse函数→实际Rust Mail service→独立合成收件进程已接通。同一拟议候选3c7a2661的初始轮23/23、真正新进程重启轮16/16；完整L3/Calendar联动仍 **NOT_TESTED**。

新增native父驱动见[KERNEL_PARENT.md](KERNEL_PARENT.md)。四个显式Kernel参数、实际签名compact/upstream映射、第二封Mail原chat入口、native改期/邮件/必选完成检查已准备。dabfe定向无Kernel轮到真实chat建Goal后正确blocked，15项plan parser及actual compact重放通过；后半程与真实Kernel仍待中央执行。这不替换下列3c7组件证据。

中央d065ad15初次创建候选后，ac_projection→calendar_agent_project→calendar_agent_binding_current(nil) 读取plan_revision真实报错。nil-binding-guard.patch仅给包装函数加非对象检查。独立check/apply/readback及其余570函数字节一致性已验证，d065ad15→3c7a2661，本聊天未修改中央main。evidence/native-d065-error-r6保留原stderr和请求/回包。此前ebbc50b8初始通过、capabilities缺失及账号池未加载的两次恢复失败也保留。最小同名参数转发和短路检查实际通过，nil field检查实际报错；不把曾考虑的错误原因当结论。

## 固定源码入口

在GPT02自有worktree运行：/Users/mima0000/.codex/worktrees/gpt02-mail-memory-recovery/Agent APP黑客松。

`prepare.py --source SOURCE --source-sha SHA --probe PROBE... --out NEW_PREPARE` 严格核对冻结源，提取真实调用闭包，记录每函数/全局SHA。初始probe依次为mail_probe.splash、mail_memory_goal_probe.splash；恢复probe为restart_recall_probe.splash。全在本目录。

`run.py --prepared NEW_PREPARE/executed.splash --runner CLI_BINARY --mail-binary MAIL_BINARY --out NEW_OUT` 执行初始轮。恢复轮增加 `--state-root INITIAL_OUT/state --mail-root INITIAL_OUT/mail-state`，使用新的restore prepare与新的out。所有out必须新建并位于自有build。每轮冻结实际CLI/Mail二进制字节及SHA；复用state严格要求专用marker，不读取用户资料。

本轮实际参数：

- SOURCE：build/gpt02-night004-l3-source-r4-proposed/main.splash；SHA：3c7a2661d0e3571c0f9035a384575dc02abcd1ceb40b1cf525645a6f329fb6e5。中央采纳后必须用中央实际冻结源及其完整SHA重新运行。
- CLI_BINARY：/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松/build/gpt03-night004/target/debug/gpt03-night004-vm。
- MAIL_BINARY：build/gpt02-night004-l3-helper-r1/mail-runtime-r3-bin；SHA ba37b915b24917be68964c10c38409169b7162489fbd2de22c082a1e05055367。
- 初始实际out：build/gpt02-night004-l3-mail-memory-goal-r7；prepare：build/gpt02-night004-l3-prepare-r8。
- 恢复实际out：build/gpt02-night004-l3-restart-r5；prepare：build/gpt02-night004-l3-restore-prepare-r5；两个state-root指向上述初始out。

## Helper与验收边界

runtime-discovery-test-driver.patch是原night004/mail_l2.rs的test-only增量；用--unidiff-zero，先核r3 identity。caller合成为muse-goals。新增runtime.list、mail.message/list/sync/folders转给真实services::dispatch；cached incoming经原Store.save_mailbox写入。六生产Mail文件字节不变。旧L2 binary原路径恢复6b67963a，旧证据未覆盖。r1/r2 identity是历史版本，当前patch以r3 identity为准。

初始轮实际compose/review/status/draft engine，经单次MockTransport向独立Python stdio收件进程交付精确message_id/body/to。核对原收件数据后调用原mail_verify_received，这是显式fixture用户声明。accepted/verified不自行生成completed Memory。随后原mail.message读取cached incoming、memory_remember_mail写external_claim/hash/范围，gm_context/chat_apply_proposal建立单一planned Goal/native候选。

恢复轮真正结束原VM/RustMail/recipient并以三个新进程读取同一marker state；验证同compose/message ID、单次历史、新进程0transport调用、不重复发送、新chat原gm_context召回带来源引用的Memory、原chat_select_session/ac_choose_matter回到同Goal。显式fixture模型卡打开依赖记忆的手写草稿，原gm_correct改版后旧候选/草稿引用失效、preview清空、原文保留、0新发送。boot_restore排队的后台poll timer未执行，不宣称完整后台启动通过。

实际OS jailed文件IO与Rust sha2；原函数只将host.request转父进程，IO/renderer/page setter适配项逐轮记录。UI ports、时间/随机、timeout排队、host.capabilities声明mail、模型候选、cached incoming、Vault、审阅true/true、MockTransport和收件声明为合成边界。实际Mail service每次重新校验授权。

父进程原样保存method/payload/回包。octos.session.open明确返回unconfigured actual backend，候选停blocked，Goal仍planned；无host_calendar_receipt、kernel_persisted、Kernel History或成功状态合成。GPT01/中央实际Kernel JSONL就绪后再接原请求，prompt/binding/turn/history不改，不改回legacy Calendar direct cap凑通过。目前native同ID更新、最新authority派生Mail、native完成Memory和整体行动链未验。

evidence含原stdio、回包、调用数、执行源、最终状态；evidence-manifest.json给出67个文件SHA。summary.json分开标注范围及未验证项。shelved-kernel-proposal是未编译未执行的旧草稿，不能应用。无SMTP/Keychain、共享main/SDK/target/bundle或用户资料写入；未push。
