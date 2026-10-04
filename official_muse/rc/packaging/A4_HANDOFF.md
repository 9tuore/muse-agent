# A4 当前交接

当前阶段：069d严格新环境完成SDK恢复/12,000文件验证及两个native依赖fetch，Host在磁盘压力下受控停止。仅删除本轮不完整target，尚未恢复2GiB；等待总控安排进一步空间与V14最终源码边界。最近完成的warm app仍是4 KiB SDK r2 Intel构建/打包，本轮没有新的完整Host/card包或最终clean-build PASS。详细终态见CLEAN_ROOM_R2_FINAL_AUDIT.json。

## 当前可用运行产物

| 产物 | ignored 路径 | 签后 executable SHA256 |
| --- | --- | --- |
| 完整 Host | `.local-state/chunk-delta-r2/Muse Chunk RC Host.app` | `938ba58a204de0421b2935c974a22645de14a6b7682f1004bc72c701c3793b3d` |
| card-host | `.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app` | `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837` |

两者 x86_64、严格 ad hoc 验签成功、未公证；Host 三组运行资源、card-host 一组 makepad_widgets 资源和 SDK license 均已打包。`otool -L` 两者只有系统动态库路径。`CHUNK_DELIVERY_AUDIT.json` 记录大小、资源、路径、签前/签后 SHA；Host 117,778,168 逻辑 bytes，card 88,898,745 bytes。没有内嵌最终 Muse bundle，没有由 A4 启动业务 GUI 或调用真实账号。

SDK 输入：lock `3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e`；splash preparation 源 `7d572f34718b494eeeaa9764264747490025a37c10aa4ba2134159585b519c29`；storage 源仍 `6667288e2a5170fa27d1efc005d71830ca302a7f7b572da2141ad81286b9443e`。Makepad tree de11ee5e...；其余四个 SDK tree 不变。

## 实际验证

- 构建前/后 `bootstrap --verify` 都 exit=0 / 12000 files，8项 watched 输入 SHA 均未改变。
- 三个实际 pure Cx/VM 测试全 PASS：`large_cold_source_is_prepared_before_one_application_run`、`a_failed_cold_preparation_cannot_restart_through_style_reapply`、`closing_a_partly_prepared_source_cancels_the_remaining_frames`。真实 namespace 为 `splash::style_tests`；两条命令实际分别运行2项和1项，避免0-test成功。
- card release 237.28秒、Host release 404.10秒，均 locked/offline exit0；card `--help` 0.081秒 exit0，不启动 app_main 窗口。
- 每条实际命令、退出码、日志 SHA、输入/输出 SHA 在 `CHUNK_DELTA_BUILD_RESULTS.json`，原始日志为 `chunk-*-r2.log`。
- 原 storage r1 窄测试4 PASS、两包、后验SDK verify 全PASS，记录保留；旧 d5000 Host、storage Host4942624e、card efd7c856 及原构建/测试失败也保留。LLM 原整包15 FAIL 没有被改写成全PASS；中文变体service19 PASS与Calendar pure3 PASS单独记录。

## 未完成与下一阶段

总控/A1/A2/A3 绑定当前 Host/card 与实际冷启动和业务证据。已只读核对 owner 的 V9 4 KiB preflight：source 4ce87cc7... / Host 938ba58a...，1次真实 Shell cold PASS；报告是合成状态，不能代替70次矩阵、真实账号或双机验收。原 SDK prepare budget FAIL 及 readonly 比较在 `BUDGET_SOURCE_COMPARISON.*` / `REPORTED_PREPARE_FAILURE_TRACES.json`；缩帧后实际产品运行结论不由编译推断。保留64ms/执行/heap校验，没有 A4 共享源码修改。

最终源码clean-room实际运行74a4bfca6880806e7d6764888fc8583714c742cb，并按总控V10修补指令在heavy编译前停止。精确新checkout、五个官方fresh archive恢复81.44秒/构建前SDK verify12000 PASS；新CargoHome fetch776.04秒，TLS/timeout重试日志保留。仅SIGINT本轮cargo86847（核对owned cwd/runner parent），cargo exit=-2、runner exit1；原FAIL报告未改写，CLEAN_ROOM_R1_FINAL_AUDIT.json解释为总控请求的受控停止，非完整构建通过。Host/card/Hub未编译、target未创建。本轮新目录/private/tmp/muse-clean-74a4bfca-r1-20261005及archive/source/cargo-home/原日志全部保留。等待V10新最终commit，再严格新out/newSDK/newCargoHome/newtarget真实执行；不复用74a4环境冒充fresh。公开开发公钥来自现有catalog，当前rc5签名bundle实际check PASS，无私钥读取、无正式publisher连续性结论。

旧Hub CLI在删除缓存前已独立保留de6840...副本，现持久工具路径`.local-state/tools/hub`，SHA de6840e5aa85c73c915434488da2cd4ec8f633bde7f2f69f6259e17993318e6f，CLI help exit0；总控已确认实际恢复。旧cache路径依赖失效的事实保留，不需要重建Hub。

