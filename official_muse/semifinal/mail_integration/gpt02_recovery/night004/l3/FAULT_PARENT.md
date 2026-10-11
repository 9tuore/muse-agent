# NIGHT004 故障父驱动

GPT02自有命名空间交付。**Mail/Memory组件：13场景、117项PASS；真正Kernel CAS两场景：PREPARED_NOT_TESTED；完整链NOT_TESTED。** 逐项状态及必选检查见 `fault-cases.json`。本轮没有改生产main、SDK、Host门禁或共享target，没有启动GUI/SMTP/Keychain；旧证据全部保留。

Root最终定位为test-only bridge错误使用open_context；正式无client请求实际走open_conversation。主源lane守卫保持，GPT01仅修真实会话入口与trigger映射，R8待编译。parent始终原样转发历史；本CAS错误检查读实际turn/thread、tool-call、digest及原生产receipt validator，不补lane。正式e7d/签名643009candidate-r2由中央固定；执行前从其实际源重新prepare。本轮8ad组件117不升级为该候选或真正Kernel/create/CAS通过。

冻结源 `8ad9a79987a651909a653a6a5b3798bdfd086096ea8842450685b879170c3ff1` 为GPT03最终完结补丁候选；2026-10-12 02:48左右只读核对中央main同SHA。中央后续UI/行动链合并若改变SHA，须从实际新源重新prepare，不能把本轮计数改标签为新候选。Root随后753c7de2及UI合并结果不计入本轮117。所有非边界生产函数按原字节提取，identity逐函数/全局记录SHA；仅既有renderer/IO/transport适配。

## 已执行组件

| 场景 | 初始检查 | 新进程恢复检查 | transport调用 初始/恢复 | 收件条数 |
| --- | --- | --- | --- | --- |
| accepted、同compose重复审阅 | 13 PASS | 7 PASS | 1 / 0 | 1 |
| 投递前失败before、只读恢复DRAFT | 13 PASS | 7 PASS | 1 / 0 | 0 |
| 投递结果未知unknown | 13 PASS | 7 PASS | 1 / 0 | 1 |
| parent故意扣留实际已完成review回包、注入timeout事件 | 13 PASS | 7 PASS | 1 / 0 | 1 |
| parent损坏实际review回包后由JSON decoder拒绝 | 13 PASS | 7 PASS | 1 / 0 | 1 |
| 实际OS备份写入失败 | 8 PASS | — | 0 | 0 |
| 实际坏JSON state setup / 新进程拒绝 | 2 PASS | 7 PASS | 0 / 0 | 0 |

timeout是明确parent回包丢失事件，不是实际计时超时或Kernel超时。malformed JSON发生在parent转发边界，保留原实际service reply、损坏wire、实际JSONDecodeError与VM收到的失败；不声称生产Host产生坏JSON。before/unknown使用已有MockTransport实际分支。所有Vault、审阅动作、接收内容及授权为fixture；独立Python stdio收件端实际收到数据，真实SMTP为0。

写失败在自有 `mail-draft.backup.json` 放临时目录，实际 `Path.write_text` 得到 `IsADirectoryError/errno21`。恢复原backup字节；primary/backup前后SHA均相同，原正文保留，compose/review均未派发。坏存储只写自有marker state，goal/memory主备、改期journal及Mail draft原坏bytes被保留，生产boot拒绝，未写完成状态。恢复是真正新VM/Mail/recipient进程；后台poll排队、未drain。

复跑入口：`run_mail_faults.py --source SOURCE --source-sha ACTUAL_SHA --runner VM_BINARY --mail-binary MAIL_BINARY --out OWN_BUILD_NEW`。每次out必须新建。当前VM来自GPT03 `build/gpt03-night004/target/debug/gpt03-night004-vm`；Mail为GPT02 `build/gpt02-night004-l3-helper-r1/mail-runtime-r3-bin`，SHA `ba37b915b24917be68964c10c38409169b7162489fbd2de22c082a1e05055367`。旧L2 binary `6b67963a…` 未改变。本轮最终原报告在 `build/gpt02-night004-mail-faults-final8ad-r1/`。

`fault-evidence`保存最终13报告/stdio、5执行源与identity、冻结文件门禁报告和两个旧失败；manifest给73文件SHA（不含manifest本身）。首轮whole JSON文本字段顺序断言失败，独立解析结构完全一致；r2嵌套断言遇到VM stack错误。最终固定attempt字段签名，修fixture断言，不改业务/VM。旧完整轮仍在build，未删除。

## 中央待执行两场景

