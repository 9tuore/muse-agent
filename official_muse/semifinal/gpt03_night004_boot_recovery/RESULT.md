# Result

PARTIAL：最小候选 patch 的 46 项功能检查 PASS；真实 Host 64 ms 预算和 R5 GUI 由 Root 验证。

现场 Main 8227 的 `core_boot_goals` 对每个 `in_flight` 克隆全记录并提交一次。R4 Host.log 第269行明确在 Main6779备份回读处报 `script time budget exceeded`。主记录8 unknown/120 in_flight，备份7 unknown/121 in_flight；实际截图停在初始界面，coldstart16.493s只是formal shell，随后记忆导航失败。只读事实见 evidence/root-readonly-observation.json。

候选只改 core_boot_goals：第一次发现 in_flight 时克隆原快照，遍历统一改 unknown，再提交一次。不改校验、提交函数、恢复函数、其他状态、ID、payload、Run/Goal或启动链。目标候选Main SHA：caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce。

实际缓存官方debug CLI VM运行6例/46项：0待恢复时0写/0提交回读；1/128待恢复均2写/2提交回读（启动读主记录另有1次）；128例原主记录原字节成为备份。全结构比较只允许 in_flight→unknown。备份写失败、主写失败、主回读失败均返回false并恢复旧内存快照，无业务dispatch。主回读失败沿用原core_commit_goals语义：磁盘主记录可能已更新，备份保留旧快照，内存恢复旧记录；不声称磁盘回滚。完整实际输出索引/操作序列见evidence，原VM结果和state留在自有build。

只有storage_read/write是显式fixture适配；5个生产函数/8global从候选原字节提取。现有VM总50M指令，没有时间预算。父进程interval包含IPC和文件IO，0/1/128例275.538/333.908/347.116ms，不能算Host64ms结果。未运行Cargo、Kernel、GUI，未改Root Main/SDK/包/用户profile，无push。

最初probe使用SDK保留字ok导致parser失败，改为restored/is_ok后通过；旧失败日志保留build/failed-probe-r0。Root最新指示先交patch/已有VM验证，因此没有编译64ms helper。
