# Calendar 宿主准入接线提案

2026-10-10。worktree `muse-semifinal-a-20261009/Agent APP黑客松`，开始 HEAD `2cebd4c8`，分支 `codex/muse-pivot-20261010`。**BLOCKED 未解除。** 只写本目录及 ignored build；没有构建完整宿主、操作 GUI、运行生产日历、提交或 push。

## 实际缺口与现有合法委派路径

固定 Desktop `4ccf8e0` / Hub `95e4831`：`appstore/src/system.rs:54` 的额外 offer 只接受 `os.*`，商店 AppStore、CardApp、Shell agent admission、glance 启动使用默认 HostLimits，没有相同的商店应用 offer 接口。

委派路径已经存在：`host_tools/script_apps.rs:113,163` 从已准入 manifest 的 `agent.tools` 导入跨应用请求，解析 owner，再设置逐工具 grant；`relay.rs:357,715,861` 依次保持 shareable、consent、实时双方 admission 检查。Calendar 原始可共享工具只有 events/add_event/notify。没有发现允许商店应用绕过 offer 的正式入口。

**查询、新建、通知**只缺宿主提供 ceiling；**精确 get_event、共享更新/删除**仍需要先前 Calendar 补丁和上游策略接受，不属于本补丁。原版 owner-only 不变。普通商店 manifest、签名、摘要、目录撤回、权限、可信输入来源和审批机制均不改变。此 offer 本身不是用户批准或逐次写入确认；原版 add_event 是 act，不保证出现本人确认窗口。Muse 若要求逐次确认，必须另外核验该工具真实审批策略，不能用 offer 当确认成功。

## 可执行补丁

- `hub-store-calendar-offer.patch`：新增宿主专用、默认关闭的 Calendar offer；只追加原版三项 shared 工具，不改变其他 HostLimits 字段。AppStore 与 CardApp 使用相同 ceiling。
- `desktop-store-calendar-offer.patch`：在 Calendar 注册后由宿主显式启用；Shell agent admission 与 glance launcher 使用相同 ceiling。没有 Muse 特例、身份替换、开发模式或新存储。
- `prepare_patch.py`：只读固定源，检查唯一替换位置，生成以上两份补丁与 `baseline-sha256.json`。输出目录必须明确指定；脚本不自动应用补丁。

公共 offer 是宿主级工具可用性上限，不是 Muse 专属授权，所有商店应用仍必须在各自已签名 manifest 请求工具，且 relay 要求 consent、shareable 与 grant。关闭 offer 只影响后续 Store 构造；不是已有会话实时撤销接口，实时撤销仍由已有 consent/admission 路径处理。补丁需官方审阅，不宣称其为已发布标准接口。

## 本轮实际证据

1. `rustc --edition 2021 --test .../store_agent_offer.rs -o build/calendar-store-offer-tests`：真实新增模块三项测试通过（默认关闭；只追加三工具且无重复，拒绝隐含 update/remove/get/shell/dev；关闭后新 ceiling 不追加）。这是纯 offer 单元验证，不是模拟 Calendar，也不是真实 Hub resolve。
2. `check_contract.py`：11项只读源码合同检查通过；记录在 `source-contract-evidence.json`。静态检查不能代替 runtime 准入。
3. 两份补丁在实际固定 checkout 上 `git apply --check --directory=...` 成功；没有应用到源树。
4. 初次 patch generation 失败：apps.rs 中 register_calendar_services 有多处，唯一性断言拒绝生成。改为匹配现有 os.mail offer 加注册的唯一片段后成功；没有绕过断言。

本次没有重复旧 Calendar 组件、进程或 UI 测试。没有新的签名准入、Relay、可信手势、模型调用、CRUD 或恢复成功证据。

## 中央串行调度请求（未执行）

1. 在中央批准的隔离源/ignored build 应用 Hub 和 Desktop 补丁（分别 `git apply --check` 后 `git apply`），保持 baseline SHA；运行新增模块及已有真实 app-policy/admission 测试。不要应用到根 bundle 或安装版。完整 Cargo 构建请中央串行调度。
2. 用固定测试签名身份的隔离商店 catalog/bundle 做真实 Store admission：默认关闭拒绝 Calendar 请求；启用+正确签名/摘要+明确 manifest 请求通过；未请求工具不能获得 grant；缺签名、篡改摘要、目录撤回、索取 update/remove/shell 继续拒绝。测试私钥只驻隔离内存/临时环境，不输出或记录。
3. 另一个商店 App 必须增加正反隔离用例：同一 ceiling 下未在 manifest 请求工具、未 consent、已撤销 consent 均不能调用；伪造 Muse calling_app 必须由原宿主身份戳与 Relay 拒绝。另一个正确签名、明确请求且本人授权的 App 可以获得它自己的 grant，这是宿主 ceiling 的设计范围，不可宣称 Muse 独占。上述实际 Store/Relay 隔离测试本轮未执行。
4. 同候选 Shell 的真实 Relay：muse-goals 身份、非dev模式、本人 consent 允许后 events/add/notify 路由到 os.calendar；拒绝 consent、无grant、错误owner、签名撤回、非shareable update/remove 都拒绝且无写入。保留原可信手势/approval反例；add 的逐次确认要求仍需明确方案。
5. GUI 与真实日历写入需中央明确批准、串行占窗；仅隔离 os.calendar 数据，事件ID独立读回/恢复。未经这项，不能把单元和静态检查当全链通过。
6. 先等待官方对商店 offer 接口及共享更新/删除/精确读回提案的审阅；不要把此前 #427 反馈当准入授权。

中央复现准备：

```sh
python3 official_muse/semifinal/calendar_integration/prepare_patch.py --sdk .local-state/official-rc2-source --hub .local-state/hub-contract-sdk/app-hub --out official_muse/semifinal/calendar_integration
python3 official_muse/semifinal/calendar_integration/check_contract.py
rustc --edition 2021 --test official_muse/semifinal/calendar_integration/store_agent_offer.rs -o build/calendar-store-offer-tests
build/calendar-store-offer-tests
git apply --check --directory=.local-state/official-rc2-source official_muse/semifinal/calendar_integration/desktop-store-calendar-offer.patch
git apply --check --directory=.local-state/hub-contract-sdk/app-hub official_muse/semifinal/calendar_integration/hub-store-calendar-offer.patch
```

上述检查已执行；应用补丁、完整构建及正反真实准入/Relay矩阵尚未执行。并发出现的共享报告及其他任务文件均未编辑。
