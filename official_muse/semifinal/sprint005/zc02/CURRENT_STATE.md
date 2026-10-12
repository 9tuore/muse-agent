# ZC02 SPRINT-005

S005UA Mail R1公开输入已准备，未注入：working/s005ua-mail-r1/incoming.json现有四字段schema，收件gui-reader/发件receiver，标题SPRINT005-ZC05-S005UA-MAIL-R1、明确2026-10-14 15:00–15:30 Asia/Shanghai。chat-mail和mail-calendar-policy为对应工作副本，原39样本未变。现有incoming只生成时间戳Message-ID，不支持请求的固定s005ua-r1-mail头；正文追踪标签不冒充该头，README要求Root保存实际返回ID/UID/SHA，未改服务/SDK存储/GUI。证据s005ua-mail-r1-working-inputs，0控制写端点/网络测试，未重跑78。

冻结rc8身份补记：当前f9e94877与冻结f00比较，18个模型流程/schema函数全部逐字未变；实际新增ac_local_run_readback，仅修改已有ac_projection。catalog及函数身份已绑定f9，39响应SHA不变；f00 catalog/身份/manifest另存evidence，原f00核验与失败记录不覆盖。新证据rc8-f9-source-identity.json仅记录现场比较和已有f00报告适用性，本次没有重跑78样本/网络协议、没有GUI/业务DB/shared target操作。新服务与正式三轮由Root/ZC05负责。

rc8身份补记：当前f00c963b与冻结947比较，18个流程函数17 unchanged/1 changed；send_chat只改两条提示为打开「来信与结果」，其余源码差异仅ResultContent标签选中颜色。模型schema所在函数逐字未变，39个样本响应文件SHA不变；catalog/当前函数身份绑定f00，新静态字段核验78/78。旧947 catalog/函数身份/manifest另存evidence，原flow-sample-contract.json及旧失败记录不覆盖。证据rc8-f00-source-schema.json、flow-sample-contract-f00.json；0服务测试/GUI/Kernel/Cargo/Root target操作，UA-PREFLIGHT-002修复效果仍由实际GUI验收。

ZC05关键模型流程交付：flows/catalog含39显式控制样本，按3次验收repeat及单轮t1/t2/t3区分；实际chat reply、Goal objective/source、Goal summary、Chat Calendar五字段、Chat Mail三字段、Mail editor两字段及MailCalendar policy分别处理。静态78/78，新增晚回包HTTP绑定4/4；response_bound可定位捕获后GUI变化，配置改动不改变旧响应。Root源本轮漂移到947c5291，旧SHA生成被正确拒绝后明确freeze947；18个相关流程/schema函数与caa逐字一致。ZC05_MODEL_WORKFLOWS.md给可直接CLI/GUI步骤、scope/更正/遗忘/候选/手写/迟到/错误验收；PRODUCT_PATH_GAPS仅源码指出自动AI记忆卡与opened Goal聊天编辑未实现，不称真实GUI复现，不写生产补丁。未重跑17/107、未构建SDK、未操作GUI/Kernel/业务DB；Root模型管理Connected仅其实际回报，不升级本轮检查。

读回/计划新unit最终21/21（旧18保留）：scopeA/B错召回、遗忘history残留、unknown新attempt/收件、错profile、空expectation、链接/缺文件拒绝，SDK mailbox正文Source SHA一致/变化/缺失检查。RootGUI profile从未seed业务库；unit数据只在独立test root。Root所需实际build_host命令/packaged resource closure/新CA exact-test提案在BUILD_CA_HOST.md；CA patch静态scratch/SHA与原verifier六项通过，未编译，Root独立testHost才可采用；registry/git缓存存在但warm target未定位。R8不可作为GUI入口。实际Main普通chat schema仅reply，默认服务已修正，多action模型样本按真实字段准备，control.py可在旧服务显式设置，不改GUI业务数据。共享源码/Root9799/生产9696/Kernel/GUI/Cargo/Keychain/真实发送均0。

正式launcher路径修复：prepare_profile/bootstrap现在生成root/kernel/.octos/profiles/_main.json，匹配WorkBuddy无条件CoreDir覆盖；路径/完整无key envelope/当前endpoint/无业务seed/FileVault五项通过。未启动Kernel/GUI。另核官方SDK mail_demo配置无需Rustbuild，但WorkBuddy会unset MAKEPAD_APP_CONFIG，需Root隔离launcher保留该配置，不能仅env冒充已启用；Demo没有独立收件或UNKNOWN。R8 driver只有CLI测试，不是GUI MockTransport入口。TLS提案零context及SHA gate，不申请新权限，Root才集成。

首轮方案/最低可执行输运已准备。当前Main caa99c57及官方SDK identity记录；自有Python服务真实TLS IMAP/SMTP、独立receiver子进程、before-DATA拒绝/收件后UNKNOWN断线、无key模型OpenAI JSON/SSE及实际offered-tool计划均可启动。新协议17/17、SSE/公开profile4/4，未跑Kernel/GUI/旧107测试。合法_main配置及显式OCTOS_APP_CORE_DIR/FileVault模式准备，未seed业务库；只读readback snapshot-only可用，validator定向验证已另记。

formal-r3保持Main/Host/Kernel不变时，Mail自签名CA不存在官方入口，HUMAN_REQUIRED或Root选择专门fixtureHost；给Root最小loopback/双marker/profile匹配/CA hash提案，TLS verifier/审批不弱化，未应用/编译。模型/只读工具不受此阻塞。服务运行在自有build/gpt02-sprint005-protocol-r1/profile动态端口，ready.json/evidence给实际端口；生产9696/资料/Keychain/真实邮箱未操作，无发送/其他聊天消息/子Agent/push。
