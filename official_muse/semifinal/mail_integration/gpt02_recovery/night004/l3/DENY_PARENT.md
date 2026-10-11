# Native same-ID update Deny probe

2026-10-12，GPT02准备供Root运行的最小负向用例。**PREPARED_NOT_TESTED；本聊天Kernel/Calendar调用0。** 固定中央源SHA `c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`，原生产main、SDK、Host及history均未改。

## 显式审批参数

`run.py --calendar-mutation-approval deny`只使实际生产update prompt对应的parent plan携带`fixture_approval=deny`；默认仍`once`。create仍Once及add→get，query仍Once及单次events，update仍get→原八字段expected的同ID update→get。原text/trigger/绑定/expected不改，reply/history不填字段。该选项交给GPT01实际Router审批fixture；不代表真人点击或真实用户日历授权。

新增两条parent只读诊断：`fixture/mutation-approval`返回显式配置；`fixture/approval-audit`从实际Kernel fixture root的`fixture-approvals.jsonl`读取真实Router行及文件SHA。后者要求实际Kernel、FIXTURE_ONLY和非symlink路径，不创建日志、不补审批、不修改history。

## 初始与新进程恢复

初始用`native_update_deny_probe.splash`：原Mail read/Memory/chat proposal建单一planned Goal→原create实际verified→手写旧Mail草稿→第二封Mail原chat proposal→原select同ID更新→原confirm实际Deny。必须看到真实Router恰一条同参数update拒绝；不能把模型文字作为拒绝证明。

Main必须保持unknown或有合法回执的failed，绝不能verified或completed。探针从实际history的当前turn原update工具行，经生产`calendar_agent_delete_receipt`核验Broker来源、owner/caller、kernel_persisted、turn/tool-call身份及error/cancelled，并精确核args_digest。没有合法回执就必须unknown；将来SDK真实落盘拒绝回执可接受failed。探针不造receipt，不赋失败状态。actual audit和Main保守unknown是分别观察的事实。

独立owner get核原八字段、单记录及events文件SHA不变；旧Mail正文保留、preview失效且0投递；重复update confirm/create/send不新增turn；无完成Goal/Run/Memory，原creation journal保留。实际观察写入专用`l3-deny-checkpoint.json`，其中legal_refusal_receipt仅是上述真实核验所得布尔值。

恢复用`native_update_deny_restart_probe.splash`，同一state/mail/Calendar fixture root，另起VM/Mail/Kernel进程。原boot读取持久记录，核同request的unknown/failed、原owner八字段/计数/SHA、旧草稿正文及无完成记录。重复确认必须0 turn/0发送；新chat仍能召回原Mail来源。恢复不重建Broker receipt，也不把checkpoint布尔值写入业务状态。

## Root执行入口

沿用`KERNEL_PARENT.md`的四个实际Kernel参数、公开signed candidate/config和`--kernel-test-frozen`选项；两个运行都显式添加`--calendar-mutation-approval deny`。此用例不传external-owner helper或授权参数，不做CAS外部编辑。初始成功后，恢复指向初始report的state_root/mail_root，并用相同Calendar fixture root。

已prepare的自有绝对根为`/Users/mima0000/.codex/worktrees/gpt02-mail-memory-recovery/Agent APP黑客松/build/`：

- 初始：`gpt02-night004-native-deny-prepare-c892-r1/executed.splash`，244个原生产函数。
- 恢复：`gpt02-night004-native-deny-restore-prepare-c892-r1/executed.splash`，322个原生产函数。

两份identity均核同c892源且非adapter函数字节相同。中央可按实际同源重新prepare到自身build；源若变化必须重新准备与签名，不借旧身份通过。

`deny-static-evidence/`保存plan32/32、源契约15/15及两份identity和manifest。旧source-contract-r1-adapter-error保留：静态字符串检查误把`receipt_status ==`当赋值，改用单等号匹配后通过；不是产品运行失败。所有检查是静态契约；真实Deny及两进程恢复由Root新out执行后判断。
