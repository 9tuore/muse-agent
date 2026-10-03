# 0.3.5 最终独立验收（2026-10-03）

**指定fixture子集162/162通过；五尺寸138张新源可见UI原图与指定交互通过；完整产品验收仍由总控汇总真实模型、新Shell、Goal链、重启及idle证据。** 本次没有重复033/034的其他场景或GM135套件，没有用历史截图代表035。

主源码SHA256 `0e4c26dcdc0760a12cc2bb545cea2eb42e4170fba86f14974edbb992339332f7`；manifest版本0.3.5，BLAKE3字段 `968e29358a1d2d7ec224f2a2b3a75afcab24524320567fd86fe6aceaafa5a419`；总控修复提交 `4135d0c`。逐字节复制不可变bundle后执行，manifest字段从现场读出，官方密码学bundle验签由总控完成。[冻结记录](evidence/ui-overnight/final-035/freeze.json)、[汇总](evidence/ui-overnight/final-035/summary.json)。实际截图/fixture使用card-host SHA `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`；新Shell f5989ea候选的真实模型/重启是总控独立范围，不能把本机card-host照片称作新Shell照片。

## 字节上限复现与修复后证据

0.3.4 main d2c04715新增13项第一次有效pilot为12通过、1失败；整套149+13为161/162。两个候选serialized对象合计1598byte，JSON数组1601byte，连固定说明文字注入1741byte。只有payload上限失败，引用过滤/会话隔离等均通过。[有效失败report](evidence/ui-overnight/final-034/attempts/focus-d2c04715/focus-pilot-r2/report.json)、[原始focus](evidence/ui-overnight/final-034/attempts/focus-d2c04715/focus-pilot-r2/focus-boundary.json)、[完整回归](evidence/ui-overnight/final-034/attempts/focus-d2c04715/full-regression/report.json)。首pilot有原始文件vs重序列化比较误报以及新建对象重复键的压力构造问题，已仅修owned fixture，保留两次attempts，不把无效压力计为产品PASS。

总控明确契约：JSON数组payload≤1600，固定140byte说明文字另计。035仅在chat_task_focus预算中初始计[]的2byte，后续计逗号1byte，并更新版本。相同压力场景修复后只注入最新一个能容纳的候选，payload1241byte、完整注入1381byte，正文仍980byte；采用整对象准入，没有截断正文。[035焦点13项report](evidence/ui-overnight/final-035/regression/task_focus/report.json)、[修复后原始focus](evidence/ui-overnight/final-035/regression/task_focus/focus-boundary.json)。本聊天未修改产品main/manifest或Host。

## 一次完整最终回归

[十二套162/162](evidence/ui-overnight/final-035/regression/report.json) 同一035 SHA首次执行全部成功，无startup预算异常，无禁止调用；逐套runtime.log保留。

| 套件 | 通过 | 验证范围 |
|---|---:|---|
| selection / calendar / model | 2 / 9 / 12 | 对应结果、Calendar批准/重复/权限/版本、迟到模型保护 |
| incoming / chat binding / chat proposal | 38 / 15 / 18 | 来信/同卡回复、原会话绑定、候选持久化与确认语义 |
| model preflight / chat derived | 12 / 12 | 新鲜授权预检、更正/遗忘/撤销后的派生上下文排除 |
| mail monitor / mail calendar chain / chat goal binding | 15 / 9 / 7 | 监听去重与恢复、合成CRUD/get、会话Goal归属 |
| task focus | 13 | 当前会话Goal独立readback count、pending请求原会话、refs生产保存、correct/forget/revoke、latest2/1600上限/oversize/旧无refs不注入、malformed refs拒绝与验证只读 |

全部是生产函数+fake transport+真实隔离fs存储；Calendar合成链含create/update/delete各1次、独立get/验证与同Goal Run/Action存储，[waiting_user](evidence/ui-overnight/final-035/regression/mail_calendar_chain/chain-waiting-user.json)、[created](evidence/ui-overnight/final-035/regression/mail_calendar_chain/chain-created.json)、[updated](evidence/ui-overnight/final-035/regression/mail_calendar_chain/chain-updated.json)保留。没有真实邮件发送/删除、Calendar写入、权限弹窗或账户变更。chat_goal_binding中的恢复是函数级恢复；本轮035未重复033 U04的实际进程重启两窗，最终035真实Shell重启由总控独立执行。033 Host HTML fallback既有合成集成测试1/1原证据保留，组件未变，本次未重复；不能将其描述为035重新执行。

