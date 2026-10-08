# Business 真实聊天交接

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
