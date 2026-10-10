# Muse 夜间工程与关机后续跑报告

状态：**PARTIAL / 本轮开发已收口**。2026-10-10关机后按用户授权续跑，16:00冻结大改、17:00前停止测试与夜间自动化。电脑关机期间没有运行或测试，不计作持续开发时间。下面较早检查点保留时间和原结果，以本节收口结论为准。

## 本轮收口结论

代码/Phone证据检查点 `efce444a4e0aa82f1c99df37749d95198c8c3d5d`，分支 `codex/muse-semifinal-a-20261009`；后续提交只收口本页、台账和交接。根rc17载荷90351cba/770540字节不变，研究rc18源5e2e84fe未安装；主工作区137项原有未提交改动不处理。未使用子代理。

| 昨夜任务 | 本轮已完成的范围 | 仍缺的验收 |
|---|---|---|
| 稳定性P0 | 邮件审阅取消关联Run、日历中断误完成、ABI误识别分别复现修复；19项邮件/能力协议、7种两VM恢复、10项日历恢复通过，失败留存 | 新官方Shell原生Mail、同候选20次与完整外部链未通过 |
| 官方接口 | 研究源迁入compose/review_send/status，UNKNOWN只读；补runtime声明；最新原生Hub锁定构建和研究r4 unsigned结构Gate通过 | 新Desktop Intel构建依赖网络失败，未升级/安装；scan7问仅材料，reviewer/签名准入未跑 |
| 官方内置日历 | 新源阻止自备EventKit默认；已提交官方共享策略与精确读回补丁供审阅 | update/remove共享策略、精确get、Muse合法工具offer未解决，relay未集成，不能称可用全链 |
| 全局记忆 | DSL62项、授权/焦点/账号/更正/遗忘/冲突/真实jailed存储与两VM恢复91项通过 | 本轮真实模型语义全链未通过 |
| Octos Agent | 隔离原型15项协议检查；实际原生Gate拒绝calendar.events，空工具对照通过、shell对照拒绝；已反馈 | 正式原生覆盖0/16，未准入/真实模型选工具；继续保留现有model.complete，不绕过Gate |
| 行动链 | 隔离266f9c66只读投影、25项状态、四种真实窗口尺寸、一次重启；报告和60–90秒演示方案已交 | 浅色/事务切换/当前正式候选回归未完成；未合主线，不宣称已制作新Host视频 |
| 手机 | 真实复现Home缺主题崩溃；单函数修补原版4FAIL/补丁6PASS；修补后APK验签、资源核对、两次API35冷启动与一次force-stop恢复通过 | 旧rc16配套Home的范围，非新rc18/手机Muse/Bridge/Kernel/Agent全链；实体DEVICE_NOT_TESTED |
| 轻量化/磁盘 | 根bundle770540字节；只清核验过的派生副本和可重建缓存；Phone组合10.5GB上限未提高，失败证据保留 | 未达新候选性能/体积/新接收设备全量门槛，不拼接旧PASS |
| 官方反馈/同步 | #182、#427、#458三条已提交；Calendar实现及Phone实际运行证据已公开供审阅 | 未被官方接受；普通开发分支push超时、远端ref404，GitHub同步未成功，main/旧Tag未动 |

新增真实发信0、系统/内置日历写入0、付费调用0。原生审批缺失保持HUMAN_REQUIRED。旧EventKit“工作”日历批准不转移到内置Calendar。旧安装、生产数据、稳定rc17和唯一失败证据保护。

本轮owned模拟器PID99877已停止，包装守护exit0、子进程exit-6；停止日志保留，不能称自然无错误退出。运行期Home两次正确渲染证据与停止结果分开记录。夜间心跳muse-07-00已删除，未留下自动继续开发任务。Phone完整报告见 `MUSE_PHONE_RESUME_REPORT.md`，行动链见 `MUSE_ACTION_CHAIN_REPORT.md`，全部任务仍在 `MUSE_NIGHT_TASK_LEDGER.md`。

### 接续顺序

1. 在官方稳定Intel环境取得同一新Host后，验证真实Mail审阅、UNKNOWN只读与不重发。
2. 等官方明确内置Calendar共享策略/合法工具offer/精确读回归宿，再接relay；已提交的补丁不等于官方接受。
3. 同一最终候选完成20次非空启动和Mail→Model→Memory→Calendar→Reply→Restart→新Chat，缺项不能删掉。
4. 行动链在浅色/事项切换及核心回归通过后再合入；Phone补Kernel/Bridge/实体设备证据，重新评估新版本。

---

## 14:15及后续历史检查点（非最终结果）

## 版本与保护

- A分支：`codex/muse-semifinal-a-20261009`，检查点提交 `14d76df6`。
- 正式根目录仍是rc17，载荷SHA-256 `90351cba7ec5c493befb6673212bfb1aa9639dbfbc2ce28b83e24b98f3e05bdc`，没有覆盖旧安装和生产资料。
- rc18研究源SHA-256 `5e2e84fe51b168fc4966346c9670189d95d314f2a00f50fe1c4fc70b2867906f`；`build/semifinal-candidate-r3`仅准备，未签名、未准入、未安装。
- 行动链隔离提交 `266f9c66`，未合入A。不使用子代理；已有B聊天已停止写入并移交。

## 已复现并修复

