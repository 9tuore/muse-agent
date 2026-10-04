## 2026-10-05 02:09：V13b修复新记忆格式与大历史Chat启动

V12最终矩阵cold1–15通过，cold16实际64ms失败定位Chat全256条校验；完整失败与日志保留。V13b把同一字段、来源引用、重复ID和总量守卫抽为共享验证，启动每回调8条，全部验证后才恢复焦点并允许写入；无预算增加、历史缩减或清库。preflight同16对话/256消息/64记忆/65来源、六页、编辑与受保护文件SHA保持通过；完整70次仍待。

V12真实模型Goal结果写入/读回已过，但第一次重启给缺元数据的新结果记忆补写，严格文件SHA断言失败。V13b只在core_add_claim新记录写入source/空conversation/history默认元数据，避免新记录立即迁移；相关独立第二进程、实际最终Goal重启验证待。初V13用了不支持的range符号，首次失败保留，已改仓库现有offset语法且V13b实机预检通过。

readable78cea03e / payloadb4ac3453 / SDK3f1bbb4e / Host938ba58a，0.3.26-rc5，冻结仍DEVELOPMENT_PARTIAL。稳定真实Mail自发自收及两份原持续运行观察继续；新最终2h尚未开始（069d soak初始错误是driver不存在label，保留而不计PASS）。新干净目录正在恢复SDK/下载锁定依赖，产品打包等待新提交。所有未过门槛、授权边界、旧安装与生产资料保护不变；没有push/发布/成功Tag。

---

## 2026-10-05 01:54：V12 修复候选冻结，最终门槛尚未完成

本地分支 codex/muse-rc-finalization，0.3.26-rc5 V12，readable f2ccdd14 / payload 599aa472，SDK lock3f1bbb4e、Host938ba58a、Card52768f57保持。V9大容量启动前18次通过，第19次真实64ms错误保留；现将启动身份索引按8条拆到既有timer，gm_prepare先只读发现迁移才复制整库，未提高预算或减少历史。撤回未证明有效的最后作用域缓存试验，原守卫不变。未选焦点/写失败不再消费Goal候选。

V12真实Shell16对话256消息/64记忆65来源首轮预检可编辑、六页、存储SHA保持；完整70次/四尺寸/最终2h/清洁构建待跑。64记忆更正返回true，66.055ms墙钟（不能写64ms内）；遗忘56.730ms，独立磁盘8/12项，六迁移变体7项各通过、两旧/新对照语义一致；中途遗忘新进程9+4核对通过。Goal卡9变体58项仅相关函数，V11b/V12字节一致复用；原失败保留。

V12真实MiniMax跨对话检索、更正revision2、遗忘空检索3次调用首轮通过；一次性Goal模型建议、批准、存储和读回完成，重启待。稳定0.3.25真实本人自发自收一次，自动提醒与独立正文SHA匹配，属于稳定来源，不冒充同RC整链。系统Calendar旧授权窗口返回完整读取，新Host仍not_determined；不绕过登录/TCC。两份持续运行观察在进行，既有稳定真实Mail/旧V9合成与新最终候选分别记录。

总体PARTIAL，T17第二模型/T18新最终真实系统写入/电脑重启/正式Hub身份政策与媒体门槛未全过。最新本人授权覆盖自发自收和系统Calendar读取，不含本轮新创建/修改/删除。旧安装、原生产资料、历史/旧Tag保护；无push、正式发布或新成功Tag。

---

## 2026-10-05 01:06：RC5 夜间收口继续

用户新指令已将工作延续到今早，旧180分钟截止不再作为本轮停工点；已授权本人邮箱自发自收与实际系统日历读取，真实Calendar新建/修改/删除仍按本轮晚间限制保留。当前0.3.26-rc5 V9，payload 4ce87cc7 / readable 974a8d2a / SDK lock 3f1bbb4e / Host938ba58a。原稳定0.3.25与旧安装保护。

实际新4KiB Card首轮V8核心28+4、稿件25+6、20故障+3、315契约通过。64记忆遗忘34.76ms/更正39.70ms及90KB损坏/新进程恢复通过。V9只改待对账时允许恢复原发送账号，8变体32断言通过，其他V8函数逐字节相同而复用，未宣称V9重跑全部。单次完整Shell大容量预检16对话256消息/64记忆65来源、编辑和六页、SHA不变通过；70次最终矩阵/持续运行/清洁构建未完成。

真实MiniMax已返回普通聊天；首个SMTP解释有过度推断，保留语义失败。稳定实机Calendar返回full_access；新隔离Host返回not_determined，不能拼为最终候选系统通过。真实自发自收正在做，按稳定来源单独标注。T17第二模型、T18同最终候选真实全链及正式Hub材料仍未全过；总体PARTIAL。未push/移动Tag/正式提交。

---

## 2026-10-04 23:00：RC收口进行中

独立分支codex/muse-rc-finalization，公开稳定基线d8a2989/0.3.25保留。当前开发0.3.26-rc2：来信request_id只检查顶层字段，修复嵌套草稿导致恢复异常；补“不用了”取消和明确邮件回复指代；失败显示简短文案及日历显式重试。真实ModelHost增加脱敏格式失败/实际重试/最终失败日志，原单次格式修复和预算不变。没有新功能、旧安装或生产数据改动。

RC2 88282 token等价；133项日历/安排/绑定fixture通过，核心28+新进程4、稿件25+新进程6通过；Memory单动作24+新进程9通过。组合58项64ms失败及大容量探针未启动失败保留，不能把这些记为PASS。新Host构建中断已确认无活cargo/rustc，再从缓存续跑；模型完成29项、lib30项/1ignored通过，原service15项文案断言失败保留。旧Host计时仅定位，不代替最终10冷启动+5重开。

本轮门槛恢复原20项全过；目前仍PARTIAL。T17第二模型、T18真实同候选全链、T20最终启动/电脑重启及正式Privacy/身份/材料待。新增付费、外发、Calendar写入均0。00:51:29北京时间硬截止不变。详见RC_ACCEPTANCE_MATRIX.md、RC_HUMAN_CHECKPOINTS.md和COLD_START_PROFILE.md；未合并公开main、未Tag/提交App Hub。

---

## 2026-10-04：当前进度与源码桌面交付

本轮仅整理交付，应用仍0.3.25，产品5 PASS /13 PARTIAL /2 BLOCKED。公开main d8a2989独立REST核对755文件内容/模式一致，允许清单源码复制、文件夹及ZIP逐文件核验通过。桌面`Muse-项目汇报与源码-0.3.25-20261004-1806/`与同名ZIP，781文件、约16.90MiB/9.38MiB，含当前进度、最新公开源码、脱敏验收/交接及构建说明。基础SDK依锁恢复，完整本地差异保留；不是预编译安装包。

应用代码/窗口/账户/生产数据未改，无新增外部动作或付费调用。旧失败与未提交资料保留。T17第二模型、T18同最终候选完整链、电脑重启及最新版重复冷启动仍待，不提升产品判定。SHA与文件明细在交付核验.json；ZIP SHA256：7647319024cd1ee8bbf601e7dcfaeaa19e7866c0e8e51757acd17377ce2c4cbb。

---

## 2026-10-04：日历阻塞修复0.3.25已验证

按用户本轮要求借鉴Aurora-X公开产品说明，修复允许窗口协议、历史候选恢复、同Goal手动改期和冷启动账号缓存阻塞。官方Splash/Makepad、model.complete、宿主Calendar及批准/防重复保留；无新Capability、运行时或宿主补丁。之前已验证的源码清理集成进新候选。

实际card-host同一最终源133/133合成断言通过，88092 token等价，本地扩展Hub check/scan/签名/catalog通过。真实模型3次相关调用返回成功和known_usage。0.3.23创建本人已批准的唯一测试事件并独立get；0.3.25同ID改到16:00–16:30、独立get、完整Shell重启七文件SHA一致、无重放、删除并get确认不存在。创建与最终版本分开记录，不冒充同最终候选完整邮件链。最终窗口8484，来信提醒已恢复，未授权自动模型分析保持关闭。

可读0b16836e / payload a44677c4 / Host0fd99361。398函数（清理前404），保护旧独立安装和Python核心/生产资料，失败证据与旧Tag不删。项目仍PARTIAL，5 PASS /13 PARTIAL /2 BLOCKED；第二模型、完整同候选邮件链和正式AppHub材料待完成。详情MUSE_CALENDAR_REPAIR_REPORT.md和official_muse/prelim/evidence/calendar-policy-0325/。按既有授权本地提交并同步公开main，提交号以本轮Git记录为准。

GitHub实际同步完成：公开main `d8a2989da8bb619139081ec96ddd05452eb364cb`，独立REST逐个核对755文件的路径、blob SHA及模式全部一致。公开工作区干净，旧Tag不动；读回记录留在忽略的build/calendar-policy-20261004/github-readback.json。

---

## 完成本轮源码与SDK瘦身（2026-10-04）

开发清理9d5d763；公开main已快进至9f847aac，并通过GitHub独立读取核对全部744个blob、路径和执行模式。当前源码从12693条/705.4MiB降至744条/16.5MiB，少约97.7%；最终源码归档9.24MiB逐文件哈希/模式/成员读回通过，已放桌面Muse-精简源码-0.3.22-20261004.tar.gz。

12000条SDK树在隔离目录精确还原，官方版本锁+76个可读差异文件+4内部链接保留。Hub重建/check原0.3.22 PASS，Calendar服务锁定离线编译PASS；38张旧截图原件在固定be552提交和本机哈希读回备份，失败记录/测试/日志不删。完整Git历史与Tag保留。

原0.3.22签名bundle和安装未变，主入口清理补丁待下一候选集成；没有调用模型或外部邮件/日历动作。日历hard_windows为空及真实整链、第二模型/正式材料仍未解决，产品PARTIAL。详细见SDK_SLIMMING_REPORT.md和MUSE_CODE_CLEANUP_REPORT.md。

---

## 2026-10-04：一次清理源码与重复交付

用户要求一次清完，并按瘦身清单处理SDK复制体积。当前开发入口395个函数；累计删9个无引用函数、144行，去掉隐藏/重复/不可达UI，旧dist18份副本已逐文件归档后移除，10个未用import及旧导出工具删除。核心保护区、生产资料、失败证据不改。

121项实际card-host合成断言通过；历史selection_fixture前后同错，保留。可读与compact 87481 token一致；可见三页截图保留。源码清理已验证，原0.3.22部署不变，产品仍PARTIAL。公开稳定签名bundle保留，清理补丁单独交付。SDK改为锁定官方基础+完整本地差异，逐树重建验证另记录。详情MUSE_CODE_CLEANUP_REPORT.md。

---

## 2026-10-04：先清理无引用业务代码

用户接受交付分层及最小清理方案，并要求先删除不必要的代码。用户转述群内最新初赛截止为“6号之前”，按此推进；具体时分尚未提供，不能沿用公开网页的10/4截止作为最新通知。

基线546a2b41，保留既有未跟踪失败证据。删除主入口5个无调用函数，以及来信模块同一函数的重复定义；主入口404→399个函数，其他399个函数逐字一致。模块同步幂等、compact 88,602个token一致、隔离真实card-host的990×539启动/输入控件检查通过。隐藏检查不作为最终视觉证据；无外部模型/邮件/日历调用。

