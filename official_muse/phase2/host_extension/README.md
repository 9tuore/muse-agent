# 最终候选 0.2.9 来源摘要补丁（2026-10-01）

`makepad-storage-sha256.patch` 为锁定 Makepad 的 `widgets/src/splash_storage.rs` 增加 `fs.sha256(text)`：返回精确 UTF-8 字节的 SHA-256 小写十六进制，最多 64 KiB，只对已有 storage jail 的 isolate 开放。该函数不读文件、不联网、不改变 grants 或路径准入。未修改原版安装包及生产 Memory；不是上游已经接受的新接口。

未修改文件 SHA-256：`a0f15e96e7fd5c990ab010fa9dce6d1d2c7d4c7dff32390cf26cf1fed217e7cf`。应用补丁后须重新 locked 构建 Shell 和 card-host，旧宿主不能直接用于这轮来源 hash 验收。Pure Splash SHA 试验对短向量正确，但长文触发原有运行预算；正式应用未引入该实现，也未提高预算。

验证命令及最终宿主 SHA 以 `PHASE2_FINAL_TEST_REPORT.md` 为准；构建正在进行，不能提前标通过。应用 envelope 沿用 `muse.dsl/1`，来源 hash 不自动回填或覆盖历史记录。

# 当前实机更新：Muse 0.2.8（2026-10-01）

最终真实打包Shell中，三个新模型Goal与23文件正常重启核验通过；Calendar full_access，合成事件create/get/update/get/delete/get通过并清理。Chat指定三轮复测2/3，仍不稳定；真实Mail与邮件→日历同Goal未验收。原版Gate拒calendar，扩展签名check通过；scan自审human-review。最终报告见仓库根目录PHASE2_LIVE_TEST_REPORT.md。以下保留基线、补丁构建过程与历史观察；0.2.1/2/3/7状态不代表最终8。

---

# Muse Phase 2: local Calendar host candidate

This is a **local extension candidate**, not a capability accepted by the unmodified official App Hub or Shell. It is delivered as reviewable patches. No upstream repository, installed production Shell, old Muse app, or production account was modified. The authorized live tests created, modified and deleted only named synthetic EventKit events, as recorded below.

## Final 0.2.2 validation update (2026-09-30)

The final Muse 0.2.2 candidate was installed through the isolated Release Shell App Hub and visibly ran eight Chinese pages. Three fresh model-backed Goals completed and retained identical result hashes across a Shell restart. A previous 0.2.1 third-Goal timer overrun recovered safely after upgrading to 0.2.2; the separate app change moves finalization to a later tick. A demo Host Mail session exercised read, draft, exact preview and confirmation but delivered no real email. The same Shell returned `calendar.status=write_only`; no TCC prompt or EventKit mutation was run. See `PHASE2_TEST_REPORT.md` in the app repository. The historical 0.2.1 failure observations below remain evidence of the defect that prompted the fix.

## Live packaging check (2026-10-01)

The first ad hoc `.app` contained only the binary and Info.plist. The packaging script now copies the pinned `makepad_widgets`, `octosense_shell`, and `octosense_app_hub_app` resource trees and links them beside the executable, matching this non-`apple_bundle` build's resource lookup. The first resource candidate (before the App Hub tree was added) retained Release binary SHA-256 `0aa2aa13176c1b2956de2174000b3b2b6c4ee4c9ebfbb24421c01fe150816438`, had `NSCalendarsFullAccessUsageDescription`, and passed `codesign --verify`. Actual `open -n` and direct bundle-executable tests still showed only the top bar while widget snapshots populated; the real-window image is `official_muse/app/build/phase2-live-resource-app.png`. The missing resource files were a packaging defect, but **adding the resources did not resolve the black client area**. No Calendar TCC prompt or mutation was run in this check. Packaged EventKit LIVE remains unverified.

