# 0.3.5 最终独立验收入口

## 总控整合结论：PARTIAL

最终新Shell实测报告见根目录[OVERNIGHT_3H_REPORT.md](../OVERNIGHT_3H_REPORT.md)、[CHAT_EVAL_REPORT.md](../CHAT_EVAL_REPORT.md)、[性能报告](../OVERNIGHT_PERF_REPORT.md)。同一035真实模型20例8 PASS/12 FAIL；两个Goal存储/读回及首项真实模型建议通过，实际count3问答却答2。首次新Goal记忆加默认字段的字节检查失败保留，规范化后10次严格整Shell重启及20分钟空闲通过、idle模型请求0。

普通Chat尚未接入明确project/owner焦点及歧义澄清；模块显式隔离测试不代表自动主题归属已完成。本人新Host登录/真实来信/最终日历权限及实际联动未测，不能提升为全面PASS。最终真实Shell[失败回答与正确结果同屏](evidence/ui-overnight/final-035/live/focus-035/goal-result-question-bottom.png)已人工查看。以下独立fixture和card-host视觉原结论保留，不用工程成功覆盖语义与真实权限缺口。

main `0e4c26dcdc0760a12cc2bb545cea2eb42e4170fba86f14974edbb992339332f7`，一次同源162/162 fixture，五尺寸138新原图和指定交互通过。034 payload1601byte边界失败原样保留，035总控最小计入[]/逗号后同压力1241byte通过。详见[夜间报告](OVERNIGHT_UI_MAIL_CALENDAR_REPORT.md)与[最终汇总](evidence/ui-overnight/final-035/summary.json)。card-host+隔离storage/fake transport范围；新Shell/实际模型/Goal/restart/idle由总控另验，不把此处PASS扩大为全面产品PASS。下方历史按各自SHA保留。

# 0.3.3 夜间独立验收入口

最新冻结SHA `c72b13578964b535ee36c4d60fc9d77eaa5e6ed277c2ef32c2cfd42413076855`，149/149 fixture、五尺寸138张UI原图、U04两尺寸实际进程重启18项通过。详细边界/失败保留/未完成总控真实链见 [夜间独立报告](OVERNIGHT_UI_MAIL_CALENDAR_REPORT.md)。以下0.3.2及历史结论按各自源码保留，U04的旧缺陷不再代表0.3.3本轮结果。

# 0.3.2 冻结源码的独立验收与待核验项

**REGRESSION_FIXTURE = PASS（118/118）；UI_CAPTURE = COMPLETE（114 PNG）；本轮指定交互子集通过；UI_REDESIGN = PARTIAL（U04 已由总控实机复现，待0.3.3修复）；真实模型遗忘语义 = PARTIAL。** 官方 full-chain 与最终产物由总控收口。

主源码 SHA256 `36bcd8703f103abda767280dfb7c3c5f2fa9cf1380c6c59479640ed4494dd126`。manifest 版本 `0.3.2`，其中 `integrity.bundle_blake3` 为 `f989d22315b9a260d274a24e8af38bdde542b34c141ecd6e14bf1dec6e149cfe`。主源码逐字节核对后复制不可变 bundle；manifest 身份与总控给值一致，本聊天没有重新计算官方 BLAKE3 验签。GM/PAGE 未改由总控反馈，本轮没有独立重新计算其 canonical 哈希。[冻结记录](evidence/ui-memory/final-032-36bcd870/freeze.json)。

[同源八套 fixture 报告](evidence/ui-memory/final-032-36bcd870/regression/report.json) **118/118**：selection 2、calendar 9、model stale protection 12、incoming 38、chat binding 15、chat proposal 18、model preflight 12、chat derived 12。全部首次在此 SHA 重新执行；没有借用 0.3.1 结果。生产函数配合合成 transport，不能替代真实模型推理、邮件投递、Calendar CRUD 或 Shell 重启。

