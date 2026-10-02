# Current State

## 当前源码交付：官方 Muse 0.2.12（2026-10-02）

用户已明确要求推送至 `https://github.com/9tuore/muse-agent`。完整源码在本仓库，分支 `main`；官方开发来源为 `codex/muse-official-migration` / `e00b8cf0bba75a7dd60f271d31faeb7b703c4295`，另外包含尚未在实机重跑的日历测试驱动改动。桌面版源码来源为 `5e7fa0b`，保留两份本地源码改动，未修改旧安装包或生产数据。

0.2.12 已通过 App Hub 更新安装并核对设置页。真实邮箱已授权并读取；0.2.11 合成日历事件创建/修改与各次读回通过，删除未确认成功，清理仍待核验。0.2.12 完整外部动作及重启回归未重跑。总体 PARTIAL；持续监听来信并主动显示结果卡、真实发送与同 Goal 全链未完成。较早报告均为对应版本历史证据，不能当作最终候选通过。

本次仅同步完整代码、配套宿主与框架源码、测试/补丁、报告与文件哈希。账号、凭据、私密截图、生产数据库和二进制不入仓库。按用户指示停止窗口自动化与功能开发；不向主办方 issue 发消息。下一步由用户指示。详见 `SOURCE_DELIVERY.md`。

## 以下为历史交接快照


协作最新偏好（2026-10-01）：用户要求后续不使用子智能体，跨对话协作用真实已有聊天。先前Agent审计为历史已完成安排，后续不再派发。参赛纯源码已整理到桌面 Muse参赛源码-0.2.8-2026-10-01 文件夹及同名ZIP；37份源码/测试/补丁/报告，导出SHA逐一核对与bundle Gate通过，未push/issue提交。

## 当前：Phase 2 实机联调 0.2.8（2026-10-01）

分支codex/muse-official-migration；产品修复56fec94，测试/源码导出e64d243。真实打包OctoSense/App Hub中文八页、三新模型Goal及矮窗735字Storage链通过。正常重启23文件SHA相同，Goal21/Run19/Action15/Memory3不变，Activity仅增加restart restore。真实Calendar full_access，create/get/update/get/delete/get完成且合成事件清理。五尺寸输入/按钮在Dock上方，真发送通过；412×892请求实际受限412×818。

总体PARTIAL：三轮Chat语义复测2/3，Memory来源hash为空、设置/视觉未1:1；本人Mail登录/测试地址/最终发送尚缺，邮件→日历同Goal未LIVE。原版Gate仍拒calendar；扩展签名check通过、scan人工human-review。旧安装版严格验签/SHA不变，未改生产数据。代码正整理为参赛纯源码；用户要求先完善再提交，未push、未评论issue。请从根目录PHASE2_LIVE_TEST_REPORT.md、PHASE2_LIVE_ACCEPTANCE.md、PHASE2_LIVE_EVIDENCE_INDEX.md进入。优先补真实Mail同任务，解决语义及剩余差异；无新Capability/Phase3。

## 以下为历史快照


## Phase 2 最终候选 0.2.2（2026-09-30，`codex/muse-official-migration`）

中文八页与左中右三栏已在隔离 Release OctoSense Shell 实际显示；最终 0.2.2 通过 App Hub 本地演练 catalog 升级/全新安装。三个新 Goal/Run 在真实 Shell 完成批准→本机 `model.complete`→存储→独立读回，Shell 重启后三个结果 SHA 不变；0.2.1 遗留的 timer 超时目标在升级后安全恢复。412×805 长文 Goal 和 990×400 矮窗 Goal 可操作，但后者内容区仅 71 点。邮箱仅在固定 `mail_demo` FIXTURE 跑完宿主连接、同步、正文、来源记忆、编辑草稿、精确预览及单独确认返回 accepted；无对外投递或收件端回执。Calendar 宿主状态真实返回 `write_only`，未触发本人 TCC、未执行系统事件 CRUD。两轮 Chat 消息持久化，但本地模型的追问误答“收到”。因此总体 **PARTIAL**，Goal 受限回归 **PASS**，Mail/Calendar/同任务 LIVE **BLOCKED**。原版 App Hub Gate 不接受 calendar；隔离宿主补丁及 ad hoc `.app` 仅本地候选。旧安装版 SHA 未变且严格验签通过；未改生产数据、未正式签名/发布/push。详细证据见 [`PHASE2_TEST_REPORT.md`](../PHASE2_TEST_REPORT.md)、[`PHASE2_PARITY_AND_FUNCTION_MATRIX.md`](../PHASE2_PARITY_AND_FUNCTION_MATRIX.md)、[`PHASE2_RUNBOOK.md`](../PHASE2_RUNBOOK.md)。

