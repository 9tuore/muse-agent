# rc50 / rc51 本轮收口报告

状态：**PARTIAL**。原二十项及外部完整整链未全部通过。用户睡前要求后续不申请权限，已沿用现有授权执行；未代填本人收件声明、批准新日历事件或正式提交 App Hub。

## 版本与实际范围

- 分支 `codex/muse-rc-finalization`；rc50 产品 `156a58b5`，rc51 产品 `6b46c3c8`。
- rc51 readable `5c182b67d91182350388b726db64b97dc588be089e9f43951284fa899e0d99f1`；compact `ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da`；官方 token 序列 98,560 个完全相同。
- Host `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3` 不变，没有新建 Runtime、改权限或提高脚本预算。
- 稳定 0.3.25、旧独立安装、生产资料、旧 Tag 和未提交 baseline 保护。所有新资料仅在已有隔离候选目录。

## 最小修复

1. 首次新对话持久记录补齐 proposals、project、owner 和 goal 字段。首次真实保存失败的缺字段原因有生产函数 fixture 证明。
2. 邮件与日程关联先保存 link，再在另一短回调记录 Goal 活动，保持账号、聊天、项目、归属、Goal/revision 和来源守卫。
3. 左栏快捷区按窗口高度收缩，给矮窗口的历史列表留可用空间。
4. 主界面仅首次挂载；恢复继续走原有分段逻辑。普通 redraw 仅渲染当前内容，输入和滚动控件保留。
5. 测试启动器处理已送达 quit 的 404/连接中断，仍独立确认端口关闭；quit 等待降为 5 秒，整体 40 秒不增加。首次端口占用拒绝误复用旧进程。
6. 打包使用明确 ZIP 等级 9；可将完整源码与历史证据整体压为 tar.xz，解压后核对全部 SHA、权限和文件集合。

## 已执行验证

| 验证 | 实际结果与边界 |
| --- | --- |
| 首次对话保存 | 旧字段 fixture 3 PASS/1 FAIL；修后 4 PASS。不是外部服务成功。 |
| rc50 邮件来源关联 | 实际生产函数 4 PASS，source/link/audit/model queue 均核对；零邮件发送、零 Calendar 写入。 |
| rc50 实装与重启 | 32 个安装前数据文件保护；5 个非轮询文件和模型 ledger 不变，8 条来信 key/status/body 投影保持；轮询文件按真实活动变化。 |
| rc51 界面 | 宽 1400×760、普通 990×539、矮 990×380、窄实际 412×813 的输入、历史首尾、删除预览取消、长文滚动、折叠、结果及入口检查通过。宽为 readable fixture，后三个为等价 compact fixture；不是同字节原封外部全链。旧矮窗启动失败仍保留。 |
| rc51 Root 实际启动 | 隔离满历史 fixture 的六页/输入检查通过；真实已授权资料目录首次 launcher 40.017 秒超时，之后实际 App Hub 打开 Muse 成功。该超时根因未定，不与 fixture 通过混为一例。 |
| 冷启动矩阵 | rc50 8/10 冷、5/5 重开；rc51 r1/r2 失败完整保留。最后 r3 冷 7/10、重开 5/5，矩阵 FAIL：两次 40 秒启动器超时、一次旧端口未关闭；失败没有足够日志，不臆断具体启动阶段。 |
| rc51 真实内部任务 | 同一 Goal 显式两个计划版本，各批准一次、各产生一条 completed Run、两条资料结果和读回。v1 的模型调用发生在 Chat 生成候选；显式 v2 更新后实际 Goal 模型建议 42 字，再批准保存。模型不是在批准后调用，不标该严格顺序通过。v1 完成时未提交输入保持。 |
| rc51 同候选 Shell 重启 | 正常重启启动器 exit0；7 个受保护文件逐字节保持，8 条提醒投影不变，9 Goal/13 Run/17 Action 不变，模型 ledger 不变，零自动重放、零 [E]。这是 Shell 进程重启，非电脑重启。 |
| rc51 另一已有聊天 | 同项目与归属的另一条已有聊天，真实 M3 正确召回两条说明及两个结果路径，引用包含两条新结果记忆。16 条聊天已满，本轮没有删历史腾出新空聊天；不称新空聊天测试。资料摘录标记“未核事实”，保存动作仍是 verified_result。 |
| 官方模型来源候选 | rc50 使用真实 MiniMax-M3 一次调用生成准确 10 月 8 日 15:00–15:30 候选，1,834 输入/3,854 输出 tokens，非估计。来源邮件是 rc49，不拼同最终链。 |
| 真实目标日历查询 | 只查询“工作”日历的明确半小时，0 冲突；一条实际核验时段符合“至多两个、不足不凑”。未创建事件。 |
| GPT 第二通道 | 一次无 fallback 的配置通道返回 HTTP200、text/html、1,166 bytes，Host provider error；非 JSON/SSE，不猜测登录页。仍 BLOCKED。 |
| 内置本地模型 | 官方 Host 严格同题两题 0/2 正确；真实 HTTP token 化提示复放得到同输出，失败在模型生成，非 UI 解码。只作基础离线模型。 |
| Hub 标准检查 | 最终 gate-rc51-release-r2 六文件与源码 bundle 完全相同；扩展 check/scan/catalog PASS。锁定官方原版 Hub 对同 rc51 实际 check exit1，唯一拒绝项是未知 calendar capability；不是上游准入、正式发布或独立评审。 |
| 打包小型验证 | 普通与 solid 两模式 CRC、SHA、中文路径、755、符号链接及 macOS 自带 tar 解压 PASS；5 个负例拒绝。真实大包结果另列，不能由小样推断。 |

