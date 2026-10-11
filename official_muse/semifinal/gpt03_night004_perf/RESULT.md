# NIGHT-004 真实计时 baseline

2026-10-12 04:42（Asia/Shanghai），GPT03。c892 baseline测量完成，14项数据/运行/计时检查PASS，归档证据复核PASS。**这是测量有效性，不是性能阈值达标结论**；没有定义或补造SLO。现成binary是`target/debug`中的debug CLI VM，执行源码仅设置50,000,000总指令上限，未启用正式GUI的64ms回调预算；**本次Memory约76ms不等同正式GUI预算失败**。新Main尚待Root明确SHA，未执行新候选。

| 单次调用，31个正式样本 | 最小 ms | 中位 ms | p95 ms | 最大 ms |
| --- | ---: | ---: | ---: | ---: |
| `gm_context("规模条目","scale-chat","")` | 68.453198 | **76.644147** | **91.168581** | 107.320224 |
| `ac_projection()` | 8.007845 | **9.477834** | **12.758504** | 13.745837 |
| 无API的RPC桥接区间 | 0.147611 | 0.206595 | 0.259184 | 0.345499 |

每项先预热3次再测31次，一个区间恰好调用一次API，不做批次平均。p95是排序后的nearest-rank `ceil(0.95*31)=30` 项。空桥接对照单列，未从API结果中扣除。总计102个区间、204条真实VM perf-mark请求。

## 计时机制

先核对现有`gpt03_night004/vm/src/main.rs`及`CLI_PROTOCOL.md`：官方VM已有同步`mod.fixture.rpc`，打印`MUSE_VM_REQUEST`后flush，并等待parent一行JSON回复。本parent只在这一已有通道内处理自有`fixture.perf_mark`，没有新增SDK/Host端口或重建VM。

parent在收到并派发start标记时调用**真实Python `time.perf_counter_ns()`**，收到end时再读同一单调时钟（本机implementation=`mach_absolute_time()`，报告resolution=1ns）。start回复序列化/IPC、VM读取回复、执行API、end请求序列化/IPC及parent队列/调度均处于区间内。因此这些值是本次环境中包含桥接开销的观测上界，不是纯函数CPU时间或所有运行环境的最坏上界。没有使用fixture clock作为计时来源。

每个`gm_context`区间实际包含一次`fixture.clock`和一次真实owned文件`Path.write_text`；这是原函数生成审计时间并写`memory-retrieval-last.json`的路径，clock返回值只用于合成资料时间。每个`ac_projection`区间及空对照无内部IO RPC。区间RPC计数随每个样本保存，证据复核检查了这一差异。

## 样本与现场身份

- Main源码SHA：`c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`；重新提取157个生产函数、65个global并保存逐项SHA。实际适配只含`ac_refresh`、`ui_layout_save`及storage read/write，另将host.request映射到明确fixture transport；其余函数按原字节提取。
- VM SHA：`f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351`。复用已有`target/debug/gpt03-night004-vm`，实际PID及exit0保留report。未Cargo/SDK/Kernel/GUI。
- 本机报告：macOS 14.8.7、进程machine x86_64、Python 3.9.6。单个CLI VM进程，本次共一个baseline run，未隔离系统负载或测跨进程置信区间。
- 数据沿用旧scale的生产保存路径：`gm_save`建立64条Memory，`core_add_source/gm_make_source`补足128 Sources；`core_add_goal/core_start_run/core_begin_action`建立32 Goal、32 Run、128 Action。48条Memory属当前project/owner，8条foreign project、8条foreign owner。实际检索返回5条、2125字节、truncated=true；每个样本保留范围隔离和有界检查。
- 动作分布为每Goal 4条；全部Goal/Run仍running、Action仍in_flight，没有完成或核验记录，没有派发`storage.write`业务动作。`ac_projection`逐次切换Goal，正式样本按probe的`i=3..33`覆盖31个不同Goal；连同预热覆盖32个。每次实际扫描最近64/总128 Actions，投影3节点且limited=true。未添Calendar历史、Mail来信/草稿或12节点缓存fixture，因此不称所有投影分支的最坏延迟。
- 测量前后实际`goals.json`与`memory.json` SHA相同；数据、绑定与原状态均保留。唯一预期测量写入是检索audit。任何非fixture backend均拒绝；实际Host/Kernel/Mail/model/network调用0。

