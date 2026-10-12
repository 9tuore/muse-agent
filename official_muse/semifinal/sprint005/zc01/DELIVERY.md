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

## 待续

实际 SDK Agent/session/profile_unresolved 诊断、当前官方比赛/App Hub 交付边界、ZC05 新 fixture Calendar owner-store 独立读回继续在本目录收口。此里程碑没有新的真实模型、Calendar 或 Mail 动作；没有发布/Tag/推送。