已完成两处获准可再生缓存清理，证据 CACHE_REMOVAL_PROOF_R2.json（先前编译活动导致的暂缓记录保留在 CACHE_REMOVAL_ATTEMPT_R1.json）。删前/删后可用空间分别 3,272,814,592 / 5,915,557,888 bytes（3.05→5.51GiB），净增2,642,743,296 bytes（2.46GiB）。旧debug/release原分配共2,794,582,016 bytes；净可用空间受其他运行活动影响，不把两值等同。容量规划仍建议8GiB以上/优先12GiB，目前低于该规划值，不是已测峰值。仅曾按明确授权删除 A4 重复 archive 恢复探针624,861,900逻辑bytes，原archive/源码/license/日志/运行app均保留；本轮仅删除上述两处旧targets。清理仅限上述两个精确编译缓存，满足检查后执行；源码、archive、SDK、CargoHome、运行包及唯一证据不删。

App Hub 材料仍 PARTIAL：真实 Privacy URL、正式身份/连续性、两张同最终RC真截图、最终scan packet/准入和本人正式提交许可。Calendar upstream Issue/PR及Privacy/Submission均为草稿，没有发送/发布。最终 Intel ZIP 由总控绑定最终payload、Host、所需模型、教程与许可；桌面旧0.3.25 ZIP不是本轮最终候选。

A4 只写 `official_muse/rc/packaging/` 及获准 ignored 构建产物，未执行Git add/commit/push，未操作生产数据/账号/系统权限，未新建子智能体或聊天。

公开维护材料：`PUBLIC_MAINTENANCE_ALLOWLIST.json` 是显式逐文件 allowlist，`PUBLIC_DELIVERY_README.md` 为公开入口。没有整体复制 packaging、raw logs、旧 main/bundle 或私人资料；未执行发布。

V10 clean runner准备：clean_room.py按实测cargo fetch --help支持的--target，自动从rustc -vV取nativehost，再fetch --locked --target nativehost，减少非交付平台依赖；report绑定cargo_fetch_target。当前script SHA e9e929bce66142a25d540dab4da8ed268b8a6fa7068c29737818960a261d335c，实际help/版本/AST证据CLEAN_ROOM_NATIVE_TARGET_PROOF.json；未改SDK/dependency/lock或复用74a4环境，等待总控新最终commit后才真正fresh执行。

069d fresh r2进展：新out/private/tmp/muse-clean-069dff5b-r2-20261005，实际checkout/9项公开输入与精确commit相等；新五archive恢复135.34秒及verify19.31秒/12000 PASS。实际native fetch正在进行，Host/card/Hub尚未编译。V13修补通知后按总控指令继续本次下载，保持069d输入绑定；阶段边界见CLEAN_ROOM_R2_PRECOMPILE_BOUNDARY.json，后续final-source重建/打包结论待总控指定，不能冒充V13 freshPASS。

最新R2终态：ownedCargo/rustc/runner都已退出，Host exit-2/445.61秒为明确space停止，原FAIL不改写。target148680KiB实际删除且无成品binary；pause后SDK verify12000 PASS，warm938b/5276严格签名/同SHA再验PASS。free删除时333070336→478339072 bytes，当前采样388505600，仍低于2GiB；没有其他可清大型owned旧target，源码/SDK/archive/newCargoHome/evidence/profiles/运行工具均未删。5991绑定guard因编译已开始而中止、没有checkout mutation；V14未冻结/未绑定/未打包，无final/ARM/双机通过声明。

最小新space授权已执行：只清旧/private/tmp/muse-clean-74a4bfca-r1-20261005/checkout/vendor还原副本及未完成cargo-home，先verify12000/lock3f1全同、五archive逐SHA一致、lsof两目录无引用。proof CLEAN_ROOM_R1_DUPLICATE_VENDOR_CARGO_REMOVAL.json含logical/du/hash/恢复命令/完整影响边界。free删除前1010245632→1761927168 bytes，净增751681536；所有r1源码/git/5archive/evidence及r2完整SDK/archive/CargoHome/currentapp工具保留。当前strict状态BLOCKED_CAPACITY，最终冻结b48618acef0ff291ad3dc23b09946b0b15fa4f2f与初始069d的SDK/两个helpers实际git archive81条记录全相同，final payload5092becd/sourceaf68b897；组合warm938b/5276明确≠cleanbuild，未启动新heavy。


2026-10-05当前交接以A4_HANDOFF_CURRENT.md为准：总控已准双部分包（92b1修复源码+旧938/527运行组合）。本历史长交接的旧“等待新Host才能打包”已被替代；旧Host缺陷/SDK3f、新源SDKda不得混绑。首轮ZIP已核验，等root新inventory HEAD重导出最终源；34公开材料冻结待root审阅。
