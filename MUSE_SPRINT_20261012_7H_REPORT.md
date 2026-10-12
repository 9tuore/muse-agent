# 最新独立APP与实际限制

## 最新独立包与邮箱管理 · 2026-10-12 收口

桌面 /Users/mima0000/Desktop/Muse-rc8-正式版-20261012.app 已独立打包、codesign strict/deep验证、LaunchServices真实启动；Host x86_64，PID80429/native1718/9696，动态SecCode三项0。保持WorkBuddy同Launcher与原Host1eb/Kernel567、本地Qwen资源；不含模拟账号或任何生产资料。launcher只指向原正式资料build/live-acceptance-003/home，不复制凭据。

最新代码d550b975/source c4dc95e2/compact022f4460，新增官方mail.remove_account接口与每账号移除确认取消、多账号添加入口。独立真实VM24项FIXTURE_PASS，原4项父断言失败保留，未宣称GUI已移除/第二账号已添加。模拟Host21195已正常quit，模拟账号仍只在旧隔离目录，并未实际删除其存储。

当前生产资料已安装仍rc7/Main ef58430f，最新rc8更新权限页已真实打开，尚未完成本人Install；不能声称最新模块已加载或真实邮箱已测通。原正式资料和R5保留，未读/复制secret。邮箱发送、账号移除、多账号、邮件联动日历与新版三轮均未真实验收通过。

用户授权延长至21:11:25；仍未达全功能三轮。旧c098候选实际Calendar query/create有owner结果，但ZC03检查发现日志/后加文件SHA及新图视察缺失，证据计为EVIDENCE_INCOMPLETE待独立修复，不把2个原matrix SIMULATION_PASS写成完整验收。新d550不能继承旧候选轮次。完整身份与边界见integrated_release/evidence/sprint005-standalone-mail-accounts/；本机包不等于官方发布，未Tag/提交比赛。

# Muse SPRINT-005 七小时报告

当前收口结论：**PARTIAL_3_ROUND_ACCEPTANCE**。截至2026-10-12 19:59北京时间；任务13:11:25开始，19:11:25停止新增高风险产品改动，20:11:25截止，不自动延长。最新正式矩阵与逐轮截图以独立ZC05报告为准。

## 固定候选与运行边界

产品Git `9a61040c86efbe967b207a058f717733df422391`；Source SHA256 `c09836478cdd5fe58f34634002400ebc517185deb30fe4a29a469705c1ac6bd7`；compact Main `58b97a5691171722608868597105fbf16bd5577180f5a602a7bd8c04ee622b5b`；manifest `8d2f8ee9e9af8bcc3fec0edc6748dc1d04290b796ed2f2a77db64be682e19736`；catalog `b05b01b8dbba42d1d502e870a04be67d25682919f74b02f4941fe5a9719ad0a5`/sequence8；Bundle BLAKE3 `dcb9f1d575e2a9803cd975333d8fefe4d349b3024f1c28d57e7b3c1857745271`。

本机Intel候选 `build/sprint005/rc8-candidate-r4/Muse.app` 保留原Host1eb1887b。真正GUI验收包 `build/sprint005/zc05-final-r4/Muse.app` 使用Host `cea8ca71c52d0a3e3f8240feb226f75cce223b50c337433c3d33a632f7bec9a7`、Kernel `56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270`。实际PID21195/native819，专属port9799；数据 `build/sprint005/zc05-release-r4/state`。模型/IMAP/SMTP是严格loopback合成服务，owner os.calendar真实运行，生产资料未复制。GUI包结果不能外推生产Host、私人账号和MiniMax云模型。

## 本轮完成的实际工作

- 统一WorkBuddy启动参数与单Host互斥，保留原Host/Kernel身份。26实际签名stub定向检查及5打包检查通过；GitHub同workflow对1a674962的实际run38234049234为success。这不是业务GUI证明，旧guard失败保留。
- Memory跳过无关阶段Source/Claim遍历；384区间/22坏输入的定向VM验证保留，Source6.510→5.395ms、Claim15.451→11.785ms仅为该测量环境，不能写成整体GUI延迟。
- 修复实际独立预检发现的候选结果入口提示与本地Run行动链投影；70实际VM边界测试通过。Calendar/Mail不因此伪标verified。
- 修复精确公开NO_CONSENT的首用提示；创建/改期/删除旧拒绝及不自动重放门禁保持。25定向VM检查通过，seq8真实UI已看到授权后明确重试提示。
- 专用CA fixture Host实际offline/locked release构建44分03秒；严格双marker、127.0.0.1、正常TLS verifier的Rust guard测试1/1通过，原生产源码未改。
- 定位真实模型wire缺工具选择为fixture匹配和SDK请求text包装问题，11+10定向案例通过。部署后真实GUI获取Calendar owner query/create回执；没有伪造权限或owner结果。

## 当前GUI验收与未完成

81个原子功能、243个轮次格；19:59实际索引2个SIMULATION_PASS，三轮完成0个。UA-CAL-02仅全事件limit200查询，未验证日期过滤。UA-CAL-06实际GUI新建 `ev-1791834681129`，get_event回执及独立owner记录匹配标题、时间、地点、notes和request_id；删除正在测试，最终计数由后续独立报告更新。

