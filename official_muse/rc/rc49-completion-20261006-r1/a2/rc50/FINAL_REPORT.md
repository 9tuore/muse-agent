# rc50r2 冻结源码：T19 受影响 UI 回归

结论：**PASS_SCOPED_UI**。同一源码0e705f33的四组可见card-host fixture均通过，16个检查组无失败。新增宽/窄结果不复用rc49。此结论不代表Root最终Shell全链，也不代表手机验证。

| 请求尺寸 | 实际尺寸 | 历史区高度 | 初始未裁剪标题按钮 | 首尾选择/删除预览取消、输入/折叠/滚动、快捷导航 |
|---|---|---|---|---|
| 1400×760 | 1400×760 | 458 | 6 | PASS |
| 990×539 | 990×539 | 285 | 3，下一条被裁为41点 | PASS |
| 990×380 | 990×380 | 161 | 1，下一条被裁为33点 | PASS |
| 412×892 | 412×809 | 496 | 7 | PASS |

宽窗证明至少四条完整可见。矮窗通过真实滚动到首尾、选择对应完整标题、打开删除预览并取消，历史16条无删除或内容改变。各窗口均能输入回读、空消息发送校验、折叠及恢复、长正文滚动；邮箱/日历/记忆/更多→操作记录通过真实滚动点击和页面标题核对。宽/普通/矮窗也验证右栏折叠。窄窗右栏原本自动隐藏，只验证其实际存在的左栏折叠。

短中文一行、长中文最多两行并尾部省略：人工检查当前宽窗 expanded.png、oldest-and-short-title.png 和窄窗 expanded.png。可见内部按钮正常高48，源码行高54，连续行起点间隔58（54+4），滚动边缘的裁剪矩形不等于行高改变。16条原始完整标题和内容在选择/删除预览取消后保持。

## 原要求核对与此前判定修正

本次直接读取用户Downloads中的 `Muse_三小时_记忆安排改期与会话标题_执行包_20261003 (1).zip`，SHA256 `8d60e672af034370c1aea01020053c848dd7d30994857973f3a689341ffe4f31`，与a3/SOURCE_PROVENANCE.json一致。

- `Muse_三小时收口/02_二十项验收.md` 第28行定义T19为短一行、长最多两行省略、等高、全文不变、无JS测量或悬停动效、原生方案需确认、窄视口不冒充手机。成员SHA256 `70b356da87086950f1b0849c661bce59541065c5ed47c743503b06e1e15e1a1f`。
- `Muse_三小时收口/01_三小时总控提示词.txt` 第178–208行明确：沿用既有字体/颜色/间距及选中态；不加悬停滚动、跑马灯或其他新动效；不用JS测文字/字符裁剪，不增ResizeObserver/canvas；测试观察布局不等于产品增加测量。成员SHA256 `8ceb22e3372a22348ae801cfee6acd5170c49a2972a1f0075e66c976a18f88e3`。
- 上述原文没有“每一种矮窗口同时显示四条”的条件。ROUND_ACCEPTANCE.md第80行的“4可见fixture视口通过”是一次历史测试结果，不能转换成所有高度的用户硬要求。此前a2/rc50/REPORT.md对此保留的条件性PARTIAL判断被本次直接核对纠正；旧报告、截图和哈希不覆盖，最终解释以本文件为准。
- 原生方案用户确认复用仓库ROUND_ACCEPTANCE.md第80、158行的已确认记录（USER_CONFIRMED / REUSED_SUPPORTING），本轮没有重新向用户求确认，也没有代替用户作新决定。

## 组件来源与复用边界

当前原生history_list从声明到shortcuts前的源码，与冻结rc49/readable-rc49-r2逐字一致，片段SHA256 `816242f448546ea35d14efeed72d2a9e17fa4d71de85e4a16699ff86d4776d2a`。使用原生Nav/ButtonFlat、`max_lines: 2`、`text_overflow: Ellipsis`、54行高和原有选择/删除回调；没有WebView、JS测量、悬停滚动或跑马灯代码。原Nav的颜色悬停反馈是既有样式，不能误读成新增标题悬停滚动。

原提示词207行还列英文长词、混排、emoji等变体。本轮新增执行仅覆盖短中文/长中文、布局、折叠和完整存储；不声称这些额外文本变体在rc50重新执行。标题组件逐字相同提供复用依据，历史完整变体证据的最终采用由Root结合已有记录完成；本报告只对本轮受影响UI范围给PASS。

## 冻结身份与证据

- 源码SHA256 `0e705f33c36c77e32c335c1489a7ebe047a2e6476a473a4678cbffb767ca480f`，本轮开始核对app/source/main.splash与隔离快照完全相同。Root标记50r2冻结；case内source_kind保留生成时的working_source，不改写原始输出。
- card-host SHA256 `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`；独立8517、全新case状态、合成16对话、拦截host.request。仅拦截mail.accounts/calendar.status，无模型、邮件发送和系统日历写入。
- 新宽/窄目录分别为visible-1400x760-r1、visible-412x892-r1；原普通/矮窗证据仍同SHA。`FINAL_SUMMARY.json`汇总实际几何；`FINAL_EVIDENCE_SHA256.json`绑定新增证据及旧摘要。自建进程已关闭，未控制8493或主profile，未改主源码、重包或push。

截图入口：宽窗 `visible-1400x760-r1/expanded.png`、短/长对照 `visible-1400x760-r1/oldest-and-short-title.png`、窄窗 `visible-412x892-r1/expanded.png`，各目录另含collapsed与long-top/bottom及页面快照。
