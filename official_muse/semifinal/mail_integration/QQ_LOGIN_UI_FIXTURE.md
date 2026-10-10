## Central observed result — 2026-10-11 05:50

The isolated complete SDK now contains the exact reviewed raw-sheet-only patch, source SHA724c7d7f. Bytes outside signin_sheet raw source are unchanged. The original-source six Mail protocol tests remain evidence for the unchanged backend, not evidence of new live login.

Actual visible reference runs at 412×892 and 990×539 each passed all14 checks, normal quit/exit0 and final error-log rescan. Central viewed both initial PNGs; the narrow instructions wrap, and short-window input/buttons remain reachable by real scroll events. See evidence/native-full-shell-r1/qq-login-ui/result.json. The managed reference intentionally displays its password-input guard in English and never accepts a credential; no claim of runtime masking, actual native Host sheet, QQ login, Vault or Person approval is made.

Fresh optional preparation replays the exact Native/Calendar/privacy/QQ patches and matches seven relevant files; it is PREPARED_NOT_BUILT. The complete canonical Desktop r7 is being built separately. Old Host, root rc17 and production data remain unchanged.

# QQ 登录 sheet 合成验证入口（待中央执行）

新增 `run_qq_login_ui_fixture.py`。本聊天只做 Python AST 语法检查；未执行 harness，未 GUI/Cargo，未应用 SDK。补丁身份仍为 `0415463dc87bba93b8867d1476f12260ac366eaf7be9a2c9380640d8437d5b25`。

入口直接读取真实 `signin_sheet()` 的 Rust raw string。输入可为原 lib SHA `5b9bbd082d7df01b9068bf1c830c30ff4f3d35ba31f182a387bea071fb2fc50e`，仅在内存严格应用 owned 补丁；或中央应用后 lib SHA `724c7d7faee03d1303b8caf20b33e6958f385a03f01bf29a92a704a477fcbf7c`。其他身份拒绝。生成 Splash 保留整个 sheet UI/handlers，只将两处 `host.request` 替换为 `qq_fixture_request`，前置合成 transport；无服务派发、登录、Vault/凭据写入、Person consent 或外发。结果只写布尔值，不保存表单或授权码。

## 精确入口

在 worktree 根目录，中央唯一 Cargo 结束后执行；`build/qq-login-ui-fixture-r1` 必须不存在。prepare 命令只生成隔离 bundle 和 PREPARED_NOT_EXECUTED 报告，不启动程序：

```sh
python3 official_muse/semifinal/mail_integration/run_qq_login_ui_fixture.py \
  --out build/qq-login-ui-fixture-prepare-r1
```

实际运行需中央提供已核真实路径、cwd、完整 binary SHA 和空闲端口（下面占位符必须替换，不能直接复制执行）：

```text
python3 official_muse/semifinal/mail_integration/run_qq_login_ui_fixture.py
  --out build/qq-login-ui-fixture-run-r1
  --host <中央已核的isolated reference/card-host binary绝对路径>
  --host-cwd <该binary已核运行cwd>
  --host-sha256 <完整64位SHA256>
  --port <中央选择的空闲端口>
```

不要传完整 Shell desktop binary：此入口沿已存在 `run_official_api.py` 的 reference CLI `--bundle/--app-data/--allow-unsigned/--stamp/--size`，窗口宽412、高1000。manifest沿项目真实schema，合成id `qq-login-ui-fixture`、仅storage、network hosts空；隔离home/state。不会修改生产权限或使用 `--system`。导入既有 `official_muse/phase2/tests/remote.py`，无新依赖。运行后保留 `bundle/main.splash`、`report.json`、`runtime.log` 和 `state/qq-login-ui-fixture/qq-login-submit.json`，结束只终止自身启动进程。

## 实际事件与验收边界

真实接口证据（SDK相对路径）：

- `.sources/makepad/platform/src/remote.rs:1808-1810` 注册 `/click`、`/k`、`/t`；2196定义键参数 `k=press,c=End/Backspace`，2241定义文本 `t=...`；1334将 Input::Text 转为 `StudioToApp::TextInput(TextInputEvent)`。
- `.sources/makepad/widgets/src/text_input.rs:675,697-699` 定义 on_change，并将handler排队；2426的控件 `set_text` 不发该事件。`apps/photos/bundle/main.splash:858` 有实际 `on_change` 用法。
- `.sources/makepad/widgets/src/text_input.rs:898-914` 明确受管应用拒绝 secret 输入，并定义宿主字段的遮罩；`widget_tree.rs:2596-2600` snapshot中的 `val` 是原值、`t` 是 `display_text()`。只允许合成表单，不接触真实登录sheet/真实凭据。

runner不调用 Splash `set_text` 模拟手填。输入使用 Remote click聚焦→End键press→Backspace键press逐字清空→`/t`文本事件→snapshot回读→等待排队handler；协议切换和连接按钮走Remote点击。任一几何裁切、回读失败、runtime error或缺提交报告都不会称通过。

检查：无用户名控件；QQ IMAP993/SMTP465初始值；POP995及IMAP往返；手动输入 `imap.fixture.invalid:1993` 后POP/IMAP往返保留；用 `  muse-fixture@example.invalid  ` 验证提交address/username trim；TLS/SMTP默认不变；`password is_password:true` 保留仅以原字符串静态断言记录。

**授权码运行时遮罩不在此受管reference中验证。** 不能因 `--system` 具有系统资源上限就假定它是未受管宿主isolate。本harness不放宽policy、不给secret字段填任何值，合成submit只接收空password，不验证账号。报告固定 `password_runtime_mask=NOT_TESTED_HOST_SHEET_REQUIRED`。中央需在实际宿主sheet用非凭据合成文本/本人合法真实操作另核遮罩；不得用本报告称密码输入、登录成功、Mail权限或trusted Person通过。

`FIXTURE_PASS`仅表示列出的静态保留项与合成reference事件检查通过，不等于官方宿主sheet/412×892视觉验收。中文wrap语法已核，但实际指引完整可读、底部滚动、宿主sheet作用域与账号服务仍由中央真实窗口检查；遇到Remote不支持或几何裁切，保留失败报告并转人工检查，不换虚构API、不用控件赋值补成功。
