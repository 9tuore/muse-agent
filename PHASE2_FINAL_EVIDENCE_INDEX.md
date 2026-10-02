# Muse 0.2.9 最终证据索引

状态PARTIAL。源17e63c5、测试4729e7a；[精确身份与宿主SHA](evidence/phase2-final-029/records/candidate-provenance.json)。大图保留在本机evidence和桌面交付包，Git保留摘要与SHA索引。

## LIVE正确渲染窗口

- [Chat](evidence/phase2-final-029/after/pages/chat.png)、[Goals](evidence/phase2-final-029/after/pages/goals.png)、[Memory](evidence/phase2-final-029/after/pages/memory.png)、[Activity](evidence/phase2-final-029/after/pages/activity.png)
- [Mail未连接](evidence/phase2-final-029/after/pages/mail.png)、[Calendar未授权](evidence/phase2-final-029/after/pages/calendar.png)、[Capabilities](evidence/phase2-final-029/after/pages/capabilities.png)、[Settings只读](evidence/phase2-final-029/after/pages/settings.png)
- [990×400](evidence/phase2-final-029/after/layout/shell-990x400.png)、[宽窗三栏](evidence/phase2-final-029/after/layout/shell-wide-three-columns.png)、[五请求数据](evidence/phase2-final-029/records/layout-report.json)。after/layout每请求含Chat/Goals/Mail/Calendar/长详情。
- [Chat语义](evidence/phase2-final-029/records/chat-final-report.json)、[真实wire角色/hash](evidence/phase2-final-029/records/chat-wire-audit.json)，五轮图在after/chat-final。
- [4Goal/Activity/精确来源hash](evidence/phase2-final-029/records/goal-activity-memory-audit.json)，图在after/goals。
- [Memory更正](evidence/phase2-final-029/after/memory/corrected.png)、[删除空态](evidence/phase2-final-029/after/memory/deleted-empty.png)、[固定](evidence/phase2-final-029/after/memory/pinned.png)、[记录](evidence/phase2-final-029/records/memory-report.json)
- [模型错误](evidence/phase2-final-029/after/model-unavailable.png)、[恢复](evidence/phase2-final-029/after/model-recovered.png)、[失败pair排除](evidence/phase2-final-029/records/model-unavailable.json)
- [整个Shell重启](evidence/phase2-final-029/after/restart/restart.png)、[7文件SHA](evidence/phase2-final-029/records/restart-report.json)、[Chat D/pin/墓碑](evidence/phase2-final-029/records/restart-semantic-state.json)

## LOCAL / FIXTURE

- [Core37项/4启动/独立DSL](evidence/phase2-final-029/records/core-contract.json)
- [完整内容SHA与64KiB边界](evidence/phase2-final-029/records/native-hash.json)
- [grant拒绝/无服务](evidence/phase2-final-029/records/service-negative.json)
- [Chat legacy/备份](evidence/phase2-final-029/records/chat-recovery-report.json)
- [计时预算/崩溃恢复](evidence/phase2-final-029/records/goal-recovery-result.json)

## 准入与保护

- [签名Gate](evidence/phase2-final-029/records/hub-check.txt)、[原版拒绝](evidence/phase2-final-029/records/stock-gate-refusal.txt)、[无注册key拒绝](evidence/phase2-final-029/records/unregistered-key-refusal.txt)
- [scan七问完整回答](evidence/phase2-final-029/records/scan-review.json)，human-review，不是正式审查通过。
- [候选Secret模式扫描](evidence/phase2-final-029/records/source-secret-scan.json)、[旧0.3.1保护](evidence/phase2-final-029/records/protected-app-check.json)、[人工节点](evidence/phase2-final-029/records/manual-nodes.json)
- [全部证据SHA](evidence/phase2-final-029/SHA256SUMS.json)：57张截图含旧独立版before。before为此前真实打开0.3.1保留基线，不冒充本轮重新拍摄。

## 配套环境

真实测试.app：`/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/muse-calendar-test/OctoSense Muse Phase2 Final 0.2.9.app`。

主源：official_muse/app/bundle；隔离jail：official_muse/app/build/phase2-final-029-r2-apps/muse-goals；签名catalog：official_muse/app/build/phase2-mirror。模型为原有keyless本地服务，未接新Key或Provider。ignored运行目录含本机状态，不纳入Git或交付账号数据。

[宿主补丁/构建说明](official_muse/phase2/host_extension/README.md)；新增fs.sha256属于本地最小Makepad补丁。Calendar扩展仍受manifest/App Hub准入、系统权限与独立确认约束，未宣称原版接受。

测试入口official_muse/phase2/tests。Calendar `live_calendar_crud.py --prepare-only`先停在真实创建确认，须本人点击后继续；同任务真实双批准/防重复仍待完成。当前邮箱Host登录中，停止截图/控件检查直至本人完成。
