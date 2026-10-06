# 运行指南

## A. 评委快速体验

1. 在 **Intel Mac，macOS 14 或更新版本**解压 `Muse-Tmall-Submission.zip`。
2. 双击 `RUN_MUSE.command`。脚本检查 Runtime 签名与固定摘要；首次显示应用中心，点击 Muse，按应用中心的正常安装路径安装并打开。再次运行脚本会直接打开已安装的 Muse。
3. 在 OctoSense「AI 模型设置」选择可用模型；在 Muse 的「邮箱」通过宿主连接自己的邮箱，「日历」按系统提示授权并选择目标日历。
4. 从自然语言聊天或新来信开始。外部写入按实际确认卡操作。没有配好 Provider 时应处理错误提示，不能把本地模板当 AI 成功。

QQ 示例：完整邮箱地址；IMAP `imap.qq.com:993` TLS，SMTP `smtp.qq.com:465` TLS；填写**授权码**。在 QQ 邮箱网页的设置中查找 POP3/IMAP/SMTP 服务并生成授权码，具体入口以用户账号当前界面为准。不要将授权码发到聊天或写入作品资料。

本包不下载模型或执行未知二进制，不保存凭据，也不更改系统安全设置。首次安装依照 App Hub 的目录、完整性和权限检查。Runtime 为本地开发签名，未经 Apple 公证；若系统阻止运行，按组织/个人安全政策处理，不提供关闭安全保护的脚本。

本包运行资料保存于 `~/Library/Application Support/Muse Tmall Experience rc51/`，与已有 Muse 测试、生产资料分开。运行日志可能含运行内容，只保存在该目录，不能随作品上传。

同一体验入口禁止重复启动。异常退出后若提示启动锁，没有活动窗口时可检查该资料目录中的 `launch.lock/pid`；不清空应用历史或账号来修启动问题。空锁或目录中有其他文件时入口停止并报错，需人工检查。

### 启动前只检查

```sh
sh RUN_MUSE.command --check
```

只验证平台、Runtime 签名、固定摘要和核心版本，不开窗口、不创建资料目录、不授权账号。

## B. 开发复现

需要 Git、Python 3、Rust/Cargo 与 macOS SDK/Xcode Command Line Tools。源码身份见 [清单](source/SOURCE_MANIFEST.md)，固定基线为 `7175af663c55703959b481791a304196343df5b6`；包装分支为 `codex/tmall-submission`。

```sh
git clone https://github.com/9tuore/muse-agent.git muse-tmall-dev
cd muse-tmall-dev
git checkout 7175af663c55703959b481791a304196343df5b6
python3 scripts/bootstrap_sdk.py
python3 scripts/bootstrap_sdk.py --verify
cd vendor/octosense
cargo build --release --locked -p octosense --bin octosense --no-default-features --features app-hub
```

bootstrap 从锁文件中的官方 pin 下载源码，再应用仓库内的准确 overlay，并核对文件摘要、模式和链接；不会运行第二套模型代理。Calendar Extension 的源码就在 `sdk-overlays/octosense/apps/calendar/host-service/`。

开发窗口可沿用同一 Shell：

```sh
# 在上面的 vendor/octosense 目录中；这是开发构建，不等同于交付 Host 的签名身份。
OCTOSENSE_HOME="$HOME/Library/Application Support/Muse Tmall Development/home" \
OCTOSENSE_APP_DATA="$HOME/Library/Application Support/Muse Tmall Development/apps" \
cargo run --release --locked -p octosense --bin octosense --no-default-features --features app-hub -- --test-action launch-apphub
```

运行本地 Muse bundle 时，使用同一版本的配套目录与正常 App Hub 安装路径。重建 Host 如需系统日历授权，应按现有 `official_muse/rc/packaging/package_host_candidate.py` 的资源布局与 Info.plist 方法打包；不要拿旧身份下的授权或结果冒充新构建。此脚本读取历史构建报告，不能未经准备直接执行；配套已构建 Runtime 可通过本包快速体验运行。

本次验证的“Clean restore”覆盖 ZIP 全文件还原、模式/链接、Runtime 验签/摘要、bundle 一致性，以及固定 Git 源码提取。没有重新进行耗时的完整 Rust 编译或宣称换机成功。
