# Calendar 自然语言结果关联修复

基于 Root `7bc2689f` 的 Main，补丁为 `natural-calendar.patch`。已对 Root 当前工作目录执行 `git apply --check`，可干净应用；没有修改 Root 主源、SDK、GUI 或用户资料。

原 Calendar 页自由输入调用 `submit_bound(text,nil)`，只有邮件来源能将真实创建回执转为事项。结果是普通自然语言即使创建成功，也没有当前事件、删除目标、同 ID 改期与行动链绑定。

补丁先保存请求的 session/project/owner/输入来源，再以同回合真实 add + get 的稳定 ID、参数摘要、来源与字段匹配作为建立普通事项的前提。查询、模型文字、缺失回执、错误账号或来源均不建立事项。新事项 ID 只由稳定请求与用户标识推导，重读和恢复不会新增副本。原邮件路径复用同一创建证明逻辑。

同时修复 SDK 合法省略空 location/notes 的摘要差异：实际 Relay 对原始参数计算摘要，Calendar 将这两个省略字段归一为空字符串。只接受这些等价空值形式，非空备注变化仍拒绝。未修改宿主权限或审批。

最终私有 Main SHA-256：`2a8fb3c9f73c7bc20756f5e978dbf5e47b54081364f4e18322506c6a0530d9f8`。身份与补丁 SHA 在 `natural-calendar-identity.json`。

| 证据目录 | 结果 |
| --- | --- |
| `evidence/natural-baseline` | 原源 17 项，7 FAIL，复现普通自然语言无绑定。 |
| `evidence/natural-optional-baseline` | 首修 29 项，3 FAIL，复现可选空字段省略。 |
| `evidence/natural-fixed-final` | 最终 29/29 FIXTURE_PASS，覆盖真实函数派发、绑定、重复、重启、改期、首次空项目、失败读回与错误来源。 |
| `evidence/natural-mail-fixed-final` | 受影响 Mail/Calendar 40/40 FIXTURE_PASS。 |
| `evidence/natural-history-fixed-final` | 历史/恢复路径 9/9 FIXTURE_PASS。 |
| `evidence/natural-full-store-r2` | 完整生产 Goal/Chat/Calendar 存储与 schema、重启恢复 8/8 PASS。首轮错误为测试误读 delete_target.event，实际字段是 expected；原运行保留在 natural-full-store。 |

总计最终同一私有源 86 项定向执行通过。运行的是真实 Splash VM 与实际生产函数，Host 回执和文件系统由隔离 fixture 提供；这不是 GUI、真实日历 owner、SMTP 或云模型验收。

中央集成后需重新准备和签名候选，并在真实 GUI 测试：直接 Calendar 新建 → 当前日程出现 → 同 ID 改期 → 删除 → 重启恢复。原 `run_linkage.py` 已补齐新增函数抽取，可直接复跑；旧 `run_mail_continuation.py --suite calendar` 的窄 stub 若单独运行，需要提供新增 request-source helper，不能将缺失测试环境函数误报为产品失败。