仅开发源码清理，部署仍为原0.3.22。源码清理PASS，产品仍PARTIAL。没有删除vendor、测试、日志、补丁或历史；没有改存储/权限。下一步处理hard_windows为空的日历阻塞，生成匹配候选后重新校验，再按既有授权同步GitHub；不创建成功Tag或正式提交AppHub。证据：official_muse/prelim/evidence/code-cleanup-20261004/。

---

> 最终实机补充：本人精确确认后，模型已给正确标题/时段且question为空，但hard_windows=[]，偏好包含校验阻止冲突查询/预览，报“软性偏好超出了硬性可安排范围”。没有创建任何系统事件，没有发送新邮件。源码e2eee495已快进同步GitHub，旧Tag不动；桌面完整源码和评审归档逐文件读回PASS。最终仍PARTIAL。

# Muse 本轮收口：0.3.22（2026-10-04，北京时间）

**PARTIAL。最新接受门槛为至少18/20；当前未达到，未测项目不补PASS。**

0.3.20完成10次整进程冷启动和5次普通重开。随后人工阶段发现记忆写入与Calendar月历重绘的64ms错误，失败原样保留；0.3.21将记忆结构检查改为原生类型，7项真实card-host形状变体通过；0.3.22展开关联候选编辑，编辑时收起月历网格。最终0.3.22已真实整进程启动并恢复本轮测试历史、来源记忆和日程关联，编辑字段可达、此窗口未见预算错误；原15次组只能作未改启动路径支持，不能称0.3.22重跑15次或电脑重启通过。

QQ已本人重新登录；实际收件254封，唯一合成测试来信自动卡/正文成功。已建立同一项目Goal和来源记忆，模型候选与项目偏好一致；本人已精确批准唯一合成事件；真实模型根据补充生成正确标题、日期和窄窗口，question为空。系统写入尚未执行，不冒充完成。当前全链尚未完成。普通真实model.complete、跨对话召回、更正/遗忘、归属隔离与冲突询问有版本绑定记录；旧S03两轮新测试正确，旧未知用量保留。本轮后续调用已获用户授权，有限调用及新回执单独记录，未清账。

T07由BLOCKED改PARTIAL（指代失败独立新测试通过，时间变体未全过）；T17第二模型和T18完整同候选业务链仍BLOCKED，其他按原表的条件保留。当前5 PASS / 13 PARTIAL / 2 BLOCKED。正式政策URL、正式publisher身份/签名选择、最终视频、电脑重启和最终摘要确认仍缺。仅交提交草稿与开发源码，不创建成功Tag或正式申请App Hub。硬截止14:50:54不变。

---

## 2026-10-04 14:08 人工阶段进展与最新用户门槛

用户将本轮接受门槛改为至少18/20，逐项定义和未测状态不改；App Hub的正式材料、准入与最终摘要确认仍须满足。用户允许继续有限、相关的真实模型调用；历史S03未知用量记录原样保留，不再把历史费用未核清作为本轮调用授权阻塞。

最终同一payload d3dcdaad / Host0fd99361真实model.complete对话成功一次，MiniMax-M3，1次provider尝试，535输入/151输出token（总686），宿主返回known_usage=true。只证明普通聊天原则问答，不代替20题、跨会话召回或外部链。额外非零结果artifact的真实Shell恢复通过，补齐了原15次启动组未带result文件的范围说明。

本人已为0.3.20完成系统日历full_access；工作日历可写。QQ现有账号缓存可读，但宿主同步实际返回“账号密码缺失，请重新登录”，已请求本人在官方连接面板输入授权码；不读取或导出凭据。自动分析仍未授权，其他私信不交给模型。当前无新增真实Calendar写入/邮件发送，不冒充最终整链通过。

## 2026-10-04 13:40 0.3.20 最终隔离Shell启动检查

同一compact源d3dcdaad / Host0fd99361 / 候选6845d35，10/10完整Shell进程冷启动、5/5普通Muse重开通过；16对话/256消息和非零Goal/日历关联/回执合成历史，选中项目、输入编辑、五页切换、持久数据SHA和模型账均检查。全冷流程5.38–6.26秒；不是电脑重启，也不是付费模型或真实外部业务整链。部分框架初始化仍有ui-hang告警，不称无停顿。

原新宿主预检64ms失败保留；最终没有调高预算、清历史或重试失败源码。Hub CLI独立锁定包重建成功，Cargo.lock未改，开发check/scan/catalog verify通过。T20由FAIL改PARTIAL；原20项现为5PASS/12PARTIAL/3BLOCKED。费用UNKNOWN、新paid0、第二模型和T18仍BLOCKED。正式政策URL/发布者Key/用户电脑重启及最终审批仍缺；不提交AppHub或新成功Tag。14:50:54硬截止不变。

## 2026-10-04 13:36 0.3.20 冷启动与改期修补（进行中）

配套Release Shell已完成锁定源码构建和本地adhoc验签，Host SHA256 0fd9936126acad3a5c61ac1e7a477ba2c9393d740572ec517472f52da9181047。真实新宿主预检仍复现一次64ms启动错误，完整失败保留；诊断版恢复成功不能当最终验收。进一步将历史原始快照留存、项目焦点恢复拆到已有启动阶段，没有提高预算或清历史。

当前可读源码de0492ea；聊天主/备快照3/3实际card-host断言通过。已完成日程卡新改期建立同Goal v2，旧批准失效：26/26成功流程及63/63守卫变体，旧10/1失败保留；全部为合成服务隔离验证，非真实系统Calendar。最终10次Shell冷启动、5次普通重开和电脑重启尚未完成。费用UNKNOWN、新增付费0、第二模型BLOCKED；AppHub正式提交门槛仍未满足。

旧Hub CLI文件在本轮中途消失，已保留两次离线重建缺依赖错误，正在从锁定源码重建工具；未修改Cargo.lock。保护旧应用、历史和生产资料。硬截止14:50:54北京不变。

## 2026-10-04 0.3.20 配套宿主集成（进行中）

正式预算保持64ms和原指令上限。已定位0.3.20原宿主完整编译157.580ms超限；增量准备使用已有解析检查点，16KiB/真实NextFrame、全部成功后才执行，错误/关闭停止、不重试。VM第二轮61/61、Widget 6/6离线原生测试通过；VM第一轮60/1失败完整保留，修正的是missing值测试表示，未删功能测试。官方model.complete整链最多两次HTTP尝试的最小补丁，59项离线Rust测试通过、1项原有Keychain测试忽略。当前最终Shell构建中，不标T20通过。

主应用0.3.20冻结，可读入口37fc18a0，实际compact6877cd4b；日历同步81/81隔离断言支持，真实系统/整链仍待。费用S03仍UNKNOWN、新增paid为0、第二模型T17 BLOCKED；隐私正式URL/发布Key/媒体缺项，只准备AppHub草稿。失败与旧27项未跟踪证据不删。硬截止仍14:50:54北京。

## 2026-10-04 本轮日历同步最小集成（进行中）

同 ID 刷新、范围外独立 get、旧批准失效、日期候选和可撤销 Muse 本地完成已集成。实际 Splash/card-host 隔离断言81/81，原始反例保留；三个UI观察提示补线待最终Shell验证。系统Calendar真实同步与整链尚未验收。原64ms及指令预算不变，新增paid为0，整体PARTIAL。

# 本轮进行中：冷启动与提交准备（2026-10-04）

T0北京11:50:54，人工阶段13:50:54，硬截止14:50:54。基线e6fe256/0.3.19及旧27个未跟踪失败证据已保护。总控＋3个既有真实聊天；main.splash仅总控写，编译一条队列。

已在16个对话/256条消息/826328字节的隔离合成历史复现恢复64ms超时；最小修复使用已存在的原生类型检查、每份快照只校验一次，未完成读取前禁止写对话。12/12真实card-host坏数据变体通过；同旧Host的一次完整Shell大历史恢复成功，256条和文件SHA不变、项目焦点恢复、零预算错误。该结果不是最终10次冷启动/5次重开或T20 PASS。冷启动原白屏失败另在匹配宿主分段计时，64ms与指令限制不变。

付费账S03仍UNKNOWN，新增付费额度0；第二模型T17 BLOCKED。日历日期入口/外部刷新与本地事项完成、白名单瘦身/AppHub材料并行定位，尚未集成或正式提交。原20项判定保持5PASS/11PARTIAL/3BLOCKED/1FAIL。隔离证据见official_muse/prelim/evidence/cold-startup-0320/。

## 上一轮已交付状态

# Muse 最新状态：0.3.19（2026-10-04，PARTIAL）

源码同步已完成：按本人“先同步到GitHub”要求，公开main为`4ff717d030aa52c22534dbbb9605eb31e4ac224b`，0.3.19；GitHub独立读回入口SHA256 `a490c2731986593921768a2d95884525e79e72c05b67aac5a6400bc7d2e408bc`及12641普通文件/4相对链接清单一致。公开工作区干净、与origin/main零差异。直连Git探测超时后，通过认证GitHub Git数据接口上传四个原始提交并严格核对全部tree/commit SHA，force=false快进；未重写历史或修改Tag。详见GITHUB_SYNC_20261004.json。

产品b0708d8；启动器54f0e97；实际源1bdcb11d/可读a490c273；Host a86364cc。通过App Hub更新原授权测试profile，旧独立版/生产SQLite/稳定0.3.16未改。

5项PASS、11项PARTIAL、3项BLOCKED、1项FAIL。邮箱/日历真实节点已完成、测试事件已清理；全同事项T18未跑。当前输入区缓存最小修复，矮窗/窄窗和实际编辑清空通过。最后整Shell冷重启64ms超时，不能称稳定；历史所有失败保留。

付费模型S03缺完整用量，共享30元表UNKNOWN暂停；第二模型及最终Goal/自动稿/跨会话模型召回仍待。下一优先：稳定64ms启动、核对失败用量，再同候选整链。原测试硬截止10:12:45北京，未自动延长。其后仅完成本人要求的源码同步；仍PARTIAL，不创建成功Tag或发布。见THREE_HOUR_FINAL_REPORT.md及ROUND_ACCEPTANCE.md。

## 以下为历史记录

# Muse 当前状态

## 当前接手：0.3.18真实授权补证据（2026-10-04，PARTIAL）

分支codex/muse-prelim-stability，产品e194dd3；Goal仪器99458ab，官方源码入口说明cb65442。稳定基线0.3.16未回退/覆盖；唯一当前用户测试窗口为C8/8422，实际compact main SHA d407a09f86d4dc42ada55b8284e0db885d64c15e66a609f6a91d125fe84cbc18，匹配Shell a86364ccb3b4733d24193159fea264d19379df511b5943c6aa513cd09e2f816e。独立旧安装包、Python核心和生产数据不改。

本人已登录邮箱/授权系统日历，并逐项确认合成日历写入和手写回复：真实新来信一张卡/正文、3笔Calendar同ID创建/改期/删除及独立get/清理、1次QQ→本人Google SMTP与本人到达声明完成。发送前后各1次Shell重启，六文件/提醒身份/模型账逐字节相同，四笔外部动作无重放。原始截图及账号数据仅在私有build，公开摘要无地址/ID/正文；不是同一邮件Goal整链。

当前Memory25项是本地真实DSL存储/冲突/同ID更正/遗忘/恢复，非最终模型召回。原生两行等高方案已获本人确认，短1行、长2行省略及全文存储可见；精确C8三尺寸未测。官方入口为main.splash，Python/Rust为bundle外测试/宿主；本地扩展Gate PASS不代表Calendar上游准入或正式人审完成。