## 五尺寸实际可见UI

[矩阵](evidence/ui-overnight/final-035/visual/matrix.json) 五尺寸串行可见card-host，全部首次完成，28/28/28/28/26，共138张原图。八页各尺寸contact sheet共5张以及两张窄/矮关键交互contact sheet均人工查看；另人工查看宽窗035版本标签、990×400日历确认、412长邮件编辑与原文展开的4张完整原图。review拼图是辅助，原PNG不经修改。

| 请求尺寸 | 实际逻辑尺寸 | 原图数 | 对话输入rect | 日历执行确认rect |
|---|---|---:|---|---|
| 1440x900 | 1440×809 | 28 | [240, 705, 767, 32] | [57, 671, 172, 36] |
| 1280x800 | 1280×800 | 28 | [240, 696, 607, 32] | [57, 662, 172, 36] |
| 990x539 | 990×539 | 28 | [198, 435, 429, 32] | [57, 401, 172, 36] |
| 990x400 | 990×400 | 28 | [198, 296, 429, 32] | [57, 262, 172, 36] |
| 412x892 | 412×813 | 26 | [164, 709, 135, 32] | [57, 719, 172, 36] |

1440请求900高度实际809，412请求892实际813，受桌面可用区域限制；其余按请求，PNG为2x实际逻辑尺寸。完整rect/PNG尺寸在summary，不以请求值冒充实际值。

- 从上一页长内容滚动后进入7页×5尺寸，首屏标题35/35；Chat/Mail/Calendar/Memory/Settings前后原图25/25实际变化，两行键盘读回5/5。
- 长来信默认摘要、展开、有界正文高度/内层滚动、收起、同卡回复30/30。外层使用边缘滚动使收起/回复可达；不把内层滚动当作按钮可达证明。
- 左栏收起/展开五尺寸、右栏收起/展开四个宽度>740窗口，18个布尔检查通过。412右栏为零宽设计，使用全宽结果页，不声称窄窗右栏已可见展开。
- 五尺寸新建日历标题/起止/时区/地点5字段实际输入并读回，合成冲突查询、本地预览与执行确认可达；邮件收件人/主题/8段正文实际输入并读回，发送按钮可达。最终Calendar执行确认和邮件发送均未点击。历史字段mail_preview_control_reachable实际记录发送按钮位置，不代表预览或投递。
- 138图无>99%同色捕获、无UI断言失败。fake Host仅accounts/status/list，model.complete/mail.send/calendar写入为0。[035设置版本原图](evidence/ui-overnight/final-035/visual/1440x900/设置-scrolled.png)已人工确认。

展开侧栏的412聊天输入仍135px，部分长状态/日期元信息裁切、能力页顶标题多行；折叠后关键工作流可用。这些排版限制继续保留，不能标U01–U16全面PASS、完整1:1或真实系统动作PASS。真实模型的格式偏好/遗忘语义等按总控035实际回答评分，不继承033/034语义结论。

## 交接与边界

本聊天独立工作已完成：新fixture、可复现034失败、035最终162与138图、报告/汇总。034五尺寸138原图及1440拼图保留[中间证据](evidence/ui-overnight/final-034/README.md)，只有1440拼图人工查看，不作为最终035视觉证据；033与更早证据原封。

仅修改owned visual/regression测试、ui-memory/ui-overnight证据、FINAL_ACCEPTANCE/UI_BEFORE_AFTER/本报告；未改公共CURRENT_STATE/HANDOFF、生产存储、旧安装、其他owner测试或Host；没有push或发布。总控剩余：035真实模型20case、Goal批准/存储/readback、新Shell restart/idle、官方hub/BLAKE3与全局结论收口。总控可直接从本报告和final-035/summary.json接手，不需要重跑本子集。

## 保留的0.3.3夜间验收记录

# Muse 0.3.3 夜间 UI／合成邮件与日历验收（2026-10-03）

**本聊天负责的指定范围通过：149/149 fixture，Host HTML fallback 合成集成测试1/1，五尺寸UI交互138张原图，U04实际隔离进程重启12张原图/18项检查。整体产品与真实模型语义仍由总控收口，不宣布全项目PASS。**

