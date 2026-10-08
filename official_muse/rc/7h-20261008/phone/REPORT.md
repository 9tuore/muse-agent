# Muse 7H · Android 平台检查与候选补丁

开始：2026-10-08 19:43:07；截止：2026-10-09 02:43:07（北京时间）。

本目录只交付源码检查、隔离构建与候选补丁。未安装手机应用、未操作 ROM、未修改共享 SDK。没有连接设备，真实手机运行状态为 `DEVICE_NOT_TESTED`。

## 当前已验证结论

| 项目 | 判定 | 证据 |
|---|---|---|
| Phone Home 与 System Bridge 路线 | SUPPORTED，源码契约已核对 | Home 使用同一 `octosense-shell`；Bridge 通过受认证 Binder/AIDL 提供系统能力 |
| 第三方 OctoScript 应用发现与加载 | SUPPORTED，已有实现 | 安装清单 → `hub:<manifest-id>` → 同一 Card runner；安装/更新后失效缓存 |
| 应用发现边界修补 | 候选测试 PASS | 原 8 项测试 3 PASS / 5 FAIL；修补后 13 项 Appstore 测试全过 |
| 签名、平台、权限准入回归 | 源码测试 PASS | App Policy 22 项单元测试 + 1 项文档测试；未改 launch 准入路径 |
| cargo-makepad 构建 | PASS | 固定源码、`--locked --offline --release` 构建成功 |
| 官方 Android 工具链 | 隔离准备完成 | JDK 17.0.2、Gradle 8.11.1、SDK 35/33-ext4、Build Tools 35/33.0.1、NDK r28b；发布摘要全部核对 |
| Home/Bridge APK 构建 | IN_PROGRESS | 实际构建日志继续保留在 `evidence/` |
| 官方源码身份检查 | BLOCKED | 冻结交付 SDK 不含 Git 元数据；`tools/setup.py --check` 拒绝，不绕过此门槛 |
| Muse Android 日历 | MISSING_CAPABILITY / NEEDS_HOST_PATCH | 当前 Calendar Host 是 macOS EventKit，非 macOS 明确返回 unavailable |
| Muse 手机全链与视觉 | DEVICE_NOT_TESTED | 未连接一加 6，也未取得模拟器运行证据 |
| 上游接受补丁 | 未接受 | 仅本地候选；没有 PR、发布或推送 |

## 官方路线与实际缺项

固定 OctoSense `7f962547cd8035ed2bb05962cf7824d8aa33e3a3`；App Hub `e8601b80ce104db2e48208094714bdcffdce6b5a`。其他固定来源见项目 `dependencies.lock.json` 与隔离 SDK 的 `SNAPSHOT.json`。

Home (`phone/`) 与桌面共用 `crates/shell`，不是另一个 Muse Runtime。Android Home 启动同一官方 octos 内核；原有 `rom/scripts/build-home.py` 将内核打包为 `liboctos.so`。Bridge 独立 APK 验证 Binder UID、用户、包和证书；公开开发签名只用于测试，不建立生产身份。原有 root 控制仍为显式可选路径。

App Hub 原先已经读取安装目录并将应用加入启动列表。Shell 将清单 ID 变为 `hub:<id>`，Card 通过既有 App Hub 校验加载。安装与更新会让图标、启动列表和旧 Card 缓存失效。本轮没有重复实现这一机制。

Muse 当前 listing 只声明 macOS。Android 邮箱有真实网络服务和 Keystore 分支，模型沿用官方 `model.complete`/provider 契约；这些只能说明源码存在，不能当作手机运行通过。现日历实现仅有 EventKit，没有 Android CalendarProvider 适配，因此不能把 Muse 直接改成 Android 可安装全功能应用。

## 跨平台复用评估

| Muse 组成 | 结论 | 条件 |
|---|---|---|
| 一次性事项、Memory DSL、去重与恢复 | 可原样复用业务源码 | 复用官方 app-scoped Storage；不迁入私人桌面数据 |
| Model contract | 小幅兼容 | 手机需独立配置已授权 provider；成功回复不是系统动作回执 |
| Mail adapter | 需要手机运行验证 | Android Keystore、账号登录、网络与后台生命周期仍需实机检查 |
| Calendar adapter | 需要宿主支持 | 要先实现并审查 Android 日历查询/写入/独立读回契约 |
| 结果卡 | 可复用语义；视觉需验证 | 使用现有 Splash/Card runner，不换技术栈 |
| 三栏 UI | 小幅兼容，未验收手机像素 | 纵向手机要使用现有折叠行为；不能由桌面宽屏截图推定可用 |
| ROM 集成 | 暂不执行 | 不刷机，不替换系统组件，不授予 root |

## 最小候选贡献

`patches/app-hub-installed-discovery.patch` 仅修改 `crates/appstore/src/lib.rs`：

1. 清单 ID 必须等于安装目录名。
2. 清单最多读取 64 KiB，并在实际读取时继续限制增长。
3. 安装目录、bundle、manifest 的规范路径必须分别留在所属根内。
4. 坏清单、缺目录和坏 UTF-8 不阻止其他正常应用被发现。

显式指定的安装根本身可以是软链接。签名、摘要、平台、publisher 与 capability 验证仍由原有 Card launch 执行。这个补丁加强发现边界，不把启动列表当作授权凭据。

证据：`evidence/discovery-before.log` 保留 5 项失败；`discovery-after.log` 为实际 13 项 Rust PASS；`admission-regression.log` 为实际 22+1 项 PASS。新的原始副本干净应用补丁后，与被测试候选 SHA-256 一致。版本与哈希见 `patches/PATCH_IDENTITY.json`。

## 隔离复现

`prepare_sdk.py` 只复制既有固定源码，不修改原始 vendor；`.local-state/` 被排除在 Git 外。

```sh
python3 prepare_sdk.py --vendor /path/to/pinned/vendor --output /path/to/isolated/sdk
patch -C -p1 -d /path/to/isolated/sdk/app-hub -i /absolute/path/to/app-hub-installed-discovery.patch
patch -p1 -d /path/to/isolated/sdk/app-hub -i /absolute/path/to/app-hub-installed-discovery.patch
CARGO_TARGET_DIR=/path/to/isolated/cargo-target cargo test --locked --offline --release --manifest-path /path/to/isolated/sdk/app-hub/Cargo.toml -p octosense-appstore -- --test-threads=1
CARGO_TARGET_DIR=/path/to/isolated/cargo-target cargo test --locked --offline --release --manifest-path /path/to/isolated/sdk/app-hub/Cargo.toml -p octosense-app-policy -- --test-threads=1
```

上述命令已用实际隔离路径执行。离线测试要求已缓存锁定的 Rust 依赖；新环境没有缓存时会准确失败，不修改锁文件。

构建工具以 `TOOLCHAIN_LOCK.json` 固定官方 URL 和摘要。`prepare_tools.py` 验证后安装到给定目录；NDK 只省略未用于编译的调试和分析工具，保留编译器、完整 sysroot、Clang 资源及许可证。构建状态与最终产物哈希会在实际完成后补入报告。