| 问题 | 最小修改 | 实际证据 |
|---|---|---|
| 取消宿主邮件审阅后，关联Run一直运行 | 确认未发送时关闭精确绑定的Run，UNKNOWN保持待核对 | 修前3项FAIL保留；修后16项协议通过，7个独立双VM恢复案例通过 |
| 日历中断后仅凭本地产物文件显示完成 | 运行中的日历任务不晋升完成、不显示未核验结果；历史已完成记录保留 | 修前3项FAIL；修后10项恢复检查、零外部写入 |
| Host方法ABI 2被当成ABI 1 | 精确要求ABI 1 | 修前版本检查FAIL；修后19项能力与邮件协议检查通过 |
| 候选漏声明runtime与必需方法 | 独立候选准备器声明runtime、host-api-v1与四项@1方法 | manifest文件核对完成；尚无新Host原生准入证据 |

全部失败记录保留在 `official_muse/semifinal/evidence/` 或其对应ignored build原始目录，没有硬编码模型答案。

## 验证范围

| 任务 | 目前结论 | 限制 |
|---|---|---|
| rc17稳定基线冷启动 | 真实Shell 20/20，非空16对话/256消息/64记忆 | 不是rc18或最新官方Host的20次 |
| rc18邮件审阅/UNKNOWN/恢复 | 19项合成协议，7/7独立双VM恢复 | 不是原生审批、SMTP投递或收件证明 |
| 授权全局记忆 | DSL 62项；真实jailed文件/元数据/双VM 91项 | 合成授权项目；不是本轮真实模型语义全链 |
| 日历恢复 | 10项真实VM检查 | 官方内置Calendar真实relay仍缺；不恢复自备EventKit默认 |
| 真实可见UI | 参考card-host输入/日历阻塞/非空历史/九文件哈希保持 | 源fa25ccda；当前5e2仅一行ABI判断不同，不能冒充新Host实跑 |
| 官方Agent隔离原型 | 15项协议/jailed存储检查 | 没有真人consent、实际模型选工具或原生准入；正式Chat仍model.complete |
| 行动链 | 25项状态检查、四种可见窗口尺寸、一次进程重启 | 明色未测、事务切换未做；独立树未合主线 |
| Phone | 历史r7 Home APK已构建验签，Bridge曾模拟器UI通过 | 旧七小时截止报告不改；Home运行/新模拟器续验待做，实体DEVICE_NOT_TESTED |
| 同候选完整外部链 | **未通过** | 原生Mail审阅、新Host、Calendar relay、真实工具选择仍受阻 |

## 官方升级与缺口

固定Desktop `desktop-v0.1.0-rc.2 / 4ccf8e068399b1da139771a9ed94cef05fa6ae60`，Host契约1.10.0。源码完整checkout及官方framework setup/--check通过；公开Mac成品只有arm64，本机Intel。

全图Git依赖下载在293322763字节停滞12分钟，13:46停止；最小锁定offline构建exit101；官方octoscode归档下载14:04超时exit28，收到72167452字节但归档未完整。新Host未构建、未安装。失败日志保留，继续独立官方Hub构建，不改锁和准入规则。

AppHub #182、OctoSense #427仍OPEN。Calendar最小实现补丁已贴#427评论6083645335供维护者审阅，**没有官方接受或合入证明**。update/remove目前owner-only，精确get缺失；范围列表缺项不等于精确不存在。

## 操作与授权

本检查点新增真实发信0、日历写入0、付费调用0。外发限已登录QQ本人自发自收、最多20封合成；原生可信批准仍需本人输入，缺失则HUMAN_REQUIRED。内置Calendar与旧EventKit“工作”日历的授权不混用。不push main、不force、不移动旧Tag、不正式发布。

完整任务及下一检查点以 `MUSE_NIGHT_TASK_LEDGER.md` 为准；本文件17:00收口前仍需更新，不能作为全部任务通过声明。

## 2026-10-10 14:51 后续检查点

- 最新官方Hub构建完成、锁未变。rc18研究r4 unsigned结构check通过；scan生成7问，reviewer未跑，正式准入未测。原空integrity字段拒绝与修复后原生Gate证据在evidence/native-hub-rc2，提交4af1f02e。
- Phone API35新隔离模拟器boot=1、r7 APK安装成功；Home实际崩溃：ThemeCatalog缺mobile-presets.json。packager依赖路径拆空格错误已复现，最新Makepad32d同函数仍相同；单函数补丁Rust检查修前4FAIL、修后6PASS，工具重建中。原日志/截帧保留，不标Home运行通过。

## 2026-10-10 后续补验与恢复

- 本地检查点f9175df8；最新原生Hub95e4831已构建，研究r4正确完整性字段的unsigned结构Gate通过，scan只生成7问，未运行reviewer或正式准入。
- outbound-only原型原生Gate修正listing后仍因calendar.events不在商店默认offered_tools而拒绝；空工具对照通过、kernel shell对照拒绝。已补AppHub #182 comment6095096789，未放宽Gate或变成系统应用。原生Agent覆盖仍0/16。
- Phone路径解析补丁已锁定构建通过、Cargo.lock未变；可复现脚本再次得到原函数4FAIL/补丁6PASS。提交OctoSense #458供审阅，未被接受。本夜三条新Issue额度已用完。
- Home重建r1组合Phone状态达到10515320832字节，10.5GB守护停止，exit -15及日志保留；模拟器续跑预检也被同一上限拒绝。只清两个可重建strip派生副本及本轮无账号的鲜启动AVD镜像缓存，保留原APK/ELF、config、crash日志、截图和缓存哈希清单；实体、旧AVD和生产未变。r2复用编译缓存重试，上限未提高。
- 普通开发分支同步45秒超时，随后GitHub API核对目标分支404；未同步，不改main或Tag。针对1043个变更路径/823个文本文件的凭据模式与禁止文件扫描无命中；这项扫描不保证全部隐私语义。
- 16:00停止大改；剩余时间核对APK资源、验签、运行和交接。新候选20次启动及同候选真实外部全链继续保留缺项。
