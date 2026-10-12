# Root / ZC05实际接入与编译边界

## 无key模型与新profile：无需Rust构建

先bootstrap新root并启动serve；再prepare_profile。实际_main位置是**root/kernel/.octos/profiles/_main.json**，与正式WorkBuddy launcher一致；完整public envelope/primary family local/model/route，env_vars为空，没有生产数据或keychain marker。launch-environment要求MUSE_INTEGRATED_STATE新root、OCTOS_APP_CORE_DIR同路径、OCTOSENSE_LLM_VAULT=file、OCTOSENSE_MAIL_VAULT=file。明确CoreDir使SDK不进入个人共享profile迁移。

serve提供真实HTTP /v1/models及chat/completions JSON/SSE；Kernel native prompt仅选择实际offered Calendar events/add/get/update/remove，args从原text解析，旧expected不换、create get的ID来自实际tool result，actual error停止。它不造Kernel结果/history/receipt或批准。Root formal-r3原Kernel/Host/Broker/AppHub准入保持，9799由Root分配。ZC02未启动这些GUI/Kernel，Source schema来自官方config/profile.rs、kernel/dirs.rs与真实write_profile测试。

可用模型响应由控制API显式设置，例如chat的response应匹配Main该请求的实际schema；无schema时拒绝猜造PASS。delay_ms用于真实晚回包，http_error/malformed产生真实HTTP/JSON错误。LLM调用不是实际远程模型推理。必须实际GUI创建聊天/记忆/事项；prep不写业务库。

## Mail基础GUI：官方demo入口及其限制

当前SDK crates/shell/src/apps.rs:175/197读取MAKEPAD_APP_CONFIG.mail_demo，进入原mail::register_demo，使用FileVault和官方DemoTransport；**无需重编译SDK**。原账号登录sheet输入公共demo口令、固定合成Inbox三封/Sent样本、原SDK draft/edit/review/批准/accepted状态可从真实GUI验证；不调用网络或Keychain。

但正式workbuddy_launcher.sh清除MAKEPAD_APP_CONFIG。仅传环境变量不能生效，Root需在独立双marker测试launcher中明确保留/设置该官方配置，生产默认launcher和R5保底不动。不要重新启用被正式launcher清除的dev_mode、grants_all或不可信Kernel路径。Demo不验证真实TLS登录，发送去往无处且没有独立收件或可配置UNKNOWN；这些格不能由demo accepted升级通过。

R8现有night004_kernel_jsonl_bridge_fixture_driver是libtest入口，初始化services、CLI stdin/JSONL与pump，不创建Native GUI事件循环。Mail runtime helper同样用内部ServiceHost记录sheet而非真实窗口。**不能直接把R8 MockTransport测试当GUI验收**。SDK公开register_with/register_with_vault可供专门fixtureHost接入，但没有发现R8/正式Host的通用GUI MockTransport CLI开关。

## 真Network路径的隔离TLS：仅Root决定/构建

tls-fixture.patch只改Mail network.rs：无fixture env时原WebPKI行为；开启时profile匹配、FileVault、双exact marker、canonical/nonsymlink CA及SHA，host严格127.0.0.1并在DNS前拒绝其他host。仍由rustls验证链/名称/有效期，不使用dangerous verifier或明文。此为未编译提案，不在正式R3/R5上应用。专门隔离Host可让GUI账号输入走真正Network::test/IMAP，再实际SDK review/send_checked经loopback SMTP把DATA送独立receiver；before在DATA前拒绝，unknown在收到完整DATA后无250断开。

Root实际现有构建入口已核：

```sh
python3 official_muse/integrated_release/build_host.py \
  --sdk <Root的隔离SDK副本> --target <Root明确选择的隔离或可复用target> --out <新fixtureHost输出>
```

其实际命令为cargo build --offline --locked --release -p octosense --bin octosense --no-default-features --features app-hub,octos-core,app-muse-native-prototype。不需重编Kernel或修改Main；Mail crate及最终Host链接会受network.rs变化影响。先核完整before SHA，再git apply --check --unidiff-zero；当前提案只在自有scratch通过check/apply及after SHA，未typecheck或编译。

缓存只读观察：标准registry/cache及git/checkouts存在，13个rustls crate包已缓存；中央和原始项目build顶层未找到target目录，不能声称有warm release target或完整离线依赖。最近可读mail-lifecycle-host-r1 receipt记录上述Host全命令成功324.61秒，只是历史观测，不能当本次增量ETA。优先先用模型+官方demo/读回；不要为未知cache或内部测试盲目全量重编。Root若决定CA Host构建，先确定实际可复用target并保留新包及构建证据，R5保底不动。

## 独立只读验收

readback.py白名单读取新doublemarked Root的Muse业务JSON、SDK box消息body hash和draft状态/attempt/Message-ID；不枚举vault/keys/secrets，不输出密码/能力token，不回写。mail_source_ids可要求Source SHA与实际SDK缓存Mail正文哈希一致；retrieval_scope+retrieval_expected_ids可检验项目/owner/account隔离及确切召回。forgotten_claim_ids要求内容/历史/source_ids清空。unknown_no_resubmit必须给同profile真实before snapshot，要求实际unknown已存在、同draft/attempt/payload及独立receiver计数不增；无unknown、空expected、不同profile或坏/链接文件均不能PASS。

只有snapshot时输出SNAPSHOT_ONLY。实际功能验收需ZC05 GUI动作和明确expected断言；18项validator/parser测试仅unit root，绝不作为GUI业务seed或243格结果。证据层和HUMAN_REQUIRED保持明确，不再申请新生产权限。
