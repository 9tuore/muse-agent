# Handoff

## Task
A4暂停后，按Root指定ed4874先做矮窗r2，通过后补普通/窄窗。

## Result
3组、12检查组PASS。实际990×380、990×539、412×813。结果重开/结果页可见，首尾对话/输入/滚动/快捷页面/折叠恢复通过。

## Changed
仅a2/rc51新增R2证据、报告、退出回执；脚本/Host/源码/35秒/预算均未改。

## Tests
2026-10-06串行全新profile；每组退出后source仍ed4874且8517释放。最后窗口03:22:25+08退出，后续无native测试。

## Commit
本地精确文件提交，未push。

## Remaining
Root/A4可继续最后10+5。原矮窗r1失败保留；r1/旧宽窗是5c182b67 readable，本轮是ed4874 compact，不混为同字节重放或四尺寸本轮执行。

## Important Boundaries
纯合成card-host fixture；结果卡不是动作回执。零外发，未控制8493/主profile；不宣称cold稳定性或最终Shell整链通过。
