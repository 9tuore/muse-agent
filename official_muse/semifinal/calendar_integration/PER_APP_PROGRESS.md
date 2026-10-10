# 第二阶段：Store per-app ceiling

2026-10-10。第一阶段文件保持。BLOCKED 未解除。

## 中央串行构建请求（尚未启动）

目标是隔离副本中的 `octosense-app-hub --test per_app_offer`，真实 `Store::install_staged` / `may_run` / `prepare_launch` / `validate_prepared_launch`，不是 Makepad/Shell/Calendar 大构建。命令计划：`CARGO_BUILD_JOBS=1 cargo test --offline --manifest-path build/calendar-per-app-store-r2/Cargo.toml --target-dir build/official-hub-rc2-target -p octosense-app-hub --test per_app_offer -- --test-threads=1`。

现场已有 target 5.6GiB，Data 可用约14GiB。估计单job重编 Hub 与链接此测试增量约0.2–1GiB、1–5分钟；只是预算，未经构建测量。若依赖缓存未命中可能更多；不得自动转为下载或全workspace构建。准备脚本仅拷贝 contract/policy/hub 小源码、复用固定 l0 源与 lock，所有新增输出都在 ignored build。

没有抢跑 Cargo；待中央串行调度。完整 Shell、GUI、签名商店 v2 实机准入仍另需调度。

## 实际原 Store 定位与最小提案

固定 Hub95e4831 的 `crates/app-hub/src/client.rs`：Store 在114定义，180构造，460安装时用 staged manifest/digest，541在 `verify_release_bundle` 对已安装/快照启动重验时使用 `self.limits`。没有要求这些 limits 必须全局相同的接口约束，HostLimits 实际可 Clone；可在这两个已有 resolve 调用点按已核验 Entry.app_id 选择仅追加一个工具的副本。

`hub-per-app-store-offer.patch` 对实际 Store 增加默认空的 `BTreeMap<app_id, tool>` 与 `set_agent_tool_offer(id, Option<tool>)`。设置前要求该ID位于已接受catalog、尚未withdrawn、manifest有认证方案，调用现有 verify_manifest/PublisherKeys 验证认证；os.* 和原reserved ID拒绝。None撤销这个Store实例里的追加项。安装及启动仍原顺序验证catalog、身份/manifest相同、签名及摘要，追加仅作用于 `offered_tools`；其他App及其他limits字段不变。

另在已有 `validate_prepared_launch` 签名检查之后用当前 per-app ceiling 重做 policy resolve，防止同实例撤销后早先的 PreparedLaunch继续通过。此检查不是重置预算，不新建Runtime或存储；现有snapshot字节策略保持。

这是**Store API提案**，还未接 AppStore/CardApp/Shell。第一阶段全局offer补丁保留作历史比较，**不能和本提案叠加**，否则另一个App仍会继承全局 ceiling。正式宿主需在各个Store构造/接受catalog后从唯一受控配置装入同一 per-app offer；该后续接线尚未编写/验证，避免先创造第二套配置与授权系统。

Store clone按原结构复制配置：本实例撤销不会神奇更新旧clone或正在运行的session。宿主应将撤销传给所有存活Store，且沿原实时 consent/admission 重新检查；不能称本API实现跨实例或运行中即时撤销。已准备启动的撤销用例只覆盖同Store实例。Offer是上限，未请求工具不会进入policy，更不代替本人consent、Relay grant、共享声明、可信手势或审批。

## 真实 API 正反向测试交付（未编译/未执行）

`per_app_offer_tests.rs` 复用官方 `tests/common/mod.rs::Fixture`、真实签名HubKey/Catalog/manifest、默认require_signature=true，调用原Store API。八个测试覆盖：默认拒绝与单App准入/另一个App拒绝；额外remove工具拒绝；manifest未请求不授予；撤销后may_run及已准备launch拒绝；改动bundle摘要拒绝；错误publisher/缺签名在已有offer下仍拒绝；已签名catalog撤回；未知和reserved ID拒绝。fixture密钥只在进程内生成，不输出/记录。不是官方v2商店身份或真实用户授权证据。

准备脚本 `prepare_per_app_patch.py` 只写本目录patch/identity与ignored build隔离副本；源码副本约1.3MiB。`build/calendar-per-app-store-r2` 是最终准备对象；初版r1保留，不是执行结果。原Hub checkout没改。

实际检查：补丁生成成功；`git apply --check --directory=.local-state/hub-contract-sdk/app-hub .../hub-per-app-store-offer.patch` 成功；Python脚本语法编译通过。`rustfmt --check` 失败，因为stable-x86_64-apple-darwin没有rustfmt组件，未安装任何组件。**未运行Cargo，因此八测试既不能称通过，也不能称已验证编译。** 第一阶段3 Rust/11静态结果不能移作本阶段证明。

