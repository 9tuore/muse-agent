# 当前源码与维护边界 · rc9

产品1c9f3b46；可读9d01484c / compact4c970e04，官方91,195 token相同。OctoScript/Splash、Makepad和官方model.complete/存储/权限/宿主服务保持，没有第二Runtime。可读入口540,440字节，430个命名函数；正则扫描不是AST、没有宣称不存在死代码。

rc9只把既有用户时段完整性检查移到模型payload校验之前；其他函数字节不变，仅Settings版本递增。15变体53检查、两个真实模型D05准确追问通过。rc8邮件未指定to/subject保留的16变体86检查及两个真实模型E04通过，原失败保留。修改及版本字节绑定见RC9_DELTA_BINDING、RC8_DELTA_BINDING。

最新清理164份旧候选分发PNG：逐Git字节/SHA/长度、fresh lsof核对，原始测试截图和失败记录不删。操作前后可用增加316,456,960字节，逻辑大小507,084,720不能算实际回收。更早66份分发副本的203,149,312字节记录及另8份12,378,112字节记录保留；16份共享extent操作未获得可靠独立回收量。所有资源可由已记录Git路径恢复；不得把已移除副本说仍原样存在。

随后173份rc5–rc8分发副本核对为稳定Git提交d8a2989的同一公开主图，逐文件字节、SHA256、长度及占用重新检查后移除。该次可用空间实测增加40,439,808字节，逻辑42,581,528字节单独记录；运行中的用户窗口、当前rc9资源、原始截图、失败证据与旧完整ZIP未动。公开恢复依据见official_muse/rc/startup/RESOURCE_RECOVERY_PUBLIC_SUMMARY.json。

一次成功历史snapshot的无损归档尝试ENOSPC，未删除任何原始文件，失败archive与记录留本机。完整Host600MiB门禁保持，当前运行SDK3f不含源码SDKda的Calendar布尔桥。以下为历史修复依据和模块所有权，未换成rc9全部重跑。

---

# Muse 源码结构检查

状态：修复与验证进行中。以最终候选记录覆盖本页的临时摘要，不把代码行数作为完成标准。

## 实际执行入口

官方产品入口是 `official_muse/app/source/main.splash`，交付为其等价 compact `official_muse/app/bundle/main.splash`，由 OctoSense/App Hub 的 Makepad/Splash isolate 执行。旧 `app/` Python 实现保留为独立版历史，不是当前官方包的 Runtime，未修改。构建、测试的 Python 脚本只负责工具流程。

当前可读入口540440字节、430个命名函数（当前扫描值）；不把扫描次数当作完整AST或无死代码证明。已有全局记忆、来信处理、页面适配模块由 `sync_modules.py` 按标记嵌入，compact只移除字符串之外的注释和空白。生成入口与模块副本是构建关系，不能盲目删除其中一方。

## 本轮有依据的修改

| 问题 | 证据 | 最小边界 |
| --- | --- | --- |
| 同一记忆scope被重复验证，64条更正触发指令/时间预算 | A3 RC2/RC3/RC4单动作与原日志 | 256项有界结构缓存；每次仍检查未知字段；授权、用户、账号与遗忘检查不缓存 |
| 更正重复整库canonical转换 | `gm_correct` 两次 `gm_validate_part` | 一次canonical和索引构建，合并验证新来源和目标claim；先判断subject/predicate再比较scope |
| `fs.read/write` 原生错误直接中断回调 | A2真实目录冲突及chmod000失败 | `storage_io.splash`薄捕获，既有提交/独立读回守卫继续决定失败；Calendar执行前5个失败分支解除等待 |
| 89564字节遗忘摘要被64KB文本接口拒绝；脚本分段方案仍超时 | A3 RC3/RC4保留失败 | 最小本地SDK接口`fs.sha256_file`，沿用隔离路径、无symlink和1MiB文件上限；读回清理候选后摘要，原receipt格式保留 |
| Activity第201项直接拒绝，后续关键审计无法保存 | `core_record_event`现有200项条件 | 新`activity_archive.splash`：100项批次不可变归档、活动窗口最多200；32归档上限，原历史不删除，摘要/读回/索引重试可恢复 |
| Activity零值/对象被当作空历史 | 旧validator只遍历而不先验证array | 原生array/item字段类型检查；不把损坏JSON当正常空页面 |

| 大库启动每两条重复全库索引与结构校验 | A3 v5 `gm_boot_part` 回调预算失败 | 私有不可变boot快照一次建索引，逐两条完整详验；正常写入每次重建全身份/作用域/墓碑索引 |
| “先别改”等12个否定动作仍替换候选 | 315项契约中的12个保留失败 | 开头否定动作守卫同时用于edit/config/proposal与本地回应；引用的拒绝内容不被当成操作拒绝 |
| 大于64KB的损坏记忆保全又触发文本摘要上限 | `core_preserve_memory_file`仍对raw调用文本SHA | 使用已有新增文件摘要；标准原始字节SHA文件名不变，摘要不可验证即停止写入 |
| cold source单帧16KB解析偶发超过64ms | 新CardHost首轮4个source-preparation超时及实际偏移 | 每帧4KB解析，原64ms/完整解析后一次执行保持；附失败耗时日志，原失败不删 |