Later same-source `0aa2aa13…` trace runs narrowed the black image: the bare Release executable rendered App Hub, while its Resource3 `.app` copy had a populated widget snapshot but a black client area. Both reached `FIRST PRESENT ON GLASS`, compiled 51 shader definitions, and logged no Metal command-buffer or pipeline failure. The bare trace reported completion of 51 `newLibraryWithSource` and 102 `newRenderPipelineState` callbacks by first present; the black `.app` trace reported no completed callbacks by that point. Its offscreen `wm_window_surface` pass still ran but averaged far less GPU time. A short `gpu.drawcalls` sample showed zero completed draw calls for several main/window passes. A later 0.2.3 `.app` process sample (`official_muse/app/build/phase2-live-app-sample.txt`) showed Metal's compiler reply queue blocked inside Makepad's library completion block while it synchronously submitted `newRenderPipelineStateWithDescriptor`; Apple's compiler request queue was waiting for that reply. This is concrete evidence of a callback/request queue deadlock in that run. The raw local logs are `official_muse/app/build/phase2-trace-bare.log` and `phase2-trace-app.log`; they are diagnostic data, not a passing packaged UI test.

## Metal pipeline candidate (2026-10-01)

`makepad-metal-pipeline.patch` applies to the pinned Makepad `platform/src/os/apple/metal.rs` (original SHA-256 `47db4d10503ee4ed70860529f914df8b740c16f2bc04f768fcb9fb69314f5a04`). It retains the library completion callback's failure and function checks, then submits both pipeline variants from a short-lived named worker after the callback returns. Retained `RcObjcId` references keep the device and functions alive across that handoff. Pipeline completion still publishes the original `OnceLock` result and UI signal; failure to start the worker explicitly reports shader failure. It neither changes the VM budget nor bypasses capability or permission checks. `patch --dry-run -p1` against the untouched pinned Makepad tree passed.

The isolated Release build with this patch passed `cargo build --offline --locked --release -p octosense --no-default-features --features app-hub` in 8m47s. Binary SHA-256 is `a588d4a35d105f0c2cce213fbc7c1ca9f6f8f0ebbf4ee1006b019450657059a9`; modified `metal.rs` SHA-256 is `e1b66bc2c84700d59999e903077ffe9892a2659d9d91aa023ffc4de9815994b8`. The new isolated `target/muse-calendar-test/OctoSense Muse Phase2 Live 0.2.3 MetalFix.app` contains the three resource trees and `NSCalendarsFullAccessUsageDescription`; ad hoc `codesign --verify --deep --strict` passed. Its signed executable SHA-256 is `a4edbe60ca54c7c83fa497065d97a9e90b465da1d874c8d5c1076d0b46ba5bcf`. A normal LaunchServices start first showed a black client area, then visibly rendered App Hub and wallpaper in `official_muse/app/build/phase2-metalfix-start2.png`; `phase2-metalfix-start.png` retains the initial black frame. This verifies the first packaged render, not restart stability or Calendar LIVE. No TCC request or Calendar mutation was performed in this packaging check.

## Source identity

