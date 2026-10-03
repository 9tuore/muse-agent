# 0.3.5 最终可见UI对照入口

五尺寸1440×900/1280×800/990×539/990×400/412×892，新冻结main `0e4c26dcdc0760a12cc2bb545cea2eb42e4170fba86f14974edbb992339332f7`，138张原图与5八页/2关键交互拼图已完成并人工审阅指定图；35页首屏、25前后滚动画面变化、5键盘读回、30长来信、18侧栏布尔检查通过。五尺寸Calendar五字段/邮件八段正文实际输入读回，确认/发送均可达未点击。1440实际809高，412实际813高。完整[矩阵](evidence/ui-overnight/final-035/visual/matrix.json)和[夜间报告](OVERNIGHT_UI_MAIL_CALENDAR_REPORT.md)；412展开时135px输入/长状态裁切/标题多行继续保留，指定路径通过不代表全面UI_PARITY_PASS。历史原图不混用。

# 0.3.3 夜间可见UI对照入口

最新五尺寸1440×900/1280×800/990×539/990×400/412×892共138张实际可见card-host原图与交互，在 [夜间报告](OVERNIGHT_UI_MAIL_CALENDAR_REPORT.md) 和 [矩阵](evidence/ui-overnight/frozen-033-c72b1357/visual/matrix.json)。新会话结果隔离及实际进程重启另有宽窄12图。下方0.3.2和旧版本记录原样保留，不混用SHA或继承PASS。

# UI 前后对照（0.3.2 冻结实测，U04 已复现待修复）

主源码 SHA256 `36bcd8703f103abda767280dfb7c3c5f2fa9cf1380c6c59479640ed4494dd126`。[114张原图与交互矩阵](evidence/ui-memory/final-032-36bcd870/visual-long/matrix.json)。这是实际可见 card-host 的隔离合成资料，私人参考图未复制到证据或 Git。before 与各版历史原图保持不变。

0.3.2 本轮指定交互通过：35次从上一页长内容滚动后进入新页均显示首屏标题，原0.3.1目标/能力近空白现象未再观察到；长来信默认摘要、展开后的有界正文可滚动、收起后可点击同卡回复；日历默认权限说明单次显示。五尺寸均完成两行键盘读回、长对话滚动、侧栏折叠和结果全宽页。990×400/412×892折叠侧栏后，日历新建五字段和邮件八段正文实际输入读回，日历执行确认与邮件发送按钮均可达，两个最终执行按钮都未点击。

| 0.3.1观察 | 0.3.2本轮观察 |
|---|---|
| 上一页滚动位置带入目标/能力页，部分首屏近空白 | 7页×5尺寸首屏标题检查35/35 |
| 长来信铺满右栏 | 默认摘要，展开正文可见高度80–176px，滚动/收起/同卡回复30/30 |
| 日历权限说明重复 | 默认权限摘要只显示一次 |
| 窄屏表单关键按钮尚未实际操作核验 | 两种窄屏字段/正文输入读回和关键按钮可达；未执行外部写入 |

**UI_REDESIGN = PARTIAL。** 总控另发现新建/切换会话可能遗留旧 Goal 结果，U04 已由总控实机复现，计划0.3.3修复，本矩阵未覆盖这一条；展开侧栏的长状态元信息仍有裁切、能力标题多行。不能把本轮子集通过写成全面 UI PASS。真实 Shell/系统动作和0.6B遗忘后编造新值的语义 PARTIAL，详见 [验收报告](FINAL_ACCEPTANCE.md)。

![0.3.2宽窗长对话](evidence/ui-memory/final-032-36bcd870/visual-long/1400x900/chat.png)

![0.3.2窄窗目标首屏](evidence/ui-memory/final-032-36bcd870/visual-long/412x892/长期目标.png)

![0.3.2窄窗长原邮件展开](evidence/ui-memory/final-032-36bcd870/visual-long/412x892/mail-original-expanded.png)

![0.3.2低矮窗口日历确认可达](evidence/ui-memory/final-032-36bcd870/visual-long/990x400/calendar-confirmation-reachable.png)

