# 统一宿主接线：下一单元

2026-10-10。入口HEAD现场 `67571ec3`，保留已提交Store八项证据与r2失败；总体BLOCKED。

## 中央串行构建请求（未启动）

第一小目标：隔离Hub的 `octosense-app-hub --test per_app_offer`，只追加共享配置/克隆/多Store撤销和准确工具集合用例。单job、offline、复用 `build/official-hub-rc2-target`；预计源码重编/链接0.2–1GiB、1–5分钟，不含缓存锁等待，未实测。不能使用旧八项证明新增缺口。

第二目标：`cargo check --offline -p octosense-appstore --no-default-features -p octosense-app-hub-app`，验证真实统一factory及AppHub native catalog接线；涉及Makepad/Octoscript，可能1–3GiB、3–10分钟以上，未经测量，须中央选择串行窗口。完整Shell/GUI不属于这两个小目标，只提交Desktop源码接线供中央后续验证。

不自行运行Cargo/GUI/外发；不新增用户授权存储或运行时。配置仍默认空，按app+准确工具集合；尚无正式启用或官方接受。

## 真实路径审计

固定Hub95e4831/Desktop4ccf8e0：

|入口|原位置/检查|接线提案|
|---|---|---|
|AppStoreView|appstore/src/lib.rs:208创建，open:378用may_run|统一host_store factory|
|CardApp|appstore/src/cardapp.rs:96创建，109 prepare_launch；system单独prepare|仅第三方分支用factory，system路径不变|
|原生App Hub|app-hub-app/src/catalog.rs:164创建，234/237 clone，422 for_install_root，465 may_open|统一factory，clone/staging共享引用|
|原生App Hub安装确认|catalog.rs:342生成InstallConsent，459核对确认；两次都原默认limits|改调用Store.resolve_offered_policy，canonical_entry/sequence/manifest及确认流程保留|
|Shell Agent实时准入|host_tools/admission.rs:34创建；mod.rs:634 Env.admitted调用；relay.rs:861重验双方|统一factory，每个后续Relay请求仍先走原双方admission|
|glance isolate|glance_card.rs:1355创建，may_run/sequence floor|统一factory，原catalog cache、floor、API及isolate路径保持|

未发现现成第三方per-app配置入口；原host_api.rs的METHODS/FEATURES只是API实现描述，不应当作授权。复用已有HostLimits、Host API版本、data root及CatalogChannel，新增唯一薄host-only共享配置接口；不增加环境变量、script service、持久权限库、另一个Runtime或Calendar存储。

## 最小统一补丁

`hub-shared-host-wiring.patch` 是相对原固定Hub的**累积补丁**，包含已审阅r3 Store及本轮接线，不要在已经应用r3的树上直接再次应用；中央先对干净固定副本apply-check。

1. Hub新增 `AgentToolOffers`（空的Arc/Mutex map），Store clone、for_install_root和使用同配置的独立实例共享引用；准确集合替换而非累加。仍通过已认证catalog entry及原PublisherKeys签名检查才能设置非空集合。单工具r3 API保留为同一集合接口的入口；旧8项测试保留。
2. 每次安装、may_run/prepare_launch、prepared launch再验，从共享配置取当前按app的ceiling；锁失败返回错误，不退回宽权限。未请求的工具不会进入policy、其他App默认不扩展。
3. appstore新增 `host_store(anchor,root)` factory；宿主进程唯一默认空共享配置，所有五个第三方Store创建路径使用它。宿主在接受catalog并核对既有channel sequence floor之后，才可通过所得Store的 `set_agent_tool_offers(app, exact_tools)` 设置或清空配置。没有默认Muse启用，没有把Muse改为os.*，没有调用system-only setter给Muse。
4. 原生App Hub的展示/安装确认用Store当前ceiling解析，保留原InstallConsent、canonical_entry、host_api检查、catalog freshness及下载后再次确认。不写新的用户授权存储。

`desktop-shared-host-wiring.patch` 只接Shell admission/glance factory，不改Relay、身份/签名/摘要、consent、可信手势或owner shareable声明。Calendar update/remove策略未动。

