# 原20项精确门槛与rc49补齐路线

**状态：PARTIAL；本次包含原20只读审计及后来分别明确授权的两次独立GPT真实诊断，不是新完整产品验收。** 产品冻结`0.3.26-rc49/e0eb5d82`，可读2bad514d、载荷15ea7e6d、配套Host1d7。没有修改产品/原配置，没有邮箱/日历动作、8493操作或push；两次真实模型核验均用不同全新隔离副本，详见单次结果。

## 标准来源与不能增加的门槛

已实际读取用户附件 `Muse_三小时_记忆安排改期与会话标题_执行包_20261003 (1).zip` 的二十项定义和总控提示词，以及随后`Muse_三小时_修复瘦身与AppHub提交_执行包 (1).zip`的总控与20项已确认决定。原文/摘要见 [SOURCE_ORIGINAL20.md](SOURCE_ORIGINAL20.md)、[SOURCE_CONFIRMED_DECISIONS.md](SOURCE_CONFIRMED_DECISIONS.md)、[SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json)。这些是用户给定任务定义，不是测试结果；新增需求按当前授权执行，旧执行安排不重新启动。

- 原T17要求实际默认通道与已配置较强通道同安全题、记录fallback/成本、最终生产配置核心动作语义正确。**没有要求所有route必须等于registry官方默认URL，也没有要求弱通道所有题均PASS。** 原文明确弱通道失败照实记录，已验证较强配置可以作为生产验收配置；通道缺失或最终关键语义失败不能放行。
- 原T08要求“至多两个”，不是强制恰好两个。真实只找到一个可以只给一个；缺实际忙闲核验不能给猜测时间凑数。
- 原T18的同最终候选约定→创建→回复→改期原ID→回复→Shell重启/新聊天记忆是硬要求，不能拼旧跨版本节点。
- 后续用户明确增加A-START：**10次完整Shell冷启动、5次普通重开、用户电脑重启后的首次启动**。OS重启有明确来源，不能删；本轮由用户配合，不能擅自自动重启。
- A-CAL包含Apple日历外部改期后Muse刷新；A-COST新增≤10元且共享总额≤30元，未知金额未核清则暂停付费是原附件要求；Root本轮转达用户后续“随便用”已覆盖旧金额上限，保留旧账务未知且不提高Host预算。A-SIZE/A-PUBLISH按原决定保留。
- 30冷、100重开、真账号2小时、两接收Mac未写入上述原20/追加子检查。它们可属于后续独立用户请求或具体风险试验，**不应偷偷变成T20硬门槛**；也不据此取消独立任务或删历史真实失败。形式上原版Hub是否接受Calendar与比赛允许本地宿主扩展路线分开，不把未正式上架当所有功能失败。

## 原20逐项（不重新计算历史通过数）

历史rc10的5PASS/14PARTIAL/1BLOCKED是旧身份；本次不给rc49重新贴20/20，也不把旧T18“缺账号”原因继续当现状。准确原条件逐条在 [ORIGINAL20_AUDIT.json](ORIGINAL20_AUDIT.json)，以下是当前有效支持与最小补齐。