![0.3.2窄窗邮件长正文编辑](evidence/ui-memory/final-032-36bcd870/visual-long/412x892/mail-long-body-edit.png)

1400×900/412×892实际高度814逻辑px，PNG分别2800×1628/824×1628，其余按请求；2x原图与控件rect全部记录。首次误报与日历合成过滤契约修正保留在 [attempts](evidence/ui-memory/final-032-36bcd870/attempts/)，未修改产品解决测试问题。

## 保留的 0.3.1 与更早对照

# UI 前后对照：最终 0.3.1 冻结源码

稳定 before 仍使用原0.2.26证据，没有重复基线矩阵。最终 after 绑定 `66547123d714116b725302c16355ac933728609e2f945382e2769e84ac6fc1bd`，五尺寸八页长内容、键盘、滚动、折叠共90图均已采集并审阅总览；[最终矩阵](evidence/ui-memory/final-031-66547123/visual-long/matrix.json)。截图只含合成资料，私人参考图没有复制到证据或 Git。

**UI_REDESIGN = PARTIAL。** 0.3.1样式与0.3.0一致，本轮发现的滚动位置带入新页面、长来信正文占据右栏、日历权限文字重复仍保留。对话长正文可换行，窄窗折叠左栏与结果全宽页可用；系统动作、实际邮箱与日历可用性由总控单独核验。

![最终宽窗长对话](evidence/ui-memory/final-031-66547123/visual-long/1400x900/chat.png)

![最终窄窗折叠侧栏](evidence/ui-memory/final-031-66547123/visual-long/412x892/chat-sidebar-collapsed.png)

![最终窄窗全宽结果](evidence/ui-memory/final-031-66547123/visual-long/412x892/result-fullwidth.png)

1400×900、412×892 实际受可用屏幕高度限制为815逻辑px；其余三个尺寸按请求实现。原图、widget rect 与请求尺寸均在各份 report 中，未用请求参数冒充实际尺寸。

## 保留的 0.3.0 和更早对照

# UI 前后对照（0.3.0 冻结实测，最终 0.3.1 待定）

稳定 before 保留原样，未重复基线矩阵。最新 after 绑定主源码 `7f83f0fcea2c802b558ef6d762f363193353e9e371a902a0c1a60d73adb166b2`，五尺寸八页长内容、键盘、滚动、折叠已串行执行；[矩阵与逐页原图](evidence/ui-memory/frozen-030-7f83f0fc/visual-long/matrix.json)。所有画面为本机可见官方 card-host 与隔离合成资料，未导出私人参考图。

**UI_REDESIGN = PARTIAL**：当前五尺寸截图证明渲染与交互采集完成，不能替代最终 0.3.1、真实动作或每项可用性通过。目标/能力页保留滚动位置造成首张正文近空白，长来信正文仍占满右栏，日历权限文字重复。基线宽窄窗与最新宽窄窗均可直接对照，下方旧开发记录保持其独立 SHA。

![0.3.0 宽窗长对话](evidence/ui-memory/frozen-030-7f83f0fc/visual-long/1400x900/chat.png)

![0.3.0 窄窗折叠侧栏](evidence/ui-memory/frozen-030-7f83f0fc/visual-long/412x892/chat-sidebar-collapsed.png)

![0.3.0 窄窗全宽结果](evidence/ui-memory/frozen-030-7f83f0fc/visual-long/412x892/result-fullwidth.png)

## 保留的 baseline 与中间对照

# UI 前后对照初稿（2026-10-03）

**PARTIAL：稳定版 before已采集；after是未冻结的开发快照。** 不用用户私人reference图作公开证据。所有图来自本机实际可见 card-host 与隔离合成资料，不是设计稿或生成图。最终候选需要在同一冻结bundle重新采集after并逐页审阅。

稳定0.2.26主源码SHA `6d4519bf4c3557b23ddb4163d12f1623aa21884c2ceffcb631f73c489a744f55`。中间串行after SHA `7ac335ad6827411e2809d0a88e465c2d4c36424dfd81e8981d248c8f87219f36`。最新0.3.0开发快照SHA `3b087d3d18d4beff88dc27adad541b75a75e3b8e8814ed9b9f2dceac1b18ff48`，已串行采集五尺寸八页与长内容，见 [after矩阵](evidence/ui-memory/after-intermediate-04/matrix.json)。当前after只展示开发方向，不构成UI_REDESIGN PASS。

