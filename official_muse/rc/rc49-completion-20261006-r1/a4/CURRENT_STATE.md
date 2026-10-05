# A4 current state

PARTIAL：rc49两个Host基础题0/2。模型原始JSON回放与UI文本、573/600输入和8/7输出完全相同，无截断；故本例语义错误由模型生成，非响应错取。官方非思考采样唯一尝试未改善，未改launcher/config、Host、权重、Root主入口/8493、生产profile或预算；不push/重包。8次推理后自有进程全部退出。

Fresh profile另有FAIL_BEFORE_MODEL：先保存最小chat，再同步补defaults；gm_has预算错误留下focus_owner/goal_id缺失，发送直接读取失败。仅合成资料在FRESH_PROFILE_CAUSE.json，交Root定位；A4未改主源。

入口REPORT.md和MODEL_DIAGNOSIS.json。Root后续候选另定；不把模型0/2或fresh失败标成通过。