## 官方 Muse UI 迁移更新（2026-09-30，`codex/muse-official-migration`）

在独立版 0.3.1 与官方 OctoSense Shell 中实际打开并截图后，官方 Muse 0.1.10 已有中文六项导航、Chat/Goals/Goal Detail/Memory/Activity/Capabilities/Settings、真实 `model.complete` 对话、受限 Goal 计划审批卡、结果/错误卡和隔离存储。Shell 本地 App Hub 安装版的新 Goal `1790703104-3867664407` 完成 Goal → Plan → 用户批准 → model.complete → Storage → Readback → Shell Restart Restore；结果 SHA-256 `eeebf075285344fe9d8a6a70ff34d8d4a9a2ba32ac66b94981bb65602a51f7e2`，重启前后相同，当前 Goal 的写入/回读各一次。0.1.9 曾在同步批准时超出脚本时间预算，0.1.10 改为已持久化批准后下一 tick 执行，新 Goal 无需重试通过。可见 card-host 0.1.10 烟测通过，0.1.8 布局矩阵覆盖 412 宽、990×400 矮窗口、1280×800 宽窗口及 455 字/8 条资料；`hub check` PASS。证据与未完成项见 [`MUSE_UI_PARITY_REPORT.md`](../MUSE_UI_PARITY_REPORT.md) 和 [`docs/MUSE_UI_PARITY_MATRIX.md`](../docs/MUSE_UI_PARITY_MATRIX.md)。**总状态仍为 PARTIAL**：真实 AI 对话可调用并持久化，但本地小模型连续追问误答；独立版三栏、原有 Memory、可浏览多 Goal 历史、Activity 观察功能、可编辑模型/预算和全卡片逐态尚未 1:1；Mail、Calendar、Browser、TextEdit、插件按本轮用户澄清暂不覆盖。安装的独立版 SHA/严格验签未变化；本地测试镜像不等于正式发布，未 push。

## 官方容器迁移分支补充（2026-09-29 19:35 Asia/Shanghai）

本节仅适用于独立 worktree `/Users/mima0000/.codex/worktrees/muse-official-migration/Agent APP黑客松` 的 `codex/muse-official-migration` 分支，基线 `5e7fa0b`。下方旧版现状是接手时的历史快照；主工作区、已安装原生 .app、生产 SQLite 和密钥没有被迁移试验改写。

当前 Shell 锁定的官方源组合、首个 Muse 脚本 bundle、实测表与失败证据见 [`docs/OFFICIAL_RUNTIME_AUDIT.md`](../docs/OFFICIAL_RUNTIME_AUDIT.md)、[`docs/OFFICIAL_MIGRATION_MATRIX.md`](../docs/OFFICIAL_MIGRATION_MATRIX.md)、[`evidence/official-migration/README.md`](../evidence/official-migration/README.md)。首条资料整理目标已在 `card-host` 的真实脚本运行时完成输入、计划、批准、应用隔离文件写入、回读和重启恢复；模型按钮在无服务的 `card-host` 诚实报错。**OctoSense Shell 已构建并启动 App Hub，但大型 Splash 和 Shell 在本机 Intel Iris Pro 上分别呈灰屏和黑屏；同版本简易 Counter 与重新运行的 Muse `card-host` 正常绘制。Muse 尚未安装进 Shell，不可宣称容器集成通过。** `tools/octo check` 已通过，`hub scan` 生成七项人工审查问题；publisher 占位和签名仍是人工节点。付费模型未调用。

