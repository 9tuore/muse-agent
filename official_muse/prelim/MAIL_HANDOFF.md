# MAIL交接：模块与配套Host已冻结

分支codex/muse-prelim-stability，工作目录为既有muse-ui-global-memory worktree；开始基线b02d103／0.3.6，后续Root提交不属于本聊天。本聊天未stage/commit/push，未改main／GM／Shell／Core／生产数据，不接真实账号、用户8414/8401、窗口或外部邮件／付费模型。01/02/03执行包已读完。

## Root现在可接入的冻结产物

- incoming_mail.splash：`b1344bd79ebd37512be2a0049b060b1b84828238dc47fc916fe934233aa550df`，Root已embed。本聊天不再修改它；后续缺陷先交Root决定。
- Host包：`official_muse/app/build/ui-memory-20261003/prelim-host/OctoSense mail-sync Host candidate.app`，包装后可执行文件SHA `e9ac1e477665a93476fa10454adff5d16e482d21a075c19b34ce9a6d486d824d`。
- 未签名原始Host：同目录`target/release/octosense`，SHA `57f2e4edf3effd010fe99aa72bcec048a051affe14b5b6985fd74f2f6687597f`。签名造成两者SHA不同；对应同次成功build，未启动／安装。
- ignored matched源码的可提交补丁：[mail-sync-stability.patch](patches/mail-sync-stability.patch)，SHA `e500727cf63acb756544884defa39b7da42c42c2ea82c5b2fbd164bb0cda417e`。隔离基线重建后三个文件逐字节等于当前冻结源码，见[patch-check.json](evidence/mail-host/patch-check.json)。未丢033已有登录表单修补。
- 最终Host源码：[source-index.json](evidence/mail-host/source-index.json)：imap.rs `7e401ec4835e1d851ca04de94304c282a7dd00ebcde3ebe19dce688644bbc765`；network.rs `56edda2dd52f8a11eefd31f9f7ea89c554ed346b4fc03b9c63dca47a310b3655`；lib.rs `bdb01de9125b5f15438133ec4ce513d6eaba4d6b96badb8ab2a8eaff158708a4`。

## 验证与真实边界

最终状态为 **HOST_LOOPBACK_PASS_CANDIDATE_BUILT_PRODUCT_PARTIAL**，见[evidence-index.json](evidence/mail-host/evidence-index.json)。

1. 真实Rust回归：基线5失败；修复后全套16通过0失败2既有ignored（外网Gmail与系统keychain）。真实生产IMAP下载代码、POP已连接socket下载代码与其生产Network适配器通过本机loopback；sync出口经实际service dispatch／合成Transport。没有真实外网TLS/auth／SMTP，不能算真实邮箱全链。
2. 当前同SHA模块：83项报告检查通过，含新契约12、稳定性17、分页9、既有monitor15、预缓存9、暂停boot3、同账号防自循环3、实际65秒idle5、实际首进程1＋重启4、quiet逻辑3＋真实mtime/字节2。全部是真实card-host＋隔离fs＋模拟Host。原callbacks8与incoming38在编译结束复核后仍触发既有时间预算且无报告，46项未计通过；原日志与模块保留在mail-host/host-*-callbacks/incoming。Root随后还改了当前incoming UI suite，旧原版SHA／suite在前轮mail/final3-incoming归档。本聊天不改quota、不扩大夹具；Root使用最终精简main／新Host串行复核这些入口。不能仅将问题归因CPU，根因未证实。
3. 前轮443eaaa的112检查与中间bd3d结果均保留；不混入b134通过数。unknown夹具曾因账号记录不完整出现首轮假绿灯，最后有效17例独立在基线重现盲目重发；harness变量错误、未完成第二账号回调等旧失败亦未删。参见[前轮交接](evidence/mail-host/previous-mail-handoff.md)与mail/原证据。
4. 成功构建／资源／签名证明产物可供验收，未将compile或窗口出现记为动作成功。主候选UI、真实账号／投递、真实模型及Calendar仍归Root验证。

## 修复内容与稳定接口

