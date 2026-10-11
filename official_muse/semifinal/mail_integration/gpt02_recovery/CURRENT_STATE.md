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
