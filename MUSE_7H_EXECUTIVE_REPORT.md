# Muse 七小时可靠性与 Phone 收口报告

## 结论

**PARTIAL**。最终桌面候选 `0.3.27-rc16` 已在真实可见 OctoSense Shell 单轮完成 **10 次完整进程冷启动 + 5 次应用重开**，官方签名 bundle 的独立 check/scan 通过；真实本地模型跨会话检索、更正读回、完整 Host 重启后的记忆召回通过。

本轮同一最终候选的真实 Mail→Model→Memory→Calendar→Reply 全链未通过：隔离邮箱规范目录缺少 Keychain 登录，唯一发送尝试保留 UNKNOWN；修正后的日历授权路径确实进入系统提示流程，但最终权限仍为 not_determined。没有把旧缓存、SMTP 受理、模型文本或 DRY_RUN 当作外部动作完成。

## 时间、源码与运行身份

- 开始：2026-10-08 19:43:07，北京时间；重设后的截止：2026-10-09 02:43:07。
- 工作区：`/Users/mima0000/.codex/worktrees/muse-7h-reliability-phone/Agent APP黑客松`。
- 分支：`codex/muse-7h-reliability-phone-20261008`；基线 `5126afc4`，与受保护 rc10 业务字节一致。
- 最终源码/载荷晋升提交：`fce42f30`。后续报告与 Phone 提交不改变这个已测业务载荷。
- readable SHA-256：`7fcc94e1b7d3d1a63968bcdc990abf15c2a59208b79d39badf40b4ae91f644d4`。
- compact SHA-256：`dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4`。
- readable/compact：**99,895 个官方 tokens 完全相等**；完整 signed bundle 六文件等值。
- 最终桌面 Host SHA-256：`276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638`。
- 最终可见运行目录：`official_muse/app/build/ui-memory-20261003/7h-live-candidate-r9`，Root 端口 8492。
- 官方独立 Hub CLI SHA-256：`d60570a598865cdcfcfec29445f45b7b879999e2edecdbdd50a3494c887d29ba`。

## 实际修复

1. 保留所有消息验证，将恢复回调每批校验从 2 条改为 8 条；不清历史、不跳校验。
2. 对 Goal/Run/Action 主存储结构、唯一 ID、引用关系做严格校验；主文件失败尝试备份，两者失败则停止写入。
3. Calendar 已完成/未知动作恢复只核对原始 event ID；本地 Memory、Activity、receipt 分段结算，全部成功后才记录 settled_request_id，Activity 使用已有去重记录。
4. 右侧和窄窗结果页复用同一个原生 ScrollYView 结果组件；恢复暂停来信卡；排队处理日历状态/请求竞态，避免重复请求。
5. 只将官方 Makepad 源码准备分片从 4096 降至 1024 字节；**原 64ms 执行预算不变**。已构建新 Host，并更新固定覆层来源；SDK 12,000 文件 verify 通过。
6. 新 Chat 保留当前项目与归属，讨论、提案与 Goal 内容仍为空。缺少项目/归属而使用“这个项目”等指代时保留输入并要求明确焦点，不盲调模型。
7. 新隔离外层应用补齐 Calendar legacy/full access 用途字符串，修复实际系统拒绝原因。没有绕过 TCC 或自动点击系统 Allow。

主要本地提交：`db7a3ed3`（存储/结算），`c459bce4`（隐私描述），`57e034ed`（结果组件/恢复），`434a46e7`（1024 分片与 SDK 锁），`4ee646d3`（项目焦点），`fce42f30`（冻结载荷）。未 push、未移动旧 Tag、未发布。

## 验收矩阵与证据