- App Hub: actual Git base `e8601b80ce104db2e48208094714bdcffdce6b5a`; local patch commits `81561192b36ed87ef989f6ff00681446cace406b` (calendar Gate/copy) and `29bfc0f` (two missing lock entries needed for a locked local `hub` build). The format patch is `app-hub-calendar.patch`.
- OctoSense: the supplied locked **source archive** is labeled `7f962547cd8035ed2bb05962cf7824d8aa33e3a3`, but has no `.git` and that commit was not independently checked out here. Its original `Cargo.lock` SHA-256 is `bb15bf9058699f8341a4fc8403833eab37588e8b9828757f60bbb5ce16f44729`; `native-apps.json` SHA-256 is `efe610b3a04890b5f8404b2f545a9d04868e546114ffdb1abe7a462c0d630f9a`. `octosense-calendar.patch` applies to this archive and was replayed byte for byte on the ten changed files in a temporary tree.
- Optional Splash startup candidate: `makepad-splash-budget.patch` applies only to the pinned Makepad source copy at `widgets/src/splash.rs` (original file SHA-256 `cae76b398bf37fb92e3e6364bd7e121baac40055cc247170b1f14843129f2a07`). It separates trusted theme setup and app source evaluation into two isolate entries, each still subject to the original 64 ms wall-clock budget. Its patch replay was byte-exact in a temporary tree. This is a separate local framework extension and is not part of the official pinned framework.
- Optional Metal deadlock candidate: apply `makepad-metal-pipeline.patch` to the same isolated Makepad copy. It is a separate local framework change, not part of the official pinned framework; the first packaged render is recorded above, with subsequent normal Launch Services restart rendering verified in the live report.
- The OctoSense patch retains the original `e8601b80` dependency pins, and adds a **local Cargo path patch** to `.sources/app-hub`. This intentionally resolves all App Hub crates to the extended checkout. A Cargo build with that overlay is not evidence that upstream accepted the new capability.

## Reproduce in an isolated checkout

1. Copy the supplied OctoSense source archive to a separate directory; check the two original SHA-256 values above. Apply `patch -p1 < octosense-calendar.patch` and `patch -p1 < octosense-model-chat-history.patch` from its root.
2. In a separate App Hub Git checkout at the exact base above, apply `git am < app-hub-calendar.patch`. Do not replace the unmodified App Hub checkout or its running CLI.
3. Prepare the pinned Makepad and OctoScript dependencies according to OctoSense `tools/setup.py`. Point the isolated Shell's `.sources/app-hub` at the extended App Hub checkout. The supplied source snapshot's `.sources` are source directories without `.git`, so `tools/setup.py --check --cargo` reports `Expected an empty dependency directory`; this local build used those locked source files but does **not** satisfy that provenance check. A reproducible official check requires real Git checkouts of the precise framework pins.
4. In the isolated OctoSense root: `cargo check --offline --locked -p octosense-shell --no-default-features --features app-hub`, then `cargo test --offline --locked -p octosense-calendar-service --lib`, then `cargo build --offline --locked -p octosense --no-default-features --features app-hub`.
   To evaluate the optional framework candidates, copy the pinned Makepad source to a separate path, apply `makepad-splash-budget.patch` and `makepad-metal-pipeline.patch` inside that copy, and point only this isolated OctoSense checkout's `.sources/makepad` at it. Then run `cargo build --offline --locked --release -p octosense --no-default-features --features app-hub`. Never patch the locked original or reuse this copy for a stock comparison.
5. Run `python3 tools/package_calendar_candidate.py --release --output '<new-isolated-path>.app'` there. It copies the Release binary and the pinned Makepad widgets/Shell/App Hub resource trees into an isolated `.app`, provides executable-relative links for this non-`apple_bundle` build, adds `NSCalendarsFullAccessUsageDescription`, assigns a distinct local test bundle identifier, and applies an **ad hoc local test signature**. This is not distribution signing. Verify the bundle's Info.plist, resources, signature, and real-window rendering before testing TCC. The Debug bundle was not visually usable in the test below; do not use it for final UI evidence.
6. In the extended App Hub checkout, run `cargo build --offline --locked -p octosense-app-hub --bin hub` and `cargo build --offline --locked -p octosense-card-host --bin card-host`. Use **these** binaries for calendar bundle `hub check`, `hub scan`, and card-size checks; the stock CLI should continue rejecting the unknown `calendar` capability.

