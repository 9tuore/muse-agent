# Mail 专项接续 — 2026-10-10

状态：PARTIAL / 原生服务运行未验证。只读源码诊断完成，未发信、未查账号资料、未启动GUI、未构建、未提交。

## 现场与证据

指定 worktree，分支 `codex/muse-pivot-20261010`，开始 HEAD `2cebd4c8`。既有未提交文件保持。独占本目录。

运行 `python3 official_muse/semifinal/mail_integration/diagnose_registration.py`：exit 0，12/12源码断言通过，结果 `registration_audit.json`。这是源码合同检查，不是协议执行或官方 full-chain。

`build/pivot-reference-release-r1/muse-calendar-reference-host` 实际SHA为 `8d13132a004623761b2a529e19fa8d306fb69bc27ad4524f5cc5b49706cac7a7`，匹配旁侧 report。现有 `build/pivot-core-mail-r1` 与 `build/pivot-core-mail-restart-r1` 目录已确认存在；没有重复19/7测试。

## 服务注册定位

当前 `.local-state/official-rc2-source/crates/shell/src/apps.rs:186` 的 `register_mail_services()` 调用官方 `octosense_mail_service::register()`；demo配置分支调用 `register_demo()`。同函数设置 `public_review::on_review(...connected_review::smtp_sheet)`。`register_host_services()` 调用它，并在约249行调用 `connected_review::register()` 注册宿主审阅组件。

`apps/mail/host-service/src/public_review.rs:191` 对非前台/from_sheet请求拒绝；仅macOS/Android平台接受原生审阅准备；无钩子返回 `This host has no native Mail review surface`。`ReviewRequest::approve` 必须物理down/up；`connected_review.rs:323` 捕获 `trusted_user_input()` 的按下和点击，脚本点击不等同本人手势。

最小源码支持环境是启用 `app-hub` 的官方Shell或 `native_mobile`，并同时包含：官方Mail服务、注册的原生SMTP审阅钩子、宿主审阅widget模块、前台ServiceHost审阅挂载路径与可信平台事件。单独注册MailService只能补服务方法，不能补GUI审批。官方Shell已经实现这条路径，故本轮不写多余注册补丁，不新建SMTP/IMAP代理。

`build/pivot-builtin-calendar-original-r5/native/Cargo.toml` 和 `src/main.rs` 仅增加Calendar依赖及注册；未包含Mail依赖、Mail注册或Shell审阅。release旁侧记录无冻结源码manifest，**尚不能证明该release与r5源码逐字对应，也未实测其 runtime.list**。应把它标作“Mail未证实/组件”，不能当新版完整Shell。

## 三类阻塞必须分开

- NATIVE_HOST_UNVERIFIED：新完整Intel Shell未在本轮构建；reference组件不能代替原生Mail审阅证明。
- LOGIN_UNVERIFIED：没有读取账号或Keychain。官方服务账号按app授权（`store.granted(app, account)`），旧Host已有登录不自动证明新Host/Muse授权；应复用既有官方服务与登录流程，先只读accounts，不能私拷凭据或猜grant。
- HUMAN_REQUIRED：真实本人必须在原生宿主审阅精确内容后物理批准；能力/登录正常也不能免除。

## 请求中央串行调度（本聊天未执行）

1. 优先让中央对8d13132a组件安排一次隔离前台 `runtime.list`/Mail methods 探针，保存实际能力返回；不启动邮件审阅、无外发。建立二进制与构建源清单身份关系。
2. 若组件缺Mail，中央安排已有官方Intel Shell app-hub构建/独立窗口；复用官方注册及审阅组件，保留旧Host/安装与生产数据。禁止只给reference加假批准钩子。重构小Host审阅需额外评估完整ServiceHost/widget依赖，当前无可靠更小运行环境证据。
3. 中央在已有授权环境先查app可见accounts，明确能力缺失、登录缺失、前台缺失；无账号时本人用官方登录界面处理。本专项不读凭据。
4. 首次仅合成草稿→原生审阅→本人取消→compose_status，记录取消和Run恢复；再由中央计数安排本人自发自收批准。UNKNOWN仅查状态/收件不重发；accepted不是received，收到须独立收件核验。

这些请求是待调度项，无真实动作已批准/执行的新增声明。总体PARTIAL不变。

## 官方审阅最小接入候选（中央续派）

新增 `prepare_reference_mail.py`，要求 Python 3.11+（现场默认python3缺tomllib，已改用python3.12真实执行）。最新有效候选 **build/pivot-mail-reference-prepared-r3**；r1/r2为不含UI唤醒注册的中间产物，不要构建。未修改SDK、主源或原reference。

