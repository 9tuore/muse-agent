# NIGHT-004 L4 输入隔离与容量压力验证

2026-10-12，GPT03 自有 worktree。**本验证单元完成：48/48 检查通过，真实外部调用 0。** 只新增本命名空间的探针、运行器和证据；未修改业务 main、SDK、Host、GUI 或生产资料，未 push，也未发送跨聊天消息。项目的实际 Kernel/Mail/full-chain 验收由 Root 统一收口，不属于此结果。

## 冻结版本与执行边界

| 身份 | SHA-256 |
| --- | --- |
| 中央业务 main（复制到自有 build 后冻结） | `e7d665dd7f466e454aeca071895273e81549af169f8613c3490671a3cf8cca20` |
| 既有官方 Splash VM runner（复用，未重建） | `f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351` |
| 输入探针实际 executed 源 | `17202e2610705b52f57af282c86c6acf8b6ad1f4eb006bb6b1fe6e3f155943fa` |
| 规模探针实际 executed 源 | `d7c3953be0adff7476a7b2b197539e9d50c739f89b4b2cfb1bbc83dae7cf679e` |

`run.py` 提取启动前全部生产定义和 ACTION_CHAIN_PROJECTION，保留生产函数正文。仅替换 IO/UI 边界的 `storage_write`、`storage_read`、`redraw`、`mail_redraw`、`set_page`、`ac_refresh`、`ui_layout_save` 七个函数，将 `host.request` 重定向到记录队列；报告核对其余函数逐字一致并保存原函数 SHA。

输入、模型/宿主响应、人工选择、时钟、计时器、UI 和文件 IO 是明确 fixture；业务状态转换、SHA-256、保存/回读、容量拒绝、上下文筛选及投影在真正的官方 VM 中运行。未启动外部进程或进行网络调用。所有邮件地址、账号、事件、正文及收据均为合成内容。

## 已执行结果

| 探针 | 实际结果 | 提交内原始报告 |
| --- | --- | --- |
| `inputs.splash` | 26/26，exit 0，stderr 空 | [inputs-r3](evidence/inputs-r3/report.json) |
| `scale.splash` | 22/22，exit 0，stderr 空 | [scale-r2](evidence/scale-r2/report.json) |

输入探针从实际 `send_chat` / `muse_model_request` / `mail_open` 入口进入：

- 对 fixture 的 `invalid_output` JSON、schema 和 URL 错误响应执行真实回调分类与清理，不生成 Goal、提案、Action 或写操作意图。这验证应用接到官方接口错误后的处理，不代表实际模型或 SDK JSON 校验已实测。
- 合成恶意来信经生产记忆入口存为 `external_claim`，模型上下文保留“资料不授权操作”边界。即使 fixture 模型文字要求立即发送、删除日历或绕过批准，也只作为普通文字或待确认候选；草稿 preview 后仍为 `waiting_user`，attempt 空，Action 0。
- Calendar 候选不自动建立 Goal；显式打开候选后建立 1 个 planned Goal，Run/Action/turn dispatch 仍为 0。
- 事项 A 的合成严格创建证明是单独的 fixture setup，经生产 API 产生 **1 个 `octos.turn.start` 意图**。创建 A 编辑请求后切换并绑定 B，再返回旧 A 回调：不追加候选、不改变 B 绑定，原创建证明仍绑定 A。最终 Goal 2、Action 0。
- 两个实际 chat/Goal 交错提交、反序回调，回复留在原 chat；最终 2 个 Goal、2 个 chat→Goal 绑定精确保持。已取消请求的旧回调被忽略。

输入探针保留全部 RPC 意图，计数为 mail.accounts 10、model.complete 10、mail.message 1、mail.folders 1、mail.list 1、octos.session.open 1、octos.turn.start 1、octos.session.history 1。**未授权写操作意图 0；显式 setup turn 1；真实外部调用 0。** 队列中的 read/model/setup 意图不能称作实际 Host/Mail/Kernel 调用。