主源码 SHA256：`c72b13578964b535ee36c4d60fc9d77eaa5e6ed277c2ef32c2cfd42413076855`；manifest版本0.3.3，`integrity.bundle_blake3`字段 `211dc76214949ff956680c6f64aa4693576eb18ac9da1bda594c280607ada21f`。主源码逐字节匹配总控冻结值后复制不可变source-bundle；manifest身份一致，官方BLAKE3验签由总控执行。本轮未重算canonical GM/PAGE，其未改来自总控反馈。[冻结记录](evidence/ui-overnight/frozen-033-c72b1357/freeze.json)。

所有修改和运行都在指定worktree；本聊天只写owned测试、证据及报告。没有改main/manifest、Host源码、生产账号/用户资料、公共CURRENT_STATE/根总报告；没有push、申请权限、发送/删除真实邮件或写改删真实日历。旧0.3.2与更早证据原样保留。

## 实际运行边界

- fixture 与可见UI采用现有独立card-host，二进制SHA256 `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`；隔离fs，模型及Host邮件/日历传输全部替换为合成返回。8485仅行为fixture，8484可见窗口串行采集；可见采图明确移除MAKEPAD_HIDE_WINDOWS。
- 这些原图来自真实渲染的card-host，不能称为最终新Shell截图。总控候选Shell的Host SHA `f5989ea3b5a80a357eda4fde5a64684f4adc7e0c0b441f46b8c706845dd5f215`，身份摘录在 [candidate reference](evidence/ui-overnight/frozen-033-c72b1357/controller-candidate-reference.json)；该Shell、24个真实模型场景、实际Goal存储链、10次重启和idle性能由总控负责。
- 0.3.2真实Calendar CRUD及清理属于总控已完成的历史证据，本轮未重复。本轮Calendar CRUD/get均为合成服务调用，绝不能当作系统日历写入。

## 回归结果：149/149

[汇总与逐套原报告](evidence/ui-overnight/frozen-033-c72b1357/regression/report.json) 全部绑定同一新SHA，不继承0.3.2结果。

| 套件 | 通过数 | 验证范围 |
|---|---:|---|
| 原selection/calendar/model/incoming/chat binding/proposal/preflight/derived八套 | 118 | 2/9/12/38/15/18/12/12，旧schema、动态批准、同卡回复、取消/迟到、持久保存与记忆上下文隔离 |
| 新mail monitor | 15 | 夜间明确要求的到达/格式/恢复/跨会话场景 |
| 新mail → calendar chain | 9 | 来源、日期不明阻止、明确日期、冲突、waiting_user、合成CRUD/get、重复阻止 |
| 新Chat Goal binding | 7 | 原会话绑定、新会话隐藏、全局历史保留、切回/切空、生产函数恢复不重发 |

来信到达不会自动调用model.complete/mail.send/mail.delete，15项的forbidden_calls为空。历史206封邮件作为静默基线另由原incoming套件覆盖。

| 新监听场景 | 实际断言与结果 |
|---|---|
| ID去重 | 重复相同ID不增卡、不增MAIL_INCOMING：PASS |
| restart | 调用生产mail_watch_boot回读，原卡与去重事件不重复：PASS；这是函数恢复，进程重启另见U04 |
| 单次事件 | 单封新邮件产生一次MAIL_INCOMING：PASS |
| 顺序 | 较旧时间但新ID仍加入，不按时间误删：PASS |
| 多封 | 同批两封都保留，一次扫描产生一个批次MAIL_INCOMING：PASS |
| 空body | 空字符串仍保留卡与ID：PASS |
| 空subject | 显示函数返回“（无主题）”：PASS |
| 缺sender | Host header输出的sender:null仍保留正文/卡：PASS；未以未知Host形状代替契约 |
| HTML fallback | Muse收到Host规范化文字后完整保留：PASS；Host转换另经真实既有合成集成测试验证 |
| 长body | 80段完整保存，摘要为60字符加省略号：PASS |
| 中文 | 中文完整回读：PASS |
| 英文 | 英文完整回读：PASS |
| unavailable | 账号查询失败保留旧提醒/事件并提示重试：PASS |
| reconnect | 同步失败保留，恢复后不重复：PASS |
| 跨chat全局 | 切换A/B后监听卡与新来信属于全局邮箱状态：PASS |