完整编译后如失败，按真实输出修复隔离副本与补丁。若资源超出上述请求，不扩大为Shell/全workspace构建。当前最小Store路径存在，但其真实编译/准入与后续宿主接线待中央串行执行。

## r2 中央执行失败与 r3 fixture 修正

中央实际运行 `build/calendar-per-app-store-r2/test-r1.log`：编译34.08秒，八项测试7过1失败；第55行只在错误中寻找“does not offer”，未输出实际错误，因此该行的默认拒绝及后续双App隔离不能算通过。

为只读定位，使用中央已编好的 r2 Hub/Policy rlib，直接 rustc 链接一个小诊断 probe（未重编Hub、未启动Cargo、未跑完整测试）。它使用原r2 Harness调用真实 Store，实际输出：`conflicting public keys for publisher key "publisher-one"`。源码链证实：官方 Fixture每次独立生成publisher密钥，却使用同一个 `publisher-one` key ID；同一个catalog有两个不同公钥登记到该ID，原 PublisherKeys::verify 明确拒绝冲突。此安全检查正确，根因是fixture多publisher配置错误，不是per-app实现缺陷。诊断源码/编译及原始输出在 `build/calendar-per-app-store-diagnostic/`，r2完整失败log保持原样。

r3只修正测试夹具：每App仍独立生成publisher密钥，Agent manifest重签到独立的 `publisher-fixture-<app ID>`，catalog的publisher ID及安装时显式PublisherKeys一致；原Fixture文件和Store代码不修改。双App用例额外断言publisher ID与公钥都不同，原“does not offer”严格断言保留，新增错误输出，不接受任意错误为通过。不是改成同publisher或放宽签名规则。

`build/calendar-per-app-store-r3` 已准备，补丁apply-check通过；r2/r3 Store源码SHA相同，记录 `r3-fixture-correction.json`。原r2补丁/metadata另存本目录 `hub-per-app-store-offer-r2.patch` / `per-app-preparation-r2.json`。最新通用补丁为r3（SHA `bbf9b1a2066074b3f44299208f1dafaa16ae5ecaa156c0eb69eeb456bb1260c1`）。**r3未跑Cargo或八项测试，等待中央复跑，不声称8/8或正式接通。**

中央下一次只需把前述串行命令manifest路径改成 `build/calendar-per-app-store-r3/Cargo.toml`，加 `--nocapture` 留下两条拒绝的真实错误，日志写 `build/calendar-per-app-store-r3/test-r1.log`。范围、资源与所有正式阻塞保持。

## r3 中央实际通过与开发单元收口

中央已按上述单job offline命令运行r3，记录在 `build/calendar-per-app-store-r3/test-r2.log`，中央报告exit0；现场日志核对 **8 passed / 0 failed，测试1.02秒，构建3m28s（208秒，含package cache lock等待）**。该次没有 `--nocapture`，通过测试的两条stderr未出现在日志里；不补造输出，不再加测试或重跑。

真实结果与完整文件SHA256在 `STORE_ADMISSION_R3_RESULT.json`。现场 `git apply --reverse --check --directory=build/calendar-per-app-store-r3` 成功，证明审阅补丁对应已准备源码；编译测试源码与独占目录源码逐字一致，补丁SHA与preparation一致。共享target二进制SHA是核对时快照，后续其他构建可能覆盖同名文件，不能只凭文件名识别运行身份。

关键SHA：

|对象|SHA256|
|---|---|
|中央r3测试二进制|`7a9684692186714fef52673c5bb4ff8cfc8f79686ea5248822374141f5fb3daf`|
|补丁后的Store源码|`9272ab679a30321bc7f48cc1e464a396eca91b2ea79593e70101a1fcff4d9bc4`|
|审阅补丁|`bbf9b1a2066074b3f44299208f1dafaa16ae5ecaa156c0eb69eeb456bb1260c1`|
|中央r3测试后的Cargo.lock|`96dec86d1a3712c3a63b6365e0b66bbb6d04660f831dc1fc8a2a51bbe3e5abe2`|
|准备时Hub Cargo.lock|`00615a6f3baae357d81cf413721a0a0082df1c863ca16a3803daab40515006b3`|

本次命令使用 `--offline`，没有 `--locked`；隔离workspace的Cargo.lock在解析时改变，日志明确记录重新锁定/添加包，不能称与准备时锁文件逐字一致。两份SHA与包identity差异记录均保留，不将此fixture编译冒充整个官方workspace的locked构建。

**结论限定为签名fixture的真实Store准入8项通过。** 尚无正式Shell接线、真实本人consent、Relay、可信手势审批或Calendar CRUD；update/remove的owner-only和上游准入阻塞不变。#182反馈计划来自中央，本任务未发公开评论，也不把反馈等同获准。

第一阶段全局offer仅历史比较，不应与per-app补丁叠加。r2签名冲突失败log及原补丁保留。开发单元已整理，停止扩展；由中央审查、整合和决定提交。本任务无Git操作或新构建。
