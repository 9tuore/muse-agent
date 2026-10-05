# rc51 首轮矩阵原始失败

2026-10-06结果：矩阵FAIL，产品UI验收PARTIAL。按原40秒启动限制尝试了10cold+5reopen；只有cold01/02完成有效新进程和全部UI检查（PID10200、10839）。原报告计cold2/10、reopen0/5，不把剩余8个cold记录当作8次已发生的产品编译失败。

候选 `official_muse/app/build/ui-memory-20261003/rc51-cold-experiment-r3`；compact SHA256 `ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da`；Host保持1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3。启动前TCP8492已检查为空，没有复用旧进程。完整入口与输出为run_matrix_audit.py、cold-rc51-r1-run.txt和cold-rc51-r1/。

cold03的launch_candidate子进程超过40秒，未留下成功ready输出；快照请求HTTP404。超时具体发生于退出等待、App Hub启动或其他步骤尚无证据，原失败保留。

cold04/05在启动器line56的r.request('/quit')返回HTTP404，cold06同点连接被关闭，cold07–10同点ConnectionRefused；旧启动器没有捕获这些退出响应，异常在open -n之前结束。这是已确认的测试restart级联。5次reopen均因端口无服务未进入实际重开。缺失log/snapshot在额外审计中仍算失败，不能据此声称没有[E]、预算或编译错误。

只读补充请求记录在HANG_OBSERVATION.json：观测时8492无listener，/log与/s连接拒绝；这份记录不能证明Host持续hang。cold06留下空s快照，其余失败capture错误均保存于原report/exception。两个通过轮次有完整实内容、可编辑输入、六页、非空合成记忆及状态/ledger检查。

最终全部受保护资料SHA不变、安装source SHA不变、model ledger仍不存在；8492为空，已知两个PID均退出。未做模型提交、邮件发送、Calendar写入、系统重启或生产资料变更。Root8493、Host、模型与49桌面包保留。

Root随后对launch_candidate.py做退出协议修正：容忍quit404/ConnectionRefused后仍必须TCP确认端口关闭，首次非restart也拒绝占用端口。A4核对diff，未修改该脚本或产品/Host/预算；需要以同rc51/seed在新的cold-rc51-r2目录重测。旧r1报告、异常与snapshot永不覆盖或降为PASS。
