# 当前冷启动 · rc10

同产品6fd5b54b/payload7cdfc751、Host938/SDK3f，新的30完整Shell进程启动、20应用重开、20Shell重启全部通过。非空16聊天/256消息/64记忆/65来源/64seen，六页、输入可编辑、焦点恢复和数据/ledgerSHA均核对。原64ms/20M/64MiB不提高，不清空历史或缓存。

| 模式 | 通过 | 首次可交互：中位 / 最大秒 |
|---|---:|---|
| 新Shell进程启动 | 30/30 | 14.729 / 18.882 |
| 普通Muse重开 | 20/20 | 9.241 / 10.089 |
| Shell进程重启 | 20/20 | 12.589 / 14.661 |

同rc10额外100次连续普通重开全部PASS，首次可交互最小8.652/中位9.389/最大10.210秒。每轮同样核对六页/输入/焦点/存储及ledger；首轮截图404保留，随后只抓第100次后原生窗口，Root已实际查看，不重开或重放动作。摘要RC10_REOPEN_100_SUMMARY.json，raw报告SHAeabaefced85fc8b953e8982c918c5cabc0f8fe328c649d75786f34d8826e502c。公开70摘要RC10_STARTUP_70_SUMMARY.json，原报告SHAdf8adb7409350b069a3c3bcf9619536937d7ceab2331699dc797732e24afa66f；每模式首份真实截图保留，无截图失败。启动观测不是OS重启/清缓存/真实服务成功；原生[I]ui-hang信息保留，CPU并发影响不隐去。T20仍PARTIAL，完整2h、新Calendar Host/clean/跨机器门槛独立。

---

# 历史冷启动 · rc9

同一1c9f3b46/0.3.26-rc9/source4c970e04、Host938/运行SDK3f：第二轮30冷启动、20普通重开、20Shell重启全部完成，driver exit0。额外100次连续普通重开也完整通过。每次均检查16个非空聊天/256消息/64记忆/65来源、六页、输入、焦点和受保护SHA/模型账本。没有提高原预算、清空历史或缩小测试数据。

| 模式 | 通过 | 首次可交互秒：最小 / 中位 / 最大 |
| --- | ---: | --- |
| 完整Shell进程启动 | 30/30 | 11.224 / 12.021 / 13.419 |
| 普通Muse重开 | 20/20 | 8.409 / 8.897 / 9.407 |
| 额外Shell进程重启 | 20/20 | 11.300 / 13.904 / 17.609 |
| 额外连续Muse重开 | 100/100 | 8.452 / 8.997 / 9.649 |

公开摘要：official_muse/rc/startup/RC9_STARTUP_70_SUMMARY.json、RC9_REOPEN_100_SUMMARY.json。70次每模式首张可见PNG保留；100次首张capture返回404原记录保留，随后只补抓第100次后真实窗口，没有补造首张截图。Root已实际查看该最终PNG。其余成功快照只去重精确相同源码字段，检查内容不减少。

首轮ENOSPC的30冷/13重开和19样本542.154秒soak失败保留。cold指新Shell进程，不清OS文件缓存；100次是同一Shell进程内重开，均不等于电脑重启或真实外部服务成功。原生[I]ui-hang日志仍保留；两小时、Calendar新Host/clean/电脑重启门槛独立，T20仍PARTIAL。

---

# 历史 rc8 冷启动结果

产品 a80bd019 / source f2c2ce15，运行 Host938 / SDK3f。2026-10-05 05:44 北京时间，30次完整进程启动、20次普通重新打开、20次Shell进程重启全部通过。每次加载16个非空对话、256条消息、64条记忆、65份来源及64个已见合成邮件；检查六页、输入编辑、焦点恢复、受保护数据与模型用量SHA不变。没有清空历史，没有提高64ms callback、20M指令、64MiB堆预算。

| 模式 | 通过 | 首次可交互秒：最小 / 中位 / 最大 |
| --- | ---: | --- |
| 完整Shell进程启动 | 30/30 | 11.255 / 11.938 / 12.946 |
| 普通Muse重新打开 | 20/20 | 8.507 / 8.838 / 9.747 |
| 额外Shell进程重启 | 20/20 | 11.578 / 12.063 / 12.670 |

原报告SHA、输入身份、完整数据数量见 official_muse/rc/startup/RC8_STARTUP_70_SUMMARY.json。每轮检查及日志原件在 evidence/rc8-a80-final-70-r1；每个模式首份可见PNG保留，其余快照只去重完全相同的源码字段，SHA及结构保留，未删除旧失败。

cold仅指新Shell进程，不清OS文件缓存，不代表电脑重启。原生theme初始化出现过[I] ui-hang采样，不能称完全无暂停；业务启动检查没有[E]、source preparation failed或no root view。Calendar布尔桥修复尚未进入该Host；两小时、真实账号和OS重启另列，T20整体仍PARTIAL。

历史rc6第二次完整进程启动源码准备124.194ms失败、rc7矩阵创建目录ENOSPC未执行，以及下方原诊断/V15结果均保留原身份。不能把新70PASS覆盖其原记录。

---

# 历史诊断与旧候选支持

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
