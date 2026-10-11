# Muse NIGHT-004 中央验收记录

更新：2026-10-12 05:18，北京时间。用户允许最晚11:00交付，09:00停止新增高风险开发。当前结论 **PARTIAL，R4真实整链与重叠已通过，规模启动恢复修复中**。这份记录会随最终固定候选更新；尚未授予整轮 SIMULATION_PASS 或 REAL_E2E_PASS。

## 新R4候选实际验收

产品提交197d16d785533469b0e90ab720d4f110f3ebe505，Main源8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d；签名Main a040d63b04e1e1928602e0137a4c13521ab0a2d6c2fde24891e7486ada96af70，manifest b69168fb90d223c879b905acfedd9fb438e89816670ac9135078d6e252ea6f4e，catalog24b2d795caab78005a368f7edb2134f1cf348452dbb79cc4637f4d9f7d566fb6。包路径build/night-004/rc7-integrated-candidate-r4/package/Muse.app。原WorkBuddy Launcher与Host/Kernel保持同一已验证字节；真实App Hub安装后精确核Main/manifest，完整界面原生图实审、输入读回/清空和动态三项SecCode0通过。

| R4同源/同签名范围 | 实际结果 |
|---|---|
| 官方Kernel整链与全进程重启 | full33+15、Deny29+12、CAS28+11、delete23+13，全164检查通过；日历是真实官方Kernel/owner，模型/审批/邮件输运为fixture |
| 原生重叠预查询 | same20、contained20、adjacent20，全60检查通过；首轮query不写，包含提示，相邻需第二次明确操作才创建，原事项不变 |
| SDK坏JSON/Mail故障/性能 | GPT03按明确8227新进程54/107/14通过，中央归档verifier核对通过；没有重复计数或改旧源标签 |
| 大数据GUI | 真实生产save输出64Memory/128Sources/32Goal/32Run/128Action/64activity原字节导入，启动失败，最终20尚未跑 |

大GUI失败原始数据：第二次观察45秒仍只有初始挂载框架；主8unknown/120in_flight，备7unknown；Host.log269行script time budget exceeded，对应Main6779写目标备份。根因为core_boot_goals逐个in_flight重新解析并提交整份83KiB库。N004-16的最小一次恢复提交修复正在准备，必须新签名真实GUI通过后才继续最终20。新分层证据与失败原始图在official_muse/semifinal/evidence/night004-r4-candidate/。

## 当前版本与入口

- 安全回退候选：0.4.0-rc7 R3，`build/night-004/rc7-integrated-candidate-r3/package/Muse.app`，产品来源提交 `fee00c9f614432f4e75fb8c13d14a45229cc90ee`。
- Main源码SHA256：`c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`。签名compact Main：`cdb1412b14a25fdbb8f97681e7fe344c855a0adaac50c26ded5eb17f876108d7`。manifest：`b45620d854b58382d561451e43af34d5effc110d07b4cec163545a660c87482f`。
- Intel Host输入SHA256：`a9fc8ca3f39a626bb1bc1fae3cb99b359f5a07c7c3c50f45cd73b21d885c397a`；包内重签Host：`1eb1887b7e89e1f3adebd750a4afff278d3ad7a942f35ae89a04fa70103cf0f7`。Kernel：`56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270`。原WorkBuddy Launcher：`acfd9a99f8bbf43ccd8b0b957285d5989c8a059c33ede5f45130e05f0f314ef6`。
- 唯一支持的启动路径沿用WorkBuddy：LaunchServices `open -n` → 原外层Launcher → 裸Intel Host → 实际App Hub Library/Open。正式业务入口不依赖直接编辑窗口或测试专用Calendar启动副本。
- 本轮全部运行在双重标记的隔离fixture。没有复制生产profile、私人日历、Keychain或密钥。保留旧稳定包和旧失败证据。安装、批准与模型工具选择为明确fixture边界，未伪造本人可信手势。

## 已完成的分层验证

