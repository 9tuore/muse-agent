# 包装交接

在既有 package_lean_portable.py 调用加 --solid-source。源码仍完整保留：桌面展开，ZIP 内 tar.xz 加逐文件清单；产品运行不用先展开源码。ZIP extraction 后 tar 逐文件还原，校验全 stage 一致。

Python 3.9.6 合成验证两模式通过；系统 tar 独立还原通过；Unicode、exec、symlink、CRC、SHA、mode、allowlist 及五类故障拒绝通过，见 RESULT.json。真实大包和原生启动没有执行，不保证最终小于 500MB，不改产品验收状态。

Root 冻结含修复的 commit 后继续实包验签、资源和启动检查，保留现有失败。临时资料在本目录 gitignored .local-state，未删除共享数据或旧包。文档写入的编码异常保留独立记录，已用补丁保存文档。
