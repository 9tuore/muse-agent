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