后续受限 `muse.goal/0.1` GoalSpec 在隔离 `card-host` 中通过真实 UI 批准、执行、读回；篡改计划路径在批准前被拒绝（`approved_at=0`，无结果）。当前 Shell 空桌面、News 和 Android 测试入口也黑屏，同机旧 Shell `a74a255` 则能显示桌面；当前 Shell 的具体渲染回归仍未定位。独立测试宿主通过不能升级为 OctoSense 容器通过。

Date: 2026-09-29 13:52 Asia/Shanghai（快照；每次接手先重新核对）

Branch: `main`

HEAD: `c068fb6adddbc8aed7ef9ddc92977724f91e7634`（文件夹整理前的核对点；功能代码调查基线为 `dbd08ed`，后续实际 HEAD 以 `git rev-parse HEAD` 为准）

Version: macOS `CFBundleShortVersionString=0.3.1`；分发目录标签 `r17-mail-contacts-reply`，不是语义版本号
Workspace: `/Users/mima0000/Documents/ChatGPT/Agent APP黑客松`

2026-09-29 磁盘清理补注：本节以上为 13:52 快照；随后安装版主程序已与 `r18-calendar-live` 一致，安装版和 r18 原包均通过 `codesign --verify --deep --strict`。旧分发版（初版、r2–r16）和旧集成候选（初版、02–18）的 `.app/.zip/.dmg` 已清理，仅保留目录中的说明及校验值；r17 回退包、r18 当前包、candidate-19、独立验收证据与用户数据保留。历史证据中指向已清理旧包的路径不再可直接复跑。详情见 [磁盘清理交接](HANDOFF_DISK_CLEANUP_20260929.md)。

交接包首次提交前的工作树已有未提交内容：`app/muse_textedit_recipe.py` 被修改，另有 108 项未跟踪旧包/证据/资料；后续接手不得盲目清理或纳入这些内容。历史 `HANDOFF.md`、`STATUS.md` 和 9 月 28 日验收表保留，但它们的旧包路径与进程状态不是当前事实。

本交接文件夹已改为自主接手：没有更新的具体用户任务时，新模型可从下方优先级自行选择非核心问题直接开工。`TASK.md` 状态为 `OPEN`，不要求用户先指定目标或可修改文件；核心保护清单见 `AGENTS.md`。

## PASS

| 项目 | 范围与证据 |
| --- | --- |
| macOS 原生 Muse | `0.3.1` 当前已安装并运行；2026-09-29 文档验收产生的 Python 缓存已按与 r17 原包逐文件比对清除，安装副本和发布原包均重新通过 `codesign --verify --deep --strict`。PASS 仅指本机运行和签名，不等于陌生用户可安装。 |
| Qwen / 本地模型 | `Qwen3-0.6B-Q8_0` 的本机 llama 服务正在 `127.0.0.1:8080` 运行，`/health` 返回 `ok`；r14 模型意外退出后自动恢复与原生问答见 `evidence/muse-g00-r14-model-recovery.md`。 |
| Goal DSL、Memory DSL、Capability DSL | `app/muse_dsl.py` 与三类 schema/存储实际存在，单元测试和此前包内校验覆盖结构、摘要、范围及错误输入；这只代表本地 DSL。 |
| Goal Engine | 第十七版历史签名包完成同一真实本地 Qwen Goal 的批准→v1→约 60 秒 `NO_CHANGE`→合成目录事件 v2→回读、暂停/重启/恢复/取消，见 `evidence/muse-g00-candidate17-integrated-20260928/README.md`。PASS 限于此本机受限场景。 |
| Background Runtime | 本次快照有原生应用、其 worker、本地模型和 QQ 桥四个进程；worker 负责定时/事件推进。进程存活不是长期目标长期正确性的证明。 |
| Files | 受限工作区写入/回读、摘要批准和重复动作阻断有第十七版包内证据；不含全盘读写。 |
| Calendar（本机真实闭环） | 2026-09-29 从**已安装 r18 成品**完成：用户在系统弹窗授予**完全访问**（`org.gosim.local-agent` auth_value=2）；成品内 `calendar_selftest.py` 读取未来窗口 → 创建 `[Muse Test] MUSE-CALENDAR-TEST-…` → 回读 → 修改 → 回读 → 应用内确认后删除 → 回读确认不存在；创建/修改均 `readback_matches=true`，删除 `readback_absent=true`，事件已清理。见 `evidence/muse-calendar-live-verification-20260929.md`。PASS 仅限本机、可写日历、唯一标记的测试事件；未做多日历/拒绝/重放等反例。2026-09-29 追加：**Agent 现在自己处理日历**——对话里说「加个日程：明天下午3点开会」会给出待确认卡，确认后写入默认日历并读回；回复邮件后若正文含时间，会附「是否加入日历」待确认卡。见 `evidence/muse-calendar-agent-20260929.md`。2026-09-29 再追加（r21-calendar-human，**人性化**）：意图解析支持中文数字与口语（`八点半`/`明天下午三点`/`今晚八点一刻`），并新增宽松的来信提议 `propose_from_mail`；邮件回复发出后，Muse 会用口语主动问「要把「今晚8点 吃饭」加进日历吗？」，用户可直接回「好/同意」写入、「算了」不写；用户对来信说「同意」时，起草的回复本身也会表达同意并复述时间（`好的，今晚8点没问题，我到时见。`）。顺带修正两处真实 bug：「下周X」原先多算一周、「八点一起…」曾把「一」当分钟。见 `evidence/muse-calendar-human-flow-20260929.md`。同日晚追加（r22-calendar-revision）：**改口可用**——「8点去咖啡厅不」→ 卡片 20:00，再说「8点去不了，改成9点」→ 卡片自动换成 21:00（标题仍为「咖啡厅」），说「好」才写入 21:00；「8点去不了了」则视为不去了、不写。同时修掉疑问尾字混进标题（原「咖啡厅不」）。 |

