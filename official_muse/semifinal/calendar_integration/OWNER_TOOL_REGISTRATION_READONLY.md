# Calendar owner工具声明冷启动只读定位

本轮只读，未GUI/Cargo、未改runner/SDK/准入/grant/身份。中央r2现场：PID70947、OS2846网格可见、quit0/无E/0写为中央报告；早期/g404与System read声明拒绝保留。

## 原因

正常Calendar owner UI的calendar.view通过CardApp services::pump→CalendarService运行，不要求Relay catalog存在工具声明。apps.rs:391 register_calendar_services只注册Host service/card回调，不declare。因此--test-action launch-calendar能显示UI，尚不能推出System test已可读。

host_tools/mod.rs:214–221的system_call_test先owner_of再declaration(risk=read)。它没有ensure_loaded；失败时日志“a test call runs only a declared read tool”发生在真实System call/grant检查之前，不是calendar.events grant已拒绝的证据。

真正登记路径：script_apps::load:179读取admitted_bundle:197（官方system::prepare与同一apps root），from_bundle解析工具；install:157→declare与set_executor。ensure_loaded:488只对实际card.<manifestID> namespace且catalog未知时加载，不能外部伪造注册消息。

## 最小现有合法UI路径

在中央自建fresh home Shell、实际已可见Calendar owner上，普通按F8打开系统聊天，不填文本、不发送、不点Allow。SDK lib.rs:6763–6769的bare F8→system_chat::toggle/open；system_chat/mod.rs:323–328发Command::Open，session.rs:379/485–498连接现有Kernel UI链并发session/open。成功Pending::Open:625–628→sync_tools:244–248→ShellSystemHost::declarations:99–103→ensure_loaded("card.os.calendar")。此处加载官方owner声明和executor，不增加System grant，不准备Calendar Agent或伪造Person。Command::SendNoted:408才启动模型turn；仅打开和load_history不发送模型请求。

中央可用已存在Remote API，仅普通键输入（w必须为/s已核对自建PID的实际Calendar窗口ID）：

```python
# remote为已核对自建PID端口的Remote；calendar_window为/s.w[].i。
remote.request('/k', k='down', c='F8', w=calendar_window)
remote.request('/k', k='up', c='F8', w=calendar_window)
# 等待系统chat正常打开/注册；不输入、不Return、不发送。
remote.request('/event', data='system-call:calendar.events {"from":"2026-10-12","to":"2026-10-13","limit":200}')
# 只依据新日志里的真实reply确认；不是依据窗口出现。
```

另有真实启动选项--test-action system-chat（mod.rs:678–682）等同open，但本轮不建议为此重启已有Shell；禁止system-chat-send、ask-send或直接调用ensure_loaded/declare。F8远程仍UntrustedInput，不算Person/consent。

**条件限制：** sync_tools只在opened/link有效时调用；fresh home若session/open返回NoProvider/NoKernel/错误，则可能根本未加载声明。不要为通过而复制生产Settings/密钥、配置模型、给grant或点consent。保留PARTIAL/HUMAN_REQUIRED，停止owner写入。该路径源码已存在，当前fresh home是否成功需中央实际只读验证，未宣称已执行/可必然成功。

成功加载后依然仅使用grants.rs:188固定events/add/notify System grant，get不在集合仍BLOCKED。读取成功应核真实reply.data与有界events形状/ID；owner声明存在不等于Muse服务注入/Agent Relay通过。若输入普通F8被某模态/门禁阻挡，HUMAN_REQUIRED，不能绕过。