| 请求尺寸 | before实际PNG像素 | 实际逻辑尺寸 | 八页 |
|---|---|---|---|
| 1400×900 | 2800×1626（初始root采集） | 1400×813 | 已采集 |
| 990×539 | 1980×1078 | 990×539 | 已采集 |
| 990×400 | 1980×800 | 990×400 | 已采集，旧导航需滚动 |
| 412×892 | 824×1628 | 412×814 | 已采集，高度受桌面限制 |
| 1200×760 | 2400×1520 | 1200×760 | 已采集 |

PNG均2x，本机可用区域会随窗口位置/系统改变1px。最终以各份report的PNG像素与snap实际rect为准。五尺寸baseline共40张合成空状态图在 [before证据](evidence/ui-memory/before/1400x900/report.json)。

| 页面 | 稳定版观察 | 开发快照与未解决项 |
|---|---|---|
| 对话 | 监听块、中央会话列表、重复时间、空会话教程卡、常驻技术状态 | 历史移左栏、输入在底部、技术状态隐藏；长正文正确串行截图可读，右栏长来信仍须折叠/滚动/最终窄屏检查 |
| 邮箱 | 正文与sender可读，但账号/消息ID/长技术说明与重复步骤占空间 | 页面适配仍在集成；同卡意图、手写、起草/预览/确认不可丢，需最终截图 |
| 日历 | 真实权限/输入/查询/确认基础存在，文字密集 | 0.3.0月/周/日程已接线：显示绝对日期、时区、未加载范围和合成事件计数；字段按新建/选中出现。真实query范围与CRUD仍另验，不宣布可视日历最终PASS |
| 记忆 | 来源/修订/作用域字段铺在默认页面 | 全局可读列表/DSL展开与更正/遗忘由主界面接线，最终M12尚待验证 |
| 长期目标 | 目标列表与详情已有 | 三条合成目标用于滚动；不显示虚构进度，最终确认一个Run不误标长期目标完成 |
| 活动 | 详细审计记录较长 | 摘要与技术详情仍需核对批准/失败不丢失 |
| 能力 | 应用能力与系统/账号状态区分已有 | 显示适配需验证未连接/仅写入不误标绿色可用 |
| 设置 | 模型预算为真实只读说明 | 新记忆检索开关/导出/会话改名按实际函数；不新增密钥输入，最终可用性待验 |

稳定空状态对话：

![稳定版宽窗对话](evidence/ui-memory/before/1400x900/chat.png)

稳定窄窗对话：

![稳定版窄窗对话](evidence/ui-memory/before/412x892/chat.png)

长场景生成三条Goal/记忆、五个历史会话、八封合成邮件、三张来信卡、四条合成日程，均显式fixture。它只测视图；日历合成事件不代表系统CRUD，合成assistant文本不代表模型推理。

截图harness入口 [visual_matrix.py](ui_memory/tests/visual_matrix.py)，source/out/port/long/sizes参数见 [FINAL_ACCEPTANCE](FINAL_ACCEPTANCE.md)。`shortcuts`导航真实scroll再click；body按`page_content`/`calendar_editor`滚动；左栏折叠点击‹，窄屏卡入口进入实际right_page并记录rect。按钮存在或非白像素不自动判可用。

初次并行可见宿主导致白帧/缺字，已保留在忽略build中，不列为有效after。后续必须串行采图；私密原reference不复制到evidence/Git。

0.3.0开发宽窗长对话与月日历（合成资料）：

![开发长对话](evidence/ui-memory/after-intermediate-04/1400x900/chat.png)

![开发月日历](evidence/ui-memory/after-intermediate-04/1400x900/日历.png)

412窄窗点击卡进入全宽结果页，实际right_page rect `[32,0,380,813]`：

![开发窄窗结果详情](evidence/ui-memory/after-intermediate-04/412x892/result-fullwidth.png)
