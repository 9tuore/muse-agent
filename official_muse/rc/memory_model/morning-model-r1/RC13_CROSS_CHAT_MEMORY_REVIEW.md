# rc13 跨新聊天记忆独立复核

**两条普通语义均 PASS；同归属引用与跨归属输出隔离均符合本例要求。** M01 的来源内容仅有报告及 Root 提供的保存说明，未独立重读记忆源文档，因此 grounding 结论保留来源核验限制。

| 用例 | 实际观测 | 结论 |
|---|---|---|
| M01 · 个人 | 回答工作日历、Asia/Shanghai、15:00至17:00、每次30分钟；带memory引用revision1及source id | 语义PASS；同归属检索及引用绑定在报告中可见 |
| M02 · 老师 | 同问题、同项目、不同session；明确无资料、refs为空，未输出个人四项偏好 | 语义PASS；本例未观察到跨归属泄漏 |

M01引用为 memory:global:1791173632-517187097 / revision1 / local，source_ids为 source:user:global:1791173632-517187097。该元数据与Root给定身份一致。Root说明它来自真实UI保存；本轮未读取源文档或保存回执，不能仅凭引用字段宣称已独立验证内容及revision当前有效性。M02的结果也不推广为所有scope组合的完整隔离证明。

两条session不同可从报告核对，“新聊天”的创建过程未在本轮独立查看。Host两次success、known_usage=true、estimated=false、attempts各1；proposals均为空。账本14 calls /13333 tokens→16 calls /15223 tokens，增量 **2 calls /1890 tokens**，与1104+786一致。费用币值未知。

保护存储未变及无外部动作是报告字段声明；报告未包含保护业务存储SHA原件，本轮没有独立核验。相同query_sha256不证明完整wire上下文相同。

## 可供主报告引用的摘要

- 版本：rc13；报告提交：0bc9028f5faf7d89b21cdc5ef3e3cce2a7dc600f
- 原报告SHA256：27fbfd5bd6ad19982273aa699ade58695573ac962b600018658a10daf80a9370
- payload SHA256：754962b96f60fe2022f6f40923e478e2aa4d72f5e6a5304bc29d4bdc8007dc90
- Host SHA256：938ba58a204de0421b2935c974a22645de14a6b7682f1004bc72c701c3793b3d
- 模型：minimax-cn/MiniMax-M3；Host实际class=strong。
- 两条语义PASS；同归属引用存在、跨归属未输出个人偏好；来源及保护存储哈希未独立重读。
- 完整public_summary字段与逐项观测保存在同名JSON。

唯一读取的原件：official_muse/app/build/ui-memory-20261003/morning-final-live-r2/memory-cross-chat-rc13-r1/report.json

rc11八条继续保持原身份，不合并为rc13重测、全20/28或T17第二strong通过。未读profile、未调用模型或GUI、未修改主报告/共享矩阵/产品源码、未执行Git。
