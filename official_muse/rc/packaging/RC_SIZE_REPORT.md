# RC 体积与 SDK 可恢复性

本轮 A4 保留历史、旧证据及既有构建缓存；后续按明确授权只删除 A4 自己的重复 archive restore 探针。统计区分源码、可恢复 SDK、Git 历史、App Hub bundle 和最终评审包，不把它们相加或互相替代。

## 接手时的现场基线

时间：2026-10-04 22:00:32 +08:00；HEAD `5bcac1fdd79eff459f9c817671fea7ac38c2eef1`。完整数值、分配空间与逐顶层分组见 `SIZE_REPORT_BEFORE.json`。

| 口径 | 逻辑 bytes | 说明 |
| --- | ---: | --- |
| RC 工作区，排除 .git 指针 | 24,457,500 | 包含当时并行产物，不含尚未恢复的 SDK |
| Git tracked 源码现场 | 17,373,161 | 757 个索引文件，以现场字节计算 |
| shared .git | 2,838,274,990 | 所有 worktree 共用的历史/对象，A4 不拥有它 |
| App Hub 脚本 bundle | 660,719 | 当时 5 个文件，旧截图及占位 Privacy 尚在 |
| 最终 review packet | 未提供 | 不能写为 0 或已经生成 |

## Git 源码历史比较

只用 `git ls-tree` 元数据计算，没有读取历史账号文件内容：

- 历史 SDK 内置提交 `be552c1e3d41602370a8a9bcc64c9f1bcab8f3a2`：12,693 个 blob，739,626,527 bytes。
- 本轮原公开基线 `d8a2989da8bb619139081ec96ddd05452eb364cb`：755 个 blob，17,367,660 bytes。
- A4 接手的 HEAD：757 个 blob，17,374,883 bytes。

这说明 SDK 从 tracked 源码分离的瘦身发生在接手前。不能把历史差异记成本轮 A4 删除；现场源码字节与提交字节也可能不同。详情见 `GIT_SOURCE_SIZE_HISTORY.json`。

## 本轮恢复产生的增长

RC 根的 ignored `vendor/` 实测有 12,000 个文件、4 个相对链接，逻辑 621,311,483 bytes，分配空间 650,657,792 bytes。它是可恢复的构建输入，不属于 App Hub 脚本 bundle。

初次恢复时，新模型日志补丁使 OctoSense 本地 overlay tree 变为 `406dee1ec74a6cf9b85cef41700ffe081aabf9bed4f7f67e77b2484afa686780`；官方固定提交仍是 `7f962547cd8035ed2bb05962cf7824d8aa33e3a3`。此阶段 lock 的实核结果见 `SDK_RESTORE_RESULT.json`，bootstrap 返回 `SDK_VERIFIED / 12000 files`。后续总控新增 storage `sha256_file`，Makepad tree 变为 `8cb0515697f48a35866d835486ec0786bec61dc9aa8a45eccd3a587e3ac46ea1`，该轮输入与新验证另见 `STORAGE_DELTA_INPUTS.json` / `STORAGE_DELTA_BUILD_RESULTS.json`，不能把初次记录当作新 SDK 结果。

为了验证真正的解包恢复路径，本目录 `.local-state/archive-restore-probe/` 使用现有精确官方 archive cache 做一次隔离 bootstrap。结果只有 `SDK_ARCHIVE_RESTORE_RESULT.json` 实际存在且 exit code 为 0 后才算通过。该诊断副本不打入源码交付、App Hub bundle 或 Intel ZIP。bootstrap 仅对本次新解出的文件应用 lock 声明的排除项，没有删除此前工作区或旧缓存文件。

该恢复探针实际通过后，按总控的单独授权检查五个 tree/count、五份保留 archive 的存在及 SHA、`lsof` 无占用，删除了探针的重复文件，逻辑 624,861,900 bytes。`PROBE_REMOVAL_PROOF.json` 保留逐项证据；原 archive、license、恢复日志、根 vendor、旧 app 与共享 target 未删除。释放的逻辑 bytes 不是承诺等量的实际磁盘净增。

Host 构建复用总控准许且无占用的旧 Cargo target，不删除旧 target；新增资源完整 `.app` 留在本目录 ignored `.local-state/`。测试日志、诊断 SDK、编译缓存与历史模型不直接塞入 App Hub bundle。

源码交付应从总控最终 commit 的 tracked 文件导出；当前未提交集成状态不能直接用旧 HEAD 的 archive 代替。Intel 运行 ZIP 应明确选择最终 app、脚本 payload、所需模型、教程与许可证，不能压缩整个 RC worktree 或 shared .git。

## 后续快照

本轮集成持续进行。最终 `SIZE_REPORT_AFTER.json` 必须标明采集时间与当时 HEAD，并说明并行证据/恢复 SDK/Host 造成的增长；不能把工作区总变化全部归属为 A4。最终 review packet 仍由总控提供路径及大小，再补入最终报告。

大小合规与 SDK 可恢复不代表业务链、冷启动、MiniMax 或正式 App Hub 原版准入已经通过。

## 存储暖构建结束时的快照

`SIZE_REPORT_AFTER.json` / `PUBLIC_PACKAGE_AUDIT_AFTER.json` 实际采集于 2026-10-05 00:20:40 +08，HEAD `aacc8d17cc25724bacaebb5260ff13b628655db7`，不是总控最终生产冻结。现场 tracked 源码 766 files、17,423,129 bytes；RC 工作区包含恢复 SDK、三轮运行 app 和并行 fixture/evidence，合计 1,535,241,527 bytes；shared Git 2,839,249,491 bytes。不能把工作区增长当成 tracked 源码变大，也不能把已移出的旧 SDK 当作 A4 删除。

现场 canonical App Hub bundle 5 files、660,719 bytes，版本字段 `0.3.26-rc5`；它不等于总控正在验证的全部临时 compact/fixture 输入，也不代表最终 packet。公开 overlay 核对零不匹配，lock 仍为 fcec896f...；Privacy URL 仍是 placeholder，最终 packet 未提供。

本轮新 storage card-host app 88,898,749 逻辑 bytes（83 files），Host app 117,778,172 bytes（167 files）；`STORAGE_DELIVERY_AUDIT.json` 记录两包签后 SHA、资源及链接库。两包只依赖系统动态库，ad hoc 严格验签实际成功；未内嵌最终 Muse bundle，未由 A4 启动业务 GUI。它们不是已生成的新 Intel ZIP，运行 ZIP 仍需总控绑定最终 payload、模型、教程和许可。

本阶段 df 可用约 3.9 GiB，新目录 clean-room 建议空间仍未达到。后续 frame delta 需先保留当前包再增量重建；缓存释放与清洁构建依总控下一阶段通知，不擅自删除共享 target。

## 授权缓存清理的现场容量

本轮仅删除两个旧可再生Rust target，exact paths及逐步结果在CACHE_REMOVAL_PROOF_R2.json。du分配合计2,794,582,016 bytes；磁盘可用从3,272,814,592升至5,915,557,888 bytes（3.05→5.51GiB），净增2,642,743,296 bytes。现场有并发活动，du与净可用增量不等同；此清理不代表最终包缩小或Git历史压缩。原before/after源码体积快照保留对应时点。没有删source/archive/vendor/CargoHome/runtime或私有资料，clean-room仍未运行，建议8GiB/优先12GiB是规划值。
