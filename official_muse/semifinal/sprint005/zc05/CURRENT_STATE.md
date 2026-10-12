# ZC-05 当前状态

阶段：PREPARATION_ONLY。81 原子功能、243 三轮结果全部 NOT_TESTED。固定候选身份与 GUI 所有权未交接，不访问生产端口 9696。

独立工作区：`/Users/mima0000/.codex/worktrees/muse-zc05-acceptance/Agent APP黑客松`。接收基线：`8da96cfdf582fc7e7e1e8a7eda4e902f75090f6a`。

已完成：产品说明/UI 入口覆盖、三轮用例、可恢复矩阵及 round 索引、原生 UI 单次输入与截图 helper、手动观察结果记录器。只修改 ZC-05 被分配的文档、证据准备目录及本目录；未改生产源码、bundle 或其他 Agent 文件。

实际验证：prepare packet 离线检查通过；81 ID 唯一、243 test/round 组合唯一、每轮 81 条、全部 NOT_TESTED 且无尝试/截图/结果，准备 SHA manifest 相符；三个 Python 文件 AST 语法解析通过。以上均非 GUI 功能 PASS。

护栏补齐：真实双 FIXTURE_ONLY marker、生产 state 路径重叠拒绝、Kernel/Launcher/config/catalog/Git/版本/Bundle 指纹和插件哈希、禁用/越界/对应 pane 裁切拒绝、逐图原生视觉证明绑定当前 snapshot、跨轮候选 key 一致。14 项离线合成反例检查通过，Root 给的裁切 Install 矩形被拒绝；完整 rect 缺原生图检查仍拒绝。无 GUI/网络调用，不计验收通过。

下一步：收到总控统一冻结 package/main/manifest/host/plugins 身份、专属 fixture 端口/PID/窗口 ID/数据目录和正常重启命令后，核对实际 GUI 可见功能，逐项执行正常、交互变化、重启重复三轮。合成外部输运通过只记 SIMULATION_PASS，缺前置记 BLOCKED/HUMAN_REQUIRED，不可达记 NOT_IMPLEMENTED。

待关注但未判定：旧根 bundle 与可读 source 字节/版本不同；旧系统日历路径是否不可达；窄范围自动安排是否具有正式可见入口。最终以冻结包 GUI 发现为准。
