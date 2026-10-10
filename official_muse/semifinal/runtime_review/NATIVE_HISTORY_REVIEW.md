# ZC-04 Native History 最小见证审查

**结论：未发现P0/P1，可作为可选只读展示提案交中央编译；不是VERIFIED判定器。** 只读取提案及指定真实wire/broker/kernel；四个定义文件、两patch、三提案文件SHA与RESULT记录一致，lib为8a1e25d0、history为024b484d。未应用、编译、跑解析测试、GUI、模型或写入，不触碰Cargo session43238。中文label可独立推进。

## 身份与成功边界

Broker:3062/3086/3115生成并提交本回合UUID，返回turn_id。固定b0759a5 transport:40822/41596将该UUID传入pre_stamp_turn_thread_id；5441–5451只给未绑定User/Assistant/Tool补thread_id。hydrate:30056–30084保留thread_id、当前turn_id=None；broker merged_history:2653起按真实来源覆盖lane。因而该固定普通回合工具行可精确用thread_id回退；这是版本/路径证据，不能宣称一般ThreadId恒等TurnId。已有不同thread的行被排除、证据不足，不能猜测关联。

role/tool_name/lane和回合均精确匹配，仅显示原tool正文；assistant/non-tool、旧回合、system_agent排除，缺call_id/content或超限拒绝。错误正文也只是原文；代码不解析成成功、写状态或产生VERIFIED。lane=person是Broker会话lane，TurnFrom仍为App，不是可信Person。History仍缺caller/owner/参数摘要/Relay outcome的交叉核验，正文不能作完整链路成功。

**P2严格性缺口（history.rs:31–32）**：非字符串turn_id会回退thread_id；合法turn_id匹配时会忽略矛盾thread_id。当前固定serializer不产此形状，但若要求严格身份拒绝，最小改为：字段仅允许缺省/null或合法非空字符串；两ID同时存在时要求一致；有类型错误/冲突即证据不足，回退仅在turn_id缺省/null时发生。补冲突/错误类型fixture，不必改Host。未知非关键字段可忽略，不能从其内容派生身份或成功。

## 单次、边界与关闭

按钮每次只发一次ContextOp::History、一个在途receiver，无模型turn/轮询；但Broker:3164–3204会hydrate当前、最多15个旧person lane及peer，最多17次内部读取，不能描述为一次Kernel RPC。4096行限制在Host Value已构造后检查，不限制Host端历史内存；正文4096、最多4记录及8192展示限制避免继续缓存大正文，超限只报不足。该提案不解决Host级分页/响应上限。

契约contract.rs:263规定每call恰好一个Complete，因此容量1发送在该契约下没有必然阻塞；不能把重复Complete假设当已复现死锁。stop/shutdown丢receiver、清last_turn；旧closure只持旧sender和turn，send失败不能污染下一请求，Broker:3299/3345另做lease检查。

**P2等待恢复**：lease失效可使Broker丢弃Complete，当前try_recv().ok()也忽略Disconnected，在途标记会一直拦新请求，须点停止恢复。最小补读取中提示“停止可取消”、显式处理Disconnected/已关闭context并清等待；若加入deadline只关闭本context、保持证据不足，不重发模型。停止仍可操作，未见不可恢复UI死锁。现3项测试尚未运行；中央窄验证应补ID冲突、超行/多记录/错误正文、不产生VERIFIED、关闭与迟到回复。真实History形状、Relay/Person仍NOT_TESTED。