当前正式原20模型题2PASS/1FAIL/17NOT_RUN；S03 invalid_output无完整用量，30元共享表UNKNOWN仍预留，后续付费停止。第二较强模型缺配置，最终Goal/model/来源邮件改期/自动稿/跨会话召回仍未完成。Settings版本文字仍0.3.17，历史64ms启动失败和全部失败证据保留。

当前C8安排/改期17组111/111确定性断言已核对，首轮64ms ERROR及UNKNOWN观察2/3失败保留，不以fixture替代真实系统。

优先：补当前发送负例与窄视口；解决失败用量回执与模型失败，再按同一最终候选完成全链和视口。二十项及旧门槛全过前不push稳定main或新Tag。用户续予两小时硬截止2026-10-04 10:12:45北京，未自动延长。详细见ROUND_ACCEPTANCE.md、BUILD_EVIDENCE.json、CHANGELOG.md。公开远端仍33b322e/0.3.16；公开源码工作区12b132e仅本地修补/说明，无push。

## 以下为保留的历史阶段记录

## 当前任务：记忆驱动安排与改期（0.3.17开发候选，PARTIAL）

用户于2026-10-04 08:12再次授权两小时，截止10:12（北京时间）；原夜间04:00截止保留为历史，期间没有继续发起测试。基线0.3.16/6a9e6d2与27个未跟踪原证据保留。总控加四个已有真实聊天，不使用子智能体；主界面统一由总控收口，安排聊天的一处7行事件关联补丁已逐项审查，没有并行主界面写入。

当前可读入口SHA256 59f6ff16e080092a69f184836594feb534cce592b7fdea2737c788eeb4a3b64a；dev7压缩入口6fcad76b9308d26526c2ccf3da37516c24dc98652a1a5d882798444033cec317，86314个官方token等价。匹配Release Shell/card-host已构建，开发Gate/scan/本地签名通过；原生产窗口和稳定0.3.16未覆盖，本地扩展不等于官方原版接受。

本次最小修复：冻结模型使用的记忆引用；日历候选/批准连续绑定来源、Goal版本、授权、软性例外与记忆；拒绝错目标日历、过期确认、超过四天或未回答缺项；修正f32 floor/max导致的日期精度；选择另一事件清理旧事项关联。模糊日期先追问、提示模型聚焦当前意图且不补拒绝理由。开发模块现与已经测试的主入口同步，sync_modules再次运行主文件SHA不变。

91项安排fixture、31受影响变体、批准边界5项，邮件41/UNKNOWN恢复3/新变体11及重启5，记忆命令42/恢复22/冻结引用21均按其保存源码记录，不当作真实外部链。dev6真实原20题19/20、未见6题6/6、新变体4/5；D07未问日期、S05编造理由、N02重放拒绝的失败全部保留。dev7新增8题诊断正在进行，首个婉拒正确；官方UTC日账滚动触发旧费用仪器停止，正在离线核对已有准确回执，没有重发或重置30元总账。

dev7完整Shell冷启动实际64ms预算失败，view=false；一次受控重载成功只用于行为诊断，不宣称稳定性修复。第二较强模型通道缺失，最终真实邮件→创建→原事件改期→确认回复→重启→跨会话记忆尚未执行。二十项及原门槛全过前不push或新建Tag。详情ROUND_ACCEPTANCE.md、BUILD_EVIDENCE.json；最终报告待收口。

以下为历史稳定交付。

## 最新交付：GitHub源码同步0.3.16（2026-10-03）

按用户最新授权，完整源码已推送到 https://github.com/9tuore/muse-agent 的main，远端HEAD `33b322ea6fc34fd5920937ad1e6440c89a453b9e`；本地纯源码工作区 `/Users/mima0000/Desktop/Muse-GitHub-Source` 干净。产品来源fd706e4，导出来源f6c2cd5。远端读回manifest版本0.3.16，main SHA256 `26be53b364be889b88ad194c860ec0fe9525952576f8be6a1d6f0822195acbc6` 与当前产品一致。

完整匹配vendor源码、Mail/可信启动补丁、当前记忆/来信模块、测试及核对过的合成证据已同步，README和SOURCE_MANIFEST更新。12609个普通文件SHA逐项核对、四相对依赖链接通过；使用正确公开验证密钥后导出bundle的本地扩展hub check PASS。无凭据、账号运行state、私密截图、模型权重或构建缓存；历史桌面源及既有本地变化保留。未公开原开发Git历史，未修改公开Tag或重发比赛issue。

用户已明确要求“以后每更新一次就提交”：今后每次完成Muse版本更新，提交并普通快进推送此源码仓库main，再读回远端HEAD。该授权覆盖旧“不push”要求，已经写入MUSE_HANDOFF/AGENTS.md；不推开发仓的旧origin。

本轮只做源码交付，没有操作当前窗口、重新安装、付费模型调用、真实外发或Calendar写入。0.3.16聊天可见性已有对应合成报告；旧候选整链不能代替当前完整业务链验收，整体仍PARTIAL。源码上传PASS不代表20项产品全过。

以下为历史记录。

## 最新增量：修补指南审计与稳定性修复 0.3.13（2026-10-03）

分支 `codex/muse-prelim-stability`。产品提交 `9a4a496`，Mail Host补丁/发布压缩保护 `39d9479`；当前已通过正常App Hub安装至原8412副本并打开，没有另建用户数据。发布main SHA256 `e52fe5eeb9e3c78d9fbbdd91f5b4320e2d830f5d0ab8037cfee5337517526170`，可读源 `1079e80725b053822e80c1f3268d0834643d13fcc6e7357046a54a391ffa2454`，匹配Host `f7064f55e6c9f452372a255d82cebffc83a6183fc6d231a75c30ff217f24c49b`。

- 已完整核对用户的修补指南及三个辅助脚本。没有采用不可靠的“文件字节安全阈值/2KB注释预算证明”，没有一律改写nested if，没有复制第二个压缩器。现有压缩器对未支持块注释元数据明确拒绝处理；75718官方token、字符串与换行标记保持一致。
- 对话管理：左侧逐条删除、具名确认/取消、对话满16项的明确提示；删除绑定目标ID，保留全局记忆/任务，清理回退副本；取消输出零高View，防止框架空渲染保留旧卡。取消按钮宽56。没有自动删除最旧对话；容量仍16项。
- 配套Mail Host复用现有服务：一个后台线程、8项有界等待，将钥匙串/网络/缓存工作移出UI；授权在排队执行和钥匙串返回后重查。队列满或中断返回错误，不自动重发。补丁在隔离已修正Mail基线上重放，产物逐字节匹配编译源码。
- 当前artifact连接12+收信15+对话管理17项fixture通过；可见来信/断开8项通过；990×539、请求412×892（实际412×813）删除/取消/新建/进程重启可用。Rust实际源码18通过、2既有真实凭据测试ignored；用匹配依赖的rustc --test，不称完整cargo workspace测试。matched Release Host编译及本地adhoc严格验签通过。
- 真实Shell view=true、无运行/预算错误。钥匙串仍等待在octos-mail线程，主线程可进入设置、对话和取消确认。四个原持久文件chat/memory/goals/draft hash不变；最终仅一个Shell窗口。实机图在 `prelim/evidence/fix-guide-0313/live-shell-0313.png`，采样节选与所有原失败报告保留。
- 本地扩展hub check PASS，目录sequence44验证通过；不是官方上游已接受。真实新来信卡尚未验收，需要本人处理系统钥匙串窗口及一封真实新信，已提出节点，不代授权或重复外发。模型20题/二十项产品验收与完整邮件→日历→回复链没有本轮重做，整体 **PARTIAL**。

本轮零新模型请求、真实外发或Calendar写入；旧独立安装版、生产SQLite及其他profile未操作。按用户最新要求只做本地提交，**不提交或推送GitHub，不发布**。报告见 [修补指南审计](../MUSE_FIX_GUIDE_AUDIT.md)。

以下为历史记录；旧版本通过证据不能冒充0.3.13完整业务链通过。

## 最新增量：来信结果卡修复 0.3.12（本人钥匙串节点待处理）

本轮仅处理新邮件不弹结果卡。产品 `7d7a6f5`，发布 artifact SHA256 `8c910a093db3c69550f3b25772f55bd712f27917b2946a6c8126a2f0e9315421`；可读源码 SHA256 `e11d7f3124fd020ca966ddf427ea5948ce172aa3869d16620f1c7210d740d040`。连接成功恢复提醒、收信启动不被结果恢复阻断、同步失败卡已实现。当前 artifact 的 12+15 项 fixture 通过；官方 tokenizer 的 75375 个 token、字符串及换行标记与可读源一致。0.3.9 的可见合成卡8项只作该版证据。

现有8412副本已从App Hub安装0.3.12，配套本地Host SHA `d6ca93b30643a601c7f91bf4e5548f0011bebc258706fbcf946b70fefbfbacf2`，真实Shell eval为view=true，无启动预算错误。应用仍保持正文/事件64ms和深度512；可信框架注册使用既有专用入口，没有改邮箱服务或授权范围。实机线程随后在`MailService→Keychain→SecKeychainFindGenericPassword→SecurityServer`阻塞，已向本人提出系统钥匙串窗口核对/允许，未代确认。交互画面与真实新信卡尚未通过。第一版Host失败及第二版0311正文超时均保留。

聊天/记忆/Goal/草稿四文件hash与升级前一致，未重置数据。仅当前现有Shell/profile被操作；旧独立版、稳定0.3.6和其他profile保持。本轮零模型请求/真实外发/Calendar写操作，无push或公开发布。本地扩展hub check PASS不等于上游接受。证据见[来信提醒修复记录](../official_muse/prelim/evidence/mail/INCOMING_REMINDER_FIX.md)。下面0.3.8模型20/20及任务/记忆回归属于历史，不绑定为0.3.12通过；整体二十项仍PARTIAL。对话删除工作暂存，未进入本轮。

## 最新：0.3.8 RC7 初赛收口（2026-10-03，PARTIAL）

产品665f507；当前AI证据f81f521、Goal/Memory证据cd49e35、UI证据90c8176；main `23bed11533c95452e3d1a29bf3ab542ac21eae152fe4f20ad22ed73be179ae2e`，manifest BLAKE3 `04900eb93b0c691508948cee993d4881b8e5151e87553ea405e668e66fd40d6b`。稳定0.3.6仍保持。

