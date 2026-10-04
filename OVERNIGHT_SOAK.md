# 夜间持续运行实测

## 最终产品 V15 合成账户：RUNNING

实际可见 OctoSense Shell，产品 b48618ac/source5092becd，Host938ba58a/SDK3f。原64ms预算与非空16对话256消息、64记忆65来源、64已见合成邮件保持。合成账户没有Mail后端或凭据，不能证明真实收信网络的持续可靠性。日历异步回调实际返回not_determined，未替本人授权。

- 开始：2026-10-05 02:41:03，北京时间。目标7200秒，预计04:41左右结束。
- 当前仍在采样，不能写2h PASS。最终统计在完成后填入本页。
- 每30秒读取实际远程日志、资料SHA/mtime、动作数量及model ledger；不以进程存活替代这些检查。
- 脚本不能观察全部Host请求计数，明确记NOT_OBSERVABLE；不能写零网络请求。
- 原件：`official_muse/app/build/ui-memory-20261003/rc5-final-b486-soak-evidence-r1/report.json`。

这是新Calendar一行修复前的Host。源码SDKda756dde/92b1df15完整Host还没编译，不能把本次测试身份换成新Host。

## 稳定0.3.25真实账号：FAIL

实际观察5357.14秒，178份完整样本；遇到原生macOS日志present gate stuck331.36408ms/3inflight/drawable pool恢复而停止。原驱动exit1、失败日志与资料保持，不把89分钟补写成2h。CPU曾约22–58%，不称低功耗；没有新增模型/action/相同内容落盘。实际自发自收独立正文SHA已过，不抹去到达证据，也不以到达替代长运行。

原件：`official_muse/app/build/ui-memory-20261003/rc5-existing-live-soak-r1/report.json`。来源Host0fd99361/sourcea44677c4，与V15合成分别记账。

## 原短测试与受控停止

V9观察4006秒、V13b361.575秒均因源码修复被受控停止，非2hPASS；069d启动探针为driver标签错误，原FAIL保留。不同运行时长不相加。电脑重启尚未执行，Shell重启不等于电脑重启。