[五尺寸视觉与交互矩阵](evidence/ui-memory/final-032-36bcd870/visual-long/matrix.json) 选取 114 张本机可见 card-host PNG，三种尺寸各22张、两种窄屏各24张。五尺寸八页总览与宽窄重点原图均已人工查看；合成长对话实际滚动后画面变化、两行键盘输入读回、左栏折叠、全宽结果页均成功。先滚动上一页再导航，**7页 × 5尺寸 = 35次首屏检查全部通过**，目标/能力页不再沿用上页尾部。默认日历权限摘要只显示一次。截图只是本轮指定路径的证据，不代表 U01–U16 全 PASS。

| 请求尺寸 | 实际逻辑尺寸 | PNG 像素 | 对话输入 rect | 结果全宽 rect |
|---|---|---|---|---|
| 1400×900 | 1400×814 | 2800×1628 | [240,710,727,32] | [32,0,1368,814] |
| 990×539 | 990×539 | 1980×1078 | [198,435,429,32] | [32,0,958,539] |
| 990×400 | 990×400 | 1980×800 | [198,296,429,32] | [32,0,958,400] |
| 412×892 | 412×814 | 824×1628 | [164,710,135,32] | [32,0,380,814] |
| 1200×760 | 1200×760 | 2400×1520 | [236,656,531,32] | [32,0,1168,760] |

1400×900 与412×892 的高度受桌面可用区域限制，不能声称实际达到请求高度。412 展开侧栏时输入宽135px；折叠后释放空间。展开侧栏时个别长状态/日期元信息仍有裁切、能力标题分三行，是本轮观察到的排版限制。

**长邮件：**五尺寸均实际点击展开原邮件、在有界内层滚动、再收起、点击同卡回复并读回意图，共30个布尔检查全部通过。可见原正文高度依次176/116/80/176/164px；990×400 视口把原88px区裁为80px。外层使用边缘滚动到收起/回复按钮，不能用内层正文的滚动替代按钮可达性。没有点击模型起草或发送。

**两种窄屏表单：**990×400 与412×892 均折叠侧栏，新建日历的标题/起止/时区/地点实际键盘输入与五字段读回通过；点击合成冲突查询和本地预览后，滚动到系统执行确认。邮件收件人、主题和八段正文实际输入，正文完整读回；发送按钮可见。两种窗口均未点击日历执行确认或发送邮件。

| 尺寸 | 日历执行确认 rect | 邮件正文可见 rect | 邮件发送按钮 rect | 最终执行 |
|---|---|---|---|---|
| 990×400 | [57,262,172,36] | [46,284,902,106] | [133,149,65,36] | 两者未点击 |
| 412×892 | [57,720,172,36] | [46,547,324,142] | [133,172,65,36] | 两者未点击 |

report 的历史字段 `mail_preview_control_reachable` 实际记录“发送邮件”按钮位置，不代表已经预览或发送。可见 Host 调用仅合成 mail.accounts/calendar.status，窄屏另有本人测试驱动的合成 calendar.list；model.complete/mail.send/calendar.create/update/delete 为零，无 >99% 同色图。

**失败与复测保留：**[attempts](evidence/ui-memory/final-032-36bcd870/attempts/) 保存首次990×400展开断言误报，以及两个窄屏日历预览未生成确认卡的日志。第一项误把屏外收起按钮不在 /snap 当作没展开；已改为读取完整正文 Label，再实际滚动到按钮。第二项是 visual transport 无条件返回10/4全部事件给10/5查询，导致产品正确拒绝冲突预览；依据现有 calendar_iso_utc 与范围契约改为按日历ID/UTC相交过滤合成事件。修的都是 owned harness；同一冻结产品 SHA 复测两个窄屏成功，没有改产品、Host 或预算。完整初次输出保留于忽略的 app/build/ui-memory-20261003/frozen-032-36bcd870/，历史0.3.1/0.3.0证据未覆盖。

