# ZC-05 验收准备交接

结果：准备可接收；正式三轮 NOT_TESTED，0 GUI 输入，0 原生截图，0 PASS。

修改：根 `MUSE_USER_ACCEPTANCE_MATRIX.md`、`MUSE_USER_ACCEPTANCE_3ROUNDS_REPORT.md`；证据根下 acceptance-matrix、summary、SHA manifest 和三个 round-index；ZC-05 cases、准备/校验脚本、原生 UI helper、结果记录器、交接模板及说明。

验证：`prepare_acceptance.py --validate` 输出 PREPARATION_PACKET_VALID，81/243 唯一且全部 NOT_TESTED；3 个 Python 文件 AST 解析通过。未运行 GUI、业务动作、模型/邮箱/日历或宿主重启。

边界：root 基线 8da96cfdf582fc7e7e1e8a7eda4e902f75090f6a；生产端口 9696 从未访问；没有读取生产账号、凭据或私有资料，也未使用开发者 PASS 作为依据。根 CURRENT_STATE/HANDOFF 不在本 Agent 文件所有权内，本目录保存自己的状态与交接。

未完成：固定候选包/host/plugin 哈希和专属 fixture GUI 交接；原生 helper 的实际运行验证；全部 243 GUI 验收格；最终实现范围、失败 Bug、独立读回与限制结论。交接模板本身不授予窗口权限。

接收后：总控可 cherry-pick 准备提交。正式测试在同一独立树中追加 attempt 目录及实际结果，失败不覆盖；修复后按新冻结身份重跑受影响三轮。不 push。
