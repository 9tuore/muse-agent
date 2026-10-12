# ZC02 SPRINT-005

读回/计划新unit最终21/21（旧18保留）：scopeA/B错召回、遗忘history残留、unknown新attempt/收件、错profile、空expectation、链接/缺文件拒绝，SDK mailbox正文Source SHA一致/变化/缺失检查。RootGUI profile从未seed业务库；unit数据只在独立test root。Root所需实际build_host命令/packaged resource closure/新CA exact-test提案在BUILD_CA_HOST.md；CA patch静态scratch/SHA与原verifier六项通过，未编译，Root独立testHost才可采用；registry/git缓存存在但warm target未定位。R8不可作为GUI入口。实际Main普通chat schema仅reply，默认服务已修正，多action模型样本按真实字段准备，control.py可在旧服务显式设置，不改GUI业务数据。共享源码/Root9799/生产9696/Kernel/GUI/Cargo/Keychain/真实发送均0。

正式launcher路径修复：prepare_profile/bootstrap现在生成root/kernel/.octos/profiles/_main.json，匹配WorkBuddy无条件CoreDir覆盖；路径/完整无key envelope/当前endpoint/无业务seed/FileVault五项通过。未启动Kernel/GUI。另核官方SDK mail_demo配置无需Rustbuild，但WorkBuddy会unset MAKEPAD_APP_CONFIG，需Root隔离launcher保留该配置，不能仅env冒充已启用；Demo没有独立收件或UNKNOWN。R8 driver只有CLI测试，不是GUI MockTransport入口。TLS提案零context及SHA gate，不申请新权限，Root才集成。

首轮方案/最低可执行输运已准备。当前Main caa99c57及官方SDK identity记录；自有Python服务真实TLS IMAP/SMTP、独立receiver子进程、before-DATA拒绝/收件后UNKNOWN断线、无key模型OpenAI JSON/SSE及实际offered-tool计划均可启动。新协议17/17、SSE/公开profile4/4，未跑Kernel/GUI/旧107测试。合法_main配置及显式OCTOS_APP_CORE_DIR/FileVault模式准备，未seed业务库；只读readback snapshot-only可用，validator定向验证已另记。

formal-r3保持Main/Host/Kernel不变时，Mail自签名CA不存在官方入口，HUMAN_REQUIRED或Root选择专门fixtureHost；给Root最小loopback/双marker/profile匹配/CA hash提案，TLS verifier/审批不弱化，未应用/编译。模型/只读工具不受此阻塞。服务运行在自有build/gpt02-sprint005-protocol-r1/profile动态端口，ready.json/evidence给实际端口；生产9696/资料/Keychain/真实邮箱未操作，无发送/其他聊天消息/子Agent/push。