**U04 未完成：**总控最新只读发现 chat_new_session/chat_select_session 没有清理或绑定 task/result，已有 Goal 结果跨新对话停留右栏，已在新空会话实机复现，原图 new-chat-stale-result-032.png 由总控持有，计划0.3.3修复；本轮矩阵没有覆盖这一情形，不能因截图或 chat binding fixture 宣告 U04 PASS。本轮证据仍绑定不可变0.3.2快照；提交后已观察到总控修改主源码，0.3.3尚未重新冻结。新增检查必须绑定最终新 SHA，不能继承本轮结论。

**总控实测反馈，非本聊天独立复核：**032 Shell 两 Goal 经实际模型→批准→存储→独立读回通过，实际 Host Glance 发布和 Activity 通知通过；Calendar CRUD/独立 get、已授权清理与一次 Shell 重启通过，7个持久文件 SHA 相同，2Goal/2Run/2Action 重启不变，Activity 仅 restart restore。总控仍拥有原证据与最终收口。真实遗忘追问未携带旧值/refs，但0.6B模型编造新代码“星尘-2032”，语义必须保留 PARTIAL；不把没有旧值泄漏写成语义成功。

本聊天仅修改 owned visual/regression 测试、证据与这三份报告；未改产品 main/manifest、公共 CURRENT_STATE/HANDOFF、Host、生产数据或旧安装，未 push。剩余：总控0.3.3 U04最小修复及新SHA窄回归、真实模型语义限制、全链证据/最终版本产物绑定。公共状态与正式交接由总控维护。

## 保留的 0.3.1 与更早验收

# 0.3.1 最终冻结源码的独立验收

**REGRESSION_FIXTURE = PASS（118/118）；UI_CAPTURE = COMPLETE；UI_REDESIGN = PARTIAL；GLOBAL_MEMORY_DSL = PARTIAL（本聊天仅验上下文隔离子集）；官方 full-chain 整体状态由总控收口。**

主源码 SHA256 `66547123d714116b725302c16355ac933728609e2f945382e2769e84ac6fc1bd`。GM `a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178`，PAGE `75a9a3bf1117f5c4bf879f2f083cb9eb222a7dc48984cf86f1a2aeaf501a3743`。逐一核对后复制不可变 bundle；本聊天没有修改产品主源码、Host、生产数据或旧安装版，没有 push。

[最终 fixture 报告](evidence/ui-memory/final-031-66547123/regression/report.json) 的八套检查都在上述新源码实际执行，没有继承 0.3.0 PASS。

| 套件 | 实际通过 | 内容 |
|---|---:|---|
| selection | 2 | 对应结果与无关清理 |
| calendar | 9 | 动作批准/重复/编辑/权限与版本保护 |
| model stale protection | 12 | revision、取消、来源、墓碑与迟到回调 |
| incoming | 38 | 来信去重、同卡回复、确认、回执与持久动作保护 |
| chat binding | 15 | 原会话绑定、取消、独立保存、删除与备份 |
| chat proposal | 18 | 候选边界、旧 schema1、持久字段及跨会话校验 |
| model preflight | 12 | 账号预检、取消、授权刷新、更正原话 recent/earlier |
| chat derived | 12 | 实际检索 refs 写入、revision/forget/revoke 后整对排除 |

新增 [派生问答套件](ui_memory/tests/regression_derived.splash) 使用真实生产保存与回调路径：user 仅提问，assistant 合成回复由实际 context.hits 生成 memory_refs；随后分别更正、遗忘与撤销账号。检查 recent messages 与 earlier task 中原 user 问题/assistant 旧值均排除，无关完整问答及较早 user 备注保留；账号撤销前故意保留旧 gm_accounts，真正 mail.accounts 回调刷新后再构造模型 payload。**这些是传输 fixture 的通过，不代表真实模型语义或观察到真实泄漏。** 总控反馈 0.3.0 实际遗忘后追问只返回格式错误，没有观察到泄漏；旧 assistant 带回 Prompt 属于静态链风险。

