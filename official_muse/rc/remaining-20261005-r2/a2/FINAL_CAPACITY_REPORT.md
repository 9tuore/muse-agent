# A2 最终容量、关系与存储独立复验

日期：2026-10-05，Asia/Shanghai。

**隔离容量节点：FIXTURE_CAPACITY_PASS。项目总体：PARTIAL，未宣告READY。** 此报告覆盖此前增量的当前结论，原报告和全部失败保留。

## 冻结与边界

- 最终真实源码SHA：`5e9318464390741f31c5deb12cf94571521aefd22efe2d02d1731ba0174c6f0a`。
- 压缩源码SHA：`4ce3a734d94e1cedea8260f9b74ca54ce2a8339d0db2e6200f702b5f2bb71ee6`。
- 实际CardHost SHA：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`，不是最终原生Shell Host。
- 默认指令、堆、时间与存储预算均未提高。实际 jailed fs，独占8509，每轮只退出自己启动的进程。
- 仅使用本聊天合成资料；没有访问生产数据库、账号或凭据，没有实际模型、SMTP、Calendar、GUI、OS重启或安装验收。
- A2只写本目录。源码优化由总控完成；A2没有修改产品、宿主、Git、稳定安装版或其他应用。
- `RC28_FINAL_FUNCTION_BINDING.json` 独立确认当前main与本次冻结全文相同，438个具名函数相同，global_memory模块的gm_save和gm_scope_valid同步。

## 真实保存流程已通过

`capacity-relation-short-circuit-r1` 从空的隔离记忆库开始，逐条调用真实 `gm_save`：

1. 64条真实保存及独立提交。
2. 对第一条调用真实 `gm_correct`，revision变2，原document保存在history，新增来源。
3. primary与当前记录相符，backup精确等于更正前64条快照。
4. 第65条保存拒绝，primary/backup和记录数量不变。
5. 退出第一个Host，第二个全新Host使用同一隔离数据，等待真实gm_boot分批校验，再验证恢复。

首进程 **12断言PASS**，第二新进程 **8断言PASS**，运行日志无预算错误；没有预种子绕过保存。尚未执行forget；这是一次完整容量流程，不是长期稳定性或任意负载保证。

独立Python对照实际63条、64条、更正后及恢复后的文件，**14项PASS**，记录在 `CAPACITY_FINAL_READBACK.json`：

- 新增第64条时，前63条claim/source全部字段不变。
- 更正后其他63条claim全部字段不变，原64条source全部字段不变。
- target旧document与history精确一致，scope不变，source_history只追加新来源。
- tombstone未变，backup/primary/activity的恢复字节正确。

## 关系与失败守卫

最终同源码 `relation-guards-r1` **10组68断言PASS**（原cowguard一组13，以及九个关系组）：

| 组 | 实际结果 |
|---|---|
| 同subject/predicate、不同value且可访问 | 新增contradicts，绑定原claim ID |
| 同subject但跨项目scope | 无关系，旧字段不变 |
| 旧account未授权 | 无关系，旧字段不变 |
| 旧user_id不同 | 无关系，旧字段不变 |
| 旧claim已deleted | 无关系 |
| 旧claim被有效合成tombstone禁止访问 | 无关系；此种子用于访问拒绝，不代表实际forget清理通过 |
| 旧claim已过期 | 无关系 |
| predicate不同 | 无关系 |
| value相同 | 无关系 |

保存前持有的旧数组、claim/source引用与提交后字段均保持不变。cowguard还验证空内容、未授权账号、缺scope与storage-not-ready拒绝，拒绝不改盘。

新旧成对校验对照在最终同源码 `final-pair-guards-r1`：有效候选及缺source、重复claim/source/旧ID、跨source scope、非法/缺失/self/deleted relation、坏hash/time/history、旧scope额外字段和坏tombstone。结果及精确计数见 `PUBLIC_FINAL_RESULT.json`；原探针的错误slice日志在 `pair-guards-r1` 保留，修正仅改测试构造。

## 其他辅助证据

- 新旧scope-cache 14变体、29断言PASS：canonical/literal、缺字段、额外字段、错误类型、legacy模式、warm后新增extra/type或切换legacy。helper在最终版本字节相同，未因版本标签全重跑。
- preserve helper真实文件14断言PASS，另独立磁盘8项PASS：valid已知原字节、不同valid记录、malformed原件精确保全、已保全幂等、另一文件的保全碰撞拒绝且不覆盖，以及真实目录导致native read/hash错误并阻止commit。fs没有被替换；最终malformed原件及正确副本都存在并有实际SHA。
- phase诊断使用本聊天合成62条记录，真实validation与commit分别在独立timer调用。da91版本观测：prepare0.846 / validation40.682 / commit32.167ms；1e565版本观测：prepare1.244 / validation26.406 / commit10.366ms。仅单次墙钟观测，不是可控性能对比或固定上界。

## 失败与负载均保留

| 目录 | 保存进度 | 实际primary / backup / activity条数 | 状态 |
|---|---:|---|---|
| capacity-r1 | 46 | 47/46/46 | ERROR，活动序列化span；未到更正 |
| capacity-deferred-r1 | 29 | 30/29/29 | ERROR，提交/读回span；未到更正 |
| capacity-copy-on-write-r1 | 45 | 46/45/45 | ERROR，提交末尾span；未到更正 |
| capacity-pair-r1 | 62 | 62/61/62 | ERROR，提交guard附近span；未到更正 |
| capacity-canonical-header-r1 | 61 | 62/61/61 | ERROR，提交/读回span；未到更正 |
| capacity-preserve-fast-r1 | 30 | 30/29/30 | ERROR，scope校验span；未到更正 |
| capacity-scope-cache-r1 | 53 | 53/52/53 | ERROR，claim校验span；未到更正 |
| capacity-scope-paused-r1 | 61 | 61/60/61 | ERROR，backup写/读回span；未到更正 |

span是VM报错位置，不能当作单条语句的根因。旧日志、状态与源码保留在本地，没有挑选删除失败。

现场曾观测load122.63/76.69/40.54。总控协调A4暂停自己专属编译组后，A2只读确认三进程T，在19:52:26做一次同1e565冻源复验，起跑load25.28/53.03/39.17；仍失败，结束已通知总控恢复。A2没有给其他进程发signal。最终成功起跑19:56:33，load5.92/26.96/31.09，rustc仍活跃。代码和环境都有变化，不能把成功单独归因某一优化，也不能说故障仅由负载引起。

## 收口

可以记录最终同源码一次真实64保存、更正、65容量拒绝和新进程恢复通过，以及关系/校验/保全守卫证据。仍缺原生UI满容量交互、真实用户profile同流程、长期高负载稳定性、实际forget全流程，以及其他整链门槛。原T05/T20和项目总体不能据此全部升级。

小范围Git白名单见 `SAFE_STAGE_LIST.txt`。只列合成探针、runner、报告、summary和独立读回；不列bundle/state/截图/实际全库，不自动stage或push。

本地诊断runner依赖本轮保留的历史模板与Card5276路径；没有验收全新checkout独立执行。成品安装、模型与实际Shell验证由总控另记。
