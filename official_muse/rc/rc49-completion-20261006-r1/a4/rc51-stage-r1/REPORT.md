# rc51 启动器阶段诊断

结果：SCOPED_LAUNCHER_PASS；一次启动器就绪链实际完成，原40秒超时未复现，原rc51-r3冷7/10、重开5/5和失败身份不变。旧超时根因仍未知。

2026-10-06只调用一次现有launch_candidate.py，候选rc51-cold-experiment-r3、port8492、--restart，subprocess.run(timeout=40,capture_output=True)。启动前端口为空，因此quit返回connection_refused；不是已有活跃Shell的关停复现。没有打开Muse、六页检查、模型、邮件或Calendar动作，没有清空seed、加时限或改Host/产品/预算。

新增阶段JSON写stderr并flush，保留原stdout就绪JSON：验证、quit请求前后、端口关闭、open前后、Hub等待/重试/就绪及未捕获异常。只写candidate/version/port/elapsed、结果和错误类型，不写环境变量、配置、命令或密钥。采集分支已覆盖TimeoutExpired.stdout/stderr保存，本次没有触发40秒超时。

实际记录：validated 0.282秒；quit后/端口关闭0.298秒；open完成0.434秒；Hub就绪1.771秒。stdout有ready=true；实际/s记录PID16688，/snap有应用中心与“已安装”，/log未观测到[E]/budget/source-preparation/compile错误。这仅证明本次launcher→Hub就绪，不证明Muse UI冷启动或原超时修复。

采集器在事后清理的literal lsof路径核验处exit1：lsof将中文文件名显示为UTF-8 byte escapes，未匹配原Unicode字符串。这个driver Assertion保留在SUMMARY/CLEANUP，不当作launcher失败。按同一预期UTF-8路径核对可执行文件后，仅向16688/8492发正常quit；未SIGTERM，PID与端口都已退出。此采集器错误导致child returncode未持久化，不编造exit0；SCOPED结果根据实际ready、阶段及/s/snap/log记录。

CPU观测前后都无FFmpeg进程；系统load average约20.29/21.30/19.29、8 logical CPUs。这是两次CPU环境快照，不能证明或否定旧超时由FFmpeg或系统负载造成。最终全部原protected SHA及安装源SHA不变，model ledger仍未创建。Root8493未触碰。

实际身份：产品compact ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da；Host1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3；完整launcher新SHA在IDENTITY.json。原始stdout/stderr、STAGES、实际三个端点、CPU、OBSERVATIONS、CLEANUP、SUMMARY均仅在本目录。未保留/运行额外matrix脚手架，未追加native测试，不push。