[Host HTML报告](evidence/ui-overnight/frozen-033-c72b1357/host-html-report.json)：实际执行官方现有 `an_app_signs_in_on_the_hosts_sheet_and_reads_and_sends_without_the_password` 测试，1 passed/0 failed/9 filtered。测试用Fake邮件后端、临时目录和FileVault；包含HTML-only消息的normalize、mail.message可读正文及安全HTML断言。未连接真实邮箱，未创建实际密码或系统凭证；其模拟发送不是投递。记录所编译测试二进制及相关源码哈希，不把此组件测试冒充最终Shell实机运行。

## 邮件转日历：合成批准链

[chain原报告](evidence/ui-overnight/frozen-033-c72b1357/regression/mail_calendar_chain/report.json) 9/9。

1. 实际mail_link_calendar函数把合成账号/消息/source ID绑定同一Goal与记忆来源；合成模型只回候选。
2. 开始/结束为空时不能查询有效候选或生成批准；明确2026-10-04 15–16时、Asia/Shanghai后候选完整。合成时间重叠使确认卡无法生成；去掉冲突并重新查询后link.status=waiting_user，Goal仍planned、Run/Action为0、写入为0。
3. 明确合成批准后，calendar.create返回合成ID/version，再独立calendar.get匹配全部字段，Action verified、Run completed、Goal产物fs独立回读匹配。重复确认只产生一次create。
4. 同一合成事件update使用原version，独立get验证v2和新标题；delete再次核对版本并get明确found=false。合成写入总计3，calendar.get总计5（更新/删除均含写前版本读取），3 Action均verified。

[waiting_user快照](evidence/ui-overnight/frozen-033-c72b1357/regression/mail_calendar_chain/chain-waiting-user.json)、created/updated诊断同时保留。以上服务返回都在owned transport生成，真实OS服务请求为零。

## 五尺寸：138张真实可见原图

[完整矩阵与逐页原图](evidence/ui-overnight/frozen-033-c72b1357/visual/matrix.json)。1440×900、1280×800、990×539、990×400各28张，412×892为26张。每尺寸八页首屏/滚动、左栏折叠展开、长邮件展开/内层滚动/收起/同卡回复、结果全宽、日历新建字段及邮件正文编辑都实际操作。五尺寸总览与宽窄重点原图已人工查看；图片是合成内容，不含私人参考原图或生产账号。

| 请求尺寸 | 实际逻辑尺寸 | PNG像素 | 对话输入rect | 日历执行确认rect | 邮件正文可见rect |
|---|---|---|---|---|---|
| 1440×900 | 1440×814 | 2880×1628 | [240,710,767,32] | [57,676,172,36] | [46,524,1352,142] |
| 1280×800 | 1280×800 | 2560×1600 | [240,696,607,32] | [57,662,172,36] | [46,524,1192,142] |
| 990×539 | 990×539 | 1980×1078 | [198,435,429,32] | [57,401,172,36] | [46,404,902,125] |
| 990×400 | 990×400 | 1980×800 | [198,296,429,32] | [57,262,172,36] | [46,284,902,106] |
| 412×892 | 412×814 | 824×1628 | [164,710,135,32] | [57,720,172,36] | [46,547,324,142] |

1440请求900高、412请求892高实际受桌面可用区域限制为814逻辑px；没有假称请求高度已实现。

- 35次从上一页滚动后导航，首屏标题均在各自body顶端。
- 长Chat/Mail/Calendar/Memory/Settings各5尺寸的前后图均变化，共25项；两行键盘输入五次完整读回。
- 左栏折叠/重开五尺寸通过，右栏折叠/重开四个宽度通过，共18布尔检查。412右栏设计宽度为0，采用“卡”进入全宽结果页，未虚称零宽栏展开可见。
- 长原邮件默认摘要，五尺寸展开、可见高度80–176px、内层滚动画面变化、收起和同卡回复意图读回共30项通过。
- 五尺寸全部折叠侧栏后输入日历五字段/精确冲突查询/本地预览，执行确认按钮可达；邮件八段正文实际输入和完整读回，发送按钮可见。**本聊天没有点击任何最终日历执行或发送邮件按钮。** 历史字段mail_preview_control_reachable实际是发送按钮位置，不能解释为已发送。
- 可见Host调用仅合成mail.accounts/calendar.status/calendar.list；model.complete/mail.send/calendar.create/update/delete为0。138张图均无>99%同色图。

