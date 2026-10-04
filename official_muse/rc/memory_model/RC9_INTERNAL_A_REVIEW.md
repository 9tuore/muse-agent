# rc9 内部 A 独立审阅

内部A70/100；原20项仍5PASS14PARTIAL1BLOCKED。没有READY、95分或正式排名证据。

审阅者：A3 现有真实聊天。证据截点为 2026-10-04T23:07:03Z；产品 1c9f3b46e7aac0ee17be385de64c97564651152f / 0.3.26-rc9；现场 HEAD 862c55e153692647b8699c2c715a0ddf60f1477a，文档汇总提交14639fe0。仅新增本 Markdown 和同名 JSON，未运行模型、GUI、构建或测试，未修改产品、SDK、Git、生产数据或旧证据。

六个维度上限由委托给定；下面的子项权重是本审阅公开的内部判断，并非官方评分细则。评分没有目标95或排名锚点。历史A66/B65已明确标注V15/b486，没有误当rc9分数。

可读源码 SHA 9d01484cb775329530d00f077fb74cfa8469e61ad3117a21360779c4bda13505；payload SHA 4c970e041bdb8d7726a1ceada2050033445374c3a9e908a873cb36e206d8c5d5。两者独立核验匹配。官方tokenizer91195等价是既有Root结果，本轮未重跑tokenizer。Host938/运行SDK3f与源码SDKda分开，92b1 Calendar布尔修复尚未进入当前Host。

| 维度 | 分数 | 扣分 |
| --- | ---: | ---: |
| 任务完成 | 17/25 | 8 |
| 可靠运行 | 13/20 | 7 |
| 人机协作 | 12/15 | 3 |
| 项目反哺 | 10/15 | 5 |
| ROM/系统突破 | 7/10 | 3 |
| 效果证据 | 11/15 | 4 |
| **合计** | **70/100** | **30** |

## 逐项依据与扣分

每个E编号在后文包含实际commit、文件、测试范围、现场SHA或原件SHA；引用历史资料时保持旧版标签。相同证据跨维度说明不同性质，不增加测试覆盖数量。

### 任务完成 17/25

| 子项 | 分 | 证据 | 扣分原因 |
| --- | ---: | --- | --- |
| 普通聊天与候选修改 | 4/5 | E01, E06 | 扣1：仅历史rc8八组中相关分支的支持，当前完整15题与自由对话准确性未完成。 |
| 跨聊天记忆更正与遗忘 | 5/6 | E02 | 扣1：六步合成内容通过，不覆盖真实冲突消解及Mail/Calendar上下文全过程。 |
| 一次性本地任务 | 6/7 | E03 | 扣1：一个Goal/Run的本地结果成立，更多任务及外部业务语义未覆盖。 |
| 同候选外部系统全链 | 0/5 | E09, E12 | 扣5：T18仍BLOCKED，最终Mail→Calendar创建/改期→独立get→回复链未通过。 |
| 两模型受影响D05 | 2/2 | E04 | 不扣：只按一个受影响问题的双通道观察给分，完整双模型测试缺口已由普通聊天子项扣除。 |

### 可靠运行 13/20

| 子项 | 分 | 证据 | 扣分原因 |
| --- | ---: | --- | --- |
| 当前启动与重开矩阵 | 4/5 | E05 | 扣1：固定合成种子、最长17.609秒；不覆盖OS重启/真实后端/无限负载。 |
| 第一次任务重启持久性 | 4/4 | E03 | 不扣：只奖励八个文件的等值与不重放，不按八次独立重启计。 |
| 故障与恢复机制 | 3/4 | E01, E07 | 扣1：历史fixture及不变函数支持，未做当前全部真实故障场景。 |
| 长运行与跨环境 | 0/4 | E11, E12 | 扣4：rc9两小时及100次普通重开未完成；真Mail5357秒旧FAIL、电脑重启、clean、第二Mac/ARM缺口保留。 |
| 失败可观察与保护 | 2/3 | E11, E12 | 扣1：原错误/中断保留，但Host请求数不可观察、历史UNKNOWN及真实绘制错误未完全解决。 |

### 人机协作 12/15

| 子项 | 分 | 证据 | 扣分原因 |
| --- | ---: | --- | --- |
| 明确批准并防重放 | 4/4 | E03 | 不扣：只限一次本地Goal批准，不能代表所有外部动作授权。 |
| 缺时间先追问 | 3/4 | E01, E04 | 扣1：D05双模型应用守卫成立，更广泛含糊输入与连续改口真实链未全部验证。 |
| 范围/过期/重复保护 | 3/4 | E01, E07 | 扣1：隔离fixture与不变函数支持，真实人工手写稿及外发连续体验未完成。 |
| 可见可编辑交互 | 2/3 | E05, E11, E12 | 扣1：当前启动检查编辑和六页，旧412×892受Dock遮挡FAIL保留，没有完整rc9尺寸/视觉验收。 |

