# MUSE-RUNTIME-CLOSURE-NIGHT-002

状态：开发中 / PARTIAL。开始北京时间2026-10-10 23:41:52，07:00冻结大改，08:00停止交付。

## 当前十项实况

1. 完整新Host：尚未构建；旧稳定Host276b2b68与活动rc17保留。
2. Muse本人ID的Calendar Relay：BLOCKED，组件检查不代替实际调用。
3. 内置Calendar查询/创建/同ID修改/删除：已有组件证据；完整Muse候选尚未验收。
4. Mail compose/review_send/status：应用协议已有；新完整宿主未运行，原生审阅仍需可信本人动作。
5. 行动链：开发源已有真实状态投影；尚未进入活动根包。
6. 根bundle晋级：未进行；rc17原字节保留。
7. 同候选最终20次：未开始；待核心冻结及宿主接通。
8. GitHub：本轮起点15cc5718已独立核对；本轮新提交未同步。
9. DSL：现有Memory DSL/GoalSpec核对中，计划复用授权、存储与状态供人和Agent阅读，尚未宣称全量接入。
10. 人工缺项：真实Agent consent及Mail原生审阅，准备具体入口后集中提出；当前先继续隔离实现。

## 单元A：发布布局与便携测试

- 默认publication-layout只检查真实根bundle；--migration显式核对旧别名和可选原字节参考。
- 合法后缀对齐锁定Hub95e4831，允许AGENT.md和skills文本；拒绝原生文件、包内symlink、逃逸资源。
- python3 -m unittest discover -s scripts/tests -p test_release_layout.py -v：9/9，exit0；合成布局含有效PNG，仅校验器测试。
- python3 scripts/check_release_layout.py --migration --out build/runtime-closure-20261011/baseline-layout.json：layout PASS/exit0；原rehearsal签名仍是正式publisher准备的阻塞。
- python3 -B -m unittest discover -s official_muse/semifinal/stability_integration -p test_check_host_log.py -v：10/10，exit0，明确合成。
- 显式读取旧compact refusal与源码timeout目录：PASS_PRESERVED_FAILURE_CHECK/exit0；不是新实机通过。缺产物NOT_TESTED/exit2保留。

## 现场保护与下一步

基线Commit15cc57187358b2ab09c089c5232ef74d4c30d53c；分支codex/muse-pivot-20261010。完整逐文件摘要在ignored build/runtime-closure-20261011/baseline.json；根main.splash摘要90351cba、472628字节（770540是六文件包总量，不是单个源码长度）。不修改旧安装、活动Host、生产数据或既有未提交工作。

下一优先级：完整Shell与真实注册/Relay/consent → 薄Calendar/Mail适配与共享DSL → 同候选冻结、实机验收及20次。上游旧Issue不重复新建或再发组件进度评论。
