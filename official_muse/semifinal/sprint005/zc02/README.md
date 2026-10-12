# ZC02 SPRINT-005：独立SDK GUI的合成输运

2026-10-12。当前Main caa99c57，SDK文件身份见source-identities.json。ZC02只拥有本目录和自有测试；Root生产9696窗口、profile、邮箱、Keychain、Secret及真实发送均不操作。不替GUI直接写账号/grant/draft/Memory库，不把服务协议测试当GUI通过。

## 最低可执行接入方案

1. 用bootstrap.py在全新build目录创建双FIXTURE_ONLY标记、合成TLS CA及server证书，绝不复制既有profile。私钥仅本机private目录，600权限、不入Git或日志。
2. serve.py提供127.0.0.1上的TLS IMAP/SMTP、无key OpenAI兼容模型及fixture控制API。SMTP只接收sprint005.example.invalid地址，无relay、无外网发送；独立receiver子进程保存实际DATA和Message-ID，UNKNOWN模式在实际收件后断连接，不返回250，SDK必须自己判UNKNOWN。
3. 独立GUI进程以此新root启动，设置已有OCTOSENSE_MAIL_VAULT=file。账号必须在官方mail.add_account原生sheet输入并验证；caller grant与review/物理批准仍走原SDK。控制API只改变服务器测试行为，不提供批准或SDK状态写入接口。
4. 模型在原设置sheet选择Ollama / Custom endpoint / OpenAI协议，模型sprint005-fixture，base_url为服务输出的http://127.0.0.1:PORT/v1，key留空。实际provider test/models/complete走SDK；响应内容是显式fixture，不能称真实模型推理。

**Mail接入依赖：**network.rs只信任WebPKI根，现有GUI无CA导入参数，OS Keychain添加CA对这一路径无效。普通自签名服务在未改SDK时应TLS验证失败。提交给Root的tls-fixture.patch仅添加双标记新profile中的指定公共CA，必须MUSE_INTEGRATED_STATE与fixture root一致、OCTOSENSE_MAIL_VAULT=file、host严格127.0.0.1；fixture模式的非loopback连接在DNS前拒绝。仍保留原rustls hostname/链/有效期验证，未用danger verifier/明文/standing授权。需Root在隔离GUI Host中采纳并构建，ZC02不应用或编译共享SDK/target，R5保底不动。补丁未编译前只能报服务/静态准备，不能报SDK GUI Mail通过。

## 统一协议

启动输出ready.json含真实绑定端口；不占9696。默认端口0由OS分配，仅绑定127.0.0.1。

- GET /__fixture/status：实际协议计数、当前case、模式和public TLS身份。
- POST /__fixture/mode：{case_id, smtp_mode: accepted|before|unknown}。before在DATA前拒绝；unknown收齐DATA并交独立receiver后断开。
- POST /__fixture/incoming：{account, subject, body, sender?}，只注入服务器合成邮箱，经真实IMAP由SDK读取；稳定UID、不改SDK数据库。
- POST /__fixture/model：{case_id, response, mode?: normal|http_error|malformed, delay_ms?}，响应仅模型输运fixture。
- GET /__fixture/receiver：独立收件日志摘要，实际Message-ID/内容SHA及重复计数。
- GET /v1/models，POST /v1/chat/completions：官方SDK兼容的模型list/probe/complete。

GUI账号：gui-reader@sprint005.example.invalid、gui-alt@sprint005.example.invalid、receiver@sprint005.example.invalid。仅合成输入，公共测试口令SPRINT005-SYNTHETIC-ONLY；不要填真实凭据。IMAP/SMTP服务器均127.0.0.1，端口取ready.json，TLS保持启用。

readback.py仅接受同双标记root；白名单读取Muse Memory/Goal/Run/Action/Source等JSON及合成SDK Mail drafts，跳过vault/keys/secrets。摘要和断言使用ID、scope、哈希及真实计数；不回写、不补receipt、不制造PASS。可对两次snapshot验证UNKNOWN重启后compose/attempt/Message-ID及独立receiver计数不增长。项目作用域和遗忘/冲突由GUI真实动作后独立读回，fixture控制端不直接造业务状态。

