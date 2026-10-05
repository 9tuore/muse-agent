# rc26-r2 en-dash 支持与不完整输入窄域复核

状态：**PARTIAL**。2026-10-05T18:38:04.451009+08:00。

原状态询问r1三组52断言已通过，此处没有重复。r1→r2精确只为时间range regex增加一个en-dash字符，status/helper其他业务源码字节相同（BYTE_BINDING_R2）。

新真实CardHost/synthetic transport两组 **26PASS / 2FAIL**：

- 原en-dash准备句“请安排日历2030-06-12 15:00–15:30，事项合成讨论，地点合成A。”确实能建候选，第二次地点修改仍同ID revision2并持久读回，9PASS。
- 6完整分隔符`- / ~ / 到 / 至 / — / –`：input_clear与candidate_input_error预期全部PASS。
- 缺开始时间与完全缺时间范围：拒绝PASS。
- **缺结束时间：“请安排日历2030-06-12 15:00–，事项合成讨论。”仍input_clear=true，且对synthetic模型返回完整payload候选检查返回空错误，2FAIL。** 所以不完整时间安全拒绝尚未通过。

没有执行该不完整候选、没有真实模型或系统日历操作。失败证明的是当前产品输入/candidate guard没有拒绝；不能说实际外部日历已被写。已通知Root，A2不改主源码。

readable `225784d4d47fd84e4d44bc47c5b1d23327e6296323890256b9764c02de5bfa24`；compact `291a68b252c973ec826563558d1ce9abf3e18b98a074db4fe046683d3d853208`，manifest rc26。真实锁定Host SHA `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`，沿既有fixture渲染/widget/Host transport替换，仅隔离实际fs。两个自启Host均退出。

原rc25 status FAIL、初始不支持en-dash候选准备FAIL、r1完整结果均保留。r2此失败保留在`rc26-endash-r2/time_formats/first/report.json`与summary；`PUBLIC_RESULT_R2.json`为PARTIAL。不把换setup当完成，不改期待答案。没有主/Host/权限/预算/Git/账号8493/8484操作。后续仅同窄probe在修正冻结复验，不重跑101或模型题集。