- 当前RC7 MiniMax原20题20/20、6变体6/6真实通过；24模型回合/27provider尝试。原始报告保留PENDING，另存人工语义评分；题集/期望未改。RC6和旧Qwen失败均保留。模型题不代替二十项产品决定。
- RC6一次性Goal真实模型→批准→Storage→独立readback→Shell重启通过，但额外冲突更正后遗忘没有写入主记录；settings进入保护停写，随后检索为空。独立semantic-review将额外记忆闭环判FAIL，原始失败保留。
- 最小补丁：确认遗忘生成不含正文的提交摘要，仅完整清理快照、原/已提交主文件hash及DSL校验一致才能恢复。摘要错误/跨资料/缺失/损坏保持停写；当前14项恢复/拒绝不匹配fixture通过。
- 64条full-main启动又复现64ms超时：每个切片重复整库JSON roundtrip。现改为启动只normalize一次、每批2条，未提高宿主预算。当前23bed完整主程序214项全部通过，含64条真实card-host启动与2172bytes/6hits有界检索；失败两轮完整保留。
- RC7真实一次性Goal模型建议→批准→Storage→独立readback→整Shell重启通过，6个持久文件hash不变，无重复执行；冲突阻断模型、更正及遗忘实际落盘。另一会话检索2条/1117bytes，保留全局偏好与任务结果，遗忘ID未返回。原driver误把保留结果“合成乙项待确认”当作已遗忘事实，原PARTIAL报告保持，另存基于ID/原句的独立核验。首次自然语言计划请求被拒绝、跨会话回答编号不完整作为质量限制保留，不称全部表达稳定。
- 当前四尺寸可见Shell的Chat长输入/记忆/设置通过，实际内容412×620、990×508、1260×569、1200×389；高窗受屏幕限制。七个页面均实际进入并留存截图（模型-only无账号，空/未授权状态如实展示）；整链的真实邮件回复/日历确认UI尚待。UI观察零模型新增。
- MiniMax沿用官方model.complete、M3官方HTTPS、无fallback。唯一30元费用表已知保守上界0.293964元、一次官方连接未知usage预留8.402151元（均非账单），总占用上界8.696115元。新预留按官方输入/输出费率分别覆盖两次尝试，17.901005元；原账表与unknown规则不重置，当前UNKNOWN/RESERVED为0。15个离线费用保护检查通过。
- 最新Root合成8412已经从App Hub打开0.3.8，无邮箱/日历账号；8413仍旧RC6真实测试登录窗口，等待本人官方QQ重连，不能读取其控件/凭据/截图或重启。Calendar full_access已通过，不重复申请系统权限。用户8414/8401、旧独立版及生产资料保持。

下一步：本人QQ重连后将真实测试应用经App Hub更新到同一候选，再跑新信→候选更新→确认→真实Calendar/独立get→回复/到达→重启/去重/跨会话记忆。没有现存适用的日历自动窄授权，不宣称自动路径通过。二十项产品决定与原20模型题分别需要证据；整体不通过。无push/发布/公开Tag改动。

以下内容是分阶段历史记录，以本节为最新状态。

# Current State

## 当前核验：0.3.7 RC6 / MiniMax（2026-10-03，整体PARTIAL）

产品7403abb，main SHA256 `c3dd3417ac69afa489b829f5b58791726ecead0537ad0c5f6c0ee162fd7105aa`；此后提交e169c27/58576b5仅测试和证据，产品字节不变。原20项真实聊天 **20/20**、固定6变体 **6/6**，24模型回合/28provider尝试与非estimated官方用量均核对；原报告PENDING保留，总控独立语义评分见 `prelim/evidence/ai/live-037-rc6-minimax/semantic-review.json`。旧Qwen12/20失败不改。官方MiniMax凭据已存在且连接测试成功，不再要求配置模型。

当前完整主源码而非0.3.6 Core抽取的Memory回归 **214项**（原198+16 transport隔离检查）通过，证据 `prelim/evidence/memory/root-rc6-full-main-20261003/full-main-summary.json`，仅fixture；先前基线Core198及汇总KeyError全部保留。

8412是RC6合成无账号模型窗口，8413是同main/Host61d7/MiniMax的私有真实账号候选；8414稳定窗口、8401原窗口不操作。8413实际EventKit完整访问、工作日历可写已观察，不再重复请求日历权限。实际QQ同步返回“账号密码缺失，请重新登录”：钥匙串按隔离Host目录命名，账号及缓存副本不等于凭据复制。已打开官方登录面板请本人重新连接；登录期间不读取控件/截图/凭据。当前尚未最终真实外发或日历写入。

用户总费用限30元沿用同一全局费用表，真实用量保守上界0.195361元，连接probe未知用量另预留8.402151元（仅提高同一次probe预留，无新请求），不称实际账单；UNKNOWN/RESERVED阻断后续付费。仍需同候选邮件→日历→回复→重启→跨会话记忆、最终代表性窗口与二十项产品决定核验。未找到已有窄范围Calendar自动授权规则，保留精确确认，自动路径未完成；不能为了20项通过造授权或改评分。整体保持PARTIAL。无push/发布/公开Tag变更、旧安装版及生产数据保持。

以下是分阶段历史记录，最新结论以上述RC6记录为准。

## 当前执行进展：初赛收口 0.3.7（2026-10-03，PARTIAL）

分支 `codex/muse-prelim-stability`，最新产品 `7403abb`；main SHA256 `c3dd3417ac69afa489b829f5b58791726ecead0537ad0c5f6c0ee162fd7105aa`，manifest BLAKE3 `92499119ed7babf343bb9928c9007d1c238de896ea2fcfdee3eaca4444d6514f`。用户要求原20项在同一最终候选20/20才算通过，fixture或旧版成绩不抵扣。基线0.3.6、用户8414/原8401、旧独立版与生产原数据保持。

已移除长期目标产品页与泛化周期入口，保留一次性任务全链及历史；加入明确项目/归属与同卡编辑/取消/引用失效保护。d142b1c修复成功询问误路由和合法分钟级ISO精度；c1c0749仅过滤内部记忆键的评分噪音，并保存官方model.complete安全用量元数据，不存提示词、回答或密钥。c1c0749源9项用量、12项preflight、6项修改、15项绑定fixture通过；旧card-host一次主题预算失败保留，顺序运行绑定15项通过，不据此承诺旧宿主可靠启动。

配套新宿主 `OctoSense trusted-theme Host candidate.app` 包内SHA `61d7fc0b5632cd88380cbbf1d644e788a992d691cd1db8f38012cc6c925a03d6`。仅可信框架主题注册入口改变，客体正文/事件64ms预算未调整。独立8412可见Shell冷启动完整428863字节main为view=true，无Splash预算错误，中文输入/三栏真实截图和本地扩展hub check通过；这是启动检查，尚非最终整链。见 `official_muse/prelim/evidence/live/rc3-startup/`。

原免费Qwen rc1真实原20项12/20、holdout5/6，失败和固定题集保留。用户新授权MiniMax总费用上限30元；官方8413“AI模型设置”已准备中国/MiniMax-M3/官方HTTPS端点，停在本人密钥填写页，尚未配置好或运行付费Muse请求。已向本人提出密钥必须只在设置页填写。新模型验收将只复制官方模型私有profile，不带Mail/Calendar账号，记录真实usage与共享费用预留。官方连接测试先保守预留2.30元；未知用量必须停，不能写成费用已准确结算。

Memory最终模块2b623e相关性45/45、原P0 20/20；历史198项不能算本模块全过。64条旧/新相同数据单次检索及未改原probe本轮均通过，观测14～31ms；历史超时未能稳定复现，确切阶段仍未知，没有据此再改生产代码或提高预算。当前尚有独立技术缺口，保持PARTIAL。7403abb仅补3行设置页外观/官方模型归属说明，其相关执行函数与c1c0749相同，尚未新做可见设置截图。执行包二十项产品决定与原二十项模型题分开验收，均须最终证据。下一步：配置MiniMax后冻结同源20+6真实验收，再集中本人精确外发与Calendar权限确认完成邮件→日历→回复→重启→跨会话记忆。未push、未发布、未改公开Tag。

以下记录为分版历史，不覆盖当前结论。

## 当前执行：初赛精简与稳定性收口（2026-10-03，未冻结候选）

现分支 `codex/muse-prelim-stability`，保护基线 b02d103 / 0.3.6；基线文件与用户状态摘要已保留于 `official_muse/app/build/ui-memory-20261003/prelim-stability-baseline-036/`。8414用户窗口、8401原窗口、旧独立安装包与原生产数据未改，本轮只使用隔离源码/fixture。

已删除长期目标导航/创建/泛化周期执行入口，保留一次性任务底座和历史，增加可见项目/归属选择。P0修复包括同卡编辑与旧批准失效、本地取消、异步scope绑定、unknown不可重发、损坏草稿保留、numeric日期验证。全局Memory模块198项、来信模块112项fixture通过；均不代表真实外部链通过。main已同步Memory与冻结来信模块，宿主分页最小补丁通过Rust测试，配套运行环境仍在独立构建。

真实免费Qwen后端诊断：复杂协议4题均缺reply；flat变体3题schema通过，语义仅1题通过（错时区/虚构缺收件人仍失败）。已保留原失败；应用改为普通Chat reply协议与操作flat协议，context移至user/input避免官方task 4096bytes上限。产品本地提交64dc98d，0.3.7 main 4c728cb。115项同源集成回归与四尺寸可见UI通过（fixture边界），当前整轮 **PARTIAL**，剩余真实模型语义、真实20题/holdout、最终可见UI和同候选邮件→日历→回复→重启→跨会话记忆。宿主IMAP游标及POP3完整性问题正在最小修复，不新增能力。无push、无发布。


## 最新：邮箱界面精简 0.3.6（2026-10-03）

本人要求删除邮箱草稿说明、蓝色发送账号到收件人之间的状态与核验文字、绿色回执，替换“监听”用词。本轮产品49da447仅做该UI精简：写信页直接从收件人开始，实际核验入口留在默认收起的详细记录；右侧回执默认隐藏，来信提醒/自动查看新邮件用词统一。未修改批准、防重、真实发送与读回函数。

0.3.6已通过正常App Hub在现有8414私有用户副本中安装打开，main SHA `79959890d266d07b8a6c6698851893a1f139b436565897125c57b07a82857bf2`。本地扩展hub check/签名目录sequence44 PASS。可见card-host合成前后/详细记录截图通过，相关轮询fixture15/15；真实Shell输入/技术文字隐藏已核对。五个持久文件对照见 `official_muse/evidence/mail-ui-cleanup-036/live-install.json`。整体仍PARTIAL，本轮不新增外发或全链声明。桌面完整源码已同步并改名为 `Muse-0.3.6-完整源码-2026-10-03`。原8401、旧安装/原数据保留，未push。

## 最新交付：0.3.5 打开与完整源码桌面文件夹（2026-10-03）

按本人要求仅打开最新候选并整理源码，未追加功能或全链测试。0.3.5 使用配套新 Mail Host 在真实 OctoSense 8414 打开；候选 `candidate-035-user-20261003` 从原 0.2.26 私有数据复制聊天、全局记忆、Goal、草稿、监听和日历状态，启动前六项文件 SHA 与原文件相同。已观察到三栏对话与可用输入框；本轮不声明新的真实邮件/日历动作成功。原 8401 与原安装包/数据未覆盖。

桌面交付 `/Users/mima0000/Desktop/Muse-0.3.5-完整源码-2026-10-03`：官方 Muse 0.3.5，主仓实际独立桌面源文件及两份既有本地变化，实际匹配的 OctoSense、App Hub、Makepad、OctoScript、OctoScript-Makepad 全部源码/资源/许可证、宿主补丁、合成验收和说明。`SOURCE_MANIFEST.json` 记录来源与文件哈希，四个依赖链接为文件夹内相对链接。未带入凭据、私人运行数据、Git 历史或编译缓存；旧 `Muse-GitHub-Source` 未覆盖，未 push。产品仍 PARTIAL，已有验收缺口保持。

## 最新：夜间UI／全局记忆候选0.3.5（2026-10-03）

**归属验收缺口：**普通Chat当前project/owner焦点保持空；模块显式过滤已测，但对话中的明确归属选择/歧义澄清尚未接入。未知老师项目0hit不等于两项目同时存在事实的碰撞通过。此项列为下一轮优先，不能只归因于小模型。