Mail实际合成IMAP收信、原文查看、手写草稿和原生审阅可见；remote Approve & Send被SDK“physical activation”拒绝，SMTP DATA=0、独立receiver=0：HUMAN_REQUIRED，不能称发送或自发自收通过。邮件→日历选择加入、同候选完整恢复/防重、最终20次冷启动、长时间业务soak与全功能三轮未通过。30分钟360点PID/RSS采样只为OBSERVED_NOT_FUNCTIONAL_SOAK。自动AI记忆建议卡和部分已打开Goal聊天改计划路径不伪称已实现。

生产rc7已本人安装且R5 Main/manifest核对一致，现有MiniMax metadata保留；本轮未做生产云模型实调、私人日历变更或真实外部发信。根bundle仍历史版本，本机候选本地准入签名不等于官方GitHub publisher证明，未公开发布/Tag/比赛提交。

## 证据入口

- `official_muse/integrated_release/evidence/sprint005-rc8-frozen-r4/`：实际窗口、动态身份、冻结和旧/修正handoff。
- `official_muse/semifinal/evidence/user-acceptance-3rounds/`：独立每次GUI输入、native图、视觉核对、readback与SHA清单；保留失败/旧sequence7，不拼作seq8通过。
- `official_muse/integrated_release/evidence/sprint005-consent-notice-r4/`、`sprint005-entry-single-host-r1/`、`sprint005-latest-ci/`：定向实现及实际命令证据。
- `official_muse/semifinal/sprint005/zc01/`、`zc02/`、`zc03/`：公开SDK来源、fixture输运、UI/VM测试。TLS私钥/账号secret不进入公开证据。

后续最高价值工作：完成同候选Calendar删除/改期/重启读回；通过本人native发送步骤后验证SMTP与独立收件；实际邮件联动日历；对同一冻结候选重跑适用三轮。截止后不自动扩时，未测试项如实保留。

---

# 早期检查点记录

状态：进行中。实际开始北京时间2026-10-12 13:11:25；19:11:25停止新增高风险改动；20:11:25截止，不自动延长。

R5保底完整：产品0c3aa9b1、Main源caa99c57、签名ef58430f、manifest7b746fb0。此前164业务链、107Mail恢复、20大数据启动仍只是其明确隔离边界下的历史证据。

当前真实问题：试用窗口用了未配置_main模型的夜间隔离资料，正式资料里仍是rc6。用户已本人Install rc7，中央核Main/manifest与R5一致；原MiniMax-M3配置原位沿用，没有凭据复制。正式默认资料包已生成并签名验证，入口改为AppHub及已安装正式Muse，24项签名stub/隔离启动器测试通过，真实新入口已实际正常启动，完整聊天/导航/行动链出现；PID9278，动态三项SecCode0。用户本机UI照片仅保留build/calendar-live-dispatch-20261012-r1，不入公开证据。

独立ZC-05已建立，正在根据实际产品说明/源码/UI准备全功能矩阵；正式三轮尚未开始，不能声明FULL_3_ROUND_PASS。ZC-01、ZC-02、ZC-03已通过真实已有GPT聊天接手SDK/发布核查、Mail与模型fixture、UI/性能/演示，独立ZC05独占新worktree。矩阵准备81个原子功能/243格，全部NOT_TESTED，不将准备或历史通过记正式三轮。实际模型管理UI搜索两种名称均无入口，作为新增SDK/打包核查交由ZC01。

本轮只读模型连接仅在现有合法授权内执行；用户离线后不审批生产系统权限、不修改私人日历、不发送真实邮件。需要人工的步骤记录HUMAN_REQUIRED。生产证据/私人UI只留本机，不进入公开证据。

本轮最新结果、Agent分工、性能/发布准备、三轮证据与实际远端SHA将在收口时更新；检查点见official_muse/semifinal/evidence/sprint005-start。

14:38新增检查点：见official_muse/semifinal/evidence/sprint005-entry-single-host-r1。独立预检Bug已证据化，單Host新正式入口恢复。Source优化候选及rc8准备、CA测试Host编译中；26签名stub PASS和Loopback模型UI连接不等于正式三轮/真实云模型。用户最新已又授权且离开，接下来不申请权限；新真人交互标HUMAN_REQUIRED继续其他工作。

2026-10-12 15:13:14：单Host完整窗口已交ZC05实际UI预检，Root未并发操作；准备rc8正式外层/新签名目录，CA专用测试Host编译中。rc8启动器26项与打包四项+修订单项分别真实PASS，原错误记录保留。三轮schema控制39样本及源路径限制已接收；未实现的自动AI记忆建议卡、已打开Goal聊天改计划路径不会伪装为已完成。

16:20 rc8/seq7已冻结，实际完整GUI与三SecCode0；专用CA Host仅合成输运验收，生产候选保留原1eb。独立ZC05正式三轮开始，优先Calendar/Mail。旧35图预检两问题已修，投影70真实VM边界PASS，新增CA guard1PASS；这些不计三轮。最新身份和Root原生预检见sprint005-rc8-frozen，阶段结果持续按实际证据更新。

17:44：独立GUI首次Calendar request实调停在session前置并保留FAIL；首用consent源码会拒绝当前调用而Allow只prepare，没有自动重放，原error未保存所以该次具体分支仍未证实。修复仅识别精确公开NO_CONSENT并提示授权后再次明确操作；9a61040c / c098源的25真实VM合成案例PASS。新seq8两候选签名校验完毕尚未启动，不能混算旧f9三轮。Mail用localhost首次遭fixture guard拒绝保留BLOCKED；127.0.0.1后实际原生连接和IMAP登录已出现。当前mailbox为空，不计正文、SMTP或联动成功。准备失败与30分钟被动PID采样均保留，后者不算功能soak。
