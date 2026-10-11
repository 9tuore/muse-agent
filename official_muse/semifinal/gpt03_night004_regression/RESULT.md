# NIGHT-004：改期候选归属防护与受影响回归

2026-10-12，GPT03 自有 worktree。结果为 **PARTIAL：官方 Splash VM 的合成边界检查通过；真实 Calendar/Mail L3 和 GUI 交中央执行**。本单元不启动 Host，不修改共享源码、SDK、bundle、target、生产资料或核心 Python。

## 可应用修复及版本身份

`edit-goal-binding.patch` 只在 `chat_add_proposal` 的 native 改期编辑分支加入六行校验，采用 GPT04 实测提案。当前 active candidate 必须与请求 candidate ID 一致；请求/card 显式 Goal 不能矛盾；后续新 card 必须携带原事件 Goal。原候选、最新合法改期候选和同 Goal 的后续候选保持可编辑。

| 身份 | SHA-256 |
| --- | --- |
| 原候选：中央 wall/strict create + native update | `d065ad15ebeef1e67d69ef4e3c722f2b76cf03e7a0ab325fc2b29073b10dfba5` |
| 本补丁 | `10289635c7cfdba509176a1fb9359405534e4d55e4e3074ac6754b2d42d7da42` |
| 原候选 + 本补丁 | `1db491bb7b3fab8aadd5676605fd9851783b59cdfa5995f125854b334bf8b85c` |
| 再组合 GPT02 `nil-binding-guard.patch` 的自有副本 | `dabfe65bbb859e51db5cc2b9eea59855024af927f8bfbe548fa86f50ded95a6d` |

实际 `git apply --check`/`git apply` 于自有临时目录完成，结果与冻结目标字节一致。单独补丁仅改变 `chat_add_proposal`；组合副本仅改变它和 GPT02 的 `calendar_agent_binding_current`，其余生产函数逐字一致。GPT02 补丁先用 `gm_object(binding)` 防止 nil 的字段读取，由 GPT02 交付、中央单独集成，本目录不重复交付该补丁。

## 已执行的检查

原候选运行 `edit_binding.splash`：11 项中 4 项失败，实际保存第二个 Goal 后，另一 Goal 的候选会被重绑到原事件 Goal，打开后可准备原 stable event 的改期。另两个失败是 request/card Goal 矛盾。原候选与合法最新候选的正例仍通过。六行校验后的 11/11 与原改期 99/99 均通过。

| 原有检查 | 结果 | 执行源 | 原始日志（仓库根相对路径） |
| --- | --- | --- | --- |
| Goal byte bounds | 10/10 | `d065ad15…` | `build/gpt03-night004-regression/original-r2/goal_bounds/` |
| Memory 完整回归 | 58/58 | `d065ad15…` | `build/gpt03-night004-regression/current-memory-boundary/memory/` |
| Memory 新 VM 进程恢复 | 8/8 | `d065ad15…` | `build/gpt03-night004-regression/current-memory-boundary/memory_restart/` |
| Mail production | 19/19 | `d065ad15…` | `build/gpt03-night004-regression/current-mail-fixture/mail/` |
| Mail Host receipt 状态防护 | 8/8 | `d065ad15…` | `build/gpt03-night004-regression/original-r2/mail_receipts/` |
| Calendar restore | 10/10 | `d065ad15…` | `build/gpt03-night004-regression/original-r2/calendar_restore/` |
| Action chain projection | 37/37 | 两补丁组合 `dabfe65b…` | `build/gpt03-night004-regression/action-chain-two-fixes/action_chain/` |

两补丁组合源 **dabfe65b…** 的改期99/99、归属11/11、行动链37/37全部通过；前两组原始报告分别在 `build/gpt03-night004-regression/combined-update99/` 和 `combined-edit11/`。单独六行补丁的原始报告是 `final-guard-update99/`、`final-guard-cases/`，原候选反例是 `final-guard-counterexample/`。每个目录保存实际 `executed.splash`、stdout、stderr；已有 runner 的报告包含生产函数 SHA。原有七组回归保存 aggregate `command.log`，不另生成逐组报告。

### 失败分类与边界修正

- Memory 初轮 51/58、恢复 6/8：本 VM 边界缺 `fs.sha256_file`，真实存储校验按设计拒绝遗忘。补齐文件字节的真实 SHA-256 接口后 58+8 全通过；两个 VM 进程间传入第一进程准确的 serialized file 字符串，未改 Memory 函数。
- Mail 旧 fixture 18/19：只给顶层 `accepted`，缺当前 Host 的 operation/revision/status/payload/receipt attempt 证据。仅补 `mail.compose_status` 的合成响应后 19/19，保留生产端严格回执判定；原有 8 项 receipt 反例也通过。
- Action chain 原候选直接 VM 崩溃：`calendar_agent_binding_current(nil)` 在验证前索引 `plan_revision`。采用 GPT02 独立防护后，原 37 项通过。

执行的是官方 SDK 的真实 Splash VM，业务函数从冻结源提取。存储 IO、重绘、页面切换、时钟/定时器、控件 text ports 和 Host 传输为合成边界；restore fixture 另替换原有 `mail_watch_boot` 外部入口。其余生产函数逐字校验。上述七组最终通过的运行 stderr 均为空，禁止外部 transport 的记录均为 `[]`。这不证明真实 Kernel、EventKit、SMTP、模型调用或 official full-chain 成功。