- IMAP先下载最早待取UID的25条、批内降序显示，游标只推进到本批成功最高UID。last100＋101–130先到125再到130，缺metadata则返回错误不提交游标。首次reset记录baseline_uid，以区分此后到达的新UID。
- POP保留首次UIDL snapshot为baseline_uids，续批历史仍historical=true、新到UID为false；生产Network保留has_more及baseline state。mail.sync通过原new/total追加可选has_more/reset bool，mail.list header通过可选historical bool。消息标记保存在cache，UI提前sync后watcher的new=0仍可正确判定。
- schema1 mail-watch.json保持，仅账号可选baseline_started／sync_complete。has_more=true时不提前ready，真正新信仍准入；完整scan且has_more=false才sync_complete=true。旧Host缺标记仍建立本地cache baseline／继续监听，sync_complete=false，不宣称完整性。现代Host空轮询不再因完整性字段来回切换重写；真实mtime不变。
- unknown/sending不被DRAFT降级；非空request_id且core日志缺失或已有非failed动作均阻止再次发送。损坏schema10／重复账号／非法key或draft仅只读暂停，保留文件且拒绝后续save。授权快照与轮询epoch撤销旧账号／pause/boot回复；正文独立body epoch，普通空轮询不取消慢正文，撤权或错误id不落入current/pending。
- 公共函数保持boot/poll/schedule/toggle/sync_account/scan/read_body/current/pending与同卡回复签名。沿用一次性任务、core_action_index/actions、core_record_event、GM授权与通知钩子，不增加daemon／Runtime／Capability或新的AI过滤。邮件正文只作外部上下文，不自动推理、发送或写Calendar。

## 延迟、旧状态与Root集成

**不承诺几秒提醒。** 每批25条，IMAP按最早待取UID排队，无新消息优先。全新账号大历史backlog会延迟新UID下载；正常watch轮次约30秒，网络耗时／失败会更久。既有Rust例验证30封历史＋分页间新UID31在第二批被取到并historical=false，未模拟大历史的真实时间。沿既有游标继续验收，不重构runtime。旧构建已跳过的UID不能追溯恢复；非空seen/last_uid缺首次快照时不臆造历史边界，部分未取旧信可能出现为待核对来信。

Root已独占main并加入INCOMING_MAIL marker，按`// Inbox polling`至下一`fn mail_redraw(`一次替换；别重复定义mail_body_preview或丢gm_set_accounts/muse_notify。UI监听开关用mail_watch_toggle()，不直接改enabled。

main手动mail_sync的mail_watch_busy/mail_pending guard已现场核对；watcher也检查mail_pending。sync回调后mail_list立即持有mail_pending直到列表回调结束，保留这一串行关系。has_more=true仅代表本批完成；手动同步日志／提示勿称全箱完成，list.total是本地cache数量。真正同步／恢复／保存失败需仍能看到并有效重试。

回复UI依赖ui.mail_to/mail_subject/mail_body/mail_intent；render依赖ui.right_content/right_page_content/page_content。夹具有空render替换，不证明最终精简UI通过。核心审批／动作日志／回读不随长期Goal页面删除。

## 构建复现与资源配套

matched目录`app/build/ui-memory-20261003/mail-host-033/OctoSense`；新target为`app/build/ui-memory-20261003/prelim-host/target`，原033/release哈希保持。Cargo1.98.1 --locked --offline，锁文件／依赖／配置哈希见[build-inputs.json](evidence/mail-host/build-inputs.json)。在仓库根执行`bash official_muse/prelim/tests/mail_host_build.sh`，脚本cd到matched root，使用已有.cargo配置与-j2。

第一轮从外层cwd未加载OCTOSENSE_WORKSPACE配置失败，原candidate-build.log保留；修正工作目录的candidate-build-r2.log成功，无Shell修补。新的app使用matched shell/widgets/app-hub-app resources，树哈希相同，三条MacOS→Resources链接及.sources路径可解析，严格adhoc签名验证通过，见[candidate-artifact.json](evidence/mail-host/candidate-artifact.json)。没有替换用户安装版。

Root完成source／Host／main配对、串行最终相关回归、版本／摘要和必要真实条件验收后收口；当前不能标记整轮MUSE_CORE_RC_PASS。
