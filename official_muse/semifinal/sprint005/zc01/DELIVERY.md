# ZC01 SPRINT-005 交付

## Models 入口与严格连接探针（源码/包审计完成，live 未执行）

正式 R5 Host SHA256 `1eb1887b7e89e1f3adebd750a4afff278d3ad7a942f35ae89a04fa70103cf0f7` **确实包含** `os.ai-providers` 系统 pack。解析出的 `main.splash` 为 21763 bytes / `c6680953e01ca7c004b90dc774d00b20a38a67016317bf38a3ef04b1842e2267`，与展开 SDK 完全相同，包含 `run_test` 和 `llm.test`。`model_resource_audit.json` 是实际公开二进制的只读结果；没有读取运行时 profile、Secret、Keychain。此前裸文本 `run_test(p)`/`llm.test` 未命中不能说明缺包：App Hub pack 的文件内容是 Base64（Hub `crates/app-hub/src/pack.rs:27,119`）。本次已纠正该推断。

Root 报告的两次搜索 `ai-providers` / `models` 无结果，**不足以证明 UI 不存在**。SDK `crates/shell/src/shell/menu.rs:112,657,1021` 将叶 ID/alias 的 `-` 转为空格，而搜索输入仅 trim/lowercase；`ai-providers` 不会匹配 `AI providers` / `ai providers`。`models` 也没有对应别名（`shell/launcher.rs:112`）。Root 可在同一授权 UI 中核对 **`AI providers`、`providers` 或 `ai`**，并记录实际菜单子树；搜索只覆盖当前子树（menu.rs:667）。源码还提供 Start → Settings → AI providers（menu.rs:485）和系统聊天 OpenProviders → `launch_app("ai-providers")`（shell `lib.rs:4205`）。这些是现场源码路径，尚未由本站点击验证。若这些入口仍不存在，下一步核对 `clients::available_apps` → `system_card_apps` → `is_launchable`、`wm/launcher.hides` 与实际菜单 path；不用先补资源或重建 Host。

SDK `crates/shell/src/apps.rs:126` 从 App Hub 注册表产生短 ID；`catalog_visible/listed:658` 不隐藏 `ai-providers`。正式包与 ZC05 preflight-r1 的 **211 个 host-runtime 文件逐一名称/长度/SHA256 相同，无 symlink**。这是公开资源闭合的证据，不证明实际进程选择了哪条 Makepad resource 分支。资源路径分支位于 Makepad `platform/src/script/res.rs:396,414`；NSBundle / cwd / executable 的实际路径仍需 Root 的受控进程证据。本站没有做 GPU/布局改动。

### 可用的两条无工具连接检查

1. **指定 provider：内建 AI providers 的 Test。** 已内嵌脚本 `main.splash:143` 调 `host.request("llm.test", {id:p.id}, ...)`；host-service `lib.rs:1166` 按那个已配置 ID 取 provider，host 内部取 key，`probe.rs:16` 构造固定 `ping` / 单 user message；Anthropic/OpenAI `max_tokens:1`，Responses `max_output_tokens:16`。无 Calendar/Mail tools、Memory、聊天历史或用户文档，无 Agent turn。应由合法的 `os.ai-providers` scope 触发，不能把 `llm` 授给 Muse 或伪造系统 app。微小 token 上限可能被 provider 拒绝；HTTP 错误不能一概解释为凭据错误。本站未调用。
2. **Muse 已有 model capability：`model.complete` 固定合成 payload。** 文件 `model_connection_payload.json` 可原样作为 `host.request("model.complete", payload, callback)` 的 args；只含 `{probe:1, nonce:"SPRINT005-ZC01-CONNECTION-ONLY"}`，schema 要求完全相同的 JSON，禁止额外字段/URL。SDK `complete/mod.rs:196` 只接收 task/input/schema/class/allow_urls，拒绝 messages/tools/system/model/provider；`complete/wire.rs:26` 直接构造 system+单 user 的 HTTP 请求，**没有 tools 字段或工具执行器**。该路径不打开 Kernel Agent session，不附加 Memory/历史。不能走现有普通 Chat 包装（Main `muse_model_request` 的调用者可能附加历史）。payload 已准备，Root 拥有 UI 挂接/实际执行边界；本站未挂到 Main、未发送请求。

