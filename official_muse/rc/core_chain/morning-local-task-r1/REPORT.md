# rc18 本地 Goal 分段执行独立复核

**状态：FIXTURE_PASS_NO_REAL_UI_MODEL_CLAIM。**

A2 仅拥有本目录，Root 是产品源码唯一写入者。13:29 开始，13:31:34 完成；未扩其他功能、未运行旧全套矩阵。

## 实际绑定

- readable `776965bbc2081edb31ca759265c288429f9a2a641d6157457ef905f66213e38c`
- compact `3d908cdca777c938f2543474964099c637caecf08dc98947b2190b70862742b8`
- 实际 CardHost `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。路径与版本在 rc18-r1/summary.json。
- 默认 20M instructions / 64MiB heap / 默认运行时间预算，未提高。与 Root 新 SDK 的真实 Shell 性能验收分开。

## 检查结果

4 组、71 项全部 PASS，两个独立进程重启通过。

|组|首进程|第二进程|结果|
|---|---:|---:|---|
|flow|16|8|PASS|
|card|19|8|PASS|
|switch_early|10|0|PASS|
|switch_late|10|0|PASS|

- flow：实际 make_plan 返回已保存 Goal ID；短延时后 chat_bind_goal 持久化并进入 Goal Detail；实际 plan_error 通过。
- card：实际 chat_apply_proposal 建立并消费 goal_plan 卡，依 make_plan 成功返回判断；保存后 card=opened，重复点击不新增 Goal；随后真实延时绑定并进入详情。
- 单次批准：实际 approve 创建唯一 running Run，revision 与 Goal 绑定；立即重复批准不新增 Run。
- 结果：实际 finish_result/finalize_result 写入并独立读取两条中文资料；Goal/Run=completed，结果带同一 task_id；verified_result 来源摘要 SHA 与实际产物匹配。
- 审计：同一 Goal/Run 的 Plan approved、storage write、readback 三条实际 Activity 记录存在；不是手工注入。
- 完成后再次批准：Goal 文件与结果文件字节不变，仍只有一个 Run。
- 重启：复用同一隔离 app-data 但真正启动第二个 CardHost；恢复同一会话绑定、Goal、Run、结果 SHA。goals/chat/memory/activity 主文件全部字节不变，无模型重放；再次批准仍不执行。
- switch_early：保存后、第一段绑定前换到真实 chat_new_session；新旧会话均未绑定该 Goal，Goal 保留 planned，无 Run。
- switch_late：旧会话已绑定后、开页前换会话；旧绑定保留，新会话没有旧 Goal，页面保持 Chat，不跳进旧详情，无执行。

## 沿用边界

以下实际函数与冻结 rc17 字节比较（没有重新跑原完整 fixture 矩阵）：

- plan_error: UNCHANGED
- core_start_run: UNCHANGED
- core_finish_run: UNCHANGED
- core_cancel_goal: UNCHANGED
- core_upsert_goal: UNCHANGED
- goal_spec: UNCHANGED
- chat_bind_goal: UNCHANGED
- core_commit_goals: UNCHANGED
- core_commit_memory: UNCHANGED

## 范围与限制

这里运行真实 CardHost、实际产品函数、独立 jailed fs；既有 harness 替换 redraw/set_page 的渲染和测试小控件，Host transport 明确使用 fixture。未发起 model.complete，本次 no_model_or_external_action 各组均通过；不能据此称模型或正式 Shell UI 验收通过。
本轮未读取生产/私密资料、未 GUI 操作、未改主源码、未提交或 push，旧安装版未触碰。Root 实机64ms中断/恢复由 Root 留证，本 fixture 的通过不否定实机失败。

## 复现与证据

run.py 指向冻结 rc18-r1/readable-bundle/main.splash、上述 readable SHA、summary 的 Host路径；--out 必须是本拥有目录中的新目录；--cases flow card switch_early switch_late。
每组 first/report.json、runtime.log、state/muse-goals 为实际记录；flow/card 另有 restart-runtime.log、restart-report.json 和冻结恢复 bundle。隐藏窗口仅用于执行证据，不充当视觉截图。
