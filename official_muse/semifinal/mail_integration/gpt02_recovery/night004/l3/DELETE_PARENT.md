# Native exact delete: parent准备交接

2026-10-12 GPT02，**PREPARED_NOT_TESTED**。固定Main `c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`，Root已有公开签名候选`cdb1412b14a25fdbb8f97681e7fe344c855a0adaac50c26ded5eb17f876108d7`。本聊天Kernel/Calendar/GUI/Cargo调用0，不改Main/SDK/Host。

## parent计划

实际`calendar_agent_delete_confirm`生成marker **`2. calendar.remove_event 参数：`**；parent仅解析其原`{id,expected}`。expected必须保留所选事件八字段及原request_id，外层id必须等于expected.id。计划固定get(id)→remove(id,原expected)→get(同id)，fixture Once由真实Router对当前resolved plan的owner/tool/args匹配后决定。没有把expected替换为新get结果，没有编辑text/trigger/其他payload或reply/history。

query/create/update原三个分支体逐字一致；实际c892候选参数下，原parent与新增parent的query/create/update/update-Deny outbound JSON字节一致。默认Once不变；既有update-Deny选项仍只作用update，本正向删除用默认Once。

## 原生探针

`native_delete_probe.splash`复用已交付Deny探针的原Mail read/Memory/chat候选及单一planned Goal→生产create_verified前缀。之后生产delete_select冻结同ID八字段→delete_confirm→自动delete_history核验；必须verified且保留创建请求。实际history须两get/一remove、原生产receipt validator及digest通过、removed:true和found:false/event:null；实际Router audit须恰一条匹配remove的Once批准。

独立owner get同ID不存在，实际events计数0；原creation journal及Goal/Run/Memory不变。重复select/confirm/create不新增turn，0 Mail compose/review/transport。原ac_projection必须出现同删除request ID的“官方日历删除请求”和“官方日历删除精确核验”两个已核验节点。checkpoint仅保存这些实际观察，不赋verified或Goal完成。

`native_delete_restart_probe.splash`用于新VM/Mail/Kernel进程，复用初始state/mail/Calendar root。原boot读取同delete request/turn/event/expected、verified及三call proof，独立owner仍0记录，重复确认0 turn/0 Mail，原事项删除行动链节点恢复；无完成Goal/Run/Memory。新chat可召回Mail来源。不重建Broker回执或注入历史。

## Root运行

沿用`KERNEL_PARENT.md`四个显式Kernel参数及冻结二进制选项，使用匹配c892/cdb的实际config；不传external-owner helper/授权，不做外部编辑。保持默认Once。根目录是GPT02 worktree的`build/`：

- 初始：`gpt02-night004-native-delete-prepare-c892-r1/executed.splash`，232生产函数。
- 恢复：`gpt02-night004-native-delete-restore-prepare-c892-r1/executed.splash`，318生产函数。

Root可将这两个probe按同一实际c892重新prepare至中央build；初始全部检查通过后，恢复指向初始report的state_root/mail_root及同Calendar fixture root。源码变化需重新prepare和签名。run.py报告实际probe status；删除用例不扩展完整正向链的full_chain_status。

静态plan44/44、源契约23/23及Python AST通过，identity逐函数/全局SHA及manifest见`delete-static-evidence/`。最终plan输入来自实际c892 `native-l3-central-r4/initial/report.json`；早期旧源parser输入报告保留。prepare保证非adapter函数字节一致；未进行Splash VM解析或真实删除运行，不能据此宣称原生删除成功。
