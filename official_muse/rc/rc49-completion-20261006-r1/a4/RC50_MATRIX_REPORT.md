# rc50-r2 独立 Shell 启动矩阵

结果：FAIL。2026-10-06 自有端口8492完成10次新Shell进程冷启动和5次关闭应用后重开；冷启动8/10，重开5/5。没有跳过失败、追加重试或改变Host/预算。此结果不证明两台接收Mac、系统重启、模型语义或外部整链通过。

候选为 `official_muse/app/build/ui-memory-20261003/rc50-cold-synthetic-r1`；版本0.3.26-rc50，Root提供的compact为rc50-r2。compact SHA256 `15ba9ea00f55079a1243ca1dfab9b266b23e434855b69bd49cd13fb9d524d471`；Host SHA256 `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`。metadata commit为320540e66ddb9b03b22bc3872b533719e3595470；实际产品身份以验证过的bundle字节为准。

执行入口：

```sh
python3 official_muse/rc/rc49-completion-20261006-r1/a4/run_matrix_audit.py --candidate official_muse/app/build/ui-memory-20261003/rc50-cold-synthetic-r1 --out official_muse/rc/rc49-completion-20261006-r1/a4/cold-rc50-r1 --port 8492
```

wrapper调用现有 `official_muse/rc/startup/run_shell_matrix.py --cold-count 10 --reopen-count 5 --restart-count 0 --compact-evidence`。原脚本只读，SHA256前后同为 `bd11c0ba7c5883cdbb8958f7ff46fb40a048e376b398b6bd31ee5dbb270b9f3f`。额外审阅实际日志、启动输出与Label中的编译/语法/预算/根视图错误，保留原始判定，不扫描整段源码文本来制造错误。原report的wall_budget_ms=64是既有脚本字段，本轮未独立审计SDK数值；Host与配置未改。

失败记录：

| 轮次 | 观察 | 判定边界 |
| --- | --- | --- |
| cold-02 | SPLASH_COMPILE完成：115 chunks，total103.244ms，max_chunk23.987ms。随后eval line8701:96报script time budget exceeded，view=false；两条[E]为ui不存在和goal_input getter失败。会话焦点与可编辑输入未出现。 | UI初始化执行失败；不是source preparation失败，也不能把成功编译当作成功启动。 |
| cold-07 | 输入编辑、合成焦点和非空记忆已检查；切到邮箱后，驱动无法完成日历导航。无[E]、编译或预算错误。失败snapshot中日历Button仍存在，rect为[96,495,41,16]；现有click_scroll要求Button高度至少24。 | 导航可达性检查失败；未证实日历实际功能失败。保留FAIL，不通过放宽驱动阈值来改成绩。 |

10个冷启动PID互不相同：95070、95657、96331、96893、97451、98020、98614、99224、99795、774；5次重开均保持PID774。通过冷启动的首个实内容时间范围16.21–17.29秒，首个可编辑输入16.78–17.81秒；这包含Shell/App Hub启动，并非只测源码编译。冷启动指新进程，不清空OS文件缓存。

数据仅来自Root提供的合成seed：16个会话/256条消息、64条claims/65条sources、邮件基线64条。通过轮次实际编辑输入但不发送，并访问记忆、邮箱、日历、能力授权、设置、对话六页。最终所有受保护资料SHA与测前一致，安装源SHA一致，模型ledger仍不存在，主模型route为不可达的127.0.0.1:65534/v1且无fallback。未做模型调用、邮件发送、Calendar写入、生产资料替换或系统重启。

原始report、逐轮log/snapshot、首轮及所有失败PNG、两次exception与补充audit均在 `cold-rc50-r1/`；`SUMMARY.json`提供机器可读的数量、PID、完整性与证据SHA。最终仅退出已记录的自有PID774；端口8492释放。Root8493、候选、Host、模型与旧失败证据保留。桌面rc49交付包继续冻结，未用未通过的rc50替换它。
