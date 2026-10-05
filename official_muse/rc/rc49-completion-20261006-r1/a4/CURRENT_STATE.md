# A4 current state

PARTIAL：rc49两个Host基础题0/2。模型原始JSON回放与UI文本、573/600输入和8/7输出完全相同，无截断；故本例语义错误由模型生成，非响应错取。官方非思考采样唯一尝试未改善，未改launcher/config、Host、权重、Root主入口/8493、生产profile或预算；不push/重包。8次推理后自有进程全部退出。

Fresh profile另有FAIL_BEFORE_MODEL：先保存最小chat，再同步补defaults；gm_has预算错误留下focus_owner/goal_id缺失，发送直接读取失败。仅合成资料在FRESH_PROFILE_CAUSE.json，交Root定位；A4未改主源。

rc50-r2独立矩阵已完成：冷启动8/10、重开5/5，整体FAIL。cold-02编译完成后eval UI初始化预算失败，view=false/ui不存在；cold-07日历Button可见高度16小于驱动24要求，导航未完成且无编译/[E]，不推断Calendar语义失败。10个新进程、重开同PID；最终合成资料SHA不变、model ledger未创建。自有PID774退出，8492释放；不改Host/预算/Root8493或49 ZIP。

rc51-r1矩阵FAIL/产品UI PARTIAL：只有cold01/02有效完成。cold03 launcher超时40秒原因未明；cold04–10在quit404/连接拒绝处未执行新open，5重开因无服务未发生。不能写10次产品编译失败。数据SHA不变，已知两PID退出/8492空。Root已修launcher退出协议，A4只读核对，下一轮同51/seed于鲜目录r2；旧r1不覆盖。

模型入口REPORT.md / MODEL_DIAGNOSIS.json / PROMPT_COMPARISON.md；启动入口RC50_MATRIX_REPORT.md / RC51_R1_REPORT.md及各SUMMARY.json。所有原失败保留；A4未修改产品源/Host/预算。旧包补清提交39a1a080，49 ZIP保留。
