# 当前已核验事件删除接线提案

2026-10-11，GPT-02 own namespace。状态 **PARTIAL / PROPOSAL**。已准备 source-bound patch 与定向 Node fixture；共享 main、SDK、Bundle、用户存储和真实 Calendar 均未写入。未 GUI/model/Cargo，未读取凭据，未 push。

## 已核实的官方契约

当前 SDK `apps/calendar/bundle/tools.json` 已有 `calendar.remove_event`，必需参数为 **id + expected**，risk=destructive、confirm=host、auto_approvable=false。`host-service/src/lib.rs` 的 Event 是 id/title/start/end/location/notes/request_id/timezone 八字段；remove_event 将 expected 反序列化为 Event，并要求稳定ID和全部Event值与当前存储一致才删除。get_event 只能精确传 id 或 request_id 之一，输出 found/event，权威缺席为 found=false/event=null。没有新增 SDK API，没有直接向 owner-only Calendar service 发请求。

现有 Broker metadata 真实字段已有 `args_digest`；Kernel `octos-agent/src/tools/peer_host_tool.rs:416` 使用 `approval::digest_tool_args`，算法是递归排序键的紧凑 JSON→SHA-256，带 `sha256:` 前缀。因为 removed/found=false 本身不带事件ID，提案同时核此digest。固定八字段手工按字典序编码，再复用已存在 fs.sha256，无假排序或新Host接口。合同与Kernel源码完整SHA均见 identity。当前读取的 Broker canonical 仍只收四工具；**Root/GPT01 的合法第五工具 offer/manifest/ceiling 及 remove_event 回执映射是必要依赖，本聊天未修改或验证该Host扩展。**

## 用户路径与边界

只允许当前会话中本人明确选择的 Goal/plan/card/account/user/project/owner 均仍匹配、由 Muse 创建并精确读回的事件。通过原创建request_id与三项创建 proof（稳定ID、add/get call IDs、完整event）绑定自己的事件；不会按标题搜索或删除任意列出的事件。

1. 创建操作已真实 verified，行动链已明确选择该事项，进入「官方内置日历」。
2. 点击「选择删除当前已核验事件」，无Host调用，仅捕获现有稳定ID及八字段。
3. 核对「本人所选删除目标」后点击「确认删除所选事件」。身份/事项/版本变化会隐藏旧选择并拒绝确认；预览不展示完整内部binding JSON。
4. 独立有界 journal（calendar-agent-delete.json，最多32条）先保存/回读，再使用现有 octos.session.open→octos.turn.start。提示精确三步：get_event(id)并比较全部expected→remove_event(id,expected)且本人在宿主批准→仅removed=true后再次get_event同id。模型提示不是授权绕过或执行保证，Host原批准仍是门禁。
5. 「核对原删除请求」只读 octos.session.history。只投射同turn/person lane、同session、正确owner/caller/kernel持久化的真实收据，并检查get/remove精确args_digest、三步顺序和三个不同call/tool_call IDs。必须先完全一致的found=true，再removed=true，最后同id found=false且明确存在event:null，才 verified。仅remove成功至多accepted；缺失、冲突、重复或未知不算核验。

所有已有同ID删除请求都保留并禁止重发，包括取消或前置blocked；这是精简提案的保守限制。中断in_flight经实际恢复函数入口变unknown，不派发。身份或事项变化后不采用迟到turn/history；保留原请求ID与已知turn ID，必要时在宿主按原请求核对。没有调用Goal完成/重排/执行写函数；行动链显示「官方日历删除精确核验」仍明确事项未整体完成。

原创建binding和历史不替换。删除记录存在时，原 Calendar→Mail 的旧创建事实暂不能继续授权关联稿发送；只对现有 mail_calendar_verified 增加一个前提，原稿/正文/历史不删除。Mail其他功能排后。

## 最终身份及验证

- baseline：`e2f3ab878d7d7f77772507dc85e18cbef284cff86c2d4ee0a7e6639296107ea3`。
- proposed after：`6e0f2b7009367409173b990522e4078746eeaf9e1bc46dc649bdb8d2838ead6f`。
- patch SHA：`7b001acae667cdb6d8d88be863a63e0660418a0eaa1a88137c4b1f50bb396b6f`。
- 4个既有函数与Calendar UI必要接点改变，526其他既有具名函数字节不变，新增15个删除helper；不改原创建派发、model.complete和SDK。
- `evidence/calendar-delete-r7.json`：**88/88 PASS**，0外部调用、0Goal写入。提取23个真实提案/既有函数投影到Node，scope/UI/time/Host receipts为合成adapter，落盘只在临时目录。八字段、错ID/expected digest、缺event:null、乱序/重复/错误收据/取消、两级迟到、UNKNOWN/恢复/限额/保存失败及Mail/事项前提均覆盖。
- `calendar-delete-application.json`：临时副本实际 git apply --check/apply及最终SHA读回通过；中央source仍baseline；符号均为实际原定义或本次定义；UI旧选择有当前target精确守卫。
- r1-r3是Node语句分隔适配器错误；r4是容量fixture错误地放了空对象，改为有界有效合成历史。四份错误保留。r5 76/76和r6 88/88属于先前proposal/UI身份，不作为最终SHA；只r7对应上述after。

这是 **SOURCE_BOUND_NODE_PROJECTION_FIXTURE**，没有执行Splash VM、编译/安装新增Host、合法第五工具准入、原生删除批准或真实event删除，不能称真实删除通过。Root须在当前baseline相同的前提下应用此patch，准备新候选并按正常安装/本人批准做实测；源漂移则按四个具名函数和UI锚点重新生成，不强行偏移。

生成入口：prepare_calendar_delete.py --source <固定main> --sdk <已核SDK> --kernel <固定Kernel src> --out <own build/after.splash>。测试入口：test_calendar_delete.py --source <baseline副本> --out <新证据路径>；无Cargo/GUI/模型调用。