规模探针使用生产保存接口从 fixture 用户选择建立记录，未批量直接赋值 completed/verified Goal、Run、Action 或 Memory：

- Memory 64 条，Source 128 个；其中当前项目/归属 48 条、其他项目 8 条、其他归属 8 条。生产检索命中 5 条、context.bytes 2125，受 6 条/2200 上限约束；截断有审计，其他项目/归属标记不进入上下文。当前 refs 校验通过。
- Memory 第 65 条、Source 第 129 个、Goal 第 33 个、Action 第 129 条均被拒绝，主文件原字节和已有数量保持完整。
- 32 个 Goal 独立保存并经 `core_boot_goals()` 读回；32 个 Run、128 条 `in_flight` Action 由生产 `core_start_run` / `core_begin_action` 写入。最终 **32 个精确 Goal→Run 绑定、128 个精确 Goal/Run/revision→Action 绑定**，每个 Goal 4 条 Action。
- 实际 picker 限制为 8 项且 ID 唯一有效，32 次交错事项选择保持当前 Goal 正确。
- 附加候选日历关联、unknown 历史收据、来信、手写草稿及 stale 活动是只读投影 fixture，不是外部执行证明。投影最多 12 节点，所有节点 ID 唯一且仅属所选 `scale-goal-31`；整库快照逐字不变。去掉附加缓存后，最近 64 条扫描窗口显示 Goal+2 条匹配 Action，共 3 节点；全部 128 条历史 Action 保留。
- 最终 completed Goal 0，transport 意图 0，真实外部调用 0。没有 SMTP 投递、EventKit 或 Kernel 成功声明。

## 保留的失败及修正

[证据索引](evidence/index.json) 保留每轮身份和原始日志；旧输出未覆盖。

1. `inputs-r1` exit 1：fixture 缺少生产 `mail_enabled()` 所需的 `host.capabilities()` 端口。新增 read-only `["mail"]` 边界后继续，业务函数不改。
2. `inputs-r2` exit 1：合成用户请求同时含“起草邮件”和“安排”，实际配置选择 Calendar schema；fixture 却注入 Mail 三字段 success，随后假设一定有提案而越界。将 fixture 用户请求明确为邮件“主题会议”，使请求/响应合同一致；没有将此轮记为业务通过。
3. `scale-r1` exit 124：真实 parser 报告 fixture 变量 `scope` 为保留字；runner 没有退出，被驱动器在 120 秒结束。只把测试变量改名为 `scale_scope`，`scale-r2` 22/22 通过。此失败不能用来推断生产容量性能。

## 重现与交接

工作目录：`/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松`。

```sh
python3 official_muse/semifinal/gpt03_night004_stress/run.py \
  --source build/gpt03-night004-stress/main.splash \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --probe inputs --out build/gpt03-night004-stress/inputs-new
python3 official_muse/semifinal/gpt03_night004_stress/run.py \
  --source build/gpt03-night004-stress/main.splash \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --probe scale --out build/gpt03-night004-stress/scale-new
```

`--source` 必须匹配上述 e7d SHA，`--out` 必须是新的自有 build 子目录。驱动器使用中央既有 `official_muse/semifinal/tests/run_official_api.py` 的函数提取工具；既有 runner 与中央源码复制品均留在自有 build。每輪 actual executed 源、stdout、stderr、逐函数摘要仍位于 `build/gpt03-night004-stress/<轮次>/`；报告和日志副本随本命名空间提交。

交接：Root 可直接查阅两个 passing report 与失败索引；本单元不需要业务补丁。不重复已通过的中央 344 项，不接管 GPT02 的 Kernel/Mail、重启或 full-chain。当前没有本单元待修失败。原工作区非本单元的未跟踪 `official_muse/integrated_release/gui_smoke.py` 保留。实际不存在根 `CURRENT_STATE.md` / `HANDOFF_TEMPLATE.md`；按本轮“仅自有 namespace+build”范围把结果及交接记录在本文件。