## 保留的边界

没有新Capability、第二运行时、外部Mail/Calendar桥、长期Goal页面、动态JS测量或测试答案硬编码。新的文件摘要是明确的本地Makepad overlay，不能称为官方上游已接受。原64ms、callback指令上限、isolate指令及heap上限保持原值。

Activity归档满后仍会安全拒绝新增审计并提示导出，不丢弃旧历史；自动删除归档和无限容量均未加入。v6实际新存储CardHost的64条更正和遗忘、315项契约首轮通过；SDK改为4KB源码帧后仍须绑定最终Host验证，不凭代码宣布整体稳定。活动13项真实隔离文件检查通过，最终新Host重放待完成。

## 最终 V15 的追加修复

- V9 第19次完整冷启动：Memory 身份索引与恢复回调预算失败；按8条分批建立不可变启动索引，原记录完整验证。撤回中间未证明有效的最后scope缓存试验，保留先前已核验的有界结构缓存。
- V12 第16次冷启动：256条聊天一次校验超时。把原字段/重复ID/refs/上限校验抽成共享函数，每回调验证8条；全部完成后才恢复焦点并开放写入。
- V12真实任务首次重启：新来源记忆缺默认metadata，重启立即补写导致SHA失败。现在创建时写完整metadata；实际最终候选首次重启八项SHA相同。
- V13b第二次冷启动：64张Memory卡一次构造超时。改为每页8条，仍完整检索/存储64条，实际8页均可滚动到。
- V14搜索重绘：空遗忘集合仍反复查来源/算摘要。仅为空集合提前返回；非空墓碑函数主体字节相同，28个变体首轮通过。坏值仍在提前返回前拒绝。

历史V15产品b48618acef0ff291ad3dc23b09946b0b15fa4f2f，可读af68b897、compact5092becd；当时官方tokenizer90,541个token相等。原失败、负向测试、源码及日志都保留。实际模型/记忆/任务首次恢复见RC_FINAL_LIVE_REPORT；本轮新rc8的70次启动已经全部通过，2小时合成运行仍在观察。严格独立clean构建因磁盘不足受控中止，暖构建签名运行包不能代替clean PASS。总体PARTIAL。


## 审阅定位与模块所有权

| 内容 | 实际位置/符号 | 维护方式 |
| --- | --- | --- |
| 文件错误捕获 | storage_io.splash / storage_read、storage_write | root维护模块，sync_modules嵌入；原读回决定成功 |
| 活动归档 | activity_archive.splash / core_archive_activity | 近期200项、100项归档、最多32批，满后安全拒绝，不丢旧审计 |
| 记忆schema/validator | global_memory.splash / gm_doc_valid、gm_scope_valid、gm_validate_* | 用户/账号/项目/归属/墓碑均参与授权检索 |
| 记忆检索/更正/遗忘 | global_memory.splash / gm_entries、gm_correct、gm_forget | 自然语言默认，DSL详情展开；每轮相关检索，非整库上下文 |
| 邮件提醒/逐封连续处理 | incoming_mail.splash / mail_watch_* | 账号同步通过Host；草稿/发送确认与防重复仍在产品入口 |
| 页面适配 | ui_page_adapters.splash | 根入口嵌入，三栏/侧栏行为仍由root统一修改 |
| Chat结构验证与恢复 | main.splash / chat_state_header、chat_session_valid、chat_entry_valid、chat_boot_* | 同一守卫复用于同步fixture与分批启动，不简化字段/refs检查 |
| 模型结构化候选 | main.splash / chat_model_config、chat_task_focus | schema与有效来源；模型只产候选，不获得系统批准 |
| 日历时间与候选 | main.splash / calendar_iso_utc、calendar_iso_epoch、calendar_*valid | 保留当前支持范围，修改前重新读系统原事件与目标日历 |
| 邮件draft校验 | main.splash / mail_draft_valid | 手写保护、exact preview、send request绑定，SMTP受理与投递核验分开 |
| 活动显示/结果显示 | main.splash / event_name、activity_visible、activity_summary、结果View | 只格式化已记录真实状态；不由显示文字生成事实 |

五个模块在sync_modules的BEGIN/END标记处生成，入口是产物。每次对模块修改都同步并做官方token等价检查；不能把模块或生成入口当“重复屎山”盲删。主入口仍有430个扫描函数/约528KiB，结构复杂度未完全解决；这次已将存储、归档、记忆、来信循环和页面适配职责明确，但不宣称整份入口已经彻底拆分或不存在死代码。

当前产品对约定时间主要使用Asia/Shanghai与明确UTC偏移ISO，系统读回保留event原time_zone，实际界面更新时刻可能以UTC表达。未实现通用全球时区/任意夏令时系统，跨时区和本机时区显示仍作为限制。原契约的跨日/月/年等合成输入已有检查，不能由此宣称每个全球时区真实通过。
