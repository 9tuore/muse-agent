# Root最小fixtureCA Host构建与护栏提案

ZC02未编译或改共享SDK，正式R5/生产Host不动。Root按当前计划备份SHA确切network.rs、独立target构建后恢复源；新Host仅隔离测试，不出货。Main caa及原Kernel/签名bundle不变。

## 实际入口

SDK路径已核：Root `build/runtime-closure-full-shell-r1/sdk`；network.rs完整before SHA为`c47bfbd7529a88fda95bd24912bbb2fb0932a18c6726f45526cb3b6ae781ddba`。不要仅按行号套用。tls-fixture.patch是零context，Root隔离副本先`git apply --check --unidiff-zero`，应用后与tls-patch-identity.json的after SHA核对；这里的scratch检查已通过，类型/构建仍未验证。

已有官方构建包装入口：

```sh
python3 official_muse/integrated_release/build_host.py \
  --sdk "$FIXTURE_SDK" \
  --target "$REPO/build/sprint005/zc02-fixture-ca-target" \
  --out "$REPO/build/sprint005/zc02-fixture-ca-host"
```

FIXTURE_SDK/REPO由Root按实际临时SDK与worktree设置；本命令不由ZC02执行。脚本设置独立CARGO_TARGET_DIR，实际为offline+locked+release、package/bin均octosense、no-default-features，features `app-hub,octos-core,app-muse-native-prototype`。Cargo.lock前后SHA必须不变。不要误编R8 testbin、Mail helper或Kernel以替代GUI Host。

## 资源closure不能省略

build_host使用SDK desktop/scripts/package.py的package_env/build_env：macOS `MAKEPAD_PACKAGE_DIR=.`、`MAKEPAD=apple_bundle`、原deployment target/图标/strip及CARGO_ENCODED_RUSTFLAGS路径remap；有空格的路径不自行拼RUSTFLAGS。

build_host输出octosense和host-build-receipt，但**不自行stage资源**。新fixture package必须保留package_app.py所用的linked资源closure：cargo tree/metadata以相同features筛选git/path crate resources，stage `<crate_name>/resources/`，再放`Contents/Resources/host-runtime/`，muse-host与原octos-kernel及octos-kernel.json配对；原mirror/catalog与签名Muse bundle保持。Root可复用已核R5公共资源closure，network.rs没有新资源依赖，但必须核新Host的packaged mode及所有原资源存在，不能把裸release binary当可运行包。

配对package的Host SHA、动态签名、launcher/guardian receipt必须更新到新testHost；不能让旧Host SHA校验失败，也不能跳过校验。原Kernel SHA/receipt不改，生产默认状态不复制。9799及Root独占窗口不由ZC02触碰。

缓存：registry/git checkout已在只读观测中存在，13份rustls包缓存；中央及原始project build顶层无target目录，warm release artifacts未定位。最近历史Host全命令324.61秒不是本次ETA。Root若有已有兼容target可以选明确路径；否则该独立target可能重编依赖，不保证快速。先模型/GUI定位可继续，无需等待Mail构建。

## 只测新增CA护栏

ca_guard_tests.rs是**未执行的test-only提案**。将其append到已打CA patch的network.rs（仅临时SDK；Root做，仍不动正式Host），只跑一个exact test：

```sh
SPRINT005_TEST_CA_DER="$STATE/public/mail-fixture-ca.der" \
CARGO_TARGET_DIR="$REPO/build/sprint005/zc02-fixture-ca-target" \
cargo test --offline --locked --release -p octosense-mail-service --lib \
  network::sprint005_fixture_tests::sprint005_ca_guard_matrix -- --exact --test-threads=1
```

执行cwd为实际FIXTURE_SDK；使用公开generated CA，不读取私钥或production credential。该matrix覆盖：无env返回原路径、正确doublemarker/profile/filevault/loopback允许且DER可加入RootStore、非127/localhost/IPv6及拼接域名拒绝、Keychain模式拒绝、profile不同、缺owner marker、legacy marker、坏配置、CA SHA错、CA超限、symlink拒绝。只新增护栏测试，不重复107 Mail基线；libtest不代表GUI。

Root若不希望额外test-target，可先typecheck/构建Host后在独立SDK测试driver直接调用原Network::test到fixture IMAP：无override的自签名TLS必须失败；严格override成功；错误CA/profile/marker必须失败且不发送LOGIN。还需Leaf名称错误/不可信证书保持原rustls拒绝，最后由ZC05真实GUI login→review→Network send_checked→独立receiver及UNKNOWN新进程恢复验收。我们不会用模拟receipt或direct grant填补这层。

launch-environment本身不启用CA；Root专门testHost才用tls-proposal-environment，MUSE_INTEGRATED_STATE与CA root必须相同，MAIL_VAULT=file。服务器地址GUI输入严格127.0.0.1，端口取真实ready.json；SMTP只接收合成域且不relay。真实生产新批准仍HUMAN_REQUIRED，不再申请权限。