| ID | 现有有效支持 | 真正剩余门槛/下一步 |
|---|---|---|
| T01 基线/复用 | e0eb5d82/2bad/15ea/Host1d7；Root保护稳定安装/生产/失败；本次附件与证据SHA核对 | 最终导出版本/源码/包/配置身份匹配，不混私人资料；不需重新造项目 |
| T02 逐封提醒/防重复 | rc37/41真实来信和提醒；收信绑定/重启夹具保留 | rc49同账号连续测试来信可见，切聊天、重连/重启零漏/零旧信重复；复用隔离负例只能支持安全条件 |
| T03 分析/费用开关 | 现有默认、显式关闭、许可/无模型/无预算守卫夹具；手写真实历史 | 当前隔离账号的显式开关、提醒继续/手写可用及已授权真实分析；按当前费用授权/Host预算，不把usage已知当人民币账清 |
| T04 项目/账号归属 | 同名/不同账号/项目/墓碑夹具及跨版本来源记忆 | 最终新来信明确项目不切当前聊天；同事项来源/账号一致，归属不明无错误绑定 |
| T05 全局记忆 | rc14冲突采用保留另一原文；容量/更正/遗忘/恢复；rc48跨聊天真召回；rc49结果记忆 | 同最终外部事项正确来源/时间/当前事实及新会话召回；相关逻辑未变的负例可支持，不强制全套重复跑 |
| T06 偏好≠批准 | 原PASS，软硬约束/未答零写入/分别确认已有fixture；相关函数与rc47字节未变 | 最终事项如不符软偏好先问，未答不写；不能把模型或记忆当批准 |
| T07 时间歧义 | 合成日期/时区/缺时长/模糊日期拒绝与两模型历史题；真实问题修正节点 | 最终交付模型安全题含未见变体，保留已知字段、问缺项，旧S02格式失败与R02缺因不删除 |
| T08 替代时间 | 原日+后三天/窄范围/至多两个/政策夹具；Work真查询节点 | 最终选定日历真实检查可选候选，数量0/1/2按事实；查询范围和时区可追踪，不要求凑两个 |
| T09 创建/回读 | rc22独立CRUD、rc37邮件事项create/get；rc49普通资料存储非Calendar | rc49完整事项经前置复查/有效批准真实create、独立get，唯一eventID；根本无动作时不标完成 |
| T10 原ID改期 | rc34/41同eventID update/get且未新增；绑定/版本负例 | rc49第二封信展示原安排，确认只改日期时间，独立get其他字段保持且只有原eventID |
| T11 不明/权限拒绝 | 原PASS；来源/多匹配/缺事件/只读/撤权夹具；配套Host权限实际历史 | 当前实际权限状态复核，负例拒绝相关函数未变可支持；不能将full-access推广至任意事件修改 |
| T12 外变/迟到 | 20故障/新进程、stale/取消/UNKNOWN不重放；相关逻辑支持 | 对已批准合成事件由Apple日历外部改期，再Muse刷新及执行前重查；可控迟到fixture不必制造真实破坏 |
| T13 连续来信 | rc37/41顺序关联历史；逐封来源/恢复夹具 | 同rc49两封同事项每封留独立记录，依次推进，旧候选重新核对，无最后一封覆盖旧处理 |
| T14 结果卡 | rc49真右卡一次点击→storage/readback/记忆、输入保持；历史外部卡 | rc49同外部事项创建/改期/发送状态连贯，一句结论/动作/下一步，原文可展开、没有假已完成 |
| T15 自动稿/手写 | draft保护/采用变体及真实手写历史；模型候选成功不等于邮件稿 | rc49日历读回后按设置真实起草，手写→重新起草保持→显式采用；无模型/关闭仍手写 |
| T16 独立发送 | 原PASS；单独确认、源改失效、UNKNOWN恢复/零盲重发；历史本人收件 | 最终链单独确认账号/to/body后发送，accepted与到达分开；到达需测试收件端/本人证据 |
| T17 双通道 | 当前配置2个不同模型名，均catalog strong；旧rc10各28安全题与失败原样保留 | r3协议受限，后续r4已修正后一次请求仍收到HTML/非JSON、Host provider/UI error；未提供可用模型回答。仍需成功通道后同题/usage/成本/语义审查 |
| T18 最终全链 | 旧rc37/41/42/45真实跨版本链；rc49普通Goal和右卡真通过 | 冻结rc49从头一事项两信→偏好冲突创建→稿/发送→原ID改期→稿/发送→同目录Shell重启→新聊天记忆；不得将跨版本升为PASS |
| T19 标题 | 用户已确认原生等效，历史短/长两行省略、54px等高/原文保存；后续右卡改动与标题分离 | 对未变标题组件复用有依据截图/原文；若布局/标题实现改动仅重测受影响项，窄窗不称手机 |
| T20 回归/交付 | rc49安装6SHA/23应用文件保持、16聊天启动、实际模型与右卡；rc48重启及两次真实模型按原身份 | 当前受影响路径/签名Gate/scan/输入/源码包补丁和公开安全审核，A-START另列10冷5重开+用户OS首次；不用新自设次数/时长阻止T20 |

## 可复用逻辑的字节依据

[FUNCTION_REUSE.json](FUNCTION_REUSE.json) 实际只读比较461个顶层函数：rc47→rc49有459相同，仅`chat_boot_check`与`approve_plan_card`变；rc48→rc49有460相同，仅`approve_plan_card`变；r1→r2顶层461全部相同，但两处UI回调捕获ID/版本不同。因此：

- 未改的mail发送/回执、Calendar policy/get、Memory冲突/墓碑等函数的既有负例可作为 **REUSED_SUPPORTING**，保留旧测试的版本、Host与数据范围。
- rc46/47提案18与Calendar9、导航/删除15、回执15各有旧报告，不能整套称rc49重跑；启动/批准/渲染绑定受影响，其当前证据分别用rc48启动和rc49-r2实际右卡。
- 函数SHA相同本身不证明UI、全局状态、transport、权限与模型同一性。本报告没有用“461相同”推出新实时外部链或整机恢复通过。
- rc10的7200秒合成驻留和100重开保留为旧版本支持；不是当前真账号驻留/OS重启。保留所有预算/语义/路径失败。

## 模型投影结论

[MODEL_PROJECTION.json](MODEL_PROJECTION.json) 只输出允许的非敏感字段：

- 配置候选2：`minimax-cn / MiniMax-M3`、`openai / gpt-4o`；静态catalog均strong。
- effective origin不同、path不同、api_type相同；都非loopback；与各family官方默认route都不匹配。**自定义路由不等于失败。**
- family/model标签与静态strong不证明实际后端/成功调用；当前未解析凭据，Host按Key筛选后的可运行候选数为NOT_CHECKED，不猜成2。
- 没有输出任意URL、env_vars、Key后缀、标记或凭据，未直接调用钥匙串，未寻找新通道。用户已向Root确认GPT/OpenAI，A3不重复问；后续独立实调由Host使用既有授权配置。
- 最小执行路径见 [MODEL_ISOLATION_STEPS.md](MODEL_ISOLATION_STEPS.md)。两候选共存时Host可以排序/fallback，不能以主配置标签推断实际调用模型；现有公开model.complete meta不含provider身份，不能靠class=strong辨别两后端。

