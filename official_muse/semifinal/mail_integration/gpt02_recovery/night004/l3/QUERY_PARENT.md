# Native L3 query → create → update

2026-10-12 GPT02仅补此前缺失的独立query turn。原full-chain、restart及CAS父驱动保留；不改生产main/SDK/Host。**PREPARED；静态plan26/26、源/原流程保留12/12 PASS；实际query/整链NOT_TESTED，Root执行R8。**

现场固定main SHA：`e7d665dd7f466e454aeca071895273e81549af169f8613c3490671a3cf8cca20`。自有冻结副本build/gpt02-night004-l3-source-r7-central-e7d/main.splash。prepare提取初始272、恢复317原生产函数，非适配函数归一transport后逐字相同。query-static-evidence保存4个静态report/identity及SHA，不能称真实query回执或Kernel通过。

## 正式入口与最小新增

主源878的calendar_agent_submit(text)转879的submit_bound(text,nil)：自行分配请求ID、真实session.open、原prompt+trigger app→turn.start→自动calendar_agent_history。query没有额外私有API；533的历史回调只接受真实person lane/current turn和原receipt validator，统计query_only；1641的settle_if_resolved仅在turn_completed、所有read工具成功且未核验数0时归档。UI11839的“回读并结清当前请求”设置history_settle=true后调用同一history函数。probe完全沿用这些生产函数，不写idle/verified或伪造history/lane。

full probe建立首封Mail来源/候选/单一planned Goal后，在原create提交前调用native_query_before_create。用户查询文本明确只读，带`精确 calendar.events 参数：{}`。parent只从实际生产生成prompt解析该DTO，计划只有一次calendar.events；原text/trigger/其他绑定字段全部保留。实际工具Schema来源为中央sdk/apps/calendar/bundle/tools.json：from/to可选string≤32、limit可选整数1..200、无额外字段，因此{}为合法query。模型选择为fixture；工具、结果和history必须真实。

query mandatory checks：实际turn完成且无binding；真实history中恰一calendar.events、无其他工具；原生产receipt validator通过，args_digest=实际sha256({})，result.data.events确为array。读取真实owner计数必须仍0，Goal/Run/Memory原文本无改。通过真实history回读/settle归档query并恢复idle；归档请求/turn持久保留。之后原submit_candidate执行单独create turn，仍严格add/get，request/turn与query不同。query返回失败/未知/无真实回执就停止，不越过门禁进入create。

checkpoint新增实际query_request_id/query_turn_id；restart经原calendar_agent_boot读取previous_requests，必选保存的无binding turn_completed query。其他Mail/收件声明/完结/Memory/行动链检查不删。独立receiver精确核验仍是调用生产mail_verify_received的前置门禁。

## parent计划与边界

kernel_rpc新增query marker路由；混合query/create/update marker或重复marker拒绝。query只允许正式events DTO，创建仍只有add→实际返回id的get，更新仍get→原expected update→get，CAS路径不变。fixture_approval沿用Once，只适用于GPT01当前resolved plan的实际owner/tool/args匹配审批；query计划无写工具，未给写入standing授权。完整payload/history不编辑，尤其不填lane或kernel_persisted。

静态plan26项包括原15项以及query-only、原文/trigger/opaque、过滤字段、非法limit/type/额外字段/混合marker拒绝和create不夹events。源检查12项含正式入口/回调/settle/创建guard逐字提取及旧full/restart步骤保留。这些调用数为0；Root收到R8真回包后才能报runtime结果。

## Root执行

沿用KERNEL_PARENT.md四显式Kernel参数及冻结二进制选项。初始probe仍native_full_chain_probe.splash、恢复仍native_restart_probe.splash；CAS两probe不改。

已prepare：GPT02/build/gpt02-night004-native-query-prepare-e7d-r1/executed.splash；恢复GPT02/build/gpt02-night004-native-query-restore-prepare-e7d-r1/executed.splash。两者来自同e7d，identity给逐函数/全局SHA。中央copy/cherry-pick后也可用实际e7d源重新prepare进入中央namespace，再按原run.py运行；新Kernel root和公开signed candidate/config由Root提供。原L3失败日志仍保留。实际执行需R8正式open_conversation/trigger桥，不使用旧open_context、不parent造lane。