撤销语义只承诺**下一个验证边界**：所有共享Store、clone、staging和新实例读到同一撤销；下一次Relay env.admitted重新创建factory Store并原样验签/读回policy。已经返回的AppPolicy、已经运行的UI、已发出的Calendar操作不会被自动取消；不宣称跨进程/重启持久撤销，也没有发明安全的在途回滚。进程重启默认空，必须由宿主重新提供受控配置，不能从未可信应用恢复授权。

## 准备与新增验证范围

隔离准备对象 `build/calendar-shared-host-wiring-r2`，源码约2.1MiB；没有运行Cargo。`prepare_host_wiring.py` 只写独占目录及ignored build，保留r3八项证据与r2签名冲突失败。新增仅两项真实Store API用例：共享clone/staging/独立/新Store撤销；准确工具集合替换与另一个App隔离。测试总数10，**尚未编译/执行**。

两份补丁对原固定checkout `git apply --check` 通过。初次接线准备r1在只读源码审阅中发现prepared-launch调用漏了Result传播的问号；已修正准备脚本并生成r2，r1保留，不是编译失败证据。不把apply-check或旧8/8当本轮通过。

中央第一命令：

```sh
CARGO_BUILD_JOBS=1 cargo test --offline --manifest-path build/calendar-shared-host-wiring-r2/Cargo.toml --target-dir build/official-hub-rc2-target -p octosense-app-hub --test per_app_offer -- --test-threads=1
```

中央第二命令（需安排资源）：

```sh
CARGO_BUILD_JOBS=1 cargo check --offline --manifest-path build/calendar-shared-host-wiring-r2/Cargo.toml --target-dir build/official-hub-rc2-target -p octosense-appstore -p octosense-app-hub-app --no-default-features
```

依赖与框架使用已准备固定checkout，不自动下载/提高预算；lock从r3已实际解析的版本复制，但本轮没有运行解析，不能称locked构建。第二命令验证AppStore/CardApp/native backend源码，不能证明完整Shell编译。Desktop接线的完整编译/GUI/真实商店v2准入/本人consent/Relay/Calendar CRUD仍由中央后续串行安排。首次实际结果或错误须留在该r2 build，不覆盖旧失败。

当前**BLOCKED**：这只是默认关闭的宿主受控offer及统一入口提案，上游未接受，未正式启用Muse权限。中央已反馈#182 comment6098136836的是上一Store8项证据，不是本次共享接线验收。本任务没有外发、Git或共享报告修改。

## 五crates离线失败与Store独立准备

中央第一命令在依赖解析阶段失败；原始 `build/calendar-shared-host-wiring-r2/store-tests.log` 保留。实际错误为 appstore 依赖的 `Octoscript-Makepad.git?rev=33dea2f1f3ad3f1346a219aa8cf6e91b31361e23` 在Cargo preexisting repository中找不到该reference，offline禁止更新。**未编译，10项未执行**；不能把这次失败称为Store实现测试失败或接线编译通过。

只读版本核对（未执行Git）：固定Hub appstore manifest请求33dea2f1…，DesktopRC2根manifest同样请求该rev；已准备Hub identity.json也声明它。Hub本地octoscript-makepad是指向DesktopRC2 `.sources/octoscript-makepad` 的symlink，两者 `.git/HEAD` 均为相同完整rev。其package声明版本0.1.0，与引用相符。仅能确认名义checkout版本匹配；没有核对全部worktree文件与Git对象逐字身份，不能称本地路径patch已验证原版版本/编译。日志显示的是Cargo离线source metadata/ref缺失，不能推断实际源码版本错了，更不能拿它作为成功证据。

按中央要求另建 `build/calendar-shared-store-only-r1`：只包含contract/policy/hub三个crates，复制**未经改变的共享Store代码与10项测试**，逐文件SHA与完整五crates副本相同；Cargo.toml及初始lock复用中央已真实解析通过的per-app r3三crates workspace。没有删改完整workspace、appstore依赖或失败日志，也没有换成其他版本来冒充接线成功。

