# rc6 薄源码与签名材料方案

当前PREPARED，未导出新ZIP。等待总控冻结最终sourceHEAD与更新后的SOURCE_MANIFEST。现有087桌面ZIP/sha保持，完整宿主包600MiB门禁不改。

小包仅含已签名App Hub mirror/bundle/pack、完整冻结公开Git源码、离线HTML教程、身份与逐文件校验清单。不含Host/Card/Hub二进制、启动器、模型、账号、vendor、CargoHome或target；不是独立可运行包。旧087入口仍运行rc5，不改其内部资源或签名；rc6接收机运行入口和包含Calendar桥修复的新Host都是明确缺项。

`package_thin_source.py`只流式写单个ZIP，不生成解压源码stage、不新编译runtime。参数为`--commit`最终源码快照、`--application-commit`签名应用提交、`--mirror`公开签名镜像。版本从application manifest读取。`--check-only`只核验，不写归档。

生成前必须验证catalog来源/manifest、Git/mirror/pack六文件逐bytes、公钥签名以及SOURCE_MANIFEST对最终Git文件集合和SHA；过时清单拒绝。直接从git archive写入明确的普通文件列表，逐blob/长度/模式比较；ZIP完成后全部读回SHA/权限/集合，再改名为最终ZIP，失败的incomplete输出保留。

薄包单独空间检查：已知源码+mirror未压缩字节预算、额外4MiB元数据和64MiB保留量；每文件写入前继续检查保留量。此阈值只用于无Host、无stage的流式材料导出，不降低完整包600MiB检查；不能保证抵御其他任务并发写满磁盘。旧087源码约29.5MB，当前mirror约15MB是体积参考，最终HEAD文件数量/输出体积待实际生成确认。

主线现为PARTIAL：协调任务报告finalb9 M3/更正/遗忘/Goal/读回/首次Shell重启通过；rc6 cold2源码准备124ms失败保留，两小时与第二模型观察未以本材料代报。Host938/旧SDK3f不是Calendar92b1/新SDKda修复构建。A4没有GUI/账号/模型动作；严格clean build仍BLOCKED_CAPACITY。
