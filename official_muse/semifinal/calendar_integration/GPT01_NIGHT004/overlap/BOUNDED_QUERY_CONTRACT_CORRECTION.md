# Bounded query fixture contract correction

Root原 `build/night-004/overlap-8227-contained-r1/run/report.json` 是真实 FAIL，只有8条checks，失败项仅 actual_bounded_query_contract。执行了两次generic query，尚未建立新候选／进入candidate preflight。原report/VM/Kernel/audit/owner均保持原样；此文件不是对原report的修补或PASS声明。

实际第二次请求是 `{"from":"2026-10-13T16:10","limit":200,"to":"2026-10-13T16:20"}`。模型resolved args原样相同，canonical digest `sha256:5da0f1329b98b32e764d6e1f6b4f35a0f05bb2d3c8bfad10a919da8976a69e3b` 与Broker receipt和call/done audit三处一致。实际turn `b564fcb7-27cd-434d-8bf5-67f4c966bc68`，toolcall `fixture_call_2`，call `ptc-0498995c64d44e39a8e1e67a81b9ae60`，person lane、kernel_persisted、terminal ok。原16:00–16:30事件返回1；owner count1/SHA103a5a86保持原值。

对应官方源码 `apps/calendar/host-service/src/lib.rs` SHA `81b904807a886397cdf9401fb1b5e66cd25befbb3d11bef8cb99bde51979dd86`：

- line112–116：local_stamp(true)取end，false取start；显式timezone转到device Local后stamp；end不存在则退到start。
- line128–145：parse_time接受无秒的 `YYYY-MM-DDTHH:MM`，无偏移输入视作device local；RFC3339输入换成Local，stamp输出分钟。不是丢掉了from/to；当天宿主只读观察为CST/+0800。
- line308–320：from/to各经parse_time/stamp；过滤是 `local_stamp(true) >= from` 且 `local_stamp(false) <= to`，即**含端点重叠**，不是完整包含。16:30>=16:10且16:00<=16:20，因此contained返回1正确；adjacent从16:30开始同样被inclusive equality选中，应返回1。
- line440–444：CalendarService把ServiceCall原args直接传给handle。

Relay与adapter也核对：relay Target::Bus用call.args.to_string()（line853）不改值；实际Calendar经script_apps执行器，scoped_args对非Mail返回call.args.clone()（line251–254），随后用该args创建ServiceCall并dispatch（line403–407）。本地fixture model也按resolved args原值生成tool arguments。没有找到把此16:10/to16:20改成全列表的转换；真实digest和audit已排除“只发了limit”的解释。

我先前读反true/false，导致contained/adjacent两个小入口把bounded-match写为0。这次最小修正只将它们设为1，并修正文档。Main仍保持精确 `{"limit":200}` 全列表preflight和半开区间比较：`event_start < candidate_end && event_end > candidate_start`，所以adjacent应是0个产品conflicts；官方bounded返回1与此不矛盾。SDK/Main/Relay/model/原始结果不改，不启动Kernel。新closure与原failure分开，状态仍PREPARED_NOT_RUN，Root使用新fixture实际重跑。
