# A4 完整 Shell 测试与独立 Host 构建

**完整默认 dev profile Shell：558 PASS / 0 FAIL / 0 ignored / 0 filtered。独立空 target Host locked release：PASS。** 原失败记录全部保留，rc27 与现运行 Host 未替换。

| 实际运行 | 通过 | 失败 | ignored | filtered | 说明 |
|---|---:|---:|---:|---:|---|
| 首轮完整 release | 552 | 6 | 0 | 0 | 保留原日志；两项受 A4 TMPDIR 空格影响 |
| 完整 release / 修正 TMPDIR | 554 | 4 | 0 | 0 | 生产与测试源码均未再改；两项沙箱复核通过 |
| 完整默认 dev / 两个测试修复 | 558 | 0 | 0 | 0 | 全部用例串行，未筛选，不启用 --ignored |

默认测试命令去掉 --release，使用 Cargo 默认 dev/test 配置；其余为 --lib --locked --offline -j 2 -p octosense-shell --no-default-features --features app-hub -- --test-threads=1。默认 dev 的完整编译与测试墙钟耗时 1296.06 秒，包含 Root 请求的 283.85 秒协调暂停；不得把它当作无负载构建性能基准。暂停与恢复只针对核实的本轮 cargo/rustc 进程组，没有据此认定 Memory 波动根因。三项 release 失败依赖开发构建行为；剩余搜索测试是本地中文化后标签与查询不一致。测试修复只涉及 launcher 命名空间两行和 menu 查询四行，模块前后生产字节均不变。早期 5 项 PASS 不替代本次完整计数。

已只读核实 fixture、沙箱探针、FakeHost/FakeService/RecordingRelay 和 secrets::select_backend：cfg(test) 强制文件后端；HOME/MAKEPAD_HOME/OCTOSENSE_HOME/TMPDIR 指向独立目录，环境不继承账号凭据。kernel cfg 未开启，真实 kernel 测试未编译；默认不存在 ignored 用例，不能宣称执行了未编译的外部链。没有发信、真实模型请求或系统日历操作。

Host 命令为 cargo build --release --locked --offline -j 2 -p octosense --bin octosense --no-default-features --features app-hub。全新空 target `.local-state/cold-host-target`，使用原冻结 SDK + 已下载 Cargo 源码缓存，**没有使用旧 target**；耗时 1476.88 秒（24.61 分）。构建成功后 target 实际分配 912363520 bytes（0.850 GiB）。可执行文件为 x86_64 Mach-O，SHA c81c9011fc66127ee23022d62986c8edb87c4e642f70f2b5f251c085077b8525。只生成构建可执行文件，没有新 .app/ZIP，没有 GUI/live，未安装或替换产品 Host。

启动可用 13.833 GiB；运行监测最低 12.921 GiB；结束可用 12.875 GiB；6 GiB reserve / 全盘净增 4 GiB 守卫均未触发。最后默认测试完成后可用 11.026 GiB。监测最低是约 2 秒采样值，不冒充瞬时峰值；全盘差额受其他任务影响，不等同于本轮 target 分配。没有删除现有 target。

**身份边界必须保留：** Cold Host 的输入是旧锁 `78a5eef0b1af8eb82cd28e464d5681e6e3b0685e63719207d1a77e4ffdd706d6` / OctoSense tree `0f832030637de18258e191effa2e8b1d000df5a6e90a7223d82c3fde52a88e6e`。Root 主线和本轮测试副本对应合并新锁 `f487df0cc37049fe09e92a66bad348b7ce6b42c834313967ca33f49c3442f715` / 完整树 `24b324a2473880afadeee8f6bbefce21fe5ce213bbe12b22d6572eadb19687bf`。两者生产源码逐字节等价，只差 cfg(test) 内上述两处修复；它们仍是不同源码身份，不能把本次 cold build 标为新锁构建。原 launcher-only lock proposal 与日志均保留。新版 Host 的 SHA 与已交付 Host 不相同，不能继承旧 GUI/live 验收。

构建与测试后原冻结 SDK 12,000 文件仍匹配旧冻结身份；隔离测试副本归一化四条定位同一依赖的 .sources 链接后，完整 2,309 文件树匹配新树。两处 overlay、Cargo.lock 及 Root 新锁已实核。Root 当前 HEAD 为 438943d11be8bb1839a90d918103054a12d2a113；本 A4 未 commit/push/Tag。

现运行 Host SHA 仍 1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3；rc27 ZIP SHA 仍 a5db3565f0b9daf3bc446792c9210ec629107863417fb88d18b220532d18cb8f。接收机 A/B、OS 重启、Mail/Calendar/回复全链仍需独立实测，本轮不补写其成功。

详见 FULL_AND_CLEAN_SUMMARY.json、shell-full-default-dev-combined-test-only-fixes.log/.json、host-clean-empty-target.log/.json、COLD_HOST_NATIVE_INSPECTION.json、FULL_RELEASE_FAILURE_CLASSIFICATION.json、COMBINED_TEST_ONLY_INTEGRATION.json。严格 fresh checkout + fresh SDK + fresh Cargo home 的旧 clean-room 流程未执行，不与本次空 target 构建混称。
