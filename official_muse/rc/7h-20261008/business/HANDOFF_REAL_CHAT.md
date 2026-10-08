# Business 真实聊天交接

## rc17 compact 同候选链补证（2026-10-09）

**Scoped DRY_RUN PASS：30/30**。源 `90351cba7ec5c493befb6673212bfb1aa9639dbfbc2ce28b83e24b98f3e05bdc`；参考card-host `46a4d16dc4ac7cfcc33b866643e777524cdb8a87d2c5022d44ae1c24e8c5a0fe`。原chain.splash 20/20，原restart.splash新进程10/10；PID332→714，旧进程退出后才启动，seed goals字节绑定已核对。

rc17对rc15：315 Calendar/core/gm/schedule/storage/mail函数全部原字节；仅3个聊天函数变化、新增路由helper。与storage-shape旧候选比较，有授权查询/授权请求/mail_watch_boot三处差异，failure/recovery probe与合成be_boot未调用这些直接入口；恢复、UNKNOWN、receipt、settlement实际函数仍同字节。复用旧候选6故障场景、4组新进程恢复和rc15代表恢复/授权证据，全部保留原candidate/Host身份，不改称rc17重跑。未发现受路由修改影响的失败contract，无额外窄测需要。

`RC17_CHAIN_RESULTS.json`保存具体断言、SHA、PID、315函数字节审计及旧证据身份；`.local-state/route-rc17-chain-r1/`保存原始日志/状态。旧预算ERROR和未集成r1路由FAIL保留。业务侧无真实模型/邮件/EventKit，无可见UI或最终ShellHost验收；Root的Shell同候选全链是独立证据，不能与参考Host合并身份。只business文件提交，不push，测试结束，8661空闲。

## Post-window helper r2：DRY_RUN PASS，仍未集成

实际捕获源 `66790986b82a1a95c6c6b589720209b3df9af4a6869a60838ba767ce75be9197`，已包含中英冒号、但是/但分句（先但是再但）及重复否定前缀。参考card-host `46a4d16d...`。官方VM编译成功max_chunk28.763ms（预算未变），实际config action/schema **32/32检查通过**：原29项全部通过，追加“但是请不要”“也先不要”“请整理资料但不要发邮件”均goal_plan。31路由+1无模型/外部调用检查。

与r1 readable对比478函数仅chat_action_intent变化；config/send_chat/muse_model_request原字节不变。`ACTION_INTENT_POST_WINDOW_R2_RESULTS.json`、`chat_action_intent_r2.splash`及`.local-state/action-intent-post-window-r2/route/`保存结果。r1三个FAIL及原报告原样保留；本次不改主源码、生产资料或冻结rc16 bundle，不冒称rc16/最终Shell/真实模型通过。仅business文件提交，不push，进程结束，8661空闲。

## Post-window chat_action_intent 未集成修补：FAIL

实际readable源 `cd8bdf7831fc9a8307abc2479e5c4a2bd56a80733aa7cbcb7d4f06c450108e14`；参考card-host `46a4d16d...`。官方VM完成编译并实际调用生产chat_model_config，29检查26通过（28路由case，25路由正确、28返回schema正确、无模型/外部调用检查通过），不是Python镜像逻辑。

三个失败（期望goal_plan）：
- “请整理资料准备计划，但不要发邮件或创建日历。” → calendar_candidate。
- “请整理资料，不能发邮件，也不要创建日历。” → calendar_candidate。
- “请整理资料准备计划：不要发邮件，不操作日历。” → mail_compose。

原因定位：分句只包含逗号/句号/分号/换行，不包含冒号；否定前缀不识别但/也。正常goal_plan、禁止日历只聊天、正常日历/mail、资料/原文中动作词及其余混合否定通过。未改主源码，失败全部保留，rc16 bundle未集成，不改标rc16通过。

`chat_action_intent.splash`与`ACTION_INTENT_POST_WINDOW_RESULTS.json`；原始`.local-state/action-intent-post-window-r1/route/`。readable对readable比较：只chat_model_config改动、新增chat_action_intent，send_chat/muse_model_request原字节相同；模型原输入不变仅有静态证据，本轮没有模型请求。全部进程结束，8661释放；仅business测试文件提交，不push。

## rc16 焦点窄验（2026-10-09）

**DRY_RUN PASS（参考 card-host）**。源 `dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4`；Host仍 `46a4d16d...`。

