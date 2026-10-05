# 按签名版本导出的薄源码与材料方案

当前PREPARED，未导出新ZIP。总控已冻结签名应用0.3.26-rc10，applicationCommit为`6fd5b54beeba7cc9892916c3de7f01106ab8a158`；mirror为`official_muse/app/build/ui-memory-20261003/rc10-memory-ui-r1/mirror`。可读源码SHA256 `a19622e0977b3f988531a1d7db743bc9ef4cd6973fa75bbcdc5dec07d6823cc5`，compact SHA256 `7cdfc751ca3438d453ad28918b30ee93bc5b86091faa56a30864caa5ed1e6cd0`；A4已逐bytes核对六文件/Git/mirror/pack及catalog、公钥签名。等待最终source S/F与更新后的SOURCE_MANIFEST，并在获准导出时重新检查容量。版本仍只从指定application manifest读取。现有087桌面ZIP/sha保护，完整宿主包600MiB门禁不改。

小包仅含已签名App Hub mirror/bundle/pack、完整冻结公开Git源码、离线HTML教程、身份与逐文件校验清单。不含Host/Card/Hub二进制、启动器、模型、账号、vendor、CargoHome或target；不是独立可运行包。旧087入口仍运行rc5，不改其内部资源或签名；本次应用的接收机运行入口和包含Calendar桥修复的新Host都是明确缺项。

`package_thin_source.py`只流式写单个ZIP，不生成解压源码stage、不新编译runtime。参数为`--commit`最终源码快照、`--application-commit`签名应用提交、`--mirror`公开签名镜像。版本从application manifest读取。`--check-only`只核验，不写归档。

生成前必须验证catalog来源/manifest、Git/mirror/pack六文件逐bytes、公钥签名以及SOURCE_MANIFEST对最终Git文件集合和SHA；过时清单拒绝。直接从git archive写入明确的普通文件列表，逐blob/长度/模式比较；ZIP完成后全部读回SHA/权限/集合，再改名为最终ZIP，失败的incomplete输出保留。

薄包单独空间检查：已知源码+mirror未压缩字节预算、额外4MiB元数据和64MiB保留量；每文件写入前继续检查保留量。此阈值只用于无Host、无stage的流式材料导出，不降低完整包600MiB检查；不能保证抵御其他任务并发写满磁盘。旧087源码约29.5MB，当前mirror约15MB是体积参考，最终HEAD文件数量/输出体积待实际生成确认。

主线现为PARTIAL：Root真实UI两个单独保存点击复现rc9 Memory更正回退，rc10最小修复已由真实UI限定摘要支持：更正保持新值、第二次保存不改Memory/Activity、首次Shell重启10SHA与ledger保持。见`official_muse/rc/startup/RC10_MEMORY_CORRECTION_UI_SUMMARY.json`。不将其扩写为电脑重启或模型/外部服务通过；新rc10 70次启动、7200秒和full28仍运行。rc9的70启动/100次应用重开/D05两模型及此前Memory/Goal入口支持仅对应1c9，后来的真实双保存失败保留；rc8及更早支持/失败也保留且不计rc10通过。M2.7 unknown不当作strong或完整T17。Host938/旧SDK3f未含源码SDKda的Calendar92b1修复；严格clean build仍BLOCKED_CAPACITY，新Host、Calendar/T18、接收双Mac/OS/电脑重启和正式Hub仍缺。A4无GUI/账号/model/编译/Git写操作，未修改SOURCE_MANIFEST、未导出。
