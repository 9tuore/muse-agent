# rc17 真实 M3 合成排程候选独立评审

**整体 PARTIAL：候选内容 PASS，policy 搜索范围 FAIL；系统写入确认仍 PENDING，不能记 full-chain PASS。**

候选时间为2026年10月5日15:00–15:30、Asia/Shanghai，时长30分钟；地点Muse synthetic acceptance、项目及验收ID均与合成来源一致。报告称目标为Work日历且候选区间无冲突，但本轮未独立查询系统日历或解析calendar_id映射。

## 搜索范围是真实约束缺陷

来源只明确10月5日15:00–15:30，偏好给出下午15–17点、30分钟，未提供额外日期授权。policy却设置10月5日00:00至10月8日23:59:59，将完整四日范围放入hard_windows，并添加10月6日至8日的preferred_windows。reason用“当天及后三天”“未明确禁止”解释扩展，没有体现Root给定的“已有更窄范围取交集”要求。

因此，**按该要求应判policy语义失败**。正确候选不能使附带的错误搜索约束通过。若后续冲突搜索使用此policy，额外三日可能被当成可选日期；当前无冲突候选仍在原时段，本例没有观察到越界排程或系统写入。

核验限制：本报告不包含完整task prompt、原始较窄search边界或wire请求。取交集规则及已有窄范围由Root说明，日期扩展可从报告直接核对；无法仅据本摘要重建精确窄边界或确定具体代码/模型责任。

期望行为是将默认搜索范围与已有窄范围取交集，并同步裁剪hard/preferred windows；空交集应澄清，不得静默放宽。未获准改期时，应保留邮件指定时段。这里是评审要求，没有实施修复或重新调用模型。

## 执行与证据边界

- user_exact_write_confirmation=pending；question为空不是批准。没有系统创建、读回或邮件投递成功证据。
- “无冲突”只覆盖报告所述选定Work日历的候选区间，不等于四日搜索范围已获许可或均无冲突。
- memory_ref_count=2、包含项目偏好均为摘要声明，没有完整引用供本轮核验。
- Host元数据class=strong、requested=fast、attempts=1；usage为1572输入+3337输出=4909 tokens。累计预算18 calls /20966 tokens；没有before/after账本，不独立确认本次账本增量或币值费用。

唯一读取原件：RC17_REAL_SCHEDULE_CANDIDATE.json。SHA256：02979bf094b61d0a3f20d60bf3765f5d40284b8f34721e3030d74e90aaf4469a。报告source_sha256：30ae1a7a5581fa716d6eb5c43bccbeb8377cc2c56418bbd323153b6051a064ff。

只新增本owned目录评审Markdown/JSON；其余报告包括rc11八条身份保持，未读private、真实邮箱或凭据，未调用模型/GUI/Git，未操作系统写入、主报告或共享矩阵。
