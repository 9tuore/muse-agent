# rc10 独立内部 A 证据审阅

**当前截点：73/100，PARTIAL。** 原二十项仍为5 PASS / 14 PARTIAL / 1 BLOCKED；当前7200秒soak尚未完成，不预加完成分。

评阅归属：Root指定的gpt-6-astra既有真实聊天A3。本轮未独立校验应用运行模型配置。这里是对既有证据的独立审阅，未独立执行产品测试、模型调用、GUI操作、构建或系统动作，也不是官方评分或排名。

证据截点：2026-10-05T01:58:43.491974+00:00（北京时间2026-10-05 09:58:43）。仓库HEAD `642aa35b5c648e026f9c068244ebcbe92a7896d1`，分支 `codex/muse-rc-finalization`。

产品 `6fd5b54beeba7cc9892916c3de7f01106ab8a158` / 0.3.26-rc10；readable `a19622e0977b3f988531a1d7db743bc9ef4cd6973fa75bbcdc5dec07d6823cc5`；payload `7cdfc751ca3438d453ad28918b30ee93bc5b86091faa56a30864caa5ed1e6cd0`。

最终运行Host `938ba58a204de0421b2935c974a22645de14a6b7682f1004bc72c701c3793b3d` / SDK `3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e`；源码SDK `da756dde48232ccc9a3ec642cf206a0872e1731d4f0c0d55b2490de281a810cc` 的Calendar布尔桥修复未进入该Host。诊断Host0fd只读证据单列，不能拼成938整链。

沿用RC9内部A的六维度及全部子项权重；按当前证据逐项判定。Root提供维度，本聊天的内部子项判断不是官方评委量表。不以旧70或目标95为起点加减。报告准备完成，待Root提供完整soak结果后只更新对应新增证据一次。

| 维度 | 得分 |
|---|---:|
| 任务完成 | 17/25 |
| 可靠运行 | 14/20 |
| 人机协作 | 13/15 |
| 项目反哺 | 10/15 |
| ROM/系统突破 | 7/10 |
| 效果证据 | 12/15 |
| **合计** | **73/100** |

子项权重与RC9_INTERNAL_A_REVIEW逐项一致。每行E编号对应下方的真实commit、文件、测试与完整SHA；JSON在每个子项内展开相同凭据。未把用例数量按比例直接转换为比赛分数。

**任务完成：17/25。**

| 子项 | 得分 | 证据 | 扣分及评分边界 |
|---|---:|---|---|
| 普通聊天与候选修改 | 4/5 | E01、E04 | 扣1：候选生成和同卡编辑已有双模型当前证据，但M3 S02未答出要求值、M2.7 R02缺回执原因，且两模型M01新增无依据评价；普通聊天可靠性未满。 |
| 跨聊天记忆更正与遗忘 | 5/6 | E02、E04 | 扣1：当前双保存、更正/遗忘、跨会话项目与归属隔离已证实；真实冲突询问及Mail/Calendar关联全过程未覆盖。 |
| 一次性本地任务 | 6/7 | E03 | 扣1：一个本地Goal/Run经模型、批准、存储/读回和首次Shell重启成立；其他任务与外部业务语义未覆盖。 |
| 同候选外部系统全链 | 0/5 | E16、E17、E12 | 扣5：T18仍BLOCKED。最终profile无同步凭据，新Calendar桥未进Host938，同候选来信→记忆→创建/get→原ID改期/get→回复到达链未过。 |
| 两模型受影响D05 | 2/2 | E04 | 不扣：当前两个模型D05均准确要求起止时间且既有候选不变；仅奖励冻结D05这个窄子项，其他模型失败在普通聊天项处理。 |

**可靠运行：14/20。**

| 子项 | 得分 | 证据 | 扣分及评分边界 |
|---|---:|---|---|
| 当前启动与重开矩阵 | 4/5 | E05、E06 | 扣1：同候选70和100重开全部成立，但固定合成负载、最大可交互18.882秒且有ui-hang信息；不计OS冷缓存/真实后端或不同硬件。 |
| 第一次任务重启持久性 | 4/4 | E03、E02 | 不扣：本地Goal首次Shell重启八SHA相等且无重放；Memory另有十SHA等值。文件数不当作多次重启。 |
| 故障与恢复机制 | 3/4 | E01、E07 | 扣1：已有真实隔离文件系统/合成Host故障与恢复记录，未改变路径有限支持；当前真实服务异常、外部改动和未知投递恢复未完整验证。 |
| 长运行与跨环境 | 1/4 | E06、E13、E10 | 扣3：只给完成100次持续重开的耐受观察1分；当前完整7200秒仍RUNNING，不给长驻完成分；真实后端长测、clean/OS重启/第二Mac/ARM仍缺。 |
| 失败可观察与保护 | 2/3 | E04、E12、E13 | 扣1：失败和no-replay/未知项保留，当前可核对回调与账本；M3 S02 usage/attempts未知、Host收信请求数不可观察，历史真实Mail绘制FAIL未由当前真后端长测关闭。 |