当前开发分支 `codex/muse-ui-global-memory`，产品冻结 `4135d0c`；main SHA `0e4c26dcdc0760a12cc2bb545cea2eb42e4170fba86f14974edbb992339332f7`，BLAKE3 `968e29358a1d2d7ec224f2a2b3a75afcab24524320567fd86fe6aceaafa5a419`。整体 **PARTIAL**，入口根目录 `OVERNIGHT_3H_REPORT.md`、`CHAT_EVAL_REPORT.md` 与 `OVERNIGHT_HUMAN_CHECKPOINTS.md`。稳定0.2.26及生产8401未覆盖，旧独立0.3.1未改；仅隔离候选，不push。

已完成中文三栏、会话历史/快捷入口、有效结果与来信、会话Goal关联、自然语言Memory及折叠DSL/技术详情。GM/Core唯一权威、授权归属和有限检索保持；用户名在新隔离Host登录表单移除，只用完整地址和密码/授权码。最终162项fixture、138张五尺寸可见card-host原图通过；GM135是033模块证据，035字节静态绑定，不能冒充035重新执行。1440/412高窗受桌面限制实际809/813px；窄展开输入135px等排版限制保留。

035新Host实机20个qwen3-0.6b合成聊天8 PASS/12 FAIL，跨会话代号/更正召回通过但协议/日期/格式偏好/指代仍失败；已有候选追问修改只文本回复的缺口待修。另2Goal真实模型建议（首项）→本地批准→存储/独立读回通过；结果count3问答却答2，工程关联检查6/6而语义FAIL。首次重启为新Goal记忆补18个默认scope字段，旧内容/引用/时间/墓碑不变；原严格byte失败保存，规范化后10次严格重启通过。20分钟idle结果见性能报告。

本夜禁止真实外发/日历写改删/新权限/收费测试/公开发布；0.3.2在禁止前本人批准的真实工作日历CRUD/get/重启/清理只作历史，不继承035。最终合成mail→calendar9项和listener15项通过，真实新Host登录/新信/外部链仍本人节点；本地扩展hub PASS不代表官方原版接受或review完成。下一优先：候选追问变更闭环及模型协议稳定性，再按本人批准跑一次最终真实链，不重构或无限复测。


## 本人实测确认与下一阶段（2026-10-02）

用户在本次对话明确反馈：“我已经全部测试，已经跑通了。”记录为当前安装版0.2.26的 **USER_LIVE_CONFIRMED**；没有额外操作用户窗口或重新发送邮件。代码产品da4a377、交付记录c6a4e02；现场核对源码与安装manifest均0.2.26，主源码无未提交改动，历史未跟踪证据保留。

下一阶段按用户指定推进：中文UI与卡片/输入/滚动体验优化；将现有真实Calendar宿主读写接入来信和对话任务，完成候选日程→本人确认→系统写入→独立读回→结果/记忆/Activity；随后沿现有结构做必要的代码去重与状态整理，不重构核心链。保留模型、Goal、批准、存储、读回、重启与发信防重。

本人的全部实测确认与既有38项fixture/9项真实本地模型证据分别记录；不据此改写旧版17或26未执行的逐项正式报告。正式UI_PARITY/上游准入仍有既有待完成项。GitHub与桌面完整ZIP按当前交付记录尚未同步26；未push。本轮仅汇报与登记状态，未开始修改UI/日历代码。

## 最新：来信正文、手写回复与常用语，0.2.26（2026-10-02）

产品da4a377已通过正常 App Hub 安装到同一OctoSense Shell；成品main SHA `6d4519bf4c3557b23ddb4163d12f1623aa21884c2ceffcb631f73c489a744f55`，源码一致。来信显示正文；同卡起草/编辑/重新起草/确认发送；“自己写回复”不调用AI。拒绝/算了与明天/后天/过几天等时间绑定；相反意思或时间错误的AI草稿不采用。保留原批准/日志防重、归档旧草稿、未知结果不重试；无变化轮询不重绘输入。

生产函数fixture38项、当前真实本地模型9个常用时间合成输入通过。实际安装/冷开五文件SHA保持相同，原正文和发送记录恢复；root没有确认真实发送。23/24同卡可见合成截图是各自版本历史，不冒充26全量UI回归。配套本地Calendar扩展Gate与目录sequence42通过，scan正式人审仍待完成。详情见MUSE_INCOMING_MAIL_REPORT.md、evidence/incoming-mail-20261002/candidate026。

整体PARTIAL：复杂复合意图/日期计算不保证，26未重做SMTP收件/邮件日历完整链。保持17历史链边界，未扩能力/Provider/Host；旧独立版/生产SQLite不改，无push。公开GitHub、桌面完整ZIP仍旧候选，未称已同步。窗口操作已停，留给本人试用。


## 最新：持续来信提醒与意图回复，0.2.21（2026-10-02）

现有单一 OctoSense Shell 已通过 App Hub 安装0.2.21，产品603bd7d。应用运行时每30秒检查已授权INBOX，首次静默基线、新信对话侧栏提醒、先问回复意图、模型草稿、原精确预览与确认、不予回复持久化、错误重试与暂停。到信不调用模型或发送，关闭应用不监听；未加系统自启。详情见根目录 MUSE_INCOMING_MAIL_REPORT.md。

0.2.19 真实新来信自动弹卡通过；0.2.21 17项生产函数fixture通过、同一个真实本地模型肯定/拒绝/改时间三项合成语义通过。原“可以的”复述来信问题已定位并修起草要求，原样复述拒绝采用、编辑意图重新绑定。当前正常安装/冷Shell打开与数据恢复通过，五个既有文件SHA相同；watch状态轮询重新序列化不称字节一致。9Goal/9Run/12Action/11Claim/12Source/6日历Receipt；新增Action来自本人回复操作，root未确认真实发送。

本地扩展Gate PASS、catalog sequence38校验通过，正式scan仍human-review。0.2.18两尺寸UI合成截图与0.2.21最新证据分开标注。当前未重做21真实SMTP投递/日历全链，整体PARTIAL；17历史报告边界保留。桌面完整源码更新至21，公开GitHub尚未同步，无push。旧独立版和生产数据未改。

## 最新：第二轮收口，Muse 0.2.17（2026-10-02）

本轮已按用户“不要重复验证，做好收口”结束执行。分支 `codex/muse-round2-improvements`；冻结产品 `72e37240d53c045b57570d6b9178ff9980a83c8e`，正常 App Hub 已安装 0.2.17。完整入口为根目录 `MUSE_ROUND2_TEST_REPORT.md`、`MUSE_ROUND2_CHANGELOG.md`、`MUSE_ROUND2_BEFORE_AFTER.md`、`MUSE_VERSION_EVIDENCE_INDEX.json`。

**总体 PARTIAL，当前不扩测。** C02 动态前提九项 fixture、C03 迟到回复十二项 fixture、选择结果两项 fixture、Core helper37、C05/C06 UNIT7 已执行。真实聊天14个初始请求/22条 wire，原话上下文和 NOVA 更正/切回召回通过；连字符计数为 MODEL_LIMITATION。

最终 C01 `MUSE-R2-20261002-182500`：同一 Goal `1790936960-3704225443` 的源邮件与后续确认邮件分别经本人批准发送、本人确认到达；日历真实创建/独立读回；真实模型后续草稿；关联结果/三条 Claim/Activity 保存；一次整 Shell 重启六文件 SHA 及 Run/Action/模型计数不变；已授权测试事件删除并两路确认不存在。人工核对候选后的真实闭环完成；日程提取时模型停机，故完整 AI 候选提取未通过。

当前 C02 真实 stale-conflict、C03 外部模型竞态、C04 非空显式 Memory/重启后真实模型召回、当前全量响应式和普通多 Goal 模型链未覆盖，旧证据仅历史。索引六条历史 STALE、二十条当前作用域 PASS、一条 PARTIAL；不相加为 ROUND2_PASS。配套本地 Calendar 扩展 Gate PASS、目录 sequence35 校验通过；正式 publisher/support 元数据仍占位，scan 路由 human-review，不宣称官方原版准入。

单一 OctoSense 窗口已留在对话页。原本本地模型/转发服务保留供用户继续使用；没有新 Provider。旧独立安装版、桌面生产数据未修改，没有 push。公开初赛仓库仍 `c1c5e947b27ea158e79201064b2f7367d887fcb2`，本轮代码尚未同步公开仓库。

以下为历史快照，不覆盖上述新候选边界。

## 最新：新邮件发送入口修复（2026-10-02）

官方 Muse 0.2.14 已通过正常 App Hub 更新，并重开配套 OctoSense Shell。新邮件顶部固定“发送邮件”；点击进入独立确认卡，“确认发送这封新邮件”继续调用原批准绑定和持久化发送路径。新增继续编辑草稿；用户原草稿在 UI 中恢复，保存文件 SHA 与更新前一致，独立重启后的原账号选择与 UI 字段恢复通过。实际窗口留在草稿页，没有确认真实发送。

代码提交 `5542aea`、`bcf2beb`；最终本地 Gate PASS，目录 sequence 32 校验通过。LOCAL 最终可见 card-host 两种尺寸、FIXTURE 官方 mail_demo 全按钮链和 LIVE 最终预览/取消/重启草稿恢复分层记录在 `MUSE_MAIL_SEND_UI_FIX.md` 与 `evidence/mail-send-ui-20261002/`。首次热更新窗口操作曾出现空草稿，已恢复并冷启动核对；原因尚未确认，详见报告。

产品总体验收仍 PARTIAL；本次不作真实 SMTP 投递、收件核验、完整 Goal/model.complete 或邮件→日历全链新声明。未 push；公开源码仓库暂仍为原提交。原有 calendar 驱动未提交改动和私密旧证据均保留。

## 初赛仓库登记已提交（2026-10-02）

用户明确授权向主办方 issue #13 提交，并补充正式队伍名“星海”。已使用 GitHub 账号 `9tuore` 发布评论，ID `5946091544`；独立 GET 核对作者、正文和目标 issue 一致。

评论链接：`https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-5946091544`

提交正文为三行：

```text
队伍名：星海
GitHub 仓库地址：https://github.com/9tuore/muse-agent
团队ID：561194752707317763
```

GitHub 连接器最初返回 integration 403，未创建评论；使用已配置的 Git 认证正常提交成功，凭据没有输出或持久化。此前“未提交主办方 issue”的记录为旧快照，本条为最新登记状态。参赛源码仍为公开仓库 main / `c1c5e947b27ea158e79201064b2f7367d887fcb2`；产品总体 PARTIAL，本次没有改变产品代码或重跑应用验收。


## GitHub 完整源码交付（2026-10-02）

按用户授权，将已整理的完整参赛源码推送至用户创建的仓库，并将 `123` 改名为 `muse-agent`，重写中文简介与 README。仓库：`https://github.com/9tuore/muse-agent`；分支 `main`；远端已确认提交 `c1c5e947b27ea158e79201064b2f7367d887fcb2`。

完整源码工作区：`/Users/mima0000/Desktop/Muse-GitHub-Source`，共 12,324 个 tracked 路径。包含独立桌面源码、官方 Muse 0.2.12、实际配套 OctoSense / App Hub / Makepad / OctoScript 全量源码、测试、补丁、报告和许可证。SOURCE_MANIFEST.json 的 12,319 个普通文件 SHA 逐项核对；另外 4 个相对依赖链接与清单自身不纳入文件哈希。未带入原项目 Git 历史、凭据、账号/生产数据库或最新私密截图；主办方 issue 未留言。

