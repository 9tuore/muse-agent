# rc51 ed4874 串行复测

结论：**本轮3组PASS，12个检查组通过**。严格按Root通知在A4矩阵停止后串行运行，990×380通过后才执行990×539和412×892。没有增加其他实验或重复宽窗。

| 请求 | 实际尺寸 | 结果内容验证 | 其余交互 |
|---|---|---|---|
| 990×380 | 990×380 | 右栏折叠重开后可见，切页返回仍可见 | 4检查组PASS |
| 990×539 | 990×539 | 同上 | 4检查组PASS |
| 412×892 | 412×813 | 结果页打开后合成标题/结果可见，返回后输入恢复 | 4检查组PASS |

全部验证16条完整标题及历史内容保持、首尾选择、删除预览取消、输入真实编辑回读、空消息发送校验、长正文滚动、左栏折叠恢复和邮箱/日历/记忆/更多→操作记录导航。宽度990的两个窗口另验证右栏折叠恢复。窄窗右栏自动隐藏，使用实际可见的“结果”入口验证独立结果页，不声称窄窗显示桌面三栏。

## 原失败与源码区别

原`visible-990x380-r1`的35秒启动失败仍完整保留，未覆盖、未清除、未推断根因。本轮一次成功不证明cold稳定性，更不覆盖A4的10+5结论。

按Root最新指定，本轮使用 `official_muse/app/build/ui-memory-20261003/rc51-cold-experiment-r3/bundle/main.splash`，SHA256 **ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da**。原r1和此前宽窗使用readable源5c182b67…；它们不是同一SHA，不能把本轮说成对旧失败的同字节重放，也不能把旧宽窗写成本轮ed4874重新测试。

脚本保持未改，SHA256 `eba665df1285ed3f1116cf3deeffafbf04e8495a2e09068b3df60f9e8b9695ae`；Host保持packaged card-host `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`；启动等待仍为35秒，预算未改。来源绑定见R2_SOURCE_BINDING.json。

## 退出与边界

每组的exit-receipt.json都在所属进程退出后记录8517未占用，且source SHA仍为ed4874。最后窄窗退出记录时间 **2026-10-06 03:22:25 +08:00**。此后不再启动native测试，交还串行窗口给Root/A4。

这是隔离card-host fixture，不是Root8493 Shell。合成结果标题/正文明确标注“未执行系统动作”“不是真实执行回执”，只证明挂载后渲染与恢复；host.request全部拦截，只有mail.accounts/calendar.status调用记录，无模型调用、邮件发送、系统日历写入。未改源码/Host/主profile/预算，未push。

截图：三组目录的result-reopened.png展示重开后的真实合成内容；expanded/collapsed/long-top/long-bottom及navigation快照保留。新证据见R2_EVIDENCE_SHA256.json，旧REPORT/SUMMARY和旧证据哈希保持不变。
