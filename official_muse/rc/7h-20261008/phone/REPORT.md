# Transparent compression checkpoint - 2026-10-09T03:18:27.831132+08:00

SPACE_RECOVERY_PARTIAL_RESOURCE_BLOCKED. No build or emulator restarted.

Verified local ditto supports --hfsCompression/--noclone. The raw-log pilot saved no blocks and was not replaced; the rlib pilot saved36864 bytes with identical SHA/size/mode. Batch audited370 files and atomically replaced369 only after full SHA/size/mode/uid/gid/mtime checks, nlink=1, no symlink parents, no open lsof handles, and positive st_blocks savings. One no-benefit file retained; no copy/verification failures. All369 replaced files were independently rehashed and their sizes/modes verified again after the controlled stop. No dependencies, sources, unique evidence or original bytes were deleted.

Batch block savings1425551360 bytes plus pilot36864. Data free changed218083328 ->1674952704 bytes (actual observed gain1456869376, includes concurrent filesystem activity). Remaining eligible1108 files occupy286113792 bytes; even zero blocks for all of them gives1961066496, belowData2GB and insufficient APK/AVD headroom. Therefore stopped own compressor while a verified lsof child checked an own file. One unreplaced temporary copy was compared with its retained original, then only the temp was removed. Original preserved. No cargo/rustc/java/emulator/ditto process observed afterward.

Policyown10.5GB/Data2GB unchanged. Home APK is still NOT_COMPLETED_OR_SIGNED; Android AppHub/Muse runtime NOT_RUN; original seven-hour PARTIAL counts unchanged. Shared read-only Cargo cache, hardlinks, other workspaces and user data untouched. Per-item receipt hfs-compression-items.jsonl; summary hfs-compression-summary.json; pilots hfs-compression-pilot.json/hfs-compression-rlib-pilot.json.

Resume existing locked offline runner only after Data2GB plus packaging/emulator headroom are available; then APK digest/signature/liboctos.so checks and own AVD install/runtime verification. Current resource recovery cannot safely complete those steps.

---

# Post-window continuation - 2026-10-09T03:03:18.108900+08:00

Overall PARTIAL_RESOURCE_BLOCKED. These results are excluded from the ended seven-hour pass counts; original report remains verbatim in REPORT_7H_FINAL.md and the section below.

- Calendar target-OS patch compiled successfully through Home in r5/r6. Android Calendar remains unavailable.
- Home native Rust build finished in r5 (11m38s), again in r6 (49.02s). Real x86_64 Android liboctosense_home.so is retained at official_muse/rc/7h-20261008/phone/.local-state/android-target/x86_64-linux-android/release/liboctosense_home.so; SHA256 8c52e1d7746bc1cbedc88e53902fe88079fe0ec832b614f84f2d2dae7474456f. This is native compilation, not a complete installable APK or runtime success.
- r5 exited241 at own10599292928/free2494001152 bytes, above own10.5GB limit. Only unused own SDK command-line tools and AArch64 Rust std were removed after no-open-file checks (311066624 bytes); sources/downloads/x86 std/artifacts retained.
- Existing locked offline runner r6 exited241 at own10174619648/free233742336 bytes: total Data free fell below2GB. Both failure logs and stop receipts retained. No active build/emulator was observed after exit.
- Partial unaligned APK has five entries, no liboctos.so, and no completed signing/alignment. No usable Home APK; no kernel startup, AppHub/Muse Card/Chat/Memory, rc16 or physical-phone runtime proof.

Do not restart until Data free>=2GB and own10.5GB has packaging headroom. Resume the same runner/cache, then APK/signature/kernel digest and own AVD. No shared cleanup, user data, permissions, contacts, fees or public release. Evidence: post-window-current-status.json, post-window-home-native-elf.txt, home-x86-build-r5/r6.log, home-build-resource-stop-r5/r6.json, post-window-unused-tools-cleanup.json.

---

<!-- PHONE_STATUS_CURRENT_START -->
# Final seven-hour Phone status - 2026-10-09T02:43:44.146610+08:00

Overall: PARTIAL. Deadline 2026-10-09 02:43:07 Asia/Shanghai.