## 工作产物与提交范围

a3初始工具只读检查原附件、源码、指定隔离profile和已有脱敏证据；单次GPT驱动仅修改自建隔离副本。初始审计新运行测试=0；随后先收到GPT/OpenAI单次实调授权、再收到修正观察协议后的一次授权，结果单独记录，不混为旧fixture重跑。原profile修改=0。保留原20全部条款；这里只完成A3证据梳理，不宣称整个产品通过。Root持有唯一UI/外部动作写入权，本轮A3仅本地提交本目录，不改主报告/README，不push。

## 后续授权的单GPT实调：未通过

证据：[GPT_ONCE_RESULT.json](GPT_ONCE_RESULT.json)、[GPT_ONCE_RESULT_R2.json](GPT_ONCE_RESULT_R2.json)、[GPT_ONCE_RESULT_R3.json](GPT_ONCE_RESULT_R3.json)。共三次隔离Shell启动，其中前两次在发送前失败；第三次仅一次UI发送、一条实际API请求，未重发。

- r1：端口尚未ready，0模型调用。
- r2：49实际载荷冷编译`SPLASH_COMPILE_FAILED`，337324/464045字节处`max_chunk_ms=71.085`、script time budget exceeded，0模型调用。这是具体启动失败，保留，影响A-START/T20；没有拿第三次暖Hub成功覆盖它。
- r3：02:40:37–02:40:50，同Host1d7/Gate49-r2，通过App Hub再打开Muse，单provider OpenAI/gpt-4o、fallback空。HTTP200；Host `error_code=provider/is_ok=false/known_usage=false`，日志确有非JSON响应错误；UI error，未回答5。响应模型/usage无法核验，不计零费用，不标GPT或T17成功。

**协议限制必须保留：**请求API尾路径`/chat/completions`；正文观察器保持body字节，但强制响应Content-Type、未传Content-Encoding、urllib可跟随重定向，而原Host禁止重定向。原响应内存已丢弃，类型/编码/字节数/SHA及HTML/SSE/gzip/JSON/plainerror形态和网页登录redirect均未观测。故不能唯一归因于上游错误，也不能宣称这是完全透明的原版直连；不自动重复请求补证据。

当前Host wire非流式JSON解析路径不直接处理SSE/压缩体，但本次没有其形态证据，不改Host猜修。原指定profile摘要未变，未复制Mail/Calendar账号数据，自己Shell与8515/8516已退出，8493未动。实际操作入口与限制详见[MODEL_ISOLATION_STEPS.md](MODEL_ISOLATION_STEPS.md)。

## 修正观察协议后 r4：当前通道返回网页，仍未通过

Root再次明确授权后，新增独立r4，未覆盖r1–r3。工具[run_gpt_protocol_once.py](run_gpt_protocol_once.py)，证据[GPT_ONCE_RESULT_R4.json](GPT_ONCE_RESULT_R4.json)。02:44:59–02:45:11，Host/payload仍1d7/15ea；HTTPClient不跟随redirect、不自动解压，保留端到端重复响应头和正文，只重建HTTP逐跳传输长度。请求`/chat/completions`，预先及实请求确认没有重复suffix；一个provider/fallback空，一次UI发送、一条API请求。

| 字段 | 真实结果 |
|---|---|
| HTTP | 200 |
| Content-Type / Encoding | text/html / 空 |
| 原响应大小 / SHA256 | 1166字节 / 05530b4453e1e2fc31a692864ba6912af3aa4bf03cfe0f56ca9cbfc9f0a689d7 |
| HTML / JSON / SSE / gzip | true / false / false / false |
| 登录页路径/登录表单启发式 | false / false；不能证明具体页面用途 |
| 网页应用外壳启发式 | true |
| Host / UI | provider；is_ok=false；known_usage=false / error |
| 返回模型 / usage / 成本 | 未观测 / 未知 / 未知；不能算零成本 |

**能确认的根因范围：当前配置的API请求返回HTML页面而不是OpenAI completion JSON。**不能猜正确base地址、断言网页登录或改Host吞掉HTML。需要现有通道的正确API base/路径，配置者或通道提供方核验后再作真实模型验收。本次不继续T17题集，不宣称模型名证明真实后端身份。

原始响应仅保存在git忽略的`.local-state/gpt-once-r4/upstream-response.private.bin`，权限0600；未打印正文、Key或endpoint。原profile摘要不变，自己的PID76898及8515/8516已退出，Root8493不操作。初始审计0runtime；后续合计4个启动（2个未发送失败）、2条分别授权的API请求；不是原20/整产品重测。
