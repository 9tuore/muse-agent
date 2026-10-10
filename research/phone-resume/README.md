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
- 当前 Home 完整重建和修补后运行仍待验证；不声明新正式 APK 或手机全链通过。

已按用户授权提交给官方审阅：[OctoSense #458](https://github.com/OctoSense-org/OctoSense/issues/458)。尚未被官方接受。