**人机协作：13/15。**

| 子项 | 得分 | 证据 | 扣分及评分边界 |
|---|---:|---|---|
| 明确批准并防重放 | 4/4 | E03 | 不扣：一次明确本地批准、唯一Goal/Run及首次恢复不重放有证据；只奖励该本地批准机制。 |
| 缺时间先追问 | 4/4 | E04 | 不扣：当前两模型E01缺收件人、D05缺时段、D07/H05缺日期时段均正确追问且未添候选；E01 error与waiting_user准确区分，不把应用守卫说成原始模型自行追问。 |
| 范围/过期/重复保护 | 3/4 | E01、E04、E07 | 扣1：当前项目/归属隔离、遗忘、同卡修订和取消已见，历史stale/重复守卫支持；最终真实手写稿与外发连续体验未完成。 |
| 可见可编辑交互 | 2/3 | E02、E05、E06、E11 | 扣1：当前六页、编辑、焦点和Memory输入修复有记录；完整当前尺寸/视觉验收缺失，旧412×892 Dock遮挡失败不被412×700替代。 |

**项目反哺：10/15。**

| 子项 | 得分 | 证据 | 扣分及评分边界 |
|---|---:|---|---|
| 可还原SDK与锁 | 3/4 | E08、E10、E15 | 扣1：固定SDK/overlay/锁及历史12000还原可查，源码导出器有窄fixture；当前新SDK完整clean构建和实际F导出未完成。 |
| 具体框架与桥接修复 | 4/5 | E08、E09、E17 | 扣1：native存储摘要、4KiB准备/取消机制及Calendar布尔序列化最小修复有具体源和测试；新Calendar修复未进运行Host。 |
| 贡献材料与边界 | 3/3 | E09、E10 | 不扣：已有可审阅的缺陷、接口、纯测试、权限/回读限制和最小上游拆分草稿；只奖励材料质量，不奖励尚未提交的贡献。 |
| 上游合并与准入 | 0/3 | E10、E12 | 扣3：贡献仍DRAFT/NOT_SUBMITTED，本地扩展没有上游合并、官方原版准入或正式reviewer通过的证据。 |

**ROM/系统突破：7/10。**

| 子项 | 得分 | 证据 | 扣分及评分边界 |
|---|---:|---|---|
| 官方运行路径与模型 | 4/4 | E03、E04、E05 | 不扣：同rc10官方Splash/OctoSense真实Host路径、model.complete和本地存储确实运行；M2.7 classunknown仍保留。 |
| OS服务机制 | 2/4 | E09、E16、E17 | 扣2：已有历史EventKit读和稳定版Mail节点与宿主机制；当前Mail同步缺凭据、当前UI旧Host只读schema拒绝，新桥及最终系统写入/get链缺失。 |
| 隔离存储与能力边界 | 1/2 | E03、E08、E12 | 扣1：隔离本地存储与受限能力可核对；LOCAL_EXTENDED_HUB不是stock准入，跨机器权限和完整外部能力没有完成证据。 |

**效果证据：12/15。**

| 子项 | 得分 | 证据 | 扣分及评分边界 |
|---|---:|---|---|
| 身份与原件哈希绑定 | 3/3 | E01、E02、E03、E04、E05、E06、E12 | 不扣：当前源、六文件bundle、四条模型原报告、启动/重开/首恢复和55行索引SHA可核对；身份未拼接。 |
| 实际原生画面 | 2/3 | E11 | 扣1：当前四张合成原生截图有Root查看与SHA provenance；rc9约61秒UI采样片是历史，当前外部业务全过程视频仍缺。本轮不声称独立视觉重测。 |
| 输出独立核对与反例 | 3/3 | E02、E03、E04、E05、E06 | 不扣：输出/候选字段、记忆存储、独立Readback、SHA和原反例可追踪；证据复核不等于重新跑测试，也不把多个副本累加为覆盖。 |
| 完整复现与材料同步 | 2/4 | E10、E12、E14、E15 | 扣2：当前55行索引完整匹配、源身份与工具边界明确；实际F/桌面导出、完整clean/第二Mac/ARM/OS重启未做，三处当前入口文字滞后。资源合并约210MB观测不作为复现成功。 |
| 真实披露覆盖边界 | 2/2 | E04、E12、E13、E16、E17 | 不扣：fixture/真实节点/官方全链、旧新版本、诊断Host0fd/最终Host938、未知usage和未完成soak均明确披露。 |

