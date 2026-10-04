# SDK 锁与完整 overlay 核对

现场基线 `5bcac1fd` / `0.3.26-rc1`，时间见 `PUBLIC_PACKAGE_AUDIT.json`。

| SDK | 固定官方 commit | 本地普通文件 | 声明内部链接 | 锁定恢复 files |
| --- | --- | ---: | ---: | ---: |
| Makepad | `bf318136a375c4d1fb7ee10e13e27336b6d98744` | 35 | 0 | 8724 |
| OctoSense | `7f962547cd8035ed2bb05962cf7824d8aa33e3a3` | 32 | 4 | 2309 |
| App Hub | `e8601b80ce104db2e48208094714bdcffdce6b5a` | 9 | 0 | 121 |
| Octoscript | `68f6a9df55692b5d8ef8873a12721e279a3f40d6` | 0 | 0 | 278 |
| OctoScript-Makepad | `019e6bf043b484676ff39d6ff5be58a1e94abed8` | 0 | 0 | 568 |

普通文件合计 76，已实读并逐个 SHA-256/执行模式核对锁声明，零不匹配。4 个 `.sources/` 相对链接由 bootstrap 在恢复目录建立，不是把外部运行环境打进 bundle。锁记录的排除条目 21 个是已有批准快照规则，本轮没有执行删除。

接手时 RC 工作区尚未恢复 `vendor/`，当时结果仅为 **OVERLAY_STATIC_MATCH**。后续真实恢复/metadata/构建见下方和 `STATUS.md`，不以静态检查代替它们。新 RC 若改框架/宿主，固定 commit + 完整差异 + 最终 tree hash 要由总控同步核对。

已读取 `scripts/bootstrap_sdk.py`：已有 vendor 时只验证，不覆写；恢复使用固定官方归档、普通文件/相对链接/执行模式，并在每个 SDK 的最终 tree hash 和 file count 全相等后放入 vendor。初始核对阶段没有运行恢复或编译；后续总控单独授权的运行记录如下。

总控后续需要保留真实命令/版本绑定：bootstrap restore → `--verify` → Cargo metadata → 锁定 Hub 构建 → Calendar Host 构建/check。这些属于总控集成步骤，不把前轮 0.3.22 的 SDK 恢复/构建证明冒充本轮 RC。

本地 Calendar/EventKit、准入和 Makepad 启动补丁仍属于完整 overlay；锁和源码可读不等于官方上游已接受。正式原版 Gate 与本地扩展 Gate 必须分开报告。

## 实际恢复与核验

2026-10-04T14:18:54.494803+00:00：使用逐依赖 tree-hash 一致的旧 sdk-rebuild/vendor，源缓存只读；恢复到本 RC ignored vendor，再仅同步 complete/mod.rs 的三处模型日志补丁。官方 commit 不变。当前 OctoSense 整体 tree 为 `406dee1ec74a6cf9b85cef41700ffe081aabf9bed4f7f67e77b2484afa686780`，2309 files；其余四树仍与原锁一致。总控更新共享 lock，A4 未修改它。

`python3 scripts/bootstrap_sdk.py --verify` 已成功，返回 SDK_VERIFIED / 12000 files；日志 SDK_VERIFY_INITIAL.log。两工作区 `cargo metadata --no-deps --format-version 1 --locked --offline` 均成功，Cargo.lock SHA 前后相同；详见 CARGO_METADATA_RESULTS.json。metadata 不代表编译或动作成功。

## 官方 archive 解包路径实测

2026-10-04T14:26:14.187366+00:00：在 A4 ignored `.local-state/archive-restore-probe` 复制当前锁/overlay/bootstrap，使用现有 reconstructed official pinned archive cache，五个 SDK 均返回 EXACT_TREE_PASS，随后 --verify 成功。耗时 68.05 秒，restore_exit=0 / verify_exit=0。缓存只读，未重新下载；没有删除此前源码、缓存或证据。bootstrap 仅在新解包文件中应用锁内排除项。当前 root vendor 与 probe vendor 都匹配当前锁，探针不属于发行包。完整证据见 SDK_ARCHIVE_RESTORE_RESULT.json / SDK_ARCHIVE_RESTORE.log / SDK_ARCHIVE_VERIFY.log。

该探针之后按单独授权删除；五份原 archive 的 SHA、tree/count 和无占用检查保留在 `PROBE_REMOVAL_PROOF.json`。这份已通过的恢复证据对应当时的模型 logger SDK，不能替代后续 storage delta 的树验证。

## 后续 storage native delta

总控新增 `fs.sha256_file(path)` 并同步锁。overlay/vendor 两份源 SHA 都是 `6667288e2a5170fa27d1efc005d71830ca302a7f7b572da2141ad81286b9443e`；lock SHA `fcec896f2d2013a65ca51030c2f8e509dc740d675747904098c27b933eaed17f`；Makepad tree `8cb0515697f48a35866d835486ec0786bec61dc9aa8a45eccd3a587e3ac46ea1`（8724 files）。其余四树保持上轮值。构建前 `bootstrap --verify` 再次实际 exit=0 / 12000 files；四项 `splash_storage::tests` 实际 PASS。新 Host/card-host 构建和签后身份只引用 `STORAGE_DELTA_BUILD_RESULTS.json` 与相应 `STORAGE_*_PACKAGE_RESULT.json`，不引用旧 d5000 Host 作为新存储接口的证据。

该 storage 构建完整结束，后验 verify 也实际 12000 PASS。总控后续新增4 KiB准备帧、失败耗时诊断和测试适配，输入改为 lock `3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e` / Makepad tree `de11ee5e9a0509e51039cb9929bb9a217e2a36d63bf0744cbad4a84e1d13ccef`；当前r2构建前 verify再次12000 PASS。storage源仍6667288e...，`vm.rs` / `widget_async.rs` 没有随该帧补丁变更。新测试/包记录用 `CHUNK_*`，旧STORAGE/d5000包与失败证据保留；任一阶段的PASS只适用于其记录的SDK输入。
