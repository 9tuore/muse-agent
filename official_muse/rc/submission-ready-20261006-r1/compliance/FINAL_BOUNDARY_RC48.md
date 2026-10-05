# rc48 最终证据与官方边界

**状态：PARTIAL。** 本文只核对和引用已有证据，没有运行新测试、模型调用、系统动作、Hub检查或发布。它补充 rc45 审计，不改写历史结果，不表示 UI_PARITY_PASS 或正式上架通过。

## 版本身份

- 工作区：`/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松`；分支 `codex/muse-rc-finalization`。
- 产品：`0.3.26-rc48`，提交 `89bfd3996b5c2727242b600cd02d075bede24ef4`。
- 可读源码 `official_muse/app/source/main.splash` 与 `readable-rc48-r1/main.splash` SHA256 均为 `179fd6b6fc8e54c55fe7627af2eb1ed117d8ce34bdbbc93cd491456404b0d46d`。
- 实际 Gate bundle 入口 `gate-rc48-r1/bundle/main.splash` SHA256 为 `fcf9408f8e153129dff9614c91b0fdde69f214f0740cc88189095ba64157fb0f`。Root 的 live/restart 记录使用 source_sha256 标记这个运行载荷摘要；不要与可读源码摘要混用。
- 运行 Host 由已有 `RC48_LIVE_TASK.json` 记录为 `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`，与 rc45 审计身份相同；本次没有重建、替换或重新实测 Host。

## 当前候选真实运行（引用 Root 已保存证据）

[RC48_INSTALL.json](../RC48_INSTALL.json)：六项安装 bundle 文件均匹配；记录中的全部安装前私人状态保持。此项不等于第二台 Mac 安装验收。

[RC48_LIVE_TASK.json](../RC48_LIVE_TASK.json)：当前候选实际启动，model.complete 单次响应成功，known_usage=true、estimated=false，1178 input / 879 output tokens；宿主报告请求 fast、实际 class=strong。模型先生成候选，随后形成 Goal `1791221504-3719825078`，同 Goal 的批准、storage write、readback、结果记忆有活动记录。Run completed，结果两个条目，产物 SHA256 `5e32cc0163e82f8f7e86279735989c6e5bb278bc3bfe7e2a4e425dc8858942b5`。普通任务的结果界面核验标记 true。模型回执 goal_id 为空，属于建 Goal 前的候选请求，不虚构成 Goal 内再次调用模型。没有新增真实 Mail/Calendar 写入。

[RC48_RESTART.json](../RC48_RESTART.json)：同候选 Shell 重启后 goals、memory、chat-sessions、mail-draft、calendar-state、model-ledger 六项及 task-result 保持；chat_ready/project_visible=true，errors=[]。activity 与 mail-watch **不相同**，因此不能写成全部状态逐字节不变。记录明确重启没有新增模型、邮件或日历写入；本次没有重跑或补充解释其变化原因。

## 夹具与历史证据复用范围

- [chat-restore-r1/report.json](../chat-restore-r1/report.json)：valid_full 5/5、invalid_final 5/5；属于生产函数配合合成 transport/资料的10项检查，覆盖256消息完整校验及坏尾条拒绝。测试报告 source SHA 为 `ad6c3c4272ede0f98a26b4404c4c4f1170e01b3583d0705971785a7b6a8e6317`，不能替换为最终179fd6b6的全产品测试身份。rc48产品提交是启动校验批次8→2，不表示删除尾部校验。
- [retest/REPORT.md](retest/REPORT.md)：两套修正后的旧测试分别在 rc46、rc47 各27项，共54 fixture断言；不升级为 rc48 真实模型或系统日历验收。
- rc37/rc41/rc42/rc45 的邮件、EventKit改期、本人收件及清理是**跨版本真实链**。当前rc48普通任务/重启证明不能拼接成同最终版本从头完成外部全链。
- [OFFICIAL_REQUIREMENTS_AUDIT.md](OFFICIAL_REQUIREMENTS_AUDIT.md)、[UPSTREAM_BUILD_PROVENANCE.json](UPSTREAM_BUILD_PROVENANCE.json)及原rc45日志保留。规则读取、上游闭合能力列表、SDK锁和原版审计工具来源可引用；rc45包清单、签名、平台试用、扫描或私有配置的结论不能自动转成rc48验收。

## Hub：本地扩展与原版必须分开

[gate-rc48-r1/check.txt](../gate-rc48-r1/check.txt) 文本为本地扩展 Hub `PASSED`，授予 calendar/glance/mail/model/storage，hosts为空，storage 16777216 bytes，agent none。它是本地演练预检，不是独立 reviewer 或官方目录采纳。

[UPSTREAM_HUB_CHECK_RC48.txt](UPSTREAM_HUB_CHECK_RC48.txt) 文本明确 `REFUSED`，唯一列出的拒绝为 unknown capability `calendar`，没有列出 digest/signature 错误。Root使用此前核验的公钥执行原版检查；本文只读取日志，没有重新执行。该日志未保存可独立确认的进程退出码，最后 shell 打印可能覆盖退出状态，故本文件**不补造 exit=1 或 exit=0**。

审计工具基于锁定上游 AppHub `e8601b80ce104db2e48208094714bdcffdce6b5a`；其构建来源记录说明 crate 源码未改，但独立审计 workspace/Cargo.lock 有已记录的解析调整。不能称最新 main 的 CLI 已执行。当前运行的是含 Calendar 本地扩展的配套 Shell/Hub，不能称官方原版 Calendar 已准入；没有 Rinx 验收或正式 App Hub 发布证明。

## 仍未通过的整体门槛

最终单版本真实邮件/日历全链、第二模型完整独立验收、接收机/系统重启及完整产品/UI矩阵仍依相应报告保持缺项，不能因本次文档核对升级。旧独立.app、用户数据、Secret、主README和他人改动未修改；本次仅本地提交本文，不push、不签名、不发布。
