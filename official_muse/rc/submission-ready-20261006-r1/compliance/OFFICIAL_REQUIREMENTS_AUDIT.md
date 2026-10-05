# Muse 官方技术与交付核对

**结论：PARTIAL。** 核对的是rc45与当前配套本地扩展，不是对后续候选或上架结果的认证。只读审计未改产品/Host/SDK、未操作8493、未查账号密钥、未进行模型/邮件/日历动作或付费调用。

## 当前版本基线

- worktree：`/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松`，分支`codex/muse-rc-finalization`；进入时HEAD `9b83f98c75965e76c58943224b5eadf0e632345e`。
- 产品rc45冻结源码`d306d3c04284413a5891592c26a30a93d2c0866e`；Readable SHA`51c09d4b…`；payload SHA`3f0c9ee0…`；Host SHA`1d7d1674…`；本地Hub SHA`24db5e55…`。
- 实际签名bundle：桌面rc45 `.app/Contents/Resources/mirror/artifacts/muse-goals-0.3.26-rc45.bundle`；六个SHA完全匹配DELIVERY。完整清单见RC45_SIGNED_BUNDLE_INVENTORY.json。另保留compact准备目录清单，其manifest不同，不能直接拿它当签名交付artifact。
- `dependencies.lock.json`固定Makepad bf318136、OctoSense 7f962547、AppHub e8601b80、Octoscript 68f6a9df、Octoscript-Makepad 019e6bf0；包含本地overlay。lock.product_version仍0.3.22，应理解为SDK冻结元数据，不能当rc45产品版本。
- 最新在线 main：比赛0db87b58、DesignFlow a5a87d3c、AppHub9e7f0778。本文没有升级产品锁。
- 进入时有他人的未提交/未跟踪证据；没有混入审计提交。

## 逐项核对