## 保留证据与接续

`evidence/baseline-r1/`保存完整report、102个原始ns区间、204条VM原perf请求、实际Main状态、执行闭包/身份、执行parent/prepare及现有VM RPC源码快照。完整VM stdout 46,746,259字节保留在自有`build/gpt03-night004-perf/baseline-run-r1/vm-stdout.log`，SHA在report和raw-log-index；不重复把46MB存储payload日志放入Git。基线证据manifest只覆盖该固定归档，未来候选另建目录。

`verify_evidence.py`另核对真实请求配对与样本ns、重算统计、核对实际64/128/32/32/128存储与所有Goal/Run/Action绑定、范围和无完成、前后SHA；PASS，不额外增加14项实际运行计数。重现及Root显式SHA命令见README。

## 生产save输出的可选GUI规模fixture

按Root追加要求，独立`export_fixture.py`只读本次标记state和实际report，校验SHA、合成文字及无完成/核验，再原字节导出白名单到自有`build/gpt03-night004-perf/baseline-run-r1/gui-scale-export-r2/fixture_files/`。没有重新跑VM或改原状态，r1初次导出亦保留；r2补全scope字段和每文件数量。8文件的来源与SHA在同目录manifest，scope在scope.json。副本和源逐字相等。

| 导出文件 | 实际来源 | 本文件记录数 |
| --- | --- | --- |
| memory.json / memory.backup.json | gm_save、gm_make_source、core_add_source的commit | primary 64 Memory/128 Sources；backup 64/127 |
| goals.json / goals.backup.json | core_add_goal、core_start_run、core_begin_action的commit | primary 32 Goal/32 Run/128 Action；backup 32/32/127 |
| activity.json / activity.backup.json | gm_save排队的core_record_event审计 | primary 64，backup 63，全为memory saved |
| global-memory-settings.json | owned gm_boot生成合成profile标识 | 1 settings |
| memory-retrieval-last.json | 本次实际gm_context审计写入 | 5 hits/2125 bytes |

backup保留真实前一状态，未补写成primary容量。Memory、来源excerpt和Goal文字均核对为本probe的固定合成literal；Action payload均为fixture=true，没有Secret或真人资料输入，未读Root profile。全部Goal/Run running、Action in_flight；Memory都是user_statement，没有completed/verified记录。chat仅是本次内存中的视图fixture，未执行chat_save，故两份chat文件明确absent，没有生成假UI状态。

当前合成user_id=`user:profile:1-2-3-4`、project=`muse-goals`、account=`local`、visibility=`personal`，focus project_id=`fixture-project`、owner_id=`fixture-owner`。Memory的scope分组48当前/8异project/8异owner；Sources另有64个由原scale API建立的孤立来源，其project_id/owner_id实际为空，其余48/8/8；Goal只有真实top-level project_id/owner_id字段，32个同focus，Action target_scope均local。所有字段原值导出，未对齐或猜测Host默认scope。

Root可在核对SDK实际storage路径、Host默认scope后决定合法GUI fixture适配。`gui_import_status=NOT_TESTED`，没有自行启动GUI或写用户profile。归档另存export manifest/scope/执行exporter SHA，数据内容复用baseline main-state，不在Git重复存两套JSON。

边界为合成数据、原生产API、官方CLI VM和实际owned文件IO；UI/计时队列/资料clock为fixture，不含GUI布局/绘制、冷启动恢复、真正磁盘fsync保证或Mail/Calendar网络时延。`full_chain_status=NOT_TESTED`。旧54/107项目录及Root Main/SDK/包未改；新Main复验仍待明确SHA。

## 2026-10-12 caa99 新执行

14项PASS，新证据复核PASS；Memory中位88.653645/p95 105.173179ms，Projection10.773112/15.596808ms。新prepare闭包只改变core_boot_goals，数据SHA同8227。原始102区间/204标记及来源见CANDIDATE_CAA99.md、evidence/candidate-caa99-r1。debug CLI未64ms预算，不作GUI/性能SLO结论。