477函数核对只有 chat_new_session/send_chat 改动，475函数原样，两函数外全部源码字节相同。真实VM 21/21 +独立磁盘8/8：新Chat继承项目/归属但messages/proposals/goal为空，旧Chat与Memory保持；同项目两归属合成资料以运行时观察的Memory ID验证检索不混用，返回旧Chat恢复原焦点；三个项目指代×缺项目/缺归属/两者缺失，九次实际send_chat均不开模型并保留输入/记录/requests。

第一probe 19/20：切回旧Chat后updated_at随chat_save更新，使全对象早期快照比较失败。已把拦截基线移到选择后，另加旧内容字段保留检查；生产函数未改，首FAIL留存。`FOCUS_R2_RESULTS.json`与`.local-state/focus-r2-r1/`含证据。最小TextInput、redraw/set_page等stub如runner摘要，无可见UI/真实Qwen/最终Shell证明。rc15链与恢复51+22仍绑定cef7d576原身份，不复跑、不改标rc16。

## r3 最新结果（2026-10-09）

**PARTIAL：r3 在参考 card-host 的 scoped DRY_RUN 通过；最终 Shell Host 未验。** 仅 business 文件修改，不 push。

- 最终源：`cef7d576b2de31e5c22a813e70e68370ff0ddd043ef1bbcd57acae75eb81b546`。
- 实测 card-host：`46a4d16dc4ac7cfcc33b866643e777524cdb8a87d2c5022d44ae1c24e8c5a0fe`。
- 最终 Shell：`276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638`，不能与参考 Host 混称。
- 实际 VM 异步授权 6/6：status pending 两次点击不提前发请求；稍后 status 回调发一次；inflight 重复点击不增加请求；授权回调清旗并刷新状态。生产函数原样，transport 回调合成。
- r3 完整合成链 20/20、独立新进程重启/召回 10/10。
- linked_memory_failure 停止/新进程恢复 3+12/15，PID13148→13211；22/22 独立磁盘检查。仅精确 calendar.get，无写重放，原 artifact/receipt/Memory SHA、Activity 与重复恢复稳定均核对。
- 合计 r3 51/51 VM +22/22 独立磁盘检查。r2 另30/30链/重启通过，未覆盖 paused mail_watch_boot 专项。

证据 `RESULT_COMPONENT_R3_RESULTS.json`；原始 `.local-state/result-component-r3-final-r1/`。未重跑未影响的18变体。首个授权 probe 漏启动 timer，未执行断言，保留 ERROR 后仅修 probe 重跑；r2 source-only 缺 manifest 初次失败也保留。Shell `--help` 实际启动 PID11311并取 News，已停止；现有 runner 验证接口为 card-host，最终 Shell 不计本轮通过。旧预算 ERROR 不撤销。

边界：真实 VM/fs/timers；合成 Mail/Calendar/Model，隐藏最小测试控件，无本轮真实系统CRUD/外发/推理或可见 UI 验收。Final Shell同版完整链仍需总控收口。测试已结束，8661空闲。

## 前次 cceeaa 证据（保留）

## 结果

仅业务DRY_RUN完成；源码/主bundle/生产数据未改。测试工具提交 `ad460d68`，报告提交见本文件所属commit，未push。

候选SHA：`cceeaa009f029c951d8e0a61a8a1cf0ac91802746868d2f38d3de892a889be78`。
Host SHA：`46a4d16dc4ac7cfcc33b866643e777524cdb8a87d2c5022d44ae1c24e8c5a0fe`，cwd `vendor/app-hub`。

18场景串行首轮16通过、2 ERROR，107/107已执行断言通过。late_model为eval脚本预算超限，delete_unknown为源码准备预算超限；原日志保留。同SHA/同预算单独串行重试2/2、10/10通过，覆盖18场景119/119；**不是一次全绿或冷启动可靠性通过**。

4组故障后全新Host恢复全部通过：linked_memory_failure、linked_result_failure、delete_receipt_failure、delete_accept_failure。真实8进程，49/49 VM + 80/80独立磁盘检查。旧进程退出后才启动新进程；恢复仅精确calendar.get，无update/delete重放。原artifact/receipt/Memory来源SHA、Activity增量及再次恢复字节稳定均核对。

## 证据

`REAL_CHAT_RESULTS.json` 含全部断言、SHA、PID/时序；`.local-state/storage-shape-real-chat-r1`、`storage-shape-retry-*-r1`、`storage-shape-process-recovery-r1` 保留原始证据。已接续并验证前任未提交的故障停止/恢复probe；没有删改旧红证据。

## 边界与剩余

实际官方VM/fs，transport合成；无真实模型、邮件或EventKit。总控负责LIVE和预算问题。本次测试进程已全部结束，端口8661释放；未接触8492，无需复跑已通过业务矩阵，源码换SHA后再绑定新候选。
