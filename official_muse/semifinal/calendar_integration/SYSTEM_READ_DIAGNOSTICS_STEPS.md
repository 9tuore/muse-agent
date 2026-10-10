# Cold System read诊断：中央实测与复跑步骤

**中央r8实测追加（2026-10-11）：** r8候选baf55d24已由中央完整build/test；本轮只读核对[实际诊断回执](../../../../build/runtime-closure-system-read-r8-r1/report.json)：8项matched，state=PASS_COLD_READ_DIAGNOSTIC_ONLY，remote_quit成功、fallback=false、exit0、runtime_errors为空。events读取成功为空、limit=0 schema拒绝、get仍not_granted，add/update/remove/notify四项在只读预检直接拒绝，未增加grant。执行人为中央，本任务未重跑。

这只证明补丁调试read入口。另据中央现场消息，owner UI已创建ev-1791700320125、同ID15:00改16:00、固定System events全字段读回与真实进程重启无重复；中央06:32已完成普通owner UI二步删除与第二次重启，目标日期有界events均为空；精确get及权威不存在仍BLOCKED。owner UI操作不是Muse Agent Relay；正式MuseRelay/可信Person仍未由这些结果证明。以下保留脚本准备时的未运行说明和原命令。07冻结、08截止，本任务仅追加本文件，不GUI/Cargo/主文件/driver/Git。

run_system_read_diagnostics.py共153行；只Python AST语法检查通过，没有GUI/Cargo/脚本执行。复用当前run_owner_ui_acceptance中的WindowRemote/Remote；不修改owner runner，不打开System chat/配置provider/点consent，不截图或操作普通UI，不访问Calendar私有store。

中央等唯一pipeline26499/r8完成，核对新binary完整SHA及相邻packaged Kernel/receipt。选空闲port与全新ROOT/build直接子目录，再运行一次：

```sh
python3 '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/calendar_integration/run_system_read_diagnostics.py' \
  --binary "$calendar_shell_binary" --binary-sha256 "$calendar_shell_sha256" \
  --port "$calendar_remote_port" \
  --out '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/system-read-diagnostics-new'
```

脚本创建全新700home（rinx共享目录exist_ok=True），SHA/Kernel receipt/端口/PID检查，正常--test-action launch-calendar；只读/s和/snap确认实际owner窗口，不将layout当像素成功。只发已存在/event system-call测试入口，每次记录UUID/时间与新shell.log byte offset：
1. events{limit:1}：真实reply.ok=true、reply.data.events=[]。
2. events{limit:0}：真实reply.ok=false、error.kind=invalid_args，源码relay.rs:730对应schema拒绝。
3. get_event{id:MUSE-N002-READ-ABSENT}：真实error.kind=not_granted，不追加System get grant。
4. add/update/remove/notify {}：各必须出现“a test call runs only a declared read tool”，在预检直接拒绝；若进入JSON reply路径或无结果即停止，不重发。
5. 最后events{limit:1}再次为空，结合全部写工具预检拒绝记录0-write诊断证据；不声称私有store独立审计或正式业务成功。

每次等待最多12秒，工具结果来自真实新日志，而非/event HTTP应答。未知形状/错误/缺日志均PARTIAL并保存，不读取私有store、不增grant、不发模型回合或假Person。report.json与shell.log保留所有失败。

仅向/s已核对自身PID进程/quit，记录remote_quit/应答/fallback/exit/时间；fallback仅terminate精确Popen子进程，不碰503/进程组/独立Kernel。退出后扫完整日志迟到[E]/time-budget错误，任一fallback/非0exit/错误都不通过。PASS_COLD_READ_DIAGNOSTIC_ONLY仅代表隔离cold-read补丁26267dc6的调试路径预期匹配，不是官方原版能力、Muse Agent Relay或可信Person。

SHA256：8f506632a7d4d82ca78e3736783e378de514873bbc7f18b790b0419927a1602b。
