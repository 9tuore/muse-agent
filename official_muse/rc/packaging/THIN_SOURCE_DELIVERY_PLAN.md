# 按签名版本导出的薄源码与材料方案

当前PREPARED，未导出新ZIP。总控已冻结签名应用0.3.26-rc8，applicationCommit为`a80bd019db7581511b3891bcc3892548f767a42d`；mirror为`official_muse/app/build/ui-memory-20261003/rc8-final-a80-startup-r1/mirror`。等待最终sourceHEAD与更新后的SOURCE_MANIFEST，并在获准导出时重新检查容量。版本只从指定application manifest读取。现有087桌面ZIP/sha保持，完整宿主包600MiB门禁不改。

小包仅含已签名App Hub mirror/bundle/pack、完整冻结公开Git源码、离线HTML教程、身份与逐文件校验清单。不含Host/Card/Hub二进制、启动器、模型、账号、vendor、CargoHome或target；不是独立可运行包。旧087入口仍运行rc5，不改其内部资源或签名；本次应用的接收机运行入口和包含Calendar桥修复的新Host都是明确缺项。

`package_thin_source.py`只流式写单个ZIP，不生成解压源码stage、不新编译runtime。参数为`--commit`最终源码快照、`--application-commit`签名应用提交、`--mirror`公开签名镜像。版本从application manifest读取。`--check-only`只核验，不写归档。

生成前必须验证catalog来源/manifest、Git/mirror/pack六文件逐bytes、公钥签名以及SOURCE_MANIFEST对最终Git文件集合和SHA；过时清单拒绝。直接从git archive写入明确的普通文件列表，逐blob/长度/模式比较；ZIP完成后全部读回SHA/权限/集合，再改名为最终ZIP，失败的incomplete输出保留。

薄包单独空间检查：已知源码+mirror未压缩字节预算、额外4MiB元数据和64MiB保留量；每文件写入前继续检查保留量。此阈值只用于无Host、无stage的流式材料导出，不降低完整包600MiB检查；不能保证抵御其他任务并发写满磁盘。旧087源码约29.5MB，当前mirror约15MB是体积参考，最终HEAD文件数量/输出体积待实际生成确认。

主线现为PARTIAL：rc7 E04真实模型擅改subject失败保留；rc8只做未请求字段保留的最小修复，86项隔离fixture由总控报告通过，最终真实模型复测仍待。rc8新70次启动与2小时观察尚在进行，不能标全门槛通过。历史b9/rc6 cold2准备124ms失败和rc6/rc7 synthetic soak报告写入ENOSPC中断均保留，不记PASS；旧V15的7200.3秒/240样本支持仅对应旧候选。Host938/旧SDK3f不是Calendar92b1/新SDKda修复构建。A4没有GUI/账号/模型动作；严格clean build仍BLOCKED_CAPACITY，新Host/接收双Mac运行入口/电脑重启仍是缺项。