| Item | Actual evidence |
|---|---|
| Official Android kernel | BUILD_AND_ELF_PASS: locked c608384d, api/git/ast, real x86_64 ELF PIE with /system/bin/linker64. SHA32987f438f9b3bdddf62c7db521a7691a405322a796afbd58ace38bd1bf1a496, preserved kernel-artifacts/octos-x86_64 |
| Home APK | NOT_BUILT. r4 real error: Calendar build.rs used its macOS host cfg to compile EventKit for Android; -fobjc-arc legacy runtime rejected. No APK exists under own android-target at this snapshot |
| Minimal Calendar build patch | Own SDK build.rs now checks CARGO_CFG_TARGET_OS. NonmacOS unavailable implementation retained. Patch saved; no post-patch Home rebuild or runtime PASS |
| Bridge | Prior build/lint89 tasks, emulator install and actual settings UI verified. Private AVD generated disks were later removed for storage and have not been recreated; reinstall Bridge after -wipe-data. APK/screenshots/logs retained |
| AppHub to Muse Card/Chat/Memory | NOT_RUN. Private rc15 Gate/catalog verify PASS only. Latest Rootrc16 dd2ce025 was not Android-tested |
| Physical phone / Android Calendar | DEVICE_NOT_TESTED / MISSING_CAPABILITY |

Data free 3564646400 bytes. r4 exec67577 has observed failure and is waiting for remaining compilation jobs; no second Home build started. All r1-r4 failures and deadline snapshot retained. Kernel and source/download/evidence preserved; only authorized own runtime caches removed. No shared SDK/locks, production data, permissions, public release, real contacts or other workspaces changed.

Next: let failed r4 finish, rebuild with own Calendar target-OS patch, verify APK signature and liboctos.so, then recreate only own AVD and reinstall Bridge/Home. Check latest Root source freeze before replacing the private candidate. No Calendar availability claim.

Earlier evidence below is retained; this final status takes precedence.
<!-- PHONE_STATUS_CURRENT_END -->

# Muse 7H · Android 平台检查与候选补丁

开始：2026-10-08 19:43:07；截止：2026-10-09 02:43:07（北京时间）。

本目录只交付源码检查、隔离构建与候选补丁。已在独立Android模拟器安装Bridge prototype，未在实体手机安装应用、未操作 ROM、未修改共享 SDK。没有连接设备，真实手机运行状态为 `DEVICE_NOT_TESTED`。

## 当前已验证结论

| 项目 | 判定 | 证据 |
|---|---|---|
| Phone Home 与 System Bridge 路线 | SUPPORTED，源码契约已核对 | Home 使用同一 `octosense-shell`；Bridge 通过受认证 Binder/AIDL 提供系统能力 |
| 第三方 OctoScript 应用发现与加载 | SUPPORTED，已有实现 | 安装清单 → `hub:<manifest-id>` → 同一 Card runner；安装/更新后失效缓存 |
| 应用发现边界修补 | 候选测试 PASS | 原 8 项测试 3 PASS / 5 FAIL；修补后 13 项 Appstore 测试全过 |
| 签名、平台、权限准入回归 | 源码测试 PASS | App Policy 22 项单元测试 + 1 项文档测试；未改 launch 准入路径 |
| cargo-makepad 构建 | PASS | 固定源码、`--locked --offline --release` 构建成功 |
| 官方 Android 工具链 | 隔离准备完成 | JDK 17.0.2、Gradle 8.11.1、SDK 35/33-ext4、Build Tools 35/33.0.1、NDK r28b；发布摘要全部核对 |
| Home APK 构建 | NOT_BUILT，x86_64 std下载中 | Home契约导出24任务成功；准备独立模拟器构建 |
| Bridge APK 构建 | BUILD_PASS + EMULATOR_UI_PASS | prototype+lint 89任务成功；模拟器真实安装、设置页截图已查看 |
| 官方源码身份检查 | FIXED_BASE_WITH_EXISTING_OVERLAYS | 真实Git恢复7f962547；2301文件核对，28既有覆层差异；framework --check --no-hub PASS |
| Muse Android 日历 | MISSING_CAPABILITY / NEEDS_HOST_PATCH | 当前 Calendar Host 是 macOS EventKit，非 macOS 明确返回 unavailable |
| Muse 手机全链与视觉 | NOT_RUN / DEVICE_NOT_TESTED | 模拟器已开机，Muse尚未加载；实体手机未连接 |
| 上游接受补丁 | 未接受 | 仅本地候选；没有 PR、发布或推送 |