生成器将官方 `connected_review.rs` 原字节复制到隔离native，SHA `4ab475500052d01eaff30a9409c16c9d9ba594216580989440a94ccd14cd5726`；复制官方Mail/OAuth服务，保留方法、receipt、物理手势及失败保护。该原文件生产段没有crate/super引用；test段super::*为自身模块测试，不是Shell依赖。新增直接依赖 Mail、OAuth(host)、uuid；serde_json和Makepad沿用reference。OAuth依赖保留官方uuid/url/oauth2=5.0.0/reqwest配置及blocking功能，Mail包含keyring/apple-native、TLS、mailparse、scraper等。完整审阅原文件包含Gmail/Save变体，因此OAuth(host)不能省去，未注册OAuth服务，不新增代理。

注册顺序：真实 `mail_service::register()` → `public_review::on_review(Arc::new(connected_review::smtp_sheet))` → `connected_review::register()` → 官方 `drafts::on_change(SignalToUI::set_ui_signal)` → 原Calendar注册 → host启动/隔离VM创建。无register_demo、无假approve。生成源码及服务文件SHA清单在r3/prepare_report.json。

ServiceHost源码链已核对：reference `host.rs` 有独立sheet，`services::pump` 调度；`SheetOps::open_sheet` 检查may_prompt/hold_for_sheet；`apply_sheet` 取消旧heap再挂新body；可见sheet独占输入。官方 `public_review::open` 将smtp_sheet返回body交给host.open_sheet。此为源码支持证据，仍非已运行挂载或可信点击实测。

轻量结果：r3 `cargo metadata --offline --no-deps --format-version 1` exit0；完整offline metadata exit101，缺本地crates.io `dbus-secret-service`（经keyring解析到Linux secret-service依赖）。这是依赖解析阻塞，不是macOS运行要求，也不是审批失败。原错误在r3/resolution.log；尚未编译/GUI/送信。不通过删除Linux依赖或改审批来绕过。

资源：候选约1.2MiB源码；现场Data可用约14GiB。可复用 `build/official-hub-rc2-target` 的release缓存，但Mail/OAuth/TLS/keyring/reqwest增量未构建，时间与增量磁盘未知。中央应先恢复官方依赖缓存/允许依赖获取，锁定解析结果，再串行构建r3。准备报告提供准确build argv（offline当前会失败）；不要称locked或构建成功。

中央请求：构建r3 → 记录二进制SHA及注册ABI探针 → 隔离前台原生审阅取消测试 → app账号可见性 → 本人可信批准。没有物理手势时仍HUMAN_REQUIRED；UNKNOWN不重发，accepted不算收到。

## r4：修复crate文档位置与身份遗漏

中央指出的错误属实：r3在//! crate文档前插入mod，引发E0753。生成器已改为在原`mod args;`前插入`mod connected_review;`，完整文档保持在首项前；保留r3不改。**当前唯一待构建候选为 build/pivot-mail-reference-prepared-r4**，取代以上r3建议。

真实轻量核验：分别对r3/r4入口运行`rustc --edition=2021 --emit=metadata --error-format=json`，r3有22处E0753，r4为0；两次exit1，剩余E0432/E0433为没有Cargo传入依赖的外部符号解析错误。此检查证实文档位置回归修复，不等于完整编译、全部宏语法或类型检查通过。结果r4/entry_syntax_report.json，原诊断jsonl保留。未Cargo构建、未GUI。

r4 `cargo metadata --offline --no-deps` exit0。官方审阅原文件SHA仍`4ab47550...`，原字节未动。prepare_report.json的source_files现包含全部calendar/native/mail/oauth文件、workspace Cargo.toml和Cargo.lock；必需native/Cargo.toml、main.rs、host.rs、args.rs、connected_review.rs均在清单，实际逐文件SHA复核通过。生成器身份也记录。此清单是候选本地输入快照，**尚无输出二进制身份；外部path依赖源码也尚未全量冻结**，不能提前称完整二进制来源证明。

Lock来源：`build/pivot-builtin-calendar-original-r5/Cargo.lock`原字节复制；SHA `81c0ffab796304ed2241b2b7a4080736376e6aa0ae4d09127979587b8be5fed2`，r3/r4一致。这是Calendar构建种子，尚非Mail/OAuth已解析lock；报告seed_lock.status明确`SEED_NOT_RESOLVED_FOR_MAIL_OAUTH`。

中央下一步可仅联网fetch官方依赖，target为现场Intel macOS `x86_64-apple-darwin`；不删除Linux依赖。fetch/解析可能改变r4 Cargo.lock，须保留当前seed清单并新增post-fetch解析lock SHA及时间/命令，再以解析后的lock构建并记录二进制SHA、外部path依赖来源。不能用准备阶段seed SHA绑定后续变化的lock。本专项未fetch，也没有新建任何官方账号或触碰凭据。原生审批仍待本人，HUMAN_REQUIRED。
