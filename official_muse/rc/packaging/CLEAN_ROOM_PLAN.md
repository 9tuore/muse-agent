# 最终 commit 清洁构建入口

状态：**74A4_INTERRUPTED_BEFORE_HEAVY_BUILD_WAIT_V10**。总控明确要求停止本轮74a4会话，以修补V9应用boot预算失败，随后提供新的最终提交。真实新目录/private/tmp/muse-clean-74a4bfca-r1-20261005已完成精确checkout、五个官方archive fresh恢复81.44秒及SDK verify12000文件PASS；cargo-fetch运行776.04秒并记录TLS/连接超时重试，在总控停止请求后仅给本轮owned cargo发送SIGINT（exit=-2），runner实际exit1/原报告FAIL原样保留。Host/card/Hub编译未开始，target未创建，没有完整clean-build PASS。`CLEAN_ROOM_R1_FINAL_AUDIT.json`明确区分受控停止、网络日志和未执行阶段。全部新source/archive/CargoHome/日志保留，下一次必须新out、新checkout、新SDK、新CargoHome和新target，不能把本轮目录改版或复用为严格fresh。

## 输入和运行

从原 Git 仓库根目录运行，填入总控认可的完整 40/64 位 commit SHA，不用 HEAD、branch 或未提交文件：

```sh
python3 official_muse/rc/packaging/clean_room.py \
  --source . \
  --commit <FINAL_CANDIDATE_COMMIT> \
  --directory ../muse-clean-<commit-short>
```

如果冻结 bundle 带现有开发身份的签名，增加 `--publisher-key <publisher-id>=<64位十六进制公开公钥>`。该参数可重复，每项原样绑定 `CLEAN_REPRODUCIBILITY_REPORT.json` 与实际 `hub-check-final` command。只传公开身份，不读取私钥，不重签 bundle；开发身份的 check 不表示正式 publisher 或 key continuity 已获确认。

`--source .` 只在初始 fetch 时读取该 Git 仓库已经提交的对象；新目录建立独立 shallow checkout，没有 worktree 引用、hardlink target、旧 vendor 或未提交文件依赖。也可传公开无凭据 HTTPS Git URL。源码位置作为一次性参数，构建依赖不包含原机器硬编码绝对路径。新目录必须不存在，脚本拒绝复用或清空旧目录。

脚本依次执行：精确 commit fetch/checkout → 工具版本 → 官方固定 archive bootstrap + overlays → SDK verify → 新 Cargo home 依赖恢复 → 新 target Host release/完整 `.app` → card-host release/独立 `.app` → Hub → 再次 SDK verify → 原字节 Muse bundle+Hub CLI → 带显式公开身份参数的本地扩展 Hub check。Host 三组资源、card-host 的 makepad_widgets 资源及 SDK license 分别打包，每个 app 进行 ad hoc 严格验签；Host 在 card-host 编译前打包，避免共用 target 的 Info.plist 被后一构建覆盖。

相关入口：`clean_room.py`、`package_clean_host.py`。后者只接收该新 checkout 内的 SDK/target/output；不调用本轮硬编码诊断缓存路径的 build_host/resume_host/package_host_candidate。

## 隔离与验收

