# Legacy task-focus async fixture patch

legacy_task_focus_async.patch applies on the shared legacy suite after central envelope adaptation. patch --dry-run -p1 succeeded; static balanced delimiters and all 17 original check assignment names preserved. VM NOT_TESTED here. Patch SHA256 909914f6bd7ff889c43d36f4c54086e2850609a3ce3b36329fcd2369fc5f19d2.

Observed actual failure runtime-closure-legacy-task-focus-r2/run/runtime.log: model callback index0 with empty queue after production request split through start_timeout(0.05). Original fixture assumed synchronous dispatch. No production fix or budget change needed.

Added one bounded focus_wait helper: poll every0.03s at most100 retries (about3s scheduled wait per stage), require exactly one new callback; excess callbacks or exhausted wait record dispatch_wait_accounts/model=false, chat_stop and callback(false). Never index when not ready. This is fixture scheduling only, not a VM/Host budget increase. Failure flags stay false through later stages, so collecting later checks cannot turn timeout into PASS.

Original-session test awaits actual account preflight and model dispatch, retaining the session switch before preflight completion and same wire/session assertions. focus_card now returns via callback after actual model dispatch; revision/forget/revoke stages run existing validations only after proposal generation. Revocation awaits accounts then model, retaining the no-model-before-preflight check and original source/revocation assertions. Added wire!=nil safety does not weaken assertions. Correction/forget/ref persistence, original-session isolation, bounded context and forbidden tool checks unchanged.

Central alone applies patch to existing tests and runs current frozen source with explicit verified Host78ab9efce55cb692552a3566e7b579d2e8c304eadfd6b107c51b2efb027e34db and a new isolated output. Keep r2 failure. No repeat invocation of an out-of-bounds callback, no catch-and-ignore runtime errors; no report/failed check means ERROR/NOT_TESTED. Retain original runtime log and source/suite/Host identity.

This is SYNTHETIC intercepted model/mail accounts transport plus real isolated fs through production functions; no real model inference, Mail/Calendar writes, native consent or official full-chain proof. Existing component passes reported by central do not establish this legacy suite passing.

## Central actual legacy task-focus r4 closure

中央实际执行r4：正常检查13/13、failed=[]；suite SHA cfbb35b077fea601acb4b9c0bac976555994e2e0cc951c9bf266ec58c16b869b，source2253e9f00e8a0a57b713c316db2c40d26e5c937beef54703833a52cdee6cb7fa，Host78ab9efce55cb692552a3566e7b579d2e8c304eadfd6b107c51b2efb027e34db。公开摘要 official_muse/semifinal/evidence/shared-dsl-legacy-task-focus.json。原17 assignment names包含仅失败时出现的flags，不能写17项实际PASS。

保留r1缺manifest、r2队列out-of-bounds、r3三个Goal绑定检查false；r4是生产函数＋合成transport＋隔离fs的reference VM证明，不是真实模型、Mail/Calendar动作、native consent、官方full-chain或fullDesktop证明。本聊天未另启动测试或独立重跑。中央报告共享DSL已提交aec355db并精确验证开发分支远端；主源未改，fullDesktop仍由中央编译。此次仅追加owned说明，随后待命。
