# A4 公开维护材料入口

本清单是交总控审阅的最小维护材料集合。它不是可直接运行的 Intel 应用包，也不表示最终 RC 或 App Hub 已发布。

当前新方案见`THIN_SOURCE_DELIVERY_PLAN.md`：`package_thin_source.py`按application manifest版本导出签名mirror和冻结公开源码，不含Host、启动器或模型。离线教程为`thin_source_tutorial.html`。待交付签名应用为0.3.26-rc8 / `a80bd019db7581511b3891bcc3892548f767a42d`，最终sourceHEAD与SOURCE_MANIFEST仍待总控固定，不生成归档。rc7 E04真实失败保留；rc8的86项fixture支持不代替最终模型复测、70启动或2小时验收。旧087桌面运行包保留，新版本接收机入口和包含Calendar92b1修复的新Host仍缺，PARTIAL不变；完整运行包600MiB门禁保持。

`PUBLIC_MAINTENANCE_ALLOWLIST.json` 逐个列出允许复制的文件、长度和 SHA256。仅复制 `files` 中的精确路径；不递归复制整个 packaging 目录。文件修改后先重新核对清单，不套用旧 SHA。

## 源码复现入口

`clean_room.py` 和 `package_clean_host.py` 用于最终已提交源码的新目录构建；`inspect_packaging.py` 用于源码/SDK与体积快照。具体要求和命令见 `CLEAN_ROOM_PLAN.md`。总控冻结的`74a4bfca6880806e7d6764888fc8583714c742cb`已实际在全新目录运行，fresh SDK恢复及12,000文件verify通过；依赖获取期间按总控V10修补指令受控停止，未进入Host/card/Hub编译，完整clean-build未通过。`CLEAN_ROOM_R1_FINAL_AUDIT.json`绑定真实阶段、SIGINT退出和保留的原FAIL报告。等待新的最终提交后另建严格新环境，不把74a4阶段证据转成V10 PASS。

运行这套维护脚本需要最终项目源码、已安装的 Python/Rust/Cargo/Xcode Command Line Tools 及官方依赖下载。它们不是接收方双击启动器。双机 Intel 应用包仍需由总控绑定最终 bundle、Host、模型、启动器和离线 HTML 教程。

## 已有证据的范围

`A4_HANDOFF.md` 说明最新 4 KiB SDK 的两个 Intel app。`CHUNK_*` 绑定实际测试、构建、签后 SHA 和资源；这是使用旧编译缓存的构建证据。报告中的本机路径和原始日志 SHA 用于定位本地证据，原始日志不进入本公开集合。

`MODEL_TEST_RESULTS.json` 保留原整包失败结果；Calendar pure 与源准备 pure 测试分别列出，不表示真实邮箱、Calendar 或付费模型全链通过。SDK/体积报告保留各自时点，最终冻结源码要产生新的验证记录。

App Hub 契约/状态和 Calendar Issue/PR 文件是核对材料或草稿。最终 Privacy URL、身份、截图、packet 与发布许可仍由总控收口；此集合没有发送或公开发布动作。

## 保留在本机的内容

原始日志、旧失败细节、临时源码/patch、诊断缓存脚本、重复 main/bundle、源码归档缓存、vendor、CargoHome、运行 app、模型及私人资料都不在公开 allowlist 中。已有原件继续保留；本清单不授权删除它们。最终应用包有另一份交付清单，不能从本目录整体打包代替。

历史069d R2支持证据：fresh SDK验证及native依赖下载通过，Host构建在低磁盘空间下按总控要求受控停止，未产生成品包；CLEAN_ROOM_R2_FINAL_AUDIT.json保留精确输入/命令/退出/清理和欠项。不把该历史阶段当当前候选的最终clean-build或跨Mac运行通过。