[最终五尺寸八页长内容矩阵](evidence/ui-memory/final-031-66547123/visual-long/matrix.json) 保存 90 张真实可见 card-host PNG（隔离合成资料）；八页、两行键盘输入读回、对话滚动变化、左栏折叠和结果全宽页均完成。五尺寸八页总览已人工审阅，宽窄窗重点原图已查看。八页截图与输入数值不能替代所有表单、系统授权和真实动作验收。

| 请求尺寸 | 实际逻辑尺寸 | PNG 像素 | 输入 rect | 结果全宽 rect |
|---|---|---|---|---|
| 1400×900 | 1400×815 | 2800×1630 | [240,711,727,32] | [32,0,1368,815] |
| 990×539 | 990×539 | 1980×1078 | [198,435,429,32] | [32,0,958,539] |
| 990×400 | 990×400 | 1980×800 | [198,296,429,32] | [32,0,958,400] |
| 412×892 | 412×815 | 824×1630 | [164,711,135,32] | [32,0,380,815] |
| 1200×760 | 1200×760 | 2400×1520 | [236,656,531,32] | [32,0,1168,760] |

所有图无 >99% 同色帧，键盘读回 true、侧栏折叠 true；截图期间观察到 Host 调用只有合成 mail.accounts/calendar.status，自动 model.complete/mail.send/calendar.create/update/delete 为零。glance/Shell 通知与系统日历均未在本聊天调用。

**UI 尚存观察：**长对话滚动后导航，目标/能力页正文沿用之前滚动位置，部分尺寸首张正文近空白；长来信正文占满右栏，日历权限说明重复，412 展开左栏时输入区135×32，折叠后释放空间。空页上的滚动输入不等于可见内容滚动通过。没有为截图隐藏这些现象，原 PNG/snap 保留；产品整改由总控决定，本聊天没有改 main。

**失败与复测：**Calendar、1400/990×539/412 初次在 startup 发生 script time budget exceeded；同源串行仅补跑失败项后通过。chat_derived 初次把三种情形放同一事件触发 instruction limit，拆成三个事件后12/12；没有增加预算或改变 Host。首轮日志保存在 [attempts](evidence/ui-memory/final-031-66547123/attempts/)，原完整隔离输出仍在 app/build/ui-memory-20261003/frozen-031-66547123/。0.3.0 与更早失败证据未覆盖。

真实模型、正式 Shell 的 Goal 批准→写入→独立读回→重启、系统 Calendar CRUD、邮件投递、通知、最终 bundle check/scan 和版本产物交付由总控并行验收。本聊天不借118 fixture替代这些节点。公共 CURRENT_STATE 与正式 HANDOFF 仍由总控维护。

## 保留的 0.3.0 与历史验收

# UI 与全局记忆验收记录（2026-10-03）

**总体 PARTIAL。0.3.0 冻结快照的 fixture 已完成；总控正在处理 assistant 派生旧值的上下文风险，最终候选将更新到 0.3.1。以下结果不继承到新源码。**

## 最新已执行：冻结 0.3.0

主源码 SHA256 `7f83f0fcea2c802b558ef6d762f363193353e9e371a902a0c1a60d73adb166b2`；GM `a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178`；PAGE `75a9a3bf1117f5c4bf879f2f083cb9eb222a7dc48984cf86f1a2aeaf501a3743`。三个哈希逐一核对后复制不可变 source-bundle。Host 沿用下方已记录的二进制哈希。

[同源回归报告](evidence/ui-memory/frozen-030-7f83f0fc/regression/report.json)：**106/106 PASS_FIXTURE**，真实模型/邮件/日历均未执行。

| 套件 | 实际通过数量 |
|---|---:|
| selection | 2 |
| calendar | 9 |
| model stale protection | 12 |
| incoming / same-card reply | 38 |
| chat binding / session deletion | 15 |
| chat proposals / persisted validation / old schema1 | 18 |
| account preflight / corrected recent and earlier originals | 12 |

