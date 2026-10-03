# 邮箱登录简化：0.3.3 UI-candidate

状态：隔离 Release Host、严格 ad hoc 签名、实际空白登录表单验证 PASS；真实账号登录 WAITING_USER。

已读Host根目录与apps/AGENTS.md。基线是无Git元数据的本地OctoSense源码快照，无法用上游commit代表；逐文件SHA登记在 `ui_memory/host-login/source_provenance.json`。Git提交使用当前仓库已配置的公开noreply身份，交付基线到patch，不伪造原Host Git提交。

修改范围只限隔离副本的 `apps/mail/host-service/src/lib.rs`：删除username widget/提交绑定；新登录回调忽略单独username，使用trim后的完整邮箱地址；保留ACCOUNT_FIELDS和旧账号读取、IMAP/POP3/SMTP/TLS、原Calendar服务。

隔离源码/构建：本仓库 `official_muse/app/build/ui-memory-20261003/mail-host-033/OctoSense` 与独立target。依赖目录只读复用既有锁定来源；执行setup检查模式，不对共享依赖运行迁移/更新。原Host源码、运行二进制、账号/用户数据和8401窗口不修改。

2026-10-03 本机验证：mail-service Rust测试 11 passed / 0 failed / 2 ignored（真实 Gmail、Keychain 原测试保留 ignored）；锁文件离线 Release 构建 PASS，功能仅 app-hub，与旧候选一致；独立 .app 严格签名验证 PASS。端口8495运行新包的真实 Host sheet，mail_demo 使用文件 vault、无网络/Keychain；空白凭据、无 username widget、密码或授权码标签、IMAP 993 到 POP3 995 切换和 SMTP 465读回通过。两张截图已直接查看，表单内容正确；表单本身可滚动，顶端取消/登录始终可见。未输入凭据、未提交登录，随后取消并退出该实例。

候选应用：`app/build/ui-memory-20261003/mail-host-033/OctoSense Muse 0.3.3 UI-candidate.app`。独立 bundle id 为 `dev.makepad.octosense.muse.mail033.local`，仅本地 ad hoc 签名。二进制冻结 SHA256：`f5989ea3b5a80a357eda4fde5a64684f4adc7e0c0b441f46b8c706845dd5f215`。未安装、未覆盖旧版、未公开发布。此包是 Host；Muse 已冻结 0.3.3 bundle 的安装和其余验收由总控负责。

从仓库根目录运行 `python3 official_muse/ui_memory/host-login/launch_host.py` 可启动普通候选，使用独立 `user-candidate-state` 空数据；不会复制生产账号。`--demo-ui --hidden --port 8495` 使用单独 `ui-probe-state` 无网络演示服务；随后 `probe_login_ui.py --port 8495` 只点添加账号、协议切换、取消，不点登录。若端口已有实例，启动器拒绝覆盖。

基线→patch、锁文件与原Host SHA复核、测试/编译/setup日志、打包与界面JSON、实图位于 `ui_memory/host-login/`。修改后 mail lib SHA256 为 `bebdedd540046c1d8839433e47aad2f233a59707568dd3d21edcc9dfad8948b5`；网络、Calendar lib/EventKit、Cargo与运行时锁文件及原Host二进制逐项复核未变。ACCOUNT_FIELDS保留username、旧账号读取路径未变；未以真实旧账号迁移测试作为证据。

官方 setup检查确实失败：`Expected an empty dependency directory: .sources/octoscript-makepad`。这些是原锁定快照的只读链接，没有改共享依赖以绕过检查；实际 locked/offline Rust测试与构建通过。初次 UI启动把manifest ID `os.mail` 当启动ID，日志明确未找到应用，已依源码改为 `launch-mail`；立即重启8494遇 TIME_WAIT，保留失败并改用空闲8495后通过。未把失败算作成功。

准备阶段第一次临时脚本发生UTF-8解析失败，随后缓存拷贝因目标目录未创建而退出；未创建隔离副本、未修改原源/缓存。改用保存的ASCII准备脚本并在失败时停止后续步骤。

未完成项：本人在新 Host sheet输入实际邮箱和密码/授权码后，才可验收真实账号登录。新bundle身份的系统日历权限也需本人按实际提示决定；本次未申请权限或做任何真实日历写入。登录UI移除字段的范围已完成，不能据此宣称网络登录错误的所有原因已消除。