**本轮核对得到的事实。**

- 当前源与六文件bundle哈希匹配；与rc9相比，去除memory_correct并仅归一化版本文字后，其余完整文本相同。官方91244 token等价引用既有Root结果，未重新运行tokenizer。
- RC_EVIDENCE_INDEX的55行文件大小与SHA全部匹配。原20项状态独立计数为5/14/1。
- 70次启动和100次重开的每行pass、六页、输入、焦点、固定非空记录数量、受保护存储及ledger均核对通过。100次发生在同一Shell进程，不是100次冷启动。最大首次可交互18.882秒。
- Memory双保存的完整文档相同，输入框与已保存NOVA值一致，重复保存无新写入；首次Shell重启10SHA相等。Goal一次批准、两项结果、首恢复8SHA相等、唯一Goal/Run、不重放。
- 两模型各28唯一输入，冻结原20各19PASS/1FAIL、setup2和holdout6全PASS；这套原20题不同于T01–T20产品验收矩阵。M3 S02 invalid_output及未知usage/attempts、M27 R02缺少缺回执原因、两模型M01无依据评价均保留。
- E04同候选修改正文保留to/subject；日历候选字段和waiting_user前后候选未新增已在先前同聊天独立语义复核中核对。E01应用error提示补收件人是语义PASS，不等于Host失败。
- 四张当前合成原生截图SHA匹配；Root已看图的记录存在。本轮没有重新进行视觉验收，也没有当前外部业务全过程视频。

soak状态快照：`official_muse/app/build/ui-memory-20261003/rc10-final-soak-evidence-r1/report.json`，SHA `7ff2a607fcd020915be0f1f75639d38f44e189e1755530a2fd1a12d795e9b351`；RUNNING，截点看到173个样本，要求7200秒。原文件会继续原子更新，此SHA只是截点快照。Host请求数为NOT_OBSERVABLE，不写成零。旧rc9完整7200秒不能替代当前完成结果。

长运行与跨环境子项的1/4仅来自已完成的100次连续普通重开耐受观察；当前长驻完成、真实后端长测及跨环境复现均未获完成分。

资源合并记录是32个同字节分发文件，两批观测可用空间差额合计210,481,152字节（约210.5MB / 200.7MiB）。差额包含并发系统分配，不能由320,205,669逻辑字节推出物理回收量。没有因此获得新Host构建或运行复现分。导出器为10+4微型fixture/当前脚本窄复核，1725字节测试源；实际F及桌面导出仍未执行。

**需要Root同步的三处文档。**

- P3 · `CHAMPIONSHIP_SCORECARD.md:1`：页面rc9标题和RC9审阅引用是历史身份，但正文仍称当前内部A/B且写原28步骤两模型尚待；作为rc10晨间报告的评分入口容易误读。 Root把旧70/70段明确标为rc9历史截点；rc10审阅另列，保留原结果，不把完整观察写为尚待。
- P3 · `MUSE_HANDOFF/CURRENT_STATE.md:5`：最新接手段仍把额外100普通重开与7200秒都写为运行中；当前RC10_REOPEN_100_SUMMARY及原报告已100/100 PASS。 Root只同步最新入口的100完成状态；7200秒仍按本截点RUNNING。
- P3 · `SOURCE_DELIVERY.md:9`：写当前三张rc10截图；RC10_NATIVE_PROVENANCE已列四张且四个文件SHA匹配。 Root同步为四张，保留合成资料及非外部业务视频的限制。

这些发现仅记录在本审阅，不修改Root主报告。评分页旧70/70作为历史结果保留；最新晨间报告已正确标成历史截点。

**逐文件证据凭据。**

以下commit为该主证据文件在当前HEAD中的最近修改commit；不自动当作产品commit。support_files的哈希/跟踪状态及未跟踪原始报告范围见配套JSON。