### 项目反哺 10/15

| 子项 | 分 | 证据 | 扣分原因 |
| --- | ---: | --- | --- |
| 可还原SDK与锁 | 3/4 | E08, E10 | 扣1：锁/overlay/旧SDK重建有证据，但当前新SDK/rc9完整clean重建未完成。 |
| 具体框架与桥接修复 | 4/5 | E08, E09 | 扣1：native摘要与4KiB准备有原生验证；Calendar布尔修复未进入当前运行Host。 |
| 贡献材料与边界 | 3/3 | E09, E10 | 不扣：文档给出实际缺陷、纯测试、权限/回读限制及最小上游拆分草稿；只奖励可审阅材料。 |
| 上游合并与准入 | 0/3 | E10, E12 | 扣3：DRAFT/NOT_SUBMITTED，本地扩展未获官方上游接纳。 |

### ROM/系统突破 7/10

| 子项 | 分 | 证据 | 扣分原因 |
| --- | ---: | --- | --- |
| 官方运行路径与模型 | 4/4 | E02, E03, E04, E05 | 不扣：当前Splash/OctoSense真实Host运行和model.complete成立，未声称stock政策准入。 |
| OS服务机制 | 2/4 | E09, E10, E12 | 扣2：历史真实EventKit读与Calendar宿主机制成立；最终桥缺陷/写入独立读回链未通过。 |
| 隔离存储与能力边界 | 1/2 | E03, E08, E12 | 扣1：本地存储和锁定宿主有证据；LOCAL_EXTENDED_HUB不等于官方原版准入或跨机器权限可用。 |

### 效果证据 11/15

| 子项 | 分 | 证据 | 扣分原因 |
| --- | ---: | --- | --- |
| 身份与原件哈希绑定 | 3/3 | E01, E02, E03, E04, E05 | 不扣：当前源/报告逐文件SHA对应，70摘要尚未提交如实注明。 |
| 实际原生画面 | 2/3 | E11 | 扣1：两张公开合成实机图，未有同最终完整链的视频及全页视觉证明。 |
| 输出独立核对与反例 | 3/3 | E03, E04, E05, E11 | 不扣：本地回读、SHA、无重复/未动作断言与原失败可追踪；仅奖励可核验性，不再累加成完成覆盖。 |
| 完整复现与材料同步 | 1/4 | E10, E12 | 扣3：旧SDK还原与静态材料可查；rc9 clean/第二Mac/ARM/电脑重启未完成，证据索引/70进度文字滞后。 |
| 真实披露覆盖边界 | 2/2 | E01, E04, E11, E12 | 不扣：历史版本、fixture、应用守卫、费用未知和失败均显式区分；A66/B65明确标为历史估计。 |

## 证据目录

仅公开合成摘要与哈希引用；不复制原始trace、消息、state、系统标识或凭据。

**E01** — commit 1c9f3b46e7aac0ee17be385de64c97564651152f. 文件：[RC9_DELTA_BINDING.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/RC9_DELTA_BINDING.json>)。

测试：rc8→rc9 readable source diff; only chat_candidate_input_error and Settings label changed; A2 15 variants/53 assertions recorded。范围：Diff independently read; A2 fixtures are prior run, not repeated by A3; tokenizer result coordinator-reported。
现场文件SHA256：0c3c2af66f71abd1fcb43e006c861936fecff5d5a8084b0a6f63f5e5324f9075（1594 bytes）。

**E02** — commit 1c9f3b46e7aac0ee17be385de64c97564651152f, fa89b6750c13e271de2b5b374b45afd3774edc86. 文件：[RC9_LIVE_NODE_SUMMARY.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/RC9_LIVE_NODE_SUMMARY.json>)。

测试：Six memory steps, three real M3 calls, same-ID revision1→2, cross-chat recall, forget/history removal/tombstone/empty recall。范围：Current rc9; six raw steps and PASS independently counted; no external action。
现场文件SHA256：304c3f09fbcfc5e95711ea18cfa8d9ca56bfbc3db6e10323844210243d335cb7（4694 bytes）。
本地原件引用：official_muse/app/build/ui-memory-20261003/rc9-final-model-r1/live-evidence/report.json；SHA256：d9bde45093d45a8e4c2b62932db304ee334673abb331e119c55327826a2f2e26。本审阅核对原件哈希及指定合成字段，不公开原件。

