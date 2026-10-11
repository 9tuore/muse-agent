# NIGHT-004 native 同 ID 改期可应用单元

本单元实现及官方 Splash VM 定向验证完成；整条 Calendar/Mail L3 仍待中央接入真实 helper。未修改共享 Main、SDK、bundle、target，未访问真实日历/邮件/模型，未 push。

冻结补丁基线是 `c183a5c4e7fcb5d543fb7b43ea72cced03a46819827e5b7ee0db1e80be968539`。`calendar-update.patch` 应用后为 `2ed8cb0b4c32260bf1a15b49bf9cdc7b5d46a5275e7a51d407a01369a2043b1e`。该基线仍包含旧 wall；本补丁不改中央负责的 wall 或 create link_result。

中央已经修好 wall 和严格创建核验的 `ebbc50b8a84ec7e7e2f891226ee022c0840efac26a3de6f1fdbb77a69797fd35`，在 own 临时副本实际 `git apply --check` / `git apply` 本补丁后为 **`d065ad15ebeef1e67d69ef4e3c722f2b76cf03e7a0ab325fc2b29073b10dfba5`**。该合成源改期 **99/99**、原安全 **22/22** PASS；中央 wall/link_result 函数逐字未变。接收请核对 `apply-combined.json`、`evidence/identity.json` 和完整 report。

## 行为

- 本人打开同一事项的新日历候选后，在日历面板选择原事件并准备改期，再明确确认；不会由模型同标题查找或换 ID。
- 真实 `chat_add_proposal` 的已建日程修改分支追加同 Goal 新候选，保留原候选及创建绑定；pending/unknown 改期不接受继续覆盖。避免旧聊天编辑在 prepare 之前使原事件失去关联。该入口含原卡 `opened` 状态实测。
- 准备阶段保存并逐字读回独立 `calendar-agent-update.json`，冻结创建 request/turn/proof、原事件八字段、完整身份、账号、两个候选卡及 memory_refs、旧/新完整 Goal、版本和参数摘要。之后使用已有 `core_replan_goal` 增加版本，取消旧批准、清除旧计划和模型摘要，保留 ID、来源、旧快照与 runs/actions。
- 只容许 `get旧 → update → get新` 三条当前回合回执，匹配 canonical sorted compact JSON 的 SHA-256、同一非空 Kernel session、唯一 call/tool_call IDs 和现有 broker provenance。更新实际 DTO 显式传六个替换字段，保留原 id/request_id，不含顶层 request_id；成功取 `data.event`。
- update 成功但没有 final get 至多 accepted。错误、取消、缺回执、逆序、重复及额外 Calendar 工具不能 verified。重启 prepared/in_flight 转 unknown，不自动重发；有原 turn 的 unknown 可人工触发只读回执核对。
- 创建证据不改写、不伪造 add_call_id。pending/unknown 禁用旧快照的 Mail 和删除；verified 后新的 authority 明确包含更新沿革。删除 expected 取最新事件。
- 准备即令旧邮件预览失效；正文保留，发送中转 unknown，accepted/verified 历史保留。新草稿绑定新 authority；旧 preview/send/review/compose 与迟到 callback 都经过现有 current/context gate。

## 重现

沿用 safety 单元的官方 VM binary 和 `run.py`，不重复 Cargo 构建。以下在 GPT03 own worktree 运行，`--out` 必须是新的 own `build/` 目录：

```sh
python3 official_muse/semifinal/gpt03_night004_update/build_patch.py
python3 official_muse/semifinal/gpt03_night004_update/compose_probe.py
python3 official_muse/semifinal/gpt03_night004/run.py \
  --source build/gpt03-night004/combined-apply/official_muse/app/source/main.splash \
  --runner build/gpt03-night004/target/debug/gpt03-night004-vm \
  --probe official_muse/semifinal/gpt03_night004_update/probe.splash \
  --out build/gpt03-night004/update-central-repeat
```

`build_patch.py` 只从 own 冻结 safety source 生成 patch/full source；`compose_probe.py` 只合入冻结的中央 wall 函数，用于早期独立探针。最终 PASS 使用实际中央 `ebbc50b8` 加补丁的 full source，包含中央严格 create verifier，fixture 创建行带真实参数生成的摘要。以上脚本不写中央文件。

最终原始命令输出：own `build/gpt03-night004/update-combined-final-r2/{report.json,stdout.log,stderr.log,executed.splash}` 和 `update-safety-final-r2/`。两份最终 stderr 为空，VM exit 0。摘要另经 Python `json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=False)` 独立核对，与 Splash sha256 值完全一致。

初轮失败日志全部保留在 own build：`update-probe-r1` 暴露原 delete_expected 的字符串键/点号读取问题，修为 JSON 归一化；`update-debug-r1/r2` 暴露 clone 后对象字段顺序变化使 history snapshot guard 丢弃有效回执，修为对原记录取 snapshot，delete history 同样做此最小修正。没有改宽松 create verifier。

前一阶段提交 `41b95c9b` 的 94 项证据仍保留在 Git 和 own build；最终追加聊天入口适配后为 99 项，本文 SHA 和 evidence/report 均对应最终单元。

## 验收边界与下一步

99 项使用真实官方 Splash 函数；只替换 storage/transport/render 和 UI text ports，clock、history 和两封邮件候选数据为合成。覆盖参数生成、完整 prepare/confirm/history、版本、旧/新 Mail、更新后实际 delete 函数链、后续第三候选沿革、UNKNOWN、迟到、持久化失败与损坏文件。没有通过 Rust/Node 重写业务逻辑。**不能称真实 CalendarService/Relay/Kernel/Mail 或 GUI/full-chain PASS。** 中央需对最终合成 SHA 做同候选 L3；GUI布局只做源码适配，未在此窗口运行。
