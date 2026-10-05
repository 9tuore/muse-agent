# rc26-r1 状态询问解释后缀独立复核

状态：**FIXTURE_PASS_RC26_R1**。2026-10-05T18:36:01.424568+08:00。

真实锁定CardHost、实际生产路由与候选生成/修改/存储，合成Host模型回调，不是真实GPT、邮箱或日历动作。3窄组52断言PASS，另10实际候选持久读回PASS。

原失败输入完全保留：只依据记录回答：日历工具报告创建失败，没有系统回执，也没有独立读回。现在能向用户说日程已经安排好吗？请解释。

rc25 baseline将它误判calendar_candidate，邮件/日历5种其他解释/原因后缀也错，6输入共18路由/status/schema断言FAIL。rc26同原输入与同probe-v2实际复测全部reply，问号后“请解释／请简要说明／请说明原因／请解释原因／请分析原因”识别正确；无后缀普通问句正常。明确Mail/Calendar/Goal与“日历结果已完成吗？请创建下一条日程。”动作对照不被误当解释。

Mail/Calendar用生产send_chat→合成model callback建候选→明确修改→第二callback更新同ID/revision2→持久读回各9PASS。Mail保原to/subject只改正文，Calendar只改地点保原start/end；无外部动作。这里只测试路由/schema及synthetic候选，不能证明真实模型已回答“不能声称完成”。

初始Calendar准备输入使用常见en-dash“15:00–15:30”，在旧格式guard被拒，实际持久assistant是“请补充明确的开始和结束时间。”：`CALENDAR_SETUP_NOTE.json`记录。这是独立输入支持缺口，不是status词误判。首次失败保留；r1候选对照用既有支持“15:00到15:30”。**仅换setup不算修复常见en-dash支持**，Root正在r2最小修正，下一冻结将用原en-dash准备输入及控制复测。本r1不称该缺口修复。

readable `250584f959979f6468e508affc04431f0620f1cbc0bb93dd50334e85bbe06671`；compact `e76a619751eae46a7caefdb6d23a97869504ebfd52516b0b764910ce1e623f44`。源码仅chat_status_question regex与About版本变化，其余全业务字节相同。未跑101全套或模型题集，未改主/Host/权限/预算/Git/安装/账号。

`CANDIDATE_READBACK.json`独立读取两候选各5检查：单候选、revision2、candidate状态、明确字段和持久成功确认。第一次外部读回草稿错误使用不存在actions.json的默认true表示“零动作”，不能作为磁盘证明，原稿保留`CANDIDATE_READBACK_FIELD_REVIEW_INITIAL.json`；现已替换为实际持久assistant确认。零动作另有实际runtime actions/runs断言，不靠文件缺失判断。

原`rc25-baseline-r1`与`rc25-baseline-v2`全部保留，固定结果`rc26-fixed-r1`。最新机器摘要`PUBLIC_RESULT_R1.json`，`SOURCE_DIFF.patch`/`BYTE_BINDING.json`。自己启动的Host全退出。Root负责真实同问模型与后续r2。
