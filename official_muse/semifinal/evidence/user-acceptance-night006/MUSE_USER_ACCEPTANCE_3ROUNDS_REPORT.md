# Muse 独立三轮用户验收

**PARTIAL_3_ROUND_ACCEPTANCE**

候选：{"candidate_key": "5acb4815f42cca983c1214d9c30fbe148d47898ef22024fcc55356c507ea57ca", "git_commit": "ab30195c862906527782fd4d82573ca2b6ff7c46", "version": "0.4.0-rc9", "octosense_revision": "f9f6fea90b52182790cb2641fd0145c425af4d84", "candidate_name": "night006-rc9-r5", "host_source_commit": "8569e0ce"}

计划覆盖 90 项；实际 GUI 发现 3 项；完成三轮 0 项；三轮通过 0 项。

结果格数量：{"BLOCKED": 0, "FAIL": 0, "HUMAN_REQUIRED": 0, "NOT_IMPLEMENTED": 0, "NOT_TESTED": 269, "PASS": 1, "SIMULATION_PASS": 0}

证据清单完整：True；同候选保留失败尝试：0。

REAL_OWNER_SYNTHETIC_MODEL 和 FIXTURE_TRANSPORT 的通过仅计 SIMULATION_PASS，不能视作真实模型、生产账号或真实外部发送验收。

| 用例 | 功能 | 第一轮 | 第二轮 | 第三轮 |
| --- | --- | --- | --- | --- |
| UA-BASE-01 | 全新候选启动、窗口显示、正常退出 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-02 | 全部主导航与更多入口 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-03 | 侧栏收起/展开 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-04 | 结果栏收起/展开/窄页返回 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-05 | 中文输入与多轮聊天 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-06 | 聊天停止和中途切会话 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-07 | 新建/切换/持久化对话 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-08 | 对话改名 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-09 | 对话删除取消/确认 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-10 | 项目与资料归属选择 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-11 | 较早消息与回到最新 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-01 | 新增偏好 | [PASS](round-01/UA-MEM-01/attempt-01/result.json) | NOT_TESTED | NOT_TESTED |
| UA-MEM-02 | 新增事实/资料 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-03 | 聊天记住这条 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-04 | 跨会话相关检索 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-05 | 项目/归属/账号隔离 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-06 | 来源与历史展开 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-07 | 更正 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-08 | 固定/取消固定 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-09 | 冲突采用新内容 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-10 | 冲突保留旧内容 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-11 | 遗忘取消 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-12 | 确认遗忘且不从旧来源回流 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-13 | 记忆分页 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-14 | 暂停/启用记忆 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-15 | 导出 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MEM-16 | 同用户合法导入/无效导入阻断 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-01 | 账号连接/选择 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-02 | 同步与失败提示 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-03 | 文件夹与收件分页 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-04 | 读取正文与长正文展开 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-05 | 首次基线/新来信逐封提醒 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-06 | 回复意图模型起草 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-07 | 手写回复 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-08 | 编辑/重新起草/采用新稿 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-09 | 不予回复无发送 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-10 | 写新邮件与草稿继续 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-11 | 发送进入原生审阅与取消 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-12 | 精确确认发送 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-13 | 已受理状态与独立收件核对 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-14 | 未知结果保留且可继续写新邮件 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-15 | 邮件来源记忆 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-16 | 从来信安排/改期入口 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-17 | 自动分析授权与开关 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-18 | 来信提醒暂停/继续 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-19 | 宿主通知启用/暂停 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-01 | 模型或账号前置缺失的可操作提示 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-02 | 自由查询请求 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-03 | 聊天候选打开与对应事项显示 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-04 | 冲突查询 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-05 | 查询结果与实际日程一致 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-06 | 明确添加候选日程 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-07 | 稳定ID精确get_event核验 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-08 | 选原事件同ID改期 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-09 | 原事件变化时处理冲突 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-10 | 删除测试事件及取消 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-11 | 删除后同ID权威缺席 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-12 | 中断后刷新原请求结果 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-13 | 重启unknown不重发 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-14 | 旧私有系统日历不可达功能 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-01 | 行动链/结果切换 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-02 | 跟随会话与切换事项 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-03 | 节点状态与查看依据 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-04 | 旧行动链 DSL 入口已移除 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-05 | 行动链浅深色和布局保存 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-06 | 查看事项与确认 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-07 | 失败/冲突/未知状态不抬高 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CHAIN-08 | 来源关联/旧确认失效/重启保留 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-01 | 模型计划候选生成/打开/暂不处理 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-02 | 批准纯存储计划与独立读回 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-03 | 暂停/恢复任务 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-04 | 取消任务 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-05 | 更新计划使旧批准失效 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-06 | 任务来源记忆 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-07 | 归档、操作记录与诊断 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-08 | 邮件/日历候选生成打开与暂不处理 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-09 | 记忆变化使候选/草稿失效 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-10 | 缺信息询问/授权缺失阻断 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-11 | 邮件→日历→同ID改期→确认稿→结果记忆闭环 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-12 | 安全重试/回读不产生重复动作 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-AGENT-13 | 窄范围来信自动安排可见实现 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-12 | 全应用深浅色范围 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-13 | 窄窗口与长文本布局 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-BASE-14 | 输入为空、格式错误与错误恢复 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-20 | 移除邮箱确认与取消 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-21 | 添加第二邮箱并切换 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-MAIL-22 | 写信编辑器内滚动与返回 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-15 | 自由文字连续新建和默认时长 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-CAL-16 | 自由请求后改期、删除入口 | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| UA-DIAG-01 | 诊断页面与返回 | NOT_TESTED | NOT_TESTED | NOT_TESTED |

