# RC 冷启动实测定位

诊断时间：2026-10-04 22:04–22:11 北京时间。真实 OctoSense Shell/App Hub，既有 Host SHA `0fd9936126acad3a5c61ac1e7a477ba2c9393d740572ec517472f52da9181047`。诊断源码为计时插桩副本，**不计入最终 RC 的十次冷启动**。没有提高64ms callback、20M指令或64MiB堆预算。

## 数据和方法

16个合成聊天，256条非空长消息，200个已见合成邮件ID，非空Goal/result/calendar状态。先用6条记忆/7来源/6遗忘记录；再按已有核心上限扩成64记忆/65来源。原生产资料没有覆盖。

`time_now()`包围真实恢复函数；fs计时写入只发生在诊断副本。下表时间含被调用函数的时间，不能把嵌套项相加。UI construction测量原生root对象构造；字体绘制/首屏首次可交互由最终cold runner另外测量。

## 64条记忆场景

| 阶段 | 总耗时ms | 最大单次ms | 调用数 |
|---|---:|---:|---:|
| ui_construction | 0.815 | 0.815 | 1 |
| ui_layout_boot | 0.250 | 0.250 | 1 |
| notification_boot | 0.050 | 0.050 | 1 |
| chat_boot_data | 41.756 | 41.756 | 1 |
| core_boot_activity | 3.872 | 3.872 | 1 |
| core_boot_memory | 10.849 | 10.849 | 1 |
| gm_boot | 6.666 | 6.666 | 1 |
| gm_boot_part | 1084.312 | 24.896 | 65 |
| gm_finish_boot | 6.376 | 6.376 | 1 |
| core_boot_goals | 0.516 | 0.516 | 1 |
| calendar_boot | 0.697 | 0.697 | 1 |
| redraw | 3.848 | 3.848 | 1 |
| boot_restore | 8.165 | 8.165 | 1 |
| mail_watch_boot | 1.498 | 1.498 | 1 |

从诊断源顶层开始到mail本地初始化完成：3642.073ms（包括现有异步分批校验的timer等待）。Splash parse日志约35ms/32chunks；具体原始log保存在 `official_muse/rc/startup/evidence/profile-64/log.json`。

- storage/chat/activity/memory/goals/calendar本地恢复：同步短片段；聊天本地历史与可用输入属于首屏必要内容。
- gm_boot_part：异步分批，每批2条，65个片段；最大约25ms。记忆校验必须最终完成；不是忽略记忆。
- mail_watch_boot：本地baseline恢复同步，mail.accounts及后续同步为异步Host回调；无账号/服务暂不可用仍可打开界面。
- UI构造/结果卡重建：分别实测root构造和boot_restore/redraw，时间包含其嵌套操作。
- model/provider初始化：启动函数未调用model.complete或model.budget；没有首次模型请求，记录为启动阶段未执行，不能捏造0ms推理性能。模型配置由官方Host在首次相关请求使用。

两组启动没有 `[E]`、运行预算超时或损坏恢复提示。没有为得到结果清空历史或禁用服务。最终T20仍需对实际final source/bundle/Host/Hub执行10完整停止启动+5普通重开，并比较每次存储哈希和动作数量；本定位报告不能代替该门槛。

## 保留的诊断失败

第一版计时包装函数写在原实现前面，Splash闭包作用域不能找到rc_impl_ui_layout_boot；保存原包/日志，随后将包装函数放在已有函数定义之后解决。预算只读探针第一版直接序列化Host result对象失败，后改为仅序列化公开is_ok/data/error字段。这两项为测试插桩错误，没有计入产品启动PASS。

## V15最终70次实测（2026-10-05）

产品b48618ac/source5092becd，实际暖构建Host938ba58a/SDK3f1bbb4e；新92b1Calendar桥源码尚未进入此Host。真实可见Shell载入16对话256消息、64记忆65来源与64已见合成邮件，全部六页、可编辑输入、完整存储SHA及model ledger核对。

| 模式 | 完整通过 | 首次可交互秒：最小/中位/最大 |
| --- | ---: | --- |
| 完整Shell进程冷启动 | 30/30 | 12.154 / 13.093 / 24.844 |
| 普通Muse重开 | 20/20 | 8.709 / 9.085 / 9.427 |
| 显式Shell进程重启 | 20/20 | 11.909 / 12.557 / 13.641 |

cold是完全替换Shell进程，不清OS文件缓存，不是电脑重启。原64ms/20M/64MiB预算未提高；30次含首次内容23.543秒、可交互24.844秒的慢样本，不隐去为秒开。原V9第19次Memory、V12第16次Chat、V13b第二次Memory渲染和V14搜索预算失败原样保留；首次目标源码仍失败后才做最小修复。2h与真实账号的长期运行另见OVERNIGHT_SOAK.md，不能把70次替代。
