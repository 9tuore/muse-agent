# Handoff

## Task
GPT-02，codex/gpt02-mail-memory-recovery；中央88e5ba28/source0c7，只读核Chat bad_request契约及最小修复。

## Result
PARTIAL：SDK Request::from_args拒绝顶层messages，根因确定。Root已并行加补丁，独立生成结果e2f3ab87与其当前source逐字一致。

## Changed
model-input.patch/identity、生成器、定向测试、MODEL_INPUT.md和证据。仅wrapper 6增1替、529其他函数不变；历史进入input.messages，保留schema/class/URL/usage/identityguards。

## Tests
2026-10-11 Node四个真实函数投影：before-r4 24/26，两项契约失败；after-r4 26/26。临时git apply/check及SHA读回通过。初次源码漂移拒绝及r1-r3六份适配器错误保留，非产品错误。

## Commit
本地提交见最终回复，未push。

## Remaining
Root已有补丁无需重放，直接新候选GUI短问→计划→日程候选→明确选事项→add/get精确核验→关联未发送草稿。

## Important Boundaries
Node fixture不是真实VM/模型/GUI通过；零外部调用。未写共享main/SDK/Bundle/用户资料，未Cargo/GUI/凭据操作。旧compact提交6e5仍未实际VM运行。