| 要求 | 依据 | 分类 | rc45现状/缺项 |
|---|---|---|---|
| 围绕12场景、Agent真实办事与用户控制 | C1/C2 | 强制比赛交付 | Mail/Calendar组合有跨版本真动作与回读；不能升级为所有场景通过 |
| Rinx主要基线；OctoSense或Rinx注明版本实际验收 | C1/C3 | 官网要求/支持路线 | Muse跑配套OctoSense Shell；不能称已在Rinx实测。C3也允许原生宿主扩展，交付需锁宿主和说明范围 |
| Apache-2.0公开仓库源码与固定版本 | C1/C3 | 强制比赛交付 | listing声明Apache-2.0不等于完整License核验；Root正在核对/公开同步。不得用当前公开较旧Tag冒充rc45 |
| 可运行作品、宿主/平台/安装说明 | C3/C2 | 强制比赛交付 | rc45Intel x86_64 macOS14+，ad hoc未公证；接收机未通过，不能写全Mac通用 |
| 数据来源、权限、隐私、功能说明 | C3/C2 | 强制比赛交付 | public listing真实标本地扩展；privacy仍example.com占位，需真实政策链接及发布者审阅 |
| 演示/两截图/失败或空状态 | C2 | 文档要求 | 两PNG存在但本次未核验其最终版本画面；录像尚未验收，参见视频清单 |
| 复赛队外试用及真实正常/失败证据 | C2 | 文档要求 | 接收机/队外实际运行缺项；fixture不代替 |
| 10/4/10/9/10/12冻结与材料安排 | C2/C1官网部署脚本 | 文档安排/待确认版本差异 | 与用户较早6号群通知存在差异，不能据此改Tag；等待赛务最终口径 |
| 队伍名、成员id、主题、加群 | C4/C2 | 报名字段/赛务核验 | 已有用户选择星海；本次未独立验证登记回执和成员报名；不公开私人登记表 |
| 不必等待AppHub上架 | C1/C3 | 官网明确 | 本地预检+运行可备交付；不等于正式商店采纳 |
| Splash脚本或L0卡片，Makepad原生运行 | D1/H1/H2 | 技术契约 | Muse入口main.splash，为Splash/Makepad Script，不是L0源码；DSL为业务协议，不能代替运行时 |
| bundle只有入口/manifest/listing/资源/截图 | H1/H2 | 强制Hub规则 | rc45六文件符合形态；Python/AppKit/模型权重不在受限bundle |
| Bundle上限8,388,608字节，无symlink/二进制 | D2/H1/H2 | 强制Hub规则 | 签名bundle大小见RC45_SIGNED_BUNDLE_INVENTORY.json；低于8MiB，本次清单无symlink。外层运行包和其合法内部链接不是Hub bundle |
| manifest精确schema=1、合法非os.id | H1/H2 | 强制Hub规则 | muse-goals、schema1；没有假冒系统应用身份 |
| 最小闭合capability、逐项同意 | H1/D2 | 强制Hub规则 | 请求storage/model/mail/calendar/glance；calendar在锁定及最新上游列表均不存在 |
| net精确域名，不能本机HTTP绕权限 | H1/H2/D2 | 强制Hub规则 | network.hosts=[]，无net。宿主代做model/mail通信不能解释为完全离线 |
| storage只能本应用jail | H1/D2 | 强制Hub规则 | 应用fs读取/写入自己的JSON与结果；不能宣称全电脑访问或生产SQLite全部迁入 |
| model.complete宿主一发调用+schema+预算 | H1/D2 | 真实支持的API | Muse有真实调用证据；模型/费用由宿主配置，不因调用model变成运行octos peer |
| llm只管理系统提供商，不是聊天API | H1/D2 | 技术限制 | Muse没有声明llm；不在应用收Key |
| agent/工具/触发声明≠已运行能力 | H1/D2 | 技术限制 | manifest.agent=null，没有octos.*。当前聊天/动作路由是Splash状态机+model.complete；不能称官方octos后台peer已接通 |
| 长期Goal/后台触发需实际执行证明 | D2/H1 | 推断/运行限制 | listing明确精简为一次性任务/来信提醒；当前不宣传完整长期周期Goal。页面计时器不证明关闭进程后的调度 |
| Mail账号/Key走宿主sheet/vault | D2/H1 | 技术契约 | 使用mail.*，应用不收密码；本次未读取凭据、未实测重新登录 |
| Calendar普通应用上游支持 | 最新D2 HOST-SERVICES/H1 manifest | **明确不支持** | 最新上游只服务os.calendar；本地扩展单独标注，不能写原版正式准入 |
| 新Host能力需能力/隐私行/派发/OS/范围/确认共同执行 | D2 HOST-SERVICES/H1 | 技术契约 | 本地Calendar overlay覆盖policy/listing/index/Host等；源码锁可复现但没有维护者认可 |
| card-host与真实Shell服务分开 | D1/D2/H1 | 技术验收限制 | card-host不提供model/mail/calendar；fixture替换transport只能验生产函数逻辑 |
| secret不能进入应用包 | H1/D1 | 强制Hub规则 | 本地Gate secrets检查通过仅检查规定密码控件，不能称通用Secret审计；本轮没有寻找Secret |
| 截图真实且实际检查，不能占位 | D1/D2/H1 | 强制交付/人工审核 | 两PNG存在；仍需最终版本和正确渲染的真实窗口验证与对外脱敏 |
| check与scan必须分别解释 | H1/D2 | 技术流程 | 现有本地check PASSED，scan写7问题，no reviewer；不是独立审核通过 |
| 摘要/签名绑定所有bundle字节 | H1/H2 | 强制Hub规则 | rc45使用muse-local-rehearsal，本地演练公钥；改任何bundle文件需重绑定。本轮不生成或查私钥 |
| publisher continuity/catalog trust | H1/H2 | 强制Hub规则 | 本地演练catalog71entries/seq77通过，不是官方anchor目录里的采纳记录 |
| 正式AppHub提交仓库/tag/SHA/完整check/scan答案 | H1/H2 | 官方发布流程 | 尚无正式提交/维护者审核；不能编辑官方catalog强行上架；不是本轮获授权动作 |
| 公共测试可在干净checkout复现 | C3/D1 | 复现要求/推断 | regression_result_receipt依赖6个未跟踪fixture文件和本机构建路径，见PUBLIC_FIXTURE_DEPENDENCIES.json；应修成便携seed/参数化Host |
| 一项任务同最终候选从头全链 | C2+D1 | 运行验收/推断 | 当前同事项链跨rc37/41/45；最终rc45重启/结果/清理真实，不覆盖最终单版本完整流程 |
| 本地Gate/Host测试不替代接收机与真实模型/账号链 | C2/C3/D1 | 验收限制 | 包静态/解压/签名通过；rc45包装未重复GUI；第二Mac、真账号2小时、第二strong语义仍缺 |
| 500MB外层ZIP硬上限 | 本地DELIVERY，不在已读官方规则 | 工程约束 | 131,297,109字节符合本地目标，不能写官方比赛限制 |
| 报名/隐私/签名/正式投稿人工节点 | D1/D2/H1 | 发布流程 | 准备草案，Root/用户审阅；本审计没有提交商店、改Tag或push |

## Calendar上游与本地差异

固定e8601b80的`app-policy/src/manifest.rs`有65项已知capability，最新9e7f0778将契约移到`app-contract`，有96项；两者均没有calendar。本地vendor/app-hub新增calendar与对应隐私行、目录/准入测试，OctoSense overlay增加EventKit服务、权限与派发等。锁定源加补丁是可复现的本地扩展，不能用通过本地CLI证明原版接受。

已实际独立构建原版e8601b80 Hub：`cargo build --offline --release`，2m18s；原crate源码字节未改，只缩小独立审计workspace成员，Cargo.lock随解析变化也明确保留。完整命令/文件摘要见UPSTREAM_BUILD_PROVENANCE.json，工具链与解析锁分别记录，不替换产品Hub/Shell。

同一个交付签名artifact：原版Hub exit1，唯一拒绝`policy: app muse-goals requests unknown capability "calendar"`；本地扩展Hub exit0 PASSED。实际日志UPSTREAM_HUB_CHECK_RC45.txt、LOCAL_EXTENDED_HUB_CHECK_RC45.txt与HUB_COMPARISON.json。最新main的closed list已源码核对，但没有构建其CLI，不能把pinned CLI测试写成最新main执行。