| 层级 | 实际结果 | 范围与证据 |
|---|---|---|
| L1 / L2组件 | c892中央363项通过；SDK Mail生命周期定向49、Relay43、固定Kernel旅程3通过 | 实际命令、VM和SDK函数。IO、时钟、UI与模型输入是fixture；不等于生产业务完成。`official_muse/semifinal/evidence/night004-actionchain-restore-central/` |
| L3同候选链 | 初始28＋完整进程重启15通过 | 实际官方Kernel/Calendar、SDK Mail与独立MockTransport收件端：读邮件→候选/事项→新建/精确读回→同ID改期→草稿/原生审阅→状态/收件核对→完成Memory→新聊天行动链恢复。`night004-final-candidate/native-l3/` |
| 原生删除 | 初始18＋VM/Mail/Kernel新进程恢复13通过 | 真实get/remove(expected)/get三Broker回执，owner事件数降为0；重复选择/确认和重启无新Turn、发送或伪完成。`night004-final-candidate/native-delete/` |
| L4 Calendar与Kernel | Deny24＋12、CAS23＋11；Kernel5场景通过 | 实际拒绝和陈旧expected保留owner；同request重启复用、destructive Deny、实际同Turn中断与已签catalog撤回。审批策略是fixture，回执/拒绝来自真实Kernel。 |
| L4 Mail恢复 | 旧13场景117、新4场景107通过 | 实际SDK Mail、独立合成收件端；SIGKILL发生于accepted之后/Main收到答复之前，真实errno21写入失败、Review取消、实际fixture计时期满及迟到结果丢弃。恢复只查状态、不再次发送。`night004-final-candidate/mail-durability/` |
| L4模型坏JSON | 19＋19＋16＝54通过 | 原始坏JSON经过实际SDK decoder两次解析/repair失败，再由原Main回调拒绝；无候选/Goal/Run完成/Calendar或Mail写入。合法JSON对照通过。`night004-final-candidate/model-json/` |
| 官方Calendar GUI | CRUD/恢复6项、独立读回12、正式入口Host3次、原生图片7张通过 | 新建、同ID更新、重启、删除、再次重启；Root实际审图。`night004-final-candidate/calendar-normal-entry/`。05确认按钮部分裁切、07卡片屏下的限制在native-review保留，独立owner读回补证。 |
| 最终20启动（R3） | 20次通过，60张原生图全部实审 | 每次实际Library/Open、对话/记忆/对话切换、输入读回/清空；源包8关键文件、安装Main/manifest摘要未变，动态SecCode=0；正常退出后无残余所属Host/guardian。`night004-final-candidate/final20/acceptance.json`。原raw pending结论不改，中央acceptance单列。 |
| 打包复制 | 可选APFS路径5/5小型测试通过 | 保持默认复制/启动方式；副本inode独立、nlink1、源SHA不变。只测小C打印stub和Launcher --check，无真实Host/模型或Cargo构建。`night004-final-candidate/package-clone/r2/` |

上述计数覆盖不同阶段与层级，不能相加为单一最终候选全通。若Main或签名候选变化，必须重新执行受影响业务与最终20；不会将R3结果改标签冒充新候选结果。

## 性能实测

R3最终20：Muse可交互15.389–17.541秒，中位16.243秒；Host就绪3.282–4.433秒，中位3.864秒；导航交互1.048–1.421秒，中位1.167秒；总计18.865–21.170秒，中位19.919秒。所属进程RSS采样最大468.996MiB，`ps`采样CPU平均值之和最大136%，不是全时间峰值测量。启动过程中Calendar前后均0事件；GUI Mail为空，不能借此证明Mail业务或防重发。

有界Memory/行动链规模检查与64ms脚本限额保留。尚无实际大历史GUI长期帧率、真实云端模型延迟、SMTP/IMAP网络时延或本地Qwen长时间协同的测量结论。本轮优先修复已观察业务阻塞，不据推测进行重构。

## 已观察故障与剩余项

台账累计15个编号。10项实现问题（01、02、03、04、06、07、08、09、10、13）已有针对性修复及相应验证；2项测试桥问题（11、12）已修复并完成实际Kernel验证。05同候选业务证据已补齐L3与核心L4，整轮L4仍受15阻塞；14在支持入口的视觉/CRUD复验通过，早期测试副本绘制异常原因仍未确认，原证据保留，不算已修复绘制根因。

旧 **N004-15，P1**：c892原生候选首次提交没有已验证的重叠预查询/提示。Root真实fixture中旧事项16:00–16:30保持不变，首次提交新增同时间事项；未发生第二次重叠选择。官方events的from/to筛选实际是含端点重叠，早期将local_stamp(true/false)读反的测试解释已纠正；产品采用limit200全列表并用半开区间比较。`night004-final-candidate/overlap-baseline/`保留原owner/Broker/非法JSONstdout；新R4的same/contained/adjacent已全60检查通过，不修补旧driver FAIL。当前实际阻塞变为N004-16规模GUI恢复时间上限。

下一步：最小预查询/快照提示/独立确认补丁→定向VM拒绝测试→实际同时间、包含、相邻控制→重签新候选→同候选L3/恢复与最终20。列表达到官方200条上限时停止自动判断，不虚称完整无冲突；查询快照不锁定时段，Host批准规则保持原样。

## Git与交付边界

当前开发分支 `codex/muse-pivot-20261010`，最新已同步checkpoint `cdc37f773e5fdc68503ea26a763176ec631dcacd`；产品Main仍来自fee00c9，后续checkpoint包含证据与测试/打包工具。r6普通push发生HTTP2 framing错误；r7只读远端预检连接github443失败，因此没有进行r7 push，旧网络日志保留。04:39，r8经普通push成功，独立ls-remote返回同一cdc37f77，完整原始命令与SHA核验保留在`build/night-004/git-checkpoint-r8/`。

目前没有正式公开发布、强推、main推送或比赛提交。本轮已获用户邮箱授权意愿，不反复索取；但Night要求隔离模拟，因此没有验证生产账号当前登录状态或进行真实SMTP自发自收。完成模拟后真实验收还包括：本人宿主Agent权限、官方连接账号与原生Review、真实邮件收件及发送状态、实际云端模型、生产资料中的日历业务和公开App Hub发布验证。MockTransport、窗口出现和accepted状态分别不会被提升为真实投递或事项完结。

最终会在这份文件中记录新固定候选身份、分层结论、远端SHA核验、当前留开的可试用窗口和需用户实际验收的步骤。