**E01** · `RC10_DELTA_BINDING.json`
- 证据commit：`6e3204f2d53fba0103f3baa8a75c35d0debaeae4`；SHA256：`c6e557053d8760aa86e316eedb107eb7d0c9f4781770fbdebcb9727396fa536b`；1781 bytes。
- 测试/核对：当前源/六文件哈希；相对rc9仅memory_correct和版本文本变化；官方91244 token等价为既有Root结果，本轮不重跑tokenizer。
- 范围：当前产品身份及限定函数复用，不把regex边界当AST证明。
- 关联文件：`official_muse/app/source/main.splash`、`official_muse/app/bundle/main.splash`、`RC_CODE_FREEZE.json`。

**E02** · `official_muse/rc/startup/RC10_MEMORY_CORRECTION_UI_SUMMARY.json`
- 证据commit：`f8b1d612de0ee97defd35309b35059e615292dfb`；SHA256：`d35e54837f14181b9799d50a3eaecb3c7ecc359320cfd65c8e3c9f0bc05e4ee4`；1156 bytes。
- 测试/核对：两个真实单保存相同文档/输入；重复保存无写入；首次Shell重启10SHA与ledger相同。
- 范围：当前rc10合成Memory UI；本轮检查报告，不点击UI。
- 关联文件：`official_muse/app/build/ui-memory-20261003/rc10-memory-ui-r1/memory-correction-ui-evidence-r2/report.json`。

**E03** · `RC10_LIVE_NODE_SUMMARY.json`
- 证据commit：`10a1b12491569782cfda5d11e4829b0f2e9f4dcd`；SHA256：`c6fc7e68c94b0cc02b65d1dcc864d05ef6416c8e07c40ed3faacbf0cf3816eca`；1807 bytes。
- 测试/核对：两次模型调用、一次批准、两个结果；首Shell重启八SHA相等、唯一Goal/Run、不重放。
- 范围：本地任务，非外部业务链或OS重启。
- 关联文件：`official_muse/app/build/ui-memory-20261003/rc10-final-goal-r1/goal-restart-evidence/report.json`。

**E04** · `official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`
- 证据commit：`10a1b12491569782cfda5d11e4829b0f2e9f4dcd`；SHA256：`1a75b836a6b79b6bc597e0eb8fdc3e59705370267e9f2f85316ef3831c82fbe1`；93833 bytes。
- 测试/核对：同一真实聊天先前逐项复核，两模型各28；原20各19PASS1FAIL，setup2/holdout6PASS；M01额外grounding保留。
- 范围：24模型步+4本地步每模型；S02未知usage、M27 classunknown、R02严格缺项均不抹除。
- 关联文件：`official_muse/prelim/tests/semantic_expectations.json`。

**E05** · `official_muse/rc/startup/RC10_STARTUP_70_SUMMARY.json`
- 证据commit：`10a1b12491569782cfda5d11e4829b0f2e9f4dcd`；SHA256：`bd911844ce37920703ef6118d787a248c6b674698fea90e700919ac01a1ef579`；1747 bytes。
- 测试/核对：逐行核对30冷/20重开/20Shell重启PASS；六页、输入、焦点、16聊天256消息64claims65sources、SHA/ledger保持。
- 范围：无OS缓存清理/电脑重启/真实Mail后端；最大可交互18.882秒。
- 关联文件：`official_muse/rc/startup/evidence/rc10-6fd-final-70-r1/report.json`。

**E06** · `official_muse/rc/startup/RC10_REOPEN_100_SUMMARY.json`
- 证据commit：`9780c16f4e27ae55a30908885a9596ba419077ca`；SHA256：`3594c7496adff38b8f221485f5f2f5c0526c2e91b4bf625101bdc2279f77d42e`；1295 bytes。
- 测试/核对：同一Shell PID的100普通重开逐行检查PASS；原capture404保留。
- 范围：不是100次冷启动；仅重复重开耐受证据。
- 关联文件：`official_muse/rc/startup/evidence/rc10-6fd-light-reopen-100-r1/report.json`。

**E07** · `official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json`
- 证据commit：`91d21a3fd94f67953d048e1901fd0403b888db65`；SHA256：`8b2657b1e490e53c0a07b70ae7f9948ec82e9bbf11899342bc88339fd407db05`；12254 bytes。
- 测试/核对：历史core28+4、proposal25+6、fault20+3；限定Goal9/58和metadata5/91等按原源身份记录。
- 范围：fixture/synthetic Host及本地存储；以不变路径有限复用，不是rc10全部故障实测。

