# Handoff

## Task
MUSE-NIGHT-001 官方接口整改；A 独立分支 codex/muse-semifinal-a-20261009，基线9b247c89。

10月10日12:14关机恢复后，用户明确延长到今天北京时间17:00，16:00冻结大改。当前A HEAD c4fcbc08，稳定数据和代码未回退。关机期间无持续测试。自动化已按新截止更新。B确认停写，A已接管行动链独立工作树唯一写入权；不是新子代理。

## Result
PARTIAL。活动rc17未覆盖，rc18可读源准备中。

## Changed
Mail compose/review/status与宿主版本绑定；内置Calendar方向固定，私有桥隔离；接口矩阵与合成验证。

## Tests
10月9日参考官方Splash VM：Mail协议11/11 FIXTURE_PASS；两VM进程中断/恢复7/7变体通过，r1/r2支架错误FAIL保留。rc17稳定基线20/20真实Shell冷启动，16对话/256消息/64记忆保留；不作为rc18最终候选PASS。独立device研究22/22，3轮精度失败保留。evidence在official_muse/semifinal/evidence。原始冷启动捕获保存在ignored build/semifinal-cold-baseline-raw，有逐文件SHA清单。

## Commit
本地小步提交，未push。

## Remaining
新Host下载与构建、官方准入、Agent真实工具选择、可信手势发信、新候选20次冷启动和全链。rc2官方Mac成品arm64，本机Intel；前轮网络失败保留；12:34官方Tag完整源码已获取，SHA核验/status干净，setup准备锁定依赖，尚未安装。A在行动链隔离树有只读MVP与fixture，状态fixture已通过，原生可见节点/连接线/展开/旧结果切换通过；响应式和恢复仍在测，未合入。#182/#427已公开，#427 comment6083645335含实际两文件代码补丁；未接受或安装。完整清单MUSE_NIGHT_TASK_LEDGER.md，新截止17:00。

## Important Boundaries
合成协议不代表SMTP/日历/原生确认成功；用户选择内置日历，OS研究不进入默认；不改旧安装/生产/Tag。
