# 启动预算只读诊断交接

状态：READ_ONLY_DIAGNOSIS_COMPLETE；没有实施或验证启动修复。详情见 [evidence/startup/diagnosis.json](evidence/startup/diagnosis.json)。

输入固定为 `e2b455ca63ede03ab8c85e88d8eb9663ddff472386920ef7e4f29f9e262fe750`，426,497 字节/7,418 行。实际读到的 rc1 日志包含 `script time budget exceeded` 和 `view=false`，不能称启动成功。主对话提供的 Host8412 成功未在本任务复跑。

当前依赖从 OctoSense Cargo.toml 的本地 patch 落到 `phase2-host/makepad-splash-budget`。`widgets/src/widget_async.rs:456` 设置软/硬 64ms；`widgets/src/splash.rs:316-318` 在同一入口对完整源码求值。`platform/script/src/vm.rs:1603` 的 Rust 增量接口首次解析全量、随后解析增量，每次从 opcode 0 重执行；没有证据说明它可由卡片脚本调用。`parser.rs:4096` 的 `use x.*` 导入已有命名空间，不等于文件模块加载。

5 次集中读搜内没有确认到脚本可用的模块加载/延迟定义 API；这不是对所有依赖的不存在证明。标准库猜测路径 `platform/script_std` 和 `platform/script/src/std.rs` 不存在，其注册入口未在限定范围内完成核对。因此不建议依据假设接口拆分模块。

最小候选建议：从固定源码生成单独压缩候选，只移除字符串外行首 ASCII 缩进与普通注释，保留每个换行、文档注释 `/**...*/`、字面量和 token 间必要分隔。`tokenizer.rs:223` 证明换行参与语句边界，`:269` 证明文档注释参与元数据；不能直接删全部注释或把源码拼成一行。原始缩进统计 56,688 字节，注释粗估 4,306 字节、空白行原始统计 267 字节，存在重叠/字面量影响，均不等于实际安全可删量。压缩保持 token/opcode 数量，不能保证能恢复 64ms 余量；延后函数调用也不延后函数体首次词法/语法解析。

本次只写启动证据和本交接；未修改 main、Memory、Host 或预算，未编译、启动服务、重测、提交或 push。没有用单次采样声称定位到唯一耗时点。下一步实现及启动验收由主对话决定。
