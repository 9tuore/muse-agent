# 按签名版本导出的薄源码与材料方案

当前PREPARED，未导出新ZIP。总控已冻结签名应用0.3.26-rc9，applicationCommit为`1c9f3b46e7aac0ee17be385de64c97564651152f`；mirror为`official_muse/app/build/ui-memory-20261003/rc9-final-startup-r1/mirror`。等待最终sourceHEAD与更新后的SOURCE_MANIFEST，并在获准导出时重新检查容量。版本只从指定application manifest读取。现有087桌面ZIP/sha保持，完整宿主包600MiB门禁不改。

小包仅含已签名App Hub mirror/bundle/pack、完整冻结公开Git源码、离线HTML教程、身份与逐文件校验清单。不含Host/Card/Hub二进制、启动器、模型、账号、vendor、CargoHome或target；不是独立可运行包。旧087入口仍运行rc5，不改其内部资源或签名；本次应用的接收机运行入口和包含Calendar桥修复的新Host都是明确缺项。

`package_thin_source.py`只流式写单个ZIP，不生成解压源码stage、不新编译runtime。参数为`--commit`最终源码快照、`--application-commit`签名应用提交、`--mirror`公开签名镜像。版本从application manifest读取。`--check-only`只核验，不写归档。

生成前必须验证catalog来源/manifest、Git/mirror/pack六文件逐bytes、公钥签名以及SOURCE_MANIFEST对最终Git文件集合和SHA；过时清单拒绝。直接从git archive写入明确的普通文件列表，逐blob/长度/模式比较；ZIP完成后全部读回SHA/权限/集合，再改名为最终ZIP，失败的incomplete输出保留。

薄包单独空间检查：已知源码+mirror未压缩字节预算、额外4MiB元数据和64MiB保留量；每文件写入前继续检查保留量。此阈值只用于无Host、无stage的流式材料导出，不降低完整包600MiB检查；不能保证抵御其他任务并发写满磁盘。旧087源码约29.5MB，当前mirror约15MB是体积参考，最终HEAD文件数量/输出体积待实际生成确认。

主线现为PARTIAL：rc9仅将既有用户时间完整性询问置于payload验证前，再更新版本。A2报告15变体53/53隔离fixture通过；rc9新70次启动、2小时、真实Memory/Goal与两模型D05重测仍未完成，不能标PASS。历史rc8的70启动、M3八题8PASS、M2.7七PASS/D05FAIL及E04两模型保留字段成功只对应a80候选，不计rc9通过；M2.7 unknown不当作strong，完整T17尚缺。rc7 E04真实失败、rc6冷启动失败与rc6/rc7 synthetic soak的ENOSPC写入中断均保留。Host938/旧SDK3f未含Calendar92b1修复；严格clean build仍BLOCKED_CAPACITY，新Host、Calendar/T18、接收双Mac/OS/电脑重启和正式App Hub仍缺。A4无GUI/账号/模型动作。