## PARTIAL

| 项目 | 已有部分与缺口 |
| --- | --- |
| 高阶 GPT、DeepSeek Provider、Provider Switch | OpenAI Responses、DeepSeek Chat、模型/预算/Primary-Backup/预览有代码和 fixture；没有本轮可核验的真实远端推理、账单和同任务工具动作。Backup 还有同源/协议限制。 |
| Memory、Knowledge Graph | SQLite 记忆、来源、claim、关系、更正/遗忘、范围与检索有代码和隔离测试；整台电脑历史自动抽取与事实质量未验。 |
| Mail | 本轮真实 QQ IMAP 状态 `CONNECTED`、最近收件箱邮件头提取 27 位联系人；原生联系人窗口与合成点击测试通过。用户已反馈新版操作正常，旧结果卡→真实 SMTP 回复曾由用户确认。r17 新的“无来信卡选人回复”没有由本轮自动化向真实联系人发信，故完整外发回执仍缺独立证据。见 `evidence/muse-r17-mail-contacts-reply.md`。 |
| Browser Research、Browser real action | 第十七版历史签名包在 Edge 上真实点击/读回三页公开网页并生成本地 Qwen 报告；当前 r17 邮箱版未重跑这条 GUI 链，报告事实并非全量复核。 |
| Terminal | 旧的 `mkdir`/`touch` 等受限确认能力有本机证据；不含任意 shell，当前 r17 未单独重测。 |
| App Learning、TextEdit real action | 有 `RecipeStore`、AX 观察/配方、TextEdit 签名候选实写读回证据；当前 r17 未独立复跑，不能称通用软件学习。 |
| Plugin system | 审查过的内置插件、声明式 SDK、批准/撤销、篡改阻断有本地和旧包证据；任意第三方代码安装与通用插件生态未通过。 |
| DMG、first-run onboarding | r17 DMG 隔离安装启动/退出与原始包验签通过；首启部分选项有历史测试。ad hoc、未公证、仅 Intel；第二台 Mac/Apple Silicon/全新用户权限未验。 |
| Keychain | 成品在用户允许后恢复 QQ 邮箱授权码并维持连接；GPT/DeepSeek 密钥从成品读取并真实调用未验。本交接没有读取或记录密钥。 |
| OctoSense | 官方 Octos/AppCard 曾形成真实会话与审批请求，宿主与局部 MCP 实验有证据；尚无同一 Muse Goal 的可信人工确认→动作→回读→官方结果。见 `evidence/muse-g01-h5-evening-entry-20260928.md`。 |

## BLOCKED

