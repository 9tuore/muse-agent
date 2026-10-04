# Native schema target cache review

明确结论：overnight-native-schema/target是**可重建Cargo cache**；只删target不会删除已有测试源码、输入生成器或验收报告，也不会破坏现有cargo run测试入口。A3未删除、未构建、未执行测试，交Root决定与授权实际清理。

只读盘点396个regular files，逻辑51,979,317bytes，唯一inode分配50253824bytes（du49,076KiB，约47.9MiB）；全部在Cargo debug产物/metadata/incremental/build/fingerprint结构内，无symlink。所有JSON均Cargo元数据，未发现唯一失败日志或不可重建二进制；三个build-script stderr为空。lsof exit1且stdout/stderr均为空，检查时无占用。

Cargo.toml/lock/src/main.rs/src/production_schema.rs/SOURCE_BINDING.json/REPORT.json均在target外。main.rs通过path直接引入SDK schema.rs，该文件目前SHA与SOURCE_BINDING匹配，保留副本也逐字一致。306/306结果报告在target外，不会被cache删除。manifest、lock、源码、SDK及全部旧证据应保留。

唯一现有复现入口是PUBLIC_TESTS_README中的cargo run --locked --offline；Cargo会先构建再执行。未发现项目现有Python/Shell脚本直接硬编码target内驱动二进制。若有人手动执行旧target/debug/muse-contract-schema-unit，需要先cargo build或改用现有cargo run。cargo/rustc命令存在，lock的14个registry依赖source/archive目前全部缓存，无须为了此cache重新下载。没有在低磁盘时实际构建，不能把检查称为rebuild PASS。/tmp corpus缺失时可用保留生成器重建。

仅释放约48MiB仍达不到Root声明的600MiB完整新Host门禁，不建议改变门禁；也不能用这个小驱动cache冒充可增量复用的Host target。

Root补充M2.7同应用11调用：9项成功，D05 waiting_user，D07失败原因UNKNOWN，T17不PASS。此为Controller报告，A3本轮未读取其原始结果，不能升级为独立验证。