会话删除覆盖未确认无效、只取消原 A、A 迟到回调忽略、保留 B 与全局记忆、主文件与备份无原 ID、删掉最后一个会话后生成新空会话并恢复焦点。更正检查覆盖旧 user 原话不再进入 recent/earlier；**未覆盖新的 assistant 派生事实引用风险**，不得以此宣布 M05 全通过。

[五尺寸八页长内容矩阵](evidence/ui-memory/frozen-030-7f83f0fc/visual-long/matrix.json)：共 90 张 PNG，五个尺寸均已完成八页、真实键盘两行输入读回、滚动输入、侧栏折叠及结果全宽页。所有捕获无 >99% 同色图；Host 仅合成 mail.accounts/calendar.status，model.complete、mail.send、calendar.create/update/delete 为零。已审阅五尺寸八页缩略总览及宽窗/窄窗重点原图；总览用于发现布局与空页，不替代逐控件操作验收。

| 请求尺寸 | 实际逻辑尺寸 | 键盘读回 | 侧栏折叠 | 结果页 rect |
|---|---|---|---|---|
| 1400×900 | 1400×814 | true | true | [32,0,1368,814] |
| 990×539 | 990×539 | true | true | [32,0,958,539] |
| 990×400 | 990×400 | true | true | [32,0,958,400] |
| 412×892 | 412×814 | true | true | [32,0,380,814] |
| 1200×760 | 1200×760 | true | true | [32,0,1168,760] |

异常：chat_binding 首次 probe.json 为 NaN，来自 harness 对象与变量合并写法；改为项目已有对象与 literal 合并方式，同 SHA 仅重跑该套件 15/15。1200 首次 /g 截图 HTTP404，保留原日志，补有限次数截图重试，同 SHA 仅重跑该尺寸完成。[失败记录](evidence/ui-memory/frozen-030-7f83f0fc/attempts/) 保留；无产品主文件修改。

视觉限制：导航后正文沿用上一页滚动位置，990/412 的目标和能力页首张正文接近空白；原截图与 snap 均保留，需总控定位。长来信正文占据结果栏、日历权限说明重复、窄窗展开侧栏时输入区仅 135×32，折叠可释放空间。点击滚动已执行，但空页的滚动输入不能当作可见内容滚动通过。当前不能宣布 U01–U16 全 PASS。

真实模型语义、Goal 官方完整链、Shell 通知、系统 Calendar CRUD 与 bundle check/scan 由总控并行验收，本聊天未代验。公共 CURRENT_STATE/交接仍由总控收口。历史证据未重复运行或覆盖。

## 历史中间检查（保留原始结论）

# UI 与全局记忆验收初稿（验证执行聊天，2026-10-03）

**总体 PARTIAL。本文件是中间检查记录，不是最终候选通过声明。** 总控仍在修改主界面，版本、产物 digest 与最终源码提交须在冻结后填入。本聊天仅修改 owned 测试、证据及本报告；公共 CURRENT_STATE 与最终交接由总控收口。

UI_REDESIGN = PARTIAL；GLOBAL_MEMORY_DSL = PARTIAL；REGRESSION = PARTIAL。

## 已执行与绑定

- 稳定 baseline：0.2.26；主源码 SHA256 `6d4519bf4c3557b23ddb4163d12f1623aa21884c2ceffcb631f73c489a744f55`。隔离合成 app-data，未读取生产账号与用户原文。
- 独立 fixture 中间快照：`64377bd1b83820787e6eecda218639f0882e8274370fac6e321a19af850f9e36`，69/69 布尔断言通过（此前中间快照）。旧套件直接运行当前产品函数，Host、redraw 与测试 widgets 被替换；不代表模型推理、真实邮件投递或系统 CRUD。证据 [regression report](evidence/ui-memory/regression-intermediate-02/report.json)。
- 可见中间快照：`7ac335ad6827411e2809d0a88e465c2d4c36424dfd81e8981d248c8f87219f36`。宽窗八页、长内容、导航滚动、左栏折叠与全宽结果页已实际执行；尚非冻结产品。串行正确渲染证据在忽略的 `app/build/ui-memory-20261003/after-intermediate-03-serial/1400x900/`。这组图不替代最终五尺寸验收。
- card-host 二进制 SHA256 `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`。路径由现有 runtime_probe.py 提供；原有本地扩展与 unsigned 合成测试路径，不改变 Host 或准入。