| 项目 | 本轮实际结论 | 证据与边界 |
|---|---|---|
| T20 冷启动 | **PASS，单轮 10/10 cold + 5/5 reopen** | [最终摘要](official_muse/rc/7h-20261008/final_quality/FINAL_SUMMARY_RC16.json)；10 个独立冷启动 PID、5 次重开同一 PID |
| 非空历史恢复 | PASS | 16 对话、256 消息、64 claims/65 sources、一次性任务/失败动作均非空；15/15 实际输入编辑读回 |
| 冷启动耗时 | 实测 14.46–17.67 秒，中位数 15.45 秒 | 正确可见窗口，没有 hidden 截图或空框替代；source prep 最大分片 17.288ms |
| 页面与状态保护 | PASS，范围限定 | 15 次均检查 Chat/邮箱/日历/记忆/Activity/能力/设置；核心种子与模型账本未变；Activity 合法追加权限观察，**不是所有文件严格相等** |
| signed hub check / scan | PASS | [独立结果](official_muse/rc/7h-20261008/final_quality/official-signed-rc16-r1/report.json)，精确最终六文件、无重签或变更 |
| rc16 项目/归属隔离 | DRY_RUN PASS | [FOCUS_R2_RESULTS](official_muse/rc/7h-20261008/business/FOCUS_R2_RESULTS.json)，21 VM + 8 磁盘检查；参考 card-host 46a4…，不是最终 Host 外部全链 |
| 一次性 synthetic 全链/恢复 | DRY_RUN PASS，保留原版本身份 | [rc15 结果](official_muse/rc/7h-20261008/business/RESULT_COMPONENT_R3_RESULTS.json)：Calendar 排序 6、主链 20、新进程 10、恢复 15 VM +22 磁盘；rc16 仅两函数变化，其余475函数及外部字节等值，未改标为 rc16 实跑 |
| 损坏/备份恢复证据 | 保留与复用 | [复用边界](official_muse/rc/7h-20261008/final_quality/storage-reuse-rc16.json)，8 旧 Host 案例不伪称新 Host 全部重测 |
| 真实官方 model.complete | PASS，基础离线范围 | Qwen2.5-0.5B Instruct Q4_0，经最终 Shell 官方 API；本轮新增付费调用 0 |
| 跨会话全局记忆 | PASS，合成授权项目 | 新 Chat 继承焦点，返回真实保存的辰帆83/25分钟，并包含实际检索 Memory ID/revision/source |
| 更正与遗忘 | 部分通过 | 显式选中 Memory 更正→独立读回→新 Chat 回答辰帆84，引用 revision2；遗忘写入 deleted=true/value空/tombstones4。短自然语言主题未唯一定位安全拒绝；遗忘后的模型语义探针被中断，**不标 PASS** |
| 完整 Host 重启与召回 | PASS | 重启前后9份核心主/备份文件逐字节相等，UNKNOWN action仍为1、未重发；新Chat真实回答暮塔62，引用有效来源 |
| Calendar 系统申请 | 原拒绝原因修复，授权未完成 | [真实原因](official_muse/rc/7h-20261008/quality/calendar-identity-r2/ROOT_CAUSE.json)及[修后系统链](official_muse/rc/7h-20261008/quality/calendar-wrapper-r3/REPORT.md)；系统 AUTHREQ_PROMPTING、找到用途说明，120秒回调超时；最终 not_determined |
| 本轮真实 Calendar CRUD | **BLOCKED** | 新系统身份尚未 full_access，本轮未创建任何事件；用户批准内容并不代替 macOS 系统 grant |
| 本轮真实 Mail | **UNKNOWN / BLOCKED** | 唯一 QQ 自发自收尝试，读取同步错误“账号密码缺失，请重新登录”；没有 verified 投递、未重发 |
| 同最终 Mail→Calendar→Reply 全链 | **未通过** | mailbox 新规范目录需要原生登录，Calendar需要系统权限；不能把 DRY_RUN/旧候选通过拼接为本轮全过 |
| Phone 内核 | BUILD PASS | 官方锁定 c608384d、api/git/ast/no-default；x86_64 Android ELF161,277,512 bytes，SHA32987f43… |
| Bridge | BUILD + EMULATOR UI PASS | prototype/lint89tasks、实际 APK 验签/安装、真实设置页；初次System UI ANR与Wait恢复记录均保留 |
| Home / Muse Android | **NOT_BUILT / BUILD_FAILED，02:42观察** | r4在Android目标错误编译macOS EventKit，`-fobjc-arc`失败；修复/截止状态见Phone报告。无APK验签、安装或Muse全链证据；不由内核/Bridge通过升级 |
| 实体手机 | **DEVICE_NOT_TESTED** | 未连接；没有刷ROM、清用户手机数据、系统分区或安全配置变更 |
| 正式上游 Calendar/发布 | 未完成 | 本地扩展 Gate 是结构/权限校验，不等于上游原版已接受；未提交发布/App Hub正式申请 |

