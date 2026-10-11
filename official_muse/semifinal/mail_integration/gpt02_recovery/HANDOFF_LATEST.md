# GPT-02 Mail recovery handoff

## Task

基线e962e4183d844002a22e4f8c91268dfb5b004b19；独立worktree/branch codex/gpt02-mail-memory-recovery。只改本目录。

## Result

PARTIAL：source→claim中断重复问题未复现；原core_add_source已有幂等复用。转向已复现的Host failed_before_delivery只读回执始终被留UNKNOWN，生成最小正式源码补丁提案。

## Changed

mail-terminal-recovery.patch新增严格terminal分类并沿原receipt phases恢复未投递状态；正式main未改。prepare_patch.py/patch_identity.json可重建；test_recovery.py与evidence保存前后结果；host_receipt_status_probe.splash供中央真实VM补验，未运行。

## Tests

2026-10-11：before-r3 26/27，唯一失败before_delivery_reconciles_unsent；after-r4 44/44通过。source/claim重启后各1条，cancel/DRAFT、UNKNOWN、accepted未收件与身份/正文保留。before-r2另为投影适配器语法错误，原stderr保留。

## Commit

本地提交由交付回复列出；不push。

## Remaining

中央应用补丁后用配套官方Splash/Host验证；Node投影不是官方VM、native审批或live SMTP证据。本人登录/真实批准留中央串行。

## Important Boundaries

无GUI/Cargo/模型/真实账户/发送。patch只read status，新增无Host调用、不重compose/review，不伪造审批。
