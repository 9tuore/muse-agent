# rc25 侧栏与剩余链窄域复核

状态：**NARROW_FIXTURE_PASS_VISUAL_PENDING**。完成：2026-10-05T17:58:20.988082+08:00。

## 版本与现有Host

- frozen readable-rc25-r1：`da6239fab0c0f5422a941aa005369eeb7adf8f721cfb029bc9f82219b147c0d2`。
- 本次压缩及实测compact：`6daa7c0493ee5a7bfed53313896e4782531109e5853d322990672a152520147a`。
- manifest：`0.3.26-rc25`；除version/integrity，其余配置与rc24相同，未新增授权或预算。
- 可用实际Host：`/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松/official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host`；SHA `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。已确认可执行。已被清理的默认路径没有使用。

该CardHost与A2之前fixture锁定一致，**不等于Root针对Dock调整的新Shell/Host**。这里不验证Dock/窗口边界。

## 本次实际窄fixture

真实CardHost，生产 `chat_request_delete` / `chat_select_session` / `chat_save` 和隔离fs；渲染、根widgets、Host transport沿既有fixture替换。**25条生产断言全PASS**，Python再次读持久主文件，16独立ID、全部长标题/消息及最终所选ID符合预期。

准备16个合成长标题聊天，每个独立scope和消息；分别选目标索引15、7、0执行：

1. 删除预览绑定准确目标，不改变当前选择/消息/主文件/备份。
2. 执行与真实取消on_click相同的 `chat_delete_pending=""; redraw()` 表达式；所有16聊天和持久文件不变。
3. 选择该聊天后，ID、所属消息、project/owner正确；全局记忆、来源、Goal保持。

无效ID预览拒绝。未调用 `chat_delete_session`，未确认删除任何资料；0 Host调用、0 Run/Action。取消是fixture执行同一handler表达式，**不是点击真实UI按钮**。真实窗口滚动/长标题布局/可点击面积不在本测试中。

## 字节绑定与可复用清单

相对rc24整源码差异精确只有 `history_list padding: Inset{right:12}` 与About版本号。`BYTE_BINDING.json`附23个当前真实函数的SHA，以下函数全部字节相同：

| 范围 | 当前源码护栏事实 | 可复用/限制 |
|---|---|---|
| Mail投递核验 | `mail_preview`精确snapshot、`mail_send_confirmed`确认及防重复；`mail_verify_received`仅accepted状态、邮件中匹配测试ID、受持久action约束，记录明确的本人声明 | rc25没有因padding而改这些逻辑；既有同任务证据可复用。**SMTP受理不是投递；本人声明不是Host自动证明**。不能凭字节一致新增真实投递PASS。 |
| 手写草稿保护 | `mail_watch_edit_body`标manual并清proposed/preview；`mail_watch_adopt_proposed`要求shown/base正文主题及intent仍匹配；`mail_watch_send`要求显示精确草稿与持久request防重 | 5相关函数含status/model_draft字节一致；可复用已有明确源码绑定证据。此轮未实调草稿模型或发信。 |
| Calendar同项关联 | `mail_link_calendar`、generation/current、finish/link、approval/execute、`mail_finish_linked_result`字节一致，仍将邮件来源/Goal/事件/request联系起来 | 既有rc17同来源scope/ID及恢复fixture报告保留；不是rc25重跑真实邮件→日历→邮件链。旧报告版本须按其原SHA表述。 |
| Chat全局记忆 | `gm_access`、`gm_score`、`gm_context`、`chat_memory_command`、wrapper、reply_context_valid完全相同 | rc24六组106断言/25读回中的授权纳入、跨归属排除及不修改持久消息可复用；rc21/23/20报告保留，不全套重跑。 |
| 聊天删除/选择 | request_delete/select/delete_session字节相同 | 仅预览/取消/选择在rc25新测通过；确认删除不在本轮范围。 |

这张表区分源码护栏、历史fixture和真正live。源码不变不自动把历史live更新为当前成品验收。

## 真正待补项

1. Root在真实最新Shell窗口做最大化/Dock及侧栏滚动条遮挡几何验收；fixture不看native窗口，不能给视觉PASS。
2. 同一16长标题真实UI的“删除”点击目标、可见取消按钮和不同聊天切换，由Root唯GUI操作员验收；A2逻辑结果不替代截图/真实点击。
3. 若本轮验收要求新同任务Mail投递终点，须在已授权本人收件端核对并关联准确request/test ID；不能由A2点击本人核对或把accepted当投递。此轮不操作8493/8484，不新增真实发送。
4. 手写草稿若要当前成品live证据，需要当前产品自己的晚到模型/用户编辑竞争实际演示；此轮只字节复核，不能说已重新发生。
5. Calendar same-item若要当前成品同任务full-chain，应绑定同一个Goal/source/event/mail action的读回证据；当前表不造出这一新链。
6. 实际GPT/M3格式稳定性仍以Root本轮真实问题回传为准，A2不调用真实模型或整套题集。

没有为上述项添加新功能、权限或任务测试。本次single Host已退出。旧fixture/失败记录未动；未改主源码/Host/Git/安装/共享文档/用户资料或凭据。

## 文件

`rc25-first-r1/sidebar/first/report.json`、runtime.log、隔离state及summary；`SOURCE_DIFF.patch`、`BYTE_BINDING.json`；`PUBLIC_RESULT.json`；`probe.splash`/`run.py`。