## 重现入口

已有官方 VM runner：`build/gpt03-night004/target/debug/gpt03-night004-vm`，本轮未重建。以下输出目录需使用新的自有目录，脚本拒绝覆盖旧证据。

```sh
python3 official_muse/semifinal/gpt03_night004_regression/run.py \
  --source build/gpt03-night004/combined-apply/official_muse/app/source/main.splash \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --cases goal_bounds memory memory_restart mail mail_receipts calendar_restore \
  --mail-terminal-fixture --out build/gpt03-night004-regression/NEW_BASE_RUN

python3 official_muse/semifinal/gpt03_night004_regression/run.py \
  --source build/gpt03-night004-regression/combined-fixes-apply/official_muse/app/source/main.splash \
  --expected-sha dabfe65bbb859e51db5cc2b9eea59855024af927f8bfbe548fa86f50ded95a6d \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --cases action_chain --out build/gpt03-night004-regression/NEW_ACTION_CHAIN

python3 official_muse/semifinal/gpt03_night004/run.py \
  --source build/gpt03-night004-regression/combined-fixes-apply/official_muse/app/source/main.splash \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --probe official_muse/semifinal/gpt03_night004_regression/edit_binding.splash \
  --out build/gpt03-night004-regression/NEW_EDIT_BINDING
```

`fix_edit_binding.py` 从冻结 d065 自有副本重建六行 patch 与 `guard-main.splash`；普通回归 `run.py` 读取中央已有 probes/helper，记录原 probe/executed SHA，限定自有 build 输出。既有 probe 路径见 `run.py` 的 `CASES`。原有已通过组不因单独入口 guard 重跑。

### 现有完整检查入口清单（本轮未运行 Host）

| 入口 | 有价值的范围与实际参数 |
| --- | --- |
| `official_muse/prelim/tests/memory_runtime.py` | `--main-source <冻结源> --probe memory_regression_suite --output <自有目录>`，随后同资料目录跑 `memory_regression_restart`；支持 `--port`，`--visible` 会用真实窗口 |
| `official_muse/semifinal/tests/run_official_api.py` | `--host <参考Host> --host-cwd <工作目录> --source <冻结源> --suite production` 或 `calendar-restore`，另需 `--out`，支持 `--port` |
| `official_muse/semifinal/tests/run_mail_restart.py` | 原七种跨进程恢复；支持 `--host --host-cwd --out --port`，读取所在仓库主源，不支持 `--source`。旧 accepted fixture 必须先补当前 attempt 回执，不能把旧 fixture 失败判成业务退化 |
| `official_muse/action_chain/tests/run_projection.py` | 原 projection 37 项；支持 `--host --host-cwd --out --port`，读取所在仓库主源，不支持 `--source` |

这些是参数现场核对后的入口清单，当前任务没有启动它们的 Host，也没有重复中央的安全22/create23/wall6或 Rust 回归。

## GUI 只读预检与中央操作步骤

以下行号来自冻结 **d065** 主源，六行补丁后相应 UI 行号加6。未启动窗口，布局可见性/几何位置/真实点击仍未验证。

| 源中实际定位 | 控件/条件 |
| --- | --- |
| 11023 `打开并核对` | 日程候选 card 调用 `chat_apply_proposal(card.id)`；native 分支先 ensure matter、prepare candidate，再切 Calendar 页 |
| 11117 `日历` | Nav 切 Calendar 页 |
| 11598 `calendar_editor` | 已命名 `ScrollYView`，Fill/Fill、Down，初始不可见 |
| 11600 `calendar_panel` | 已命名 View，Fill/Fit、Down，动态 render |
| 11610 `calendar_agent_input` | 已命名 TextInput，height90 |
| 11625 `选择原事件并准备同ID改期` | 未命名 Secondary；有 update target 才显示；不 busy 才可用 |
| 11633 `确认所选事件同ID改期` | 未命名 Secondary；当前 prepared record 且选中 raw snapshot 才显示；不 busy 且 writable 才可用 |
| 11636 `核对原改期请求` | 未命名 Secondary；当前未 verified record 且已有原 turn 才显示；调用该 record 的只读 history |

中央真实操作应保留已独立验证的原创建 request，当前用户/account/project/owner、chat、Goal 必须一致；不要先“结清当前请求”清空此 native 权威。明确选择当前行动链事项，生成同 Goal 后续改期候选，点击其“打开并核对”。Calendar 页滚动 `calendar_editor` 找到准备按钮，核对旧八字段、新八字段、stable event ID 和计划版本；准备只落 journal/新计划，不执行 update。再次本人确认后才提交新官方 turn，必要的真实系统/Host 审批由中央按既有授权执行。以同 Kernel 原 turn 的严格 get旧→update→get新三条回执及独立读取证明 stable ID/request ID 不变、新时间正确；旧 Mail 草稿需重新审阅。UNKNOWN/重启只能先核对原改期请求，不自动重发。

上述三个按钮没有 `:=` widget ID；GUI 测试必须按实际文字和 render 条件定位，不能假造 ID。L3 或 GUI 失败若来自 core/shared/Host 分支，按中央边界单独归属，不把本 VM 的通过结果扩展成真实动作完成。
