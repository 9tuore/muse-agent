# Muse 统一候选 0.4.0-rc15

NIGHT-006 的 rc9 基于官方 desktop-v0.1.0-rc.6 源码和 Muse 兼容补丁，统一构建 Intel Host、配套 Kernel、签名界面及本地模型。旧 rc8/rc7/R5 与用户资料保留；旧版本或组件测试不自动计入本候选三轮，也不代表生产账号全链通过。当前运行、候选身份和证据以 [CURRENT_STATE](../../MUSE_HANDOFF/CURRENT_STATE.md) 与 [三轮报告](../../MUSE_USER_ACCEPTANCE_3ROUNDS_REPORT.md) 为准。

## 唯一启动方法

双击 `Muse.app`，或使用仓库和成品中的同一脚本：

```sh
./official_muse/integrated_release/launch_muse.sh '/absolute/path/Muse.app'
```

脚本通过 `/usr/bin/open -n -W` 进入应用的 `CFBundleExecutable=Launcher`。外层 shell 在自己的 Contents 中定位资源，等待签名检查和 guardian 就绪，然后由原 PID 直接 exec `Contents/Resources/host-runtime/muse-host`。保留已验证的 WorkBuddy 启动身份及外层 shell，显示名称为 Muse，不直接运行裸 Host。

Host 默认接收实际 SDK 支持的参数：

```text
--remote=9696 --test-action launch-apphub --test-action launch-hub:muse-goals
```

这会打开 App Hub 与已安装的完整 Muse。首次安装/更新仍通过正常 App Hub 权限流程；Launcher 不写入安装库或批准权限。只读 native prototype 不是完整 Muse 的入口。额外调用者参数不能替换默认 Host argv。

启动器以同用户临时目录的文件锁防止跨资料同时启动，并从可执行文件路径识别旧 packaged Muse Host。已有实例会被激活并拒绝第二个 Host；正常退出后再打开另一份包。此措施对应本机曾出现的并发初始化黑主体，原 GPU 根因仍未确定。识别范围是 `Contents/Resources/host-runtime/muse-host`，不声称控制其他应用。

## 资料与模型

默认资料为 `Muse.app` 同级的 `Muse Data`：`shell/`、`apps/`、`kernel/.octos/`、`rinx/`、`config/`、`data/`、`cache/`、`logs/`。`package_app.py --state-root` 只记录已有绝对资料根，不读取或复制生产目录。运行时优先 `MUSE_INTEGRATED_STATE`，然后包内 state_root，最后默认路径。HOME 保持原值；不迁移凭据或 profile。

测试可设置 `MUSE_INTEGRATED_REMOTE` 为单独端口；生产默认 9696。`--check` 检查签名/资源；`--gpt-check` 仅检查包与原生 config.llm 的提供方 metadata。配置检查通过不证明凭据、模型实调或工具操作成功。

产品使用 `--model-mode hybrid --model-source ...`，携带 Qwen2.5-0.5B 基础本地服务。已有 Native profile 原样保留，包括 MiniMax 等云端路由；只在 profile 完全不存在的全新资料目录创建无凭证的 local 主模型配置，指向自己启动的 loopback Qwen 服务。存在但损坏的 profile 不覆盖。guardian 只管理自己的模型进程，不迁移 Keychain，也不发付费轮询。模型服务就绪与真实推理、工具调用分别验收；小型离线模型不等于已验证的云端协同。宿主 AppsMenu 搜索 `providers` 可打开原生 AI providers 页面。

GPT 专用开发包可选 `--model-mode gpt` 并省略 `--model-source`；`--models` 仅抑制 Qwen，仍使用相同正式入口。开发 Agent 使用 GPT 不意味着替换产品已有 MiniMax 配置。

## 构建与打包

先用 `prepare_official_host.py --sdk` 核对官方 rc.6 源码及兼容补丁，再使用 `build_official_host.py --sdk ... --work ... --phase {check,tests,host,kernel,hub} --offline` 逐阶段构建。实际 features 为 `app-hub,octos-core`，保留官方 `.cargo/config.toml`，打入真实 Mail/Calendar 系统应用。脚本记录 tag、各源码 revision、补丁 SHA、锁文件与产物 SHA。完整界面的有界冷加载补丁也必须纳入统一源码；不能混用旧 Host。

完整界面还依赖受限的 `fs.sha256` / `fs.sha256_file` 原生接口。rc.6 适配将这两个只读绑定与有界冷加载补丁一起锁定并重放；原生摘要测试覆盖标准向量、中文及文件访问边界。仅旧 VM fixture 通过无法证明最新 GUI 宿主具备这些方法，仍须真实检验聊天和记忆保存。

`prepare_bundle.py` 从 `official_muse/app/source/main.splash` 创建新的可读/压缩 bundle；根 `bundle/` 当前保留历史 rc17，不能混用版本。签名后不修改清单或文件；需要修复时生成新候选。