## 官方路线与实际缺项

固定 OctoSense `7f962547cd8035ed2bb05962cf7824d8aa33e3a3`；App Hub `e8601b80ce104db2e48208094714bdcffdce6b5a`。其他固定来源见项目 `dependencies.lock.json` 与隔离 SDK 的 `SNAPSHOT.json`。

Home (`phone/`) 与桌面共用 `crates/shell`，不是另一个 Muse Runtime。Android Home 启动同一官方 octos 内核；原有 `rom/scripts/build-home.py` 将内核打包为 `liboctos.so`。Bridge 独立 APK 验证 Binder UID、用户、包和证书；公开开发签名只用于测试，不建立生产身份。原有 root 控制仍为显式可选路径。

App Hub 原先已经读取安装目录并将应用加入启动列表。Shell 将清单 ID 变为 `hub:<id>`，Card 通过既有 App Hub 校验加载。安装与更新会让图标、启动列表和旧 Card 缓存失效。本轮没有重复实现这一机制。

Muse 当前 listing 只声明 macOS。Android 邮箱有真实网络服务和 Keystore 分支，模型沿用官方 `model.complete`/provider 契约；这些只能说明源码存在，不能当作手机运行通过。现日历实现仅有 EventKit，没有 Android CalendarProvider 适配，因此不能把 Muse 直接改成 Android 可安装全功能应用。

## 跨平台复用评估

| Muse 组成 | 结论 | 条件 |
|---|---|---|
| 一次性事项、Memory DSL、去重与恢复 | 可原样复用业务源码 | 复用官方 app-scoped Storage；不迁入私人桌面数据 |
| Model contract | 小幅兼容 | 手机需独立配置已授权 provider；成功回复不是系统动作回执 |
| Mail adapter | 需要手机运行验证 | Android Keystore、账号登录、网络与后台生命周期仍需实机检查 |
| Calendar adapter | 需要宿主支持 | 要先实现并审查 Android 日历查询/写入/独立读回契约 |
| 结果卡 | 可复用语义；视觉需验证 | 使用现有 Splash/Card runner，不换技术栈 |
| 三栏 UI | 小幅兼容，未验收手机像素 | 纵向手机要使用现有折叠行为；不能由桌面宽屏截图推定可用 |
| ROM 集成 | 暂不执行 | 不刷机，不替换系统组件，不授予 root |

## 最小候选贡献

`patches/app-hub-installed-discovery.patch` 仅修改 `crates/appstore/src/lib.rs`：

1. 清单 ID 必须等于安装目录名。
2. 清单最多读取 64 KiB，并在实际读取时继续限制增长。
3. 安装目录、bundle、manifest 的规范路径必须分别留在所属根内。
4. 坏清单、缺目录和坏 UTF-8 不阻止其他正常应用被发现。

显式指定的安装根本身可以是软链接。签名、摘要、平台、publisher 与 capability 验证仍由原有 Card launch 执行。这个补丁加强发现边界，不把启动列表当作授权凭据。

证据：`evidence/discovery-before.log` 保留 5 项失败；`discovery-after.log` 为实际 13 项 Rust PASS；`admission-regression.log` 为实际 22+1 项 PASS。新的原始副本干净应用补丁后，与被测试候选 SHA-256 一致。版本与哈希见 `patches/PATCH_IDENTITY.json`。

## 隔离复现

`prepare_sdk.py` 只复制既有固定源码，不修改原始 vendor；`.local-state/` 被排除在 Git 外。

```sh
python3 prepare_sdk.py --vendor /path/to/pinned/vendor --output /path/to/isolated/sdk
patch -C -p1 -d /path/to/isolated/sdk/app-hub -i /absolute/path/to/app-hub-installed-discovery.patch
patch -p1 -d /path/to/isolated/sdk/app-hub -i /absolute/path/to/app-hub-installed-discovery.patch
CARGO_TARGET_DIR=/path/to/isolated/cargo-target cargo test --locked --offline --release --manifest-path /path/to/isolated/sdk/app-hub/Cargo.toml -p octosense-appstore -- --test-threads=1
CARGO_TARGET_DIR=/path/to/isolated/cargo-target cargo test --locked --offline --release --manifest-path /path/to/isolated/sdk/app-hub/Cargo.toml -p octosense-app-policy -- --test-threads=1
```

