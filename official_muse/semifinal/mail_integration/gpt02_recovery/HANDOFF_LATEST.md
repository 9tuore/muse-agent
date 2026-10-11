# Handoff

## Task
ZC02四原生L3初始probe适配新8227 preflight；基线33de17ce。

## Result
PREPARED_NOT_TESTED。原首次candidate query→ready/binding nil/owner无写→原history结清idle/current→独立第二次原create。通用query仍另一个turn。

## Changed
仅四初始probe新增相同helper/PREFLIGHT_PARENT/静态身份。其余原流程逐字保留，四restart/parent/run/parser未改。

## Tests
源33/33、parser44/44、8227实际prompt唯一events limit200/Once；八prepare原函数逐字。CAS恢复路径错误保留后修正。Kernel/VM/GUI/Cargo运行0。

## Commit
见最终回复，未push。

## Remaining
Root新8227重签后按PREFLIGHT_PARENT串行执行full/deny/CAS/delete及恢复。

## Important Boundaries
无Main/SDK/包/history/资料写入，不造ready/回执，不stub binding，不借旧源PASS。
