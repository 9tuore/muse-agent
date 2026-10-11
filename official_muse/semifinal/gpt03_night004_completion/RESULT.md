# NIGHT-004 native Calendar → Mail 完结

2026-10-12，GPT03自有worktree。**PARTIAL：缺口实测、完结补丁及VM检查通过；中央集成，GPT02负责独立收件产物及parent full-chain/重启。** 未启动Host/GUI、未改共享main/SDK/bundle/target/生产资料、未push。

## 调用证据与缺口

基线中央HEAD `961d05ec9755abb3436aa2c6c38914427ae20f5d`，main `dabfe65b…`。

- 基线main6232的 `mail_verify_received_step` 保存verified Action、draft核验ID/time和 `MAIL_DELIVERY_USER_CONFIRMED`，6257调用 `mail_finish_linked_result`。
- 基线6115–6116的native分支只return `mail_calendar_current(mail_draft)`，未建立Run/结果/完成Memory。1065的改期authority又只接受planned Goal完整快照。
- `counterexample.splash` 实际经过生产preview/send/receipt/user verification：10项6通过/4失败；新建和同ID改期后Mail draft/Action已verified，Goal仍planned、Run0、完成Memory缺失。日志 `build/gpt03-night004-completion/before-r2/`。探针未直接赋值verified/completed Goal、Run、Action或Memory。

## 可应用补丁

`native-mail-completion.patch` 只替换 `mail_finish_linked_result` 和 `calendar_agent_update_current`，新增 `mail_finish_native_result`、`mail_finish_native_step`、`mail_native_completion_matches`。legacy、core存储/Run/Memory、Mail发送/回执/收件声明入口及GUI widget字节不改。实际apply后与冻结候选字节一致；脚本对所有既有生产函数逐字核对。

| 身份 | SHA-256 |
| --- | --- |
| 基线main | `dabfe65bbb859e51db5cc2b9eea59855024af927f8bfbe548fa86f50ded95a6d` |
| 最终main | `8ad9a79987a651909a653a6a5b3798bdfd086096ea8842450685b879170c3ff1` |
| 最终patch | `7672db9d37d223c891cde7e6d1fc174455174df501ac61d47f8d4f908873ab7e` |

必须匹配当前user/accounts/project/owner/chat所选Goal、最新verified Calendar authority及revision、稳定event ID、原独立verified Mail Action、精确payload和已保存的本人收件声明。accepted/UNKNOWN、缺声明、旧revision、其他Goal/user、声明request被改写均拒绝完成。

先冻结并回读完整authority/planned Goal/payload/声明产物，再经原core API建立同版本Run、回读含Run ID的产物、完成Run/Goal并保存摘要绑定来源及verified_result Memory。原Action仍是发送时的独立身份，不改旧证据。Run后写失败按原Mail request恢复同Run；重复完结不增Run/Memory、不发Mail。完成来源已有摘要时，产物改写会阻断authority沿用；保留历史记录。

**证明语义：生产入口仍是本人收件端核验声明，活动与产物注明“非宿主自动投递证明”。本补丁没有自动读取独立收件产物的生产API。GPT02 driver必须继续先读独立receiver产物并核对message ID/收件人/正文/attempt，再调用 `mail_verify_received()`。若要求生产入口本身读取独立产物，该接口合同及实现仍缺失，不能把本补丁称自动收件证明；已发出语义澄清，未收到选择，按现有接口交付提案。**

## 已执行检查与版本区别

| 检查 | 结果 | 源及原始日志 |
| --- | --- | --- |
| 完结、负例、恢复、幂等、摘要、准备声明篡改 | 33/33 | 最终`8ad9a799…`，`build/gpt03-night004-completion/final-completion33/` |
| 原改期99、候选归属11、Mail19、receipt8、Calendar restore10 | 147/147 | 前一源`f964dafd2a961e58d7170a4147fff081f04456815e3de6db14ee82e16551fbf1`，`update99-final/`、`edit11-final/`、`mail-restore-final/`（同上build父目录） |

最后两项仅加强已存准备产物的声明/schema/长度检查；按Root最新收口指令，不重复147项，中央接最终SHA后复验。前一完结31/31在 `guards-r3/`，原字段/JSON顺序/边界错误日志保留。最终33检查stderr为空，业务状态由生产函数写入；transport、历史、IO、UI及人工选择为合成边界，不是SMTP、收件、Kernel或full-chain PASS。

33项包含新建/同ID改期完成，accepted/UNKNOWN、其他Goal、旧revision、其他user、prepare后选项变化、缺落盘声明、两阶段写失败及同Run恢复、不重发/幂等、完成后authority、摘要改写/原字节恢复、准备声明request被改写及原字节恢复。所有目录保存真实executed源/stdout/stderr/report；runner未重建。

## 重现与接收

`prepare_patch.py` 从自有 `build/gpt03-night004-completion/baseline.splash` 重建patch及 `proposed.splash`。运行已有 `official_muse/semifinal/gpt03_night004/run.py`，参数为 `--source <上述冻结源> --runner build/gpt03-night004/target/debug/gpt03-night004-vm --probe <本目录probe.splash或counterexample.splash> --out <新的自有build目录>`；基线用counterexample，候选用probe，旧输出不能覆盖。

只读GPT02现场改动集中在l3 driver/Kernel RPC/native initial和restart probes，没有相同业务函数改动。本单元交付completion patch；其driver沿用生产 `mail_verify_received()`，不要fixture写完成状态。中央负责接收及同SHA VM/签名，GPT02负责parent initial/restart和新聊天completed Memory recall。直接消息未发送：消息工具要求人类直接授权，当前只有其他聊天委派；分工通过本交接接收。

本单元未做真实parent/restart/GUI。初次产物写失败的重试测试直接调用生产完结入口；现有native UI恢复按钮仍受空link_run_id限制，旧行动链“尚未整体完成”文案也未改。正常入口自动接完结；失败后的UI重试及文案不能冒充已验收。
