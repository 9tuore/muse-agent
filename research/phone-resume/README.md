# Phone 关机后恢复验证

这是隔离验证工具和官方打包器的单函数补丁，不是第二套 Runtime。当前未替换正式安装、旧 r7 APK、生产资料或实体设备。

## 已观察到的失败与修补

旧 r7 Home APK（SHA256 `70a318d1ccef68f62449a77ebc4b8d6d6dad79f6722a5b41b449ee8b534a62f1`）在新 API35 x86_64 模拟器启动后，实际因缺少 `mobile-presets.json` 崩溃。安装成功和 am start 返回成功没有计为 Home 运行成功。独立模拟器一小时守护已正常退出；没有授予系统权限。

`extract_dependency_paths` 按空格切分 Cargo tree 输出，漏掉带空格的依赖目录和资源。原函数与最新 Desktop rc.2 的 Makepad `32d6415f` 相同。仅修改这个函数，保留目录存在检查；六项实际 Rust/文件系统变体原版4FAIL/2PASS，补丁6PASS。锁定的官方 packager 构建成功，Cargo.lock 哈希未变。rustfmt 组件缺失，未记录格式通过。原失败、offline 缺依赖失败和真实崩溃均保留。

## 复现函数测试

先准备同一源码的原版和补丁版 `utils.rs`，再运行（输出目录必须尚不存在）：

```sh
python3 research/phone-resume/test_parser.py --before /path/to/original/utils.rs --after /path/to/patched/utils.rs --out build/phone-parser-check
```

测试实际提取并编译源码函数，不是 Python 模拟 Cargo 行解析。Rust 测试、补丁和结果在本目录；全 APK/日志和模拟器数据在 ignored build，不进入 Git。

## 运行边界

- `run_emulator.py` 使用保留 SDK、全新隔离 AVD，校验原 r7 APK；时间/磁盘守护只停止它自己创建的进程组。
- `repackage_home.py` 使用补丁版官方 cargo-makepad、既有 Phone 源码和 SDK；只更新可重建 Android target，不修改原 SDK 源文件。组合 Phone 状态上限10.5GB、磁盘底线2GB；保留 r7 与失败证据。
- 保留 SDK Git 基线是 `7f962547`，已有本地模型、邮件、日历和 Phone 配套补丁，并非官方 rc.2 原版。重建后的二进制身份需另行核对，不能从 r7 哈希推断一致。
- 真实硬件 `DEVICE_NOT_TESTED`。不刷 ROM、不改安全设置、不授予账号/日历访问。
- 修补后的 Home 完整重建、APK 资源/签名核对和两次模拟器冷启动已通过；一次强制停止后恢复正常 Home。它仍属于保留的 rc16 Phone 配套候选，不能作为 rc18 Desktop 或手机 Muse 全链证据。

已按用户授权提交给官方审阅：[OctoSense #458](https://github.com/OctoSense-org/OctoSense/issues/458)。尚未被官方接受。

## 修补后实际运行

新 APK SHA256 `a7bac6c066c2cbac2d679ae8278e814d837baeb77a3afa4ea115df26f4673634`，246,145,986 字节。缺失的主题资源现已进入 APK，原 r7 的全部 native `.so` 字节保持一致；`apksigner verify` exit0。首次拒绝定位，重启后取消再次询问，没有自动授予权限。两次实际 Home 截图、不同进程及 AndroidRuntime 检查见 `evidence/home-emulator-report.json`；未观察到 Kernel 进程，不声明 Bridge、Agent、邮件或日历联动通过。

首次重建被10.5GB组合上限停止，第二次发现 packager 工具树缺少保留 Phone 已有的 Java 触控/返回兼容层，两项编译错误原样保留。按同一 framework 基线复制已有三份 Java 文件后，第三次构建 exit0。`retained-touch-back-compatibility.patch` 是原有配套改动的来源记录，不是本轮新增业务实现，也不是官方已合入的补丁。锁、Phone源码、旧APK和原始二进制不改。

低磁盘模式仅在官方工具明确结束 Rust 编译、开始 APK 打包后清理 `.rlib/.rmeta/.d` 可重建缓存，保留最后的 native/shared `.so`；组合10.5GB上限和磁盘底线不提高。首次资源停止与 Java 错误仍在 `evidence/` 和 ignored build。

真实运行证据已补到[#458 评论6095819625](https://github.com/OctoSense-org/OctoSense/issues/458#issuecomment-6095819625)。完整边界见根目录 `MUSE_PHONE_RESUME_REPORT.md`。
