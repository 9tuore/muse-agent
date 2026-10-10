## 中央实际验收：2026-10-11 06:04

r7完整Host `50d545c2…` / Kernel `9c3d4b94…`，新隔离资料、PID73069。原生Mail→一次Add account→真实宿主中文sheet，8项布局与QQ默认检查均通过。一次固定无效合成授权码输入真实显示圆点，中央已看OS原图；下半部服务器可滚动访问，返回顶部取消正常，remote quit/exit0且完整迟到日志无错误。公开receipt与三张图：`../evidence/native-full-shell-r1/native-mail-sheet/`。这是 **UI_READONLY_PASS_NOT_LOGIN**；QQ真实登录、Person确认、SMTP、投递未测试。

R1捕获枚举到消失/menu窗口，R2屏幕layer0筛选找不到root，R3未先滚动到服务器控件，失败和原始报告全部保留。当前runner将读帧404有限重试、实际滚动和输入值脱敏纳入检查；不重复Add/Cancel/提交。C探针只选同PID最大普通尺寸窗口，OS像素仍由中央看，不自动宣布视觉成功。

复現前编译：`clang official_muse/semifinal/tests/owned_main_window_id.c -framework ApplicationServices -o build/runtime-closure-render-compare-r1/owned-main-window-id`。默认探针已改该位置；必须在对应macOS环境执行。以下是执行前的历史交接，后续结果以上方为准。

# 官方 Mail native 登录 sheet 只读入口（未执行）

入口：`official_muse/semifinal/mail_integration/run_native_mail_sheet_readonly.py`。中央 Calendar 验收后串行运行。本聊天未启动 GUI、Cargo 或账号动作，只做 Python AST 检查；不新增或覆盖既有 r1/两尺寸 fixture 证据。

```text
python3 official_muse/semifinal/mail_integration/run_native_mail_sheet_readonly.py
  --binary <中央冻结r7 artifacts内完整Host绝对路径>
  --binary-sha256 <中央实际50d545c2开头的完整64位SHA>
  --out build/native-mail-sheet-readonly-r1
  --port <中央已选空闲端口>
```

以上占位符必须用中央已验证真实值替换。out必须是新ROOT/build直接子目录，既有目录拒绝；默认CGWindow探针是 `build/runtime-closure-render-compare-r1/owned-window-id`，可用 `--owned-window-id` 指定已核真实可执行文件；报告保存探针SHA。可用 `--mail-source` 指定中央已应用同补丁的lib.rs，要求SHA `724c7d7faee03d1303b8caf20b33e6958f385a03f01bf29a92a704a477fcbf7c`。单独源码SHA不证明二进制绑定，r7构建身份仍须中央证据。

启动前核完整Host SHA，邻接 `octos-kernel.json` pinned revision `b0759a57719fd35b3a2da1c5d969bc67538ed516`，邻接 `octos-kernel` bytes SHA与receipt相同。沿中央ignored `build/runtime-closure-render-compare-r1/run_calendar_readonly.py` fresh env：清除Kernel override/any revision/contained override及窗口隐藏等变量，将Shell/app-data/Kernel/Rinx/XDG目录全部设为新的home子目录，不复制账号、缓存或凭据；不改系统HOME/Keychain、不授予权限。`OCTOSENSE_DEV_MODE=0`，无 `--system`、policy或managed_mode修改。

真实入口证据：SDK `crates/shell/src/lib.rs:5332-5396` 的 `--test-action` 解析与 `strip_prefix("launch-")`，因此传 `launch-mail`；`apps/mail/bundle/main.splash:74-77,218` 的普通 Add account→`mail.add_account`→宿主sheet。复用既有 `calendar_integration/run_owner_ui_acceptance.py` 的 `Remote/WindowRemote`：window selector `w`，单次UI click不自动重复。核所有Remote状态PID属于own Popen子进程。出现permission/approval提示或初始Mail/sheet无法出现时 `HUMAN_REQUIRED`，不点击consent、不重启尝试绕过。

动作只有：打开官方os.mail初始页→一次Add account→读native sheet→一次中文“取消”。不按“连接账号”、不登录、不发信、不调用其他服务。保存初始页与native sheet的Remote PNG、同PID CGWindow OS PNG及SHA；snapshot移除所有 `val/value`，额外去除password控件的显示文本。默认不输入任何授权码。

现场布局断言：中文标题、无独立username/login控件、QQ IMAP993/SMTP465，以及三条QQ帮助Label。截图状态最多 `CAPTURED_NOT_VISUALLY_VERIFIED`，中央须查看Remote与OS图，确认真正可见/未黑屏、文字可读、帮助/服务器布局；widget树与截图文件生成不等于视觉通过。若字段不在snapshot或裁切导致缺失，保存FAIL/HUMAN_REQUIRED，不扩大窗口或伪造成功。

可选 `--probe-mask` 仅允许一次固定无效合成文本输入到**原生宿主**授权码控件；原值意外非空则立即停HUMAN_REQUIRED，不编辑。若Remote/宿主限制阻止或字段裁切，记NOT_TESTED，不重试、不程序set_text、不改权限。只在内部观测值等于固定合成文本且显示为对应圆点时记 `SYNTHETIC_MASK_OBSERVED_NOT_LOGIN` 并截图，不记录输入值。随后取消sheet，始终不提交表单。仅验证遮罩不证明账号登录/凭据有效或可信Person。

结束优先对own PID Remote `/quit`，等待退出；fallback terminate/kill仅针对自己Popen子进程，报告记unclean并失败。退出后重新扫描完整日志，迟到Script错误/非0退出/强制退出均不允许成功；缺屏幕录制权限是HUMAN_REQUIRED，不自动申请。成功也只说明原生sheet已捕获和取消，QQ真实登录、SMTP、收件、Person/native send审批均NOT_TESTED。