**E08** · `official_muse/rc/packaging/CHUNK_DELTA_BUILD_RESULTS.json`
- 证据commit：`51359d702603e9cc5c98e6f46f2aa6ed631ded26`；SHA256：`566d9642b158d46dc77130b8f048533785750ef984bd619b5042c873aaebb00c`；13963 bytes。
- 测试/核对：历史native摘要/4KiB准备与取消测试、增量Host/Card构建及签名。
- 范围：增量SDK机制；非当前clean或新Calendar Host。
- 关联文件：`official_muse/rc/overnight/NATIVE_STORAGE_CHANGE.md`、`PREPARATION_CHUNK_CHANGE.md`。

**E09** · `RC_CALENDAR_READONLY_REPORT.md`
- 证据commit：`637cbe519686d6d28f30b31292b0e8a7f10102c7`；SHA256：`3cca5dfde37bc0f0edc9fa23d19a9c86f9911df3e7ed23c667462d4b2d805f1e`；4293 bytes。
- 测试/核对：旧Host实读数字truncated问题；源码92b1布尔修复、Foundation三个边界与桥object编译的既有结果。
- 范围：源码修复未进运行Host938；不计当前创建/改期/get成功。
- 关联文件：`official_muse/rc/startup/calendar_boolean_serialization.m`、`sdk-overlays/octosense/apps/calendar/host-service/src/eventkit.m`。

**E10** · `official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json`
- 证据commit：`51359d702603e9cc5c98e6f46f2aa6ed631ded26`；SHA256：`1c4f75db8cc99d72962e7665562961282b949d68f71281012d94356b3f56f36c`；6696 bytes。
- 测试/核对：历史五SDK固定还原/12000验证与三项纯Calendar测试；clean最终中止、无新可执行物。贡献草稿可审阅。
- 范围：DRAFT/NOT_SUBMITTED；非官方准入/上游合并/当前复现。
- 关联文件：`official_muse/rc/packaging/CALENDAR_PURE_TEST_RESULTS.json`、`official_muse/rc/packaging/UPSTREAM_CALENDAR_CONTRIBUTION.md`。

**E11** · `official_muse/rc/screenshots/RC10_NATIVE_PROVENANCE.json`
- 证据commit：`9780c16f4e27ae55a30908885a9596ba419077ca`；SHA256：`b18d34d5c6397423bb5ea6142c9af7e24e2ce37b1c817bd5da42060813cdd979`；1309 bytes。
- 测试/核对：四张当前合成原生PNG逐文件SHA匹配，Root已看图的provenance。
- 范围：本轮不声称新视觉验收；无当前外部链视频。

**E12** · `RC_EVIDENCE_INDEX.json`
- 证据commit：`642aa35b5c648e026f9c068244ebcbe92a7896d1`；SHA256：`eec7c106d8a9955781f7091a2cfeb2c60cf99abe15859a165f30fa1cbf1bb1f6`；23398 bytes。
- 测试/核对：55行bytes/SHA均匹配；原20项5/14/1独立计数；主报告身份分开。
- 范围：三处入口文字滞后单列，不修改主报告。
- 关联文件：`RC_ACCEPTANCE_MATRIX.md`、`RC_CODE_FREEZE.json`、`MORNING_CHAMPIONSHIP_REPORT.md`、`CHAMPIONSHIP_SCORECARD.md`、`MUSE_HANDOFF/CURRENT_STATE.md`、`SOURCE_DELIVERY.md`、`OVERNIGHT_SOAK.md`。

**E13** · `OVERNIGHT_SOAK.md`
- 证据commit：`3237019b82bceb8e47a1c4dcf74640d4650dfa06`；SHA256：`62ba2c1aaabfc91ccd8a9757983b7d4a5032d4b0a50bcb08a72f6e78dc6754a8`；2950 bytes。
- 测试/核对：rc10新7200秒仍RUNNING；原始原子报告只作本轮状态快照。
- 范围：不预加完成分；rc9旧7200PASS与稳定真Mail5357秒FAIL均保留版本。

**E14** · `official_muse/rc/packaging/RC10_DISTRIBUTION_COALESCING_SUMMARY.json`
- 证据commit：`932d4f6bfc1a3e2cafb9d8c26a4129b7f7a32ae0`；SHA256：`789809c0a53e64d1499d0c096ed2647d80a8e24860bf73e85f45cd2dc96b8db8`；2178 bytes。
- 测试/核对：两批15+17=32份相同分发文件；分别观测空间差额合计210481152字节。
- 范围：观测包含并发系统分配，非按逻辑320205669字节推算物理回收；没有新Host构建。

