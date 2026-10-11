# 统一候选最小薄修补提案（未应用）

只向中央提交边界建议，不改主源/SDK/旧dirty文件，不创建新runtime或假授权。

1. **manifest required ABI审查优先于代码补丁**。若新manifest把mail.accounts/add_account、fs.sha256/fs.sha256_file、猜测abi字段写required，删去未登记要求或仅在中央确实登记后声明。官方当前确实注册compose/status/review/send@1。保留mail capability与标准consent；不要通过改mail_enabled强行显示可用。
2. **discovery不需要适配伪字段**。当前2253读取schema/methods/runtime_features、descriptor.name/version与实际SDK相符。可增加仅无secret的diagnostic观测（当前response字段、三方法flags与错误分类），不赋权、不令configured:null变true。失效时保留明确“缺接口”错误，勿仅按method名字忽略supported/version。若版本受理策略变化，应依据正式ABI元数据，非兼容猜测。
3. **连接后的watch副作用**。当前mail_add_account成功会自动mail_watch_toggle。最小无模型联调由中央先在UI暂停并确认连接后状态；若无法维持暂停，只在新的统一候选里按真实暂停偏好修一处成功callback，不改账号授权、不新增全局测试模式。需实际定位偏好状态后再决定代码，本文不提供未经核对变量的patch。
4. **取消语义保留**。精确cancel错误已识别，草稿正文与host_compose_id/revision保留；action/run failed、MAIL_NOT_SENT是当前真实记账。不要为追求全green把它改accepted/verified；也不要删除未知action或Host composer来“清理”。对native cancel后Host awaiting_approval residue只read/status记录，不重发。
5. **Memory两写恢复风险若复现才小修**。source成功、claim失败可能留下source；先只读核core_add_source/core_add_claim幂等与真实错误，不先扩成跨域事务框架。最小修补是可恢复引用/同source复用，并保留旧证据；具体行须中央复现确认后定。本文未宣告已有bug复现或修复。

现场完成标准以INTEGRATED_MAIL_CHAIN_STEPS.md为准。真实账号连接和native发送批准必须本人；本准备不包含模型、SMTP或收件授权。
