# rc51 第二轮矩阵原始失败

结果FAIL，产品UI验收PARTIAL。2026-10-06按原10cold+5reopen/启动40秒门槛执行完整尝试，cold01–04/07共5次完成真实新进程与六页/输入/合成资料检查；其余5cold与5reopen未通过。没有用通过轮次抹去失败，也不能说10个产品源码都启动失败。

同候选rc51-cold-experiment-r3、compact ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da、Host1d7及同一合成seed。启动前8492空，受保护文件与r1一致；PREFLIGHT在相邻cold-rc51-r2-preflight.json。主run_shell_matrix.py与wrapper未改；Root第一版launcher已加入TCP关停确认及quit404/拒绝连接处理。

| 失败 | 事实 | 未确认事项 |
| --- | --- | --- |
| cold05 | quit处RemoteDisconnected未捕获，启动器异常在新open前退出；capture连接拒绝。 | 不代表新产品源码编译失败。 |
| cold06、08 | launcher子进程超过40秒；capture HTTP404，没有完整startup日志。07恢复并完成全部检查。 | 超时发生在哪一阶段未取得足够证据，不能声称没有预算/E或归因产品UI。 |
| cold09、10 | launcher报Previous candidate Shell is still running，TCP检查未确认端口关闭，因此没有执行新open。 | 保留实际关停失败，不提高时限或强行复用旧进程。 |
| reopen01–05 | /s阶段HTTP404或端口拒绝，无法取得有效PID并进行实际重开。 | 没有5次有效重开，不能计PASS。 |

完整完成的冷PID为18572、19342、19987、20843、22487；最终合成文件和安装源SHA不变，model ledger未创建，8492已空。未调用模型、邮件发送、Calendar写入、OS重启或生产资料替换。失败capture缺失仍为FAIL，不能证明无[E]。原report/audit/exception/launch保存在cold-rc51-r2/，SUMMARY.json记录分类与SHA。

launcher预先SHA307318c0，结束时49cef8ba；已通过字节重建验证，两者唯一差异是删除未使用的urlopen import，执行逻辑未变。这仍记录为字节变化，不隐藏。A4此轮没有写launcher。

停机后按Root明确移交的单文件边界，A4在launcher增加http.client.RemoteDisconnected捕获，将quit读取超时由Remote固定15秒降为5秒。仍必须独立TCP确认旧端口已关闭，未改变整体40秒门槛、Host/预算/产品源。下一组须使用鲜r3目录；r1/r2原失败不覆盖。
