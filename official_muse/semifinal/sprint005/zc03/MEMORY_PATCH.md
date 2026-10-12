# Memory 校验最小候选

Root基线8da96cfd；Main caa99。仅gm_validate_indexed_part增加两个本地count，在claims阶段不遍历sources，在sources阶段不遍历claims。所有有效校验、all/correction及异常范围语义不变，batch=2/20ms/64ms Host预算/128动作一次提交保持。

同生产API生成的64 Memory/128 Sources原字节fixture，独立新非GUI ScriptVM，A/B/B/A四个进程，384个实际片段interval、每进程22边界/损坏结果一致；active坏Source/Claim被拒、未选片段仍沿用原过滤语义，文件不变、零业务dispatch。24函数/6global仅目标函数不同。实际父perf_counter_ns含RPC/调度，系统负载未隔离；Source中位6.510→5.395ms、Claim15.451→11.785ms，不算GUI首屏/64ms通过。

此前CLI缓存已清理，最小ScriptVM离线重建27.58s、独立target63MiB、无incremental，无Host/Kernel/GUI构建。新VM337cbba7，driver源码与旧VM逐字相同，profile dev debug=0；不拿它与旧14指标比较。SDKscript163源文件构建前后相同。

候选Main SHA947c52915c507f9a7a7a896c554b43f1c1e0a9ec11bee490bed5304d054b642b。Root独占接入并在同fixture/同入口/同方法测实际GUI；本地patch不直接修改中央Main。

只读证据复核：python3 -B official_muse/semifinal/sprint005/zc03/verify_memory_evidence.py

定向实际重跑命令见README（全新out）。GUI未执行。默认仅建议Root先审patch，不把独立CLI测量当宿主改进结论。
