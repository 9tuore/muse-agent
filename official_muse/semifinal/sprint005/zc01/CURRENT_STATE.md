# SPRINT-005 ZC-01

基线：own codex/gpt01-calendar-history / ea4d6e52；中央8da96cfdf582fc7e7e1e8a7eda4e902f75090f6a；Main caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce。13:11:25开始，19:11:25高风险冻结，20:11:25截止（2026-10-12上海）。仅拥有本目录/自有测试；Root独占生产GUI9696，本站不读生产profile/Secret/Keychain，不给其他聊天发送消息，不写Root/Main/Host/生产数据，不发布/Tag。

正在完成三项：真实Agent前置条件与profile_unresolved诊断；官方Rust/OctoScript/比赛与AppHub交付核查；专属隔离ZC05 Calendar稳定ID读回。

已确认：Kernel源码在中央build/runtime-closure-kernel-r1/src，真实Git b0759a57719fd35b3a2da1c5d969bc67538ed516。profile_unresolved在ui_protocol_transport.rs10408/23331，profile_is_known查store或runtime，再准备session；不能当Calendar Relay失败，也不能拿fixture model充当真实连接。SDK展开目录git rev-parse继承Muse HEAD，不是upstream revision；preparation.json写SDK4ccf8e06/Hub95e4831a，但旧root dependencies.lock.json仍7f962547，需要明确区分。

严格无Calendar/Mail工具模型连接入口：SDKmodel.complete/complete/wire.rs直接one-shot，只有固定system+task/schema/input，无tools/memory/history/browsing；source要求task/input/schema/class?/allow_urls?。成功仅是选中/回退provider的direct inference，不证明MiniMax-M3 Agent或工具链。另有os.ai-providers的llm.test固定ping/1 token（Responses16），无tools/私人上下文，但UI入口的compiled系统pack仍在核对。

Models里程碑：实际formal-r3 Host内解析出7个系统pack，os.ai-providers脚本21763 bytes/c6680953…与SDK相同且含run_test/llm.test。裸文本未命中是Base64打包所致，不能判缺包。搜索输入ai-providers/models无结果也不足判UI缺失：menu源码只把叶/alias连字符转空格，query未同步转换，且只搜索当前子树。合法入口与固定无工具payload见DELIVERY.md；Root可用AI providers/providers/ai核对。实际模型请求0、GUI操作0；配置metadata不是连通性。

资源闭合：formal与zc05-preflight-r1的211个host-runtime文件名称/大小/hash逐一相同，无symlink，结果model_resource_audit.json。Root报告originalR5同state单Host重启已恢复正文（PID27091/native715），首用Deny状态亦已持久化，根因未单独隔离；不改GPU。实际resource分支/路径未观测。

官方网页已browse：旧Design-Flow重定向App-Flow；当前GitHub-attested AppHub流程、bundle不带native代码、native/system需shell release，Rust/WASM另一条。AppFlow技术规则不是比赛组织规则；官方链接create.gosim.org/agenticapp26页面JS，正文待读取。Desktop RC6发布日期2026-10-11/sourcef9f6fea9与我们的固定Host分开，未下载/安装新Host。

旧Calendar helper源码/历史证据保留，但own build/gpt01-calendar-history只有sdk/app-peers，没有现场旧target/binary。将准备严格拒生产/R5 root的独立owner-store读回，显式区别服务API调用；不能假装历史binary目前可用。ZC05专属fixture路径/合成标题/稳定ID白名单和symlink拒绝是必要边界。不大规模编译或重复已通过164等测试。