The test launch should use a fresh `OCTOSENSE_HOME` so no production Shell state is touched. The macOS `open` command supports `--env`, for example `open -n --env OCTOSENSE_HOME=<new-empty-test-directory> <candidate.app>`. Do not set `OCTOSENSE_DEV_MODE` or `--dev-grant-all`. Install only a bundle that has passed this extended `hub` Gate; ordinary capability grant and the user's separate confirmation are still required before any calendar mutation. The original test instructions reserved the system TCC prompt for the user. The user later explicitly authorized the agent to grant local test permissions. In the 2026-10-01 live test the agent clicked the actual macOS Full Access button under that authorization; no TCC database or permission bypass was used. Mail login and final real send still require the person.

## Local verification and limits

- `cargo check --offline --locked -p octosense-shell --no-default-features --features app-hub`: PASS.
- With the separate Makepad startup candidate, the same `cargo check` also PASSED (3m38s); its Release Shell runtime evidence is recorded below.
- With that Makepad copy, `cargo build --offline --locked --release -p octosense --no-default-features --features app-hub` PASSED (6m56s). Final pre-signing Release binary SHA-256: `0aa2aa13176c1b2956de2174000b3b2b6c4ee4c9ebfbb24421c01fe150816438`. The same build was copied into `OctoSense Calendar Release Candidate.app` and ad hoc signed: its **post-signing** executable SHA-256 is `617a2d896253c9eb6aab123464c56d947d3010e09ad759da0a1e3405b2284c14`, Info.plist SHA-256 `976a70cdbaab8b5e9a346edaa5bddd4b06525d01e71b52abc9c293424274839b`, bundle identifier `dev.makepad.octosense.musecalendar.release.local`; `codesign --verify` PASSED and the full Calendar usage description is present. No TCC prompt was triggered.
- The isolated Release Shell subsequently loaded the four-capability Muse card visibly; the first Goal (including the model path) completed and survived a Shell restart, and a second Goal completed. A third Goal's approval reached durable `running`, then wrote and independently read back its result; the timer callback exceeded the existing 64 ms VM budget at the start of `core_finish_run`, leaving the Goal/Run marked `running`. The persisted Activity sequence is `Plan approved` → `storage write` → `readback`, and the Shell log reports `script time budget exceeded`. This is a separate callback budget issue; the startup patch does not make the complete multi-Goal chain PASS. The successful initial render alone does not prove the startup patch was the sole cause, because Shell rendering showed nondeterminism in controlled retries.
- In that isolated Shell, Muse's read-only `calendar.status` returned the actual host permission `write_only`; the Calendar page showed this value and disabled operations requiring `full_access`. The real-window evidence is `evidence/phase2/after/shell-release-0.2.1/calendar-permission.png` in the app repository. This establishes capability dispatch and EventKit permission-state readback only. `calendar.request_access`, TCC choice, `list/get/create/update/delete`, system-event readback, and the end-to-end mail-to-calendar flow have not run. The signed local `.app` is prepared for a later authorized TCC test; the current Shell run used the bare Release binary and cannot establish packaged TCC behavior.
- `cargo build --offline --locked -p octosense --no-default-features --features app-hub`: PASS. Candidate binary SHA-256: `1089aeb6302334ffc0d780d29f0ff7c9271b654f22608d4db0e9d0087f69bbcf`. Linked EventKit confirmed with `otool -L`.
- The first Release build **before** the optional Makepad startup patch also compiled (15m50s), binary SHA-256 `cb541cccf54c5f2b920baffc38b8fd8692e0ee03a280311fb85eb7ddfd4bc3a0`. Its initial captures showed only the top bar and a dark desktop/App Hub. The earlier Debug `.app` capture was uniformly RGB(16,19,21). These remain historical failed visual attempts, not the current candidate's result.
- A later controlled comparison launched the unmodified stock Release Shell with the same isolated HOME/APP_DATA/Hub mirror; one capture was dark outside the top bar while its widget snapshot populated. A single-instance retry with **the same** HOME/APP_DATA/Hub mirror then rendered the full App Hub (`stock-shell-release-apps-retry.png`, 2.66 MB). The black capture is therefore nondeterministic in this setup and cannot be attributed to either Calendar code or APP_DATA content from these observations.
- `cargo test --offline --locked -p octosense-calendar-service --lib`: 3 PASS (validation, damaged journal, completed/pending replay).
- Objective-C EventKit bridge: `clang -fobjc-arc -fsyntax-only -x objective-c -Werror ...`: PASS against macOS SDK 15.2; test machine runs macOS 14.8.7.
- `cargo build --offline --locked -p octosense-app-hub --bin hub`: PASS after the two-entry App Hub lock fix. Extended `hub` SHA-256: `e8d68c072a24f01bcc7edbdd1061d3ea9c2b18f61ba12e299e6104669fb79d1b`.
- `cargo build --offline --locked -p octosense-card-host --bin card-host`: PASS; extended `card-host --help` ran. Binary SHA-256: `013ac719b56009ce9483cf819bbddee43c68a49e5b1cb47ed6f5033052e37b74`.
- `cargo build --offline --locked --release -p octosense-card-host --bin card-host`: PASS (8m45s). Binary SHA-256: `cde35951308eab724a0ed01c0894619c78a5c74221eb67aa8af031aac958d198`. In a separate app-data jail, it admitted the final four-capability Muse 0.2.1 bundle (`main.splash` SHA-256 `14fcbe6fedf020ffea4f42339b2d69446678331f3248f751ba43cfca0cf61f87`) and evaluated its 180,046-byte Splash body with `view=true`. A real 990×539 remote window capture displayed the Chinese Chat page and navigation. This card-host test establishes bundle loading and visible card rendering; the subsequent Shell test above establishes separate `calendar.status` dispatch.
- `cargo test --offline --locked -p octosense-app-policy calendar_requires_an_explicit_capability -- --exact`: 1 PASS.
- Extended `hub check <isolated-bundle> --allow-unsigned`: PASSED with the expected unsigned-publisher warning; it resolved exactly `{calendar, mail, model, storage}`. The same check without `--allow-unsigned` was refused by the normal signature policy.
- `python3 tools/native_apps.py --check`: PASS. Candidate `.app` contains the full calendar usage description and passes `codesign --verify`; its signature is ad hoc and has no Team ID.

