# Mail 来源隔离与延时 continuation 独立复核

**状态：FIXTURE_PASS_NO_REAL_UI_MAIL_MODEL_CALENDAR_CLAIM。**

执行者 A2；拥有目录仅本目录。总控 Root 修改产品源码；A2 只冻结来源、编写 probe/runner、运行真实 CardHost 隔离合成测试。13:04 开始，13:14:11 最终运行完成。

## 版本绑定

- rc17 readable：`4d6897472953daa50aa4e41e3092c45d08fff9044ccbc43d7a67c34263e4dc9f`。
- rc17 compact：`30ae1a7a5581fa716d6eb5c43bccbeb8377cc2c56418bbd323153b6051a064ff`。
- CardHost：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`，完整路径记录在 `rc17-r2/summary.json`。
- 20M instructions / 64MiB heap / 默认执行时间预算，未调高；实际 Card5276，不把源码 dependencies.lock 的 SDKda 解释为运行时已换成 Root 的新 SDK Shell。
- rc16 readable 62ae15ad90352ff8fb4feec629369b8076b2245f18811b574ee7f454bc8e41f2；compact 04dba16d0f788fcbf046814da18c5e86c4fe98eb7e04a351c4c10e1421785eca。
- rc15 实际来源为不可变 compact 881e5c6b548e03fcc12dde98bebae31d1488542a8dce736f817a4838b1a72854，baseline 第二轮使用相同字节，不逆造旧源码。

## 原始失败

`rc15-baseline-r2/flow/first/report.json`：先调用实际 `memory_remember_mail`，再 `mail_link_calendar`，报“同一来源 ID 指向不同位置”。用户来源与 claim 的 project_id/owner_id 不正确；Goal 已写入，但 calendar link 和 model candidate 没建立。5 项 PASS、6 项 FAIL，保留原记录。

## 最终 rc17 结果

9 组、248 项布尔检查全部 PASS。3 次真正第二进程恢复，使用相同隔离存储，无模型自动重放。

|组|首进程 PASS|第二进程 PASS（含独立 Python 语义读回）|结果|
|---|---:|---:|---|
|flow|26|18|PASS|
|recover|24|18|PASS|
|populated|34|18|PASS|
|revoke_early|18|0|PASS|
|revoke_late|18|0|PASS|
|session_early|18|0|PASS|
|session_late|18|0|PASS|
|revision_early|19|0|PASS|
|revision_late|19|0|PASS|

### 覆盖

- 手动记忆 `source:mail:<account>:<message>` 与任务 `source:goalmail:<goal>:<account>:<message>` 不冲突；分别写入正确邮件项目、归属、账号，当前 Chat 焦点可以不同且不被改写。
- 同一邮件、同一 Goal 重复进入不新增 Goal/source/claim，不重复调用 model transport。
- 模拟旧 planned Goal 已保存但关联缺失：恢复只更新 mail_source.source_id，其余旧 Goal 字段保留；来源、claim、calendar link 与 Goal 一致。
- 原事件改期：实际 schedule_replan_original 的 calendar.get 通过合成 transport 返回明确原事件，仍保留同一 Goal、事件ID、旧消息历史；新来源ID与 Goal.mail_source/calendar link 一致。此处未执行 calendar.create/update。
- populated 在进入真实 mail_link_calendar 前独立写出 before-mail-link.json，明确 6 claims / 6 sources / 2 forget；先分别经实际 gm_save/一次 gm_forget 构造。正常分段完成，并重启全对象语义一致。
- 账号撤销、会话变化、Goal revision 变化，各在 phase1 前（0.01s）和来源写入后（0.075s）干预：保留干预时已发生的来源写入，不再写 claim/calendar link，不排队 model，pending 清除并给出变化错误。
- 重启：全部 Goal/link 字段由独立 Python json.loads 与基线比较；source/claim 恢复、scope、数量及原始主记录字节保持同时检查。

## 预算结论和限制

rc16 空库/恢复 2组86项 PASS；rc16 精确 6/6/2 状态 1组52项 PASS。这个轻量 fixture 未复现 Root 新 SDK 真实 UI 的 script time budget exceeded，因此不宣告该 live 错误不存在或已由本测试修好。UI redraw 被既有 harness 替换、资料短、宿主版本不同，均影响预算。rc17 分段方案的持久化与取消安全性在此实际 CardHost 已验证；真实 Shell 窗口的性能及模型结果须由 Root 验收。

所有 Host transport 已由明确 fixture 替换：model.complete 仅排队，不执行付费/本地推理；calendar.get 返回 synthetic event；其他外部动作拒绝。未读取 private profile/账号/Secret/生产数据，未操作 GUI、未改主文件、未 Git commit/push。隐藏窗口证据只用于执行，不能充当视觉截图。

## 保留的夹具失败与修正

- rc16-r1：新 probe 参数 scope 为 Splash 保留字，编译错误，改用 mem_scope；原日志保留。
- rc16-r2/r3：把同内容 JSON 的不同序列化顺序当成变化。隔离资料经 Python json.loads 全等；最终改为原始文件/字段及完整对象语义比较，不删检查。
- rc15-baseline-r1：真实碰撞后不存在 calendar-state，夹具 finish 读文件失败；r2 添加存在性判断，保留产品碰撞 FAIL。
- rc16-populated-r1：两次 gm_forget 产生4墓碑；r2 只显式遗忘一次，实际进入前6/6/2，再通过52项。
- rc17-r1：recover 固定0.35s检查早于分段结束，盘上随后出现关联；改用最多40次0.05s就绪轮询，不重复执行动作、不改 Host预算。populated 的名称误含 late，改为匹配 _late/_early 后缀。最终 rc17-r2 全9组重跑。

## 复现

使用本目录 run.py 指向冻结的 `rc17-r2/readable-bundle/main.splash`、上述 readable SHA、summary 中 Host路径，并指定本目录内一个新的 --out；--cases 可指定9组。不能复用已有输出覆盖历史。

每组：first/report.json、first/runtime.log、first/state/muse-goals；有恢复的组还含 restart-runtime.log、restart-report.json 和 semantic-readback.json。