仍有排版限制：412展开左栏时输入宽135px、能力标题分多行、部分长状态/日期元信息裁切；折叠后关键工作流可达。截图与这些指定交互不能替代所有设置功能、实际账号授权或完整U01–U16。

## U04：实际退出并重启隔离进程

[U04报告](evidence/ui-overnight/frozen-033-c72b1357/u04/report.json)，1280×800/412×892各6张图、9项检查，共12图/18项。

使用实际make_plan创建会话A关联Goal，通过core_start_run、合成产物写入和core_finish_run构造完成状态；明确标记人工合成产物，不声称真实模型执行。真实UI在新空会话B的结果页显示空态，切A显示原Goal与同一产物，切B再次空态。退出实际card-host进程，再用同一隔离app-data启动，B仍空、切A恢复。前后goals.json与产物SHA相同，1Goal/1Run/0Action不变，无模型或外部写入自动重发。

宽窗空结果页面积>99%为背景，原均匀帧判据误报3张；原report/flags保留。[capture质量复核](evidence/ui-overnight/frozen-033-c72b1357/u04/1280x800/capture-quality-review.json)记录顶部strip确有按钮/空态文字，原图和两尺寸六图总览已人工查看，结论是合法空结果页。后续驱动保留uniform标记，并验证空态及顶部实际像素；没有放宽五尺寸长内容矩阵的同色检查。窄窗原始report无此误报。

## 失败与修正记录

[attempts](evidence/ui-overnight/frozen-033-c72b1357/attempts/)全部保留，不覆盖旧证据。

- 初次mail_monitor省略sender键，Splash报prototype property缺失；核对实际Host header总输出sender键（源缺失为JSON null）后，fixture改为sender:nil，15/15。原畸形Host响应没有被写成合法接口通过；UI对所有非法传输形状的鲁棒性未声明。
- mail_calendar_chain初次startup时间预算超限，同源重试9/9。
- model/preflight初次（preflight两次）在UI脚本startup时间预算超限，同源仅重跑失败套件后通过。
- 原incoming两次在密集历史扫描/后续同步事件内时间预算超限；owned copy保留38项原断言，将初始监听与草稿处理拆成两个timeout事件后同源38/38。原round2文件、产品和Host预算未改。
- 1280视觉初次startup超限，仅补跑此尺寸成功。
- U04初次驱动在端口尚未ready时退出，改为有限启动等待；后续实际检查成功。宽窗均匀帧误报按上述真实原图复核保留，没有重写原报告。

完整bundle/state和失败输出仍在忽略的app/build/ui-overnight-20261003/frozen-033-c72b1357/；Git证据仅复制合成报告/日志/原图/诊断，不复制运行账户资料、完整Host二进制或用户原文。

## 交接与未完成范围

指定0.3.3夜间UI/合成Mail/Calendar/U04验收已完成；四个Python驱动py_compile与git diff --check已实际通过。0.3.3真实模型的时钟/日期问答与语义、最终新Shell实机截图、实际Goal完整链、10次重启及idle性能由总控继续并写根总报告；本聊天不代验或将fixture提升为真实full-chain。此前0.6B遗忘后编造新值的语义PARTIAL不可被149条上下文/动作fixture覆盖。

总控最新真实033 benchmark反馈（本聊天未独立代跑）：动作请求频繁产生intent/proposal却漏掉schema必需reply，Host因此拒绝；结果追问也缺当前会话候选字段的有限上下文。总控准备补提示与context后冻结0.3.4。当前149项与150张原图只代表0.3.3上述合成/视觉范围，不能继承到新SHA或掩盖真实模型问题。新版本将按影响补窄回归与必要截图，暂不重复全矩阵。

[990×400日历关键确认可达](evidence/ui-overnight/frozen-033-c72b1357/visual/990x400/calendar-confirmation-reachable.png) · [412邮件长正文编辑](evidence/ui-overnight/frozen-033-c72b1357/visual/412x892/mail-long-body-edit.png) · [412新空会话结果](evidence/ui-overnight/frozen-033-c72b1357/u04/412x892/new-empty-no-goal.png) · [412重启后原会话结果](evidence/ui-overnight/frozen-033-c72b1357/u04/412x892/restart-switch-original-restores.png)