**E03** — commit 1c9f3b46e7aac0ee17be385de64c97564651152f, fa89b6750c13e271de2b5b374b45afd3774edc86. 文件：[RC9_LIVE_NODE_SUMMARY.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/RC9_LIVE_NODE_SUMMARY.json>)。

测试：Two M3 calls, one approval, two local results; first Shell restart compares eight protected SHA values。范围：Current rc9; raw approval/result counts, eight hash equality, unique Goal/Run and no replay independently asserted; no OS reboot/external chain。
现场文件SHA256：304c3f09fbcfc5e95711ea18cfa8d9ca56bfbc3db6e10323844210243d335cb7（4694 bytes）。
本地原件引用：official_muse/app/build/ui-memory-20261003/rc9-final-model-r1/goal-restart-evidence/report.json；SHA256：d5049c9e2b2c27f98bf5af79b7225b93ad12dbf7593eab4637210fbe34715c5a。本审阅核对原件哈希及指定合成字段，不公开原件。

**E04** — commit 1c9f3b46e7aac0ee17be385de64c97564651152f, fa89b6750c13e271de2b5b374b45afd3774edc86. 文件：[official_muse/rc/startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json>)。

测试：Actual M3 and M2.7 D05, one UI input each; waiting_user asks explicit start/end, zero proposals, no external actions。范围：Reply.text, waiting_user, zero proposals and ledger95→96→97 independently asserted; app guard after actual model completion, not raw model's own clarification; raw driver review remains PENDING_MANUAL_REVIEW and separate Root semantic review supplies PASS; not full T17。
现场文件SHA256：11ecc7b1b75d3ce2f4143cced8286bd8347d722a7975a5fd604384108877e33e（3899 bytes）。
本地原件引用：official_muse/app/build/ui-memory-20261003/rc9-final-model-r1/calendar-D05-m3-r1/report.json；SHA256：775f5eee95264235ca007fa73299d2dda26ca8774d0afbd46dd64986e52ea2b8。本审阅核对原件哈希及指定合成字段，不公开原件。
本地原件引用：official_muse/app/build/ui-memory-20261003/rc9-final-model-m27-r1/calendar-D05-m27-r1/report.json；SHA256：4b0fdbb18bb41f5512ef6e8d5f22e26a41b887d4030767e556a8a3d0945b383d。本审阅核对原件哈希及指定合成字段，不公开原件。

**E05** — commit 1c9f3b46e7aac0ee17be385de64c97564651152f. 文件：[official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json>)。

测试：rc9 r2 disjoint 30 cold/20 ordinary reopen/20 Shell restart; all70 per-row pass, editable input, protected state and model ledger equal。范围：Raw arrays/counts/pass flags independently asserted; summary untracked at audit HEAD, cannot claim committed evidence; synthetic16 sessions/256 messages/64 claims; neither OS cache clearing nor real backend semantics。
现场文件SHA256：cbc7813c17310e639284a72f3e87fe2571d581b29e12cb6febafae9bbeccd70b（3976 bytes）。
本地原件引用：official_muse/rc/startup/evidence/rc9-1c9-final-70-r2/report.json；SHA256：6a2605399d70c7bea316117e230d6f5da578d31a43e82aa0ef7a461e30eb8154。本审阅核对原件哈希及指定合成字段，不公开原件。

**E06** — commit a80bd019db7581511b3891bcc3892548f767a42d, 0cf33fabf4ae25bb62067828a7367beae8cd98e4. 文件：[official_muse/rc/startup/RC8_M3_EIGHT_SEMANTIC_REVIEW.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/startup/RC8_M3_EIGHT_SEMANTIC_REVIEW.json>)。

测试：Historical rc8 eight cases including S01=13/S02=15 and E04 same-card revision retaining to/subject; S02 two Host attempts retained。范围：Historical model result, bounded support through E01 unchanged functions; not an rc9 eight-case rerun or full15。
现场文件SHA256：3932f063aef52e460bc764983bd5d0c234c59f4bf5966b5b0b44e2745abc7944（3706 bytes）。

**E07** — commit f98277d6ea534ce29577c2cc089ed73601311f91, 91d21a3fd94f67953d048e1901fd0403b888db65. 文件：[official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/core_chain/PUBLIC_TEST_SUMMARY.json>)。

测试：Historical core28+4 restarts/proposal25+6/fault20+3; later limited Goal9cases58checks, metadata5cases91checks; typed scope/duplicate/stale/recovery controls。范围：Synthetic Host/isolated filesystem and historical snapshots; limited function reuse support only; real inference/Mail/EventKit/visual acceptance false; no current full-suite claim。
现场文件SHA256：8b2657b1e490e53c0a07b70ae7f9948ec82e9bbf11899342bc88339fd407db05（12254 bytes）。

