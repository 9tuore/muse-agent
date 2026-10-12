# ZC05可直接使用的模型控制与关键GUI流程

全部响应均为明确fixture，实际GUI/SDK/Kernel/存储结果独立验收。当前rc8 Root Source为`f00c963bcdf0a9a8b614083a40134de570a92ff08a9b53af47b151a48afaa50f`，身份见flows/source-function-identities.json。与旧947比较，本文件依赖的18个函数中17个逐字未变，send_chat仅两条候选提示改为明确打开「来信与结果」；其余源码差异仅ResultContent选中标签颜色。模型schema所在函数全部未变，39个样本内容保持不变，新静态核验78/78见evidence/flow-sample-contract-f00.json；未执行GUI。候选生成后按提示打开「来信与结果」再核对内容，不能只看到行动链就判定候选缺失。

旧947初始生成器拒绝旧SHA的记录、原始身份和78/78报告保留：evidence/flow-catalog-947.json、flow-source-functions-947.json、flow-manifest-947.json和flow-sample-contract.json；947时18个相关函数与caa逐字一致。新旧实际比较见evidence/rc8-f00-source-schema.json，不覆盖旧失败或原始记录。

## 控制与三轮重复

ROOT为Root服务实际双标记state，不是生产目录。每个GUI操作**前**配置对应文件：

```sh
python3 official_muse/semifinal/sprint005/zc02/control.py --root "$ROOT" model \
  --json official_muse/semifinal/sprint005/zc02/flows/chat-r1.json
python3 official_muse/semifinal/sprint005/zc02/control.py --root "$ROOT" status
```

flows/catalog.json列出39个控制文件。r1/r2/r3是三次独立验收重复，名称/资料/时段各不相同，避免上一轮结果冒充本轮；单轮里的t1/t2/t3是多轮对话步骤，勿混为243格的三次重复。同profile上按UI删除不需要的对话或另用全新合成profile，避免16会话、每会话8候选、约256消息容量阻挡；绝不直接删改业务JSON来重置PASS。

| 实际调用/入口 | 控制文件 | response精确字段 |
| --- | --- | --- |
| Chat普通问答 | chat-r1/r2/r3 | reply |
| Chat一次性Goal计划候选 | goal-plan-r1/r2/r3 | objective, source |
| Goal页“请模型给建议” | goal-summary-r1/r2/r3 | summary（≤45 Unicode/180 UTF-8 bytes） |
| Chat Calendar候选 | calendar-r1/r2/r3 | title, start, end, time_zone, location |
| Chat邮件候选 | chat-mail-r1/r2/r3 | to, subject, body |
| Mail页“模型起草（需先读取一封邮件）” | mail-accept/decline/time-r1/r2/r3 | subject, body；**不能有to** |
| 邮件日程整理calendar_model_candidate | mail-calendar-policy-r1/r2/r3 | 五日程字段+question, policy, duration_changed, duration_quote |

上表响应不能包intent/proposal；Chat回调本身包装动作。Mail复杂policy只用于确实进入calendar_model_candidate的路径，不能塞给Chat五字段schema。未来日期均明确2026-10-13/上海+08:00，模型只提候选，不表示查空闲/创建/发送。

## A. 普通AI对话 → 用户记忆保存/更正/遗忘

1. UI新建对话，选择项目S005-P1与归属合成归属1；用chat-r1，发送“请简短回复SPRINT005测试”。应有一次实际model.request与原对话assistant回复；只有回复不算写Memory。
2. 输入“记住：S005-R1负责人=合成甲”，或先发送“S005-R1负责人=合成甲”再点该**用户消息**的“记住这条”。这是chat_local_command/chat_remember，不需要memory_suggestion模型JSON，不应新增model.request。资料需当前项目/归属；记忆页独立读回新的source/claim和scope。
3. 新对话仍选同项目/归属，设置chat-r1再问“S005-R1负责人是谁”；fixture回答不自动使用记忆，**验证以真实memory-retrieval-last.hits、revision/source_ids及readback的scope/expected IDs为准**，不能凭固定回答推断召回成功。
4. 用“更正：S005-R1负责人=合成乙”验证原claim revision/历史与新内容；用“遗忘：S005-R1负责人”或记忆页选择记录的实际遗忘入口，验证deleted/value/source_ids/history/source_history清空。local命令不调用模型。r2/r3换对应唯一predicate/资料。
5. 项目S005-P2建立另一条同名资料（在UI操作，不seed）。切回P1验证只召回P1；全局偏好另测“记住：偏好：回答尽量简短”，该现有分类允许全局scope；“本项目安排偏好=……”含偏好+项目/安排，必须绑定当前项目与归属。readback允许期望project_id为["", "S005-P1"]以纳入全局偏好，不能要求所有偏好都局限项目。

**当前没有自动AI记忆建议卡。** Main只给用户消息“记住这条”，或记住/更正/遗忘命令及记忆页手动表单；Goal的模型summary也不自动写Memory。若81表要求“AI自动提建议→确认入库”，应标UNIMPLEMENTED_SOURCE/待产品实现，不能返回虚构memory_suggestion字段或直接写库填PASS。边界提案见PRODUCT_PATH_GAPS.md。

## B. Chat → Goal候选 → 计划/模型建议

