# Muse NIGHT-004 故障台账

截至本轮开始：2026-10-12 01:08 北京时间。截止延长至11:00，09:00停止新增高风险开发。
只记录已观察的问题。状态和通过项必须绑定同一候选；本轮模拟不操作生产邮箱、私人日历或用户资料。

| ID | 等级 | 复现 / 实际结果 | 预期 | 原因证据 | 修复 / 回归 | 状态 |
|---|---|---|---|---|---|---|
| N004-01 | P0 | Mail真实登录/同步后，官方审阅报 signed out；原 compose 保留 UNKNOWN | 按应用声明的账号存储模式检查生命周期，保持邮箱选择、准入和grant检查 | SDK lifecycle.rs 对 accounts=false 仍查 Some(mail_account)；独立生产函数fixture before4/6 after6/6 | 8a80b8ed接收补丁；已精确SHA应用到owned SDK，完整Shell定向49/49通过；43 Relay gates与3真实固定Kernel旅程通过；新Host构建中 | FULL_SHELL_TEST_PASS_HOST_BUILDING |
| N004-02 | P0 | Calendar上一回合 turn_completed 或账号变化后，提交按钮不可用，页面未清楚解释恢复入口 | 保留旧请求，UNKNOWN不重发，允许显式另写不同事项 | 已观察UI账号不一致提示及原submit enabled状态；未提交settle修复快照SHA768e295d | 外部已落盘90行补丁保留，ZC03核验真实VM和安全边界 | UNDER_REVIEW |
| N004-03 | P0 | 日程候选没有已选事项时，打开候选被挡住 | 能建立本应用内事项并核对候选，外部执行保持独立授权与回执验证 | UI提示请先选择当前事项；未提交ensure_matter实现 | ZC03验证持久化/绑定/事务切换与迟到回调 | UNDER_REVIEW |
| N004-04 | P1 | 包内官方资源目录octosense与可执行文件同名，首轮pack报IsADirectoryError | 资源保留原路径，裸Host独立签名后可执行 | rc6-standalone-r1失败保留；r2改muse-host后签名及实际GUI通过 | 3处basename修正；本轮绑定源码28/28签名stub/包fixture通过，真实rc6-r2 GUI来自此前记录 | FIXTURE_PASS_RUNTIME_RECORDED |
| N004-05 | P0 | 尚无同一最终候选Mail→Calendar同ID改期→草稿→回执→重启→Memory/行动链全链证据 | 同候选L3完整模拟及L4故障注入验证最终状态/副作用数 | 既有组件和跨版本记录只属局部通过 | 已接收30bc0fdc真实CalendarService九进程L1，SHA与中央SDK一致；L3真实VM/Relay/Mail边界继续统一验收 | OPEN |

真实日历测试使用隔离资料内的官方os.calendar事件持久化，并单独记录创建、同ID读回、改期、删除和重启；模拟工具选择/测试授权不标为真实模型或本人consent。
