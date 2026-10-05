# rc51 整体展开包交付

**状态：PASS_DISTRIBUTION_ONLY_PRODUCT_PARTIAL。**完整分发封装的体积、还原与资源验证通过；整个 Muse 产品仍 PARTIAL。没有启动 GUI、调用模型、发信、改日历或进行两台接收 Mac 测试。

## 实际文件与身份

- ZIP：`/Users/mima0000/Desktop/Muse-0.3.26-rc51-Intel完整展开包-a4cf4d9e-2026-10-06.zip`
- ZIP 大小：**492361442 字节**，严格小于 500000000，余量 7638558 字节。
- ZIP SHA256：`e7a80d006443352932784e3f5b56304dec66106c71f59ff1764a24905d8a6c65`
- 桌面对应文件夹：同名无 `.zip` 后缀，包含标准完整内容 tar.xz、展开启动命令、说明、完整清单及新分发工具源码。
- Payload tar.xz：491626268 字节，SHA256 `a9c92d341f672b50af41cbd889bf4a7a6832a849eaeda7c80ed51f995adb8c35`。
- 产品源码 F：`a4cf4d9e6cd3ff1067e2821a29d4e5be48d2ad39`；原完整 **2180 文件 / 199506103 逻辑字节**保持，逐文件 SHA、mode、集合实际复验。
- 原全部内容逻辑大小：691629674 字节；模型权重、原 `.app`、Host、签名、源码和支持资料字节未改。唯一未重复放入的文件是从完整展开源码生成的 `04-公开源码-a4cf4d9e.tar.xz`；它的原件和首次失败 ZIP 仍保留。
- 新分发工具实现提交 `d27c3d52`，工具 SHA256 `bdda3ace14a9ded542e80bf497ea33155bcd334030888ade1aa55c28614499c2`；这是分发调整，不是 F 的产品功能升级。工具源码随 ZIP 交付。

首次 527708351 字节超限包的失败没有覆盖。本次唯一整体 XZ 尝试用标准 preset9；ZIP 全部成员明确 STORED，避免无效二次 deflate。没有拆出唯一源码或删历史证据来达成体积门槛。

## 如何打开

1. Finder 双击 ZIP 解压。
2. 阅读 `01-先看这里.txt`。
3. 双击 `00-展开并启动.command`。它使用 macOS 自带工具核对完整 tar 的 SHA、首次展开，验证原应用签名和资源，再请求 macOS 打开原 `.app`。
4. 首次完成后，原 `Muse 0.3.26-rc51.app` 和完整 F 源码都在展开的内容子目录内；以后可以直接双击原应用。

Intel Mac / macOS 14+；不需要 Python、Rust、Git 或第三方解压软件来运行。首次展开需要约 700MB 以上额外空间；当前压缩包解压到外层也要占空间。保留原 ad hoc 签名与既有系统安全流程，没有公证或新正式签名；系统许可仍由使用者按意愿处理。

原支持资料完整保留。其旧教程描述的“单独源码 tar.xz”属于前一次分发形式；本包整体展开后源码已完整展开，无需寻找该重复归档。

实际新版 96 秒中文视频独立交付：`/Users/mima0000/Desktop/Muse-0.3.26-rc51-本轮实录.mp4`，2439624 字节，SHA256 `5cecf600c6d4a18b0217a0f08f97b76648598a559b1b69cb80b0003375361f21`；没有用旧 rc49 视频。该视频也是 F 的已跟踪文件，完整源码内保留它。

## 真正执行的验证

- 小合成测试：Unicode、exec mode、symlink、系统 tar 还原、STORED ZIP CRC/SHA/mode；损坏 SHA、路径逃逸、应用缺失时明确拒绝，没有假启动。
- 一次实际完整 XZ 压缩；验证 tar 的全部成员、类型、mode、安全路径、相对 symlink 和精确集合。
- 严格小于 500000000 的实际 ZIP 大小检查。
- 独立 ZIP 解压，原生执行新命令 `--check-only`，使用 macOS tar 完整展开；没有调用 `open`。
- 完整原 payload 及 F 源码逐文件 SHA/mode/集合/symlink 一致。
- 原 `.app` strict deep codesign 与 Launcher 资源 `--check` 通过。
- 解压后本地扩展 Hub verify/check/scan 通过；不等于上游 Calendar 准入或官方 full-chain。
- Root 另做 ZIP 容器、CRC、STORED、命令0755及身份独立核对，记录在其 DELIVERY_ROOT_VERIFICATION.json。

启动命令错误时明确输出并停止；校验或资源检查失败不创建成功标记、不请求打开应用。实际 native 窗口、模型质量、同最终外部业务整链及两台 Mac 尚未因包装测试升级为通过。

## 时间与空间

整体压缩 605.37 秒；tar 成员验证与分发准备 54.79 秒；独立还原和资源检查 82.91 秒；总计 **765.2 秒**。其余时间为输入核对、ZIP 写入与摘要等开销。

Root 明确授权且所有还原验证通过后，已仅删除 `.local-state/independent-envelope` 这份可重建副本；删除前保留完整实际 inventory、SHA、报告和命令/Hub 日志。验证副本逻辑大小 1183989217 字节，删除后可用空间从 586915840 增至 1778315264 字节。桌面整体包、原 `.app` 和源码 stage、旧49、首次超限包及唯一失败证据都保留。

依据见 RESULT.json、PAYLOAD_INVENTORY.json、VERIFIED_EXTRACT_INVENTORY.json、VERIFIED_REPLICA_CLEANUP.json；不提交包、权重或 private，不 push。