| 项目 | 当前证据与解除条件 |
| --- | --- |
| robrix2 | 旧官方 checkout 有静态接口，原生构建曾在 Swift `Foundation` 桥失败；Matrix 登录、owner/project room、设备登记和 backend session 无 live 证据。不能把源码 parser 算真实宿主。 |
| official full-chain | OctoSense/robrix2 与同一 Muse Goal 的官方会话、真人确认、唯一受限动作、独立回读和官方结果没有闭合；此前官方原生 shell 负例出现未审批执行，产品侧必须继续禁用该副作用路径。 |

## NOT TESTED

| 项目 | 边界 |
| --- | --- |
| mobile / OnePlus 6 | 尚无移动端安装、设备桥或真实手机动作验收。 |
| 真实付费 GPT / DeepSeek 结果 | 协议 fixture 不能替代远端内容、用量与费用回执；本次未发付费请求。 |
| 朋友另一台 Mac 的分发 | 新用户 TCC、Apple Silicon、Gatekeeper/公证、模型首次下载未在第二台机器上测。 |

## Active Processes

13:20 快照：原生 Muse PID `82355`、独占 worker `82395`、本地 llama/Qwen `82558`、应用持有的 QQ IMAP 桥 `89304`。QQ 健康文件状态 `CONNECTED`，联系人快照 27 位；这些 PID 会变化，接手须重新查询。未观察到 OctoSense/robrix2 进程。

## Latest Tests

- 2026-09-29 日历改口/标题修复（r22-calendar-revision）：新增 `parse_calendar_change()`（取**最后一个**时间）与 `looks_like_change()`；`_chat_message` 在有待确认卡时先试改口、再试同意/拒绝，显式新指令仍整卡替换；`_TAIL_WORDS` 增加 `不/没`，`is_refusal` 增加 `不了/改天`。日历相关单测 **51/51**；全量 **313 项仅 G01 环境性失败**。证据 `evidence/muse-calendar-human-flow-20260929.md`。
- 2026-09-29 日历人性化闭环（r21-calendar-human）：来信「我们今晚八点一起吃饭？」→ 用户说「同意」→ 草稿 `好的，今晚8点没问题，我到时见。` → 回复发出后提议「要把「今晚8点 吃饭」加入日历吗？」→ 用户回「好」→ 写入 20:00 且 `READBACK_MATCH`。用**安装包内代码**跑通（假日历后端，未写真实日历）。日历相关单测 **41/41**；全量 **303 项仅 G01 环境性失败**；`bundle_integrity=PASS`。证据 `evidence/muse-calendar-human-flow-20260929.md`、`evidence/muse-unit-tests-r21-20260929.txt`。**尚未经用户在成品里手点一遍。**
- 2026-09-29 Agent 日历能力（r19-calendar-agent）：新增确定性意图解析 `muse_calendar_intent.py` 与 `UserCalendarService`（真实用户事件，`approved=True` 才写 + 读回）；`desktop_app.m` 复用通用任务卡确认流；回复邮件后按正文时间给出待确认卡。日历相关单测 23/23；全量 **285 项仅 G01 环境性失败**。证据 `evidence/muse-calendar-agent-20260929.md`。**尚未经用户在成品里实点验证**。
- 2026-09-29 Calendar **真实闭环（已通过）**：从已安装 r18 成品、用户系统弹窗授予完全访问后，`calendar_selftest.py` 完成 读未来窗口 → 创建 `[Muse Test] MUSE-CALENDAR-TEST-…` → 回读 → 修改 → 回读 → 应用内确认删除 → 回读确认不存在；全部 `readback_matches=true` / `readback_absent=true`。证据 `evidence/muse-calendar-live-verification-20260929.md`。定向单测 `test_muse_calendar.py` 6/6、`test_calendar_selftest.py` 4/4；全量 **272 项仅 G01 环境性失败**；`bundle_integrity=PASS`。
- 2026-09-29 安全测试运行器（新增 `scripts/run_muse_unit_tests.sh`）：用**安装包自带 Python** 跑全量 267 项，`bundle_integrity=PASS`（包零改动、严格验签通过）。该脚本导出 `PYTHONDONTWRITEBYTECODE=1` + `PYTHONPYCACHEPREFIX` 给整棵进程树，并在运行前后对目标包做验签+文件清单门禁。证据：`evidence/muse-pyc-signature-gate-20260929.md`、`evidence/muse-unit-tests-safe-20260929.txt`。唯一失败项见下条说明。
- 2026-09-29 `test_g01_capabilities.test_owned_worker_start_health_stop_and_readback`：在工作沙箱内持续失败，原因是该用例用 `ps -p <pid> -o command=` 做进程身份校验而沙箱禁用 `ps`（`_process_command` 返回空 → `owned=False`）。已在未改动 HEAD 上复现同一失败，属环境限制，非代码回归。
- 2026-09-29 本次源码：`PYTHONPATH=app /Applications/GOSIM-Local-Agent.app/Contents/Resources/python/bin/python3 -B -m unittest discover -s app -p 'test_*.py' -q`，**267 tests / OK / 32.123 秒**。此命令或它启动的子进程随后在**安装副本**写出 88 个 `.pyc`。逐文件确认原有 746 个文件与发布包哈希一致后，只移除这些新缓存；安装副本与发布包最终均严格验签通过。此命令不能作为今后的成品验签测试模板。
- 2026-09-29 r17 定向：`test_agent_app test_qqmail_imap_bridge test_desktop_worker`，47/47；`scripts/test_muse_mail_contacts_ui.py` 的隔离包合成联系人原生点击 `PASS_FIXTURE`；`scripts/test_g04_install.sh` 在 r17 DMG 的隔离安装 `PASS_LOCAL`，见 `evidence/muse-r17-mail-contacts-install-smoke.txt`。
- 2026-09-29 交接包自检：仅用五个入口文件回答十个接手问题，10/10 可定位；七个文档的本地链接无断链，未发现邮箱地址或常见 API/GitHub 密钥形状。此检查是文档可读性测试，不是产品能力测试。
- 后续跑单元测试请改用 `scripts/run_muse_unit_tests.sh`（已按上面三条经验固化）：它默认用安装包 Python 但全程导出字节码守卫并做前后验签门禁；需要更保守时设 `MUSE_TEST_APP_COPY=1` 在临时副本上跑，或设 `MUSE_TEST_PYTHON=<独立 3.12>`。不要再用裸 `python3 -B` 直接指向签名包。