首次误选compact准备目录产生digest与publisher-signature失败，两CLI均拒绝；失败保留在*_PREP_DIRECTORY_CHECK_RC45.txt。独立比较发现五个非manifest文件等于交付包，manifest不等于交付文件；换用DELIVERY所指真实签名artifact后得到以上对照。这不意味着此前准备目录曾通过Gate，也不表明签名成品损坏。

## 现有真实证据的等级

- **实际本机在线（引用Root保留证据，本审计未重做）**：rc37初始创建、rc41同事件改期和邮件、rc42本人收件确认、rc45模型新对话记忆、结算/恢复/精确清理。
- **隔离fixture**：rc45结果回归3组各15条；生产函数+合成transport/资料；不证明真实SMTP/EventKit/model。
- **本地技术预检/演练**：check/scan/catalog验证与ZIP解压/签名/启动器；不证明上游Calendar、独立reviewer或第二Mac。
- **已知失败**：rc45目标导航VM时间超限、删除后视图缓存需手动刷新、记忆答案部分把“时间”误解为核验时间戳。后续修复不能删这些失败或逆改原证据。

## 最小收口动作

1. Root审阅隐私草案，发布真实政策，再绑定listing及新包Gate。
2. 便携化fixture依赖，或交付明确可复现的窄替代测试；不把历史本机seed夹进产品资料。
3. 最终新版本固定源码/包/Host/hash，重做其实际必要任务与截图；跨版本历史单独保留。
4. 第二Mac真实安装与用户试用，按支持的平台宣告；未测机器不提前PASS。
5. 交付本地扩展与原版Hub拒绝依据；比赛原生扩展路线可准备，正式上游准入仍需维护者。
6. 官网与群通知时间差异请赛务确认；不擅自补造公开冻结状态或上架结果。

## 官方依据与读取时间

本次在线读取：2026-10-06T00:53:50.732166+08:00 至 2026-10-06T00:56:03.212038+08:00（北京时间）；每文件精确时间、SHA-256、URL和状态见 [SOURCES.json](SOURCES.json)。官网直接读取 HTML 与部署脚本 `index-Dp13UqI0.js`，公开源码另按真实 `git ls-remote` main SHA 固定。GitHub API `/commits/main` 返回 HTTPError，改用公共 Git transport，不使用账号凭据。

- C1：[官网](https://create.gosim.org/agenticapp26/)；[实际官网源 App.vue](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/src/App.vue)，FAQ/共同交付。
- C2：[比赛赛程](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/docs/competition-schedule.md)，9/25方案、9/26更新；不是用户群通知。
- C3：[官方提交区](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/src/components/AppHubSubmission.vue)与[Rinx路径](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/docs/rinx-miniapps.md)。
- C4：[报名 Issue #5](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/5)，本次只核对字段，不统计其他队伍、不核实星海的报名回执。
- D1：[设计仓库 README](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/README.zh-CN.md)、[AGENTS](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/AGENTS.md)、[flows](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/flows/README.md)、[script-app FLOW](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/flows/script-app/FLOW.md)、[QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/QUICKSTART.md)。
- D2：[SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/SCRIPT-API.md)、[CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/CAPABILITIES.md)、[HOST-SERVICES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/HOST-SERVICES.md)、[AI-SERVICES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/AI-SERVICES.zh-CN.md)、[PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/PUBLISHING.md)。
- H1：[最新 AppHub 发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/9e7f0778429125402dcfefef95ba2b01e8de7b94/docs/PUBLISHING.md)、[app-contract manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/9e7f0778429125402dcfefef95ba2b01e8de7b94/crates/app-contract/src/manifest.rs)。
- H2：[当前锁定上游发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e8601b80ce104db2e48208094714bdcffdce6b5a/docs/PUBLISHING.md)、[当前锁定上游 manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e8601b80ce104db2e48208094714bdcffdce6b5a/crates/app-policy/src/manifest.rs)。

分类：**强制**是对应比赛交付或Hub技术契约明确写出的条件；**建议**是准备方法；**推断**是由当前代码/证据得出的工程判断；**待确认**是规则版本、身份或真实测试尚无证据。Hub技术契约不是比赛日程或评分表。

## 交付后协同变化（不改rc45历史判定）

Root在审计期间开始修复导航/删除缓存，并写出新的 receipt_fixture.py、fixtures/receipt-template.json 和 regression_receipt.splash，替换A2输出依赖。已只读验证working-tree合成profile的63/64/63条生成，wrapper不再引用A2输出或覆盖Host；见PUBLIC_FIXTURE_REPAIR_WORKING_TREE.json。核对时HEAD f2a47219尚未包含这三个新文件，修复需提交并从最终公共Git树再次核验；本审计没有运行其CardHost测试或将之写成产品真链。Root也正在把隐私草案审阅为正式公开政策；rc45占位链接的历史结论不改写。