本轮只整理和上传源码，没有继续功能开发或窗口测试，没有使用子智能体。0.2.12 已在此前通过 App Hub 更新安装；完整产品验收仍为 PARTIAL。真实邮箱已授权并同步/读取；0.2.11 合成事件创建/修改及各自读回通过，最终删除/清理未确认成功。0.2.12 全量回归、真实发送与收件核验、邮件到日历同 Goal、持续新邮件结果卡仍待后续指示。原型与历史报告的通过范围不能代替最终候选验收。

官方代码来源仍为本工作树 `e00b8cf` 加 `official_muse/phase2/tests/live_calendar_crud.py` 未提交驱动改动；该改动已导出，只有语法核对，未重跑 LIVE。桌面工作树已有的两份本地源码改动保留在导出。后续开发继续当前官方迁移分支，再按需要同步公开源码仓库。

## 以下为历史快照


## 最新：0.2.10 中文界面修订（2026-10-02）

用户要求所有 Muse 界面使用中文。官方分支继续 `codex/muse-official-migration`，0.2.9 数据通过正常应用中心升级保留。Muse 八页、卡片、来源记忆、邮箱宿主登录、应用中心、AI 模型设置和容器菜单/顶部栏/启动器/快捷键显示已中文化。没有改协议字段、能力 ID、枚举、批准绑定或模型路由。最终可见容器为 `OctoSense Muse 中文版 0.2.10-r2.app`，SHA `24bcaddaee2297a1fe524a2cebc380814e1987d609e89e2cfb4a8efac9ebd10f`；报告 `MUSE_CHINESE_UI_REPORT.md`，证据 `evidence/zh-ui-20261002/`。宿主无 Git 导出以 `octosense-zh-ui.patch` 交付；App Hub 中文提交 `97d75ac`。

真实八页和 Mail 中文空表单/协议切换 PASS；五种窗口请求 PASS；最终容器真实 AI 两轮代号追问和一个中文模型 Goal 全链 PASS。最终正常重启 9 文件 SHA 不变，7 Goal/6 Run/6 Memory/0 外部 action，Activity 仅新增 restore。一个复杂 Goal 的模型格式回复两次被拒绝，保留待批准及中文错误证据，不将其计为成功。Core37 LOCAL、Mail8/2ignored、模型27/1ignored、AppHub36测试和本地扩展hub check PASS。旧独立0.3.1哈希/严格签名保持不变。

Phase2整体仍PARTIAL：真实Mail登录/发送/收件端验证、最终Calendar CRUD及关联同任务未完成；中文修订不是上述能力的通过证据。禁子智能体、GitHub继续暂停、只本地提交、不push、不改生产资料。桌面中文修订交付文件夹包含运行包/源码补丁/真实截图/报告。

## 当前优先：0.2.9 收口，GitHub暂停（2026-10-02）

最新用户要求先完成Phase2收口，暂停建仓/上传。官方分支codex/muse-official-migration；产品17e63c5、测试4729e7a。最终main SHA eb0e32778c03ea4cc7e331a63ad9aee7bd36bdf5c541e1ec61d99502199b1489，bundle77e8960d...。根目录PHASE2_FINAL_ACCEPTANCE/TEST_REPORT/EVIDENCE_INDEX及MEMORY_PARITY_MATRIX为最新入口；后续报告提交只本地、不push。

真实打包Shell安装0.2.9重测：Chat传输/A/C/D通过，B计数语义受限；3模型Goal+1长文Goal、4Run完成，模型建议在批准前生成，批准后真实存储/读回。来源完整UTF-8 SHA、独立DSL/MemoryGraph验证、更正/固定/2墓碑、重启通过。五窗口请求均实际模型发送、四页滚动与长详情；高窄受桌面限制818。整个Shell重启7文件SHA不变，4Goal/4Run/4Memory/0外部action，Activity只新增restart restore。停本轮relay后的真实错误与恢复通过，共享模型未停。Core37项、Native9hash+超64KiB拒绝、Host Calendar3与Mail8单元通过，均明确LOCAL边界。

总体PARTIAL：Calendar本机新宿主权限not_determined，已请求本人完整访问；最终CRUD未跑。官方Mail accounts为空，Host登录sheet已打开等待本人；登录期间停止截图/控件查询。待真实Mail读取/本人发送确认/收件端确认、同Goal双批准Calendar链，以及外部重启防重复。原版Gate仍拒calendar；本地扩展签名Gate PASS、scan七问human-review。旧0.3.1主程序SHA/严格签名不变、生产数据未读改。禁止子智能体；本人节点之外自主继续，无新Capability/Provider/Phase3。

原GitHub完整源码仓库整理为历史保留，未创建远程、未push、未评论issue。勿再追问建仓。本机证据evidence/phase2-final-029，57张真实图含旧独立before；源码与签名候选/测试环境见最终证据索引。


## 最新接手：完整源码仓库与 Phase 2 收口（2026-10-01）

用户已授权建立独立 GitHub 仓库并上传全部参赛源码，暂不评论主办方 issue。完整源码本地仓库位于 `/Users/mima0000/Desktop/Muse-GitHub-Source`，分支 `main`，HEAD `f04ef0a`，12,274 个跟踪路径，5 个分步提交；包含桌面源码、官方 Muse 0.2.8、隔离 OctoSense/App Hub 与锁定 Makepad/OctoScript、合成测试证据。源文件 SHA 清单读回核对通过；依赖相对链接和宿主 Cargo metadata 检查通过。未上传 GitHub，不能把本地整理当作远程交付完成。

计划独立仓库 `9tuore/muse-agentic-app-2026` 当前 GitHub 查询 404。连接器无建仓接口，浏览器自动化连接超时；已请本人在 GitHub 新建空公开仓库后告知地址。不要寻找或输出凭据，不把旧配置 remote 当作已存在仓库。

后续任务完整提示词：`/Users/mima0000/.codex/attachments/e21e0598-856c-438e-80d7-0153f735a732/已粘贴的文本.txt`，已完整阅读。顺序是先完成独立仓库上传，再冻结 Muse 0.2.9 并执行 Phase 2 收口与全量回归。现场 0.2.8 布局修复已在 `56fec94` 提交；提示词中的 `fa0ab02`、未提交布局和未做 0.2.8 Calendar/Goal/restart 为旧快照，以现有代码和 0.2.8 报告为准，但不能复用旧证据代替 0.2.9 验收。后续收口提交仅本地，不 push；不新增 Capability/Provider/Phase 3，不改独立安装版或生产资料。禁止子智能体。Mail 登录、Calendar/发送人工确认按新提示词办理，其他测试继续。


协作最新偏好（2026-10-01）：用户要求后续不使用子智能体，跨对话协作用真实已有聊天。先前Agent审计为历史已完成安排，后续不再派发。参赛纯源码已整理到桌面 Muse参赛源码-0.2.8-2026-10-01 文件夹及同名ZIP；37份源码/测试/补丁/报告，导出SHA逐一核对与bundle Gate通过，未push/issue提交。

## 当前：Phase 2 实机联调 0.2.8（2026-10-01）

分支codex/muse-official-migration；产品修复56fec94，测试/源码导出e64d243。真实打包OctoSense/App Hub中文八页、三新模型Goal及矮窗735字Storage链通过。正常重启23文件SHA相同，Goal21/Run19/Action15/Memory3不变，Activity仅增加restart restore。真实Calendar full_access，create/get/update/get/delete/get完成且合成事件清理。五尺寸输入/按钮在Dock上方，真发送通过；412×892请求实际受限412×818。

总体PARTIAL：三轮Chat语义复测2/3，Memory来源hash为空、设置/视觉未1:1；本人Mail登录/测试地址/最终发送尚缺，邮件→日历同Goal未LIVE。原版Gate仍拒calendar；扩展签名check通过、scan人工human-review。旧安装版严格验签/SHA不变，未改生产数据。代码正整理为参赛纯源码；用户要求先完善再提交，未push、未评论issue。请从根目录PHASE2_LIVE_TEST_REPORT.md、PHASE2_LIVE_ACCEPTANCE.md、PHASE2_LIVE_EVIDENCE_INDEX.md进入。优先补真实Mail同任务，解决语义及剩余差异；无新Capability/Phase3。

## 以下为历史快照


## Phase 2 最终候选 0.2.2（2026-09-30，`codex/muse-official-migration`）

中文八页与左中右三栏已在隔离 Release OctoSense Shell 实际显示；最终 0.2.2 通过 App Hub 本地演练 catalog 升级/全新安装。三个新 Goal/Run 在真实 Shell 完成批准→本机 `model.complete`→存储→独立读回，Shell 重启后三个结果 SHA 不变；0.2.1 遗留的 timer 超时目标在升级后安全恢复。412×805 长文 Goal 和 990×400 矮窗 Goal 可操作，但后者内容区仅 71 点。邮箱仅在固定 `mail_demo` FIXTURE 跑完宿主连接、同步、正文、来源记忆、编辑草稿、精确预览及单独确认返回 accepted；无对外投递或收件端回执。Calendar 宿主状态真实返回 `write_only`，未触发本人 TCC、未执行系统事件 CRUD。两轮 Chat 消息持久化，但本地模型的追问误答“收到”。因此总体 **PARTIAL**，Goal 受限回归 **PASS**，Mail/Calendar/同任务 LIVE **BLOCKED**。原版 App Hub Gate 不接受 calendar；隔离宿主补丁及 ad hoc `.app` 仅本地候选。旧安装版 SHA 未变且严格验签通过；未改生产数据、未正式签名/发布/push。详细证据见 [`PHASE2_TEST_REPORT.md`](../PHASE2_TEST_REPORT.md)、[`PHASE2_PARITY_AND_FUNCTION_MATRIX.md`](../PHASE2_PARITY_AND_FUNCTION_MATRIX.md)、[`PHASE2_RUNBOOK.md`](../PHASE2_RUNBOOK.md)。

## 官方 Muse UI 迁移更新（2026-09-30，`codex/muse-official-migration`）

在独立版 0.3.1 与官方 OctoSense Shell 中实际打开并截图后，官方 Muse 0.1.10 已有中文六项导航、Chat/Goals/Goal Detail/Memory/Activity/Capabilities/Settings、真实 `model.complete` 对话、受限 Goal 计划审批卡、结果/错误卡和隔离存储。Shell 本地 App Hub 安装版的新 Goal `1790703104-3867664407` 完成 Goal → Plan → 用户批准 → model.complete → Storage → Readback → Shell Restart Restore；结果 SHA-256 `eeebf075285344fe9d8a6a70ff34d8d4a9a2ba32ac66b94981bb65602a51f7e2`，重启前后相同，当前 Goal 的写入/回读各一次。0.1.9 曾在同步批准时超出脚本时间预算，0.1.10 改为已持久化批准后下一 tick 执行，新 Goal 无需重试通过。可见 card-host 0.1.10 烟测通过，0.1.8 布局矩阵覆盖 412 宽、990×400 矮窗口、1280×800 宽窗口及 455 字/8 条资料；`hub check` PASS。证据与未完成项见 [`MUSE_UI_PARITY_REPORT.md`](../MUSE_UI_PARITY_REPORT.md) 和 [`docs/MUSE_UI_PARITY_MATRIX.md`](../docs/MUSE_UI_PARITY_MATRIX.md)。**总状态仍为 PARTIAL**：真实 AI 对话可调用并持久化，但本地小模型连续追问误答；独立版三栏、原有 Memory、可浏览多 Goal 历史、Activity 观察功能、可编辑模型/预算和全卡片逐态尚未 1:1；Mail、Calendar、Browser、TextEdit、插件按本轮用户澄清暂不覆盖。安装的独立版 SHA/严格验签未变化；本地测试镜像不等于正式发布，未 push。

