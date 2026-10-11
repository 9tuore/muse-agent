# NIGHT-004 Calendar JSONL helper

可执行文件：

`/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-calendar-history/target/debug/gpt01-night004-relay-jsonl`

调用：`gpt01-night004-relay-jsonl /absolute/isolated/host-dir`。参数必须指向自有或中央 worktree 的 `build/night-004` 之下已存在且带 `FIXTURE_ONLY` 的隔离目录，例如中央 `build/night-004/calendar-gui-r1/state/apps/.host`。helper不创建标记、不复制DB。calendar/events.json/cards.json及calendar目录不允许symlink。写入与读取都走此范围门禁，不能指定其他state目录。

stdin每行一个JSON，stdout逐行一个JSON并flush；进程支持多个请求和EOF正常退出。单行上限1MiB。bad JSON返回bad_json，进程继续；启动root不合格时stderr给实际原因且exit2。

```json
{"method":"calendar.add_event","args":{"title":"NIGHT004 synthetic","start":"2026-10-13T15:00","end":"2026-10-13T15:30","timezone":"Asia/Shanghai","location":"Fixture room A","notes":"Synthetic notes","request_id":"night004-stable"},"scope":{"caller":"card.muse-goals","owner":"os.calendar","account":"fixture-account","fixture_consent":true,"granted":true},"fixture_approval":"once"}
```

支持calendar.add_event/get_event/update_event/remove_event/events，以及相同不带calendar.前缀的方法名。update需要完整替换字段和actual get_event返回的完整expected快照；remove需要id和expected。get_event使用id或稳定request_id二选一。add稳定request_id和相同数据可重试，真实服务决定是否reused；数据冲突返回真实错误。

每次请求须显式scope对象。fixture_consent/granted默认false，caller默认card.muse-goals，owner默认os.calendar，account默认fixture-account。可设置signed_out:true、withdrawn:["muse-goals"|"os.calendar"]模拟已撤下状态。这些是synthetic scope输入；实际授权判断由未经修改的Relay/Catalog执行。此harness没有另造官方Scope类型，也没有签名admission、账号或本人同意证明。

三种写方法必须显式fixture_approval:once或deny。实际Event::Approval→真实Router pending sheet→TEST sheet_tap→实际Decision→ApprovalAnswer；没有standing/developer blanket approval。只有当前owner/tool/完整args匹配且实际批准为true才提交Event::Call。revoke_after_approval:true在真实Router答Once后撤掉Catalog grant，再由实际Relay拒绝dispatch。deny/refusal不执行owner服务。

返回字段：

- is_ok/data/error：可直接给GPT03 VM callback；data仅来自实际ToolOutcome或服务结果。error含kind/message。
- result：原始真实Relay ToolReply结果（call_id为明确fixture transport ID）；审批/协议错误没有伪造Relay成功。
- approval_trace：本次实际Router sheet/请求/args/decision；fixture_gesture明确true。读取/提前拒绝时为空。
- executor_calls：本次实际owner executor调用记录；被权限/schema挡住或审批拒绝时为空。
- store_event_count：实际events.json解析后的条数；坏/缺存储返回null，不冒充零条。
- fixture：authorization/scope/approval_gestures均synthetic，kernel:false；relay_logs记录实际拒绝原因。

GPT03父driver可保持该子进程，收到MUSE_VM_REQUEST的真实Calendar低层调用后写一行、flush、读一行，再转发is_ok/data/error。VM的octos.session.open/history、octos.turn.start等必须连接真实Kernel/Broker；此helper对这些方法返回fixture_protocol错误，没有KernelHistory或Muse验证receipt生成器。不可用fixture call_id当Kernel调用证明；仅Rust helper成功不能记同候选L3应用链PASS。GPT03 VM主业务函数身份仍按其CLI_PROTOCOL.md核对。

readonly GUI reader保持read_calendar.py（commit46f3a773），它兼容原owner/method/args协议，并只读同一标记.host。此次JSONL helper是独立接口，不替换该reader。

构建复用自有小target：先有prepare.py/prepare_relay.py阶段，再python3 prepare_jsonl.py，nice -n10 cargo build --offline --locked --manifest-path OWN/build/gpt01-night004-calendar/relay/Cargo.toml --target-dir OWN/build/gpt01-calendar-history/target -j1 --bin gpt01-night004-relay-jsonl。不使用中央target。binary和业务源码SHA见HELPER_IDENTITY.json。

验证：run_l4.py首轮25步PASS，三次JSONL进程重启，另一个真实CalendarService进程作synthetic外部编辑。存储坏JSON与实际.tmp写失败均拒绝且原bytes不变；稳定重试未造重复event，最后删除/重启count=0。证据L4_RESULT.json/l4-run-r1.log；真实文件错误用自有.events-PID.json目录占位触发，未伪造errno。首次编译E0277/E0382日志保留，修正Option/borrow后成功；审批trace增量构建3.03秒。
