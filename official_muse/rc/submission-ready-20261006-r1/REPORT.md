# Muse rc49 · 当前冻结产品

**PARTIAL。产品 `e0eb5d82`，实际候选 `gate-rc49-r2`。** readable `2bad514d69d777fabb9ad2daf2b0aa2862555c2db5c146b22bc635b3b1e70484`；实装 compact `15ea7e6d2da21ce8bedbcb1e4cee1537217ee653a4f603539e51fc35cefc540f`，98469官方tokens完全相等；Host1d7不变。

rc48收口中再次发现真正回归：右卡确认仍假设select_goal同步，直接确认读到空/手写composer，且延迟导航会覆盖草稿。`plan-card-before-r2`保留6FAIL。rc49仅为当前绑定Goal/id/revision确认，临时使用原计划目标与资料调用既有approve并还原编辑内容，去掉冗余导航；两处按钮捕获渲染时的id/revision，拒绝旧卡使用新全局Task。实际完整本地存储/readback等10检查在最终readable2bad上通过（不是spy批准）；重复、旧版本、不同聊天绑定拒绝，未增加权限或预算。见 [PLAN_CARD_REGRESSION.json](PLAN_CARD_REGRESSION.json)。49-r1是未安装/未公开的中间候选，原Gate/测试/上游拒绝日志保留，不替换成r2身份。

**rc49最终实机关键路径：** App Hub安装6文件SHA相同、23个应用文件/ledger保持；启动16聊天可写、无[E]。自然语言输入后真实官方model.complete生成候选，实际1204输入/410输出；打开核对后回到Chat，保留未发送手写内容，右侧“确认执行这个计划”仅点击一次。Goal `1791222912-516469458` / 新Run completed，实际2条资料保存并独立readback，结果卡与来源记忆一致，composer原文完整保留。完整证明见 [RC49_LIVE_PLAN_CARD.json](RC49_LIVE_PLAN_CARD.json) / [安装核对](RC49_INSTALL.json)。没有新发邮件或写系统日历。

rc48的Shell恢复、跨聊天召回及模型精度保持原版本身份，相关路径未因rc49卡片修补改变，可作支持证据，不重贴49标签或拼成最终外部整链。内置0.6B自动配置与误答验证源于rc45/48，复用范围在模型报告中说明；它仍不是第二strong。原版Hub对最终49-r2的可靠exit=1、唯一calendar拒绝见 [来源及退出状态](compliance/UPSTREAM_HUB_CHECK_RC49_R2_PROVENANCE.json)，本地Gate/check/scan/catalog通过只是扩展演练。

真实视频、两张脱敏关键截图、封面和内置模型<500,000,000字节桌面包，以最终 `DELIVERY.json` 的路径/摘要为准。代码按本人授权普通推送，旧Tag不动，未正式上架。原二十项的完整外部最终链、第二strong、两替代、真实账号2h、OS/两Mac及publisher/review缺项仍保留；不宣布20/20。

---

# Muse rc48 · 已保留的前一候选验证

状态：**PARTIAL**。当前产品提交 `89bfd399`，版本 `0.3.26-rc48`；本轮在真实 OctoSense / App Hub 安装并验证。原二十项未全过，未正式申请 App Hub，没有移动旧 Tag。

## 版本身份

- readable SHA256：`179fd6b6fc8e54c55fe7627af2eb1ed117d8ce34bdbbc93cd491456404b0d46d`。
- 实装 compact SHA256：`fcf9408f8e153129dff9614c91b0fdde69f214f0740cc88189095ba64157fb0f`；官方 tokenizer **98422 / 98422，相等**。
- Host SHA256：`1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`；未换 Host 或修改 VM 执行预算。
- Gate 构建前 Git 字段是 `21b275f7`，产品提交在构建后形成；不能把 Gate 字段误当产品提交。身份以以上源码摘要及 `89bfd399` 的 bundle 核对。

## 最小产品修复

1. 关联任务导航：持久 Goal 选择、聊天绑定和结果渲染分为短回调；每步检查 Goal、版本、聊天、页面、请求序号，拒绝旧回调。
2. 删除缓存：仅在实际 `calendar.delete` 的独立 get 确认不存在及 verified 收据后，移除精确 `(event_id, calendar_id)` 的月视图缓存；不删除历史或记忆。
3. 任务意图：明确“资料：/原文：”之后的引用不决定操作种类，完整原文仍作为资料传入；修复普通整理任务因资料含“日历”误进日程。
4. 启动恢复：聊天消息校验每次 8 条改为 2 条，仍检查完整历史；不清历史、不显示空壳来假通过、不提高执行预算。rc47 的真实 `gm_has` 预算失败保留。现有复现未完全证明原失败所有根因，不能称所有启动条件已消除风险。
5. 测试可交付：结果回执 fixture 不依赖开发机未跟踪资料；旧异步提案/日历测试改为有界等待及明天的合成日期，保留原行为断言和旧失败。

