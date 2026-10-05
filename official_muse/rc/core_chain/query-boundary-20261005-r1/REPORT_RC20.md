# rc20 日历查询边界收尾复核

**状态：FIXTURE_PASS_NO_LIVE_UI_MODEL_CALENDAR_CLAIM。**

本次15:18:26接续，2026-10-05 15:24:06最终执行完成。仅新增总控要求的两类helper检查，重新绑定原13组及5次第二进程恢复，没有继续扩大变体。

## 最终身份

- manifest：0.3.26-rc20。
- readable：`162d3ebb631b88ac92a9e11314a8b4128ff51e18661eb5fdadecb0eca239f54e`。
- compact：`302b562f91d8bcbf2d3ecc69b1b39dfb2dbe2710a22e9b6102ee51de484219a9`。
- 实际CardHost：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。完整启动路径、来源锁及manifest在各summary记录。
- 默认预算，不修改Host或提升执行预算。最终主文件SHA仍与本绑定一致。

## 结果

**15组、101项全部PASS，5次真实第二进程恢复。**

- rc20-main-r1：原13组，89项；精确窗口、弹性、改期、软/硬限制与交集、日数限制、时区、手动纠正、跨calendar、来源时区与日期、5次重启恢复均通过。
- rc20-semantic-r1：两类新增helper，共12项。单点预约错误日期拒绝；同日正向候选和来源revision保留；4条无关任选表达不扩大；4条否定表达拒绝；真实同日时间任选保留。

完整逐组计数见 RESULT_TABLE_RC20.md，实际布尔检查才计数，没有把输出对象和文本计为检查。

## r5原失败及修复

Root根据A3静态审查补单点日期与否定/时间上下文判断。A2实际r5 helper中singlepoint_wrong_day的3项通过；另一个helper8项通过、1项失败：

“2030-06-12 时间固定15点见，菜单任选，Asia/Shanghai。”

此时r5返回整日范围，而非保持原15:00–15:30候选或拒绝；正则中的“时间.{0,12}任选”跨越了“固定15点见，菜单”语境。原记录在 rc19-semantic-r5/unrelated_negated_flexible/first/report.json。

Root收紧为相邻许可词并递增到rc20。A2相同helper重新验证：该唯一菜单邻句不再扩大，其他3条无关表达、4条否定和真实时间任选仍通过。没有靠删除失败样本完成验收。

r5原13组与5次恢复均为89项PASS，见rc19-r5；R5_REVIEW.json如实记录该版整体为PARTIAL，不能用旧13组PASS覆盖新增helper失败。

## 历史结果保留

原r4 REPORT.md / PUBLIC_RESULT.json未覆盖，哈希重新核对保持原值；原15组100项PASS仍属于85da03a6/11f46af5的r4绑定，未改成rc20结果。rc18宽查、rc19精度/时区/日期失败和manual旧断言失败仍保留。

rc20计数只有这次新绑定的89+12=101项；之前r4的额外纯clipping10项和source_day1项没有混入rc20计数。

一次首次r5命令expected SHA输入多写字符，guard在运行前拒绝，未生成测试输出；校正成实际观察SHA后才正式运行。不是产品变更或产品失败。

## 边界

真实CardHost、产品函数及隔离jailed存储；全部外部transport是明确fixture，页面渲染和测试小控件沿用既有harness替换。没有真实UI、GPT/M3、邮箱或系统Calendar动作。不能用这些结果替代新SDK Shell实测、Calendar CRUD或App Hub准入，不宣告READY/UI_PARITY_PASS。

只验证上述明确样本与新bound恢复，不宣称任意自然语言解析完备，也未验证旧无requested_range记录自动迁移。

A2只写本拥有目录，无产品/Host/锁/共享文档修改，无Git操作，不读private/生产/Secret，不新增付费调用。Root唯一写产品。测试进程均已退出。

## 复现

本目录run.py，source指向rc20-main-r1/readable-bundle/main.splash，使用上述SHA和summary的Host路径，out为本目录下不存在的新目录。主13组同run.py的CASES；新增两类使用--probe-template singlepoint_flexible.splash以及singlepoint_wrong_day / unrelated_negated_flexible。

每组都有原始probe、runtime.log、report、隔离state；恢复组另有restart-runtime.log、restart-report.json和恢复bundle。
