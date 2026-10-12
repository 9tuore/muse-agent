# ZC-05 验收准备交接

结果：准备可接收；正式三轮 NOT_TESTED，0 GUI 输入，0 原生截图，0 PASS。

修改：根 `MUSE_USER_ACCEPTANCE_MATRIX.md`、`MUSE_USER_ACCEPTANCE_3ROUNDS_REPORT.md`；证据根下 acceptance-matrix、summary、SHA manifest 和三个 round-index；ZC-05 cases、准备/校验脚本、原生 UI helper、结果记录器、交接模板及说明。

验证：`prepare_acceptance.py --validate` 输出 PREPARATION_PACKET_VALID，81/243 唯一且全部 NOT_TESTED；3 个 Python 文件 AST 解析通过。未运行 GUI、业务动作、模型/邮箱/日历或宿主重启。

后续护栏修订：双 marker/生产 state 路径、完整 Kernel/Launcher/config/catalog/Git/版本/Bundle/插件身份、控件 enabled/真实窗口/pane 全矩形、原生视觉证明和跨轮候选一致已补齐。`check_guards_offline.py` 的14项合成反例通过，无GUI/网络；裁切/无视觉证明不点击。交接需补齐新版模板字段，生产目录清单由总控提供，不扫描或读生产资料。

独立PRE_FLIGHT已完成并回交9799窗口：3张未修改原生截图全部view_image查看；初始正文全黑，OctoSense顶栏主题下拉能绘制，Muse标签点击后菜单关闭且正文仍黑。仅2次真实非敏感UI输入，无业务/权限/账号/重启/DB动作。preflight/保存身份、3snapshot、UI日志、逐图观察、Bug UA-PREFLIGHT-001及SHA manifest；正式结果矩阵未改。诊断noGauss启动包不是最终三轮候选，不据本轮宣称最终产品失败或通过。版本实际为0.4.0-rc7，不记录旧source字符串版本Bug。

边界：root 基线 8da96cfdf582fc7e7e1e8a7eda4e902f75090f6a；生产端口 9696 从未访问；没有读取生产账号、凭据或私有资料，也未使用开发者 PASS 作为依据。根 CURRENT_STATE/HANDOFF 不在本 Agent 文件所有权内，本目录保存自己的状态与交接。

未完成：固定候选包/host/plugin 哈希和专属 fixture GUI 交接；原生 helper 的实际运行验证；全部 243 GUI 验收格；最终实现范围、失败 Bug、独立读回与限制结论。交接模板本身不授予窗口权限。

接收后：总控可 cherry-pick 准备提交。正式测试在同一独立树中追加 attempt 目录及实际结果，失败不覆盖；修复后按新冻结身份重跑受影响三轮。不 push。
