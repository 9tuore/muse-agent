# ZC02 SPRINT-005

正式launcher路径修复：prepare_profile/bootstrap现在生成root/kernel/.octos/profiles/_main.json，匹配WorkBuddy无条件CoreDir覆盖；路径/完整无key envelope/当前endpoint/无业务seed/FileVault五项通过。未启动Kernel/GUI。另核官方SDK mail_demo配置无需Rustbuild，但WorkBuddy会unset MAKEPAD_APP_CONFIG，需Root隔离launcher保留该配置，不能仅env冒充已启用；Demo没有独立收件或UNKNOWN。R8 driver只有CLI测试，不是GUI MockTransport入口。TLS提案零context及SHA gate，不申请新权限，Root才集成。

2026-10-12 13:41前首个方案/最低可执行输运已准备。当前Main caa99c57及官方SDK identity记录；自有Python服务真实TLS IMAP/SMTP、独立receiver子进程、before-DATA拒绝/收件后UNKNOWN断线、无key模型OpenAI JSON/SSE及实际offered-tool计划均可启动。新协议17/17、SSE/公开profile4/4，未跑Kernel/GUI/旧107测试。合法_main配置及显式OCTOS_APP_CORE_DIR/FileVault模式准备，未seed业务库；只读readback snapshot-only可用，validator定向验证待续。

formal-r3保持Main/Host/Kernel不变时，Mail自签名CA不存在官方入口，HUMAN_REQUIRED或Root选择专门fixtureHost；给Root最小loopback/双marker/profile匹配/CA hash提案，TLS verifier/审批不弱化，未应用/编译。模型/只读工具不受此阻塞。服务运行在自有build/gpt02-sprint005-protocol-r1/profile动态端口，ready.json/evidence给实际端口；生产9696/资料/Keychain/真实邮箱未操作，无发送/其他聊天消息/子Agent/push。
