# Muse 0.3.20 配套宿主增量

这是现有 OctoSense / Makepad 宿主的小范围修补，不是第二套 Agent 运行时，也未获上游正式接纳。当前产品整体仍为 PARTIAL。

## 修补内容

- `bounded-source-preparation.patch`：Makepad 首次评估超过 64 KiB 的 Splash 源码时，每个真实 NextFrame 准备最多 16 KiB；沿用原生增量解析检查点，准备期间不执行应用语句。完整源码成功后执行一次。错误、panic 或关闭会停止 isolate；样式重应用不能重新启动失败的源码。
- `model-complete-attempt-boundary.patch`：官方 model.complete 一次逻辑请求的所有 provider 合计最多两次 HTTP post；只有格式错误、用量已知且预算允许时可作一次修复。拒绝、截断、超时、未知用量等停止后续尝试。公开服务接口保持不变，不能由此核清旧 S03 失败费用。

64 毫秒、采样周期、200000 条应用评估限制及 Muse manifest 指令预算均未调高。大源码编译分帧并不等于应用成功启动；必须验证有真实内容、可编辑输入、导航和状态恢复。

## 来源与重建

公开源码的 `vendor/makepad` 和 `vendor/octosense` 已包含匹配增量，不能重复应用补丁。补丁用于对比 0.3.19 基线；五份文件的基线与候选 SHA 见证据绑定。依赖沿用原锁文件与相对链接，禁止另换 SDK。

在完整源码根目录，依次运行：

```sh
cargo test --release --locked --offline -j2 --manifest-path vendor/octosense/Cargo.toml -p octosense-llm-service --lib --test complete
cargo test --release --locked --offline -j2 --manifest-path vendor/octosense/Cargo.toml -p makepad-script --lib
cargo test --release --locked --offline -j2 --manifest-path vendor/octosense/Cargo.toml -p makepad-widgets --lib style_tests
cargo build --release --locked --offline -j2 --manifest-path vendor/octosense/Cargo.toml -p octosense --bin octosense --no-default-features --features app-hub
```

这些命令需已有 Rust 工具链与锁定依赖；本轮验证复用本机缓存，不声称完成陌生机器从零离线安装。模型测试使用合成传输，不接付费服务。macOS 日历真实读写需现有授权，并按具体确认卡执行。

## 证据边界

原生模型测试 59 项通过、1 项既有 Keychain 测试忽略；VM 第二轮 61 项通过。VM 首轮 60 项通过、1 项错误断言失败已保留：缺失 heap 值返回 not-found 而非 NIL，修正后的同名测试直接计数原生调用，准备时零次、执行时一次。控件、最终 Shell 和系统全链的结果以最终报告为准，不能用本文件提前标 PASS。
