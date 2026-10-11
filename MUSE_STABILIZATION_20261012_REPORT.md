# Muse NIGHT-004 中央验收记录

更新：2026-10-12 06:03，北京时间。用户允许最晚11:00交付，09:00停止新增高风险开发。固定 R5 候选在本轮隔离模拟范围内为 **SIMULATION_PASS**；生产端到端为 **NOT_TESTED**。这是已验证的开发候选，尚非公开正式发布或比赛提交。

## 固定候选与打开方式

- 版本：0.4.0-rc7 R5。产品提交：0c3aa9b1e0574a550f21b93b6d8942cdd2759f35。
- Main 源 SHA256：caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce。
- 已签 Main：ef58430fef4b2f707b78a12f4c4bcd2403b8404c092f5cd73239e5d128a9e750；manifest：7b746fb0871e9e40f30819e4f6d851cda9c61d9ccb595468373cf622307f9714；catalog：1ea34df14b36ddf3ddb5727a17d6ef4c3bf22fdbdac709de4417bb76cf86c7a9。
- 包：build/night-004/rc7-integrated-candidate-r5/package/Muse.app。实际 Intel x86_64，沿用原 WorkBuddy 的 LaunchServices open → 原 Launcher → Intel Host → App Hub Library/Open。没有替换为直接编辑窗口或专用 Calendar 启动副本。
- Host 输入 a9fc8ca3f39a626bb1bc1fae3cb99b359f5a07c7c3c50f45cd73b21d885c397a；包内重签 Host 1eb1887b7e89e1f3adebd750a4afff278d3ad7a942f35ae89a04fa70103cf0f7；Kernel 56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270；原 Launcher acfd9a99f8bbf43ccd8b0b957285d5989c8a059c33ede5f45130e05f0f314ef6。
- 已安装 Main/manifest 与候选逐字节相等。06:02 留开的完整 Muse 为 PID26569，动态三项 SecCode 状态均0，实际 executable 为包内 muse-host。保存图片 narrow-and-ready/04-ready-for-trial.png。

## 同 R5 实际验证

| 范围 | 实际结果 | 证据 |
|---|---|---|
| 原生业务链与完整进程恢复 | full33+15、Deny29+12、CAS28+11、delete23+13，共164检查通过 | native-full、native-deny、native-cas、native-delete；真实官方 Kernel/Relay/Calendar 和 SDK Mail，模型/授权/邮件输运是 fixture |
| 邮件联动日历及行动链 | 邮件输入→候选/事项→新建/精确读回→同ID改期→草稿/原生审阅→状态与独立收件核对→完成Memory→新聊天行动链恢复通过 | 同一已签 Main 的 native-full；accepted 单独不算完成，MockTransport 不算 SMTP |
| 重叠与相邻控制 | same、contained、adjacent 各20检查通过 | 首次预查询不写 owner；同时间/包含提示冲突，相邻需第二次独立操作才创建，旧事件ID与字段不变 |
| Kernel L4 | 实际5场景通过 | 重试/重启复用、destructive update/remove Deny、同Turn中断、已签更高sequence目录撤回；kernel-l4及withdrawal |
| 启动恢复 | 中央真实官方VM46检查通过；真实GUI128待恢复动作全部UNKNOWN | 原83KiB/128in_flight字节完整备份，32Goal/32Run/负载不变；0待恢复不写，写失败/读回失败拒绝提交成功声明；night004-boot-recovery-central及large-ui |
| SDK坏模型JSON | 54检查通过 | 原SDK decoder/repair与原Main回调，负例无Calendar/Mail写入；gpt03_night004_model_json/evidence/candidate-caa99-r1 |
| Mail故障与防重发 | 107检查通过 | 实际SDK、accepted后真实SIGKILL、真实errno21、Review取消、fixture期限及迟到包；重启UNKNOWN只查状态、0再次发送；gpt03_night004_l4_audit/evidence/candidate-caa99-r1 |
| Memory/行动链规模组件 | 14检查通过 | 实际生产API/官方VM定时，gpt03_night004_perf/evidence/candidate-caa99-r1；不是Host64ms预算测量 |
| 最终20次启动 | 20次真实WorkBuddy/AppHub打开、60张原生照片逐张实审通过 | 每轮Chat/Memory/Chat及真实输入读回清空；20不同Host PID，动态身份、包8文件/安装2文件/helper2文件不变；final20/acceptance.json |
| 官方日历GUI | 创建、同ID修改、重启恢复、删除、再次重启6检查通过；12独立读回、3真实Host、7原生照片实审 | calendar-gui/acceptance.json；8业务点击每次单一派发；图片05确认部分裁切、07空日标签屏下的限制照录，精确owner读回补证 |
| 窄窗口 | 真实412点宽度输入、结果行动链、返回聊天通过 | 4原生照片实审；恢复宽窗口后64Memory与聊天输入正常；narrow-and-ready/acceptance.json |

