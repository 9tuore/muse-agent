# rc13 两条 topic guard 独立复核

**Mail guard 2/2 PASS；普通聊天语义 1/2 PASS，G02 FAIL。** 两条 Host success 不能合并写成两条语义通过。

| 用例 | 当前输入 / 实际回复 | 原 guard 要求 | 普通聊天语义 |
|---|---|---|---|
| G01 | 换题为秋日阅读活动起名 → 秋阅时光 | PASS：proposals为空，没有旧邮件候选 | PASS：简短名字符合输入，未多输出 |
| G02 | reader@example.invalid → 金秋书韵 | PASS：proposals为空，没有误建邮件候选 | FAIL（额外意图评审）：当前输入未要求继续起名，回复未回应地址或澄清用途，仍沿用旧起名意图 |

G02 的原要求仅禁止在没有等待邮件澄清时关联旧邮件或创建候选；这一 guard 确实通过。普通聊天语义失败另记，不能倒改原 guard 判据，也不能凭“未建候选”掩盖答非所问。单独地址用途未明，适宜澄清其用途，而不是自行继续旧标题任务。名称本身不构成事实幻觉；失败点是无依据承接旧意图。该报告不足以定位 helper、历史拼接、提示或 provider 的具体责任。

两个报告 session_id 一致，input_count各1，Host实际class=strong、requested=fast。G01 attempts=1、G02 attempts=2；G02首尝试原文及原因未知。账本从12 calls /11012 tokens到14 calls /13333 tokens，增量2 calls /2321 tokens，与两项Host usage分别887、1434一致；币值费用未知。G01远程单击HTTP404原样保留。

证据身份：0.3.26-rc13；报告提交 0bc9028f5faf7d89b21cdc5ef3e3cce2a7dc600f；payload 754962b96f60fe2022f6f40923e478e2aa4d72f5e6a5304bc29d4bdc8007dc90；Host 938ba58a204de0421b2935c974a22645de14a6b7682f1004bc72c701c3793b3d；minimax-cn/MiniMax-M3。

原件：official_muse/app/build/ui-memory-20261003/morning-final-live-r2/mail-topic-regression-rc13-r1/report.json
SHA256：4100fde09f3bdce4a8a4b9b13ae72dda507901d021aff8984142996a77a9c8a1

只读取以上被授权的合成报告。protected_files_unchanged=true、no_external_action_confirmed=true为报告字段；报告没有保护存储SHA原件，未独立复核存储哈希或外部系统。Root告知无trap，但本轮未读运行日志，不能声称独立验证无trap。

rc11八条保持原身份与原文件，不并入rc13重测或全20/28结论；T17第二strong缺项不变。仅新增本owned目录中的评审Markdown/JSON，没有模型、GUI、Git、产品源码或共享矩阵操作。
