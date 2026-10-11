# Handoff

## Task
GPT-02，codex/gpt02-mail-memory-recovery；中央88e5ba28/source0c7，只读核Chat bad_request契约及最小修复。

## Result
PARTIAL：SDK拒绝顶层messages，Root原patch e2f3ab87独立核对及全部六处调用参数补验通过，中央当前source相同。

## Changed
model-input提案及test_model_boundaries.py/证据。仅wrapper 6增1替，历史进入input.messages，保留schema/class/URL/usage/guards；无新增main修改。

## Tests
2026-10-11 before24/26→after26/26；补验r5 112/112（含26），12真实函数+2闭包、六实际args、nil/默认/false和非Chat input、19种发送前/迟到守卫。临时apply/SHA通过；旧错误和三个新适配器错误保留。

## Commit
本地提交见最终回复，未push。

## Remaining
Root已有补丁无需重放，直接新候选GUI短问→计划→日程候选→明确选事项→add/get精确核验→关联未发送草稿。

## Important Boundaries
Node fixture，六完整caller/SDK parser/schema compiler/VM/模型/GUI未执行，零外部调用。未写共享main/SDK/Bundle/用户资料，未Cargo/GUI/凭据。旧compact6e5仍未VM运行。