所有数字是明确层级中的检查数，不拼成一个虚构的单次全链总数。旧R3的组件/20启动、旧R4的164/60均只作历史证据；这次更改Main后已重新执行R5受影响链路及最终20。

## 修复与真实性能

N004-16 的实际根因是 core_boot_goals 对每个 in_flight 重新解析、提交整份83KiB库，触发Host脚本时间预算。产品只做一次原始快照与一次受原门禁保护的恢复提交，保留备份、写后读回和失败返回。R4规模GUI45秒仍未完成；R5同原API-save输出完成128UNKNOWN恢复、聊天/64Memory/行动链/输入，再连续20次启动通过。没有伪造完成状态、抹去旧失败或修改生产SQLite。

台账16个产品/桥编号中，01–13、15、16已有针对性修复或证据补齐；14在支持的WorkBuddy入口复验GUI通过，但早期测试副本绘制异常根因仍未知。额外两个测试驱动问题也完成实跑：启动判据等待完整聊天恢复；Calendar点击改单一派发后独立等待，避免画面确认失败重试业务。窄窗口首轮返回聊天的滚动方向错误已修正驱动并完整重跑。失败原始数据仍保持FAIL。

R5大数据最终20：Muse可交互中位21.652秒、范围20.923–24.280秒；Host就绪中位3.799秒；导航加输入读回清空中位1.874秒；全轮中位25.964秒。所属进程RSS采样最大477.5625MiB，ps采样CPU平均值之和最大140.1%，不是全时间峰值。旧R3空数据16.243秒与本次大数据不可作为同负载速度改善比较。

组件Memory median88.654ms/p95105.173ms、行动链projection median10.773ms/p9515.597ms来自debug VM/RPC及实际审计写入，不等于Host帧预算。没有真实云模型延迟、SMTP/IMAP时延、长时间本地与云端协同或小时级持续稳定性结论。

## 边界和白天验收

本轮资料有双重FIXTURE_ONLY标记，日历使用真实官方owner/Kernel持久化，但事件与资料是隔离合成数据。模型选择/审批策略/邮件MockTransport为fixture。原生日历窗口CRUD证明官方owner可用；Muse Agent链路由独立的真实Kernel整链证据证明，不能互相替代。GUI启动时Mail为空，仅验证空状态计数，没有用它证明邮件投递。

重叠查询是快照，不锁定或预约时间；达到官方200条上限时停止完整性判断。静态工具声明含写工具，提示词不是每Turn工具权限隔离，不能声称模型已获得只读工具集。实际生产模型与权限仍需验收。

用户已表达邮箱授权，不重复索取，但Night协议要求隔离模拟，因此没有读取生产账号当前状态、复制生产profile/私人日历/Keychain/Secret，或进行SMTP自发自收。尚待白天实际验收：当前R5宿主Agent权限、官方账号登录/原生Review、真实邮件发送与独立收件、真实模型调用及本地/云端协同、生产资料Calendar业务闭环和公开App Hub发布。仅在实际需要新增可信授权时准备相应界面。

## 证据与Git

统一归档：official_muse/semifinal/evidence/night004-r5-candidate/，包含固定身份、各层原始回执、60启动图、7日历图、4窄窗口图、执行过的驱动、旧失败和中央acceptance。evidence-manifest.json逐文件SHA256核验；组件证据保持各自已提交的candidate-caa99-r1目录。旧R4报告另存report-before-r5.md。

开发分支codex/muse-pivot-20261010。产品提交0c3aa9b1固定，报告与证据另做本地checkpoint后普通推送，并独立ls-remote核对最终SHA；实际同步结果保存在独立git-sync目录。06:01只读预检远端仍cdc37f773e5fdc68503ea26a763176ec631dcacd，不据预检宣称新候选已同步。旧r9连接失败记录保留。

未做main推送、强推、公开发布或比赛提交；四项既有他人未提交源码/文档改动保留，未纳入本轮checkpoint。最新R5模拟窗口保持打开，供用户后续试用。
