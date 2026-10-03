# 磁盘清理交接 · 2026-09-29

## Task

用户要求紧急腾出空间，并清理 Muse/GOSIM 多次更新留下的旧版本；基线 `main`，清理前 HEAD `106c07f`。

## Result

PASS（仅磁盘清理）。Data 容器可用空间从 859.5 MB 升至约 12.3 GB；清理期间其他任务可能写盘，净增以最终 `diskutil` 为准。

## Changed

- 清除 `/private/tmp/g01-h5-chain-target` 的旧 Rust 构建产物、`work/official/robrix2/target` 和 `runtime/octos-lean-target` 的可重建编译缓存。
- 仅删除 `dist` 初版及 r2–r16、`runtime` 集成候选初版及 02–18 内的 `.app/.zip/.dmg` 旧二进制；保留各目录的说明、校验值及 `evidence/`。
- 保留已安装应用、r18 当前包、r17 回退包、candidate-19、模型与用户数据。没有修改产品源码。

## Tests

安装版主程序 SHA-256 与 r18 相同（`0c87d27801dbb25538c7d5072a61458e9b3c84c875a8f1970e75d7962553cde8`）；两者 `codesign --verify --deep --strict` 均通过。清理后 `diskutil` 可用 12.3 GB。未做产品功能回归；下次 Rust 构建需重新编译。

## Commit

本地提交 `ddf2472`，未推送。共享工作树的另一任务在暂存区核对后并发加入 Calendar 实现、测试、证据与交接修改，因此该提交意外包含这些文件；它们并非本次清理产生或验证。已通知 G-00 核对归属与测试结论；不重写该提交，以免损坏并发工作。本文的后续修订见 Git 历史。

## Remaining

历史证据内部分旧包路径已不可直接复跑；若需复核旧版，先从对应源码/提交重建。18 GB 屏幕录制和微信缓存未触碰。

## Important Boundaries

“r18 当前包”仅指本机安装副本主程序哈希一致且签名有效，不等于 r18 全部功能已验收；r17 保留作回退。