**Current boundary:** the prior isolated Release Shell visibly ran the four-capability Muse and returned the real `calendar.status=write_only` permission state; the final 0.2.2 Goal regression is recorded above. The new 0.2.3 MetalFix `.app` has built, passed packaging checks, and rendered App Hub and wallpaper after an initial black frame. Restart stability and packaged EventKit TCC remain unverified. Full Calendar read/write and the combined mail-to-calendar task remain unverified. This is a local candidate only; it does not prove official upstream acceptance or production packaging.

## Latest live verification: Muse 0.2.7 (2026-10-01)

The final runtime is `OctoSense Muse Phase2 Live 0.2.7.app`, launched normally through `open -n`, with isolated HOME/APP_DATA and the signed local App Hub catalog. The post-signing executable SHA-256 is `a4edbe60ca54c7c83fa497065d97a9e90b465da1d874c8d5c1076d0b46ba5bcf`. It uses the Calendar, native model-history, Splash startup and Metal pipeline patches listed here. This is an ad hoc local test environment, not stock official acceptance or distribution signing.

Actual 0.2.5 EventKit create/get/update/get/delete/get receipts were verified and both earlier synthetic test events were removed. Final 0.2.7 repeats and the independent restart checks are recorded in the repository root `PHASE2_LIVE_TEST_REPORT.md`; that report supersedes historical “unverified” status above. Mail remains blocked on person-only account login and a designated test recipient. Native role history reaches the real Qwen model, but its three-turn no-repeat/counting instruction is not stable, so the overall result remains PARTIAL.

