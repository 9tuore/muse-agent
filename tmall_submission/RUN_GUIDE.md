# 运行指南

完整中文操作教程见 [使用教程](使用教程.md)，包含 QQ 授权码获取与两版入口。

## A. 评委快速体验

1. 在 **Intel Mac，macOS 14 或更新版本**解压 `Muse-Tmall-Submission.zip`。
2. 双击 **Muse.app**，或 `RUN_MUSE.command`。原生入口校验整包签名，自动启动随包 Qwen2.5-0.5B Instruct 基础离线模型、建立本机官方模型配置。首次显示应用中心，点击 Muse 并确认正常安装、打开；以后直接进入已安装的 Muse。
3. 基础聊天无需模型账号、API Key 或额外下载；已有有效模型配置不会被替换。需要真实业务时，在 Muse 的「邮箱」通过宿主连接自己的邮箱，「日历」按系统提示授权并选择目标日历。复杂任务可在 OctoSense「AI 模型设置」选择更强模型。
4. 从自然语言聊天或新来信开始。外部写入按实际确认卡操作。结果来自官方 model.complete 的真实调用，不使用模板冒充 AI。离线模型只用于基础体验，复杂安排、长上下文与起草的准确率仍有限。

QQ 示例：完整邮箱地址；IMAP `imap.qq.com:993` TLS，SMTP `smtp.qq.com:465` TLS；填写**授权码**。在 QQ 邮箱网页的设置中查找 POP3/IMAP/SMTP 服务并生成授权码，具体入口以用户账号当前界面为准。不要将授权码发到聊天或写入作品资料。

模型权重、Intel 推理组件、来源锁与许可已随包附带；只绑定本机回环端口，不联网下载、不携带账号凭据、不更改系统安全设置。用户连接邮箱时，凭据仍由宿主按自身体系保存。首次安装依照 App Hub 的目录、完整性和权限检查。Runtime 为本地开发签名，未经 Apple 公证；若系统阻止运行，按组织/个人安全政策处理，不提供关闭安全保护的脚本。

本包运行资料保存于 `~/Library/Application Support/Muse Tmall Experience rc51/`，与已有 Muse 测试、生产资料分开。运行日志可能含运行内容，只保存在该目录，不能随作品上传。

同一体验入口使用进程文件锁防止重复启动，退出后系统自动释放；退出配套 OctoSense 会结束入口及它自己启动的离线模型，不影响其他服务。运行资料留在本机，不随包提供。

### 启动前只检查

```sh
sh RUN_MUSE.command --check
```

只验证平台、整包签名、模型/Runtime 资源和核心版本，不开窗口、不创建资料目录、不授权账号。

需要打开官方模型设置时：`sh RUN_MUSE.command --models`。离线模型使用 CPU 4 线程、4096 token 上下文；不属于强模型验收。

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

本次验证的“Clean restore”覆盖 ZIP 全文件还原、模式/链接、Runtime 验签/摘要、bundle 一致性、固定 Git 源码提取，以及全新目录恢复五套准确SDK并独立核对12,000个文件。首次网络TLS失败保留，重试恢复通过。没有重新进行完整 Rust 编译或宣称换机成功。

重建比赛 ZIP 时，从本任务的 `codex/tmall-submission` 包装提交运行 `build_submission.py`，传入已验证的 Host 应用、配套 mirror、`--model-root` 模型组件目录和全新输出目录。模型目录必须与 `runtime/MODEL_LOCK.json` 中 22 项文件/链接、大小与摘要完全一致；不能混入账号资料。构建原生入口需 macOS SDK/clang；最终 ZIP 采用标准 ZIP 压缩并硬性检查小于 500,000,000 字节。工具读取固定基线Git对象；不要在单独桌面材料目录中运行它。Git不会重复提交Host二进制，发行ZIP由允许清单附带。