真实模型、记忆及恢复的单独证据：[live-model-memory-rc16.json](official_muse/rc/7h-20261008/source-component-r1/live-model-memory-rc16.json)。最终可见截图包括 [记忆更正](official_muse/rc/7h-20261008/source-component-r1/final-rc16-memory-correction.png) 和 final_quality 每次 cold/reopen 的 visible.png、memory-visible.png；没有私人邮件正文公开。

## 邮箱/日历当前精确状态

白名单只使用已授权 QQ 自发自收，最多20封；本轮累计 **1 次发送尝试**，尚余19次额度但登录阻塞时不继续外发。该尝试实际发生在本轮前一候选 rc15 / cef7d576（r7、同 Host276b2b68）；rc16恢复保留它，没有把它改标为rc16新发送。唯一 request ID `mail-1791480704-3473558707` 保留 UNKNOWN。同步“凭据缺失”错误也保留实际r7身份。后续先只读同步/对账，不能因旧缓存存在或模型说“已发”而再次发送。

rc16/r9 又完成一次真实只读同步与技术详情展开，仍准确返回“账号密码缺失，请重新登录”；[最终只读证据](official_muse/rc/7h-20261008/source-component-r1/final-rc16-mail-readonly.json)绑定最终源码/Host与白名单，仅同步，不发信或写日历。首次技术详情未展开时只有通用错误，检查后取得原始凭据缺失错误，未把通用提示猜成后端结果。

官方邮箱 vault 的 Keychain service 由规范 Host 邮箱目录摘要区分。因此新隔离资料目录的缓存和 grants 不等于已登录凭据；当前错误对应凭据缺失，未证明是新签名的 Keychain ACL 问题。没有导出秘密、复用生产目录链接或改 vault 命名来绕过。

“工作”日历为本轮指定测试日历。只允许操作本轮创建并记录 ID 的事件；由于新身份授权未完成，本轮事件创建/改期/删除数量均为0。下一次继续应先补原生邮箱登录与该应用系统完整日历访问，再继续唯一事项，不能复用不存在的系统回执。

## 本地交付与路线

成品为 `build/7h-delivery-r1/Muse.app`，约547MB目录，内置既有Qwen基础离线模型。单条本地签名Hub目录、Host与bundle摘要、严格deep验签、启动器资源检查通过；[构建说明](official_muse/rc/7h-20261008/packaging/README.md)准确区分新成品资源检查与最终测试外层身份。不携带生产数据或登录凭据，没有本轮ZIP大小声明。新外层 rc16 资料目录未做完整全新接收Mac验收。构建与记录本地提交 `c209839a`。

桌面和手机沿用官方 OctoScript / Splash、Makepad、App Hub、manifest capability、Storage、model.complete 和 Host Service。Phone测试只在自己的隔离源码/开发APK，App Hub发现边界候选补丁有13测试及22+1准入回归，未获得上游接受。Android目前无EventKit能力，Calendar明确缺失，不改变manifest冒充可用。

## 保留的失败与保护边界

- 未修之前的来源准备预算异常、存储故障、rc15探针报告缺失、rc16首次探针19/20失败均保留；修后采用明确新版身份与探针依据。
- 新Chat旧焦点丢失导致真实Qwen回答错误的前证据保留；不硬编码辰帆/暮塔答案。
- Calendar系统回调超时、Mail UNKNOWN、遗忘后模型探针中断、Android下载/构建/资源停线失败均不删除。
- 旧rc10 readable `a9e8e414…`、bundle `0caaee73…`复核与基线相等；旧安装包/生产数据未改。一次独立聊天压缩恢复误进入旧分发清理，删除1475旧bundle副本并记录于原项目清单；**不能宣称整个旧工作区完全没变化**。详见 [保护复核](official_muse/rc/7h-20261008/source-component-r1/protected-core-recheck.json)。此清理已停止，不计本轮Phone成果。
- `.local-state` 保存私有运行资料，未纳入公开Git；公开报告只含合成内容与摘要。不输出账号授权码/模型密钥，不新增付费额度，不正式发布。
- 协作使用真实 Codex 聊天，主UI唯一写入者；业务low、最终质量medium、手机因复杂构建失败从low逐步提高到high；未继续启动子代理。

## 后续最小剩余工作