上述命令已用实际隔离路径执行。离线测试要求已缓存锁定的 Rust 依赖；新环境没有缓存时会准确失败，不修改锁文件。

构建工具以 `TOOLCHAIN_LOCK.json` 固定官方 URL 和摘要。`prepare_tools.py` 验证后安装到给定目录；NDK 只省略未用于编译的调试和分析工具，保留编译器、完整 sysroot、Clang 资源及许可证。构建状态与最终产物哈希会在实际完成后补入报告。

## 真实聊天接续检查点（23:25，非最终验收）

最新授权与意外上下文恢复边界见 `HANDOFF_REAL_CHAT.md`。当前分支只产出Phone范围成果；原项目清理提交7fbda978不属于本轮成果。

AVD MusePhoneAPI35、Android API35 x86_64，emulator37.2.12；独立模拟器端口5580，ADB5041且仅连接emulator-5580。sys.boot_completed实际1。Bridge prototype安装Success，冷启动Status ok/8739ms；初次截图System UI ANR保留，点击Wait恢复后截图显示真实设置页。Notification access仍Not enabled，没有授权系统权限。`bridge-emulator-after-wait.png`为已查看页面证据。

Home尚无APK。脚本计划使用官方包名dev.makepad.octosense，实际官方packager，release opt-level=1/debug=0/incremental=false，用于模拟器开发候选；已核对官方强制内核路径，新增独立x86_64 kernel构建脚本；Home构建强制检查并打包liboctos.so，尚无构建结果，不能称完整正式Home+kernel成品。最终还须实际构建、安装、AppHub→Muse Card/Chat/Memory验证。无EventKit，不做Calendar CRUD。

## 2026-10-09 00:15 resource-limited checkpoint

Bridge installation and real settings UI remain verified. Kernel r3/r4 used the explicit private Android sysroot and progressed beyond the prior missing-core error; r4 compiled octos-core/octos-bus and native dependencies. Both attempts terminated by the authorized resource guard, not by a new observed compiler error. r4 receipt: own8995561472 bytes, free5049843712 bytes. No kernel executable, Home APK or Muse Android full-chain success is claimed.

CMake3.31.6 CLI/modules were installed only into own ignored tooling, after official published SHA validation. Scoped repair/evidence commit bbbdd2c2; no push. All sources, downloads, incremental build cache and failure evidence are retained. No kernel/Home/emulator build process is active. Resume only after adequate Data free space and own9GB headroom; private mirror remains running on127.0.0.1:8571. The cceeaa Muse input is a historical validation candidate, not Root final freeze.

## 2026-10-09 01:38 continuation checkpoint

Latest Root changed guard to own10.5GB/Data2GB (decimal bytes), recorded resource-policy-r2.json. Frozen rc15 main SHAcef7d576b2de31e5c22a813e70e68370ff0ddd043ef1bbcd57acae75eb81b546 copied unchanged. Manifest0.3.27-rc15 without Android Calendar; Gate PASS and new private catalog anchor verify PASS. Original catalog and refused attempts retained. Candidate receipt phone-candidate-rc15-identity.json; scoped commit89b29df2.

Locked official kernel r5 progressed through octos-cli and all listed dependencies; final rustc remained active, but disk free suddenly fell from~3.5GB to1398710272 bytes. Own9998991360 bytes remained below10.5GB. Guard terminated exec63323 (exit241), no new observed compiler failure. Data1.4GB remains below2GB. Cannot safely resume. Kernel executable/Home APK are still NOT_BUILT; no AppHub-Muse Android runtime claim. Bridge prior UI evidence remains valid; physicalDEVICE_NOT_TESTED. No core/shared SDK/original project/production data/permissions changed. Own SDK lacks preparation_chunk, so Root4096-to1024 single-line patch was not silently fabricated.
