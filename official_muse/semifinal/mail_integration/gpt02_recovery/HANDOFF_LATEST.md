# Handoff

## Task
GPT-02，codex/gpt02-mail-memory-recovery；中央8279a606/源码271b1beb。接官方Calendar候选到当前事项行动链。

## Result
PARTIAL：实际patch和定向测试已交，中央正式main/VM/GUI未改未测。

## Changed
calendar-chain.patch仅6个既有函数及Calendar UI+绑定/精确回执helper；identity固定271b1beb→0c17e4cc。生成器、test、CALENDAR_CHAIN.md和证据。旧私有日历、Mail暂停与模型选择字节保持。

## Tests
2026-10-11：Node提取17实际函数，最终r7 65/65；临时JSON回读、精确add/get、身份/版本迟到、错配/错误/取消、重启未知不重发、归档完整绑定、写入失败等。git apply --check --unidiff-zero通过；只有6个旧函数变化。五次适配器错误保留，不算产品失败。

## Commit
本地提交见最终回复，未push。

## Remaining
中央真实VM/正式包GUI/本人批准。候选联动限上海整分钟；Mail确认依赖、改期和整体完成未接通，UI如实提示。

## Important Boundaries
用户选择事项后才绑定候选，派发前存goal/plan/project/owner/account/request，回调存turn；只Host broker精确配对可verified，模型text不算成功。历史保留、unknown不重派、旧身份版本不投射。零GUI/Cargo/外部模型/SMTP/秘密，不伪装owner，不恢复旧EventKit。