最新中间快照0.3.0：源码SHA `3b087d3d18d4beff88dc27adad541b75a75e3b8e8814ed9b9f2dceac1b18ff48`，同源78/78 fixture通过；[最新回归报告](evidence/ui-memory/regression-intermediate-04/report.json)。新增候选9项最初2条断言把规范空数组误判为字段不应存在，已核对实际保存JSON并修测试，在完全相同源码重跑9/9；首次7/9失败保留在build，产品未因此修改。

最新[五尺寸长内容矩阵](evidence/ui-memory/after-intermediate-04/matrix.json)全部八页采集成功、无>99%同色图、无自动模型/外部写入；按真实导航/滚动/左栏折叠进入结果页。宽窗与412窄窗实际查看正文正确，默认右栏满屏长来信、重复结果/结果页按钮和少字优化仍待总控最终整合。稳定版[五尺寸长内容矩阵](evidence/ui-memory/before-long-serial/matrix.json)也已完成。

更新：新授权预检中间源码SHA `da33af72da154344456f1586afbcf9f452729adfe4854f3a5496d60ef2bc61bf` 的selection/incoming/chat/proposal共57项通过，preflight另8项通过，Calendar9启动eval首次超时后同源重试通过；旧集成Memory hit序列化使model12无法完成，详见 [独立发现](evidence/ui-memory/FINDINGS.md)。当前global_memory模块已有bracket scope处理，尚待总控同步。本轮不继承先前78通过到新源码。

412窄窗的实际键盘两行输入与读回通过，见 [input report](evidence/ui-memory/after-input-412/report.json)。Remote通用set_text的End只到当前行尾，初次残留后行属于harness；已根据当前TextInput键盘实现修正。

## 实际 fixture 回归

| 检查 | 结果 | 数量与边界 |
|---|---|---|
| 结果选择 | PASS_FIXTURE | 2，清理无关结果、恢复对应结果 |
| 日历动作保护 | PASS_FIXTURE | 9，重复点击、冲突增加、重新批准、编辑失效、权限撤销、恢复无批准、更新/删除版本变化 |
| 日历模型迟到保护 | PASS_FIXTURE | 12，Goal revision/取消、来源 SHA/revision、Claim revision、墓碑、来源删除、请求取代、候选编辑等 |
| 来信/同卡回复 | PASS_FIXTURE | 38，静默历史基线、提醒、去重、手写不调用模型、原意/时间保护、单独确认、回执/UNKNOWN/持久动作保护、取消回调等 |
| 聊天候选卡 | PASS_FIXTURE | 9，候选回原会话、取消无卡/记忆、另一会话不可打开、独立保存与恢复无动作、仅填未批准表单、重复打开忽略、无关模型intent拒绝 |
| 聊天 request binding | PASS_FIXTURE | 8，A请求→B请求→A迟到结果回A；B仍 pending；重复请求/回调忽略；取消回调不污染聊天/记忆/活动；独立保存读回与 boot 恢复不重发 |

上述78项绑定同一0.3.0中间快照；此前69项保留其独立旧SHA。总控冻结后必须重跑到新的独立输出目录，不能把数字直接沿用为 REGRESSION PASS。

## 验收项当前状态