**E08** — commit aacc8d17cc25724bacaebb5260ff13b628655db7, 852fa951b5b509d04cd0f0b9b9225d1091ef84fe, 51359d702603e9cc5c98e6f46f2aa6ed631ded26. 文件：[official_muse/rc/packaging/CHUNK_DELTA_BUILD_RESULTS.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/packaging/CHUNK_DELTA_BUILD_RESULTS.json>)。

测试：Native storage hash tests and preparation/cancel tests; locked incremental Host/Card builds, strict ad-hoc verification and SDK12000 verify recorded。范围：Historical incremental SDK mechanism/build evidence; signed binaries938/527 bind current runtime; not clean build/new Calendar Host/ARM/upstream merged。
现场文件SHA256：566d9642b158d46dc77130b8f048533785750ef984bd619b5042c873aaebb00c（13963 bytes）。
配套文件：official_muse/rc/overnight/NATIVE_STORAGE_CHANGE.md, PREPARATION_CHUNK_CHANGE.md。

**E09** — commit 92b1df15112a1d5edf6336a3d3cfae181b4a99ca. 文件：[RC_CALENDAR_READONLY_REPORT.md](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/RC_CALENDAR_READONLY_REPORT.md>)。

测试：Authorized old Host actual EventKit read; product rejects numeric truncated; Foundation count0/100/101 comparison regression exit0 recorded。范围：Source fix and historical OS-read diagnostic only; source SDKda hash verified; fix absent from current runtime938; no current create/update/get PASS。
现场文件SHA256：3cca5dfde37bc0f0edc9fa23d19a9c86f9911df3e7ed23c667462d4b2d805f1e（4293 bytes）。
配套文件：official_muse/rc/startup/calendar_boolean_serialization.m。

**E10** — commit 51359d702603e9cc5c98e6f46f2aa6ed631ded26, eba2924db8a8531a3affe8882a7c5b89fb0c220d. 文件：[official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/packaging/CLEAN_ROOM_R2_FINAL_AUDIT.json>)。

测试：Five exact archives/SDK12000 bootstrap and verify completed; Calendar three pure validation/journal tests exit0; reproducibility run stops before clean executable。范围：Historical source069d and runtimeSDK3f; retained controlled failure; no rc9 clean build or upstream acceptance; contribution DRAFT/NOT_SUBMITTED。
现场文件SHA256：1c4f75db8cc99d72962e7665562961282b949d68f71281012d94356b3f56f36c（6696 bytes）。
配套文件：sdk-overlays/README.md, official_muse/rc/packaging/UPSTREAM_CALENDAR_CONTRIBUTION.md, official_muse/rc/packaging/CALENDAR_PURE_TEST_RESULTS.json。

**E11** — commit 1c9f3b46e7aac0ee17be385de64c97564651152f, 8a60d51a13bdcda1791cd57149823b5f33bbf3ac. 文件：[official_muse/rc/screenshots/RC9_PROVENANCE.json](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/screenshots/RC9_PROVENANCE.json>)。

测试：Two current synthetic native PNG hashes, Root actually-viewed provenance; r1 ENOSPC startup30/13 and soak19samples542.154s retained。范围：A3 verifies hashes only, no new visual QA; two PNGs not full UI/video/chain; interruptions not PASS。
现场文件SHA256：8d1fc0f09b5945a383a30fdc44ed28dbe6ad82c8f5ad2267d75434609aad9562（1316 bytes）。
配套文件：official_muse/rc/screenshots/rc9-cross-session-forgotten-memory.png, official_muse/rc/screenshots/rc9-goal-after-first-restart.png, official_muse/rc/startup/RC9_STABILITY_INTERRUPTION_SUMMARY.json。

**E12** — commit 14639fe0d2ed39b20fe3ccd42d3adac94fa61dd9, 34fb31323713f69d22f368f009dbab4459526b12, 862c55e153692647b8699c2c715a0ddf60f1477a. 文件：[RC_ACCEPTANCE_MATRIX.md](</Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/RC_ACCEPTANCE_MATRIX.md>)。

