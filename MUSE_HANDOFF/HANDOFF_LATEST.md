# 2026-10-06 23:10 Muse rc10 接续

代码已在现有最终参赛分支收口。详见 official_muse/rc/final-contest-20261006-r1/FINAL_REPORT.md。正常静止重启六文件和外部动作一致；真实改期、回信及新空白对话记忆有证据。完整同一候选受model日预算阻塞，删除后回执仍有脚本预算问题，状态PARTIAL。未修改旧独立安装包与生产资料。

# Handoff

## Task

天猫离线模型打包与GOSIM/天猫中文使用教程。Root；codex/tmall-submission，核心rc51/6b46c3c8不变。

## Result

交付包/入门教程通过范围核验；产品总体PARTIAL。最终天猫ZIP以桌面Muse-Tmall-Delivery.json为准。GOSIM492,370,211字节，旧内载荷不变。

## Changed

原生入口复用：Qwen2.5-0.5B Q4_0/llama.cpp自动本机配置、整包验签、生命周期/正常安装；精确allowlist与500MB硬门槛。docs使用教程和天猫md/html；GOSIM外层加教程。

## Tests

真实AppHub安装6 SHA一致；4次官方model.complete/usage，重开自然两题通过。短格式1/2、旧Qwen3 0/2及驱动首次竞争失败保留。已有合成Provider配置字节保持；22模型文件锁、ZIP全还原/验签/五入口检查PASS，最终身份见记录。

## Commit

教程10784ccf；原生模型781feb7a；后续包装/远端回执见桌面交付记录。只普通同步包装分支，main/Tag不动。

## Remaining

基本模型有限，原冷启动、第二strong、同最终外部整链、接收Mac等未补证。无付费或外部写入。旧76MB包/492MB旧ZIP保留；旧安装/生产/dirty baseline保护。

## 23:18 交付追加

ZIP 为489,595,070字节（489.60 MB），SHA256：000b2815c6072d2b8033bea42ddc608b91c307a38f11bc53299b67f8391efbd8。814文件独立解压一致，基础离线模型与宿主文件一致，五项入口/失败保护测试通过。没有复制私人账号或运行数据库。

本人追加授权后，仅隔离测试profile的官方model ledger日token限制调整为200,000，原day/apps调用计数和100,211 token使用记录保留；未改脚本执行预算。此配置不会消除已有业务缺项，不改变PARTIAL结论。
