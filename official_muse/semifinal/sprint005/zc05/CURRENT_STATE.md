# ZC-05 当前状态

阶段：PREPARATION_ONLY。81 原子功能、243 三轮结果全部 NOT_TESTED。固定候选身份与 GUI 所有权未交接，不访问生产端口 9696。

独立工作区：`/Users/mima0000/.codex/worktrees/muse-zc05-acceptance/Agent APP黑客松`。接收基线：`8da96cfdf582fc7e7e1e8a7eda4e902f75090f6a`。

已完成：产品说明/UI 入口覆盖、三轮用例、可恢复矩阵及 round 索引、原生 UI 单次输入与截图 helper、手动观察结果记录器。只修改 ZC-05 被分配的文档、证据准备目录及本目录；未改生产源码、bundle 或其他 Agent 文件。

实际验证：prepare packet 离线检查通过；81 ID 唯一、243 test/round 组合唯一、每轮 81 条、全部 NOT_TESTED 且无尝试/截图/结果，准备 SHA manifest 相符；三个 Python 文件 AST 语法解析通过。以上均非 GUI 功能 PASS。

护栏补齐：真实双 FIXTURE_ONLY marker、生产 state 路径重叠拒绝、Kernel/Launcher/config/catalog/Git/版本/Bundle 指纹和插件哈希、禁用/越界/对应 pane 裁切拒绝、逐图原生视觉证明绑定当前 snapshot、跨轮候选 key 一致。14 项离线合成反例检查通过，Root 给的裁切 Install 矩形被拒绝；完整 rect 缺原生图检查仍拒绝。无 GUI/网络调用，不计验收通过。

下一步：收到总控统一冻结 package/main/manifest/host/plugins 身份、专属 fixture 端口/PID/窗口 ID/数据目录和正常重启命令后，核对实际 GUI 可见功能，逐项执行正常、交互变化、重启重复三轮。合成外部输运通过只记 SIMULATION_PASS，缺前置记 BLOCKED/HUMAN_REQUIRED，不可达记 NOT_IMPLEMENTED。

身份纠正：Root已交接R5 transform后的实际可读/已签Bundle均为0.4.0-rc7，旧source rc18字串被transform替换；不将旧字串差异列为产品版本Bug。旧系统日历路径与窄范围自动安排的可见实现仍以最终冻结GUI发现为准。

PRE_FLIGHT独立原生发现已完成：9799/PID22287/native663交接后自行捕获并view_image查看3张原生图，顶部ShellBar和主题菜单可见，Muse/AppHub正文全黑。只点了两次可见非敏感顶栏；未点隐藏业务控件、未重启、未改软件/DB。窗口已回交ZC-00，不再访问。此诊断noGauss包非最终冻结；正式243格保持NOT_TESTED。详见preflight目录Bug UA-PREFLIGHT-001。

后续single-host PRE_FLIGHT：PID49780/native786实际正文可见。完成真实GUI Chat/scope/新会话检索、记忆更正/取消遗忘/确认遗忘、Goal候选/暂停恢复/模型建议/单次批准与独立真实产物读回。35原生图逐张查看，发现002候选指引及003本地已核验Goal链投影问题。Calendar仅填写查询，未提交，NOT_TESTED；Root要求切freeze后在16:10:18正常/quit且9799无LISTEN PID，GUI已回交。正式243格未改。证据为preflight/preflight-r3-single-host-independent/。

外部清理聊天删除本树历史跟踪文件；仅按Root允许恢复本Agent已有文件并使用Root现有remote.py，保留其他删除且不stage它们。后续commit须精确stage本Agent路径。
