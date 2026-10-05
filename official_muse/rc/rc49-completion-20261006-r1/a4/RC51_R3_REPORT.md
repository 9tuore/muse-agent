# rc51 最后一次独立启动矩阵

2026-10-06最终结果：矩阵FAIL，产品UI验收PARTIAL。原10cold+5reopen尝试完整执行，cold7/10、reopen5/5；不追加重试，不把旧r1/r2或当前失败改为PASS。

固定候选 `official_muse/app/build/ui-memory-20261003/rc51-cold-experiment-r3`；compact SHA256 `ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da`，Host SHA256 `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`。launcher来自6ba4af24，SHA256 `04a23e0c659f2fa07f7ed1a8aedd741592d4b5aca24bbf05b1aa8d9fafa426fe`，结束后保持一致。Source/Host/模型/预算未改，原单次launcher子进程40秒限制保留。

执行：

```sh
python3 official_muse/rc/rc49-completion-20261006-r1/a4/run_matrix_audit.py --candidate official_muse/app/build/ui-memory-20261003/rc51-cold-experiment-r3 --out official_muse/rc/rc49-completion-20261006-r1/a4/cold-rc51-r3 --port 8492
```

启动前8492为空，seed受保护文件与r2逐字节相同，主模型route127.0.0.1:65534/v1且无fallback。主矩阵脚本SHA前后bd11c0ba7c5883cdbb8958f7ff46fb40a048e376b398b6bd31ee5dbb270b9f3f。wrapper SHA前后44a2da8194551ba1bac2d315bddd961854cc047d606c4b3367d0d5ee7abdf0d2；本轮前仅改善最终清理的quit响应丢失/TCP关停确认，未改任何case、页面、输入、数据、ledger及编译/E错误门槛。

| 轮次 | 观察 | 判定 |
| --- | --- | --- |
| cold02、09 | launcher子进程超过40秒，snapshot HTTP404，未取得完整startup log。 | FAIL；超时具体位于关停、App Hub启动或后续哪一步未定位，不能声称无budget/E或写成产品编译失败。 |
| cold03 | launcher line80报Previous candidate Shell is still running，旧端口未确认关闭，没有执行新open；snapshot HTTP404。 | FAIL；保留真实关停失败，没有提高时限或复用旧进程。 |
| cold01、04–08、10 | 实际新进程、合成焦点、可编辑输入、非空记忆和六页检查完整通过；数据/ledger保持。 | 7次完成有效cold，不冒充10个独立产品启动。 |
| reopen01–05 | 关闭Muse回App Hub后重新打开，全部原检查通过。 | 5/5；同一Shell PID41984，没有进程替换。 |

7个已证实不同的有效cold PID：35256、37022、37504、38404、39116、40013、41984。通过cold的首个实内容时间18.81–49.37秒，首次可编辑输入19.52–50.14秒；包含旧进程退出/App Hub启动/UI恢复，不是只有源码编译，40秒门槛仅约束launcher子进程。冷启动不清空OS文件缓存，未做OS重启。

所有完成case日志中未观测到[E]/budget/source-preparation/compile错误；失败case缺少log，不构成错误不存在的证明。原report/audit、逐轮launch/exception/log/snapshot及首轮PNG、SUMMARY.json完整保存于cold-rc51-r3/；原始runner与wrapper都exit1，整体FAIL不能用后续通过覆盖。

合成数据来源不变：16会话/256消息，64 claims/65 sources，邮件基线64。最终所有受保护SHA和安装源SHA一致，model ledger仍不存在；未做模型提交、邮件发送、Calendar写入或生产资料替换。最终仅对已记录自有PID41984发quit，独立TCP确认8492释放；ps验证所有已记录PID均已退出。Root8493、Host、模型、候选及全部唯一失败记录保留。

当前边界：UI有12次完整通过的case，但完整矩阵仍FAIL，2接收Mac/模型语义/外部整链均不由此证明。既有rc49小模型诊断0/2保留；本轮没有复测模型。桌面rc49包没有重包或删除。Root可继续其原任务，A4本轮停止native测试；后续需定位40秒超时和端口关停，不以放宽预算/时限掩盖问题。