## 原二十项的判定边界

定义原文见 [SOURCE_ORIGINAL20.md](a3/SOURCE_ORIGINAL20.md)，逐项审查见 [REMAINING20.json](a3/rc51/REMAINING20.json)。后者是 03:11 的只读审计快照，不覆盖后续成功或失败。

- T08 的一条已核验时段符合原条件；此前“必须两个替代”是错误加严，已纠正。
- T19 原生两行等高方案已获本人确认；原条件不要求每个矮窗同时显示四条完整历史。实际窄窗高度不冒充 892 或手机实测。
- T17 尚缺有效 GPT 模型 API 与相同安全题集成功证据；自定义地址本身不算失败原因。
- rc51 内部任务、读回、结果记忆和 Shell 恢复已真实补证，但其调用顺序及另一已有聊天范围如上，不能替代外部整链或严格的批准后模型节点。
- T09/T10/T15/T18 尚缺同一最终候选的新系统创建、原事件改期、读回后起草/独立发送、重启及跨聊天结果召回整链。
- 新源邮件仅由服务受理与 IMAP 同步证明，未写成“本人已收件核对”。新日历候选未批准，零写入。旧事件批准不套用新事件。
- OS 重启、两接收 Intel Mac、正式 publisher 登记和独立 App Hub 审核仍未完成，测试启动器或文件检查不替代它们。

## 证据入口

- [rc50 修复范围](SCOPE_RC50.md)、[rc51 修复范围](SCOPE_RC51.md)、[受影响函数审计](a3/rc51/SOURCE_IMPACT.json)
- [rc51 UI 四尺寸](a2/rc51/FINAL_REPORT.md)、[rc50 矩阵](a4/RC50_MATRIX_REPORT.md)、[rc51 最终矩阵](a4/RC51_R3_REPORT.md)、[rc51 r2 失败分类](a4/RC51_R2_REPORT.md)
- [真实目标日历只读](REAL_TARGET_CALENDAR_QUERY.json)、[rc50 恢复](RC50_REAL_RESTART.json)、[本地 Gate 身份](compliance-rc51/GATE_IDENTITY.json)
- [官方原版 rc51 实际检查](compliance-rc51/UPSTREAM_HUB_CHECK_RC51_PROVENANCE.json)与[完整拒绝输出](compliance-rc51/UPSTREAM_HUB_CHECK_RC51.txt)
- [rc51 实机内部任务](RC51_LIVE_REGRESSION.json)、[同候选恢复](RC51_REAL_RESTART.json)、[跨聊天召回](RC51_CROSS_CHAT.json)、[真实启动超时](RC51_LIVE_LAUNCH.json)
- [压缩补丁小型测试](a3/solid-source/RESULT.json)、[Root 实验原结果](MOUNT_EXPERIMENT_RESULTS.json)、[启动驱动故障](RUNNER_FAILURE_AND_FIX.md)

## 当前交付

实机 rc51 内部回归及最终 r3 矩阵已完成。新版[96 秒中文配音视频](media/rc51-public/Muse-rc51-demo.zh-CN.mp4)、字幕及封面已制作；真实时间轴保留 22 秒连续段和一次 2.18 秒采集间隙。全部 37 张准备画面及 13 张成片关键帧核对，完整解码、音轨与字幕时段通过；未做听感审听。视频 2,439,624 字节，SHA256 `5cecf600c6d4a18b0217a0f08f97b76648598a559b1b69cb80b0003375361f21`。Root 独立确认摘要与两个关键画面，实际产物见[媒体交付记录](media/rc51-public/DELIVERY.json)。

冻结源码与桌面包继续收口，实际结果按 DELIVERY.json 更新。既有 rc49 媒体和小于 500MB 的包保留原身份，不改名冒充 rc51。正常 GitHub 同步已授权；不 force、不动旧 Tag、不正式提交 App Hub。