## Actual independent scope

The matrix contains exactly 90 features and 270 result cells. Three feature paths were touched, one normal round completed, zero features completed three rounds, and zero features passed three rounds. Result cells: 1 PASS and 269 NOT_TESTED.

Candidate: final r5, Main SHA-256 4584798590c1b8dc5e6f4cc801c3409ff869b919c95e24417b47436f68b56212. Full product/host/kernel identities are in handoff-r5.json and identity.json. Genuine local Qwen0.5B was used; no model fixture or internal business function was invoked. All input used real Makepad remote keyboard and single clicks, screenshots used the owned native window and were actually viewed.

- UA-MEM-01 round 1: saved a synthetic preference; native success screenshot and read-only isolated memory.json confirm persistence. PASS for this normal round only.
- UA-BASE-05: real Chinese single-turn input and reply observed; no follow-up or restart. NOT_TESTED for the incomplete matrix round, with partial evidence retained.
- UA-MEM-07: correction editor opened, no edit/save completed. NOT_TESTED.
- No second or third round was performed. Calendar, Mail, Agent plans and all other r5 operations remain NOT_TESTED. No cloud MiniMax, real send, Calendar CRUD or official full-chain pass is claimed.

Root subsequent actions and Root startup evidence are excluded from this independent matrix. GUI returned to Root at the explicit cutoff; final independent action was opening the memory correction editor at approximately 03:43 Beijing time.

## Prior failed candidate

preflight-r4 retains 15 native screenshots, all actually viewed, and the original action log. Chat stayed thinking and memory save failed; observed host errors were method sha256 not found on object at chat 8585:22 and memory 8596:100. Root then fixed the host and replaced the candidate. No r4 result or historical PASS is included in r5 counts. r1 and static source findings are not GUI passes.

## Evidence and remaining work

round-01/UA-BASE-05/attempt-01 preserves the original continuous action log, three r5 native images and synthetic isolated storage readback. UA-MEM-01/attempt-01 preserves the case identity, copied native screenshot, action provenance, independent readback and reviewed result. Untested features remain NOT_TESTED; missing accounts were not inferred as tested BLOCKED cases. PARTIAL_3_ROUND_ACCEPTANCE is the only supported overall conclusion.

Only acceptance scripts and evidence were changed. The driver fix handles macOS non-ASCII executable paths through reversible read-only lsof output. Production source, Bundle, database and authorization files were not modified.