## 官方容器迁移分支补充（2026-09-29 19:35 Asia/Shanghai）

本节仅适用于独立 worktree `/Users/mima0000/.codex/worktrees/muse-official-migration/Agent APP黑客松` 的 `codex/muse-official-migration` 分支，基线 `5e7fa0b`。下方旧版现状是接手时的历史快照；主工作区、已安装原生 .app、生产 SQLite 和密钥没有被迁移试验改写。

当前 Shell 锁定的官方源组合、首个 Muse 脚本 bundle、实测表与失败证据见 [`docs/OFFICIAL_RUNTIME_AUDIT.md`](../docs/OFFICIAL_RUNTIME_AUDIT.md)、[`docs/OFFICIAL_MIGRATION_MATRIX.md`](../docs/OFFICIAL_MIGRATION_MATRIX.md)、[`evidence/official-migration/README.md`](../evidence/official-migration/README.md)。首条资料整理目标已在 `card-host` 的真实脚本运行时完成输入、计划、批准、应用隔离文件写入、回读和重启恢复；模型按钮在无服务的 `card-host` 诚实报错。**OctoSense Shell 已构建并启动 App Hub，但大型 Splash 和 Shell 在本机 Intel Iris Pro 上分别呈灰屏和黑屏；同版本简易 Counter 与重新运行的 Muse `card-host` 正常绘制。Muse 尚未安装进 Shell，不可宣称容器集成通过。** `tools/octo check` 已通过，`hub scan` 生成七项人工审查问题；publisher 占位和签名仍是人工节点。付费模型未调用。

后续受限 `muse.goal/0.1` GoalSpec 在隔离 `card-host` 中通过真实 UI 批准、执行、读回；篡改计划路径在批准前被拒绝（`approved_at=0`，无结果）。当前 Shell 空桌面、News 和 Android 测试入口也黑屏，同机旧 Shell `a74a255` 则能显示桌面；当前 Shell 的具体渲染回归仍未定位。独立测试宿主通过不能升级为 OctoSense 容器通过。

Date: 2026-09-29 13:52 Asia/Shanghai（快照；每次接手先重新核对）

Branch: `main`

HEAD: `c068fb6adddbc8aed7ef9ddc92977724f91e7634`（文件夹整理前的核对点；功能代码调查基线为 `dbd08ed`，后续实际 HEAD 以 `git rev-parse HEAD` 为准）

Version: macOS `CFBundleShortVersionString=0.3.1`；分发目录标签 `r17-mail-contacts-reply`，不是语义版本号
Workspace: `/Users/mima0000/Documents/ChatGPT/Agent APP黑客松`

2026-09-29 磁盘清理补注：本节以上为 13:52 快照；随后安装版主程序已与 `r18-calendar-live` 一致，安装版和 r18 原包均通过 `codesign --verify --deep --strict`。旧分发版（初版、r2–r16）和旧集成候选（初版、02–18）的 `.app/.zip/.dmg` 已清理，仅保留目录中的说明及校验值；r17 回退包、r18 当前包、candidate-19、独立验收证据与用户数据保留。历史证据中指向已清理旧包的路径不再可直接复跑。详情见 [磁盘清理交接](HANDOFF_DISK_CLEANUP_20260929.md)。

交接包首次提交前的工作树已有未提交内容：`app/muse_textedit_recipe.py` 被修改，另有 108 项未跟踪旧包/证据/资料；后续接手不得盲目清理或纳入这些内容。历史 `HANDOFF.md`、`STATUS.md` 和 9 月 28 日验收表保留，但它们的旧包路径与进程状态不是当前事实。

本交接文件夹已改为自主接手：没有更新的具体用户任务时，新模型可从下方优先级自行选择非核心问题直接开工。`TASK.md` 状态为 `OPEN`，不要求用户先指定目标或可修改文件；核心保护清单见 `AGENTS.md`。

## PASS

| 项目 | 范围与证据 |
| --- | --- |
| macOS 原生 Muse | `0.3.1` 当前已安装并运行；2026-09-29 文档验收产生的 Python 缓存已按与 r17 原包逐文件比对清除，安装副本和发布原包均重新通过 `codesign --verify --deep --strict`。PASS 仅指本机运行和签名，不等于陌生用户可安装。 |
| Qwen / 本地模型 | `Qwen3-0.6B-Q8_0` 的本机 llama 服务正在 `127.0.0.1:8080` 运行，`/health` 返回 `ok`；r14 模型意外退出后自动恢复与原生问答见 `evidence/muse-g00-r14-model-recovery.md`。 |
| Goal DSL、Memory DSL、Capability DSL | `app/muse_dsl.py` 与三类 schema/存储实际存在，单元测试和此前包内校验覆盖结构、摘要、范围及错误输入；这只代表本地 DSL。 |
| Goal Engine | 第十七版历史签名包完成同一真实本地 Qwen Goal 的批准→v1→约 60 秒 `NO_CHANGE`→合成目录事件 v2→回读、暂停/重启/恢复/取消，见 `evidence/muse-g00-candidate17-integrated-20260928/README.md`。PASS 限于此本机受限场景。 |
| Background Runtime | 本次快照有原生应用、其 worker、本地模型和 QQ 桥四个进程；worker 负责定时/事件推进。进程存活不是长期目标长期正确性的证明。 |
| Files | 受限工作区写入/回读、摘要批准和重复动作阻断有第十七版包内证据；不含全盘读写。 |
| Calendar（本机真实闭环） | 2026-09-29 从**已安装 r18 成品**完成：用户在系统弹窗授予**完全访问**（`org.gosim.local-agent` auth_value=2）；成品内 `calendar_selftest.py` 读取未来窗口 → 创建 `[Muse Test] MUSE-CALENDAR-TEST-…` → 回读 → 修改 → 回读 → 应用内确认后删除 → 回读确认不存在；创建/修改均 `readback_matches=true`，删除 `readback_absent=true`，事件已清理。见 `evidence/muse-calendar-live-verification-20260929.md`。PASS 仅限本机、可写日历、唯一标记的测试事件；未做多日历/拒绝/重放等反例。2026-09-29 追加：**Agent 现在自己处理日历**——对话里说「加个日程：明天下午3点开会」会给出待确认卡，确认后写入默认日历并读回；回复邮件后若正文含时间，会附「是否加入日历」待确认卡。见 `evidence/muse-calendar-agent-20260929.md`。2026-09-29 再追加（r21-calendar-human，**人性化**）：意图解析支持中文数字与口语（`八点半`/`明天下午三点`/`今晚八点一刻`），并新增宽松的来信提议 `propose_from_mail`；邮件回复发出后，Muse 会用口语主动问「要把「今晚8点 吃饭」加进日历吗？」，用户可直接回「好/同意」写入、「算了」不写；用户对来信说「同意」时，起草的回复本身也会表达同意并复述时间（`好的，今晚8点没问题，我到时见。`）。顺带修正两处真实 bug：「下周X」原先多算一周、「八点一起…」曾把「一」当分钟。见 `evidence/muse-calendar-human-flow-20260929.md`。同日晚追加（r22-calendar-revision）：**改口可用**——「8点去咖啡厅不」→ 卡片 20:00，再说「8点去不了，改成9点」→ 卡片自动换成 21:00（标题仍为「咖啡厅」），说「好」才写入 21:00；「8点去不了了」则视为不去了、不写。同时修掉疑问尾字混进标题（原「咖啡厅不」）。 |

## PARTIAL

| 项目 | 已有部分与缺口 |
| --- | --- |
| 高阶 GPT、DeepSeek Provider、Provider Switch | OpenAI Responses、DeepSeek Chat、模型/预算/Primary-Backup/预览有代码和 fixture；没有本轮可核验的真实远端推理、账单和同任务工具动作。Backup 还有同源/协议限制。 |
| Memory、Knowledge Graph | SQLite 记忆、来源、claim、关系、更正/遗忘、范围与检索有代码和隔离测试；整台电脑历史自动抽取与事实质量未验。 |
| Mail | 本轮真实 QQ IMAP 状态 `CONNECTED`、最近收件箱邮件头提取 27 位联系人；原生联系人窗口与合成点击测试通过。用户已反馈新版操作正常，旧结果卡→真实 SMTP 回复曾由用户确认。r17 新的“无来信卡选人回复”没有由本轮自动化向真实联系人发信，故完整外发回执仍缺独立证据。见 `evidence/muse-r17-mail-contacts-reply.md`。 |
| Browser Research、Browser real action | 第十七版历史签名包在 Edge 上真实点击/读回三页公开网页并生成本地 Qwen 报告；当前 r17 邮箱版未重跑这条 GUI 链，报告事实并非全量复核。 |
| Terminal | 旧的 `mkdir`/`touch` 等受限确认能力有本机证据；不含任意 shell，当前 r17 未单独重测。 |
| App Learning、TextEdit real action | 有 `RecipeStore`、AX 观察/配方、TextEdit 签名候选实写读回证据；当前 r17 未独立复跑，不能称通用软件学习。 |
| Plugin system | 审查过的内置插件、声明式 SDK、批准/撤销、篡改阻断有本地和旧包证据；任意第三方代码安装与通用插件生态未通过。 |
| DMG、first-run onboarding | r17 DMG 隔离安装启动/退出与原始包验签通过；首启部分选项有历史测试。ad hoc、未公证、仅 Intel；第二台 Mac/Apple Silicon/全新用户权限未验。 |
| Keychain | 成品在用户允许后恢复 QQ 邮箱授权码并维持连接；GPT/DeepSeek 密钥从成品读取并真实调用未验。本交接没有读取或记录密钥。 |
| OctoSense | 官方 Octos/AppCard 曾形成真实会话与审批请求，宿主与局部 MCP 实验有证据；尚无同一 Muse Goal 的可信人工确认→动作→回读→官方结果。见 `evidence/muse-g01-h5-evening-entry-20260928.md`。 |

## BLOCKED

| 项目 | 当前证据与解除条件 |
| --- | --- |
| robrix2 | 旧官方 checkout 有静态接口，原生构建曾在 Swift `Foundation` 桥失败；Matrix 登录、owner/project room、设备登记和 backend session 无 live 证据。不能把源码 parser 算真实宿主。 |
| official full-chain | OctoSense/robrix2 与同一 Muse Goal 的官方会话、真人确认、唯一受限动作、独立回读和官方结果没有闭合；此前官方原生 shell 负例出现未审批执行，产品侧必须继续禁用该副作用路径。 |

## NOT TESTED

| 项目 | 边界 |
| --- | --- |
| mobile / OnePlus 6 | 尚无移动端安装、设备桥或真实手机动作验收。 |
| 真实付费 GPT / DeepSeek 结果 | 协议 fixture 不能替代远端内容、用量与费用回执；本次未发付费请求。 |
| 朋友另一台 Mac 的分发 | 新用户 TCC、Apple Silicon、Gatekeeper/公证、模型首次下载未在第二台机器上测。 |

## Active Processes

13:20 快照：原生 Muse PID `82355`、独占 worker `82395`、本地 llama/Qwen `82558`、应用持有的 QQ IMAP 桥 `89304`。QQ 健康文件状态 `CONNECTED`，联系人快照 27 位；这些 PID 会变化，接手须重新查询。未观察到 OctoSense/robrix2 进程。

