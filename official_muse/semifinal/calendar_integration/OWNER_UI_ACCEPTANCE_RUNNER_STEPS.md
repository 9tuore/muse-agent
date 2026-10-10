## 最新实测：2026-10-11 06:32

r8冻结二进制baf55d24在隔离资料中实际完成普通owner UI创建、原ID改期、独立固定System events全字段读回、真实重启、二步删除、删除后及再次重启的有界列表为空。唯一事件ID ev-1791700320125；三个进程83319/83760/83859均remote quit/exit0，无迟到运行错误。六检查通过，状态严格为 OWNER_UI_COMPLETED_BOUNDED_READBACK_EXACT_GET_BLOCKED；不是精确get、权威不存在、Muse Agent Relay、模型选工具或可信Person批准通过。

原r8-r1超时等视觉哨兵、r8-r2 notes位于可滚动底部而不可见均在Save之前停止、events空、0写；失败未删。最小驱动修复仅在原ScrollYView所属pane内最多14次正常滚动，Save/Delete仍单次投递、不重试。中央实际看全部九张OS截图；公开三张与独立视觉回执在 ../evidence/native-full-shell-r1/calendar-r8-owner/，完整原始日志与截图保留 build/runtime-closure-owner-ui-r8-r3/。重启后的最后一张默认显示10月11日，10月12日缺席来自目标日期的独立有界events结果，不能用截图宣称权威不存在。下文为原准备记录和可复跑边界。

## 中央实际结果：2026-10-11 06:10

r7已完成真实release构建，SHA `50d545c2…`。R1启动前Rinx重复mkdir失败；R2早期只读抓帧404；R3 Calendar正常可见，但System read尚未声明；R4显式现有 `--test-action system-chat` 显示“No model provider is set up yet”，合法read在声明预检查停止。所有进程正常退出，**零日历写入**。这不是get grant拒绝或Calendar不存在的证据，更不是CRUD/Muse Relay通过。独立报告 `../evidence/native-full-shell-r1/calendar-r7-owner-read-result.json` 与实际OS图均保留。

runner现在允许 `--read-only-system-chat`，仅启动已有System聊天界面和有界查询，不发模型prompt、不配provider、不写事件。r7原入口的冷加载阻塞正作为隔离小补丁评审，未改正式Shell或权限；r8尚需实际构建/运行证据。真实get仍不在System固定grant，不能补造权威缺席。上方最新结果覆盖以下执行前交接。

# Owner UI合成runner交接（未运行）

run_owner_ui_acceptance.py已准备，仅Python AST语法检查通过；没有执行runner/import smoke、Cargo、GUI或模型。运行结果仍未验证，不宣称实际窗口/CRUD通过。源接口复核：SDK lib.rs:5335/5394–5399的--test-action launch-<id>→launch_app；既有run_calendar_readonly.py使用--remote=PORT --test-action launch-calendar；phase2/tests/remote.py的真实/snap、/click、/k、/t、/g；Makepad remote.rs /s字段pid/w[i]、/event数据、raw PNG与w；host_tools/mod.rs:209–239只读system-call及固定System Calendar grant；C owned-window-id.c实际按CGWindowOwnerPID筛选窗口，原可执行工具保留。没有复用旧journey的直接私有store oracle。

## 中央唯一队列步骤

1. 等唯一Cargo97204/r7构建完成，选已核验完整Shell二进制，必须同目录有octos-kernel及receipt；给--binary-sha256完整实测SHA。确认没有其他GUI/Kernel测试占用，选择空闲remote端口和新的ROOT/build直接子目录。稳定PID503保持。
2. 中央运行一次下面命令。runner核对Shell SHA、Kernel SHA与b0759a5 revision、端口空闲，创建700新home，不复制任何profile/Settings/consent。自建进程仅启动官方Calendar owner，非MuseNative，不点击任何Allow。
3. 初始remote/自建PID OS截图后，runner打印输出目录与initial-visual-reviewed.txt路径并flush，最多120秒等内容精确为VISIBLE_REVIEWED（无换行）。中央先实际view_image检查自建PID OS截图中的日期网格可见，再写该测试哨兵；未满足则PARTIAL停止，不写日历。report记录initial_pixels_reviewed及测试边界：这不是Person/consent或业务批准，不改变授权。随后仅读合法System calendar.events。合成日若非空、读取拒绝/未知、截图失败、门禁则停止。正常控件输入唯一“MUSE-N002-20261011-A 合成联调”，2026-10-12 15:00–15:30，Asia/Shanghai，Muse synthetic acceptance，notes空；不触发notify。UI不填写request_id，缺省空不冒充幂等key。
4. 单次Save后用合法events严格核对全部Event字段并获得ID；缺ID/错字段/重复/达到200条cap即PARTIAL，不继续修改或删。正常Edit仅改16:00–16:30，单次Save并核同ID。等待自建父进程实际退出，同home重启，合法events核同ID/无重复，再正常日期控件12 •选日/进入事件；控件不可见则停止，不注入focus方法。
5. 第一次Delete event只出现Confirm delete，合法events应仍同ID；第二次正常Confirm delete只发送一次，查询该有界日无记录。再实际重启做有界列表缺席检查。精确get与权威absence始终BLOCKED，Muse Agent Relay NOT_TESTED、可信Person NOT_CLAIMED。实际PNG仍须中央视觉复核。

```sh
# binary与sha由中央刚完成的候选提供，port由中央选择空闲端口；out必须全新。
python3 '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/calendar_integration/run_owner_ui_acceptance.py' \
  --binary "$calendar_shell_binary" --binary-sha256 "$calendar_shell_sha256" \
  --port "$calendar_remote_port" \
  --out '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/owner-ui-acceptance-new'
```

## 不确定与停止边界

普通UI输入由WindowRemote固定实际w并沿用Remote真实文本输入/值回读；覆盖click为单次delivery，不复用原click的帧失败retry。Save/Delete/Confirm delete均不会自动重发。异常先尝试一次合法只读listing并保存实际reply（不造CallID，operation UUID仅runner记录），然后退出；若创建已发生但后续PARTIAL，保留同home和真实event，不自动清理未知事件，不另开新home重复该批准事件。central应先只读核对report后决定。

只发送固定System events工具，不尝试get，也不改System grant、native grant、consent或审批规则。remote为UntrustedInput，任何权限/可信确认门禁HUMAN_REQUIRED停止。不是正式Muse Relay全链测试。

输出report.json保存每操作UUID/时间、进程PID/启动与退出、实际reply与eventID、截图窗口/退出、错误；shell-N.log为自建stdout/error日志。remote PNG绑定实际w，OS PNG使用已观察C owned-window-id对自建PID筛选；图片头核对，视觉仍REQUIRED。结束仅/quit在核实自身PID后发送；失败仅terminate精确Popen子进程，不杀进程组/所有Shell/503，也不另启或杀Kernel。shutdown记录remote_quit是否成功、原始应答、fallback、exit及时间。任何fallback、非remote_quit退出、非0exit都停止后续重启并记PARTIAL_SHUTDOWN；父进程未退出为HUMAN_REQUIRED。每次退出后检查迟到[E]/time-budget错误，阻止继续重启；最终汇总所有日志与所有shutdown，任一异常均不能成功。运行home/原始日志仅写新ROOT/build目录，源码目录只保留runner/说明。

脚本SHA256：c340492057bc603b737c2e1806653fecdf16a1ca19098d4c1539f8d38c24a73d。
