# NIGHT-002 真实聊天协作与成本记录

时间窗口：2026-10-10 23:41:52 → 2026-10-11 08:00（北京时间），07:00冻结高风险改动。当前为阶段记录；最终结果以本轮运行报告为准。

## 分工与实际分发

没有调用子代理。复用4个已有Codex聊天，不新建另一套执行Runtime；总控独占共享main.splash、候选、Git、所有大型Cargo和窗口自动操作。

| 角色 / 真实聊天 | 独占目录 | 分发模型 / 推理 | 当前产出与验证范围 |
| --- | --- | --- | --- |
| ZC-01 / 01a125ef-2423-7361-a999-1a52988f7927 | calendar_integration | gpt-6.1-sol；复杂准入high、启动核对medium | Native独立ID原型/3个隔离patch、owner准备、准确Calendar参数修正、Kernel/metadata启动预检；中央已应用旧原型，完整Shell正在编译，真实Relay/Person未通过 |
| ZC-02 / 01a125ef-37d8-7091-8a9f-7eb5b49eb3d6 | mail_integration | gpt-6.1-sol；协议修订high、证据和文档low | 官方Mail/Memory边界、shared DSL合同、完整Host审计、jailed digest提案；中央实际reference68/23/9/3通过，真实Mail审阅仍HUMAN_REQUIRED |
| ZC-03 / 01a125ef-45a5-71f2-bad3-e6bc5a00227f | stability_integration | gpt-6.1-sol；UI/fixture适配medium、最终记录low | readonly DSL UI驱动、候选映射、Task23项及旧fixture异步适配；中央可见三尺寸各9项、旧task-focus13项通过，所有失败保留 |
| ZC-04 / 01a0fc7a-bfc0-7bd3-b0c8-860d8a5ed3d9 | runtime_review | gpt-6.1-sol；复杂权限复核high、单次上游核对low | 独立查出同ID碰撞、指纹不足、陈旧scope方案、FIFO open顺序；中央修复或隔离。02:11完整Issue评论/timeline核对未观察到维护者接受；当前只读复核可选History见证 |

以上为实际send_message_to_thread提交并接受的模型与thinking参数。总控自身模型由当前聊天设置决定，工具不能替总控切换；不伪造切换结果。

## Token与节省措施

工具未提供这些聊天的输入/输出Token、缓存Token或人民币账单，记为 **NOT_AVAILABLE**，不估造精确用量/节省比例。协作模型成本与Muse实际业务模型预算是不同事项；本阶段没有新增Muse付费模型调用。

实际措施：复用已有聊天；消息只给当前证据路径/摘要和具体边界；小任务降low；异步测试和参数修正用medium，准入/权限风险才high；不要求整库/完整聊天重读；只有总控运行真实VM/UI/Cargo，协作者交精简patch；复用未受影响的旧证据但不拼接新候选PASS；完成后待命，不循环生成同类报告。

## 合并纪律

每个patch先检查实际文件和接口再应用，执行结果分为静态、组件、VM、可见窗口、完整Shell、模型工具选择、外部动作及独立核验。Git由总控逐单元提交，普通传输失败则保留日志；已用非强制Git对象API核对tree/commit及远端aec355db，main/Tag未动。尚未提交的原型和文档不能称已经同步。

02:41，4f7620f4普通开发分支推送成功，独立远端SHA一致；此前aec的精确对象API失败回退与回执保留。尚未提交原型仍不称已同步。

可信Person/原生审阅缺失保持HUMAN_REQUIRED；原型编译、窗口或模型回答都不替代Calendar执行。磁盘不足仅清无占用可重建缓存/核验重复产物并记录释放空间。

03:39现场：完整Desktop r2/r3真实编译，r2 Native/Calendar隔离启动；实际Calendar像素空白，B定点只读审查提出Cache2跨VM候选。中央唯一r5可逆对照在编译，不升级为已修。Native History r2 5/5纯解析与Scroll已编译，真实consent/Relay仍缺。ZC01 medium只修生成器模块遗漏与冻结输出保护；ZC04 low接收诊断状态后待命，未再扩审。两次无占用缓存净清约4.96GB，实际产物核验保留。
