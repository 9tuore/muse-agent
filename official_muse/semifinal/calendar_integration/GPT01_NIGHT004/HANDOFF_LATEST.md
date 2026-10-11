# Handoff

## Task

NIGHT-004 GPT01：Root contained-r1 bounded query FAIL的只读定位与最小fixture契约修正。

## Result

TEST_EXPECTATION_ERROR；原Root FAIL保持原样，candidate preflight尚未触达。官方events使用end>=from且start<=to含端点重叠。此前读反local_stamp(true/false)，contained/adjacent预期0错误，两入口现修为1。

## Changed

只改contained/adjacent入口数字、相关说明、只读证据与R7准备记录。Main/SDK/Relay/model不改。R7 prepared绝对路径和Root命令见overlap/ROOT_R4_INTERVAL_HANDOFF.md。

## Tests

原resolved args精确from16:10/limit200/to16:20，canonical digest5da0f132与真实Broker receipt及call/done audit一致；person lane/turn/toolcall/session/persisted/terminal ok严格关联。返回原事件1，七字段与checkpoint/owner一致，owner count1/SHA103a5a86不变。9个离线断言PASS，原report仅8checks/FAIL保存且未进新candidate。official parse_time/stamp/local_stamp与Relay/scoped_args→ServiceCall已核对。新R7实际source8227三例338functions/184globals逐字准备通过，仅PREPARED_NOT_RUN。没有再跑Kernel/VM或改写原结果。

## Commit

当前本地修正提交见Git/聊天，未push。

## Remaining

Root以新独立fixture执行R7 contained/adjacent。Main仍按半开区间将adjacent判conflicts0；bounded官方结果1不等于产品冲突1。不可把此前置fixture失败报告成产品preflight失败。

## Important Boundaries

旧失败保留，不补PASS。Main/SDK/包/状态没有写入；未启动Kernel/GUI/Cargo。原Host权限和提示词不隔离工具的限制保持。