Final 0.2.7 packaged EventKit create/get/update/get/delete/get passed for `MUSE-CALENDAR-TEST-20261001-027`, including independent `found=false` after delete. The 0.2.6 test event was also removed after repairing the app test-ID check. Three fresh 0.2.7 model-backed Goals completed with one Run each. Main Splash SHA-256: `776809486924a9d91ae42aaf38d0af2ca2731bbfb8747401d8c7732ff7f2a6e5`; bundle BLAKE3: `cb3cacdd3716ef5048eee4780c921d58b0f3a2dd7b52f59c225b89091352d2c0`.

## Final 0.2.9 candidate (2026-10-02)

The final main source is product commit `17e63c5`, SHA-256 `eb0e32778c03ea4cc7e331a63ad9aee7bd36bdf5c541e1ec61d99502199b1489`. The signed and installed source matches byte for byte. Packaged Shell executable SHA-256 is `56ad9012c8dae9387c690d3fd896efc2e67e0806b91e097ad0342567df2f7e2f`; patched card-host SHA-256 is `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`.

The isolated `makepad-splash-budget` tree now includes the UTF-8 `fs.sha256` patch. An explicit Cargo config, `official_muse/app/build/phase2-029-cargo.toml`, resolves the eight Makepad patch packages to this tree. The card-host was built using that config with `build --offline --locked --release --target-dir ../OctoSense/target -p octosense-card-host`; native digest vectors and over-64-KiB refusal passed in that exact runtime. No script/time/heap budget increase was used.

Final visible Shell tests passed three model-backed Goals, a long-text Goal, source Memory edits, five window requests and normal restart with seven file hashes unchanged. Chat transport is verified; numeric-count semantics remain limited. The new packaged binary returns `calendar.status=not_determined`, and Mail has no signed-in account. Final Calendar CRUD, real Mail delivery and the linked external task are pending person-only nodes. Historical 0.2.7 CRUD is not counted as a 0.2.9 pass.

See the root `PHASE2_FINAL_ACCEPTANCE.md`, `PHASE2_FINAL_TEST_REPORT.md` and `PHASE2_FINAL_EVIDENCE_INDEX.md`. This remains a local ad hoc runtime and signed rehearsal catalog. Stock Gate still refuses calendar; neither Calendar nor the SHA interface is presented as accepted upstream.

## 0.2.10 Chinese presentation patch (2026-10-02)

Apply `octosense-zh-ui.patch` inside the isolated OctoSense export and
`app-hub-zh-ui.patch` inside its paired App Hub checkout, **after** the existing
Phase 2 patches described above. Both apply checks passed against the saved
pre-localization baseline. App Hub source commit: `97d75ac`.

These patches translate Muse-facing Mail and model settings sheets, App Hub
navigation/permission descriptions, Shell menus, launcher labels, weekday and
startup presentation. Protocol fields, persisted states, manifest capabilities,
consent hashes, credential namespaces and model route decisions stay unchanged.
Only host display JSON fields receive Chinese labels. No new grant is added.

Build using the same locked local Makepad source with
`cargo build --offline --locked --release -p octosense --no-default-features --features app-hub`.
Package into a new path with the existing `tools/package_calendar_candidate.py`.
The accepted package is `OctoSense Muse 中文版 0.2.10-r2.app`, locally ad hoc signed,
executable SHA-256 `24bcaddaee2297a1fe524a2cebc380814e1987d609e89e2cfb4a8efac9ebd10f`.

Mail unit tests: 8 passed/2 ignored; model unit tests: 27 passed/1 ignored;
App Hub unit tests: 36 passed. Final visible Shell passed eight Chinese pages,
empty Mail validation/protocol switching, five requested layouts, real model
chat, a real model Goal and restart with nine durable file hashes unchanged.
Model format rejection is recorded separately; real Mail send and final system
Calendar CRUD remain unverified. See `MUSE_CHINESE_UI_REPORT.md`. This is a local
extension and rehearsal catalog, not upstream acceptance or distribution signing.
