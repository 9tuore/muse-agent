# NIGHT-004 · ZC-02 Mail / Memory

本目录交付实际 Rust Mail crate 的隔离测试、真实 Splash VM 的 Memory 检查，以及供 ZC-03 集成的持久 Mail helper。业务源码未替换为简化实现。完整 Muse / Calendar / Mail L3 尚待中央集成，不能把此处组件结果升级为全链 PASS。

所有状态、target、收件数据均在 GPT-02 worktree 的 `build/gpt02-night004-*`。官方 SDK 与 Hub 实际复制后独立编译；Cargo 仅 resolver 路径指向缺失的固定来源，不改中央 SDK/target。rsync 的一个地图例子悬空链接失败保留，六个 Mail 生产文件逐 SHA 核对。生产 Mail 函数保持原字节，只在自有副本增加 `cfg(test)` 模块。`mail-l2-tests.patch` 是测试补丁，先核 `mail-test-identity.json` 的 before SHA，再 `git apply --check --unidiff-zero`；独立临时应用和读回已验证。不是业务补丁。

Mail 测试使用真实 `services::dispatch`、compose/status、public review 和 drafts 持久化逻辑。Vault 是固定合成值；`approve(true,true)` 是合成物理输入。MockTransport 通过子进程管道交给独立 Python 收件端，不使用 socket、SMTP、真实账号或 Keychain。实际 Shell claim guard 源码没有改动，Shell 执行由中央单独验收。组件测试中的 guard callback 只注入拒绝；没有宣称原生本人批准。

## 集成用 helper

在本机使用实际已编译二进制，`mail_helper.py` 将 Rust test harness 的输出整理为纯 JSON-lines。每次创建新的合成 root，恢复时只接纳带本 fixture 专用 marker 的自有 state。

```sh
python3 '/Users/mima0000/.codex/worktrees/gpt02-mail-memory-recovery/Agent APP黑客松/official_muse/semifinal/mail_integration/gpt02_recovery/night004/mail_helper.py' \
  --binary '/Users/mima0000/.codex/worktrees/gpt02-mail-memory-recovery/Agent APP黑客松/build/gpt02-night004-mail-r1/target/debug/deps/octosense_mail_service-f1a378928c07f474' \
  --root '/Users/mima0000/.codex/worktrees/gpt02-mail-memory-recovery/Agent APP黑客松/build/gpt02-night004-l3-owned-NEW'
```

输入 `{"id":1,"method":"mail.compose","args":{"account":"one","to":"receiver@example.invalid","subject":"Synthetic","body":"Synthetic body"}}`。回复为实际服务数据 `{"id":1,"is_ok":true,"data":...}` 或 `is_ok:false/error`。SDK caller 固定为 `night004.synthetic-mail`，sender 为 `sender@example.invalid`；这两项都是 fixture 元数据。

支持 `mail.accounts`、`mail.compose`、`mail.compose_status`、`mail.review_send`。review 的真实 args 包含 compose_id、expected_revision 及精确正文快照；顶层 `decision` 为 `approve/cancel/reject`，只控制合成审阅，默认 cancel，不进入生产 args。fixture 方法为 `fixture.mode`（顶层 mode=`accepted/before/unknown`）、`fixture.receiver`（独立收件数据及当前进程 transport_calls）、`fixture.quit`。UNKNOWN 模式先交付独立模拟收件端再丢失回执。恢复时重新启动同一命令、同一 marker root；状态/attempt/message ID 保留，transport_calls 从零开始，不重新发送。

`verify_mail_helper.py` 的 report 留存精确实际请求、服务回复与独立收件数据。此接口适用于 L3 模拟 Host 边界，不能当作正式原生同意或真实投递。

## Memory VM

`prepare_memory.py` 按真实调用闭包提取冻结 main 的原函数和全局定义；默认运行原 Memory suite，`--probe memory_completion.splash` 运行实际 finalize_result 与 mail_finish_linked_step 门禁。仅 redraw/mail_redraw/set_page 按已有 runner 替换，外部服务禁止。合成步骤拆为 timer 回合，生产函数、文件读回、schema、hash 和 VM 预算未改。

冻结 main SHA 为 `768e295df55316c037f61181b25e47191ef452eb3deed60d518361df699c5b7b`，reference host SHA 为 `78ab9efce55cb692552a3566e7b579d2e8c304eadfd6b107c51b2efb027e34db`。这是实际 VM + jailed fs 的业务 fixture；没有跑完整主界面、官方新 Host admission 或真实系统动作。原 suite 的异步、大库、重启和视觉占位说明没有计入 61 项布尔通过。

`run_memory_vm.py` 的第一个位置参数是中央实际 runner 路径，其余参数沿用该 runner 的 `--host --host-cwd --source --probe --out --port`。证据中的 report/log/identity 给出运行源码、生产函数和二进制身份；旧失败及适配器修复保留，不覆盖。