`native_cas_fault_probe.splash`：原Mail读取→来源Memory→原chat建Goal→真正Kernel create/get/history verified。重复incoming不得加Memory，重复create不得加turn/event。原第二封Mail/chat改期select后，旧手写草稿不能发送。然后**独立专用真实CalendarService进程**更新同一marker `.host` 事件；原confirm携带旧八字段expected，经真正Kernel get/update/history；必需actual kernel_persisted error receipt、update digest和真实changed elsewhere错误。模型fixture故意提交保留旧快照以检验实际CAS，不将首次get发现的新事件替换为expected。必选：新改期不可verified、owner新事件/稳定ID/request_id不被覆盖、events文件SHA不变、重复confirm/create不增turn、原journal/正文保留、无完成Goal/Run/Memory、Mail transport0。

`native_cas_restart_probe.splash`：新VM/Mail/Kernel进程恢复上述state；实际owner字段及events SHA相同、同一失败改期记录不可verified、原Goal不completed、原手写正文保留且发送被阻断、turn/mail transport0、新chat实际来源召回。原Kernel history不合成，不从旧raw hydrate重构当前Broker证明。

先确认中央首个可执行完整L3通过，再新建专用Kernel root跑CAS初始；恢复沿用CAS初始的三个state根。按照 `KERNEL_PARENT.md` 给四显式Kernel参数，再加：

```text
--calendar-owner-helper /Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-calendar-history/target/debug/gpt01-night004-external-owner
--authorize-external-owner-write
--kernel-test-frozen
```

实际shell命令应正常引用有空格的路径。owner helper只用于初始，SHA固定 `e7dc890860d1a17d2fbc08e68ed98aa39c75eaee370bb18a6eb2281b2ed6c265`，复制到本轮out。必须已有ready Kernel；host根精确取其fixture_root/apps/.host并核marker。Root显式传--authorize-external-owner-write时，parent仅为本次真实所选ID/request创建精确EXTERNAL_CALENDAR_OWNER_WRITE_OK.json并在实际独立进程结束后删除；未传时必须由Root预置完全相同marker，否则拒绝。原args/许可写入out，实际helper stdout/stderr原样保留。只改notes，时间/时区/地点不改，expected不替换。Root实际执行该命令才会写isolated owner，本聊天未执行。旧只读helper保持原边界。原Kernel只读诊断口未扩大为写口；专用helper按双marker与精确event/request写许可操作实际Store，不产生Kernel回执。

先 `prepare.py --source SOURCE --source-sha SHA --probe <CAS_PROBE> --out NEW_PREPARE`，再用 `run.py` 既有参数执行；恢复增加 `--state-root INITIAL/state --mail-root INITIAL/mail-state` 和指向同一Kernel fixture_root的config。当前8ad源码已分别prepare为自有 `build/gpt02-night004-native-cas-prepare-final8ad-r4`、`build/gpt02-night004-native-cas-restore-prepare-final8ad-r3`。无Kernel定向VM仅前四项通过，create明确blocked/FAIL；此证据不能称CAS执行。

## Shell二进制磁盘约束

默认仍每轮复制。显式 `--kernel-test-frozen` 才复用Root冻结一次的独立副本；不能指向会重编的target、symlink或hardlink。副本在中央build/night-004或GPT02自有build下，权限必须无write位。旁边必须有 `FROZEN_TEST_BINARY.json`，精确两字段：

```json
{"filename":"shell-test-bin","sha256":"实际冻结副本的完整SHA256"}
```

Root负责从唯一R7产物普通复制一次、计算SHA、写marker并去掉write位。每case启动前核marker/路径/权限/nlink及实际SHA；记录实际文件路径、SHA、marker SHA，退出后再次核SHA，不一致使report FAIL。每case仍独立wrapper/model/config/state/raw logs，不改业务回包和history。实际冻结文件门禁6/6通过；这是文件条件验证，不是Shell/Kernel运行。

2026-10-12 CAS fixture notes修正：中央r1实际外owner成功，官方lib::text.trim把输入开头空格去掉，旧probe逐字比较因此FAIL。仅新输入表达式改为(selected.expected.notes + " 外部合成编辑").trim()；expected及CAS真实error/digest/owner bytes/count/重启断言不改。cas-notes-static.json记录原实际请求/回包和5项静态核对，cas-notes-identity.json为同e7d逐字提取244函数字段。Root r1失败保留；本聊天未重跑真实CAS。前置query已经bd44e5c0交付，仍按QUERY_PARENT.md由Root跑R8，不重复修改。
