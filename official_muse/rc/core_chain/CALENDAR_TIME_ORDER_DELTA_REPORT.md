# Calendar 问询顺序最小提案（A2）

状态：`PROPOSAL_FIXTURE_PASS_ROOT_REVIEW`。仅隔离提案通过，未标正式产品或真实模型整链 PASS。

## 最小变化

仅替换 `chat_candidate_input_error`：保留日期缺失/含糊的第一分支；将既有 `!editing && !chat_calendar_input_clear(message)` 检查提前到 `chat_payload_error` 前，日期已知时固定询问“请补充明确的开始和结束时间。”。删除原后置重复检查。所有其他源码字节相同。

明确日期和起止、editing=true 仍走原 payload / 时区校验；日期含糊优先问日期和起止。没有修改 input_clear/date_known 的词法、批准、候选绑定、模型或服务接口。

## 实测

实际复用 CardHost `52768f57`，独占端口8509、独立文件目录，manifest-only复制，无资产复制或构建。宿主UI被抑制，合成输入及模型输出；生产校验、候选与存储函数在真实Splash运行。没有 Host 请求、模型推理或系统动作。

| 对照 | 变体 | 通过 | 失败 |
|---|---:|---:|---:|
| 原rc8源码3bce91a8 | 15 | 50 | 三个known_date_*问询文案 |
| 单函数提案02c26224 | 15 | 53 | 0 |

覆盖：已知日期缺起止（空slot、反向slot、模型臆造正常slot）均问明确起止并零候选；明确有效时段创建未批准候选；反向、过去、时区不一致拒绝；缺日期/含糊日期问日期及起止；editing地点有效及反向校验；原Mail/Goal四种输出完全相同。

已有候选实际地点编辑通过，同ID/revision2，原生fs保存与读取一致；stale candidate_payload拒绝并保留卡片。每个非editing Calendar分支真实chat_save/native readback；Python独立读schema和检查无calendar-state系统动作产物。总计53项，不把 real_model=false 等边界标志计入断言。

## 版本与证据

- 原源码：`3bce91a8e340c109ec627d6dfa73e776ecd37e98614b77eac85958616d1c2351`
- 隔离提案：`02c26224c99f3000ed1f627ab96ee0eee4846b93cdc117999872ebe2e050652c`
- CardHost：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`
- 运行时现场仓库SDK lock：`da756dde48232ccc9a3ec642cf206a0872e1731d4f0c0d55b2490de281a810cc`。与复用二进制的构建来源分开记录，未重建或声称它已经包含da锁更新。
- 本地证据：`evidence/rc8-calendar-time-order-20261005-r8/summary.json`，原/提案report、runtime.log、隔离state与patch均保留。
- 每对薄fixture约1.45MB，无公开原始state/log/full bundle。

## 失败保留及限制

r1访问缺失候选导致out-of-bounds；r2-r6混合所有动作字段的fixture在字段归一复制后丢end/location，正常候选及编辑失败。已核验nil request没有直接拒绝规则，补binding和factory最终JSON转换未解决此失败，不能据此归因产品。改为Calendar五字段、Mail三字段、Goal两字段后，r7在finish缺action字段报错；补合法factory参数后r8通过。所有首轮错误及失败保留，没有删除或改写。

本提案不增加日期解析能力、不扩Calendar能力，未直接覆盖生产文件、SDK或Git。Root负责应用最小变更、版本/compact token核对和真实模型/GUI复测。

## 复现

从项目worktree运行以下命令（CardHost路径须为本机已核验52768f57二进制；out必须是新的A2私有目录，端口8509必须空闲）：

```sh
MUSE_CARD_HOST='<已核验的CardHost绝对路径>' python3 official_muse/rc/core_chain/run_calendar_time_order_delta.py --source '<3bce91a8可读源码快照>' --expected-source-sha256 3bce91a8e340c109ec627d6dfa73e776ecd37e98614b77eac85958616d1c2351 --out official_muse/rc/core_chain/evidence/<新目录>
```

公开仅 `CALENDAR_TIME_ORDER_PUBLIC_ALLOWLIST.json` 中独立六文件。既有21文件和其他独立清单不变；A2未暂存/提交/push，没有访问生产资料、凭据、真实模型或联系人。