1. 在最终候选自己的原生邮箱登录完成Keychain配置，并正常系统确认日历full_access；对唯一UNKNOWN发送先只读核对。
2. 以同一最终rc16完成限定资源真实 Mail→Memory→Model→Calendar→Reply→Restart，记录收件端独立核验与事件ID并只清理本轮事件。
3. 按Phone截止实际结果补Home APK/模拟器AppHub→Muse验证；实体设备仍单独标DEVICE_NOT_TESTED，AndroidCalendar宿主能力未实现。
4. 短主题自然纠正、更强独立第二模型、上游Calendar准入及新接收Mac仍为独立未通过项，不提高总评。

## 窗口后续测（与七小时结果分开）

Phone原生Home后续编译通过，目标OS补丁已生效；r5/r6因自身10.5GB或Data2GB底线停线，不能把原生ELF当作已签名APK。Phone已透明压缩369个自身文件，释放约1.43GB，所有原字节/模式/大小复核一致，提交`b988e491`；仍需APK和模拟器证据。

Root进一步对无打开句柄的旧Quality副本做透明压缩：公开已跟踪文件释放15,478,784字节块；闲置合成runtime释放346,300,416字节块，逐项原SHA/大小/模式保持，原路径仍可正常读。私有runtime逐项清单位于ignored目录，只提交公开概要，不把运行资料上Git。另仅清理已完成独立CLI的生成rmeta/rlib/o/a缓存172,048,384字节；source/lock/CLI和失败证据保持，CLI SHA仍为d60570a5，清理后实际catalog verify通过。Data恢复到约2.18GB，但不能假定已足够完整APK/模拟器峰值。

随后对2004份内容、mode、owner及xattrs相同的旧fixture图片使用APFS写时复制，原路径、原始SHA/大小/mtime/属性全检查一致；[概要](official_muse/rc/7h-20261008/packaging/image-clones-summary.json)记录Data观察约2.35GB（并发其他进程存在，不能把全局变化全部算作本脚本收益）。FinalQuality透明压缩36份文本证据另释放8,941,568字节，提交6ca26f5a。Phone保留原ELF并制作标准strip-unneeded派生物，尚未据此取得APK/runtime PASS；仍按实际峰值和2GB底线推进。

持续目标恢复后，Phone以已保存缓存进行离线重建，原失败/截止PARTIAL继续保留；已有目标OS补丁提交`ec51bd60`。后续APK与模拟器结果以Phone实时证据为准，不回填进七小时完成数量。

rc16最终Shell用已确认的本地Qwen且没有云端fallback，完成一次新空Chat遗忘后提问。实际检索未引用已deleted/value空的辰帆记录，仍保持遗忘；但模型把剩余“重启记忆代号暮塔62”当作报告代号，并把项目名中的“七小时”当作碰面时长。判定 **RETRIEVAL_PASS_SEMANTIC_FAIL**，原回答及实际引用保存于[post-forget-followup.json](official_muse/rc/7h-20261008/source-component-r1/post-forget-followup.json)。不将这个基础模型误答归为遗忘存储恢复失败，也不宣称问答准确性通过。探针首次误取DSL wrapper字段导致KeyError，模型调用前终止；核对document/payload结构后再执行，前失败记录保留。

## 七小时截止记录（保留）

02:43截止观察：Phone已在自身SDK准备[最小目标OS补丁](official_muse/rc/7h-20261008/phone/patches/calendar-build-target-os.patch)，改读CARGO_CFG_TARGET_OS；没有修改冻结桌面SDK/Host。Home尚未重新构建成功，NOT_BUILT结论保持。截止后只允许完成已有记录/本地提交，不启动新一轮构建。

Home r4真实构建日志报 `octosense-calendar-service` 编译 `src/eventkit.m` 的 `-fobjc-arc` 不支持 Android runtime。已只读核对实际build.rs：`#[cfg(target_os = "macos")]`在构建脚本中判断的是执行构建的宿主，而当前目标是Android；服务lib.rs已有非macOS unavailable分支。最小修复应按Cargo提供的目标OS控制EventKit编译/链接，只在Phone隔离SDK交补丁，不新增Android日历或修改冻结桌面载荷。失败日志 `phone/evidence/home-x86-build-r4.log`保留。本报告观察时尚未取得修后APK成功证据，具体补丁、构建最终退出码与截止状态以[Phone报告](official_muse/rc/7h-20261008/phone/REPORT.md)为准。