## Deliverables

- 最新 r22（改口/标题修复）包：`dist/Muse-5A-2026-09-29-r22-calendar-revision/`（ZIP SHA-256 `0922fe9448ff9f477b26f960df5e36d6ff383b8150fa58892fd88389d319027a`）。
- 最新 r21（日历人性化）包：`dist/Muse-5A-2026-09-29-r21-calendar-human/`（ZIP SHA-256 `2157a83f89df5878e0327fe9bd0463aa5b8de8d7431cfee7ed3368912086a815`）。
- 最新 r19（Agent 日历）包：`dist/Muse-5A-2026-09-29-r19-calendar-agent/`（ZIP SHA-256 `d97ff7f76ba0a238613afcc54fc01faa7475b3b156ea8f3e47621fd09f8063ba`）。
- 正在运行的安装副本：`/Applications/GOSIM-Local-Agent.app`（**r22-calendar-revision**，r21/r20/r19/r18/r17 备份在 `runtime/backups/`）。（历史：**r21-calendar-human**，r20/r19/r18/r17 备份在 `runtime/backups/`），含日历入口与人性化日历流；已严格验签。（历史行：r19-calendar-agentr17 备份在 `runtime/backups/GOSIM-Local-Agent-r17-20260929.app`）。
- r18 候选包（本机已安装）：`dist/Muse-5A-2026-09-29-r18-calendar-live/`（含 .app/.zip/.dmg）。ZIP SHA-256 `54fcd9ed3c2bc01dd0bda1203f45970a06ca57b0c8dd533f47db01c83b35f4d4`。
- r17 有效签名原包：`dist/Muse-5A-2026-09-29-r17-mail-contacts-reply/GOSIM-Local-Agent.app`。
- ZIP：`dist/Muse-5A-2026-09-29-r17-mail-contacts-reply/GOSIM-Local-Agent-macOS.zip`，SHA-256 `61b01606c1616481966df68a3446038f2e5aeabe1295a80f95927745e1612cf9`。
- DMG：`dist/Muse-5A-2026-09-29-r17-mail-contacts-reply/GOSIM-Local-Agent-macOS.dmg`，SHA-256 `a39c9338e588144dc51555db767e833e9e624a1150d7481ba3c3d3856a32234e`。
- 最新邮件证据：`evidence/muse-r17-mail-contacts-reply.md`；旧五项硬门槛台账：`docs/MUSE_5A_ACCEPTANCE_20260928.md`（历史快照）。
- 安全单元测试运行器：`scripts/run_muse_unit_tests.sh`；字节码/签名门禁定位证据：`evidence/muse-pyc-signature-gate-20260929.md` 与 `evidence/muse-unit-tests-safe-20260929.txt`。
- Calendar 证据：真实闭环 `evidence/muse-calendar-live-verification-20260929.md`；权限归属纠正与入口缺口 `evidence/muse-calendar-permission-and-loop-20260929.md`。