准备脚本 `prepare_store_only.py` 与 `store-only-preparation.json` 在独占目录，JSON记录Store/src/lib/test SHA、workspace/lock SHA及版本核对边界。没有Cargo/Git/GUI；新三crates对象仍**NOT_COMPILED/NOT_RUN**。

中央下一条串行小目标：

```sh
CARGO_BUILD_JOBS=1 cargo test --offline --manifest-path build/calendar-shared-store-only-r1/Cargo.toml --target-dir build/official-hub-rc2-target -p octosense-app-hub --test per_app_offer -- --test-threads=1
```

日志请独立写该Store-only build目录，不能覆盖五crates失败。这个目标即使10项通过，也只证明真实Store共享配置/撤销API，不证明AppStore/CardApp/nativeHub/Shell/glance接线、真实consent/Relay/CRUD。完整五crates依赖解析问题仍由中央串行处理；默认关闭及BLOCKED边界不变。

## Store-only中央实际10项通过：本单元交接

中央已执行独立三crates命令，报告exit0；现场读取 `build/calendar-shared-store-only-r1/store-tests.log` 确认 **10 passed / 0 failed，编译19.76秒、测试1.41秒**。新增共享clone/staging/独立/新Store撤销及准确工具集合替换两项通过，原八项保留。执行者为中央，本任务仅核对，不重跑Cargo或增加测试。

`HOST_WIRING_STORE_RESULT.json` 保存完整命令、执行边界、测试名、文件路径与SHA256。Store/src/lib/test源码SHA与独立准备记录及完整五crates副本一致；审阅Hub/Desktop补丁SHA与host-wiring-preparation一致。测试后lock与本次Store-only初始lock逐字相同，但命令仍是offline而非locked；不能将其称为完整官方workspace锁定构建。

|对象|SHA256|
|---|---|
|共享Store源码|`41bface270d15c2aaeb46f1fbc0019524850ee7c418498c2c4878ea13c97379d`|
|Store-only测试后的lock|`96dec86d1a3712c3a63b6365e0b66bbb6d04660f831dc1fc8a2a51bbe3e5abe2`|
|中央测试二进制|`d78a2c1151f9dd1a09f1b14bf6c65337b9af520a6cd411f21a7962a4b058422a`|
|中央通过日志|`c7d49714517cabcbb4da959217e74520836438152718d9f5afb2811493b818c8`|
|Hub接线累积补丁|`ab5d34fc44398500440a30dadaf0b6bc9e1bfa03a036ff8f2745b0f3f97de8a9`|
|Desktop接线补丁|`7c1797966c4d9887e1693f0c2676006e711983b762c7c307c38cb6b4fa3d07c9`|
|完整五crates解析失败日志|`671b766317b834feec1d9c6f65e757921d45a8ec7e15ed90e1ad85514eff2c72`|

共享target二进制名称仍为 `per_app_offer-16540a79e91eb6e9`，但内容SHA不同于先前r3八项二进制；以本次SHA+log+source识别，不能按文件名复用旧证明。

**结论仅为签名fixture的真实Store共享配置/撤销10项通过。** 完整五crates仍是Cargo git source/cache离线解析失败，factory/AppStore/CardApp/nativeHub未编译；Desktop/Shell未编译，真实本人consent、可信手势、Relay、Calendar CRUD未验证，上游未接受，正式链路仍BLOCKED。旧r2签名冲突和完整五crates失败均保留。

本开发单元已整理，交中央审查与小步提交；本任务不运行Git/Cargo/GUI、不外发、不扩大测试或Calendar策略。

## 中央后续：22:15开始完整backend检查

原五crates解析失败和三crates 10/10记录保持。中央确认本地固定33dea2f1 Git commit对象存在、checkout干净，从同一官方固定checkout补入Cargo git缓存，没有更改SDK源码或正式安装。重试AppStore/nativeHub的offline cargo check已进入实际编译，结果待记录；此前Store-only JSON是22:14时点快照，不代表完整backend最新结果。Desktop Shell仍未编译，正式consent/Relay/CRUD未测试。
