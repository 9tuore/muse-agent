# Muse 0.2.9 Memory 对照矩阵

数据基线：独立版实际源码 `app/muse_dsl.py`、`muse_memory_schema.json`、`muse_memory_graph.py`、`memory_store.py`。只读取源码和隔离测试数据，未读取或改写生产 SQLite。0.2.9 来源hash、更正、固定、墓碑、独立验证器与重启测试已完成；Mail/Calendar 来源待真实联动，不使用旧版本证据计 PASS。

| 页面/字段 | 独立版真实定义 | 官方版映射 | 当前差异/处理 | 0.2.9 验收 |
|---|---|---|---|---|
| id | envelope.id；claim_id | document.id | 保留稳定 ID，不按显示名识别 | PASS（核心字段；见最终报告） |
| type | payload.epistemic_type | 同名字段 | fact/user_statement/external_claim/inference；新增非法类型拒写 | PASS（核心字段；见最终报告） |
| entity | payload.subject_id | 同名字段 | Goal ID / mail account+message 稳定引用 | PASS（核心字段；见最终报告） |
| relation | payload.relations | 同名字段 | 保留关系与更正保持；完整循环图谱未1:1 | PARTIAL（空关系/字段兼容已验） |
| fact | epistemic_type=fact | 已核验结果摘要 | 模型建议不冒充事实；结果 fact 只说明实际产物与读回 | PASS（核心字段；见最终报告） |
| inference | epistemic_type=inference | 字段保留 | 不自动把模型输出标为 fact | PASS（核心字段；见最终报告） |
| source | muse_memory_sources | memory.json.sources | kind/locator/时间；额外 support_excerpt 为 UI 摘录 | PASS（核心字段；见最终报告） |
| source_id | source_ids + source表ID | 同名字段 | 更正保留 source_history；重复 ID 的不同 hash 拒绝 | PASS（核心字段；见最终报告） |
| source_hash | content_sha256：SHA-256 | fs.sha256(精确 UTF-8 内容) | 更正使用 trim 后内容；邮件原正文；结果使用真实文件字节。未重算旧 nil 记录 | PASS（核心字段；见最终报告） |
| confidence | 旧 raw MemoryStore 有 confidence；MemoryGraph DSL 无该字段 | 不向 DSL 伪加字段 | DSL schema additionalProperties=false；无法把 raw 信心数造为现有来源 DSL | N/A；旧 raw UI 未导入 |
| created_at | envelope.created_at | 同名 UTC ISO 字段 | 保留，不因更正变化 | PASS（核心字段；见最终报告） |
| updated_at | envelope.updated_at | 同名 UTC ISO 字段 | 更正更新 | PASS（核心字段；见最终报告） |
| pinned | 独立 pins 表 | claim.pinned | 独立于 DSL，固定与重启恢复 | PASS（核心字段；见最终报告） |
| deleted/tombstone | payload.deleted + forget内容hash键 | 同名 deleted + forget记录 | source ID 和内容 hash 同时阻止回流；兼容旧缺 hash 墓碑 | PASS（核心字段；见最终报告） |
| Goal result | runtime_receipt source + claim | verified_result + source:result:<run> | 保存摘要、精确产物 hash；不把模型报告全部复制到事实 | PASS（核心字段；见最终报告） |
| Mail 来源 | source kind / locator | runtime_receipt / mail:<account>:<message> | 明确账号作用域；稳定消息 ID 去重；不进入凭据 | 待真实登录 |
| Calendar 来源 | 系统读回回执 | runtime_receipt / calendar:<calendar>:<event> | 同一 Goal 结果同时关联邮件和 Calendar 来源 | 待联动实测 |

## 算法和边界

宿主 `fs.sha256(text)` 是本地最小补丁，最多64 KiB，不读文件、不联网、不新增 manifest capability，不提高脚本预算。独立版 `MemoryGraph.put_source` 接收由调用者选定的内容 hash；官方版的上述 hash 基础在此固定，算法均为精确 UTF-8 字节的 SHA-256。不同平台回执形状不同，不能声称不同 JSON 的 digest 相等。

旧官方来源 nil 保持原样，在 UI 标 PARTIAL；旧独立版生产 Memory 不导入。完整知识图谱、旧 raw/index 的自动迁移不在本轮重写范围。最终报告必须单列这些差异。测试数据库与复制数据可使用独立版验证器读回检查 envelope/source 兼容性，不靠页面出现判断。

## 最终验证

4份result源SHA与实际文件一致；更正hash与独立trim+UTF-8算法一致，created_at和来源历史保留。实机固定与删除产生2墓碑，整个Shell重启保持。总4claim（3活跃），无启动重复记忆。核心37项含同内容换sourceID阻止删除回流、缺hash拒绝；新源及claim由独立MemoryGraph测试DB接收。

confidence保持N/A，旧raw/index及完整图谱不自动导入。Mail/Calendar locator区分和引用代码存在，未获真实源邮件/系统事件联动证据，不计PASS。详见PHASE2_FINAL_TEST_REPORT.md。