## Known Boundaries

### DO NOT CLAIM

- 本地结果卡 ≠ 官方 AppCard；编译或打开官方窗口 ≠ official full-chain。
- Provider 设置 UI / 协议 fixture ≠ 真实 GPT/DeepSeek 推理或收费验收。
- 固定 TextEdit/Edge 操作 ≠ 任意 App Learning；能读授权目录 ≠ 整台电脑全知。
- mock / fixture ≠ live integration；进程存活 ≠ 长期 Goal 持续正确工作。
- Codex 能操控电脑 ≠ Muse 成品具有同样的权限；QQ 收件箱最近联系人 ≠ QQ 通讯录。
- 发布包的验签结果不能代替 `/Applications` 安装副本的再次验签；本机安装烟测 ≠ 陌生用户可无阻安装。

## Next Priorities

1. （已完成 2026-09-29）测试向签名包写字节码的问题已定位并用 `scripts/run_muse_unit_tests.sh` 固化（导出整树字节码守卫 + 运行前后验签/文件清单门禁）。剩余可选：把该门禁接进发布前脚本或 CI。
2. 从**修复后的最终包**重跑本机 Goal、TextEdit、Edge 和 QQ 手动联系人回复的独立验证。
3. 用户在产品里明确配置与批准后，核对真实 GPT/DeepSeek 输出、用量、费用和模型回退；禁止默认付费探针。
4. （2026-09-29 已完成本机闭环）Calendar 已从 r18 成品通过真实读写回读；剩余：多日历选择、拒绝/撤销/重放/断连等反例，以及 Apple Silicon / 第二台机器的复测。
5. 完成官方宿主同一 Goal 的可信人工确认、受限执行、独立回读和官方结果；再测拒绝、重复、断连与重启。
6. 在第二台 Mac 验签、公证/Gatekeeper、首启模型和新用户 TCC；逐项修复分发阻塞。

## Recent Commits

以下是文档开始前的最近 15 条，不包括稍后的交接包提交：

```text
dbd08ed 2026-09-29 Add QQ mail contact replies without incoming cards
9f8c471 2026-09-29 Record r16 live QQ mail reconnection after keychain approval
fb69ed7 2026-09-29 Ground Muse agent capabilities in live mail status and recover stalled listener
9d54c9c 2026-09-28 Record installed model recovery verification
48501e1 2026-09-28 Restart managed local model after service exit
9941f9e 2026-09-28 Update native layout probe for skill and result tabs
48a53f2 2026-09-28 Keep skill navigation clear at minimum window size
8ad8d7e 2026-09-28 Keep skill and result panes visually separate
38ec46f 2026-09-28 Add skill and result card tabs to native inspector
11e6185 2026-09-28 Restore persistent QQ Mail bridge and expose app modules
8c3b816 2026-09-28 Use role messages for local multi-turn chat
1d2730c 2026-09-28 Exclude legacy failure replies from local chat context
e8b91cf 2026-09-28 Record native model recovery evidence
adca6ee 2026-09-28 Bound local chat to Qwen context and use configured model gateway
fa8e980 2026-09-28 Reshape native home and review card hierarchy
```