**E15** · `official_muse/rc/packaging/RC10_SOURCE_FOLDER_TOOL_SUMMARY.json`
- 证据commit：`932d4f6bfc1a3e2cafb9d8c26a4129b7f7a32ae0`；SHA256：`e258ce7ce9dc92f12b267629dd0943850fc9bc773bbc35adc8f0553fc06407b2`；1107 bytes。
- 测试/核对：源码导出器AST/help及10+4微型合成fixture结果存在且哈希匹配。
- 范围：1725字节fixture；实际F/桌面导出NOT_YET_PERFORMED，不能计复现成功。

**E16** · `official_muse/rc/startup/RC10_MAIL_PROFILE_LOGIN_SUMMARY.json`
- 证据commit：`10a1b12491569782cfda5d11e4829b0f2e9f4dcd`；SHA256：`0b21bb3f7a94bdaa1f57b87df832c0ff70cb3a2f7eb4b9e8ac8999082cba9ef3`；1822 bytes。
- 测试/核对：当前rc10在次级已授权Host0fd诊断缓存可读、同步缺凭据、零发送。
- 范围：依据公开脱敏摘要与vault源SHA；未读取私有原件或Secret；非最终Host938实发。
- 关联文件：`sdk-overlays/octosense/apps/mail/host-service/src/vault.rs`。

**E17** · `official_muse/rc/startup/RC10_CALENDAR_READONLY_UI_SUMMARY.json`
- 证据commit：`10a1b12491569782cfda5d11e4829b0f2e9f4dcd`；SHA256：`365d5d07ef3b145c90f8e250f151d6a56f5be83571290d0ec29ee7e085aea4f3`；1143 bytes。
- 测试/核对：当前UI在次级Host0fd真实只读仍严格schema拒绝，零mutation。
- 范围：不是Host938集成修复/权限/写入通过。

**计数与范围不重复累加。**

- 两个模型各28=原20+setup2+holdout6；其中24模型步+4本地步。local_cancel/local_setup不冒充模型题。
- 每个模型的前缀8/13和未见后缀20/15各合成一次28；原驱动故障和M3 S02失败保留，未重放输入。
- 48个冻结模型步骤是两个通道的同一28题集，不是48个独立业务场景；成功Host回调不等于语义通过。
- 一次Goal有2模型调用、1批准、2本地结果、1首次Shell重启；八个相等SHA不是八次重启。
- Memory双保存首次Shell恢复10文件是独立窄UI回归；不和Goal八文件混成18次重启。
- 70由30+20+20组成；另100是同Shell PID内普通重开，启动功能与长运行子项只分别奖励启动正确性及重复操作耐受，不扩大运行环境。
- 正在运行的rc10新soak不给完成分，旧rc9/V15已完成时长不累加至本候选；旧真实Mail5357秒FAIL保留。
- 32相同分发文件和210481152字节为分别观测差额；不是新Host构建或新系统能力。
- 导出器10+4为两批微型fixture及当前脚本窄复核，不是实际F导出、14次完整复现或接收Mac运行。
- 跨维度引用同一原件只证明不同属性，不增加实际测试次数；fixture、真实节点和官方full-chain始终分开。

**未完成门槛。**

- 同最终候选/身份Mail→Memory→Calendar create/get→原ID改期/get→回复到达→首次恢复/跨聊天完整业务链。
- 当前profile通过官方登录获得同步凭据；新Calendar桥编入Host、对应权限和精确动作授权。
- M3 S02 invalid_output/未知usage、M27 R02缺因及两个M01无依据评价尚未有已授权修复后的新验收。
- rc10完整7200秒合成驻留仍RUNNING；真实Mail后端长运行未完成，历史5357秒绘制FAIL未关闭。
- 完整clean构建/安装、OS重启、第二Mac/ARM；当前Frozen F及桌面交付尚未实际导出。
- 当前外部业务视频、正式publisher/政策、独立scan reviewer、stockHub准入与上游贡献接纳。

Root提供soak完成原件精确SHA和范围后，仅复核新证据并对这两份A审阅做一次短增量更新；不重复既有测试，不自动抬分，不修改共享主报告。

本轮只新增RC10_INTERNAL_A_REVIEW.md和.json。没有修改产品、SDK、Git、共享主报告、旧证据或用户资料。

