# model.complete Chat bad_request 独立核对

2026-10-11。状态 PARTIAL：SDK 契约根因与当前中央补丁的定向 fixture 已核对；真实模型、Splash VM 与 GUI 由中央执行。本聊天没有修改共享 main、SDK、Bundle 或用户资料，没有 Cargo、GUI、凭据或外部服务调用。

## 根因和最小边界

当前 SDK `apps/ai-providers/host-service/src/complete/mod.rs:194` 的真实入口名为 `Request::from_args`。其顶层允许字段只有 `task/input/schema/class/allow_urls`，多余字段直接返回 `BadRequest`。`input` 接受 JSON，脚本应用上限为 32 KiB。`user_prompt` 将其作为 `Input (JSON)` 数据提供给模型。

中央基线 source `0c7f9812cf7319cf5120557ddef7caacfe49326c0dcbc5759e689fcac38ce9eb` 的 `send_chat` 传递内部 `messages: []` 标记，`muse_model_request` 构造历史后直接将含顶层 messages 的 payload 交给服务，确定违反此契约。Calendar Agent 使用不同路径；其成功不能证明 Muse Chat 请求有效。

准备时中央源码已变，最初完整 SHA 守卫拒绝。只读复核发现 Root 已加上对应修复，改为从中央 HEAD `88e5ba28911bbd066e3dc448243d5fbb8a8aa3ce` 的已验证 source 基线生成相同 patch，独立核对 Root 当前修复。

仅 `muse_model_request` 变化，6 行增加、1 行替换；529 个其他具名函数原字节不变。已有历史、当前问题、记忆资料、事项资料及较早原话进入 `input.messages`；发送前显式保留 `task/input/schema` 和已有可选 `class/allow_urls`。原 args 未修改，普通非 Chat input 仍为 current/related_memory。原有检索、schema、clock、身份/授权/记忆守卫及 Host usage trace 未重写。

## 身份和证据

- 修复 source SHA：`e2f3ab878d7d7f77772507dc85e18cbef284cff86c2d4ee0a7e6639296107ea3`，逐字匹配观察到的 Root 当前 source。
- SDK contract SHA：`79ce9ed937208d8df1dca27110001c7af1c0bc365a4a605c1154b57053d7d2fe`。
- patch SHA：`0bc024be64781a3f45db84a34eeef0757385766bb846ee925c1d7dba86ea3a7e`。
- `evidence/model-input-before-r4.json`：24/26，两项失败为 official_top_level_keys 和 chat_history_is_inside_input。
- `evidence/model-input-after-r4.json`：26/26，零外部调用。提取真实 wrapper/history/scope/reply-context 四函数运行 Node projection；传输、存储、记忆结果为合成 fixture。SDK 允许字段从固定源码读取，未执行 Rust parser 或真实模型。
- 覆盖历史顺序与原话、失败/跨项目/遗忘过滤、reply JSON 历史格式、结构化候选、schema/strong-fast class/URL true-false-default、普通 input、调用者未变、用量与 refs、请求前七种守卫、迟到四种身份守卫和记忆冲突。
- `evidence/model-input-application.json`：临时副本实际 git apply --check、apply 后字节回读通过；中央 source 未写。r1-r3 为 Node 适配器语句/对象表达式/循环翻译错误，六份错误文件保留；不作为产品失败或通过。

Root 已有这份修复时无需再次应用。若回放，先核完整基线 SHA，再使用 model-input.patch；源码漂移则按具名函数核对，不强行偏移。

## GUI 最短接续

先用普通 Chat 发一个短问题，实际成功回复且 trace 不再 bad_request 后，在新对话用顶部「切换」填写验收项目/个人并「使用这个项目」。发一次性任务计划请求，在「结果→来信与结果→本次任务计划→打开并核对」建 Goal，保持「等你确认」；同会话发明确未来时间的日程创建请求。到「行动链→切换事项」明确点击新 Goal，再打开日程候选。「核对后提交当前事项候选」经本人批准后「回读当前请求的官方记录」，须看到该绑定的「官方日历精确读回 / 已核验」。已提前选好授权邮箱时，点击「准备或打开关联确认草稿」，止于空收件人的未发送草稿。不以 calendar.events 数量替代 add/get 配对核验，不 seed 用户存储。