`model.complete` 按 class/primary/fallback 选择 provider，失败可回退，非 JSON/schema 错误可重试一次；它不公开实际 model ID，也不是保证只产生一个计费 HTTP 请求。若成功，仅证明 direct inference 的实际结果；不能证明恰为 MiniMax-M3、tool calling 或 Calendar full-chain。精确 MiniMax-M3 连通性优先用内建 Test 对相应已配置 ID。Root 提供的 family/model metadata 只作配置线索，本站未获取 ID/凭据。新的真实同意动作若需要人类手势，记录 `HUMAN_REQUIRED`，不推断授权已发生。

## 黑正文比较边界

Root 新报告：关闭生产 9278 与旧 fixture 后，original R5 / 同合成 state / 同 flags 单 Host 重启，PID27091/native715 已显示 Ocean 壁纸、chrome 和中文正文；证据在中央 `build/sprint005/entry-single-original-r5/`。这为 Root 的实际观察，本站未独立操作该 GUI。旧 fixture 当场未恢复、重启后恢复；prototype 首用 Deny 已持久化，暂不能把恢复归因于“只允许一个 Host”或 GPU。noGauss/Omarchy 此前未修复的比较保留。Root/ZC03 继续受控 GUI / WmDesk 比较。

## Agent 前置条件与 profile_unresolved

现场 Main SHA 仍为 `caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce`；其 3 个 `octos.session.open` 调用传 `{}`（1055/1380/1635），应用不选择 Kernel profile。正式 manifest `agent.profile: "read-only"` 是工具预设，不是 provider family/model，也不能据此声称显式 Calendar 写工具被禁用。它声明 tool_calling、ask_user_question 和 6 个 Calendar 工具。

合法链路的源码定位：SDK `app-peers/hosted.rs:56` 有效服务为声明∩支持∩Host grant；`_main` 是 hosted profile，system originator 为 `_main:api:octosense#system`。`ai-host/contained.rs:397` 由 Host 按 app/account/instance 打开 scoped conversation，应用不能选择 profile/workspace/provider。`app-peers/broker.rs:1695,1741` 在同一 link 先 session/open 再 peer/tools/register；注册失败不开始 turn。`host_tools/mod.rs:295` 做 admission、加载 granted owner executor、按 consent 提供声明，并传精确 generic_tools；`relay.rs:357` 跨 owner 需要 shareable 和已授予 tool，不由提示词创造权限。最终仍由 `os.calendar` 的 service 执行；Muse 不应直接调用 `calendar.*` 或改 owner 身份。

Kernel 源码真实 Git `b0759a57719fd35b3a2da1c5d969bc67538ed516`：`ui_protocol_transport.rs:10408` 返回 invalid_params / data.kind=`profile_unresolved`；10429 只认可 profile store、dynamic/static runtime，或没有 profile store 时的 `_main` 兼容分支。`session/open:23331` 在 cwd/sandbox 准备前检查 active profile；runtime 解析24675不会替未知 ID 换成别的 profile。**这是 session profile 前置错误，尚未到 Calendar Relay。** 已配置 `minimax-cn / MiniMax-M3` 不证明对应 Kernel profile 可解析，也不证明模型连接成功。Root 的下一条有用证据是原始失败的 method、code、data.kind、非敏感 profile_id 及进程/版本绑定；本站没有读取生产 profile 或修改其注册，不推测具体缺失 ID。

## 当前官方交付边界（2026-10-12 实际 HTTPS 核对）