测试：Original20 status arithmetic, source/runtime identity separation, public static bundle gate and retained limitations; 862c only count bounds changed。范围：Docs/public static checks, not system action evidence; 100 reopens/2h r2 pending at instruction snapshot; several progress/index entries stale。
现场文件SHA256：1cb4306a9c8d6c6cc36e5c8010824260ada69cb46ae9b435bf96db666dc113a4（5121 bytes）。
配套文件：CHAMPIONSHIP_SCORECARD.md, RC_CODE_FREEZE.json, RC_EVIDENCE_INDEX.json, OVERNIGHT_SOAK.md, official_muse/rc/packaging/RC9_1C9_PUBLIC_MAINTENANCE_SYNC.json。

## Root 报告需要修正的点

没有发现把外部全链、完整双模型、电脑重启或旧V15两小时写成当前rc9通过。发现以下版本/进度/索引滞后，由Root统一修改，本审阅不写这些文件。

- P2 RC_EVIDENCE_INDEX.json:3：产品提交为1c9f3b46但顶层status仍CURRENT_RC8_PARTIAL。 Root更新为当前rc9 PARTIAL，并保持原历史rows版本。

- P2 RC_EVIDENCE_INDEX.json：记录PUBLIC_TEST_SUMMARY为6415bytes/SHA0aac6676…，现场原件为12254bytes/SHA8b2657b1…；摘要已更新，索引摘要未同步。 Root重新计算此公开条目的bytes/SHA，不覆盖旧证据原件。

- P2 RC_CODE_FREEZE.json:31：startup70仍RC9_R2_30_20_20_RUNNING，与r2原件70/70冲突。 Root追加rc9 r2已通过的独立报告/SHA引用；2h和100次普通重开保持未完成。

- P3 RC_ACCEPTANCE_MATRIX.md:26：T20将rc9 r2完整启动测试写为进行中。 Root同步70完成与2h/100未完成的分别状态；T20仍PARTIAL，不合并旧r1/rc8/V15测试计数。
  同类位置：COLD_START_PROFILE.md:3, MORNING_CHAMPIONSHIP_REPORT.md:15, README.md:11, MUSE_HANDOFF/CURRENT_STATE.md:5, RC_FINAL_LIVE_REPORT.md:29, SOURCE_DELIVERY.md:7, CHAMPIONSHIP_SCORECARD.md:5。

- P3 official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json：本次现场未跟踪；在862c55e1的Git中不能恢复此摘要。 Root在最终证据提交/允许列表中明确纳入并绑定当前文件hash。

## 本轮只读验证与计数边界

当前r2原始数组逐行核对为30/30冷启动、20/20普通重开、20/20Shell重启；70行的可编辑、非空记忆、保护存储、模型账本均成立。当前Goal原件一个批准、两个结果、八文件SHA相等、无重放；Memory原件六步且PASS、无外部动作。两个D05原件reply是对象，分别核对reply.text、waiting_user、空memory_refs、前后零候选、单输入以及账本每次增加一个调用。原驱动报告为待人工语义审阅，PASS来自单独语义审阅文件，不将驱动原件改标签。

两张公开PNG的字节/hash与provenance匹配；实际看过截图的声明来自Root，本轮A3没有重新看图或做视觉验收。

- Memory six steps contain three calls; local Goal contains two calls; two affected D05 model observations contain two calls. These are seven distinct current calls, not eleven steps-as-calls.
- D05 is one problem through two actual model routes, not two complete eight/15 suites. rc8 M2.7 D05 FAIL remains a historical failure.
- Goal's eight equal files describe one first Shell restart, not eight restart trials or OS reboot.
- Current r2 startup arrays are disjoint30+20+20=70; r1 incomplete30+13, rc8 and V15 never added to70.
- 100 same-seed ordinary reopen and rc9 r2 7200s are pending at Root instruction snapshot; no completion or score credit.
- Existing evidence used across dimensions supports different properties; no claim that reuse creates additional test coverage.
- Historical SDK/OS-read and fixture records retain original source/Host labels; sourceCalendar92b1 never relabeled as runtime938 fix.

## 未完成门槛

以下缺口未因70分或70次启动通过而取消；后续结果须另带同版本证据才更新。
- Current final external Mail→Calendar create/get→same-event update/get→reply full chain (T18).
- Complete two actual models'15-problem acceptance; M2.7 model class remains unknown.
- Current full7200s soak and additional100 same-seed ordinary reopens, pending at scope cutoff.
- New Calendar Host integrating92b1/sourceSDKda plus authorized same-candidate system read/write verification.
- Complete clean build/install, computer restart, second Mac/ARM reproduction.
- Final video/materials, public publisher/policy/stockHub admission and upstream acceptance.

本次授权新增文件仅为 RC9_INTERNAL_A_REVIEW.md 与 RC9_INTERNAL_A_REVIEW.json。Root保持唯一产品/文档/Git写入者；本审阅未commit或push。
