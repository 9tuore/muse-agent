# A4 current state

PARTIAL：rc49两个Host基础题0/2。模型原始JSON回放与UI文本、573/600输入和8/7输出完全相同，无截断；故本例语义错误由模型生成，非响应错取。官方非思考采样唯一尝试未改善，未改launcher/config、Host、权重、Root主入口/8493、生产profile或预算；不push/重包。8次推理后自有进程全部退出。

Fresh profile另有FAIL_BEFORE_MODEL：先保存最小chat，再同步补defaults；gm_has预算错误留下focus_owner/goal_id缺失，发送直接读取失败。仅合成资料在FRESH_PROFILE_CAUSE.json，交Root定位；A4未改主源。

rc50-r2独立矩阵已完成：冷启动8/10、重开5/5，整体FAIL。cold-02编译完成后eval UI初始化预算失败，view=false/ui不存在；cold-07日历Button可见高度16小于驱动24要求，导航未完成且无编译/[E]，不推断Calendar语义失败。10个新进程、重开同PID；最终合成资料SHA不变、model ledger未创建。自有PID774退出，8492释放；不改Host/预算/Root8493或49 ZIP。

rc51-r1矩阵FAIL/产品UI PARTIAL：只有cold01/02有效完成。cold03 launcher超时40秒原因未明；cold04–10在quit404/连接拒绝处未执行新open，5重开因无服务未发生。不能写10次产品编译失败。数据SHA不变，已知两PID退出/8492空。Root已修launcher退出协议，A4只读核对，下一轮同51/seed于鲜目录r2；旧r1不覆盖。

rc51-r2仍FAIL/PARTIAL：5有效cold、0有效reopen。05 quit RemoteDisconnected；06/08原40秒超时未定位；09/10旧端口未关闭；重开无有效PID。最终资料SHA不变/无ledger/8492空。启动器期间仅移除unused import，字节重建已验证；旧r2不覆盖。

停机后Root移交launcher一文件：A4补RemoteDisconnected及quit5秒读取，6ba4af24/SHA04a23e0c，仍TCP确认关停、整体40秒/Host/预算不变，产品源未改。

最后rc51-r3已结束，整体FAIL/PARTIAL：7有效cold+5/5同PID重开；02/09 launcher40秒超时未定位、03旧端口未关，失败缺log不证明无E。所有完成case原门槛通过；最终资料SHA不变/无ledger，PID41984及全部已记录PID退出，8492释放。启动器/主矩阵/wrapper SHA前后一致；wrapper仅最终退出清理改TCP确认。原r1/r2/r3全保留，不追加native测试，Root8493可继续原工作。

模型入口REPORT.md / MODEL_DIAGNOSIS.json / PROMPT_COMPARISON.md；启动入口RC50_MATRIX_REPORT.md及RC51_R1/R2/R3_REPORT.md和各SUMMARY.json。所有原失败保留；旧包补清39a1a080，49 ZIP保留。