组织方 HTML/JS 的实际 Vue render 文案及关联数据已读取，未操作浏览器。当前公告规定 **10/12 决赛用 10/9 冻结版本，10/17 只展示**；Rust 原生作品参评，不因不能进入 App Hub 扣分。公开 Apache 2.0 源码、固定版本、宿主/平台/启动说明、可运行作品、截图/视频和复现证据是交付材料；无需等待上架。公布的初赛四项各25分为任务价值、核心可用性、数据/失败真实性、复现材料；无 Agent/model 调用的任务价值最高13分。组织方链接 Muse Goals issue112，但未核验 Muse 实际冻结版本或后续修复例外。本次 sprint 修复不能自动视为已被决赛接受。来源与获取方法/hash见 `organizer_findings.json`。[组织方规则](https://create.gosim.org/agenticapp26/)

| 路线 | 最短可运行交付 | 本项目边界 |
|---|---|---|
| Native Rust + OctoScript 集成宿主 | 精确 `.app` / 源码及可构建 Host、Kernel、framework locks/patches / 启动与合成演示步骤 | 当前配对 R5 是此路线；需明确额外 Host 接口和源码绑定。不能仅交 Splash 包期待 vanilla Host 等价执行。 |
| App Hub script/card | 根目录 bundle、manifest/listing/artwork/截图，兼容宿主可用的 API；source tag+GitHub-attested pack，再独立审核 | bundle 不装 native Rust/ dylib；`os.*` 仅系统。新增 native/system 功能随 Shell release，不由资源 copy 或 store grant 创造。 |
| Rust Wasm | 支持宿主上的 core/component `fns/*.wasm`，相应 ABI/host API/imports/limits | 是受限计算/公开 host imports 路线，不能借此取得 native Calendar owner 或 Keychain。当前任务未改走 Wasm。 |

这些交付路径来自 [App Hub DEVELOPMENT](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/386359153ed6377b5f047bd9ed2767a6a2ac2bc7/docs/DEVELOPMENT.md) 和 [官方 Rust 指南](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/RUST.md)。当前 Desktop RC6/source `f9f6fea9` 已在官方 App Flow README 公告；官方 Mac 下载为 Apple silicon，其平台验收不能移用于本机 Intel R5，也未在本站下载/升级。[官方状态](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/d0344682df7c52ae5a79055f20f148f542d115e0/README.md)

App Hub 正式发布使用 GitHub-attested publisher proof：新版本不可移动 tag，保留精确 commit/workflow/pack/receipt，验证最终下载字节；issue申请、人工 review 和管理员 catalog 发布是独立步骤。本地 legacy Ed25519 rehearsal、gate pass、release workflow 都不是正式上架。现行 capability/network 声明是披露；实际 identity、account/device consent、reviewed inter-app tools、兼容版本和限额仍执行，不能把新版文档直接套作旧 R5 的权限结果。[发布规则](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/386359153ed6377b5f047bd9ed2767a6a2ac2bc7/docs/PUBLISHING.md) · [提交流程](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/386359153ed6377b5f047bd9ed2767a6a2ac2bc7/docs/SUBMITTING.md)

### 配对 Host 与官方 vanilla 的实际差异

`paired_source_audit.json` 对 preparation 声明 SDK `4ccf8e06` 的 **10 个相关文件**做 upstream 原始字节比对：Calendar service/tools、shell host_tools/mod、app-peers/broker 4 个文件不同；relay、contained、hosted、AI providers script、model.complete mod/wire 6 个相同。这不是全源码一致性证明。固定 SDK、当前 SDK main `f0754134` 和 RC6 的 Calendar tools 都包含 update_event，却**没有 get_event**；本地配对源码增加 get_event（精确列表见 `calendar_tool_surface_comparison.json`）。所以可由 owner 读稳定 ID 的 Muse 路径仍需配对 Host，不宣称 vanilla兼容。

SDK `Cargo.lock` SHA `5b58c5f5…`；Makepad base `32d6415f` 的 aggregate+stacked **32 个 patch 文件 hash 全部与 lock 一致**，native runtime lock为 `33dea2f1`；`sdk_lock_audit.json` 保存现场结果。preparation.json 自身标 `PREPARED_NOT_BUILT`，不能当已运行 Host receipt；展开 SDK 的 git继承 Muse 根目录，也不是 SDK upstream revision。正式 Host `1eb1887b…` 的脚本 pack已独立核对，但全部编译 Rust closure→该 Host 的构建 provenance 尚未由本站证明。Root需绑定实际正式构建的 Cargo/features/生成表/patches 与 binary hash；不要误用另一次 R5 diagnostic build 的 source hash。

最新官方 refs/文档 hash记录在 `official_upstream_heads.json` / `official_document_sources.json`。GitHub API曾403 rate limit，改用公开 git/HTML/immutable raw；App Flow git SSL timeout，用公开 currentOid并以该commit取README。现场 issue112标题仍rc10，但未读取/确认所有提交评论或判定冻结版本，未视为 catalog approval。公开发布、Tag、提交issue、更新Main/Host均未执行。

## ZC05 专属 Calendar 独立读回

`read_calendar_store.py` 可直接用系统 Python3，无 Cargo/Kernel/GUI/model/subprocess。它读 actual owner store 字节、返回 hash/mtime/原始 event 字段；明确输出 `service_api_called:false` / `fixture_only:true`。这是独立文件证据，**不是官方 RPC、Agent receipt、GUI动作或 full-chain PASS**。路径依据 Hub `cardapp.rs:75` 的 `.host` 和 Calendar `lib.rs:181` 的 `calendar/events.json`。

仅接受中央 `build/sprint005/zc05-<case>/state`，拒绝生产/formal/R5 root、`..`、所有路径组件/文件 symlink。状态根及 `apps/.host` 均须有 Root/ZC05 明确创建的 `FIXTURE_ONLY`；状态根须有 `SPRINT005_CALENDAR_READBACK.json`，字段按 example，case_name对应路径，nonce对应合成标题。任何记录不以 `SPRINT005-ZC05-<nonce>-` 开头、重复ID/JSON key、损坏/缺失/超限文件均拒绝；缺失文件不能当“已删除”。它不创建 marker/spec，不写 Calendar 数据，不自动修复。

使用顺序：Root/ZC05在专属新 fixture准备两处marker及spec（初始stable_ids空）；GUI创建后用 events发现仅该fixture的ID；把真实ID列入spec白名单，然后以ID回读改期/冲突/删除/重启前后。删除后保留ID白名单，真实空数组才返回found:false。标题修改仍保留nonce前缀。每轮独立nonce/spec，源码/包/Host/状态/PID/动作回执仍由GUI方绑定。此函数的 events只作原始store快照，拒绝from/to/limit，不仿造官方筛选/排序。

```sh
python3 read_calendar_store.py --state-root '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/sprint005/zc05-calendar-r1/state' <<'JSON'
{"owner":"os.calendar","method":"events","args":{}}
JSON
python3 read_calendar_store.py --state-root '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/sprint005/zc05-calendar-r1/state' --id ACTUAL_BOUND_ID
```

运行前cd本ZC01目录；以上是协议示例，本站未在Root数据运行。2026-10-12 `python3 -m unittest -v test_read_calendar_store` **13/13 fixture tests PASS**；包括精确ID创建/改期/删除后重读、未绑定ID、生产root在open前拒绝、两marker/spec、symlink文件/目录、非合成/重复记录、腐败/缺失store、FIFO/超限文件/请求及读前后bytes/mtime/inode不变。`calendar_reader_tests.log`保留实际输出。该CRUD由测试写fixture驱动，不是三轮GUI/Host重启；尚无本站live Calendar或真实模型结果。旧NIGHT004 helper依赖的现场binary不存在，已保留旧源码/证据，没有假装复用成功。

## 当前交接

Models里程碑提交 `62f28817`。本站范围内三项已准备并验证，Root仍需执行合法模型检查、确认profile错误实际绑定、完成ZC05三轮GUI及正式Host完整源码receipt/比赛冻结边界。只改本namespace；本地提交，不push，不对其他聊天发消息。

## 后续：正式 Host 构建绑定与最小 Native 交付

Root已接收635ca8d1，并报告实际GUI找到providers：内建TestConnection向loopback产生1条model.request、Connected 3ms。这是实际fixture网络请求，不是MiniMax-M3推理或Agent工具链。本节由Root提供的新现场更新，本站没有操作GUI。Root新Main源码已只读核为 `947c52915c507f9a7a7a896c554b43f1c1e0a9ec11bee490bed5304d054b642b`；rc8/catalog5仍准备中。原R5/生产资料保留。两入口同state单Host重初始化后Main可见、跨profile互斥26签名stub检查通过均为Root结果；根因仍UNKNOWN，本站不改GPU。

**正式Host的编译产物来源现已绑定。** `build_binding_r1/bind_formal_host.py`只读当前正式 `1eb1887b…`；去除最终签名load command/签名尾部并恢复LINKEDIT大小的操作仅在内存中完成。还原后的124155120 bytes SHA精确为 **`a9fc8ca3f39a626bb1bc1fae3cb99b359f5a07c7c3c50f45cd73b21d885c397a`**，与 `official_muse/integrated_release/evidence/night004-rc7-preparation/host/host-build-receipt.json`完全相同。正式Mach-O UUID为 `72569da9-f7c8-3220-883e-2056014001ee`，16个file-backed sections的hash已保存。它不是较早History Host的30d4/ec83，也不是R3/R5诊断Host。结果 `formal-host-binding.json` 标 `BINARY_TO_BUILD_RECEIPT_BOUND`；没有写出、重签或执行二进制。3/3合成Mach-O测试通过，日志binding-tests.txt。可用如下只读命令复核：

```sh
python3 build_binding_r1/bind_formal_host.py \
  --binary '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/muse-integrated-0.4.0-rc7-formal-r3/Muse.app/Contents/Resources/host-runtime/muse-host' \
  --receipt '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/integrated_release/evidence/night004-rc7-preparation/host/host-build-receipt.json'
```

**完整源码重建仍有具体缺口。** 上述真实receipt记录release/offline/locked、no-default-features、`app-hub,octos-core,app-muse-native-prototype`、lock5b58…和324.61s构建成功；builder调用SDKpackage_env生成apple_bundle、package dir`.`、deployment11.0、strip debuginfo、路径remap，然后独立签名。它没有记录当时全部path-source字节、继承flags/toolchain/linker/SDK和生成表。现场原unsigned文件已不在旧输出路径；当前完整SDK也不能被追认成旧源码快照。较早History的17文件指纹目前10同7漂移，但那是History checkpoint，不是a9fc正式构建的前置fingerprint。

本轮实际执行了 **cargo tree，未执行cargo build**：offline/locked、相同features、x86_64、normal+build边，target显式指向本站 `.repro-target`，没有操作Root target，lock仍5b58…。用已有metadata-r11按tree的source路径/URI映射，解析到 **575个精确package ID，0未映射**（不能只按name/version：registry和Makepad vendor有同名版本）。`current-source-graph.json`记录每个manifest SHA，`current-cargo-tree.txt`保存实际输出；这是当前图，不是旧正式构建图。当前rustc1.98.1/LLVM22.1.8、Apple clang16.0.0、SDK15.2已读取，不能代替旧环境证明。`reproduction-recipe-and-gaps.json`明确区分已绑定binary与缺失的历史freeze。没有拿新编译代替旧正式Host，也没有启动candidate。

最小交付核对：

| 项目 | 已有证据 | 剩余最小差距 |
|---|---|---|
| 集成Native入口 | 配对RustHost1eb→实际a9fc构建receipt；正式R5资源和Kernel保留 | 公共、可复建的精确SDK/Hub/framework/path-source冻结内容或完整base+deltas，以及旧环境/生成输入；一次隔离重建绑定到unsigned hash后再独立签名。SHA清单不能替代源文件。 |
| Muse应用版本 | R5/caa99…保底；新Main947…由Root准备rc8 | 固定rc8 commit/tag、bundle/manifest/catalog/Host/Kernel/launcher完整身份；新Main与启动器变化必须绑定到新证据，旧R5验收范围保留。 |
| 可核验业务演示 | providers入口及loopback Test已实点；已有合成证据 | 真实provider推理/合法Agent注册、ZC05三轮和当前candidate的结果核验；loopback和签名stub不能当真实M3/业务动作。 |
| Native参评材料 | 官方明确Native参评、不能进Hub不扣分、无需先上架 | 描述为Muse Splash + 配对Rust扩展；提交可运行宿主、公开Apache2源码、固定版本、支持平台/启动说明、截图/视频/复现步骤。Native路线不以伪装成store包解决宿主差异。 |
| 时间口径 | 用户经Root确认Oct13截止；主办页实际JS复查仍原hash4c454…、10/9冻结/10/12决赛文案仍在 | 同时保留两份依据，继续按用户Oct13工作；不替用户改截止、不推断延期例外或失格。`deadline-source-recheck.json`留获取方法/hash。 |

普通dev准备与本地提交可继续；正式发布、Tag、issue更新、catalog管理员操作未授权给本站，也未执行。由于历史源码/环境未冻结，当前结果不能标`FULL_SOURCE_REPRODUCED`；Root可将以上缺口作为Native交付的明确待验项，不能用旧History/source checkpoint或相同Cargo.lock填补。
