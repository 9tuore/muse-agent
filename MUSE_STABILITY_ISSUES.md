# Muse NIGHT-004 故障台账

截至本轮开始：2026-10-12 01:08 北京时间。截止延长至11:00，09:00停止新增高风险开发。
只记录已观察的问题。状态和通过项必须绑定同一候选；本轮模拟不操作生产邮箱、私人日历或用户资料。

| ID | 等级 | 复现 / 实际结果 | 预期 | 原因证据 | 修复 / 回归 | 状态 |
|---|---|---|---|---|---|---|
| N004-01 | P0 | Mail真实登录/同步后，官方审阅报 signed out；原 compose 保留 UNKNOWN | 按应用声明的账号存储模式检查生命周期，保持邮箱选择、准入和grant检查 | SDK lifecycle.rs 对 accounts=false 仍查 Some(mail_account)；独立生产函数fixture before4/6 after6/6 | 8a80b8ed接收补丁；已精确SHA应用到owned SDK，完整Shell定向49/49通过；43 Relay gates与3真实固定Kernel旅程通过；新Intel Host构建完成unsigned SHA a9fc8ca3；运行验收待做 | FULL_SHELL_TEST_PASS_HOST_BUILT |
| N004-02 | P0 | Calendar上一回合 turn_completed 或账号变化后，提交按钮不可用，页面未清楚解释恢复入口 | 保留旧请求，UNKNOWN不重发，允许显式另写不同事项 | 已观察UI账号不一致提示及原submit enabled状态；未提交settle修复快照SHA768e295d | 保留原补丁并收到b6ee81ee最小安全修复；基线6失败，修复后真实VM22/22，中央独立同源码复跑22/22；存储失败恢复原请求、全扫描计数、非查询回执不结清 | VM_PASS_GUI_PENDING |
| N004-03 | P0 | 日程候选没有已选事项时，打开候选被挡住 | 能建立本应用内事项并核对候选，外部执行保持独立授权与回执验证 | UI提示请先选择当前事项；未提交ensure_matter实现 | 候选先校验、已有事项恢复显式选择、候选稳定SHA标识；真实存储恢复重试Goal数由2降至1，中央独立真实VM复跑；late/UNKNOWN/身份切换拒绝通过 | VM_PASS_GUI_PENDING |
| N004-04 | P1 | 包内官方资源目录octosense与可执行文件同名，首轮pack报IsADirectoryError | 资源保留原路径，裸Host独立签名后可执行 | rc6-standalone-r1失败保留；r2改muse-host后签名及实际GUI通过 | 3处basename修正；本轮绑定源码28/28签名stub/包fixture通过，真实rc6-r2 GUI来自此前记录 | FIXTURE_PASS_RUNTIME_RECORDED |
| N004-05 | P0 | 尚无同一最终候选Mail→Calendar同ID改期→草稿→回执→重启→Memory/行动链全链证据 | 同候选L3完整模拟及L4故障注入验证最终状态/副作用数 | 既有组件和跨版本记录只属局部通过 | 已接收30bc0fdc真实CalendarService九进程L1，SHA与中央SDK一致；L3真实VM/Relay/Mail边界继续统一验收 | OPEN |

| N004-06 | P0 | 合法ISO候选经wall转换start/end为空；真实CalendarService拒绝旧VM参数 | 候选生成非空精确墙时 | display返回date time +08:00三段，wall要求两段；4/6 VM失败 | wall三段且+08:00；6/6 VM，新参数真实保存、独立同ID读回、删除不存在，共6个进程 | VM_AND_REAL_SERVICE_PASS |
| N004-07 | P0 | 12个错序/重复/混Kernel/错摘要回执被误verified | 严格单add后单get，同Kernel/精确摘要/调用唯一 | 同冻结源真实VM23例，12个负例误verified | 最小link_result严格两阶段；中央23/23，Wall6/6、Safety22/22；真实Muse整链待做 | VM_PASS_FULL_CHAIN_PENDING |
| N004-08 | P1 | 同聊天第二合法Goal的候选编辑，被新native update入口接到已有event的原Goal | 请求候选与Goal明确归属，不能改其它事项事件 | GPT04真实VM第二Goal控制通过、两负例失败；d065ad15 chat_add_proposal分支未核对归属 | GPT03 8b8e0a21六行guard；中央组合源dabfe65b归属11/11、原改期99/99、行动链37/37；其它回归全通过 | VM_PASS_FULL_CHAIN_PENDING |
| N004-09 | P1 | 无Calendar binding时行动链首次投影，将nil传入新包装函数后取plan_revision报错 | 无绑定返回false，正常展示行动链 | GPT02在d065ad15同候选实际VM首次投影暴露；增加对象guard后23项及重启16项通过 | GPT02 e4dab023对象guard已接收；中央Mail 23/23与真实进程重启16/16；组合源行动链37/37 | VM_PASS_FULL_CHAIN_PENDING |

真实日历测试使用隔离资料内的官方os.calendar事件持久化，并单独记录创建、同ID读回、改期、删除和重启；模拟工具选择/测试授权不标为真实模型或本人consent。

## 同源码 Native改期与空状态修复中央复验

main dabfe65b已集成GPT03 d6e2107e同ID改期、8b8e0a21 Goal归属、GPT02 e4dab023 nil绑定防护。中央311项真实官方Splash VM合成边界全通过：改期99、归属11、安全22、创建回执23、墙时6、Goal10、Memory58+新进程8、Mail19+回执8、Calendar恢复10、行动链37。组件Mail真实Rust dispatch与独立MockTransport/收件端23项及跨进程重启16项源为3c7a2661；最终dabfe65b全链仍待运行。完整Muse经真实AppHub隔离fixture Install/Open与记忆导航、输入读回成功，有三张native PNG；属于早期c183组件包。冷启动预检两次失败：第一查询未归一，第二归一后匹配Muse但Return没有launch记录，保留证据并定位真实菜单路径，不计20通过。

Kernel R4首次add/retry/get真执行，拟拒绝add也执行：官方add为act且outward:false，无强制Host审批，不是Once陈旧授权证据。R5改用官方destructive update的真实Deny，并加入全signed Muse JSONL bridge，按fb74bd8e精确应用cfg(test)源；中央唯一release编译中，尚未PASS。

## 2026-10-12 02:51 中央更新

| ID | 等级 | 观察与根因 | 修复与证据 | 状态 |
|---|---|---|---|---|
| N004-10 | P0 | native已核验Mail Action和声明，但原native完结分支只返回Calendar绑定；中央基线新建/改期均无Run/完成Memory，10项4失败 | 88fe5fb1只换两个业务函数及三个完结helper；中央e7d同源344项VM通过，恢复按钮/证据完成说明已接线 | VM_PASS_FULL_CHAIN_PENDING |
| N004-11 | P1 测试环境 | 公开签名Muse bridge缺生产Mail注册后缺device_consent ABI，真实admission失败，未派发Calendar | fc768及2d927只补cfgtest真实service/policy初始化并完整manifest API预检；R7编译中，未弱化准入 | TEST_DRIVER_FIXED_RUNTIME_PENDING |

旧冷启动两失败保留；最新同dabfe signed candidate真实AppHub Library→Open一次通过，有native照片与三SecCode0。仍不计最终20或L3通过。
