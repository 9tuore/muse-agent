# Muse RC 基线 · 0.3.26-rc1

开始：2026-10-04 21:51:29，北京时间。硬截止：2026-10-05 00:51:29。成功条件为原T01–T20全PASS，不沿用旧18/20门槛。最终关键测试统一source/bundle/host/hub；途中修复必须换RC并重跑受影响检查及核心链。

公开基线d8a2989/0.3.25，原开发起点3c2d69a。独立分支codex/muse-rc-finalization，基础SDK保持固定官方commit+bootstrap+完整overlay；完整旧开发历史和未跟踪失败保留。旧独立安装及生产资料不改，Secret不导出或写入日志。

源入口official_muse/app/source/main.splash；bundle为其compact签名成品。main/source及共享模块仅总控写；三名真实已有聊天分别写rc/core_chain、rc/memory_model、rc/packaging。不调用子智能体，不创建新聊天。审批/权限/读回/防重复保留，无新产品功能。

## 当前二十项

PASS：T01/T06/T11/T16/T19。
PARTIAL：T02/T03/T04/T05/T07/T08/T09/T10/T12/T13/T14/T15/T20。
BLOCKED：T17/T18。

## 旧证据与重跑边界

- 0.3.20的10冷启动+5重开：支持旧修复，不计RC通过，必须同RC重新测试。
- 0.3.25的一次Shell重启、七文件SHA、133项fixture：原版本节点支持；RC启动与受影响fixture重跑。
- 真实日历创建0.3.23、改期/清理0.3.25，历史邮件发送0.3.18：不能拼接T18，完整同RC重跑。
- Memory本地存储25项及历史模型召回：保留原范围；同RC任务后更正/遗忘/跨会话召回与归属隔离重跑。
- Host/VM/Widget已有锁定离线测试可作未改代码支持，源码/二进制SHA必须一致。SDK恢复/metadata/Hub build/Calendar check按瘦身要求核验。
- 正式privacy/publisher、同RC截图/视频、第二模型仍有缺项；未经核实不计PASS。

## 现场分类

产品源码：可读Splash、bundle及模块。测试：既有fixture与本轮rc子目录。文档：根RC报告/交接。Evidence：脱敏摘要与保留原失败。Build/cache：忽略目录。私人运行资料：只在权限受限隔离clone。Secret：不读取、不打印、不纳入Git。历史交付：旧桌面包保留原绑定，不混入成品commit。

固定SDK/宿主/Hub哈希和责任范围详见official_muse/rc/baseline.json。Calendar Host是锁定本地扩展，不冒充官方原版准入。
