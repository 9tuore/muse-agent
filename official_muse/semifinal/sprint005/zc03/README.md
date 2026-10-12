# SPRINT005 ZC03

Owner ZC03。仅本目录和自有build；Root唯一接入正式Main/Bundle，Root/ZC05掌握GUI，本任务不发其他聊天消息、不自动push。

- [Memory最小候选](MEMORY_PATCH.md)：同64/128数据A/B/B/A实际VM、384区间、22边界结果，唯一函数裁剪相反阶段遍历。正式GUI性能待Root。
- [复现与接入](REPRO_GUIDE.md)：旧20轮/版本审计、小型ScriptVM、被动有界observer、入口说明patch；命令占位符与fixture/live边界明确。
- [75秒真实UI演示稿](DEMO_75S.md)：Root执行，SCRIPT_READY/NOT_RECORDED，不伪造成功记录或权限。
- [黑桌面有界诊断](DIAGNOSTIC_PLAN.md)：原生图已看，资源完整核对，controlled single-host原型和新双启动完整Muse可见；根因未定，暂停GPU写改，不硬编码pass/texture ID。

保留的性能证据基线Root8da96cfd/Main caa99；Root已接Memory，当前Main947/rc8准备中，Source→stamped→compact三层分别947/a5af/049。R5 UIrc7正确stamp、包为保底，历史根bundle仍rc17；最新root-entry-doc.patch明确三层及rc8未三轮/未上架，不改Main版本模板或根签包。

`evidence/`保存实际报告/identity与已执行父代码/VM结果；旧NIGHT004不改。ROOT_CAUSE_NOT_ESTABLISHED和CLI/GPU/GUI/业务状态分开。

工具定向检查（不GUI）：

```sh
python3 -B -m unittest discover -s official_muse/semifinal/sprint005/zc03 -p test_tools.py -v
python3 -B official_muse/semifinal/sprint005/zc03/verify_memory_evidence.py
```