- CARGO_HOME 和 CARGO_TARGET_DIR 都是新目录内新建位置；Cargo 若能从 checkout 外父目录找到 `.cargo/config` 或 `config.toml`，脚本拒绝继续，避免继承机器专有配置。只允许最终源码树内的配置，不读 credentials 或旧编译 target。Git 全局/系统配置禁用，交互凭据提示关闭；HOME 原值仅供已安装 rustup/toolchain 和系统工具使用，不复制用户资料。
- target 位于 checkout 的 `build/`，不放进 vendor；bootstrap 的 tree_digest 会计算 vendor 内所有文件，向 vendor 添加 target 会破坏 12,000 文件的锁定树。
- 所有 build/fetch 使用 `--locked`；离线编译前先从官方来源恢复依赖。前后 Cargo.lock SHA 必须一致，最后 tracked source 必须无变化。
- bundle 从最终 commit 复制，脚本不 stamp、改 listing、重新签 manifest 或生成 publisher 私钥。最终源码若没有正确 integrity，check 应保留 FAIL，交总控修复后形成新最终 commit，再从另一全新目录重试。
- 当前 check 是本地 Calendar 扩展 Hub，不代表当前未修改官方 Hub 已接受。首投 unsigned 本地检查与正式 publisher continuity/signature 的检查分开。若最终 manifest 已签名，仍需总控提供已提交的公开验证身份材料；不要借用私人配置。
- 输出与每一步原始日志都在新目录 `evidence/`。任何 FAIL 不覆盖；重试使用另一新目录。输出 `CLEAN_REPRODUCIBILITY_REPORT.json/.md`，PASS 只表示该源码的构建/打包/本地准入，UI 与 T01–T20 仍另验。
- 这是最终提交源码的可重建性验证，尚未实现逐字节 deterministic build。新的源码绝对位置、资源包装身份和 ad hoc 签名可能使 SHA 与暖构建不同；`clean-host.json` / `clean-card.json` 记录各自签前/签后 SHA。clean-room app 使用独立本地 Bundle ID，不覆盖暖构建 app，也不把旧 Host 的 live 结果自动转给新 SHA；最终运行/截图/packet tuple 由总控选择并绑定。
- 不启动 GUI、不申请系统权限、不读写真实 Calendar、不使用邮箱/模型账号、不发信、不发布、不 push。

## 磁盘与工具

已实测 SDK 恢复逻辑 621,311,483 bytes，分配约 620.5 MiB；本輪复用 SDK 的 archive 恢复 68.05 秒。Host 暖缓存中断后续跑 769.30 秒成功，**不是**新 cache 时长预测。

建议开始前至少 **8 GiB 可用空间，优先 12 GiB**。这是容量规划值：新 SDK/archive、Cargo registry/git sources、Host/card-host/Hub target、中间链接文件、应用资源及失败证据均占空间；不承诺实际峰值已测。下载全部 workspace 依赖可能使占用进一步增长。每阶段记录运行时长、可用空间和原始日志 SHA，禁止为了继续构建擅删旧证据/历史/生产数据。

环境：macOS、Python 3、已安装 Rust/Cargo、Xcode Command Line Tools 与 SDK。当前暖构建是 x86_64 / rustc 1.98.1 / macOS SDK 15.2；ARM 尚未在 A4 实编。Calendar 首次完整权限请求的当前 native 分支要求 macOS 14+，二进制 Mach-O 的最低版本字段不能代替实际全链兼容验收。

官方 archive 网络下载尚未在这套新脚本执行。此前 GitHub API 限流和大 archive 取回失败记录已保留；当前暖复核使用精确官方重建 archive cache。clean-room 不回退该旧 cache，失败时如需官方 Git 对象重建，应在新目录进行并保留官方 commit/blob 校验；须由总控明确加入最终源码后再测。

## V10冻结前的最小fetch改进

已实际验证cargo fetch --help的--target支持，以及rustc -vV host=x86_64-apple-darwin。owned runner现动态取nativehost并用于两个cargo fetch --locked --target nativehost，tool/version日志和最终报告均绑定该host；不变更依赖、锁、bootstrap或隔离标准。证据CLEAN_ROOM_NATIVE_TARGET_PROOF.json，脚本SHA e9e929bce66142a25d540dab4da8ed268b8a6fa7068c29737818960a261d335c。尚未声称此改进的新依赖下载/构建已通过；需进入总控新最终commit后，在另一全新out实跑。

## 069d R2实际终态

SDK fresh恢复135.34秒、verify19.31秒/12000 PASS，native依赖fetch627.74及4.48秒成功。Host开始后已不满足5991编译前绑定条件，保持069d输入；按总控disk emergency仅停本轮compile，Host445.61秒exit-2，runner原FAIL保留。owned incomplete target148680KiB已无占用删除，new SDK/archive/CargoHome和证据保留；停止后verify12000 PASS。没有Host/card/Hub成品、final-source包或完整clean PASS；当前空间未达2GiB且无其他可删owned大target，不能继续heavy构建，V14最终边界另等总控。详情CLEAN_ROOM_R2_FINAL_AUDIT.json。