## 实际验证

| 层级 | 已执行 | 结果及范围 |
|---|---|---|
| fixture | rc46/47 关联导航与精确删除 15 检查 | PASS；含旧版本/跨聊天/页面/请求守卫；不是系统删除测试 |
| fixture | rc46 回执容量三个配置，各 15 检查 | PASS；公开确定性输入可随源码运行 |
| fixture | rc47 资料意图 11 变体 | PASS；本轮真实错误原句在 rc48 后正确进入计划 |
| fixture | rc48 16 聊天 × 16 消息，每条密集来源；正常/损坏尾条各 5 检查 | PASS；完整校验、拒绝坏数据、历史不清空；probe 只替换启动后续入口 |
| fixture | rc46、rc47 提案18/18及日历9/9，各自源码绑定 | PASS；旧数组空队列/过期日期/NaN失败原样留存，不替代实机服务 |
| live Shell | rc48 App Hub 安装 | 6 个 bundle 文件 SHA 匹配；22 个安装前应用文件/模型 ledger 不变 |
| live model | 新的一次性资料任务 | 官方 model.complete，class strong、attempts1、实际1178输入/879输出；发生在候选准备阶段 |
| live storage | Goal `1791221504-3719825078` / Run `run:1791221504-1223225220` | 用户批准一次，保存2条原资料，独立readback，completed及来源记忆落盘；模型未在批准后再次调用 |
| live restart | 同 rc48 同资料 Shell 新进程 | 任务、记忆、聊天、草稿、日历状态、ledger及结果摘要保持；Activity追加恢复事件、mail-watch正常轮询改变，不声称所有文件逐字节相同 |
| live memory | 切换既有空聊天，询问新任务资料 | 实际1400输入/381输出、strong/attempts1；正确回答两条，引用新结果claim；无新增Run或Action（仍10/16）。选择聊天更新selected Goal元数据，完整goals文件摘要不相等 |
| live UI | 最大化真实窗口、任务详情、Memory、日历权限/只读、空聊天 | 正确渲染并实录，无本轮[E]；不代替所有尺寸回归 |

rc46 的 `RC46_NAVIGATION.json` 曾用不适用的返回按钮检测而报 `actual_navigation:false`；失败文件保留。实际截图/按钮显示任务详情，本轮 rc48 更通过模型计划的“打开并核对”进入相同导航路径，显示“任务详情/目标/计划/批准并执行”，且绑定实际新 Goal。不能删除误报来美化测试。

新增合成任务仅写应用存储；这轮没有新发信或系统日历写入。此前唯一事项的真实邮件→同UID创建/改期→关联回复本人到达→结果与记忆→恢复→精确清理已在 rc37/41/42/45 完成，是**跨版本**证据，不拼成 rc48 从头外部全链。已清理事件不重放。

## 官方标准与交付

- 当前参赛入口是 OctoScript / Splash，Makepad 渲染，通过 App Hub manifest capability、宿主模型及存储服务；Python 是开发测试/打包工具，不是第二套 Agent Runtime。
- 本地扩展 check/scan/packet/catalog：PASS（演练发布者身份）。原版独立 Hub 对同 rc48 bundle：**REFUSED，唯一报告项为未知 calendar capability**。本地 EventKit/准入补丁与运行环境随源码可重建，不能称上游已经接受。
- 真实隐私说明已在仓库发布，publisher listing 指向该 HTTPS 文档；Issues 支持入口已设置。正式发布者登记和独立 packet 审核未具备。
- 完整本地模型/桌面包与中文实录视频由协作聊天并行生成，最终大小、摘要、路径及媒体审核以 `DELIVERY.json` 为准。ZIP严格要求小于500,000,000字节；视频作为同桌面目录的独立附件。
- 内置 Qwen3-0.6B 纯 Q4_K_S 权重及 CPU runner，许可证、摘要与首次配置检查随包。它不是 strong 模型；实际 Muse 复杂请求中的基本问答仍有误答，旧失败不删。强语义任务应由使用者通过官方模型设置配置较强模型，不能把自动配置成功写成回答准确。
- GitHub 按用户本轮明确授权普通 fast-forward 同步；不强推、不移动旧Tag、不正式上架。最终远端摘要独立读回。

## 仍未达标

同一最终候选从头真实邮件/日历/回复全链、第二独立 strong 的完整语义门槛、两个真实核验替代时间、最终真实账号2h、整机重启及两个接收 Mac 仍缺完整证据。rc48 当前实机启动成功与局部fixture不能替代这些门槛；不改原验收标准，不宣布20/20、UI_PARITY_PASS或正式比赛排名。

本地新榜单 Muse 91 / CFAW 90，不是主办方评分；Muse本地新代码与其他公开固定版本的口径不同，只采用持久状态、版本绑定、确定性核验及精简交付的工程原则，未读取或复制竞品实现。见 `RANKING_ADOPTION.md`。