| 范围 | 状态 | 尚缺证据 |
|---|---|---|
| U01–U16 | PARTIAL | 0.3.0中间五尺寸八页、长内容、左栏折叠与结果页已有；最终冻结候选输入/滚动/折叠、结果卡与动态副作用复测及人工视觉审阅 |
| M01–M07、M09–M12 | NOT_TESTED_BY_THIS_CHAT | 由记忆执行提供检索/DSL/迁移接口与运行证据；总控另核实实际上下文传输与模型语义表现 |
| M08 | PASS_FIXTURE_INTERMEDIATE | A→B晚返回与取消已过；需最终候选重跑与真实传输层记录 |
| R01/R02/R03 | NOT_TESTED_FINAL | 最终真实本地模型、多Goal批准→保存→独立读回→进程重启；chat_boot 单函数恢复不能冒充整 Shell 重启 |
| R04/R05/R07 | PASS_FIXTURE_INTERMEDIATE | 38来信+21日历/迟到保护断言；真实能力另验 |
| R06 | WAITING_USER_FINAL | 最终本机Calendar读取/CRUD/独立读回，新对象与系统确认由本人决定，不代点 |
| R08 | PARTIAL | 所有本聊天操作在指定 worktree/忽略build；未操作8401、旧安装版或生产数据；整体保护由总控核查 |
| R09 | NOT_TESTED_FINAL | 冻结bundle check/scan、版本/宿主/扩展提交与补丁 |
| R10 | PARTIAL | 此证据仅合成资料，无账号/Secret；用户reference原图只在build，本轮不导出；提交前仅owned路径检查 |

## 风险与异常必须保留

1. 初次 regression/intermediate-01 的宿主拒绝日志来自 harness 相对路径错误，已改绝对路径；该次无产品断言结果，不能算产品失败或通过。
2. 两个可见 card-host 同时截图时出现纯白帧/缺字；不同端口不保证截图有效。已改串行 `visual_matrix.py`，初次并行图只作异常记录，不用于对照PASS。脚本拒绝>99%同色图；非白图仍必须实际审阅正文。
3. requested 1400×900/412×892 被桌面可用高度限制为约814逻辑px；990×539、990×400、1200×760可按请求实现。必须记 requested、PNG像素与实际widget rect，不将请求参数当实际尺寸。
4. 记忆投影不能整库拼 prompt。最终必须检查 gm_context 的 hits、bytes、truncated、conflicts，确认每轮聊天/规划接入，遗忘不从旧会话语句复活；本聊天没有用78条 fixture替代M01–M12。
5. on_render/重绘/导航不能调用模型或写外部动作；可见快照8页与折叠过程捕获仅 mail.accounts、calendar.status，无 model.complete/mail.send/calendar.create/update/delete。但这不是完整渲染调用图证明，最终导航自动读取是否符合新页面合同仍须总控处理。
6. 可靠性断言检查实际调用数与持久动作保护；UI漂亮、卡出现、accepted不能替代真实动作或收到。UNKNOWN不重发，日历确认不能授权发送邮件。

## 复测接口

所有命令从指定 worktree 根执行；端口8484/8485先核对空闲。`--out`使用新目录，保留历史失败。无需模型、邮件账号、系统许可。

```bash
python3 official_muse/ui_memory/tests/regression_run.py --source official_muse/app/bundle/main.splash --out official_muse/app/build/ui-memory-20261003/regression/frozen-candidate --port 8485
python3 official_muse/ui_memory/tests/visual_matrix.py --source official_muse/app/bundle/main.splash --out official_muse/app/build/ui-memory-20261003/visual/frozen-empty --port 8484
python3 official_muse/ui_memory/tests/visual_matrix.py --source official_muse/app/bundle/main.splash --out official_muse/app/build/ui-memory-20261003/visual/frozen-long --long --port 8484
```

regression_run 一次复制source-bundle后跑所有套件；visual_matrix 一次复制source-bundle后串行五尺寸。每份report绑定源码SHA，最终还需bundle digest、源码提交、时间、Host/extension版本。`--hidden`只用于行为fixture；截图来自可见宿主。没有push/公开/费用/代理外发/系统确认。