`package_app.py` 输入显式 SDK、Host、Kernel receipt、签名 mirror 及公共本地模型目录；`--licenses` 加入收集的第三方声明。若 Host 旁存在 `.release-identity.json`，先核对其 SHA，再把源版本与输入 SHA 写入打包记录；签名后的实际 SHA 单列。输出新目录与 `Muse.app`、`PACKAGE.json`、`HOST_RESOURCES.json`、`launch_muse.sh`。普通模式按同一 features 的 Cargo closure 收集资源，并由官方 staging helper 为签名后的相同 Kernel revision 重建 receipt。原输入不改。

```sh
: "${MUSE_SDK:?explicit SDK preparation tree}"
: "${MUSE_HOST:?built Host executable}"
: "${MUSE_KERNEL:?pinned Kernel executable}"
: "${MUSE_KERNEL_RECEIPT:?matching public receipt}"
: "${MUSE_MIRROR:?new signed rc9 mirror}"
: "${MUSE_LOCAL_MODEL:?public model directory}"
: "${MUSE_OUTPUT:?new output directory}"
python3 official_muse/integrated_release/package_app.py \
  --sdk "$MUSE_SDK" --host "$MUSE_HOST" \
  --kernel "$MUSE_KERNEL" --kernel-receipt "$MUSE_KERNEL_RECEIPT" \
  --mirror "$MUSE_MIRROR" --model-mode hybrid \
  --model-source "$MUSE_LOCAL_MODEL" --out "$MUSE_OUTPUT"
```

可选 `--apfs-clone` 在同卷 APFS 请求独立 CoW 副本，不把资源链接回原工作目录。可选 `--paired-host-app` 要求真实内层 `.app/Contents/MacOS/{octosense,octos-kernel}` 和 `Contents/Resources`，验证源 pair 并复用资源/已签 Kernel；**不能传入当前外层 Muse.app**。Host 在 `.app` 外重新签名为 standalone，再复制到 host-runtime，以去除旧特殊资源封印；最终 Host SHA 可能改变，必须记录签名后实际值。原 pair 不改。

成品是本机 ad-hoc 签名，不是 Developer ID、公证或公开发行。编译/打包成功的状态为 `PACKAGED_NOT_RUNTIME_VERIFIED`；随后必须实际 LaunchServices 打开、原生窗口显示、动态身份和业务读回验证。

## 签名目录与官方接口

`muse_local_catalog.rs` 只接受 muse-goals `0.4.0-rc15`，使用原 Hub gate、packer 和签名 verifier；catalog sequence 为 16。仅为确切配套 Host 加入六个 Calendar offer：events、get_event、add_event、update_event、remove_event、notify，其他应用的默认上限不变。本地目录通过是 `ADMITTED_LOCAL_PAIRED_HOST_ONLY`，不能写成官方公开 App Hub 上架。

将 helper 放在对应 Hub 的 `crates/app-hub/examples/`，按实际 SDK workspace 锁定依赖构建。六个参数依次为 BUNDLE、NEW_MIRROR、WORKING_KEY、CERTIFICATE_FILE、ANCHOR_PUBLIC_FILE、SOURCE_COMMIT。新目录不可已存在，提交号须完整；私钥只作为本机签名工具输入，不作为成品、日志或 Git 输入。使用官方 Hub stamp/sign-manifest 后，再运行 helper 准入与目录验签。

Calendar 使用真正的内置 owner 及合法 App Agent/Relay，Muse 不能冒用 os.calendar 系统身份。session.open → turn.start(trigger:app) → session.history 的已持久请求和工具回执须精确匹配，同 ID 操作需要读回。模型文字、窗口和候选卡出现都不能作为外部成功。当前 get_event 依赖配套 Host 的待审补丁；vanilla 接口没有该扩展。

Mail 保留官方 account、draft、review、send 状态与 UNKNOWN 不重发恢复。SPRINT-005 专用 CA Host 只用于双 marker、file-vault、127.0.0.1 的合成 TLS GUI 测试，默认 WebPKI/证书验证不关闭，生产 R5 Host 不加这个覆盖。其模拟输运和审批不能写成生产 SMTP、真实模型或私人日历验收。

## 必要检查与 GitHub

本机 `python3 -m unittest discover -s official_muse/integrated_release -p "test_*.py"` 执行启动器和打包 fixture。运行前须正常退出 Muse，避免测试与真实 Host 的单实例锁冲突。NIGHT-006 首次含锁冲突的失败证据保留；退出 Host 后原 31 项全部通过，新增源版本收据防混用后 6 项打包检查通过。以上不是真实 GUI、账号、模型或日历验收。

`.github/workflows/muse-launcher.yml` 在此开发分支相关变更或手动运行时，使用相同 launcher 源码和脚本检查，依次运行启动器与打包 fixture。它不发布成品、不使用账号秘密、不请求模型。远端实际执行结果需独立核对，不能用本机结果代替；真实 Intel Host GUI 和同候选三轮另有原生证据。
