# Handoff

## Task
GPT-03；基线 4a288a26。只读核对现有 WorkBuddy Host 接入本地签名镜像的正式入口。

## Result
PASS（入口核查）：没有运行中切源或设备导入 bundle 的现成 UI/CLI。`source` 仅切预览；App Hub worker 从进程环境创建 Backend；open schema 不接受镜像参数；`hub publisher-unpack` 只解包到 staging。

唯一入口：中央在原 WorkBuddy `Muse-BlackFix-RC3.app/Contents/MacOS/Launcher` 第 31 行清环境之后、第 35 行 exec 之前加入：

```sh
export OCTOSENSE_HUB_CATALOG=legacy
export OCTOSENSE_HUB='/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/muse-integrated-0.4.0-rc3-final/mirror'
export OCTOSENSE_HUB_ANCHOR=543ffbe45b6700c23e1824157ea694f8bd7839090e0ede464c11758d350b1412
```

再经原 `.app` 的 LaunchServices 入口重启；保留原 STATE、HOME、Host 和 remote=9696。仅在外层设置变量会被原脚本清除。App Hub 刷新→选 Muse→查看权限→本人确认安装→Open `muse-goals`。

## Changed
仅本交接；未改 Launcher、SDK、生产资料或安装记录。

## Tests
2026-10-11：读取准备 SDK/Hub 的 `view.rs:221,321,889,980`、`catalog.rs:122,393,440,483`、`module.rs:22`、`source.rs:19,37,82`、CLI usage 与原 Launcher。当前镜像元数据为 sequence=1、Muse 0.4.0-rc3；当前 apps 根未见 catalog-v2.json、catalog.json。元数据读取未替代验签；未执行 GUI、编译或安装。

## Commit
本地提交见本文件所属 Git 提交；未 push。

## Remaining
中央执行重启与正式安装。若使用 rc4，须先生成该候选镜像，再将上面镜像路径指向它；当前核对的 rc3 镜像不含 rc4。

## Important Boundaries
正常安装仍经过 catalog 验签、sequence floor、权限批准和 bundle gate。若出现任何 v2 缓存，legacy 会拒绝；不得删缓存或换资料根绕过。Native prototype 可见不等于正式 Muse 已安装。