## Latest Tests

- 2026-09-29 日历改口/标题修复（r22-calendar-revision）：新增 `parse_calendar_change()`（取**最后一个**时间）与 `looks_like_change()`；`_chat_message` 在有待确认卡时先试改口、再试同意/拒绝，显式新指令仍整卡替换；`_TAIL_WORDS` 增加 `不/没`，`is_refusal` 增加 `不了/改天`。日历相关单测 **51/51**；全量 **313 项仅 G01 环境性失败**。证据 `evidence/muse-calendar-human-flow-20260929.md`。
- 2026-09-29 日历人性化闭环（r21-calendar-human）：来信「我们今晚八点一起吃饭？」→ 用户说「同意」→ 草稿 `好的，今晚8点没问题，我到时见。` → 回复发出后提议「要把「今晚8点 吃饭」加入日历吗？」→ 用户回「好」→ 写入 20:00 且 `READBACK_MATCH`。用**安装包内代码**跑通（假日历后端，未写真实日历）。日历相关单测 **41/41**；全量 **303 项仅 G01 环境性失败**；`bundle_integrity=PASS`。证据 `evidence/muse-calendar-human-flow-20260929.md`、`evidence/muse-unit-tests-r21-20260929.txt`。**尚未经用户在成品里手点一遍。**
- 2026-09-29 Agent 日历能力（r19-calendar-agent）：新增确定性意图解析 `muse_calendar_intent.py` 与 `UserCalendarService`（真实用户事件，`approved=True` 才写 + 读回）；`desktop_app.m` 复用通用任务卡确认流；回复邮件后按正文时间给出待确认卡。日历相关单测 23/23；全量 **285 项仅 G01 环境性失败**。证据 `evidence/muse-calendar-agent-20260929.md`。**尚未经用户在成品里实点验证**。
- 2026-09-29 Calendar **真实闭环（已通过）**：从已安装 r18 成品、用户系统弹窗授予完全访问后，`calendar_selftest.py` 完成 读未来窗口 → 创建 `[Muse Test] MUSE-CALENDAR-TEST-…` → 回读 → 修改 → 回读 → 应用内确认删除 → 回读确认不存在；全部 `readback_matches=true` / `readback_absent=true`。证据 `evidence/muse-calendar-live-verification-20260929.md`。定向单测 `test_muse_calendar.py` 6/6、`test_calendar_selftest.py` 4/4；全量 **272 项仅 G01 环境性失败**；`bundle_integrity=PASS`。
- 2026-09-29 安全测试运行器（新增 `scripts/run_muse_unit_tests.sh`）：用**安装包自带 Python** 跑全量 267 项，`bundle_integrity=PASS`（包零改动、严格验签通过）。该脚本导出 `PYTHONDONTWRITEBYTECODE=1` + `PYTHONPYCACHEPREFIX` 给整棵进程树，并在运行前后对目标包做验签+文件清单门禁。证据：`evidence/muse-pyc-signature-gate-20260929.md`、`evidence/muse-unit-tests-safe-20260929.txt`。唯一失败项见下条说明。
- 2026-09-29 `test_g01_capabilities.test_owned_worker_start_health_stop_and_readback`：在工作沙箱内持续失败，原因是该用例用 `ps -p <pid> -o command=` 做进程身份校验而沙箱禁用 `ps`（`_process_command` 返回空 → `owned=False`）。已在未改动 HEAD 上复现同一失败，属环境限制，非代码回归。
- 2026-09-29 本次源码：`PYTHONPATH=app /Applications/GOSIM-Local-Agent.app/Contents/Resources/python/bin/python3 -B -m unittest discover -s app -p 'test_*.py' -q`，**267 tests / OK / 32.123 秒**。此命令或它启动的子进程随后在**安装副本**写出 88 个 `.pyc`。逐文件确认原有 746 个文件与发布包哈希一致后，只移除这些新缓存；安装副本与发布包最终均严格验签通过。此命令不能作为今后的成品验签测试模板。
- 2026-09-29 r17 定向：`test_agent_app test_qqmail_imap_bridge test_desktop_worker`，47/47；`scripts/test_muse_mail_contacts_ui.py` 的隔离包合成联系人原生点击 `PASS_FIXTURE`；`scripts/test_g04_install.sh` 在 r17 DMG 的隔离安装 `PASS_LOCAL`，见 `evidence/muse-r17-mail-contacts-install-smoke.txt`。
- 2026-09-29 交接包自检：仅用五个入口文件回答十个接手问题，10/10 可定位；七个文档的本地链接无断链，未发现邮箱地址或常见 API/GitHub 密钥形状。此检查是文档可读性测试，不是产品能力测试。
- 后续跑单元测试请改用 `scripts/run_muse_unit_tests.sh`（已按上面三条经验固化）：它默认用安装包 Python 但全程导出字节码守卫并做前后验签门禁；需要更保守时设 `MUSE_TEST_APP_COPY=1` 在临时副本上跑，或设 `MUSE_TEST_PYTHON=<独立 3.12>`。不要再用裸 `python3 -B` 直接指向签名包。

## Deliverables

- 最新 r22（改口/标题修复）包：`dist/Muse-5A-2026-09-29-r22-calendar-revision/`（ZIP SHA-256 `0922fe9448ff9f477b26f960df5e36d6ff383b8150fa58892fd88389d319027a`）。
- 最新 r21（日历人性化）包：`dist/Muse-5A-2026-09-29-r21-calendar-human/`（ZIP SHA-256 `2157a83f89df5878e0327fe9bd0463aa5b8de8d7431cfee7ed3368912086a815`）。
- 最新 r19（Agent 日历）包：`dist/Muse-5A-2026-09-29-r19-calendar-agent/`（ZIP SHA-256 `d97ff7f76ba0a238613afcc54fc01faa7475b3b156ea8f3e47621fd09f8063ba`）。
- 正在运行的安装副本：`/Applications/GOSIM-Local-Agent.app`（**r22-calendar-revision**，r21/r20/r19/r18/r17 备份在 `runtime/backups/`）。（历史：**r21-calendar-human**，r20/r19/r18/r17 备份在 `runtime/backups/`），含日历入口与人性化日历流；已严格验签。（历史行：r19-calendar-agentr17 备份在 `runtime/backups/GOSIM-Local-Agent-r17-20260929.app`）。
- r18 候选包（本机已安装）：`dist/Muse-5A-2026-09-29-r18-calendar-live/`（含 .app/.zip/.dmg）。ZIP SHA-256 `54fcd9ed3c2bc01dd0bda1203f45970a06ca57b0c8dd533f47db01c83b35f4d4`。
- r17 有效签名原包：`dist/Muse-5A-2026-09-29-r17-mail-contacts-reply/GOSIM-Local-Agent.app`。
- ZIP：`dist/Muse-5A-2026-09-29-r17-mail-contacts-reply/GOSIM-Local-Agent-macOS.zip`，SHA-256 `61b01606c1616481966df68a3446038f2e5aeabe1295a80f95927745e1612cf9`。
- DMG：`dist/Muse-5A-2026-09-29-r17-mail-contacts-reply/GOSIM-Local-Agent-macOS.dmg`，SHA-256 `a39c9338e588144dc51555db767e833e9e624a1150d7481ba3c3d3856a32234e`。
- 最新邮件证据：`evidence/muse-r17-mail-contacts-reply.md`；旧五项硬门槛台账：`docs/MUSE_5A_ACCEPTANCE_20260928.md`（历史快照）。
- 安全单元测试运行器：`scripts/run_muse_unit_tests.sh`；字节码/签名门禁定位证据：`evidence/muse-pyc-signature-gate-20260929.md` 与 `evidence/muse-unit-tests-safe-20260929.txt`。
- Calendar 证据：真实闭环 `evidence/muse-calendar-live-verification-20260929.md`；权限归属纠正与入口缺口 `evidence/muse-calendar-permission-and-loop-20260929.md`。

## Known Boundaries

### DO NOT CLAIM

- 本地结果卡 ≠ 官方 AppCard；编译或打开官方窗口 ≠ official full-chain。
- Provider 设置 UI / 协议 fixture ≠ 真实 GPT/DeepSeek 推理或收费验收。
- 固定 TextEdit/Edge 操作 ≠ 任意 App Learning；能读授权目录 ≠ 整台电脑全知。
- mock / fixture ≠ live integration；进程存活 ≠ 长期 Goal 持续正确工作。
- Codex 能操控电脑 ≠ Muse 成品具有同样的权限；QQ 收件箱最近联系人 ≠ QQ 通讯录。
- 发布包的验签结果不能代替 `/Applications` 安装副本的再次验签；本机安装烟测 ≠ 陌生用户可无阻安装。

## Next Priorities

1. （已完成 2026-09-29）测试向签名包写字节码的问题已定位并用 `scripts/run_muse_unit_tests.sh` 固化（导出整树字节码守卫 + 运行前后验签/文件清单门禁）。剩余可选：把该门禁接进发布前脚本或 CI。
2. 从**修复后的最终包**重跑本机 Goal、TextEdit、Edge 和 QQ 手动联系人回复的独立验证。
3. 用户在产品里明确配置与批准后，核对真实 GPT/DeepSeek 输出、用量、费用和模型回退；禁止默认付费探针。
4. （2026-09-29 已完成本机闭环）Calendar 已从 r18 成品通过真实读写回读；剩余：多日历选择、拒绝/撤销/重放/断连等反例，以及 Apple Silicon / 第二台机器的复测。
5. 完成官方宿主同一 Goal 的可信人工确认、受限执行、独立回读和官方结果；再测拒绝、重复、断连与重启。
6. 在第二台 Mac 验签、公证/Gatekeeper、首启模型和新用户 TCC；逐项修复分发阻塞。

## Recent Commits

以下是文档开始前的最近 15 条，不包括稍后的交接包提交：

```text
dbd08ed 2026-09-29 Add QQ mail contact replies without incoming cards
9f8c471 2026-09-29 Record r16 live QQ mail reconnection after keychain approval
fb69ed7 2026-09-29 Ground Muse agent capabilities in live mail status and recover stalled listener
9d54c9c 2026-09-28 Record installed model recovery verification
48501e1 2026-09-28 Restart managed local model after service exit
9941f9e 2026-09-28 Update native layout probe for skill and result tabs
48a53f2 2026-09-28 Keep skill navigation clear at minimum window size
8ad8d7e 2026-09-28 Keep skill and result panes visually separate
38ec46f 2026-09-28 Add skill and result card tabs to native inspector
11e6185 2026-09-28 Restore persistent QQ Mail bridge and expose app modules
8c3b816 2026-09-28 Use role messages for local multi-turn chat
1d2730c 2026-09-28 Exclude legacy failure replies from local chat context
e8b91cf 2026-09-28 Record native model recovery evidence
adca6ee 2026-09-28 Bound local chat to Qwen context and use configured model gateway
fa8e980 2026-09-28 Reshape native home and review card hierarchy
```

三小时测试设施更新：可显式选择匹配 card-host、隔离拷贝移除失效产品签名、纯聊天输入合同可选且保持既有付费 Guard；新建 profile 的 UI 零调用检查允许账本不存在。新 Shell 已完成构建与严格验签，隔离 8421 四种尺寸 UI 子集通过，真实模型回归进行中。产品全量仍 PARTIAL。