1. 选择项目/归属，goal-plan-r1，发送“整理S005-R1资料甲、资料乙，准备一次性任务计划”。右侧应出现Goal候选；仅模型返回不应新增Run/完成记录。
2. 尚未打开候选时，设goal-plan-edit，发送“调整当前计划资料，新增S005-R1资料丙”。应更新同一候选revision；未点打开前仍不执行。
3. 使用原“打开/准备”候选入口建立计划，独立读回Goal planned及项目/归属。再设goal-summary-r1，点击Goal页“请模型给建议”，只能返回/保存summary，不自动批准或完成。执行/结果保存需另按实际UI与证据门禁，不能用模型文字替代。
4. 取消/保留类消息走local路径。“先不要修改”不调用模型、不改变候选；“取消本次候选”不应调用模型或外部工具。r2/r3独立使用自己的objective/source，不复用旧Goal结果。

注意：**已打开goal_plan的聊天编辑路径未实现**（chat_update_open_form只处理Mail/Calendar，Goal没有card.goal_id绑定）。不要期望同一句聊天编辑会自动改已建立Goal；现有手动重新计划入口可另验。未实际GUI复现前将其标源码路径限制，不谎报BUG已复现。

## C. Chat → Calendar候选 → 官方Kernel查询/创建/改期

1. calendar-r1，用户必须明确“安排S005-R1合成会议：2026年10月13日15:00至15:30，地点S005-R1合成会议室”。原文缺日期/起止不能靠fixture补齐。
2. 打开候选进入原Calendar入口/单Goal planned。第一次候选操作是preflight只读events limit200；必须真实ready、binding=nil及owner无新增，回读结清至idle/current，再独立第二次操作才add/get。模型服务只选择实际offered工具，不给批准或造回执。
3. 未创建前设calendar-edit-16，发送“把当前会议改到2026年10月13日16:00至16:30，其他不变”，核同候选revision/旧确认失效。已经实际create verified后，同样修改应产生新候选并通过原同ID select/confirm/get-update-get；不能重新add。第三步可选“取消本次候选”，不走模型/Kernel。
4. calendar-ambiguous配用户“过几天安排S005合成会议”，期待waiting_user/补日期与起止、不创建。不要用明确时间response来掩盖用户原文含糊。删除另走原精确ID及expected选择/确认，三真实回执后才verified。

## D. Chat邮件候选与Mail页模型正文是两条不同schema

Chat路径：先用真实GUI登录合成账号并选择邮箱；chat-mail-r1配“起草给receiver@sprint005.example.invalid的邮件，主题S005-R1合成邮件，正文S005-R1合成资料已整理，请核对”。打开候选只建立可编辑草稿，不发送。未发送前chat-mail-edit配“重新起草正文，补充S005-R1合成资料丙”，核原收件人/主题及手写保护/preview失效。保留/取消消息按local路径验证，不能靠模型回复确认发送。

Mail页路径：必须先实际读取一封合成来信，再在写信意图框输入“可以”“拒绝”或“改到后天19点再约”，分别设mail-accept/decline/time-r1，点击实际“模型起草（需先读取一封邮件）”。该response只有subject/body。已有手写正文时应出现“新稿 · 当前正文保留”，原文不被自动替换，点击“采用新稿”才应用并清空旧preview。返回原来信正文或不匹配意图/时间应拒绝，不把这类fixture错配当产品故障。

预览/Host review/批准/accepted/UNKNOWN/独立receiver按Root CA Host与实际GUI步骤另验；model.response、Demo accepted、卡片出现都不是投递证明。UNKNOWN必须原Host attempt/Message-ID及独立receiver计数在真正新进程恢复后不增长。

## E. 晚回包与负向响应

使用late-chat/late-calendar/late-mail/late-goal-summary（4500ms）。**等待服务status的model.response_bound增量及对应case_id出现后**再改变GUI；只改控制文件不是GUI stale测试。新版本记录原response SHA/请求SHA，后续控制变化不会改已捕获的旧请求。旧服务若无该字段，Root先仅重启服务并保留实际端口/profile，或等model.request出现后额外留足时间，不重启生产窗口。

- Chat切到同scope新会话：合法旧回复可保存到原会话，不能误入当前会话。返回原会话核对；不要要求所有晚回包都丢弃。
- Chat原会话改变项目/归属并保存，或使用原停止回复入口（chat_stop）：原request cancelled，旧输出不能成新scope候选/回复。pending同会话再发送会被send_chat守卫阻止；不要把“再发一条遗忘命令”当已经执行的取消。
- Mail模型pending时手工改正文/主题/意图或换账户/来信：旧稿不能覆写手写内容或新账户。适用时“采用新稿”也核base_body/base_subject/intent。
- Goal summary切换所选Goal本身未必使原请求无效；可以合法更新原Goal但不能覆盖当前另一个。要测拒绝，实际改变原Goal version/status后核旧结果未写入。
- 记忆更正/遗忘改变captured refs：在记忆页实际做操作，不能在pending同chat发送命令假装成功；旧模型结果按上下文守卫拒绝。

provider-http-error是实际HTTP503；provider-wire-malformed是provider外层坏JSON；output-not-json是OpenAI外层有效但输出不是JSON；output-extra-field是Main普通reply schema extra-property拒绝。它们是刻意fixture负例，实际UI应显示错误且不新增候选/业务执行，不报告功能实现故障或已完成。

## 证据与适用范围

39样本静态78/78字段/长度/control检查通过；新增晚回包HTTP绑定4/4（仅输运，不是Main或GUI stale验证）。未重跑旧17/107协议，未启动GUI/Kernel/Cargo或写业务DB。实际GUI三轮逐格结果、截图和独立读回仍由ZC05/Root收集。布局问题继续由专责定位，本交付不造243格PASS。