所有服务和读回结果注明fixture层、SDK层、GUI层及未验证项；243格最终由ZC05/Root实际GUI证据逐项决定。不要重复既有107 Mail/组件测试。

## 可复用CLI与formal-r3接入状态

从已接收本目录的worktree执行，ROOT取全新build路径：

```sh
python3 official_muse/semifinal/sprint005/zc02/bootstrap.py --root "$ROOT"
python3 official_muse/semifinal/sprint005/zc02/serve.py --root "$ROOT"
# 服务启动并写ready.json后，另一终端只准备服务配置：
python3 official_muse/semifinal/sprint005/zc02/prepare_profile.py --root "$ROOT"
python3 official_muse/semifinal/sprint005/zc02/readback.py --root "$ROOT" --out "$ROOT/snapshot.json"
```

prepare_profile依照SDK config/profile.rs及实际real_kernel_tests::write_profile的完整_main envelope：id/name/enabled/created_at/updated_at/config.llm.primary(family_id=local,model_id,route)，不含key或keychain marker。已有文件拒绝覆盖。实际WorkBuddy launcher无条件将OCTOS_APP_CORE_DIR设为新root/kernel/.octos，prep已按此正式路径生成，SDK dirs.rs因此不迁移个人共享profile；OCTOSENSE_LLM_VAULT=file与MAIL_VAULT=file均为已有官方模式。核心业务库没有预写，所有聊天/记忆/事项由真实GUI创建。首个13:41前版本用了通用octos-home/.octos，已按Root现场路径修正；旧自有测试目录保留，不能使用旧路径作为GUI配置。

同模型服务支持Kernel stream SSE及只从原native prompt选择实际offered Calendar工具，创建get使用实际上一条tool result的ID，update/delete保留原expected；实际error立即停止。仅选择工具，不创建Broker history/receipt或批准。原NIGHT004 Rust bridge是CLI且限制旧root，不把它冒充本GUI入口；这里只复用其公开profile与plan_model算法。formal-r3的真实Kernel仍走原GUI/apphub准入及审批。

**formal-r3 Host保持不变时：Mail可信CA接入是HUMAN_REQUIRED/专门fixtureHost依赖。** 不能让现有WebPKI接受本地自签名证书，不能通过seed账号/grant或明文来跳过登录。模型、只读工具及服务器协议已可独立使用；TLS补丁只是Root可选择的隔离Host提案，未应用/编译。default launch-environment不带该TLS override；只有tls-proposal-environment供接受提案后的专门Host使用。9799由Root后续分配，本服务当前OS动态分配端口，不触碰9696。

首个实际本机服务检查17/17、真实HTTP SSE及公开profile匹配4/4通过，均为新fixture组件；Kernel/SDK GUI NOT_TESTED。readback当前只验证snapshot-only出口，进一步定向validator验证与完整接收记录继续在本目录记录。

另已核官方SDK无编译mail_demo开关：Shell apps.rs register_mail_services读取MAKEPAD_APP_CONFIG.mail_demo并调用register_demo；口令demo、三封固定合成INBOX及Sent样本，FileVault、零网络、发送去往无处。原登录sheet、SDK draft/review/批准路径仍走GUI。它不能证明独立收件/UNKNOWN，也不能修改来信内容。**实际WorkBuddy launcher会unset MAKEPAD_APP_CONFIG**，故不能仅传env宣称启用；需Root的隔离launcher明确保留该官方配置，且双marker约束，生产launcher默认不改。现有R8 JSONL测试driver没有native GUI事件循环，其MockTransport/内部sheet调用不能替代GUI验收。

tls-fixture.patch改为零context：Root先核tls-patch-identity的完整before SHA，再在隔离SDK执行git apply --check --unidiff-zero；这里只提案，未编译或写共享源。
