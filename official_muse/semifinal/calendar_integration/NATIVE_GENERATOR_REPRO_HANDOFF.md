# NIGHT-002 生成器修复交接

只修改 prepare_native_prototype.py，新增对应小测试和报告；原型主文件、共享SDK、冻结patch/receipt不动。

修复：复制Cargo.toml与src下实际存在的全部.rs文件，当前包含lib.rs/history.rs，缺失lib.rs拒绝。新增必填--output-dir：必须是calendar_integration下尚不存在的直接子目录，已有目录拒绝。stage、SDK/Hub补丁、ENTRY、RESULT均写入该新目录，禁止覆盖根目录冻结产物。

实际验证：Python小测试3/3通过（真实模块、嵌套/缺失模块、已有输出及回执保护）。以旧回执原始SDK/Hub为只读输入，官方生成器--no-lock及--check --no-lock均exit0；新生成目录native-prototype-regenerated-night002-r2，三模块文件SHA均与当前提案一致。

冻结序列SDK→readonly-schema→中文label→History r2→Scroll在专项副本逐项零fuzz检查/应用exit0，最终三文件字节一致。Scroll补丁须在apps/muse-native-prototype执行；首轮误用SDK根目录检查exit1，已在新副本纠正并记录。r1历史保留；六个既有补丁与原回执SHA一致，根目录既有patch/RESULT/ENTRY重跑前后SHA不变。详情见NATIVE_GENERATOR_REPRO_RESULT.json和两个CHECK.log。首轮生成和失败副本保留。

下次调用必须给新的输出目录：python3 prepare_native_prototype.py --sdk <未注册原型的原始SDK> --hub <原始Hub> --output-dir <calendar_integration绝对路径>/native-prototype-regenerated-next

本任务未Cargo/GUI，未写共享SDK。中央报告Desktop r3 exit0（8008ec14）及History r2 parser5/5；不是本任务测试。当前待命。
